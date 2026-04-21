from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant, get_db, require_events_read, require_events_write
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.db.models.event_registration import EventRegistration
from app.schemas.event import (
    EventCreate,
    EventPaymentResponse,
    EventPaymentWebhookPayload,
    PaginatedEventPayments,
    PaginatedEventRegistrations,
    EventRegistrationPublicCreate,
    EventRegistrationResponse,
    EventResponse,
    EventUpdate,
    PublicEventDetailResponse,
    PublicEventPaymentStatusResponse,
    PublicEventResponse,
    PublicEventRegistrationResponse,
)
from app.schemas.event_notification import EventAnalyticsResponse, EventNotificationResponse
from app.schemas.event_checkin import EventCheckInRequest, EventCheckInResponse
from app.services import event_checkin_service, event_notification_service, event_service, mercadopago_service

router = APIRouter()


def _build_pages(total: int, size: int) -> int:
    if total <= 0:
        return 1
    return (total + size - 1) // size


@router.get("/", response_model=List[EventResponse])
def list_events(
    include_inactive: bool = True,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[EventResponse]:
    return event_service.list_events(db, current_tenant.id, include_inactive=include_inactive)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_events_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventResponse:
    return event_service.create_event(db, current_tenant.id, current_user.id, payload)


@router.get("/registrations", response_model=PaginatedEventRegistrations)
def list_registrations(
    event_id: int | None = None,
    search: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    payment_status: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PaginatedEventRegistrations:
    if event_id is not None:
        event = event_service.get_event(db, event_id, current_tenant.id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    items, total = event_service.list_registrations_paginated(
        db,
        current_tenant.id,
        event_id=event_id,
        search=search,
        status=status_filter,
        payment_status=payment_status,
        page=page,
        size=size,
    )
    return PaginatedEventRegistrations(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=_build_pages(total, size),
    )


@router.get("/payments", response_model=PaginatedEventPayments)
def list_payments(
    event_id: int | None = None,
    search: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    payment_method: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PaginatedEventPayments:
    if event_id is not None:
        event = event_service.get_event(db, event_id, current_tenant.id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    items, total = event_service.list_payments_paginated(
        db,
        current_tenant.id,
        event_id=event_id,
        search=search,
        status=status_filter,
        payment_method=payment_method,
        page=page,
        size=size,
    )
    return PaginatedEventPayments(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=_build_pages(total, size),
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventResponse:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventResponse:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event_service.update_event(db, event, payload)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event_service.delete_event(db, event)


@router.get("/{event_id}/registrations", response_model=List[EventRegistrationResponse])
def list_event_registrations(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[EventRegistrationResponse]:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event_service.list_event_registrations(db, event_id, current_tenant.id)


@router.get("/{event_id}/payments", response_model=List[EventPaymentResponse])
def list_event_payments(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[EventPaymentResponse]:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event_service.list_event_payments(db, event_id, current_tenant.id)


@router.get("/{event_id}/notifications", response_model=List[EventNotificationResponse])
def list_event_notifications(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[EventNotificationResponse]:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event_notification_service.list_notifications(db, event_id, current_tenant.id)


@router.get("/{event_id}/analytics", response_model=EventAnalyticsResponse)
def get_event_analytics(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventAnalyticsResponse:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event_notification_service.build_event_analytics(db, event)


@router.post("/payments/{payment_id}/confirm", response_model=EventPaymentResponse)
def confirm_event_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventPaymentResponse:
    payment = event_service.get_payment(db, payment_id, current_tenant.id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    webhook_payload = EventPaymentWebhookPayload(
        checkout_reference=payment.checkout_reference,
        status="paid",
        provider_reference=payment.provider_reference,
        provider_payload={"source": "manual_admin_confirmation"},
    )
    updated = event_service.apply_payment_webhook(db, webhook_payload)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return updated


@router.post("/payments/{payment_id}/refund", response_model=EventPaymentResponse)
def refund_event_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventPaymentResponse:
    payment = event_service.get_payment(db, payment_id, current_tenant.id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    try:
        return event_service.refund_payment(db, payment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/checkin", response_model=EventCheckInResponse)
def check_in_participant(
    payload: EventCheckInRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_events_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventCheckInResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    status_key, registration, checkin, attendee = event_checkin_service.check_in_by_public_token(
        db,
        tenant_id=current_tenant.id,
        public_token=payload.token,
        checked_in_by_user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    if status_key == "invalid_token":
        return EventCheckInResponse(status="invalid", message="QR Code inválido ou inscrição não encontrada.")
    if status_key == "not_paid":
        return EventCheckInResponse(
            status="not_paid",
            message="Inscrição não está confirmada (pagamento pendente).",
            event_id=registration.event_id if registration else None,
            registration_id=registration.id if registration else None,
            attendee_id=attendee.id if attendee else None,
            attendee_index=attendee.attendee_index if attendee else None,
            attendee_name=attendee.attendee_name if attendee else (registration.attendee_name if registration else None),
            attendee_email=str(registration.attendee_email) if registration else None,
        )
    if status_key == "duplicate":
        return EventCheckInResponse(
            status="duplicate",
            message="Check-in já registrado para esta inscrição.",
            event_id=registration.event_id if registration else None,
            registration_id=registration.id if registration else None,
            attendee_id=attendee.id if attendee else None,
            attendee_index=attendee.attendee_index if attendee else None,
            attendee_name=attendee.attendee_name if attendee else (registration.attendee_name if registration else None),
            attendee_email=str(registration.attendee_email) if registration else None,
            checked_in_at=checkin.checked_in_at if checkin else None,
        )
    return EventCheckInResponse(
        status="success",
        message="Check-in confirmado.",
        event_id=registration.event_id if registration else None,
        registration_id=registration.id if registration else None,
        attendee_id=attendee.id if attendee else None,
        attendee_index=attendee.attendee_index if attendee else None,
        attendee_name=attendee.attendee_name if attendee else (registration.attendee_name if registration else None),
        attendee_email=str(registration.attendee_email) if registration else None,
        checked_in_at=checkin.checked_in_at if checkin else None,
    )


@router.get("/{event_id}/checkins", response_model=list[dict])
def list_event_checkins(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_events_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[dict]:
    rows = event_checkin_service.list_event_checkins(db, tenant_id=current_tenant.id, event_id=event_id)
    registration_ids = [row.registration_id for row in rows]
    registrations = []
    if registration_ids:
        registrations = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.tenant_id == current_tenant.id,
                EventRegistration.id.in_(registration_ids),
            )
            .all()
        )
    registrations_by_id = {reg.id: reg for reg in registrations}
    attendee_ids = [row.attendee_id for row in rows if row.attendee_id]
    attendees = []
    if attendee_ids:
        from app.db.models.event_registration_attendee import EventRegistrationAttendee

        attendees = (
            db.query(EventRegistrationAttendee)
            .filter(EventRegistrationAttendee.tenant_id == current_tenant.id, EventRegistrationAttendee.id.in_(attendee_ids))
            .all()
        )
    attendees_by_id = {a.id: a for a in attendees}
    return [
        {
            "id": row.id,
            "event_id": row.event_id,
            "registration_id": row.registration_id,
            "attendee_id": row.attendee_id,
            "attendee_index": getattr(attendees_by_id.get(row.attendee_id), "attendee_index", None),
            "attendee_name": getattr(attendees_by_id.get(row.attendee_id), "attendee_name", None)
            or getattr(registrations_by_id.get(row.registration_id), "attendee_name", None),
            "attendee_email": getattr(registrations_by_id.get(row.registration_id), "attendee_email", None),
            "checked_in_at": row.checked_in_at,
            "checked_in_by_user_id": row.checked_in_by_user_id,
            "source": row.source,
        }
        for row in rows
    ]


@router.get("/public/registrations/{public_token}/qr.png", response_class=Response)
def public_registration_qr_png(public_token: str, db: Session = Depends(get_db)) -> Response:
    # Backwards compatible: accept old registration tokens or new attendee tokens.
    token = (public_token or "").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    from app.services import qr_service
    from app.db.models.event_registration_attendee import EventRegistrationAttendee

    attendee = db.query(EventRegistrationAttendee).filter(EventRegistrationAttendee.public_token == token).first()
    if attendee is None:
        reg = db.query(EventRegistration).filter(EventRegistration.public_token == token).first()
        if reg is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        png = qr_service.build_qr_png(reg.public_token)
        return Response(content=png, media_type="image/png")

    png = qr_service.build_qr_png(attendee.public_token)
    return Response(content=png, media_type="image/png")


@router.get("/public/registrations/{public_token}", response_model=EventRegistrationResponse)
def get_public_registration(
    public_token: str,
    db: Session = Depends(get_db),
) -> EventRegistrationResponse:
    registration = event_service.get_registration_by_public_token(db, public_token)
    if registration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return registration


@router.get("/public/tenants/{tenant_slug}/events", response_model=List[PublicEventResponse])
def list_public_events(
    tenant_slug: str,
    db: Session = Depends(get_db),
) -> List[PublicEventResponse]:
    tenant, events = event_service.list_public_events(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return [PublicEventResponse.model_validate(event) for event in events]


@router.get("/public/payments/{checkout_reference}", response_model=PublicEventPaymentStatusResponse)
def get_public_payment_status(
    checkout_reference: str,
    db: Session = Depends(get_db),
) -> PublicEventPaymentStatusResponse:
    tenant, event, registration, payment = event_service.get_public_payment_status(db, checkout_reference)
    if tenant is None or event is None or registration is None or payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment status not found")
    return PublicEventPaymentStatusResponse(
        tenant_slug=tenant.slug,
        event=PublicEventResponse.model_validate(event),
        registration=registration,
        payment=payment,
    )


@router.get("/public/{tenant_slug}/{event_slug}", response_model=PublicEventDetailResponse)
def get_public_event(
    tenant_slug: str,
    event_slug: str,
    db: Session = Depends(get_db),
) -> PublicEventDetailResponse:
    tenant, event = event_service.get_public_event(db, tenant_slug, event_slug)
    if tenant is None or event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public event not found")
    return PublicEventDetailResponse(
        tenant_slug=tenant.slug,
        event=PublicEventResponse.model_validate(event),
        available_slots=event_service.get_available_slots(db, event),
    )


@router.post("/public/{tenant_slug}/{event_slug}/registrations", response_model=PublicEventRegistrationResponse, status_code=status.HTTP_201_CREATED)
def create_public_registration(
    tenant_slug: str,
    event_slug: str,
    payload: EventRegistrationPublicCreate,
    db: Session = Depends(get_db),
) -> PublicEventRegistrationResponse:
    tenant, event = event_service.get_public_event(db, tenant_slug, event_slug)
    if tenant is None or event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Public event not found")
    try:
        registration, payment = event_service.create_public_registration(db, tenant, event, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PublicEventRegistrationResponse(
        event=PublicEventResponse.model_validate(event),
        registration=registration,
        payment=payment,
    )


@router.post("/public/payments/webhook", response_model=EventPaymentResponse)
async def event_payment_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> EventPaymentResponse:
    query_params = request.query_params
    payload_json: dict[str, Any] = {}
    if request.headers.get("content-type", "").startswith("application/json"):
        payload_json = await request.json()

    provider_payment_id = (
        query_params.get("data.id")
        or query_params.get("id")
        or (payload_json.get("data") or {}).get("id")
        or payload_json.get("id")
    )
    is_pagbank_payload = bool(payload_json.get("charges")) or bool(payload_json.get("reference_id"))
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")

    if provider_payment_id and not is_pagbank_payload:
        if mercadopago_service.is_enabled() and not mercadopago_service.validate_webhook_signature(
            data_id=str(provider_payment_id),
            x_signature=x_signature,
            x_request_id=x_request_id,
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")
        payment = event_service.apply_mercadopago_webhook(db, str(provider_payment_id))
    elif is_pagbank_payload:
        payment = event_service.apply_pagbank_webhook(db, payload_json)
    else:
        payload = EventPaymentWebhookPayload.model_validate(payload_json)
        payment = event_service.apply_payment_webhook(db, payload)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
