from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.schemas.category import CategoryResponse
from app.schemas.ministry import MinistryResponse
from app.schemas.transaction import TransactionResponse


class ReceivableBase(BaseModel):
    description: str
    amount: Decimal
    due_date: date
    category_id: Optional[int] = None
    ministry_id: Optional[int] = None
    source_bank_name: Optional[str] = None
    notes: Optional[str] = None
    revenue_profile: Optional[str] = None
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


class ReceivableCreate(ReceivableBase):
    pass


class ReceivableUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[date] = None
    category_id: Optional[int] = None
    ministry_id: Optional[int] = None
    source_bank_name: Optional[str] = None
    notes: Optional[str] = None
    revenue_profile: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_type: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {"pending", "received", "overdue"}
        if value not in allowed:
            raise ValueError("status must be pending, received or overdue")
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


class MarkReceivableReceivedRequest(BaseModel):
    received_at: Optional[date] = None
    receipt_method: Optional[str] = None
    generate_transaction: bool = True

    @field_validator("receipt_method")
    @classmethod
    def validate_receipt_method(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {"pix", "boleto", "cash"}
        if value not in allowed:
            raise ValueError("receipt_method must be pix, boleto or cash")
        return value


class ReceivableResponse(ReceivableBase):
    id: int
    status: str
    received_at: Optional[date] = None
    receipt_method: Optional[str] = None
    receipt_transaction_id: Optional[int] = None
    user_id: int
    attachment_storage_filename: Optional[str] = None
    attachment_original_filename: Optional[str] = None
    attachment_mime_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    category: Optional[CategoryResponse] = None
    ministry: Optional[MinistryResponse] = None
    receipt_transaction: Optional[TransactionResponse] = None

    model_config = {"from_attributes": True}


class ReceivableAlertsSummary(BaseModel):
    overdue: int
    due_today: int
    due_in_3_days: int
    due_in_7_days: int
    pending_total: int
