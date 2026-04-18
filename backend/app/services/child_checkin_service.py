from datetime import date, datetime, timedelta, timezone
import secrets
import uuid
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.services import qr_service
from jose import jwt

from app.core.config import settings
from app.core.security import decode_token, get_password_hash, verify_password

from app.db.models.child_checkin import (
    ChildCheckinAudit,
    ChildCheckinChild,
    ChildCheckinFamily,
    ChildCheckinGuardian,
    ChildCheckinNotification,
    ChildCheckinRecord,
    ChildCheckinRoom,
    ChildCheckinRoomScope,
)
from app.db.models.user import User
from app.schemas.child_checkin import (
    ChildCheckinCheckoutRequest,
    ChildCheckinChildCreate,
    ChildCheckinChildUpdate,
    ChildCheckinCreate,
    ChildCheckinFamilyCreate,
    ChildCheckinFamilyUpdate,
    ChildCheckinGuardianCreate,
    ChildCheckinGuardianUpdate,
    ChildCheckinNotificationCreate,
    ChildCheckinRoomScopeCreate,
    ChildCheckinSummaryResponse,
    ChildCheckinVisitorQuickCreate,
    ChildCheckinPublicPreRegistrationCreate,
    ChildCheckinRoomCreate,
    ChildCheckinRoomUpdate,
    ChildCheckinQrScanRequest,
)


def _family_code() -> str:
    return f"FAM-{secrets.token_hex(3).upper()}"


def _normalize_phone(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return "".join(ch for ch in raw if ch.isdigit())


def _normalize_email(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    return raw


def _age_in_months(birth_date: date, today: date | None = None) -> int:
    ref = today or date.today()
    months = (ref.year - birth_date.year) * 12 + (ref.month - birth_date.month)
    if ref.day < birth_date.day:
        months -= 1
    return max(0, months)


def _suggest_room_for_birth_date(db: Session, *, tenant_id: int, birth_date: date) -> str | None:
    months = _age_in_months(birth_date)
    rooms = (
        db.query(ChildCheckinRoom)
        .filter(
            ChildCheckinRoom.tenant_id == tenant_id,
            ChildCheckinRoom.is_active.is_(True),
            # Skip rooms without explicit ranges.
            or_(ChildCheckinRoom.min_age_months.isnot(None), ChildCheckinRoom.max_age_months.isnot(None)),
        )
        .order_by(
            func.coalesce(ChildCheckinRoom.min_age_months, 10_000).asc(),
            ChildCheckinRoom.name.asc(),
        )
        .all()
    )
    for room in rooms:
        min_ok = room.min_age_months is None or months >= int(room.min_age_months)
        max_ok = room.max_age_months is None or months <= int(room.max_age_months)
        if min_ok and max_ok:
            return room.name
    return None


def _parse_age_range_label(label: str | None) -> tuple[int | None, int | None]:
    """Parse labels like '0-3 anos', '4 a 6', '0-12 meses', '4+' into (min_months, max_months)."""
    raw = str(label or "").strip().lower()
    if not raw:
        return None, None

    # Detect unit: default is years, but if it mentions months, treat as months.
    is_months = any(token in raw for token in ["mes", "mês", "meses"])

    # "4+" style.
    if "+" in raw:
        nums = [int(n) for n in "".join(ch if ch.isdigit() or ch.isspace() else " " for ch in raw).split() if n.isdigit()]
        if nums:
            min_v = nums[0]
            return (min_v if is_months else min_v * 12), None

    # General: take first two integers found.
    cleaned = "".join(ch if ch.isdigit() or ch.isspace() else " " for ch in raw)
    nums = [int(part) for part in cleaned.split() if part.isdigit()]
    if not nums:
        return None, None
    if len(nums) == 1:
        v = nums[0]
        return (v if is_months else v * 12), None

    min_v, max_v = nums[0], nums[1]
    if max_v < min_v:
        min_v, max_v = max_v, min_v
    if is_months:
        return min_v, max_v
    return min_v * 12, max_v * 12


def _enforce_room_capacity(db: Session, *, tenant_id: int, room_name: str) -> None:
    # Backwards compatible wrapper (older callers). This checks only "current in room" without context.
    _enforce_room_capacity_for_context(
        db,
        tenant_id=tenant_id,
        room_name=room_name,
        context_type=None,
        context_name=None,
        now_utc=datetime.now(timezone.utc),
        extra=0,
    )


def _local_day_bounds_utc(now_utc: datetime, tz_name: str = "America/Sao_Paulo") -> tuple[datetime, datetime]:
    tz = ZoneInfo(tz_name)
    local = now_utc.astimezone(tz)
    start_local = datetime(local.year, local.month, local.day, tzinfo=tz)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def _enforce_room_capacity_for_context(
    db: Session,
    *,
    tenant_id: int,
    room_name: str,
    context_type: str | None,
    context_name: str | None,
    now_utc: datetime,
    extra: int = 0,
) -> None:
    normalized = str(room_name or "").strip()
    if not normalized:
        return
    room = (
        db.query(ChildCheckinRoom)
        .filter(
            ChildCheckinRoom.tenant_id == tenant_id,
            func.lower(ChildCheckinRoom.name) == normalized.lower(),
            ChildCheckinRoom.is_active.is_(True),
        )
        .first()
    )
    if not room or not room.capacity:
        return

    filters = [
        ChildCheckinRecord.tenant_id == tenant_id,
        func.lower(ChildCheckinRecord.room_name) == normalized.lower(),
        ChildCheckinRecord.status == "checked_in",
    ]

    # If context is present, capacity is enforced per culto/evento (context) and per local day.
    if context_type and context_name:
        ctx_type = str(context_type).strip().lower()
        ctx_name = str(context_name).strip().lower()
        start_utc, end_utc = _local_day_bounds_utc(now_utc)
        filters.extend(
            [
                func.lower(ChildCheckinRecord.context_type) == ctx_type,
                func.lower(ChildCheckinRecord.context_name) == ctx_name,
                ChildCheckinRecord.checkin_at >= start_utc,
                ChildCheckinRecord.checkin_at < end_utc,
            ]
        )

    active_count = (
        db.query(func.count(ChildCheckinRecord.id))
        .filter(and_(*filters))
        .scalar()
        or 0
    )
    total_after = int(active_count) + max(0, int(extra or 0))
    if total_after > int(room.capacity):
        if context_type and context_name:
            raise ValueError(
                f"Sala '{room.name}' esta lotada para este culto (limite {room.capacity}). Selecione outra sala."
            )
        raise ValueError(f"Sala '{room.name}' esta lotada (limite {room.capacity}). Selecione outra sala.")


def create_public_family_token(*, tenant_id: int, family_id: int, days: int = 30) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=days)
    payload = {"tenant_id": tenant_id, "family_id": family_id, "type": "kids_public", "exp": exp}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_public_family_token(token: str) -> dict | None:
    payload = decode_token(token)
    if not payload or payload.get("type") != "kids_public":
        return None
    if not payload.get("tenant_id") or not payload.get("family_id"):
        return None
    return payload


def _security_code() -> str:
    return f"K{secrets.token_hex(3).upper()}"


def _qr_token() -> str:
    return uuid.uuid4().hex


def _as_aware_utc(value: datetime) -> datetime:
    # Some DBs/tests may return timezone-naive datetimes even if the column is tz-aware.
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _build_alert_snapshot(child: ChildCheckinChild) -> str | None:
    alerts: list[str] = []
    if child.allergies:
        alerts.append(f"Alergias: {child.allergies}")
    if child.medical_restrictions:
        alerts.append(f"Restricoes medicas: {child.medical_restrictions}")
    if child.special_needs:
        alerts.append(f"Necessidades especiais: {child.special_needs}")
    if child.behavioral_notes:
        alerts.append(f"Comportamento/cuidados: {child.behavioral_notes}")
    return " | ".join(alerts) if alerts else None


def _audit(db: Session, *, tenant_id: int, record_id: int | None, action: str, user_id: int | None, details: str | None = None) -> None:
    db.add(
        ChildCheckinAudit(
            tenant_id=tenant_id,
            record_id=record_id,
            action=action,
            performed_by_user_id=user_id,
            details=details,
        )
    )


def get_user_room_scopes(db: Session, tenant_id: int, user_id: int) -> set[str]:
    rows = (
        db.query(ChildCheckinRoomScope)
        .filter(
            ChildCheckinRoomScope.tenant_id == tenant_id,
            ChildCheckinRoomScope.user_id == user_id,
            ChildCheckinRoomScope.is_active.is_(True),
        )
        .all()
    )
    return {str(row.room_name).strip().lower() for row in rows if row.room_name}


def list_families(
    db: Session,
    tenant_id: int,
    query: str | None = None,
    *,
    include_inactive: bool = False,
) -> list[ChildCheckinFamily]:
    q = db.query(ChildCheckinFamily).filter(ChildCheckinFamily.tenant_id == tenant_id)
    if not include_inactive:
        q = q.filter(ChildCheckinFamily.is_active.is_(True))
    if query:
        term = f"%{query.strip()}%"
        q = q.filter(
            or_(
                ChildCheckinFamily.family_name.ilike(term),
                ChildCheckinFamily.primary_responsible_name.ilike(term),
                ChildCheckinFamily.phone_primary.ilike(term),
                ChildCheckinFamily.family_code.ilike(term),
            )
        )
    return q.order_by(ChildCheckinFamily.family_name.asc()).all()


def create_family(db: Session, tenant_id: int, payload: ChildCheckinFamilyCreate, actor_user_id: int | None = None) -> ChildCheckinFamily:
    family = ChildCheckinFamily(
        tenant_id=tenant_id,
        family_code=_family_code(),
        **payload.model_dump(),
    )
    db.add(family)
    db.flush()
    _audit(db, tenant_id=tenant_id, record_id=None, action="family_created", user_id=actor_user_id, details=f"family_id={family.id}")
    db.commit()
    db.refresh(family)
    return family


def update_family(db: Session, tenant_id: int, family_id: int, payload: ChildCheckinFamilyUpdate, actor_user_id: int | None = None) -> ChildCheckinFamily | None:
    family = db.query(ChildCheckinFamily).filter(ChildCheckinFamily.tenant_id == tenant_id, ChildCheckinFamily.id == family_id).first()
    if family is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(family, field, value)
    _audit(db, tenant_id=tenant_id, record_id=None, action="family_updated", user_id=actor_user_id, details=f"family_id={family.id}")
    db.commit()
    db.refresh(family)
    return family


def list_children(db: Session, tenant_id: int, family_id: int | None = None, room_name: str | None = None, include_inactive: bool = False) -> list[ChildCheckinChild]:
    q = db.query(ChildCheckinChild).filter(ChildCheckinChild.tenant_id == tenant_id)
    if family_id:
        q = q.filter(ChildCheckinChild.family_id == family_id)
    if room_name:
        q = q.filter(func.lower(ChildCheckinChild.room_name) == room_name.strip().lower())
    if not include_inactive:
        q = q.filter(ChildCheckinChild.is_active.is_(True))
    return q.order_by(ChildCheckinChild.full_name.asc()).all()


def create_child(db: Session, tenant_id: int, payload: ChildCheckinChildCreate, actor_user_id: int | None = None) -> ChildCheckinChild:
    data = payload.model_dump()
    if not data.get("room_name") and data.get("birth_date"):
        suggested = _suggest_room_for_birth_date(db, tenant_id=tenant_id, birth_date=data["birth_date"])
        if suggested:
            data["room_name"] = suggested
    child = ChildCheckinChild(tenant_id=tenant_id, **data)
    db.add(child)
    db.flush()
    _audit(db, tenant_id=tenant_id, record_id=None, action="child_created", user_id=actor_user_id, details=f"child_id={child.id}")
    db.commit()
    db.refresh(child)
    return child


def update_child(db: Session, tenant_id: int, child_id: int, payload: ChildCheckinChildUpdate, actor_user_id: int | None = None) -> ChildCheckinChild | None:
    child = db.query(ChildCheckinChild).filter(ChildCheckinChild.tenant_id == tenant_id, ChildCheckinChild.id == child_id).first()
    if child is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(child, field, value)
    _audit(db, tenant_id=tenant_id, record_id=None, action="child_updated", user_id=actor_user_id, details=f"child_id={child.id}")
    db.commit()
    db.refresh(child)
    return child


def list_guardians(db: Session, tenant_id: int, family_id: int) -> list[ChildCheckinGuardian]:
    return (
        db.query(ChildCheckinGuardian)
        .filter(ChildCheckinGuardian.tenant_id == tenant_id, ChildCheckinGuardian.family_id == family_id)
        .order_by(ChildCheckinGuardian.full_name.asc())
        .all()
    )


def create_guardian(db: Session, tenant_id: int, payload: ChildCheckinGuardianCreate, actor_user_id: int | None = None) -> ChildCheckinGuardian:
    guardian = ChildCheckinGuardian(tenant_id=tenant_id, **payload.model_dump())
    db.add(guardian)
    db.flush()
    _audit(db, tenant_id=tenant_id, record_id=None, action="guardian_created", user_id=actor_user_id, details=f"guardian_id={guardian.id}")
    db.commit()
    db.refresh(guardian)
    return guardian


def update_guardian(db: Session, tenant_id: int, guardian_id: int, payload: ChildCheckinGuardianUpdate, actor_user_id: int | None = None) -> ChildCheckinGuardian | None:
    guardian = db.query(ChildCheckinGuardian).filter(ChildCheckinGuardian.tenant_id == tenant_id, ChildCheckinGuardian.id == guardian_id).first()
    if guardian is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(guardian, field, value)
    _audit(db, tenant_id=tenant_id, record_id=None, action="guardian_updated", user_id=actor_user_id, details=f"guardian_id={guardian.id}")
    db.commit()
    db.refresh(guardian)
    return guardian


def create_checkins(
    db: Session,
    *,
    tenant_id: int,
    payload: ChildCheckinCreate,
    actor_user_id: int | None,
    room_scope_restriction: set[str] | None,
) -> list[ChildCheckinRecord]:
    if room_scope_restriction:
        requested_room = payload.room_name.strip().lower()
        if requested_room not in room_scope_restriction:
            raise ValueError("Voce nao possui acesso para esta sala.")

    children = (
        db.query(ChildCheckinChild)
        .filter(
            ChildCheckinChild.tenant_id == tenant_id,
            ChildCheckinChild.family_id == payload.family_id,
            ChildCheckinChild.id.in_(payload.child_ids),
            ChildCheckinChild.is_active.is_(True),
        )
        .all()
    )
    child_by_id = {child.id: child for child in children}

    # Identify which child IDs already have an open check-in (single query).
    open_rows = (
        db.query(ChildCheckinRecord.child_id)
        .filter(
            ChildCheckinRecord.tenant_id == tenant_id,
            ChildCheckinRecord.child_id.in_(list(child_by_id.keys()) or [-1]),
            ChildCheckinRecord.status == "checked_in",
        )
        .all()
    )
    open_child_ids = {int(row[0]) for row in open_rows if row and row[0]}

    to_create_child_ids: list[int] = []
    for child_id in payload.child_ids:
        cid = int(child_id)
        if cid in child_by_id and cid not in open_child_ids:
            to_create_child_ids.append(cid)

    # Capacity enforcement per culto (context) and per day.
    _enforce_room_capacity_for_context(
        db,
        tenant_id=tenant_id,
        room_name=payload.room_name,
        context_type=payload.context_type,
        context_name=payload.context_name,
        now_utc=datetime.now(timezone.utc),
        extra=len(to_create_child_ids),
    )

    created: list[ChildCheckinRecord] = []
    for child_id in payload.child_ids:
        child = child_by_id.get(child_id)
        if child is None:
            continue

        if child.id in open_child_ids:
            continue

        record = ChildCheckinRecord(
            tenant_id=tenant_id,
            family_id=payload.family_id,
            child_id=child.id,
            context_type=payload.context_type,
            context_name=payload.context_name,
            room_name=payload.room_name,
            accompanied_by_name=payload.accompanied_by_name,
            checked_in_by_user_id=actor_user_id,
            security_code=_security_code(),
            qr_token=_qr_token(),
            alert_snapshot=_build_alert_snapshot(child),
        )
        db.add(record)
        db.flush()
        created.append(record)
        _audit(
            db,
            tenant_id=tenant_id,
            record_id=record.id,
            action="checkin_created",
            user_id=actor_user_id,
            details=f"child_id={child.id};room={payload.room_name}",
        )

    db.commit()
    for item in created:
        db.refresh(item)
    return created


def list_checkins(
    db: Session,
    *,
    tenant_id: int,
    status_filter: str | None = None,
    room_name: str | None = None,
    target_date: date | None = None,
    room_scope_restriction: set[str] | None = None,
) -> list[ChildCheckinRecord]:
    q = db.query(ChildCheckinRecord).filter(ChildCheckinRecord.tenant_id == tenant_id)

    if status_filter:
        q = q.filter(ChildCheckinRecord.status == status_filter)
    if room_name:
        q = q.filter(func.lower(ChildCheckinRecord.room_name) == room_name.strip().lower())
    if target_date:
        start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
        end = start.replace(hour=23, minute=59, second=59)
        q = q.filter(and_(ChildCheckinRecord.checkin_at >= start, ChildCheckinRecord.checkin_at <= end))
    if room_scope_restriction:
        lowered = [name.lower() for name in room_scope_restriction]
        q = q.filter(func.lower(ChildCheckinRecord.room_name).in_(lowered))

    return q.order_by(ChildCheckinRecord.checkin_at.desc()).all()


def checkout_checkin(
    db: Session,
    *,
    tenant_id: int,
    checkin_id: int,
    payload: ChildCheckinCheckoutRequest,
    actor_user_id: int | None,
    can_manual_override: bool,
    room_scope_restriction: set[str] | None,
) -> ChildCheckinRecord | None:
    record = db.query(ChildCheckinRecord).filter(ChildCheckinRecord.tenant_id == tenant_id, ChildCheckinRecord.id == checkin_id).first()
    if record is None:
        return None

    if room_scope_restriction and record.room_name.strip().lower() not in room_scope_restriction:
        raise ValueError("Voce nao possui acesso para esta sala.")

    if record.status != "checked_in":
        raise ValueError("Check-in ja finalizado para esta crianca.")

    token_ok = False
    if payload.security_code and payload.security_code.strip() == record.security_code:
        token_ok = True
    if payload.qr_token and payload.qr_token.strip() == record.qr_token:
        token_ok = True
    if not token_ok:
        raise ValueError("Codigo de seguranca invalido.")

    authorized_guardian = None
    if payload.pickup_guardian_id:
        authorized_guardian = (
            db.query(ChildCheckinGuardian)
            .filter(
                ChildCheckinGuardian.tenant_id == tenant_id,
                ChildCheckinGuardian.id == payload.pickup_guardian_id,
                ChildCheckinGuardian.family_id == record.family_id,
            )
            .first()
        )

    if authorized_guardian and not authorized_guardian.is_authorized and not can_manual_override:
        raise ValueError("Retirada bloqueada: responsavel nao autorizado.")

    if authorized_guardian and not authorized_guardian.is_authorized and can_manual_override:
        record.manual_override_by_user_id = actor_user_id

    record.pickup_guardian_id = payload.pickup_guardian_id
    record.pickup_person_name = payload.pickup_person_name
    record.exception_notes = payload.exception_notes
    record.checkout_at = datetime.now(timezone.utc)
    record.checked_out_by_user_id = actor_user_id
    record.status = "checked_out"

    _audit(
        db,
        tenant_id=tenant_id,
        record_id=record.id,
        action="checkout_completed",
        user_id=actor_user_id,
        details=f"pickup_guardian_id={payload.pickup_guardian_id};manual_override={bool(record.manual_override_by_user_id)}",
    )

    db.commit()
    db.refresh(record)
    return record


def create_visitor_quick_checkin(
    db: Session,
    *,
    tenant_id: int,
    payload: ChildCheckinVisitorQuickCreate,
    actor_user_id: int | None,
    room_scope_restriction: set[str] | None,
) -> list[ChildCheckinRecord]:
    family = ChildCheckinFamily(
        tenant_id=tenant_id,
        family_name=f"Visitante {payload.responsible_name}",
        primary_responsible_name=payload.responsible_name,
        phone_primary=payload.phone,
        notes=payload.important_notes,
        family_code=_family_code(),
        is_active=True,
    )
    db.add(family)
    db.flush()

    age_group = "Visitante"
    if payload.child_age is not None:
        age_group = f"{payload.child_age} anos"

    child = ChildCheckinChild(
        tenant_id=tenant_id,
        family_id=family.id,
        full_name=payload.child_name,
        age_group=age_group,
        room_name=payload.room_name,
        notes=payload.important_notes,
        is_visitor=True,
        is_active=True,
    )
    db.add(child)
    db.flush()

    guardian = ChildCheckinGuardian(
        tenant_id=tenant_id,
        family_id=family.id,
        full_name=payload.responsible_name,
        relationship="responsavel",
        phone=payload.phone,
        is_authorized=True,
    )
    db.add(guardian)
    db.flush()

    records = create_checkins(
        db,
        tenant_id=tenant_id,
        payload=ChildCheckinCreate(
            family_id=family.id,
            child_ids=[child.id],
            context_type=payload.context_type,
            context_name=payload.context_name,
            room_name=payload.room_name,
            accompanied_by_name=payload.responsible_name,
        ),
        actor_user_id=actor_user_id,
        room_scope_restriction=room_scope_restriction,
    )
    return records


def create_notification(db: Session, tenant_id: int, payload: ChildCheckinNotificationCreate, actor_user_id: int | None = None) -> ChildCheckinNotification:
    item = ChildCheckinNotification(
        tenant_id=tenant_id,
        family_id=payload.family_id,
        child_id=payload.child_id,
        channel=payload.channel,
        message_type=payload.message_type,
        message=payload.message,
        delivery_status="sent",
        created_by_user_id=actor_user_id,
    )
    db.add(item)
    db.flush()
    _audit(db, tenant_id=tenant_id, record_id=None, action="notification_created", user_id=actor_user_id, details=f"notification_id={item.id}")
    db.commit()
    db.refresh(item)
    return item


def list_notifications(db: Session, tenant_id: int, limit: int = 50) -> list[ChildCheckinNotification]:
    return (
        db.query(ChildCheckinNotification)
        .filter(ChildCheckinNotification.tenant_id == tenant_id)
        .order_by(ChildCheckinNotification.created_at.desc())
        .limit(limit)
        .all()
    )


def create_room_scope(db: Session, tenant_id: int, payload: ChildCheckinRoomScopeCreate) -> ChildCheckinRoomScope:
    row = (
        db.query(ChildCheckinRoomScope)
        .filter(
            ChildCheckinRoomScope.tenant_id == tenant_id,
            ChildCheckinRoomScope.user_id == payload.user_id,
            func.lower(ChildCheckinRoomScope.room_name) == payload.room_name.strip().lower(),
        )
        .first()
    )
    if row:
        row.is_active = True
        db.commit()
        db.refresh(row)
        return row

    created = ChildCheckinRoomScope(tenant_id=tenant_id, user_id=payload.user_id, room_name=payload.room_name)
    db.add(created)
    db.commit()
    db.refresh(created)
    return created


def list_rooms(db: Session, tenant_id: int, include_inactive: bool = False) -> list[ChildCheckinRoom]:
    q = db.query(ChildCheckinRoom).filter(ChildCheckinRoom.tenant_id == tenant_id)
    if not include_inactive:
        q = q.filter(ChildCheckinRoom.is_active.is_(True))
    return q.order_by(ChildCheckinRoom.name.asc()).all()


def create_room(db: Session, tenant_id: int, payload: ChildCheckinRoomCreate, actor_user_id: int | None = None) -> ChildCheckinRoom:
    normalized_name = payload.name.strip()
    parsed_min, parsed_max = _parse_age_range_label(payload.age_range_label)
    min_age_months = payload.min_age_months if payload.min_age_months is not None else parsed_min
    max_age_months = payload.max_age_months if payload.max_age_months is not None else parsed_max

    existing = (
        db.query(ChildCheckinRoom)
        .filter(
            ChildCheckinRoom.tenant_id == tenant_id,
            func.lower(ChildCheckinRoom.name) == normalized_name.lower(),
        )
        .first()
    )
    if existing:
        if not existing.is_active:
            existing.is_active = True
            existing.age_range_label = payload.age_range_label
            existing.min_age_months = min_age_months
            existing.max_age_months = max_age_months
            existing.capacity = payload.capacity
            existing.description = payload.description
            _audit(
                db,
                tenant_id=tenant_id,
                record_id=None,
                action="room_reactivated",
                user_id=actor_user_id,
                details=f"room_id={existing.id}",
            )
            db.commit()
            db.refresh(existing)
        return existing

    room = ChildCheckinRoom(
        tenant_id=tenant_id,
        name=normalized_name,
        age_range_label=payload.age_range_label,
        min_age_months=min_age_months,
        max_age_months=max_age_months,
        capacity=payload.capacity,
        description=payload.description,
        is_active=True,
    )
    db.add(room)
    db.flush()
    _audit(
        db,
        tenant_id=tenant_id,
        record_id=None,
        action="room_created",
        user_id=actor_user_id,
        details=f"room_id={room.id}",
    )
    db.commit()
    db.refresh(room)
    return room


def update_room(
    db: Session,
    tenant_id: int,
    room_id: int,
    payload: ChildCheckinRoomUpdate,
    actor_user_id: int | None = None,
) -> ChildCheckinRoom | None:
    room = db.query(ChildCheckinRoom).filter(ChildCheckinRoom.tenant_id == tenant_id, ChildCheckinRoom.id == room_id).first()
    if room is None:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"]:
        data["name"] = str(data["name"]).strip()

    # If age label was updated but min/max weren't, infer min/max.
    if "age_range_label" in data and ("min_age_months" not in data and "max_age_months" not in data):
        parsed_min, parsed_max = _parse_age_range_label(data.get("age_range_label"))
        if parsed_min is not None:
            data["min_age_months"] = parsed_min
        if parsed_max is not None:
            data["max_age_months"] = parsed_max

    for field, value in data.items():
        setattr(room, field, value)

    _audit(
        db,
        tenant_id=tenant_id,
        record_id=None,
        action="room_updated",
        user_id=actor_user_id,
        details=f"room_id={room.id}",
    )
    db.commit()
    db.refresh(room)
    return room


def list_room_scopes(db: Session, tenant_id: int, user_id: int | None = None) -> list[ChildCheckinRoomScope]:
    q = db.query(ChildCheckinRoomScope).filter(ChildCheckinRoomScope.tenant_id == tenant_id, ChildCheckinRoomScope.is_active.is_(True))
    if user_id:
        q = q.filter(ChildCheckinRoomScope.user_id == user_id)
    return q.order_by(ChildCheckinRoomScope.room_name.asc()).all()


def build_summary(db: Session, tenant_id: int, start_date: date | None = None, end_date: date | None = None) -> ChildCheckinSummaryResponse:
    q = db.query(ChildCheckinRecord).filter(ChildCheckinRecord.tenant_id == tenant_id)
    if start_date:
        start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
        q = q.filter(ChildCheckinRecord.checkin_at >= start_dt)
    if end_date:
        end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
        q = q.filter(ChildCheckinRecord.checkin_at <= end_dt)

    rows = q.all()
    total = len(rows)
    active = len([row for row in rows if row.status == "checked_in"])
    checked_out = len([row for row in rows if row.status == "checked_out"])
    unique_children = len({row.child_id for row in rows})

    visitor_children = (
        db.query(ChildCheckinChild)
        .filter(ChildCheckinChild.tenant_id == tenant_id, ChildCheckinChild.is_visitor.is_(True), ChildCheckinChild.is_active.is_(True))
        .count()
    )

    alerts = (
        db.query(ChildCheckinChild)
        .filter(
            ChildCheckinChild.tenant_id == tenant_id,
            ChildCheckinChild.is_active.is_(True),
            or_(
                ChildCheckinChild.allergies.isnot(None),
                ChildCheckinChild.medical_restrictions.isnot(None),
                ChildCheckinChild.special_needs.isnot(None),
            ),
        )
        .count()
    )

    return ChildCheckinSummaryResponse(
        total_checkins=total,
        active_checkins=active,
        completed_checkouts=checked_out,
        unique_children=unique_children,
        visitors=visitor_children,
        alerts_count=alerts,
    )


def validate_scope_users_exist(db: Session, tenant_id: int, user_ids: list[int]) -> None:
    if not user_ids:
        return
    existing = (
        db.query(User.id)
        .filter(User.id.in_(user_ids), User.active_tenant_id == tenant_id)
        .all()
    )
    existing_ids = {row.id for row in existing}
    missing = [user_id for user_id in user_ids if user_id not in existing_ids]
    if missing:
        raise ValueError(f"Usuarios nao encontrados neste tenant: {missing}")


def _parse_qr_payload(payload: str) -> tuple[str | None, str, int]:
    parts = str(payload or "").strip().split(":")
    if len(parts) == 4 and parts[0] == "KIDS":
        tenant_slug = parts[1].strip() or None
        family_code = parts[2].strip().upper()
        child_id = int(parts[3])
        return tenant_slug, family_code, child_id
    if len(parts) == 3 and parts[0] == "KIDS":
        family_code = parts[1].strip().upper()
        child_id = int(parts[2])
        return None, family_code, child_id
    raise ValueError("QR code invalido.")


def create_checkin_from_qr(
    db: Session,
    *,
    tenant_id: int,
    tenant_slug: str,
    payload: ChildCheckinQrScanRequest,
    actor_user_id: int | None,
    room_scope_restriction: set[str] | None,
) -> ChildCheckinRecord:
    qr_tenant_slug, family_code, child_id = _parse_qr_payload(payload.qr_payload)
    if qr_tenant_slug and qr_tenant_slug != tenant_slug:
        raise ValueError("QR code pertence a outro tenant.")

    child = (
        db.query(ChildCheckinChild)
        .join(ChildCheckinFamily, ChildCheckinFamily.id == ChildCheckinChild.family_id)
        .filter(
            ChildCheckinChild.tenant_id == tenant_id,
            ChildCheckinChild.id == child_id,
            ChildCheckinChild.is_active.is_(True),
            func.upper(ChildCheckinFamily.family_code) == family_code,
            ChildCheckinFamily.is_active.is_(True),
        )
        .first()
    )
    if child is None:
        raise ValueError("Crianca nao encontrada para o QR informado.")

    effective_room = (payload.room_name_override or child.room_name or "").strip()
    if not effective_room:
        raise ValueError("Sala nao definida para esta crianca.")

    rows = create_checkins(
        db,
        tenant_id=tenant_id,
        payload=ChildCheckinCreate(
            family_id=child.family_id,
            child_ids=[child.id],
            context_type=payload.context_type,
            context_name=payload.context_name,
            room_name=effective_room,
            accompanied_by_name=payload.accompanied_by_name,
        ),
        actor_user_id=actor_user_id,
        room_scope_restriction=room_scope_restriction,
    )
    if not rows:
        raise ValueError("Esta crianca ja possui check-in ativo.")
    return rows[0]


def get_checkout_context(db: Session, *, tenant_id: int, checkin_id: int) -> dict | None:
    record = (
        db.query(ChildCheckinRecord)
        .filter(ChildCheckinRecord.tenant_id == tenant_id, ChildCheckinRecord.id == checkin_id)
        .first()
    )
    if record is None:
        return None

    child = (
        db.query(ChildCheckinChild)
        .filter(ChildCheckinChild.tenant_id == tenant_id, ChildCheckinChild.id == record.child_id)
        .first()
    )
    family = (
        db.query(ChildCheckinFamily)
        .filter(ChildCheckinFamily.tenant_id == tenant_id, ChildCheckinFamily.id == record.family_id)
        .first()
    )
    guardians = (
        db.query(ChildCheckinGuardian)
        .filter(ChildCheckinGuardian.tenant_id == tenant_id, ChildCheckinGuardian.family_id == record.family_id)
        .order_by(ChildCheckinGuardian.full_name.asc())
        .all()
    )

    return {
        "checkin_id": record.id,
        "child_id": record.child_id,
        "child_name": child.full_name if child else f"Crianca {record.child_id}",
        "child_photo_url": child.photo_url if child else None,
        "family_id": record.family_id,
        "family_name": family.family_name if family else f"Familia {record.family_id}",
        "primary_responsible_name": family.primary_responsible_name if family else None,
        "phone_primary": family.phone_primary if family else None,
        "room_name": record.room_name,
        "checkin_at": record.checkin_at,
        "security_code": record.security_code,
        "qr_token": record.qr_token,
        "guardians": [
            {
                "id": guardian.id,
                "full_name": guardian.full_name,
                "relationship": guardian.relationship,
                "phone": guardian.phone,
                "photo_url": guardian.photo_url,
                "is_authorized": bool(guardian.is_authorized),
            }
            for guardian in guardians
        ],
    }


def build_label_payload(db: Session, *, tenant_id: int, checkin_id: int) -> dict | None:
    record = (
        db.query(ChildCheckinRecord)
        .filter(ChildCheckinRecord.tenant_id == tenant_id, ChildCheckinRecord.id == checkin_id)
        .first()
    )
    if record is None:
        return None

    child = (
        db.query(ChildCheckinChild)
        .filter(ChildCheckinChild.tenant_id == tenant_id, ChildCheckinChild.id == record.child_id)
        .first()
    )
    family = (
        db.query(ChildCheckinFamily)
        .filter(ChildCheckinFamily.tenant_id == tenant_id, ChildCheckinFamily.id == record.family_id)
        .first()
    )

    return {
        "checkin_id": record.id,
        "child_name": child.full_name if child else f"Crianca {record.child_id}",
        "family_name": family.family_name if family else f"Familia {record.family_id}",
        "room_name": record.room_name,
        "context_name": record.context_name,
        "security_code": record.security_code,
        "qr_token": record.qr_token,
        "checkin_at": record.checkin_at,
    }


def build_label_qr_png(db: Session, *, tenant_id: int, checkin_id: int) -> bytes | None:
    record = (
        db.query(ChildCheckinRecord)
        .filter(ChildCheckinRecord.tenant_id == tenant_id, ChildCheckinRecord.id == checkin_id)
        .first()
    )
    if record is None:
        return None
    return qr_service.build_qr_png(record.qr_token or "")


def list_audits(db: Session, *, tenant_id: int, limit: int = 100, record_id: int | None = None) -> list[ChildCheckinAudit]:
    q = db.query(ChildCheckinAudit).filter(ChildCheckinAudit.tenant_id == tenant_id)
    if record_id:
        q = q.filter(ChildCheckinAudit.record_id == record_id)
    return q.order_by(ChildCheckinAudit.created_at.desc()).limit(limit).all()


def _normalize_phone_digits(phone: str | None) -> str:
    return "".join(char for char in str(phone or "") if char.isdigit())


def _to_whatsapp_link(phone: str | None) -> str | None:
    digits = _normalize_phone_digits(phone)
    if not digits:
        return None
    if len(digits) <= 11:
        digits = f"55{digits}"
    return f"https://wa.me/{digits}"


def _build_virtual_cards(
    *,
    tenant_slug: str,
    family: ChildCheckinFamily,
    children: list[ChildCheckinChild],
    guardians: list[ChildCheckinGuardian],
) -> list[dict]:
    guardian_rows = [
        {
            "guardian_id": guardian.id,
            "full_name": guardian.full_name,
            "relationship": guardian.relationship,
            "phone": guardian.phone,
            # Serve via API to avoid relying on /media/uploads proxying.
            "photo_url": (
                f"/api/v1/child-checkin/public/tenants/{tenant_slug}/families/{family.family_code}/guardians/{guardian.id}/photo"
                if guardian.photo_url
                else None
            ),
            "is_authorized": bool(guardian.is_authorized),
        }
        for guardian in guardians
    ]

    cards: list[dict] = []
    for child in children:
        cards.append(
            {
                "child_id": child.id,
                "child_name": child.full_name,
                "family_name": family.family_name,
                "family_code": family.family_code,
                "room_name": child.room_name,
                # Serve via API to avoid relying on /media/uploads proxying.
                "child_photo_url": (
                    f"/api/v1/child-checkin/public/tenants/{tenant_slug}/families/{family.family_code}/children/{child.id}/photo"
                    if child.photo_url
                    else None
                ),
                "qr_payload": f"KIDS:{tenant_slug}:{family.family_code}:{child.id}",
                "guardians": guardian_rows,
            }
        )
    return cards


def build_virtual_card_qr_png(*, tenant_slug: str, family_code: str, child_id: int) -> bytes:
    payload = f"KIDS:{tenant_slug}:{family_code}:{child_id}"
    return qr_service.build_qr_png(payload)


def get_family_by_code(db: Session, *, tenant_id: int, family_code: str) -> ChildCheckinFamily | None:
    return (
        db.query(ChildCheckinFamily)
        .filter(
            ChildCheckinFamily.tenant_id == tenant_id,
            ChildCheckinFamily.family_code == family_code,
            ChildCheckinFamily.is_active.is_(True),
        )
        .first()
    )


def set_child_photo_url(
    db: Session,
    *,
    tenant_id: int,
    family_id: int,
    child_id: int,
    photo_url: str,
    actor_user_id: int | None = None,
) -> ChildCheckinChild | None:
    child = (
        db.query(ChildCheckinChild)
        .filter(
            ChildCheckinChild.tenant_id == tenant_id,
            ChildCheckinChild.family_id == family_id,
            ChildCheckinChild.id == child_id,
        )
        .first()
    )
    if child is None:
        return None
    child.photo_url = photo_url
    _audit(db, tenant_id=tenant_id, record_id=None, action="child_photo_updated", user_id=actor_user_id, details=f"child_id={child.id}")
    db.commit()
    db.refresh(child)
    return child


def set_guardian_photo_url(
    db: Session,
    *,
    tenant_id: int,
    family_id: int,
    guardian_id: int,
    photo_url: str,
    actor_user_id: int | None = None,
) -> ChildCheckinGuardian | None:
    guardian = (
        db.query(ChildCheckinGuardian)
        .filter(
            ChildCheckinGuardian.tenant_id == tenant_id,
            ChildCheckinGuardian.family_id == family_id,
            ChildCheckinGuardian.id == guardian_id,
        )
        .first()
    )
    if guardian is None:
        return None
    guardian.photo_url = photo_url
    _audit(db, tenant_id=tenant_id, record_id=None, action="guardian_photo_updated", user_id=actor_user_id, details=f"guardian_id={guardian.id}")
    db.commit()
    db.refresh(guardian)
    return guardian


def create_public_pre_registration(
    db: Session,
    *,
    tenant_id: int,
    tenant_slug: str,
    payload: ChildCheckinPublicPreRegistrationCreate,
) -> tuple[ChildCheckinFamily, list[dict]]:
    normalized_email = _normalize_email(str(payload.email))
    if not normalized_email:
        raise ValueError("Informe o e-mail.")

    existing = (
        db.query(ChildCheckinFamily)
        .filter(
            ChildCheckinFamily.tenant_id == tenant_id,
            ChildCheckinFamily.is_active.is_(True),
            ChildCheckinFamily.email.isnot(None),
            func.lower(ChildCheckinFamily.email) == normalized_email,
        )
        .first()
    )
    if existing is not None:
        raise ValueError("Este e-mail ja possui cadastro no AppKids. Use 'Ja tenho cadastro'.")

    family = ChildCheckinFamily(
        tenant_id=tenant_id,
        family_name=payload.family_name,
        primary_responsible_name=payload.primary_responsible_name,
        secondary_responsible_name=payload.secondary_responsible_name,
        phone_primary=_normalize_phone(payload.phone_primary),
        phone_secondary=_normalize_phone(payload.phone_secondary),
        email=normalized_email,
        notes=payload.notes,
        family_code=_family_code(),
        public_pin_hash=get_password_hash(payload.public_pin) if payload.public_pin else None,
        is_active=True,
    )
    db.add(family)
    db.flush()

    children: list[ChildCheckinChild] = []
    for child_payload in payload.children:
        suggested_room = None
        if child_payload.birth_date and not child_payload.room_name:
            suggested_room = _suggest_room_for_birth_date(db, tenant_id=tenant_id, birth_date=child_payload.birth_date)
        child = ChildCheckinChild(
            tenant_id=tenant_id,
            family_id=family.id,
            full_name=child_payload.full_name,
            birth_date=child_payload.birth_date,
            age_group=child_payload.age_group,
            room_name=child_payload.room_name or suggested_room,
            gender=child_payload.gender,
            photo_url=child_payload.photo_url,
            notes=child_payload.notes,
            allergies=child_payload.allergies,
            medical_restrictions=child_payload.medical_restrictions,
            special_needs=child_payload.special_needs,
            behavioral_notes=child_payload.behavioral_notes,
            is_active=True,
            is_visitor=False,
        )
        db.add(child)
        db.flush()
        children.append(child)

    guardians: list[ChildCheckinGuardian] = []
    for guardian_payload in payload.guardians:
        guardian = ChildCheckinGuardian(
            tenant_id=tenant_id,
            family_id=family.id,
            full_name=guardian_payload.full_name,
            relationship=guardian_payload.relationship,
            phone=guardian_payload.phone,
            photo_url=guardian_payload.photo_url,
            is_authorized=guardian_payload.is_authorized,
        )
        db.add(guardian)
        db.flush()
        guardians.append(guardian)

    _audit(db, tenant_id=tenant_id, record_id=None, action="public_pre_registration", user_id=None, details=f"family_id={family.id}")
    db.commit()
    db.refresh(family)

    cards = _build_virtual_cards(
        tenant_slug=tenant_slug,
        family=family,
        children=children,
        guardians=guardians,
    )
    return family, cards


def public_login_family(db: Session, *, tenant_id: int, email: str | None, phone: str | None, pin: str) -> ChildCheckinFamily:
    normalized_email = _normalize_email(email) if email else ""
    normalized_phone = _normalize_phone(phone) if phone else ""
    if not normalized_email and not normalized_phone:
        raise ValueError("Informe o e-mail.")
    if not pin or len(str(pin).strip()) < 4:
        raise ValueError("Informe o PIN.")

    if normalized_email:
        fam = (
            db.query(ChildCheckinFamily)
            .filter(
                ChildCheckinFamily.tenant_id == tenant_id,
                ChildCheckinFamily.is_active.is_(True),
                ChildCheckinFamily.public_pin_hash.isnot(None),
                ChildCheckinFamily.email.isnot(None),
                func.lower(ChildCheckinFamily.email) == normalized_email,
            )
            .first()
        )
        if fam and fam.public_pin_hash and verify_password(str(pin).strip(), fam.public_pin_hash):
            return fam

    if not normalized_phone:
        raise ValueError("Telefone ou PIN invalido.")

    needle = normalized_phone[-8:] if len(normalized_phone) >= 8 else normalized_phone
    candidates = (
        db.query(ChildCheckinFamily)
        .filter(
            ChildCheckinFamily.tenant_id == tenant_id,
            ChildCheckinFamily.is_active.is_(True),
            ChildCheckinFamily.public_pin_hash.isnot(None),
            ChildCheckinFamily.phone_primary.isnot(None),
            ChildCheckinFamily.phone_primary != "",
            ChildCheckinFamily.phone_primary.ilike(f"%{needle}%"),
        )
        .limit(50)
        .all()
    )

    for fam in candidates:
        if _normalize_phone(fam.phone_primary) != normalized_phone:
            continue
        if not fam.public_pin_hash:
            continue
        if verify_password(str(pin).strip(), fam.public_pin_hash):
            return fam

    raise ValueError("Telefone ou PIN invalido.")


def request_public_pin_recovery(db: Session, *, tenant_id: int, email: str) -> tuple[ChildCheckinFamily | None, str]:
    normalized_email = _normalize_email(email)
    if not normalized_email:
        raise ValueError("Informe o e-mail.")

    fam = (
        db.query(ChildCheckinFamily)
        .filter(
            ChildCheckinFamily.tenant_id == tenant_id,
            ChildCheckinFamily.is_active.is_(True),
            ChildCheckinFamily.email.isnot(None),
            func.lower(ChildCheckinFamily.email) == normalized_email,
        )
        .first()
    )
    if fam is None:
        return None, ""

    code = f"{secrets.randbelow(1_000_000):06d}"
    fam.public_reset_code_hash = get_password_hash(code)
    fam.public_reset_code_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.commit()
    return fam, code


def confirm_public_pin_recovery(db: Session, *, tenant_id: int, email: str, code: str, new_pin: str) -> ChildCheckinFamily:
    normalized_email = _normalize_email(email)
    if not normalized_email:
        raise ValueError("Informe o e-mail.")

    fam = (
        db.query(ChildCheckinFamily)
        .filter(
            ChildCheckinFamily.tenant_id == tenant_id,
            ChildCheckinFamily.is_active.is_(True),
            ChildCheckinFamily.email.isnot(None),
            func.lower(ChildCheckinFamily.email) == normalized_email,
        )
        .first()
    )
    if fam is None or not fam.public_reset_code_hash or not fam.public_reset_code_expires_at:
        raise ValueError("Codigo invalido.")

    if datetime.now(timezone.utc) > _as_aware_utc(fam.public_reset_code_expires_at):
        raise ValueError("Codigo expirado. Solicite novamente.")

    if not verify_password(str(code or "").strip(), fam.public_reset_code_hash):
        raise ValueError("Codigo invalido.")

    fam.public_pin_hash = get_password_hash(str(new_pin).strip())
    fam.public_reset_code_hash = None
    fam.public_reset_code_expires_at = None
    db.commit()
    db.refresh(fam)
    return fam


def verify_public_pin_recovery(db: Session, *, tenant_id: int, email: str, code: str) -> None:
    """Validate recovery code without changing PIN (used to unlock step 3 in UI)."""
    normalized_email = _normalize_email(email)
    if not normalized_email:
        raise ValueError("Informe o e-mail.")

    fam = (
        db.query(ChildCheckinFamily)
        .filter(
            ChildCheckinFamily.tenant_id == tenant_id,
            ChildCheckinFamily.is_active.is_(True),
            ChildCheckinFamily.email.isnot(None),
            func.lower(ChildCheckinFamily.email) == normalized_email,
        )
        .first()
    )
    if fam is None or not fam.public_reset_code_hash or not fam.public_reset_code_expires_at:
        raise ValueError("Codigo invalido.")

    if datetime.now(timezone.utc) > _as_aware_utc(fam.public_reset_code_expires_at):
        raise ValueError("Codigo expirado. Solicite novamente.")

    if not verify_password(str(code or "").strip(), fam.public_reset_code_hash):
        raise ValueError("Codigo invalido.")


def get_virtual_cards_by_family_code(
    db: Session,
    *,
    tenant_id: int,
    tenant_slug: str,
    family_code: str,
) -> tuple[ChildCheckinFamily | None, list[dict]]:
    normalized_code = str(family_code or "").strip().upper()
    if not normalized_code:
        return None, []

    family = (
        db.query(ChildCheckinFamily)
        .filter(
            ChildCheckinFamily.tenant_id == tenant_id,
            func.upper(ChildCheckinFamily.family_code) == normalized_code,
            ChildCheckinFamily.is_active.is_(True),
        )
        .first()
    )
    if family is None:
        return None, []

    children = (
        db.query(ChildCheckinChild)
        .filter(
            ChildCheckinChild.tenant_id == tenant_id,
            ChildCheckinChild.family_id == family.id,
            ChildCheckinChild.is_active.is_(True),
        )
        .order_by(ChildCheckinChild.full_name.asc())
        .all()
    )
    guardians = (
        db.query(ChildCheckinGuardian)
        .filter(
            ChildCheckinGuardian.tenant_id == tenant_id,
            ChildCheckinGuardian.family_id == family.id,
        )
        .order_by(ChildCheckinGuardian.full_name.asc())
        .all()
    )

    cards = _build_virtual_cards(
        tenant_slug=tenant_slug,
        family=family,
        children=children,
        guardians=guardians,
    )
    return family, cards


def list_room_active_children(
    db: Session,
    *,
    tenant_id: int,
    room_name: str,
    target_date: date | None = None,
    room_scope_restriction: set[str] | None = None,
) -> list[dict]:
    normalized_room = str(room_name or "").strip().lower()
    if not normalized_room:
        return []
    if room_scope_restriction and normalized_room not in room_scope_restriction:
        raise ValueError("Voce nao possui acesso para esta sala.")

    records_query = (
        db.query(ChildCheckinRecord)
        .filter(
            ChildCheckinRecord.tenant_id == tenant_id,
            func.lower(ChildCheckinRecord.room_name) == normalized_room,
            ChildCheckinRecord.status == "checked_in",
        )
        .order_by(ChildCheckinRecord.checkin_at.asc())
    )
    if target_date:
        start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
        end = start.replace(hour=23, minute=59, second=59)
        records_query = records_query.filter(
            ChildCheckinRecord.checkin_at >= start,
            ChildCheckinRecord.checkin_at <= end,
        )

    records = records_query.all()
    if not records:
        return []

    child_ids = {record.child_id for record in records}
    family_ids = {record.family_id for record in records}

    children = (
        db.query(ChildCheckinChild)
        .filter(ChildCheckinChild.tenant_id == tenant_id, ChildCheckinChild.id.in_(child_ids))
        .all()
    )
    families = (
        db.query(ChildCheckinFamily)
        .filter(ChildCheckinFamily.tenant_id == tenant_id, ChildCheckinFamily.id.in_(family_ids))
        .all()
    )
    child_by_id = {child.id: child for child in children}
    family_by_id = {family.id: family for family in families}

    entries: list[dict] = []
    for record in records:
        child = child_by_id.get(record.child_id)
        family = family_by_id.get(record.family_id)
        phone_primary = family.phone_primary if family else None
        entries.append(
            {
                "checkin_id": record.id,
                "child_id": record.child_id,
                "child_name": child.full_name if child else f"Crianca {record.child_id}",
                "child_photo_url": child.photo_url if child else None,
                "family_id": record.family_id,
                "family_name": family.family_name if family else f"Familia {record.family_id}",
                "primary_responsible_name": family.primary_responsible_name if family else None,
                "phone_primary": phone_primary,
                "whatsapp_link": _to_whatsapp_link(phone_primary),
                "room_name": record.room_name,
                "checkin_at": record.checkin_at,
                "alert_snapshot": record.alert_snapshot,
                "security_code": record.security_code,
            }
        )

    return entries
