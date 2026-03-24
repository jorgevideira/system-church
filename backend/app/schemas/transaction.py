from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.category import CategoryResponse


class TransactionBase(BaseModel):
    description: str
    amount: Decimal
    transaction_type: str  # income | expense
    transaction_date: date
    category_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    notes: Optional[str] = None
    reference: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    transaction_type: Optional[str] = None
    transaction_date: Optional[date] = None
    category_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    notes: Optional[str] = None
    reference: Optional[str] = None
    status: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    status: str
    ai_category_suggestion: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_suggested_category_id: Optional[int] = None
    user_id: int
    statement_file_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

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
