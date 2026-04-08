from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.payable import Payable
from app.db.models.transaction import Transaction
from app.schemas.payable import PayableCreate, PayableUpdate
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


def _ensure_next_recurring_payable(db: Session, payable: Payable) -> None:
    if not payable.is_recurring or not payable.recurrence_type:
        return

    next_due = _next_due_date(payable.due_date, payable.recurrence_type)

    existing = db.query(Payable).filter(
        Payable.tenant_id == payable.tenant_id,
        Payable.user_id == payable.user_id,
        Payable.description == payable.description,
        Payable.due_date == next_due,
        Payable.status.in_(["pending", "overdue"]),
        Payable.is_recurring.is_(True),
        Payable.recurrence_type == payable.recurrence_type,
    ).first()
    if existing:
        return

    next_payable = Payable(
        tenant_id=payable.tenant_id,
        description=payable.description,
        amount=payable.amount,
        due_date=next_due,
        status="pending",
        category_id=payable.category_id,
        ministry_id=payable.ministry_id,
        user_id=payable.user_id,
        source_bank_name=payable.source_bank_name,
        notes=payable.notes,
        is_recurring=True,
        recurrence_type=payable.recurrence_type,
    )
    db.add(next_payable)


def refresh_overdue_statuses(db: Session, user_id: int, tenant_id: int) -> None:
    today = date.today()
    db.query(Payable).filter(
        Payable.tenant_id == tenant_id,
        Payable.user_id == user_id,
        Payable.status == "pending",
        Payable.due_date < today,
    ).update({"status": "overdue"}, synchronize_session=False)
    db.commit()


def list_payables(db: Session, user_id: int, tenant_id: int, status_filter: Optional[str] = None) -> list[Payable]:
    refresh_overdue_statuses(db, user_id, tenant_id)
    q = db.query(Payable).filter(Payable.user_id == user_id, Payable.tenant_id == tenant_id)
    if status_filter:
        q = q.filter(Payable.status == status_filter)
    return q.order_by(Payable.due_date.asc(), Payable.id.desc()).all()


def get_payable(db: Session, payable_id: int, user_id: int, tenant_id: int) -> Optional[Payable]:
    refresh_overdue_statuses(db, user_id, tenant_id)
    return db.query(Payable).filter(Payable.id == payable_id, Payable.user_id == user_id, Payable.tenant_id == tenant_id).first()


def create_payable(db: Session, payable_in: PayableCreate, user_id: int, tenant_id: int) -> Payable:
    data = payable_in.model_dump()
    if not data.get("is_recurring"):
        data["recurrence_type"] = None
    payable = Payable(**data, user_id=user_id, tenant_id=tenant_id, status="pending")
    db.add(payable)
    db.commit()
    db.refresh(payable)
    return payable


def update_payable(db: Session, payable: Payable, payable_in: PayableUpdate) -> Payable:
    data = payable_in.model_dump(exclude_unset=True)
    if "is_recurring" in data and data["is_recurring"] is False:
        data["recurrence_type"] = None
    if data.get("recurrence_type") and "is_recurring" not in data:
        data["is_recurring"] = True
    for field, value in data.items():
        setattr(payable, field, value)
    db.commit()
    db.refresh(payable)
    return payable


def delete_payable(db: Session, payable: Payable) -> None:
    if payable.payment_transaction_id:
        payment_tx = db.query(Transaction).filter(
            Transaction.id == payable.payment_transaction_id,
            Transaction.user_id == payable.user_id,
            Transaction.tenant_id == payable.tenant_id,
        ).first()
        if payment_tx:
            db.delete(payment_tx)
    db.delete(payable)
    db.commit()


def mark_payable_paid(
    db: Session,
    payable: Payable,
    *,
    user_id: int,
    paid_at: Optional[date] = None,
    payment_method: Optional[str] = None,
    generate_transaction: bool = True,
) -> Payable:
    if payable.status == "paid":
        return payable

    paid_date = paid_at or date.today()
    payment_tx_id: Optional[int] = payable.payment_transaction_id

    if generate_transaction and not payment_tx_id:
        tx = transaction_service.create_transaction(
            db,
            TransactionCreate(
                description=f"Pagamento: {payable.description}",
                amount=Decimal(payable.amount),
                transaction_type="expense",
                transaction_date=paid_date,
                category_id=payable.category_id,
                ministry_id=payable.ministry_id,
                source_bank_name=payable.source_bank_name,
                reference=f"payable:{payable.id}",
                expense_profile=payable.expense_profile,
                notes=(payable.notes or "")[:900] or None,
            ),
            user_id=user_id,
            tenant_id=payable.tenant_id,
        )
        payment_tx_id = tx.id

    payable.status = "paid"
    payable.paid_at = paid_date
    payable.payment_method = payment_method or payable.payment_method
    payable.payment_transaction_id = payment_tx_id
    _ensure_next_recurring_payable(db, payable)
    db.commit()
    db.refresh(payable)
    return payable


def set_payable_attachment(
    db: Session,
    payable: Payable,
    *,
    storage_filename: str,
    original_filename: str,
    mime_type: str,
) -> Payable:
    payable.attachment_storage_filename = storage_filename
    payable.attachment_original_filename = original_filename
    payable.attachment_mime_type = mime_type
    db.commit()
    db.refresh(payable)
    return payable


def clear_payable_attachment(db: Session, payable: Payable) -> Payable:
    payable.attachment_storage_filename = None
    payable.attachment_original_filename = None
    payable.attachment_mime_type = None
    db.commit()
    db.refresh(payable)
    return payable


def get_alerts_summary(db: Session, user_id: int, tenant_id: int) -> dict:
    refresh_overdue_statuses(db, user_id, tenant_id)

    today = date.today()
    plus_3 = today + timedelta(days=3)
    plus_7 = today + timedelta(days=7)

    base_q = db.query(Payable).filter(Payable.user_id == user_id, Payable.tenant_id == tenant_id, Payable.status != "paid")

    overdue = base_q.filter(Payable.due_date < today).count()
    due_today = base_q.filter(Payable.due_date == today).count()
    due_in_3_days = base_q.filter(Payable.due_date > today, Payable.due_date <= plus_3).count()
    due_in_7_days = base_q.filter(Payable.due_date > plus_3, Payable.due_date <= plus_7).count()
    pending_total = base_q.filter(Payable.status == "pending").count()

    return {
        "overdue": overdue,
        "due_today": due_today,
        "due_in_3_days": due_in_3_days,
        "due_in_7_days": due_in_7_days,
        "pending_total": pending_total,
    }
