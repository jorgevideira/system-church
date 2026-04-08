from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.budget import Budget
from app.db.models.category import Category
from app.db.models.ministry import Ministry
from app.db.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetHealth, BudgetSimulation, BudgetUpdate, MonthlyBudgetAdherence


def _get_reference_name(db: Session, budget_type: str, reference_id: int, tenant_id: int) -> str:
    if budget_type == "category":
        cat = db.query(Category).filter(Category.id == reference_id, Category.tenant_id == tenant_id).first()
        return cat.name if cat else f"Category {reference_id}"
    else:
        ministry = db.query(Ministry).filter(Ministry.id == reference_id, Ministry.tenant_id == tenant_id).first()
        return ministry.name if ministry else f"Ministry {reference_id}"


def _calculate_spent_amount(db: Session, month: str, budget_type: str, reference_id: int, user_id: int, tenant_id: int) -> Decimal:
    """Calculate spent amount for a budget in a specific month"""
    start_date = f"{month}-01"
    end_date = f"{month}-31"
    
    query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.tenant_id == tenant_id,
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    )
    
    if budget_type == "category":
        query = query.filter(Transaction.category_id == reference_id)
    else:
        query = query.filter(Transaction.ministry_id == reference_id)
    
    result = query.scalar()
    return Decimal(result or 0)


def _calculate_alert_level(percent_spent: float, alert_threshold: int) -> str:
    if percent_spent >= 100:
        return "critical"
    if percent_spent >= alert_threshold:
        return "warning"
    return "healthy"


def create_budget(db: Session, budget_in: BudgetCreate, user_id: int, tenant_id: int) -> Budget:
    budget = Budget(
        **budget_in.model_dump(),
        user_id=user_id,
        tenant_id=tenant_id,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def get_budget(db: Session, budget_id: int, user_id: int, tenant_id: int) -> Optional[Budget]:
    return db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id,
        Budget.tenant_id == tenant_id,
    ).first()


def list_budgets(db: Session, user_id: int, tenant_id: int, month: Optional[str] = None) -> list[Budget]:
    query = db.query(Budget).filter(Budget.user_id == user_id, Budget.tenant_id == tenant_id)
    if month:
        query = query.filter(Budget.month == month)
    return query.order_by(Budget.month.desc(), Budget.id.desc()).all()


def update_budget(db: Session, budget: Budget, budget_in: BudgetUpdate) -> Budget:
    data = budget_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget: Budget) -> None:
    db.delete(budget)
    db.commit()


def get_budget_health(db: Session, budget: Budget) -> BudgetHealth:
    """Calculate health metrics for a budget"""
    spent = _calculate_spent_amount(db, budget.month, budget.budget_type, budget.reference_id, budget.user_id, budget.tenant_id or 0)
    remaining = budget.target_amount - spent
    percent_spent = float((spent / budget.target_amount * 100) if budget.target_amount > 0 else 0)
    alert_level = _calculate_alert_level(percent_spent, budget.alert_threshold_percent)
    
    return BudgetHealth(
        budget_id=budget.id,
        month=budget.month,
        budget_type=budget.budget_type,
        reference_id=budget.reference_id,
        reference_name=_get_reference_name(db, budget.budget_type, budget.reference_id, budget.tenant_id or 0),
        target_amount=budget.target_amount,
        spent_amount=spent,
        remaining_amount=max(remaining, Decimal(0)),
        percent_spent=round(percent_spent, 2),
        alert_level=alert_level,
        is_alert_triggered=alert_level != "healthy",
    )


def list_budgets_health(db: Session, user_id: int, tenant_id: int, month: Optional[str] = None) -> list[BudgetHealth]:
    """Get health for all budgets in a month"""
    budgets = list_budgets(db, user_id, tenant_id, month)
    return [get_budget_health(db, budget) for budget in budgets]


def simulate_expense(db: Session, budget: Budget, projected_expense: Decimal) -> BudgetSimulation:
    """Simulate adding an expense to a budget"""
    spent = _calculate_spent_amount(db, budget.month, budget.budget_type, budget.reference_id, budget.user_id, budget.tenant_id or 0)
    new_total = spent + projected_expense
    new_percent = float((new_total / budget.target_amount * 100) if budget.target_amount > 0 else 0)
    new_alert_level = _calculate_alert_level(new_percent, budget.alert_threshold_percent)
    
    return BudgetSimulation(
        budget_id=budget.id,
        reference_name=_get_reference_name(db, budget.budget_type, budget.reference_id, budget.tenant_id or 0),
        current_spent=spent,
        projected_expense=projected_expense,
        new_total=new_total,
        new_percent=round(new_percent, 2),
        will_trigger_alert=new_alert_level != "healthy",
        will_exceed=new_total > budget.target_amount,
    )


def get_monthly_adherence(db: Session, user_id: int, tenant_id: int, month: str) -> MonthlyBudgetAdherence:
    """Get monthly budget adherence report"""
    budgets = list_budgets(db, user_id, tenant_id, month)
    healths = [get_budget_health(db, b) for b in budgets]
    
    total_target = sum(Decimal(h.target_amount) for h in healths)
    total_spent = sum(Decimal(h.spent_amount) for h in healths)
    total_remaining = sum(Decimal(h.remaining_amount) for h in healths)
    percent_spent = float((total_spent / total_target * 100) if total_target > 0 else 0)
    
    healthy = len([h for h in healths if h.alert_level == "healthy"])
    warning = len([h for h in healths if h.alert_level == "warning"])
    critical = len([h for h in healths if h.alert_level == "critical"])
    
    return MonthlyBudgetAdherence(
        month=month,
        total_budgets=len(budgets),
        total_target=total_target,
        total_spent=total_spent,
        total_remaining=total_remaining,
        healthy_count=healthy,
        warning_count=warning,
        critical_count=critical,
        percent_spent=round(percent_spent, 2),
    )
