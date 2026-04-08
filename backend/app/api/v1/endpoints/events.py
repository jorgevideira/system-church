from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db, require_editor
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.event import (
    EventCreate,
    EventPaymentResponse,
    EventPaymentWebhookPayload,
    EventRegistrationPublicCreate,
    EventRegistrationResponse,
    EventResponse,
    EventUpdate,
    PublicEventDetailResponse,
    PublicEventResponse,
    PublicEventRegistrationResponse,
)
from app.services import event_service

router = APIRouter()


@router.get("/", response_model=List[EventResponse])
def list_events(
    include_inactive: bool = True,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[EventResponse]:
    return event_service.list_events(db, current_tenant.id, include_inactive=include_inactive)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> EventResponse:
    return event_service.create_event(db, current_tenant.id, current_user.id, payload)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
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
    _user: User = Depends(require_editor),
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
    _user: User = Depends(require_editor),
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
    _user: User = Depends(require_editor),
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
    _user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[EventPaymentResponse]:
    event = event_service.get_event(db, event_id, current_tenant.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event_service.list_event_payments(db, event_id, current_tenant.id)


@router.post("/payments/{payment_id}/confirm", response_model=EventPaymentResponse)
def confirm_event_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_editor),
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
def event_payment_webhook(
    payload: EventPaymentWebhookPayload,
    db: Session = Depends(get_db),
) -> EventPaymentResponse:
    payment = event_service.apply_payment_webhook(db, payload)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment
