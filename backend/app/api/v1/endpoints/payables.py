from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db, require_editor
from app.db.models.user import User
from app.schemas.payable import (
    MarkPayablePaidRequest,
    PayableAlertsSummary,
    PayableCreate,
    PayableResponse,
    PayableUpdate,
)
from app.services import payable_service

router = APIRouter()


@router.get("/", response_model=list[PayableResponse])
def list_payables(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[PayableResponse]:
    return payable_service.list_payables(db, current_user.id, status_filter=status_filter)


@router.post("/", response_model=PayableResponse, status_code=status.HTTP_201_CREATED)
def create_payable(
    payable_in: PayableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> PayableResponse:
    return payable_service.create_payable(db, payable_in, user_id=current_user.id)


@router.get("/alerts/summary", response_model=PayableAlertsSummary)
def get_payables_alerts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PayableAlertsSummary:
    return PayableAlertsSummary(**payable_service.get_alerts_summary(db, current_user.id))


@router.get("/{payable_id}", response_model=PayableResponse)
def get_payable(
    payable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    return payable


@router.put("/{payable_id}", response_model=PayableResponse)
def update_payable(
    payable_id: int,
    payable_in: PayableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    return payable_service.update_payable(db, payable, payable_in)


@router.delete("/{payable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payable(
    payable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> None:
    payable = payable_service.get_payable(db, payable_id, current_user.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    payable_service.delete_payable(db, payable)


@router.post("/{payable_id}/mark-paid", response_model=PayableResponse)
def mark_payable_paid(
    payable_id: int,
    payload: MarkPayablePaidRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")

    return payable_service.mark_payable_paid(
        db,
        payable,
        user_id=current_user.id,
        paid_at=payload.paid_at,
        generate_transaction=payload.generate_transaction,
    )