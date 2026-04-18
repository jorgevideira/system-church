from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.db.models.statement_file import StatementFile
from app.db.models.transaction import Transaction
from app.tasks.process_statement import process_statement_task
from tests.conftest import TestingSessionLocal, get_or_create_test_tenant


def test_process_statement_skips_inferred_opening_balance_when_bank_history_exists(test_db, test_admin, monkeypatch):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)
    test_db.commit()

    existing = Transaction(
        tenant_id=tenant.id,
        user_id=test_admin.id,
        description="Pix recebido antigo",
        amount=100,
        transaction_type="income",
        transaction_date=datetime(2026, 1, 10).date(),
        source_bank_name="PagSeguro",
        status="confirmed",
    )
    test_db.add(existing)
    test_db.commit()

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = "opening-balance-skip-test.pdf"
    file_path = upload_dir / filename
    file_path.write_text("conteudo pdf pagseguro", encoding="utf-8")

    statement = StatementFile(
        tenant_id=tenant.id,
        filename=filename,
        original_filename="Extrato da Conta - PagSeguro.pdf",
        file_type="pdf",
        file_size=file_path.stat().st_size,
        status="pending",
        user_id=test_admin.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    test_db.add(statement)
    test_db.commit()
    test_db.refresh(statement)

    monkeypatch.setattr("app.db.session.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(
        "app.services.file_parser.detect_bank_name",
        lambda *_args, **_kwargs: "PagSeguro",
    )
    monkeypatch.setattr(
        "app.services.file_parser.parse_file",
        lambda *_args, **_kwargs: [
            {
                "description": "Saldo inicial inferido do extrato",
                "amount": "489.83",
                "date": "2026-01-15",
                "reference": "pagseguro-opening-2026-01-15",
            },
            {
                "description": "Pix recebido Maria",
                "amount": "250.00",
                "date": "2026-01-16",
                "reference": "ref-01",
            },
        ],
    )
    monkeypatch.setattr("app.services.statement_ai_parser.is_enabled", lambda: False)

    result = process_statement_task.run(statement.id, False)

    assert result["status"] == "completed"
    assert result["transactions_imported"] == 1
    assert result["skipped"]["inferred_opening_balance"] == 1

    transactions = (
        test_db.query(Transaction)
        .filter(Transaction.statement_file_id == statement.id)
        .all()
    )
    assert len(transactions) == 1
    assert transactions[0].description == "Pix recebido Maria"

    file_path.unlink(missing_ok=True)
