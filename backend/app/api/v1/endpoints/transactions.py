import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user, require_admin, require_editor
from app.db.models.user import User
from app.schemas.transaction import (
    PaginatedTransactions,
    TransactionCreate,
    TransactionFilter,
    TransactionResponse,
    TransactionUpdate,
)
from app.services import transaction_service

router = APIRouter()


@router.get("/", response_model=PaginatedTransactions)
def list_transactions(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    bank_account_id: Optional[int] = Query(None),
    search_query: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedTransactions:
    from datetime import date as date_type

    def _parse_date(s: Optional[str]) -> Optional[date_type]:
        if not s:
            return None
        from app.utils.date_utils import parse_date
        return parse_date(s)

    filters = TransactionFilter(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        category_id=category_id,
        transaction_type=transaction_type,
        status=status_filter,
        bank_account_id=bank_account_id,
        search_query=search_query,
    )
    skip = (page - 1) * size
    items, total = transaction_service.get_transactions(db, filters=filters, skip=skip, limit=size)
    pages = math.ceil(total / size) if total else 1
    return PaginatedTransactions(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> TransactionResponse:
    tx = transaction_service.create_transaction(db, transaction_in, user_id=current_user.id)
    from app.services.ai_learning_service import record_feedback

    record_feedback(
        db,
        user_id=current_user.id,
        description=tx.description,
        category_id=tx.category_id,
        transaction_type=tx.transaction_type,
    )
    return tx


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
) -> TransactionResponse:
    tx = transaction_service.get_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> TransactionResponse:
    tx = transaction_service.update_transaction(db, transaction_id, transaction_in, user_id=current_user.id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    from app.services.ai_learning_service import record_feedback

    record_feedback(
        db,
        user_id=current_user.id,
        description=tx.description,
        category_id=tx.category_id,
        transaction_type=tx.transaction_type,
    )
    return tx


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    deleted = transaction_service.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")


@router.post("/{transaction_id}/approve-ai", response_model=TransactionResponse)
def approve_ai_suggestion(
    transaction_id: int,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_editor),
) -> TransactionResponse:
    tx = transaction_service.get_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if tx.ai_suggested_category_id:
        tx.category_id = tx.ai_suggested_category_id
    tx.status = "confirmed"
    db.commit()
    db.refresh(tx)
    return tx


@router.post("/{transaction_id}/reject-ai", response_model=TransactionResponse)
def reject_ai_suggestion(
    transaction_id: int,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_editor),
) -> TransactionResponse:
    tx = transaction_service.get_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    tx.ai_category_suggestion = None
    tx.ai_confidence = None
    tx.ai_suggested_category_id = None
    tx.status = "confirmed"
    db.commit()
    db.refresh(tx)
    return tx
