from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.db.models.statement_file import StatementFile
from app.db.models.transaction import Transaction
from app.tasks.process_statement import process_statement_task
from tests.conftest import TestingSessionLocal, get_or_create_test_tenant


def test_process_statement_uses_ollama_fallback_when_parser_returns_empty(test_db, test_admin, monkeypatch):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)
    test_db.commit()

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = "ai-fallback-test.pdf"
    file_path = upload_dir / filename
    file_path.write_text("conteudo sem parser tradicional", encoding="utf-8")

    statement = StatementFile(
        tenant_id=tenant.id,
        filename=filename,
        original_filename="nubank-extrato.pdf",
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
    monkeypatch.setattr("app.services.file_parser.parse_file", lambda *_args, **_kwargs: [])
    monkeypatch.setattr("app.services.statement_ai_parser.is_enabled", lambda: True)
    monkeypatch.setattr(
        "app.services.statement_ai_parser.parse_statement_with_ollama",
        lambda *_args, **_kwargs: [
            {
                "description": "Pix recebido Maria",
                "amount": "250.00",
                "date": "2026-04-14",
                "reference": "ref-01",
            }
        ],
    )

    result = process_statement_task.run(statement.id, False)

    assert result["status"] == "completed"
    assert result["transactions_imported"] == 1

    transactions = (
        test_db.query(Transaction)
        .filter(Transaction.statement_file_id == statement.id)
        .all()
    )
    assert len(transactions) == 1
    assert transactions[0].description == "Pix recebido Maria"
    assert float(transactions[0].amount) == 250.0
    assert transactions[0].transaction_type == "income"

    file_path.unlink(missing_ok=True)
