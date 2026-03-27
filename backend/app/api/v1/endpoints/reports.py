from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user
from app.db.models.category import Category
from app.db.models.transaction import Transaction
from app.db.models.user import User

router = APIRouter()


def _shift_month(month_start: date, delta: int) -> date:
    month_index = (month_start.month - 1) + delta
    year = month_start.year + (month_index // 12)
    month = (month_index % 12) + 1
    return date(year, month, 1)


def _base_query(
    db: Session,
    user_id: int,
    start_date: Optional[date],
    end_date: Optional[date],
):
    q = db.query(Transaction).filter(Transaction.user_id == user_id)
    if start_date:
        q = q.filter(Transaction.transaction_date >= start_date)
    if end_date:
        q = q.filter(Transaction.transaction_date <= end_date)
    return q


@router.get("/summary")
def summary_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    q = _base_query(db, current_user.id, start_date, end_date)
    income = q.filter(Transaction.transaction_type == "income").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()
    expenses = q.filter(Transaction.transaction_type == "expense").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()
    return {
        "total_income": float(income),
        "total_expenses": float(expenses),
        "balance": float(income) - float(expenses),
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
    }


@router.get("/by-category")
def by_category_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[dict]:
    q = _base_query(db, current_user.id, start_date, end_date)
    rows = (
        q.join(Category, Transaction.category_id == Category.id, isouter=True)
        .with_entities(
            Category.name,
            Transaction.transaction_type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .group_by(Category.name, Transaction.transaction_type)
        .all()
    )
    return [
        {
            "category": row.name or "Uncategorized",
            "transaction_type": row.transaction_type,
            "total": float(row.total),
            "count": row.count,
        }
        for row in rows
    ]


@router.get("/monthly")
def monthly_report(
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[dict]:
    rows = (
        db.query(
            extract("month", Transaction.transaction_date).label("month"),
            Transaction.transaction_type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .filter(Transaction.user_id == current_user.id)
        .filter(extract("year", Transaction.transaction_date) == year)
        .group_by("month", Transaction.transaction_type)
        .order_by("month")
        .all()
    )
    return [
        {"year": year, "month": int(row.month), "transaction_type": row.transaction_type, "total": float(row.total)}
        for row in rows
    ]


@router.get("/annual")
def annual_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[dict]:
    rows = (
        db.query(
            extract("year", Transaction.transaction_date).label("year"),
            Transaction.transaction_type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .filter(Transaction.user_id == current_user.id)
        .group_by("year", Transaction.transaction_type)
        .order_by("year")
        .all()
    )
    return [
        {"year": int(row.year), "transaction_type": row.transaction_type, "total": float(row.total), "count": row.count}
        for row in rows
    ]


@router.get("/cash-flow")
def cash_flow_report(
    months_history: int = Query(6, ge=1, le=24),
    months_forecast: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    today = date.today()
    current_month_start = date(today.year, today.month, 1)
    history_start = _shift_month(current_month_start, -(months_history - 1))

    rows = (
        db.query(
            extract("year", Transaction.transaction_date).label("year"),
            extract("month", Transaction.transaction_date).label("month"),
            Transaction.transaction_type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .filter(Transaction.user_id == current_user.id)
        .filter(Transaction.transaction_date >= history_start)
        .filter(Transaction.transaction_date < _shift_month(current_month_start, 1))
        .group_by("year", "month", Transaction.transaction_type)
        .order_by("year", "month")
        .all()
    )

    totals_by_month: dict[str, dict[str, float]] = {}
    for row in rows:
        month_key = f"{int(row.year):04d}-{int(row.month):02d}"
        if month_key not in totals_by_month:
            totals_by_month[month_key] = {"income": 0.0, "expense": 0.0}
        totals_by_month[month_key][row.transaction_type] = float(row.total)

    history = []
    net_values: list[float] = []
    running_balance = 0.0
    for i in range(months_history):
        month_date = _shift_month(history_start, i)
        month_key = month_date.strftime("%Y-%m")
        month_totals = totals_by_month.get(month_key, {"income": 0.0, "expense": 0.0})
        income = float(month_totals.get("income", 0.0))
        expense = float(month_totals.get("expense", 0.0))
        net = income - expense
        running_balance += net
        net_values.append(net)
        history.append(
            {
                "month": month_key,
                "income": income,
                "expense": expense,
                "net": net,
                "cumulative_net": running_balance,
            }
        )

    projection_base = net_values[-3:] if len(net_values) >= 3 else net_values
    avg_net = (sum(projection_base) / len(projection_base)) if projection_base else 0.0

    forecast = []
    projected_running_balance = running_balance
    for i in range(1, months_forecast + 1):
        forecast_month = _shift_month(current_month_start, i)
        forecast_key = forecast_month.strftime("%Y-%m")
        projected_running_balance += avg_net
        forecast.append(
            {
                "month": forecast_key,
                "projected_net": avg_net,
                "projected_cumulative_net": projected_running_balance,
            }
        )

    current_key = current_month_start.strftime("%Y-%m")
    current_totals = totals_by_month.get(current_key, {"income": 0.0, "expense": 0.0})

    return {
        "generated_at": today.isoformat(),
        "months_history": months_history,
        "months_forecast": months_forecast,
        "history": history,
        "current_month": {
            "month": current_key,
            "income": float(current_totals.get("income", 0.0)),
            "expense": float(current_totals.get("expense", 0.0)),
            "net": float(current_totals.get("income", 0.0)) - float(current_totals.get("expense", 0.0)),
        },
        "average_net_last_months": avg_net,
        "forecast": forecast,
    }
