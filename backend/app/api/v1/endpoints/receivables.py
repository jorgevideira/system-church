import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db, require_editor
from app.core.config import settings
from app.db.models.tenant import Tenant
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

ALLOWED_RECEIVABLE_ATTACHMENT_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_RECEIVABLE_ATTACHMENT_SIZE = 15 * 1024 * 1024  # 15 MB


def _safe_filename(name: str) -> str:
    return os.path.basename(name).replace("\x00", "").strip() or "attachment"


def _receivable_attachment_dir() -> str:
    return os.path.join(settings.UPLOAD_DIR, "receivables")


@router.get("/", response_model=list[ReceivableResponse])
def list_receivables(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ReceivableResponse]:
    return receivable_service.list_receivables(db, current_user.id, current_tenant.id, status_filter=status_filter)


@router.post("/", response_model=ReceivableResponse, status_code=status.HTTP_201_CREATED)
def create_receivable(
    receivable_in: ReceivableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ReceivableResponse:
    return receivable_service.create_receivable(db, receivable_in, user_id=current_user.id, tenant_id=current_tenant.id)


@router.get("/alerts/summary", response_model=ReceivableAlertsSummary)
def get_receivables_alerts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ReceivableAlertsSummary:
    return ReceivableAlertsSummary(**receivable_service.get_alerts_summary(db, current_user.id, current_tenant.id))


@router.get("/{receivable_id}", response_model=ReceivableResponse)
def get_receivable(
    receivable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id, current_tenant.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    return receivable


@router.put("/{receivable_id}", response_model=ReceivableResponse)
def update_receivable(
    receivable_id: int,
    receivable_in: ReceivableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id, current_tenant.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    return receivable_service.update_receivable(db, receivable, receivable_in)


@router.delete("/{receivable_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receivable(
    receivable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id, current_tenant.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    if receivable.attachment_storage_filename:
        storage_path = os.path.join(_receivable_attachment_dir(), receivable.attachment_storage_filename)
        if os.path.exists(storage_path):
            os.remove(storage_path)
    receivable_service.delete_receivable(db, receivable)


@router.post("/{receivable_id}/mark-received", response_model=ReceivableResponse)
def mark_receivable_received(
    receivable_id: int,
    payload: MarkReceivableReceivedRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id, current_tenant.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")

    return receivable_service.mark_receivable_received(
        db,
        receivable,
        user_id=current_user.id,
        received_at=payload.received_at,
        receipt_method=payload.receipt_method,
        generate_transaction=payload.generate_transaction,
    )


@router.post("/{receivable_id}/attachment", response_model=ReceivableResponse)
async def upload_receivable_attachment(
    receivable_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id, current_tenant.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required")

    mime_type = (file.content_type or "").lower()
    if mime_type not in ALLOWED_RECEIVABLE_ATTACHMENT_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and image files are allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    if len(content) > MAX_RECEIVABLE_ATTACHMENT_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 15 MB)")

    os.makedirs(_receivable_attachment_dir(), exist_ok=True)

    if receivable.attachment_storage_filename:
        old_path = os.path.join(_receivable_attachment_dir(), receivable.attachment_storage_filename)
        if os.path.exists(old_path):
            os.remove(old_path)

    extension = os.path.splitext(_safe_filename(file.filename))[1] or ".bin"
    storage_filename = f"{uuid.uuid4()}{extension}"
    storage_path = os.path.join(_receivable_attachment_dir(), storage_filename)
    with open(storage_path, "wb") as out:
        out.write(content)

    return receivable_service.set_receivable_attachment(
        db,
        receivable,
        storage_filename=storage_filename,
        original_filename=_safe_filename(file.filename),
        mime_type=mime_type,
    )


@router.get("/{receivable_id}/attachment/download")
def download_receivable_attachment(
    receivable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> Response:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id, current_tenant.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    if not receivable.attachment_storage_filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable attachment not found")

    storage_path = os.path.join(_receivable_attachment_dir(), receivable.attachment_storage_filename)
    if not os.path.exists(storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")

    with open(storage_path, "rb") as f:
        data = f.read()

    headers = {"Content-Disposition": f'attachment; filename="{receivable.attachment_original_filename or "comprovante"}"'}
    return Response(content=data, media_type=receivable.attachment_mime_type or "application/octet-stream", headers=headers)


@router.delete("/{receivable_id}/attachment", response_model=ReceivableResponse)
def delete_receivable_attachment(
    receivable_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ReceivableResponse:
    receivable = receivable_service.get_receivable(db, receivable_id, current_user.id, current_tenant.id)
    if not receivable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receivable not found")
    if receivable.attachment_storage_filename:
        storage_path = os.path.join(_receivable_attachment_dir(), receivable.attachment_storage_filename)
        if os.path.exists(storage_path):
            os.remove(storage_path)
    return receivable_service.clear_receivable_attachment(db, receivable)
