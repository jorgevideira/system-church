"""Celery task for processing uploaded bank statement files."""

import os
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.utils.logger import logger


def _is_learned_type_compatible_with_import(
    *,
    learned_type: str | None,
    inferred_type: str,
    parsed_amount: float,
) -> bool:
    """Prevent learned feedback from inverting trusted bank-statement signs.

    For imported statements, the parser sign is usually more trustworthy than
    historical keyword feedback. We still allow learned feedback when it agrees
    with the inferred type, or when the amount sign is neutral/unknown.
    """
    if learned_type not in {"income", "expense"}:
        return False

    if learned_type == inferred_type:
        return True

    if parsed_amount > 0:
        return learned_type == "income"

    if parsed_amount < 0:
        return learned_type == "expense"

    return True


@celery_app.task(name="app.tasks.process_statement.process_statement_task", bind=True)
def process_statement_task(self, file_id: int, include_duplicates: bool = False) -> dict:
    """Process a statement file: parse, classify, and import transactions."""
    from app.db.session import SessionLocal
    from app.db.models.statement_file import StatementFile
    from app.db.models.transaction import Transaction
    from app.db.models.category import Category
    from app.services.file_parser import detect_bank_name, parse_file
    from app.services.statement_ai_parser import is_enabled as is_statement_ai_enabled, parse_statement_with_ollama
    from app.services.ai_classifier import classify_transaction, infer_transaction_type
    from app.services.ai_learning_service import infer_from_feedback
    from app.services.transaction_service import (
        compute_dedup_hash,
        check_duplicate,
        check_duplicate_same_day_amount,
        create_transaction_from_import,
    )
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
        detected_bank_name = detect_bank_name(file_path, statement.file_type, statement.original_filename)
        raw_transactions = parse_file(file_path, statement.file_type)

        if not raw_transactions and is_statement_ai_enabled():
            logger.info("Traditional parser found no transactions for file_id=%s, trying Ollama fallback.", file_id)
            raw_transactions = parse_statement_with_ollama(file_path, statement.file_type)

        if not raw_transactions:
            statement.transactions_count = 0
            statement.status = "completed"
            statement.error_message = (
                "Nenhuma transacao encontrada no arquivo. "
                "Verifique se o formato e colunas do extrato sao suportados. "
                "Se desejar ampliar a cobertura, habilite o fallback IA com Ollama no ambiente."
            )
            db.commit()
            return {"status": "completed", "transactions_imported": 0, "detail": statement.error_message}

        categories = db.query(Category).filter(Category.is_active.is_(True), Category.tenant_id == statement.tenant_id).all()
        category_dicts = [{"id": c.id, "name": c.name} for c in categories]
        category_name_to_id = {c.name: c.id for c in categories}
        has_existing_bank_history = False
        if detected_bank_name:
            has_existing_bank_history = (
                db.query(Transaction.id)
                .filter(
                    Transaction.tenant_id == statement.tenant_id,
                    Transaction.user_id == statement.user_id,
                    Transaction.source_bank_name == detected_bank_name,
                    (Transaction.statement_file_id.is_(None) | (Transaction.statement_file_id != statement.id)),
                )
                .first()
                is not None
            )

        imported = 0
        skipped_duplicates = 0
        skipped_invalid_amount = 0
        skipped_invalid_date = 0
        skipped_processing_errors = 0
        skipped_inferred_opening_balance = 0
        for raw in raw_transactions:
            try:
                desc = str(raw.get("description") or "")
                if desc == "Saldo inicial inferido do extrato" and has_existing_bank_history:
                    skipped_inferred_opening_balance += 1
                    continue
                amount_str = str(raw.get("amount") or "0").replace(",", ".")
                date_str = str(raw.get("date") or "")
                reference = raw.get("reference")

                from decimal import Decimal, InvalidOperation
                try:
                    amount = Decimal(amount_str)
                except InvalidOperation:
                    logger.warning("Invalid amount '%s', skipping", amount_str)
                    skipped_invalid_amount += 1
                    continue

                from app.utils.date_utils import parse_date
                parsed_date = parse_date(date_str)
                if parsed_date is None:
                    logger.warning("Cannot parse date '%s', skipping", date_str)
                    skipped_invalid_date += 1
                    continue

                parsed_amount = float(amount)
                inferred_type, inferred_confidence = infer_transaction_type(desc, parsed_amount)
                transaction_type = inferred_type
                amount = abs(amount)

                learned_category_name, learned_type, learned_conf = infer_from_feedback(
                    db,
                    tenant_id=statement.tenant_id,
                    user_id=statement.user_id,
                    description=desc,
                )
                if _is_learned_type_compatible_with_import(
                    learned_type=learned_type,
                    inferred_type=transaction_type,
                    parsed_amount=parsed_amount,
                ):
                    transaction_type = learned_type
                    inferred_confidence = max(inferred_confidence, learned_conf)
                elif learned_type in {"income", "expense"}:
                    logger.info(
                        "Ignoring learned_type=%s for imported statement file_id=%s desc=%s parsed_amount=%s inferred_type=%s",
                        learned_type,
                        statement.id,
                        desc[:120],
                        parsed_amount,
                        transaction_type,
                    )

                dedup_hash = compute_dedup_hash(desc, str(amount), str(parsed_date), reference)
                if not include_duplicates:
                    is_dup_day_amount = check_duplicate_same_day_amount(
                        db,
                        tenant_id=statement.tenant_id,
                        user_id=statement.user_id,
                        transaction_date=parsed_date,
                        amount=amount,
                        transaction_type=transaction_type,
                        exclude_statement_file_id=statement.id,
                    )
                    if is_dup_day_amount or check_duplicate(db, dedup_hash):
                        logger.debug("Duplicate transaction detected, skipping file_id=%s date=%s amount=%s", statement.id, parsed_date, amount)
                        skipped_duplicates += 1
                        continue

                cat_name, confidence = classify_transaction(desc, category_dicts)
                if learned_category_name:
                    cat_name = learned_category_name
                    confidence = max(confidence, learned_conf)
                cat_id = category_name_to_id.get(cat_name) if cat_name else None

                tx_create = TransactionCreate(
                    description=desc,
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_date=parsed_date,
                    category_id=cat_id,
                    reference=reference,
                    source_bank_name=detected_bank_name,
                )
                tx = create_transaction_from_import(
                    db,
                    tx_create,
                    user_id=statement.user_id,
                    tenant_id=statement.tenant_id,
                    statement_file_id=statement.id,
                )
                tx.ai_confidence = max(float(tx.ai_confidence or 0), inferred_confidence)
                if cat_name:
                    tx.ai_category_suggestion = cat_name
                    tx.ai_confidence = max(float(tx.ai_confidence or 0), confidence)
                    tx.ai_suggested_category_id = cat_id
                    tx.status = "pending"
                    db.commit()

                imported += 1
            except Exception as exc:
                logger.warning("Failed to import transaction: %s", exc)
                skipped_processing_errors += 1
                continue

        total_for_file = (
            db.query(Transaction)
            .filter(Transaction.statement_file_id == statement.id)
            .count()
        )
        statement.transactions_count = total_for_file
        statement.status = "completed"
        skipped_total = (
            skipped_duplicates
            + skipped_invalid_amount
            + skipped_invalid_date
            + skipped_processing_errors
            + skipped_inferred_opening_balance
        )
        if imported == 0:
            statement.error_message = (
                "Arquivo processado, mas nenhuma linha valida foi importada. "
                f"Rejeicoes: duplicadas={skipped_duplicates}, "
                f"valor_invalido={skipped_invalid_amount}, data_invalida={skipped_invalid_date}, "
                f"erros={skipped_processing_errors}, saldo_inicial_ignorado={skipped_inferred_opening_balance}."
            )[:1000]
        elif skipped_total > 0:
            statement.error_message = (
                "Processado com avisos. "
                f"Importadas_nesta_execucao={imported}, total_no_arquivo={total_for_file}. "
                f"Rejeicoes: duplicadas={skipped_duplicates}, "
                f"valor_invalido={skipped_invalid_amount}, data_invalida={skipped_invalid_date}, "
                f"erros={skipped_processing_errors}, saldo_inicial_ignorado={skipped_inferred_opening_balance}."
            )[:1000]
        else:
            statement.error_message = None
        db.commit()
        logger.info(
            "Processed file_id=%s: imported=%s total_for_file=%s",
            file_id,
            imported,
            total_for_file,
        )
        return {
            "status": "completed",
            "transactions_imported": imported,
            "transactions_total_for_file": total_for_file,
            "include_duplicates": include_duplicates,
            "skipped": {
                "duplicates": skipped_duplicates,
                "invalid_amount": skipped_invalid_amount,
                "invalid_date": skipped_invalid_date,
                "processing_errors": skipped_processing_errors,
                "inferred_opening_balance": skipped_inferred_opening_balance,
            },
        }

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
