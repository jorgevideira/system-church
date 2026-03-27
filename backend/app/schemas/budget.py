from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator


class BudgetBase(BaseModel):
    month: str  # YYYY-MM
    budget_type: str  # "category" or "ministry"
    reference_id: int
    target_amount: Decimal
    alert_threshold_percent: int = 80

    @field_validator("month")
    @classmethod
    def validate_month(cls, value: str) -> str:
        if len(value) != 7 or value[4] != "-":
            raise ValueError("month must be in YYYY-MM format")
        return value

    @field_validator("budget_type")
    @classmethod
    def validate_budget_type(cls, value: str) -> str:
        if value not in {"category", "ministry"}:
            raise ValueError("budget_type must be 'category' or 'ministry'")
        return value

    @field_validator("alert_threshold_percent")
    @classmethod
    def validate_threshold(cls, value: int) -> int:
        if not 1 <= value <= 100:
            raise ValueError("alert_threshold_percent must be between 1 and 100")
        return value


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    target_amount: Optional[Decimal] = None
    alert_threshold_percent: Optional[int] = None

    @field_validator("alert_threshold_percent")
    @classmethod
    def validate_threshold(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and not (1 <= value <= 100):
            raise ValueError("alert_threshold_percent must be between 1 and 100")
        return value


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BudgetHealth(BaseModel):
    """Budget health metrics"""
    budget_id: int
    month: str
    budget_type: str
    reference_id: int
    reference_name: str
    target_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    percent_spent: float
    alert_level: str  # "healthy", "warning", "critical"
    is_alert_triggered: bool


class BudgetSimulation(BaseModel):
    """Simulate budget for a projected expense"""
    budget_id: int
    reference_name: str
    current_spent: Decimal
    projected_expense: Decimal
    new_total: Decimal
    new_percent: float
    will_trigger_alert: bool
    will_exceed: bool


class MonthlyBudgetAdherence(BaseModel):
    """Monthly budget report"""
    month: str
    total_budgets: int
    total_target: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    healthy_count: int
    warning_count: int
    critical_count: int
    percent_spent: float
