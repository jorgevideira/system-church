from datetime import datetime

from pydantic import BaseModel, Field


class EventCheckInRequest(BaseModel):
    token: str = Field(..., min_length=6, max_length=128)


class EventCheckInResponse(BaseModel):
    status: str
    message: str
    event_id: int | None = None
    registration_id: int | None = None
    attendee_name: str | None = None
    attendee_email: str | None = None
    checked_in_at: datetime | None = None

