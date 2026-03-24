import os
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.constants import FILE_TYPES, MAX_FILE_SIZE_BYTES
from app.db.models.statement_file import StatementFile
from app.db.models.user import User

router = APIRouter()


def _get_file_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {FILE_TYPES}",
        )
    return ext


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    file_type = _get_file_type(file.filename or "")
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE // (1024*1024)} MB",
        )
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4()}.{file_type}"
    dest_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    with open(dest_path, "wb") as f:
        f.write(contents)
    statement_file = StatementFile(
        filename=unique_name,
        original_filename=file.filename or unique_name,
        file_type=file_type,
        file_size=len(contents),
        status="pending",
        user_id=current_user.id,
    )
    db.add(statement_file)
    db.commit()
    db.refresh(statement_file)

    # Trigger background processing if Celery is available
    try:
        from app.tasks.process_statement import process_statement_task
        process_statement_task.delay(statement_file.id)
    except Exception:
        pass

    return {
        "id": statement_file.id,
        "filename": statement_file.filename,
        "original_filename": statement_file.original_filename,
        "file_type": statement_file.file_type,
        "file_size": statement_file.file_size,
        "status": statement_file.status,
        "created_at": statement_file.created_at.isoformat(),
    }


@router.get("/{file_id}")
def get_upload_status(
    file_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
) -> dict:
    record = db.query(StatementFile).filter(StatementFile.id == file_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return {
        "id": record.id,
        "filename": record.filename,
        "original_filename": record.original_filename,
        "file_type": record.file_type,
        "file_size": record.file_size,
        "status": record.status,
        "error_message": record.error_message,
        "transactions_count": record.transactions_count,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }


@router.get("/", response_model=List[dict])
def list_uploads(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[dict]:
    records = (
        db.query(StatementFile)
        .filter(StatementFile.user_id == current_user.id)
        .order_by(StatementFile.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "original_filename": r.original_filename,
            "file_type": r.file_type,
            "file_size": r.file_size,
            "status": r.status,
            "transactions_count": r.transactions_count,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]
