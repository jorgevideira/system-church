import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant, get_db, require_finance_read, require_finance_write
from app.core.config import settings
from app.db.models.tenant import Tenant
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

ALLOWED_PAYABLE_ATTACHMENT_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_PAYABLE_ATTACHMENT_SIZE = 15 * 1024 * 1024  # 15 MB


def _safe_filename(name: str) -> str:
    return os.path.basename(name).replace("\x00", "").strip() or "attachment"


def _payable_attachment_dir() -> str:
    return os.path.join(settings.UPLOAD_DIR, "payables")


@router.get("/", response_model=list[PayableResponse])
def list_payables(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[PayableResponse]:
    return payable_service.list_payables(db, current_user.id, current_tenant.id, status_filter=status_filter)


@router.post("/", response_model=PayableResponse, status_code=status.HTTP_201_CREATED)
def create_payable(
    payable_in: PayableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PayableResponse:
    return payable_service.create_payable(db, payable_in, user_id=current_user.id, tenant_id=current_tenant.id)


@router.get("/alerts/summary", response_model=PayableAlertsSummary)
def get_payables_alerts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PayableAlertsSummary:
    return PayableAlertsSummary(**payable_service.get_alerts_summary(db, current_user.id, current_tenant.id))


@router.get("/{payable_id}", response_model=PayableResponse)
def get_payable(
    payable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id, current_tenant.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    return payable


@router.put("/{payable_id}", response_model=PayableResponse)
def update_payable(
    payable_id: int,
    payable_in: PayableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id, current_tenant.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    return payable_service.update_payable(db, payable, payable_in)


@router.delete("/{payable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payable(
    payable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    payable = payable_service.get_payable(db, payable_id, current_user.id, current_tenant.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    if payable.attachment_storage_filename:
        storage_path = os.path.join(_payable_attachment_dir(), payable.attachment_storage_filename)
        if os.path.exists(storage_path):
            os.remove(storage_path)
    payable_service.delete_payable(db, payable)


@router.post("/{payable_id}/mark-paid", response_model=PayableResponse)
def mark_payable_paid(
    payable_id: int,
    payload: MarkPayablePaidRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id, current_tenant.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")

    return payable_service.mark_payable_paid(
        db,
        payable,
        user_id=current_user.id,
        paid_at=payload.paid_at,
        payment_method=payload.payment_method,
        generate_transaction=payload.generate_transaction,
    )


@router.post("/{payable_id}/attachment", response_model=PayableResponse)
async def upload_payable_attachment(
    payable_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id, current_tenant.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required")

    mime_type = (file.content_type or "").lower()
    if mime_type not in ALLOWED_PAYABLE_ATTACHMENT_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and image files are allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    if len(content) > MAX_PAYABLE_ATTACHMENT_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 15 MB)")

    os.makedirs(_payable_attachment_dir(), exist_ok=True)

    if payable.attachment_storage_filename:
        old_path = os.path.join(_payable_attachment_dir(), payable.attachment_storage_filename)
        if os.path.exists(old_path):
            os.remove(old_path)

    extension = os.path.splitext(_safe_filename(file.filename))[1] or ".bin"
    storage_filename = f"{uuid.uuid4()}{extension}"
    storage_path = os.path.join(_payable_attachment_dir(), storage_filename)
    with open(storage_path, "wb") as out:
        out.write(content)

    return payable_service.set_payable_attachment(
        db,
        payable,
        storage_filename=storage_filename,
        original_filename=_safe_filename(file.filename),
        mime_type=mime_type,
    )


@router.get("/{payable_id}/attachment/download")
def download_payable_attachment(
    payable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> Response:
    payable = payable_service.get_payable(db, payable_id, current_user.id, current_tenant.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    if not payable.attachment_storage_filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable attachment not found")

    storage_path = os.path.join(_payable_attachment_dir(), payable.attachment_storage_filename)
    if not os.path.exists(storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")

    with open(storage_path, "rb") as f:
        data = f.read()

    headers = {"Content-Disposition": f'attachment; filename="{payable.attachment_original_filename or "boleto"}"'}
    return Response(content=data, media_type=payable.attachment_mime_type or "application/octet-stream", headers=headers)


@router.delete("/{payable_id}/attachment", response_model=PayableResponse)
def delete_payable_attachment(
    payable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_finance_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> PayableResponse:
    payable = payable_service.get_payable(db, payable_id, current_user.id, current_tenant.id)
    if not payable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payable not found")
    if payable.attachment_storage_filename:
        storage_path = os.path.join(_payable_attachment_dir(), payable.attachment_storage_filename)
        if os.path.exists(storage_path):
            os.remove(storage_path)
    return payable_service.clear_payable_attachment(db, payable)
