import hashlib
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.db.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionUpdate


def get_transactions(
    db: Session,
    tenant_id: int,
    filters: Optional[TransactionFilter] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Transaction], int]:
    q = db.query(Transaction).options(selectinload(Transaction.attachments)).filter(Transaction.tenant_id == tenant_id)
    if filters:
        if filters.start_date:
            q = q.filter(Transaction.transaction_date >= filters.start_date)
        if filters.end_date:
            q = q.filter(Transaction.transaction_date <= filters.end_date)
        if filters.category_id is not None:
            q = q.filter(Transaction.category_id == filters.category_id)
        if filters.transaction_type:
            q = q.filter(Transaction.transaction_type == filters.transaction_type)
        if filters.status:
            q = q.filter(Transaction.status == filters.status)
        if filters.bank_account_id is not None:
            q = q.filter(Transaction.bank_account_id == filters.bank_account_id)
        if filters.search_query:
            like = f"%{filters.search_query}%"
            q = q.filter(Transaction.description.ilike(like))
    total = q.count()
    items = q.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return items, total


def get_transaction(db: Session, transaction_id: int, tenant_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.tenant_id == tenant_id).first()


def create_transaction(db: Session, transaction_create: TransactionCreate, user_id: int, tenant_id: int) -> Transaction:
    data = transaction_create.model_dump()
    if data.get("transaction_type") != "expense":
        data["ministry_id"] = None
    dedup = compute_dedup_hash(
        data.get("description", ""),
        str(data.get("amount", "")),
        str(data.get("transaction_date", "")),
        data.get("reference"),
    )
    tx = Transaction(**data, user_id=user_id, tenant_id=tenant_id, status="confirmed", dedup_hash=dedup)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def create_transaction_from_import(
    db: Session,
    transaction_create: TransactionCreate,
    user_id: int,
    tenant_id: int,
    statement_file_id: int,
) -> Transaction:
    data = transaction_create.model_dump()
    if data.get("transaction_type") != "expense":
        data["ministry_id"] = None
    dedup = compute_dedup_hash(
        data.get("description", ""),
        str(data.get("amount", "")),
        str(data.get("transaction_date", "")),
        data.get("reference"),
    )
    tx = Transaction(
        **data,
        user_id=user_id,
        tenant_id=tenant_id,
        statement_file_id=statement_file_id,
        status="confirmed",
        dedup_hash=dedup,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def update_transaction(
    db: Session, transaction_id: int, transaction_update: TransactionUpdate, user_id: int, tenant_id: int
) -> Optional[Transaction]:
    tx = get_transaction(db, transaction_id, tenant_id)
    if not tx:
        return None
    update_data = transaction_update.model_dump(exclude_unset=True)

    effective_transaction_type = update_data.get("transaction_type", tx.transaction_type)
    if effective_transaction_type != "expense":
        update_data["ministry_id"] = None

    for field, value in update_data.items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


def delete_transaction(db: Session, transaction_id: int, tenant_id: int) -> bool:
    tx = get_transaction(db, transaction_id, tenant_id)
    if not tx:
        return False
    db.delete(tx)
    db.commit()
    return True


def compute_dedup_hash(
    description: str,
    amount: str,
    transaction_date: str,
    reference: Optional[str] = None,
) -> str:
    raw = f"{description}|{amount}|{transaction_date}|{reference or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


def check_duplicate(db: Session, hash_value: str) -> bool:
    return db.query(Transaction).filter(Transaction.dedup_hash == hash_value).first() is not None


def check_duplicate_same_day_amount(
    db: Session,
    *,
    tenant_id: int,
    user_id: int,
    transaction_date: date,
    amount: Decimal,
    transaction_type: Optional[str] = None,
    exclude_statement_file_id: Optional[int] = None,
) -> bool:
    """Duplicate rule requested: same day and same amount for the same user."""
    q = db.query(Transaction).filter(
        Transaction.tenant_id == tenant_id,
        Transaction.user_id == user_id,
        Transaction.transaction_date == transaction_date,
        Transaction.amount == amount,
    )
    if transaction_type:
        q = q.filter(Transaction.transaction_type == transaction_type)
    if exclude_statement_file_id is not None:
        q = q.filter(
            (Transaction.statement_file_id.is_(None))
            | (Transaction.statement_file_id != exclude_statement_file_id)
        )
    return q.first() is not None
