from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.schemas.category import CategoryResponse
from app.schemas.ministry import MinistryResponse
from app.schemas.transaction import TransactionResponse


class PayableBase(BaseModel):
    description: str
    amount: Decimal
    due_date: date
    category_id: Optional[int] = None
    ministry_id: Optional[int] = None
    source_bank_name: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: bool = False
    recurrence_type: Optional[str] = None

    @field_validator("recurrence_type")
    @classmethod
    def validate_recurrence_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        allowed = {"weekly", "monthly", "yearly"}
        if value not in allowed:
            raise ValueError("recurrence_type must be weekly, monthly or yearly")
        return value


class PayableCreate(PayableBase):
    pass


class PayableUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[date] = None
    category_id: Optional[int] = None
    ministry_id: Optional[int] = None
    source_bank_name: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_type: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {"pending", "paid", "overdue"}
        if value not in allowed:
            raise ValueError("status must be pending, paid or overdue")
        return value

    @field_validator("recurrence_type")
    @classmethod
    def validate_recurrence_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        allowed = {"weekly", "monthly", "yearly"}
        if value not in allowed:
            raise ValueError("recurrence_type must be weekly, monthly or yearly")
        return value


class MarkPayablePaidRequest(BaseModel):
    paid_at: Optional[date] = None
    generate_transaction: bool = True


class PayableResponse(PayableBase):
    id: int
    status: str
    paid_at: Optional[date] = None
    payment_transaction_id: Optional[int] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    category: Optional[CategoryResponse] = None
    ministry: Optional[MinistryResponse] = None
    payment_transaction: Optional[TransactionResponse] = None

    model_config = {"from_attributes": True}


class PayableAlertsSummary(BaseModel):
    overdue: int
    due_today: int
    due_in_3_days: int
    due_in_7_days: int
    pending_total: int
