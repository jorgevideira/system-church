from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventNotificationResponse(BaseModel):
    id: int
    tenant_id: Optional[int] = None
    event_id: int
    registration_id: int
    channel: str
    template_key: str
    recipient: str
    status: str
    payload: Optional[dict] = None
    external_reference: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventNotificationRetryResponse(BaseModel):
    notification_id: int
    status: str


class EventAnalyticsResponse(BaseModel):
    event_id: int
    title: str
    capacity: Optional[int] = None
    reserved_slots: int
    confirmed_registrations: int
    confirmed_participants: int
    pending_registrations: int
    total_revenue_confirmed: float
    total_revenue_pending: float
    payment_status_breakdown: list[dict]
    payment_method_breakdown: list[dict]
    registrations_by_day: list[dict]
