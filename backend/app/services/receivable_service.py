from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.receivable import Receivable
from app.schemas.receivable import ReceivableCreate, ReceivableUpdate
from app.schemas.transaction import TransactionCreate
from app.services import transaction_service


def _next_due_date(current_due_date: date, recurrence_type: str) -> date:
    if recurrence_type == "weekly":
        return current_due_date + timedelta(days=7)

    if recurrence_type == "monthly":
        next_month = current_due_date.month + 1
        next_year = current_due_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        max_day = monthrange(next_year, next_month)[1]
        return date(next_year, next_month, min(current_due_date.day, max_day))

    if recurrence_type == "yearly":
        next_year = current_due_date.year + 1
        max_day = monthrange(next_year, current_due_date.month)[1]
        return date(next_year, current_due_date.month, min(current_due_date.day, max_day))

    return current_due_date


def _ensure_next_recurring_receivable(db: Session, receivable: Receivable) -> None:
    if not receivable.is_recurring or not receivable.recurrence_type:
        return

    next_due = _next_due_date(receivable.due_date, receivable.recurrence_type)

    existing = db.query(Receivable).filter(
        Receivable.user_id == receivable.user_id,
        Receivable.description == receivable.description,
        Receivable.due_date == next_due,
        Receivable.status.in_(["pending", "overdue"]),
        Receivable.is_recurring.is_(True),
        Receivable.recurrence_type == receivable.recurrence_type,
    ).first()
    if existing:
        return

    next_receivable = Receivable(
        description=receivable.description,
        amount=receivable.amount,
        due_date=next_due,
        status="pending",
        category_id=receivable.category_id,
        ministry_id=receivable.ministry_id,
        user_id=receivable.user_id,
        source_bank_name=receivable.source_bank_name,
        notes=receivable.notes,
        is_recurring=True,
        recurrence_type=receivable.recurrence_type,
    )
    db.add(next_receivable)


def refresh_overdue_statuses(db: Session, user_id: int) -> None:
    today = date.today()
    db.query(Receivable).filter(
        Receivable.user_id == user_id,
        Receivable.status == "pending",
        Receivable.due_date < today,
    ).update({"status": "overdue"}, synchronize_session=False)
    db.commit()


def list_receivables(db: Session, user_id: int, status_filter: Optional[str] = None) -> list[Receivable]:
    refresh_overdue_statuses(db, user_id)
    q = db.query(Receivable).filter(Receivable.user_id == user_id)
    if status_filter:
        q = q.filter(Receivable.status == status_filter)
    return q.order_by(Receivable.due_date.asc(), Receivable.id.desc()).all()


def get_receivable(db: Session, receivable_id: int, user_id: int) -> Optional[Receivable]:
    refresh_overdue_statuses(db, user_id)
    return db.query(Receivable).filter(Receivable.id == receivable_id, Receivable.user_id == user_id).first()


def create_receivable(db: Session, receivable_in: ReceivableCreate, user_id: int) -> Receivable:
    data = receivable_in.model_dump()
    if not data.get("is_recurring"):
        data["recurrence_type"] = None
    receivable = Receivable(**data, user_id=user_id, status="pending")
    db.add(receivable)
    db.commit()
    db.refresh(receivable)
    return receivable


def update_receivable(db: Session, receivable: Receivable, receivable_in: ReceivableUpdate) -> Receivable:
    data = receivable_in.model_dump(exclude_unset=True)
    if "is_recurring" in data and data["is_recurring"] is False:
        data["recurrence_type"] = None
    if data.get("recurrence_type") and "is_recurring" not in data:
        data["is_recurring"] = True
    for field, value in data.items():
        setattr(receivable, field, value)
    db.commit()
    db.refresh(receivable)
    return receivable


def delete_receivable(db: Session, receivable: Receivable) -> None:
    db.delete(receivable)
    db.commit()


def mark_receivable_received(
    db: Session,
    receivable: Receivable,
    *,
    user_id: int,
    received_at: Optional[date] = None,
    generate_transaction: bool = True,
) -> Receivable:
    if receivable.status == "received":
        return receivable

    receipt_date = received_at or date.today()
    receipt_tx_id: Optional[int] = receivable.receipt_transaction_id

    if generate_transaction and not receipt_tx_id:
        tx = transaction_service.create_transaction(
            db,
            TransactionCreate(
                description=f"Recebimento: {receivable.description}",
                amount=Decimal(receivable.amount),
                transaction_type="income",
                transaction_date=receipt_date,
                category_id=receivable.category_id,
                ministry_id=receivable.ministry_id,
                source_bank_name=receivable.source_bank_name,
                notes=(receivable.notes or "")[:900] or None,
            ),
            user_id=user_id,
        )
        receipt_tx_id = tx.id

    receivable.status = "received"
    receivable.received_at = receipt_date
    receivable.receipt_transaction_id = receipt_tx_id
    _ensure_next_recurring_receivable(db, receivable)
    db.commit()
    db.refresh(receivable)
    return receivable


def get_alerts_summary(db: Session, user_id: int) -> dict:
    refresh_overdue_statuses(db, user_id)

    today = date.today()
    plus_3 = today + timedelta(days=3)
    plus_7 = today + timedelta(days=7)

    base_q = db.query(Receivable).filter(Receivable.user_id == user_id, Receivable.status != "received")

    overdue = base_q.filter(Receivable.due_date < today).count()
    due_today = base_q.filter(Receivable.due_date == today).count()
    due_in_3_days = base_q.filter(Receivable.due_date > today, Receivable.due_date <= plus_3).count()
    due_in_7_days = base_q.filter(Receivable.due_date > plus_3, Receivable.due_date <= plus_7).count()
    pending_total = base_q.filter(Receivable.status == "pending").count()

    return {
        "overdue": overdue,
        "due_today": due_today,
        "due_in_3_days": due_in_3_days,
        "due_in_7_days": due_in_7_days,
        "pending_total": pending_total,
    }
