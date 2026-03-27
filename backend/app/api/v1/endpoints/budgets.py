from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.db.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
    MonthlyBudgetAdherence,
)
from app.schemas.budget import BudgetHealth, BudgetSimulation
from app.services import budget_service


class SimulateExpenseRequest(BaseModel):
    projected_expense: Decimal


router = APIRouter()


@router.get("/", response_model=list[BudgetResponse])
def list_budgets(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List budgets for current user, optionally filtered by month (YYYY-MM)"""
    budgets = budget_service.list_budgets(db, current_user.id, month)
    return budgets


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_in: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new budget"""
    budget = budget_service.create_budget(db, budget_in, current_user.id)
    return budget


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific budget"""
    budget = budget_service.get_budget(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_in: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a budget"""
    budget = budget_service.get_budget(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    budget = budget_service.update_budget(db, budget, budget_in)
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a budget"""
    budget = budget_service.get_budget(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    budget_service.delete_budget(db, budget)


@router.get("/{month}/health", response_model=list[BudgetHealth])
def get_budget_health(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get health metrics for all budgets in a month"""
    healths = budget_service.list_budgets_health(db, current_user.id, month)
    return healths


@router.post("/{budget_id}/simulate", response_model=BudgetSimulation)
def simulate_expense(
    budget_id: int,
    request: SimulateExpenseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Simulate adding an expense to a budget"""
    budget = budget_service.get_budget(db, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    simulation = budget_service.simulate_expense(db, budget, request.projected_expense)
    return simulation


@router.get("/{month}/adherence", response_model=MonthlyBudgetAdherence)
def get_monthly_adherence(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get monthly budget adherence report"""
    adherence = budget_service.get_monthly_adherence(db, current_user.id, month)
    return adherence
