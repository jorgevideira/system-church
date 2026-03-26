from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator

from app.schemas.category import CategoryResponse
from app.schemas.ministry import MinistryResponse


class TransactionBase(BaseModel):
    description: str
    amount: Decimal
    transaction_type: str  # income | expense
    transaction_date: date
    category_id: Optional[int] = None
    ministry_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    notes: Optional[str] = None
    reference: Optional[str] = None
    source_bank_name: Optional[str] = None
    expense_profile: Optional[str] = None  # fixed | variable

    @field_validator("expense_profile")
    @classmethod
    def validate_expense_profile(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if value not in {"fixed", "variable"}:
            raise ValueError("expense_profile must be fixed or variable")
        return value

    @model_validator(mode="after")
    def validate_expense_profile_by_type(self) -> "TransactionBase":
        if self.transaction_type != "expense" and self.expense_profile is not None:
            raise ValueError("expense_profile is only allowed for expense transactions")
        if self.transaction_type != "expense" and self.ministry_id is not None:
            raise ValueError("ministry_id is only allowed for expense transactions")
        return self


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    transaction_type: Optional[str] = None
    transaction_date: Optional[date] = None
    category_id: Optional[int] = None
    ministry_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    notes: Optional[str] = None
    reference: Optional[str] = None
    source_bank_name: Optional[str] = None
    expense_profile: Optional[str] = None
    status: Optional[str] = None

    @field_validator("expense_profile")
    @classmethod
    def validate_expense_profile(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if value not in {"fixed", "variable"}:
            raise ValueError("expense_profile must be fixed or variable")
        return value

    @model_validator(mode="after")
    def validate_expense_profile_by_type(self) -> "TransactionUpdate":
        if self.transaction_type is not None and self.transaction_type != "expense" and self.expense_profile is not None:
            raise ValueError("expense_profile is only allowed for expense transactions")
        if self.transaction_type is not None and self.transaction_type != "expense" and self.ministry_id is not None:
            raise ValueError("ministry_id is only allowed for expense transactions")
        return self


class TransactionResponse(TransactionBase):
    id: int
    status: str
    ai_category_suggestion: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_suggested_category_id: Optional[int] = None
    user_id: int
    statement_file_id: Optional[int] = None
    source_bank: Optional[str] = None
    attachment_count: int = 0
    has_attachments: bool = False
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    ministry: Optional[MinistryResponse] = None

    model_config = {"from_attributes": True}


class TransactionFilter(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[int] = None
    transaction_type: Optional[str] = None
    status: Optional[str] = None
    bank_account_id: Optional[int] = None
    search_query: Optional[str] = None


class PaginatedTransactions(BaseModel):
    items: List[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int
