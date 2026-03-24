import hashlib
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionFilter, TransactionUpdate


def get_transactions(
    db: Session,
    filters: Optional[TransactionFilter] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Transaction], int]:
    q = db.query(Transaction)
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


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def create_transaction(db: Session, transaction_create: TransactionCreate, user_id: int) -> Transaction:
    data = transaction_create.model_dump()
    dedup = compute_dedup_hash(
        data.get("description", ""),
        str(data.get("amount", "")),
        str(data.get("transaction_date", "")),
        data.get("reference"),
    )
    tx = Transaction(**data, user_id=user_id, status="confirmed", dedup_hash=dedup)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def update_transaction(
    db: Session, transaction_id: int, transaction_update: TransactionUpdate, user_id: int
) -> Optional[Transaction]:
    tx = get_transaction(db, transaction_id)
    if not tx:
        return None
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


def delete_transaction(db: Session, transaction_id: int) -> bool:
    tx = get_transaction(db, transaction_id)
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
