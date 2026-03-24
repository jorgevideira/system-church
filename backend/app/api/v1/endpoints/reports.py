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


def _base_query(db: Session, start_date: Optional[date], end_date: Optional[date]):
    q = db.query(Transaction)
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
    _user: User = Depends(get_current_active_user),
) -> dict:
    q = _base_query(db, start_date, end_date)
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
    _user: User = Depends(get_current_active_user),
) -> List[dict]:
    q = _base_query(db, start_date, end_date)
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
    _user: User = Depends(get_current_active_user),
) -> List[dict]:
    rows = (
        db.query(
            extract("month", Transaction.transaction_date).label("month"),
            Transaction.transaction_type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
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
    _user: User = Depends(get_current_active_user),
) -> List[dict]:
    rows = (
        db.query(
            extract("year", Transaction.transaction_date).label("year"),
            Transaction.transaction_type,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .group_by("year", Transaction.transaction_type)
        .order_by("year")
        .all()
    )
    return [
        {"year": int(row.year), "transaction_type": row.transaction_type, "total": float(row.total), "count": row.count}
        for row in rows
    ]
