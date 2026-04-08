import re
import secrets
import unicodedata
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.category import Category
from app.db.models.event import Event
from app.db.models.event_payment import EventPayment
from app.db.models.event_registration import EventRegistration
from app.db.models.tenant import Tenant
from app.core.config import settings
from app.schemas.event import EventCreate, EventPaymentWebhookPayload, EventRegistrationPublicCreate, EventUpdate
from app.schemas.transaction import TransactionCreate
from app.services import event_notification_service, mercadopago_service, transaction_service


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or secrets.token_hex(4)


def _build_unique_event_slug(
    db: Session,
    tenant_id: int,
    title: str,
    requested_slug: Optional[str] = None,
    exclude_event_id: Optional[int] = None,
) -> str:
    base_slug = _slugify(requested_slug or title)
    slug = base_slug
    counter = 2
    while True:
        q = db.query(Event.id).filter(Event.tenant_id == tenant_id, Event.slug == slug)
        if exclude_event_id is not None:
            q = q.filter(Event.id != exclude_event_id)
        if q.first() is None:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def list_events(db: Session, tenant_id: int, include_inactive: bool = True) -> list[Event]:
    q = db.query(Event).filter(Event.tenant_id == tenant_id)
    if not include_inactive:
        q = q.filter(Event.is_active.is_(True))
    return q.order_by(Event.start_at.desc(), Event.id.desc()).all()


def get_event(db: Session, event_id: int, tenant_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id, Event.tenant_id == tenant_id).first()


def create_event(db: Session, tenant_id: int, user_id: int, payload: EventCreate) -> Event:
    data = payload.model_dump()
    data["slug"] = _build_unique_event_slug(db, tenant_id, payload.title, payload.slug)
    event = Event(**data, tenant_id=tenant_id, created_by_user_id=user_id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_event(db: Session, event: Event, payload: EventUpdate) -> Event:
    changes = payload.model_dump(exclude_unset=True)
    if "slug" in changes or "title" in changes:
        changes["slug"] = _build_unique_event_slug(
            db,
            event.tenant_id,
            changes.get("title", event.title),
            changes.get("slug", event.slug),
            exclude_event_id=event.id,
        )
        if changes["slug"] == event.slug:
            changes.pop("slug", None)
    for field, value in changes.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: Event) -> None:
    db.delete(event)
    db.commit()


def list_event_registrations(db: Session, event_id: int, tenant_id: int) -> list[EventRegistration]:
    return (
        db.query(EventRegistration)
        .filter(EventRegistration.tenant_id == tenant_id, EventRegistration.event_id == event_id)
        .order_by(EventRegistration.created_at.desc(), EventRegistration.id.desc())
        .all()
    )


def list_event_payments(db: Session, event_id: int, tenant_id: int) -> list[EventPayment]:
    return (
        db.query(EventPayment)
        .filter(EventPayment.tenant_id == tenant_id, EventPayment.event_id == event_id)
        .order_by(EventPayment.created_at.desc(), EventPayment.id.desc())
        .all()
    )


def get_payment(db: Session, payment_id: int, tenant_id: int) -> Optional[EventPayment]:
    return db.query(EventPayment).filter(EventPayment.id == payment_id, EventPayment.tenant_id == tenant_id).first()


def get_registration_by_public_token(db: Session, public_token: str) -> Optional[EventRegistration]:
    return db.query(EventRegistration).filter(EventRegistration.public_token == public_token).first()


def get_public_event(db: Session, tenant_slug: str, event_slug: str) -> tuple[Optional[Tenant], Optional[Event]]:
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug, Tenant.is_active.is_(True)).first()
    if tenant is None:
        return None, None
    event = (
        db.query(Event)
        .filter(
            Event.tenant_id == tenant.id,
            Event.slug == event_slug,
            Event.is_active.is_(True),
            Event.visibility == "public",
        )
        .first()
    )
    return tenant, event


def list_public_events(db: Session, tenant_slug: str) -> tuple[Optional[Tenant], list[Event]]:
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug, Tenant.is_active.is_(True)).first()
    if tenant is None:
        return None, []
    events = (
        db.query(Event)
        .filter(
            Event.tenant_id == tenant.id,
            Event.visibility == "public",
            Event.is_active.is_(True),
            Event.status == "published",
        )
        .order_by(Event.start_at.asc(), Event.id.asc())
        .all()
    )
    return tenant, events


def count_reserved_slots(db: Session, event_id: int, tenant_id: int) -> int:
    rows = (
        db.query(EventRegistration.quantity)
        .filter(
            EventRegistration.tenant_id == tenant_id,
            EventRegistration.event_id == event_id,
            EventRegistration.status.in_(["pending_payment", "confirmed"]),
        )
        .all()
    )
    return int(sum(row.quantity for row in rows))


def get_available_slots(db: Session, event: Event) -> Optional[int]:
    if event.capacity is None:
        return None
    return max(event.capacity - count_reserved_slots(db, event.id, event.tenant_id), 0)


def _generate_registration_code() -> str:
    return secrets.token_hex(6).upper()


def _generate_public_token() -> str:
    return secrets.token_urlsafe(24)


def _generate_checkout_reference(event: Event, registration_code: str) -> str:
    return f"evt_{event.id}_{registration_code}_{secrets.token_hex(4)}"


def _build_pix_copy_paste(checkout_reference: str, amount: Decimal) -> str:
    return f"PIX|ref={checkout_reference}|amount={amount:.2f}|currency=BRL"


def _build_internal_checkout_url(checkout_reference: str) -> str:
    return f"{settings.PUBLIC_APP_URL}/events/registration/{checkout_reference}"


def _assert_event_open_for_registration(event: Event) -> None:
    now = datetime.now(timezone.utc)
    if event.status != "published":
        raise ValueError("Event is not available for registration")
    if not event.allow_public_registration:
        raise ValueError("Public registration is disabled for this event")
    if event.registration_opens_at and event.registration_opens_at > now:
        raise ValueError("Registration has not opened yet")
    if event.registration_closes_at and event.registration_closes_at < now:
        raise ValueError("Registration is closed")


def create_public_registration(
    db: Session,
    tenant: Tenant,
    event: Event,
    payload: EventRegistrationPublicCreate,
) -> tuple[EventRegistration, Optional[EventPayment]]:
    _assert_event_open_for_registration(event)

    if payload.quantity > event.max_registrations_per_order:
        raise ValueError("Quantity exceeds the event limit per registration")

    available_slots = get_available_slots(db, event)
    if available_slots is not None and payload.quantity > available_slots:
        raise ValueError("Not enough available slots for this event")

    total_amount = Decimal(event.price_per_registration) * payload.quantity
    payment_required = event.require_payment or total_amount > Decimal("0.00")
    payment_method = payload.payment_method
    if payment_required and payment_method is None:
        raise ValueError("payment_method is required for paid events")

    registration = EventRegistration(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_code=_generate_registration_code(),
        public_token=_generate_public_token(),
        attendee_name=payload.attendee_name,
        attendee_email=str(payload.attendee_email),
        attendee_phone=payload.attendee_phone,
        attendee_document=payload.attendee_document,
        quantity=payload.quantity,
        payment_method=payment_method,
        payment_status="pending" if payment_required else "not_required",
        status="pending_payment" if payment_required else "confirmed",
        total_amount=total_amount,
        currency=event.currency,
        notes=payload.notes,
        confirmed_at=None if payment_required else datetime.now(timezone.utc),
    )
    db.add(registration)
    db.flush()

    payment = None
    if payment_required:
        checkout_reference = _generate_checkout_reference(event, registration.registration_code)
        provider = "mercadopago" if mercadopago_service.is_enabled() else "internal"
        checkout_url = None
        pix_copy_paste = None
        provider_payload: dict | None = None
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

        if provider == "mercadopago":
            preference = mercadopago_service.create_checkout_preference(
                tenant_slug=tenant.slug,
                event_title=event.title,
                registration_code=registration.registration_code,
                checkout_reference=checkout_reference,
                amount=total_amount,
                quantity=payload.quantity,
                attendee_name=payload.attendee_name,
                attendee_email=str(payload.attendee_email),
                preferred_method=payment_method,
            )
            checkout_url = preference.get("init_point") or preference.get("sandbox_init_point")
            provider_payload = preference
            pix_copy_paste = None
            expires_at = None
        else:
            checkout_url = _build_internal_checkout_url(checkout_reference)
            pix_copy_paste = _build_pix_copy_paste(checkout_reference, total_amount) if payment_method == "pix" else None
            provider_payload = {
                "mode": "gateway_ready",
                "message": "Set PAYMENT_PROVIDER=mercadopago and credentials to enable live checkout.",
            }

        payment = EventPayment(
            tenant_id=tenant.id,
            event_id=event.id,
            registration_id=registration.id,
            provider=provider,
            payment_method=payment_method or "pix",
            status="pending",
            amount=total_amount,
            currency=event.currency,
            checkout_reference=checkout_reference,
            checkout_url=checkout_url,
            pix_copy_paste=pix_copy_paste,
            expires_at=expires_at,
            provider_payload=provider_payload,
        )
        db.add(payment)

    db.commit()
    db.refresh(registration)
    if payment is not None:
        db.refresh(payment)
    event_notification_service.enqueue_registration_notifications(
        db,
        event=event,
        registration=registration,
        phase="registration_created",
    )
    return registration, payment


def get_payment_by_reference(db: Session, checkout_reference: str) -> Optional[EventPayment]:
    return db.query(EventPayment).filter(EventPayment.checkout_reference == checkout_reference).first()


def get_public_payment_status(
    db: Session,
    checkout_reference: str,
) -> tuple[Optional[Event], Optional[EventRegistration], Optional[EventPayment]]:
    payment = get_payment_by_reference(db, checkout_reference)
    if payment is None:
        return None, None, None
    registration = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.id == payment.registration_id,
            EventRegistration.tenant_id == payment.tenant_id,
        )
        .first()
    )
    event = (
        db.query(Event)
        .filter(
            Event.id == payment.event_id,
            Event.tenant_id == payment.tenant_id,
            Event.visibility == "public",
            Event.is_active.is_(True),
        )
        .first()
    )
    return event, registration, payment


def _find_events_income_category(db: Session, tenant_id: int) -> Optional[Category]:
    return (
        db.query(Category)
        .filter(
            Category.tenant_id == tenant_id,
            Category.name == "Events",
            Category.is_active.is_(True),
        )
        .first()
    )


def _ensure_income_transaction(db: Session, event: Event, registration: EventRegistration, payment: EventPayment) -> None:
    if payment.transaction_id is not None:
        return

    category = _find_events_income_category(db, event.tenant_id)
    transaction = transaction_service.create_transaction(
        db,
        TransactionCreate(
            description=f"Inscricao evento: {event.title}",
            amount=Decimal(payment.amount),
            transaction_type="income",
            transaction_date=(payment.paid_at or datetime.now(timezone.utc)).date(),
            category_id=category.id if category else None,
            reference=f"event_registration:{registration.id}",
            notes=f"{registration.attendee_name} - {registration.quantity} inscricao(oes)",
        ),
        user_id=event.created_by_user_id,
        tenant_id=event.tenant_id,
    )
    payment.transaction_id = transaction.id


def apply_payment_webhook(db: Session, payload: EventPaymentWebhookPayload) -> Optional[EventPayment]:
    payment = get_payment_by_reference(db, payload.checkout_reference)
    if payment is None:
        return None

    registration = (
        db.query(EventRegistration)
        .filter(
            EventRegistration.id == payment.registration_id,
            EventRegistration.tenant_id == payment.tenant_id,
        )
        .first()
    )
    event = (
        db.query(Event)
        .filter(Event.id == payment.event_id, Event.tenant_id == payment.tenant_id)
        .first()
    )
    if registration is None or event is None:
        return payment

    payment.status = payload.status
    payment.provider_reference = payload.provider_reference
    payment.provider_payload = payload.provider_payload or payment.provider_payload
    if payload.status == "paid":
        payment.paid_at = payload.paid_at or datetime.now(timezone.utc)
        registration.payment_status = "paid"
        registration.status = "confirmed"
        registration.confirmed_at = payment.paid_at
        _ensure_income_transaction(db, event, registration, payment)
        db.commit()
        db.refresh(payment)
        event_notification_service.enqueue_registration_notifications(
            db,
            event=event,
            registration=registration,
            phase="payment_confirmed",
        )
        return payment
    elif payload.status in {"failed", "expired", "cancelled", "refunded"}:
        registration.payment_status = payload.status
        if payload.status in {"expired", "cancelled"}:
            registration.status = "expired" if payload.status == "expired" else "cancelled"
        elif payload.status == "refunded":
            registration.status = "refunded"

    db.commit()
    db.refresh(payment)
    return payment


def apply_mercadopago_webhook(db: Session, provider_payment_id: str) -> Optional[EventPayment]:
    payment_data = mercadopago_service.fetch_payment(provider_payment_id)
    checkout_reference = payment_data.get("external_reference")
    if not checkout_reference:
        return None

    webhook_payload = EventPaymentWebhookPayload(
        checkout_reference=checkout_reference,
        status=mercadopago_service.map_payment_status(payment_data.get("status")),
        provider_reference=str(payment_data.get("id")),
        paid_at=mercadopago_service.parse_paid_at(payment_data),
        provider_payload=payment_data,
    )
    return apply_payment_webhook(db, webhook_payload)
