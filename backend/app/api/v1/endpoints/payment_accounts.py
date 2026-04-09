from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db, require_admin
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.payment_account import PaymentAccountCreate, PaymentAccountResponse, PaymentAccountUpdate
from app.services import payment_account_service

router = APIRouter()


@router.get("/", response_model=List[PaymentAccountResponse])
def list_payment_accounts(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[PaymentAccountResponse]:
    return payment_account_service.list_payment_account_responses(db, current_tenant.id)


@router.post("/", response_model=PaymentAccountResponse, status_code=status.HTTP_201_CREATED)
def create_payment_account(
    payload: PaymentAccountCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PaymentAccountResponse:
    try:
        account = payment_account_service.create_payment_account(db, current_tenant.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return payment_account_service.to_response(account)


@router.put("/{account_id}", response_model=PaymentAccountResponse)
def update_payment_account(
    account_id: int,
    payload: PaymentAccountUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PaymentAccountResponse:
    account = payment_account_service.get_payment_account(db, account_id, current_tenant.id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment account not found")
    try:
        updated = payment_account_service.update_payment_account(db, account, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return payment_account_service.to_response(updated)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_account(
    account_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    account = payment_account_service.get_payment_account(db, account_id, current_tenant.id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment account not found")
    payment_account_service.delete_payment_account(db, account)
