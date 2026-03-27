from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db, require_editor
from app.db.models.user import User
from app.schemas.receivable import (
    MarkReceivableReceivedRequest,
    ReceivableAlertsSummary,
    ReceivableCreate,
    ReceivableResponse,
    ReceivableUpdate,
)
from app.services import receivable_service

router = APIRouter()


@router.get("/", response_model=list[ReceivableResponse])
def list_receivables(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[ReceivableResponse]:
    return receivable_service.list_receivables(db, current_user.id, status_filter=status_filter)


@router.post("/", response_model=ReceivableResponse, status_code=status.HTTP_201_CREATED)
def create_receivable(
    receivable_in: ReceivableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> ReceivableResponse:
    return receivable_service.create_receivable(db, receivable_in, user_id=current_user.id)


@router.get("/alerts/summary", response_model=ReceivableAlertsSummary)
def get_receivables_alerts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReceivableAlertsSummary:
    return ReceivableAlertsSummary(**receivable_service.get_alerts_summary(db, current_user.id))


@router.get("/{receivable_id}", response_model=ReceivableResponse)
def get_receivable(
    receivable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    return receivable


@router.put("/{receivable_id}", response_model=ReceivableResponse)
def update_receivable(
    receivable_id: int,
    receivable_in: ReceivableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    return receivable_service.update_receivable(db, receivable, receivable_in)


@router.delete("/{receivable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receivable(
    receivable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> None:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    receivable_service.delete_receivable(db, receivable)


@router.post("/{receivable_id}/mark-received", response_model=ReceivableResponse)
def mark_receivable_received(
    receivable_id: int,
    payload: MarkReceivableReceivedRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")

    return receivable_service.mark_receivable_received(
        db,
        receivable,
        user_id=current_user.id,
        received_at=payload.received_at,
        generate_transaction=payload.generate_transaction,
    )
