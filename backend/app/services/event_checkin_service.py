from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.event_checkin import EventCheckIn
from app.db.models.event_checkin_attempt import EventCheckInAttempt
from app.db.models.event_registration import EventRegistration


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    normalized = (token or "").strip()
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _log_attempt(
    db: Session,
    *,
    tenant_id: int,
    event_id: int | None,
    registration_id: int | None,
    checked_in_by_user_id: int | None,
    token: str,
    status: str,
    error_message: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    attempt = EventCheckInAttempt(
        tenant_id=tenant_id,
        event_id=event_id,
        registration_id=registration_id,
        checked_in_by_user_id=checked_in_by_user_id,
        token_hash=_hash_token(token) or None,
        status=status,
        error_message=(error_message or "")[:500] if error_message else None,
        ip_address=(ip_address or "")[:64] if ip_address else None,
        user_agent=(user_agent or "")[:255] if user_agent else None,
    )
    db.add(attempt)


def check_in_by_public_token(
    db: Session,
    *,
    tenant_id: int,
    public_token: str,
    checked_in_by_user_id: int | None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> tuple[str, Optional[EventRegistration], Optional[EventCheckIn]]:
    token = (public_token or "").strip()
    registration = (
        db.query(EventRegistration)
        .filter(EventRegistration.tenant_id == tenant_id, EventRegistration.public_token == token)
        .first()
    )
    if registration is None:
        _log_attempt(
            db,
            tenant_id=tenant_id,
            event_id=None,
            registration_id=None,
            checked_in_by_user_id=checked_in_by_user_id,
            token=token,
            status="invalid_token",
            error_message="Registration not found",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.commit()
        return "invalid_token", None, None

    if registration.payment_status != "paid" or registration.status != "confirmed":
        _log_attempt(
            db,
            tenant_id=tenant_id,
            event_id=registration.event_id,
            registration_id=registration.id,
            checked_in_by_user_id=checked_in_by_user_id,
            token=token,
            status="not_paid",
            error_message="Registration not paid",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.commit()
        return "not_paid", registration, None

    existing = (
        db.query(EventCheckIn)
        .filter(EventCheckIn.tenant_id == tenant_id, EventCheckIn.registration_id == registration.id)
        .first()
    )
    if existing is not None:
        _log_attempt(
            db,
            tenant_id=tenant_id,
            event_id=registration.event_id,
            registration_id=registration.id,
            checked_in_by_user_id=checked_in_by_user_id,
            token=token,
            status="duplicate",
            error_message="Already checked in",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.commit()
        return "duplicate", registration, existing

    checkin = EventCheckIn(
        tenant_id=tenant_id,
        event_id=registration.event_id,
        registration_id=registration.id,
        checked_in_at=_utc_now(),
        checked_in_by_user_id=checked_in_by_user_id,
        source="qr",
        meta={"ip": ip_address, "ua": user_agent},
    )
    db.add(checkin)
    _log_attempt(
        db,
        tenant_id=tenant_id,
        event_id=registration.event_id,
        registration_id=registration.id,
        checked_in_by_user_id=checked_in_by_user_id,
        token=token,
        status="success",
        error_message=None,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # A concurrent check-in might have won the race.
        existing = (
            db.query(EventCheckIn)
            .filter(EventCheckIn.tenant_id == tenant_id, EventCheckIn.registration_id == registration.id)
            .first()
        )
        return "duplicate", registration, existing
    db.refresh(checkin)
    return "success", registration, checkin


def list_event_checkins(db: Session, *, tenant_id: int, event_id: int) -> list[EventCheckIn]:
    return (
        db.query(EventCheckIn)
        .filter(EventCheckIn.tenant_id == tenant_id, EventCheckIn.event_id == event_id)
        .order_by(EventCheckIn.checked_in_at.desc(), EventCheckIn.id.desc())
        .all()
    )
