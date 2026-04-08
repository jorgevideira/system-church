import gzip
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db, require_editor
from app.core.config import settings
from app.db.models.tenant import Tenant
from app.db.models.transaction import Transaction
from app.db.models.transaction_attachment import TransactionAttachment
from app.db.models.user import User
from app.schemas.transaction_attachment import TransactionAttachmentResponse

router = APIRouter()

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
MAX_ATTACHMENT_SIZE = 15 * 1024 * 1024  # 15 MB


def _safe_filename(name: str) -> str:
    return os.path.basename(name).replace("\x00", "").strip() or "attachment"


def _get_transaction_for_user(db: Session, transaction_id: int, user: User, tenant: Tenant) -> Transaction:
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user.id, Transaction.tenant_id == tenant.id)
        .first()
    )
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.get("/{transaction_id}/attachments", response_model=List[TransactionAttachmentResponse])
def list_transaction_attachments(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[TransactionAttachment]:
    _get_transaction_for_user(db, transaction_id, current_user, current_tenant)
    return (
        db.query(TransactionAttachment)
        .filter(
            TransactionAttachment.transaction_id == transaction_id,
            TransactionAttachment.user_id == current_user.id,
        )
        .order_by(TransactionAttachment.created_at.desc())
        .all()
    )


@router.post(
    "/{transaction_id}/attachments",
    response_model=TransactionAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_transaction_attachment(
    transaction_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TransactionAttachment:
    _get_transaction_for_user(db, transaction_id, current_user, current_tenant)

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required")

    mime_type = (file.content_type or "").lower()
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and image files are allowed",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    if len(content) > MAX_ATTACHMENT_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large (max 15 MB)")

    compressed = gzip.compress(content, compresslevel=9)
    os.makedirs(settings.ATTACHMENT_DIR, exist_ok=True)

    storage_filename = f"{uuid.uuid4()}.gz"
    storage_path = os.path.join(settings.ATTACHMENT_DIR, storage_filename)
    with open(storage_path, "wb") as f:
        f.write(compressed)

    attachment = TransactionAttachment(
        transaction_id=transaction_id,
        user_id=current_user.id,
        storage_filename=storage_filename,
        original_filename=_safe_filename(file.filename),
        mime_type=mime_type,
        original_size=len(content),
        compressed_size=len(compressed),
        compression="gzip",
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/{transaction_id}/attachments/{attachment_id}/download")
def download_transaction_attachment(
    transaction_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> Response:
    _get_transaction_for_user(db, transaction_id, current_user, current_tenant)

    attachment = (
        db.query(TransactionAttachment)
        .filter(
            TransactionAttachment.id == attachment_id,
            TransactionAttachment.transaction_id == transaction_id,
            TransactionAttachment.user_id == current_user.id,
        )
        .first()
    )
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

    storage_path = os.path.join(settings.ATTACHMENT_DIR, attachment.storage_filename)
    if not os.path.exists(storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")

    with open(storage_path, "rb") as f:
        compressed = f.read()

    try:
        data = gzip.decompress(compressed)
    except OSError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Corrupted attachment data: {exc}")

    headers = {
        "Content-Disposition": f'attachment; filename="{attachment.original_filename}"'
    }
    return Response(content=data, media_type=attachment.mime_type, headers=headers)
