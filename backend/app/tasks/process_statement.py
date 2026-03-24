"""Celery task for processing uploaded bank statement files."""

import os
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.utils.logger import logger


@celery_app.task(name="app.tasks.process_statement.process_statement_task", bind=True)
def process_statement_task(self, file_id: int) -> dict:
    """Process a statement file: parse, classify, and import transactions."""
    from app.db.session import SessionLocal
    from app.db.models.statement_file import StatementFile
    from app.db.models.category import Category
    from app.services.file_parser import parse_file
    from app.services.ai_classifier import classify_transaction
    from app.services.transaction_service import compute_dedup_hash, check_duplicate, create_transaction
    from app.schemas.transaction import TransactionCreate
    from app.core.config import settings

    db = SessionLocal()
    try:
        statement = db.query(StatementFile).filter(StatementFile.id == file_id).first()
        if not statement:
            logger.error("StatementFile id=%s not found", file_id)
            return {"status": "error", "detail": "File record not found"}

        statement.status = "processing"
        db.commit()

        file_path = os.path.join(settings.UPLOAD_DIR, statement.filename)
        raw_transactions = parse_file(file_path, statement.file_type)

        categories = db.query(Category).filter(Category.is_active.is_(True)).all()
        category_dicts = [{"id": c.id, "name": c.name} for c in categories]
        category_name_to_id = {c.name: c.id for c in categories}

        imported = 0
        for raw in raw_transactions:
            try:
                desc = str(raw.get("description") or "")
                amount_str = str(raw.get("amount") or "0").replace(",", ".")
                date_str = str(raw.get("date") or "")
                reference = raw.get("reference")

                from decimal import Decimal, InvalidOperation
                try:
                    amount = Decimal(amount_str)
                except InvalidOperation:
                    logger.warning("Invalid amount '%s', skipping", amount_str)
                    continue

                from app.utils.date_utils import parse_date
                parsed_date = parse_date(date_str)
                if parsed_date is None:
                    logger.warning("Cannot parse date '%s', skipping", date_str)
                    continue

                transaction_type = "income" if amount > 0 else "expense"
                amount = abs(amount)

                dedup_hash = compute_dedup_hash(desc, str(amount), str(parsed_date), reference)
                if check_duplicate(db, dedup_hash):
                    logger.debug("Duplicate transaction detected, skipping hash=%s", dedup_hash)
                    continue

                cat_name, confidence = classify_transaction(desc, category_dicts)
                cat_id = category_name_to_id.get(cat_name) if cat_name else None

                tx_create = TransactionCreate(
                    description=desc,
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_date=parsed_date,
                    category_id=cat_id,
                    reference=reference,
                )
                tx = create_transaction(db, tx_create, user_id=statement.user_id)
                if cat_name:
                    tx.ai_category_suggestion = cat_name
                    tx.ai_confidence = confidence
                    tx.ai_suggested_category_id = cat_id
                    tx.status = "pending"
                    db.commit()

                imported += 1
            except Exception as exc:
                logger.warning("Failed to import transaction: %s", exc)
                continue

        statement.transactions_count = imported
        statement.status = "completed"
        db.commit()
        logger.info("Processed file_id=%s: %s transactions imported", file_id, imported)
        return {"status": "completed", "transactions_imported": imported}

    except Exception as exc:
        logger.exception("Error processing file_id=%s: %s", file_id, exc)
        try:
            statement = db.query(StatementFile).filter(StatementFile.id == file_id).first()
            if statement:
                statement.status = "failed"
                statement.error_message = str(exc)[:1000]
                db.commit()
        except Exception:
            pass
        raise
    finally:
        db.close()
