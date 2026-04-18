import os
import uuid
import hashlib
from decimal import Decimal, InvalidOperation
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db
from app.core.config import settings
from app.core.constants import FILE_TYPES, MAX_FILE_SIZE_BYTES
from app.db.models.statement_file import StatementFile
from app.db.models.tenant import Tenant
from app.db.models.transaction import Transaction
from app.db.models.user import User

router = APIRouter()


def _dup_choice_key(
    description: str,
    amount: Decimal,
    date_iso: str,
    reference: str | None,
    transaction_type: str,
) -> str:
    raw = f"{description}|{amount}|{date_iso}|{reference or ''}|{transaction_type}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _get_file_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {FILE_TYPES}",
        )
    return ext


def _count_transactions_for_statement(db: Session, statement_file_id: int) -> int:
    return (
        db.query(Transaction)
        .filter(Transaction.statement_file_id == statement_file_id)
        .count()
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
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
        tenant_id=current_tenant.id,
    )
    db.add(statement_file)
    db.commit()
    db.refresh(statement_file)

    # Trigger background processing if Celery is available
    try:
        from app.tasks.process_statement import process_statement_task
        process_statement_task.delay(statement_file.id, False)
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
    current_tenant: Tenant = Depends(get_current_tenant),
) -> dict:
    record = db.query(StatementFile).filter(StatementFile.id == file_id, StatementFile.tenant_id == current_tenant.id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    actual_count = _count_transactions_for_statement(db, record.id)
    if record.transactions_count != actual_count:
        record.transactions_count = actual_count
        db.commit()
    return {
        "id": record.id,
        "filename": record.filename,
        "original_filename": record.original_filename,
        "file_type": record.file_type,
        "file_size": record.file_size,
        "status": record.status,
        "error_message": record.error_message,
        "transactions_count": actual_count,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
    }


@router.post("/{file_id}/retry")
def retry_upload_processing(
    file_id: int,
    include_duplicates: bool = False,
    reset_existing: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> dict:
    record = (
        db.query(StatementFile)
        .filter(StatementFile.id == file_id, StatementFile.user_id == current_user.id, StatementFile.tenant_id == current_tenant.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if reset_existing:
        db.query(Transaction).filter(Transaction.statement_file_id == record.id).delete(synchronize_session=False)
        record.transactions_count = 0

    record.status = "pending"
    record.error_message = None
    db.commit()

    try:
        from app.tasks.process_statement import process_statement_task

        process_statement_task.delay(record.id, include_duplicates)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue processing: {exc}",
        )

    return {
        "id": record.id,
        "status": record.status,
        "include_duplicates": include_duplicates,
        "reset_existing": reset_existing,
        "detail": "Processamento reenfileirado com sucesso.",
    }


@router.get("/{file_id}/duplicates-preview")
def get_upload_duplicates_preview(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> dict:
    record = (
        db.query(StatementFile)
        .filter(StatementFile.id == file_id, StatementFile.user_id == current_user.id, StatementFile.tenant_id == current_tenant.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    try:
        from app.core.config import settings
        from app.services.ai_classifier import infer_transaction_type
        from app.services.file_parser import parse_file
        from app.services.transaction_service import check_duplicate_same_day_amount
        from app.utils.date_utils import parse_date

        file_path = os.path.join(settings.UPLOAD_DIR, record.filename)
        parsed = parse_file(file_path, record.file_type)

        duplicates: list[dict] = []
        for raw in parsed:
            desc = str(raw.get("description") or "").strip()
            amount_str = str(raw.get("amount") or "0").replace(",", ".")
            date_str = str(raw.get("date") or "")
            reference = raw.get("reference")

            try:
                raw_amount = Decimal(amount_str)
                amount = abs(raw_amount)
            except InvalidOperation:
                continue

            parsed_date = parse_date(date_str)
            if parsed_date is None:
                continue

            inferred_type, _ = infer_transaction_type(desc, float(raw_amount))
            is_dup = check_duplicate_same_day_amount(
                db,
                tenant_id=record.tenant_id,
                user_id=record.user_id,
                transaction_date=parsed_date,
                amount=amount,
                transaction_type=inferred_type,
                exclude_statement_file_id=record.id,
            )
            if not is_dup:
                continue

            key = _dup_choice_key(desc, amount, str(parsed_date), reference, inferred_type)
            existing = (
                db.query(Transaction)
                .filter(
                    Transaction.user_id == record.user_id,
                    Transaction.tenant_id == record.tenant_id,
                    Transaction.transaction_date == parsed_date,
                    Transaction.amount == amount,
                    Transaction.transaction_type == inferred_type,
                    Transaction.statement_file_id != record.id,
                )
                .order_by(Transaction.created_at.desc())
                .first()
            )
            duplicates.append(
                {
                    "key": key,
                    "date": str(parsed_date),
                    "amount": str(amount),
                    "transaction_type": inferred_type,
                    "description": desc,
                    "reference": reference,
                    "existing": {
                        "id": existing.id,
                        "date": str(existing.transaction_date),
                        "amount": str(existing.amount),
                        "transaction_type": existing.transaction_type,
                        "description": existing.description,
                        "reference": existing.reference,
                        "source_bank": existing.source_bank,
                    } if existing else None,
                }
            )

        # Remove duplicates in preview itself by key
        uniq: dict[str, dict] = {}
        for d in duplicates:
            uniq[d["key"]] = d

        return {
            "file_id": record.id,
            "duplicates": list(uniq.values()),
            "count": len(uniq),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build duplicates preview: {exc}",
        )


@router.post("/{file_id}/duplicate-selection")
def apply_duplicate_selection(
    file_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> dict:
    record = (
        db.query(StatementFile)
        .filter(StatementFile.id == file_id, StatementFile.user_id == current_user.id, StatementFile.tenant_id == current_tenant.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    selected_keys = set(payload.get("selected_keys") or [])

    # Evaluate duplicates imported for this file against existing user transactions.
    current_file_txs = (
        db.query(Transaction)
        .filter(Transaction.statement_file_id == record.id, Transaction.user_id == current_user.id, Transaction.tenant_id == current_tenant.id)
        .all()
    )

    removed = 0
    for tx in current_file_txs:
        has_other_same_day_amount = (
            db.query(Transaction)
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.tenant_id == current_tenant.id,
                Transaction.transaction_date == tx.transaction_date,
                Transaction.amount == tx.amount,
                Transaction.transaction_type == tx.transaction_type,
                Transaction.id != tx.id,
            )
            .first()
            is not None
        )
        if not has_other_same_day_amount:
            continue

        key = _dup_choice_key(
            tx.description,
            tx.amount,
            str(tx.transaction_date),
            tx.reference,
            tx.transaction_type,
        )
        if key not in selected_keys:
            db.delete(tx)
            removed += 1

    db.commit()

    total = (
        db.query(Transaction)
        .filter(Transaction.statement_file_id == record.id, Transaction.user_id == current_user.id, Transaction.tenant_id == current_tenant.id)
        .count()
    )
    record.transactions_count = total
    db.commit()

    return {
        "file_id": record.id,
        "removed": removed,
        "kept": total,
        "selected_count": len(selected_keys),
    }


@router.get("/", response_model=List[dict])
def list_uploads(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[dict]:
    records = (
        db.query(StatementFile)
        .filter(StatementFile.user_id == current_user.id, StatementFile.tenant_id == current_tenant.id)
        .order_by(StatementFile.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    payload: list[dict] = []
    updated = False
    for r in records:
        actual_count = _count_transactions_for_statement(db, r.id)
        if r.transactions_count != actual_count:
            r.transactions_count = actual_count
            updated = True
        payload.append(
            {
                "id": r.id,
                "filename": r.filename,
                "original_filename": r.original_filename,
                "file_type": r.file_type,
                "file_size": r.file_size,
                "status": r.status,
                "error_message": r.error_message,
                "transactions_count": actual_count,
                "created_at": r.created_at.isoformat(),
            }
        )
    if updated:
        db.commit()
    return payload
