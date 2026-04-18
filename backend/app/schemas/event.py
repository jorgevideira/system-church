from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator


EVENT_STATUSES = {"draft", "published", "cancelled", "completed"}
EVENT_VISIBILITIES = {"public", "private"}
EVENT_PAYMENT_METHODS = {"pix", "card"}
EVENT_PAYMENT_STATUSES = {"not_required", "pending", "paid", "failed", "expired", "cancelled", "refunded"}
EVENT_REGISTRATION_STATUSES = {"pending_payment", "confirmed", "cancelled", "expired", "refunded"}
EVENT_GATEWAY_PAYMENT_STATUSES = {"pending", "paid", "failed", "expired", "cancelled", "refunded"}


class EventBase(BaseModel):
    payment_account_id: Optional[int] = None
    title: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    timezone_name: str = "America/Sao_Paulo"
    visibility: str = "public"
    status: str = "draft"
    start_at: datetime
    end_at: datetime
    registration_opens_at: Optional[datetime] = None
    registration_closes_at: Optional[datetime] = None
    capacity: Optional[int] = None
    max_registrations_per_order: int = 1
    price_per_registration: Decimal = Decimal("0.00")
    currency: str = "BRL"
    allow_public_registration: bool = True
    require_payment: bool = False
    is_active: bool = True

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, value: str) -> str:
        if value not in EVENT_VISIBILITIES:
            raise ValueError("visibility must be public or private")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in EVENT_STATUSES:
            raise ValueError("status must be draft, published, cancelled or completed")
        return value

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 1:
            raise ValueError("capacity must be greater than zero")
        return value

    @field_validator("max_registrations_per_order")
    @classmethod
    def validate_max_registrations(cls, value: int) -> int:
        if value < 1:
            raise ValueError("max_registrations_per_order must be at least 1")
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "EventBase":
        if self.end_at < self.start_at:
            raise ValueError("end_at must be greater than or equal to start_at")
        if self.registration_opens_at and self.registration_closes_at and self.registration_closes_at < self.registration_opens_at:
            raise ValueError("registration_closes_at must be greater than or equal to registration_opens_at")
        return self


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    payment_account_id: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    timezone_name: Optional[str] = None
    visibility: Optional[str] = None
    status: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    registration_opens_at: Optional[datetime] = None
    registration_closes_at: Optional[datetime] = None
    capacity: Optional[int] = None
    max_registrations_per_order: Optional[int] = None
    price_per_registration: Optional[Decimal] = None
    currency: Optional[str] = None
    allow_public_registration: Optional[bool] = None
    require_payment: Optional[bool] = None
    is_active: Optional[bool] = None


class EventResponse(EventBase):
    id: int
    tenant_id: Optional[int] = None
    created_by_user_id: int
    payment_account_provider: Optional[str] = None
    payment_account_label: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicEventResponse(EventBase):
    id: int
    slug: str
    payment_account_provider: Optional[str] = None
    payment_account_label: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventRegistrationPublicCreate(BaseModel):
    attendee_name: str
    attendee_email: EmailStr
    attendee_phone: Optional[str] = None
    attendee_document: Optional[str] = None
    quantity: int = 1
    # Optional: explicit names for each ticket/inscricao.
    # If omitted, we will assume all tickets are in `attendee_name`.
    attendee_names: Optional[list[str]] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value < 1:
            raise ValueError("quantity must be at least 1")
        return value

    @model_validator(mode="after")
    def validate_attendee_names(self) -> "EventRegistrationPublicCreate":
        if self.attendee_names is None:
            return self
        names = [str(name or "").strip() for name in self.attendee_names]
        if not names:
            raise ValueError("attendee_names must not be empty")
        if len(names) != int(self.quantity or 0):
            raise ValueError("attendee_names length must match quantity")
        for name in names:
            if len(name) < 2:
                raise ValueError("each attendee name must have at least 2 characters")
        self.attendee_names = names
        return self


class EventRegistrationAttendeeResponse(BaseModel):
    id: int
    attendee_index: int
    attendee_name: str
    public_token: str

    model_config = {"from_attributes": True}

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in EVENT_PAYMENT_METHODS:
            raise ValueError("payment_method must be pix or card")
        return value


class EventRegistrationResponse(BaseModel):
    id: int
    tenant_id: Optional[int] = None
    event_id: int
    registration_code: str
    public_token: str
    attendee_name: str
    attendee_email: EmailStr
    attendee_phone: Optional[str] = None
    attendee_document: Optional[str] = None
    quantity: int
    status: str
    payment_method: Optional[str] = None
    payment_status: str
    total_amount: Decimal
    currency: str
    notes: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    attendees: list[EventRegistrationAttendeeResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventPaymentResponse(BaseModel):
    id: int
    tenant_id: Optional[int] = None
    event_id: int
    registration_id: int
    payment_account_id: Optional[int] = None
    transaction_id: Optional[int] = None
    provider: str
    payment_method: str
    status: str
    amount: Decimal
    currency: str
    checkout_reference: str
    provider_reference: Optional[str] = None
    checkout_url: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    provider_payload: Optional[dict] = None
    expires_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicEventDetailResponse(BaseModel):
    tenant_slug: str
    event: PublicEventResponse
    available_slots: Optional[int] = None


class PublicEventRegistrationResponse(BaseModel):
    event: PublicEventResponse
    registration: EventRegistrationResponse
    payment: Optional[EventPaymentResponse] = None


class PublicEventPaymentStatusResponse(BaseModel):
    tenant_slug: Optional[str] = None
    event: PublicEventResponse
    registration: EventRegistrationResponse
    payment: EventPaymentResponse


class EventPaymentWebhookPayload(BaseModel):
    checkout_reference: str
    status: str
    provider_reference: Optional[str] = None
    paid_at: Optional[datetime] = None
    provider_payload: Optional[dict] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in EVENT_GATEWAY_PAYMENT_STATUSES:
            raise ValueError("status must be pending, paid, failed, expired, cancelled or refunded")
        return value
