from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.event_checkin import EventCheckIn
from app.db.models.event_checkin_attempt import EventCheckInAttempt
from app.db.models.event_registration import EventRegistration
from app.db.models.event_registration_attendee import EventRegistrationAttendee


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
) -> tuple[str, Optional[EventRegistration], Optional[EventCheckIn], Optional[EventRegistrationAttendee]]:
    token = (public_token or "").strip()
    attendee = (
        db.query(EventRegistrationAttendee)
        .filter(EventRegistrationAttendee.tenant_id == tenant_id, EventRegistrationAttendee.public_token == token)
        .first()
    )
    registration = None
    if attendee is not None:
        registration = (
            db.query(EventRegistration)
            .filter(EventRegistration.tenant_id == tenant_id, EventRegistration.id == attendee.registration_id)
            .first()
        )
    if registration is None:
        # Backwards compatible: allow scanning the old "order/registration" token.
        registration = (
            db.query(EventRegistration)
            .filter(EventRegistration.tenant_id == tenant_id, EventRegistration.public_token == token)
            .first()
        )
        if registration is not None:
            attendee = (
                db.query(EventRegistrationAttendee)
                .filter(
                    EventRegistrationAttendee.tenant_id == tenant_id,
                    EventRegistrationAttendee.registration_id == registration.id,
                )
                .order_by(EventRegistrationAttendee.attendee_index.asc(), EventRegistrationAttendee.id.asc())
                .all()
            )
            # Pick the first attendee without a check-in (supports multi-ticket orders).
            attendee_by_id = {row.id: row for row in attendee}
            checked = (
                db.query(EventCheckIn.attendee_id)
                .filter(
                    EventCheckIn.tenant_id == tenant_id,
                    EventCheckIn.registration_id == registration.id,
                    EventCheckIn.attendee_id.isnot(None),
                )
                .all()
            )
            checked_ids = {row.attendee_id for row in checked if row.attendee_id}
            candidate = next((row for row in attendee if row.id not in checked_ids), None)
            attendee = candidate

    if registration is None or attendee is None:
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
        return "invalid_token", None, None, None

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
        return "not_paid", registration, None, attendee

    existing = (
        db.query(EventCheckIn)
        .filter(EventCheckIn.tenant_id == tenant_id, EventCheckIn.attendee_id == attendee.id)
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
        return "duplicate", registration, existing, attendee

    checkin = EventCheckIn(
        tenant_id=tenant_id,
        event_id=registration.event_id,
        registration_id=registration.id,
        attendee_id=attendee.id,
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
            .filter(EventCheckIn.tenant_id == tenant_id, EventCheckIn.attendee_id == attendee.id)
            .first()
        )
        return "duplicate", registration, existing, attendee
    db.refresh(checkin)
    return "success", registration, checkin, attendee


def list_event_checkins(db: Session, *, tenant_id: int, event_id: int) -> list[EventCheckIn]:
    return (
        db.query(EventCheckIn)
        .filter(EventCheckIn.tenant_id == tenant_id, EventCheckIn.event_id == event_id)
        .order_by(EventCheckIn.checked_in_at.desc(), EventCheckIn.id.desc())
        .all()
    )
