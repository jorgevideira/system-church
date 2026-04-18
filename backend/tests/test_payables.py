"""Payables endpoint tests for payment metadata and attachments."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.transaction import Transaction
from app.db.models.user import User
from tests.conftest import auth_headers, ensure_membership, get_or_create_test_tenant


@pytest.fixture
def editor_user(test_db: Session) -> User:
    existing = test_db.query(User).filter(User.email == "payable-editor@test.com").first()
    if existing:
        return existing
    tenant = get_or_create_test_tenant(test_db)
    user = User(
        email="payable-editor@test.com",
        full_name="Payable Editor",
        role="editor",
        hashed_password=get_password_hash("editorpass123"),
        is_active=True,
        active_tenant_id=tenant.id,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    ensure_membership(test_db, user, tenant, role="editor", is_default=True)
    return user


def _create_payable(test_client: TestClient, headers: dict) -> dict:
    response = test_client.post(
        "/api/v1/payables/",
        json={
            "description": "Conta de teste",
            "amount": "120.50",
            "due_date": "2026-03-31",
            "category_id": None,
            "ministry_id": None,
            "source_bank_name": "Bradesco",
            "notes": "Teste",
            "expense_profile": "fixed",
            "is_recurring": False,
            "recurrence_type": None,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_mark_payable_paid_with_payment_method_and_profile(
    test_client: TestClient,
    test_db: Session,
    editor_user: User,
):
    headers = auth_headers(editor_user)
    payable = _create_payable(test_client, headers)

    paid_resp = test_client.post(
        f"/api/v1/payables/{payable['id']}/mark-paid",
        json={
            "paid_at": "2026-03-27",
            "payment_method": "pix",
            "generate_transaction": True,
        },
        headers=headers,
    )
    assert paid_resp.status_code == 200
    data = paid_resp.json()
    assert data["status"] == "paid"
    assert data["paid_at"] == "2026-03-27"
    assert data["payment_method"] == "pix"
    assert data["payment_transaction_id"] is not None

    tx = test_db.query(Transaction).filter(Transaction.id == data["payment_transaction_id"]).first()
    assert tx is not None
    assert tx.reference == f"payable:{payable['id']}"
    assert tx.expense_profile == "fixed"
    assert tx.transaction_date == date(2026, 3, 27)


def test_delete_payable_also_deletes_linked_transaction(
    test_client: TestClient,
    test_db: Session,
    editor_user: User,
):
    headers = auth_headers(editor_user)
    payable = _create_payable(test_client, headers)

    paid_resp = test_client.post(
        f"/api/v1/payables/{payable['id']}/mark-paid",
        json={"paid_at": "2026-03-27", "payment_method": "cash", "generate_transaction": True},
        headers=headers,
    )
    assert paid_resp.status_code == 200
    tx_id = paid_resp.json()["payment_transaction_id"]
    assert tx_id is not None

    delete_resp = test_client.delete(f"/api/v1/payables/{payable['id']}", headers=headers)
    assert delete_resp.status_code == 204

    tx = test_db.query(Transaction).filter(Transaction.id == tx_id).first()
    assert tx is None


def test_payable_attachment_upload_download_delete(
    test_client: TestClient,
    editor_user: User,
    monkeypatch,
    tmp_path,
):
    headers = auth_headers(editor_user)
    payable = _create_payable(test_client, headers)

    upload_root = tmp_path / "uploads"
    upload_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_root))

    files = {"file": ("boleto.pdf", b"%PDF-1.4 test boleto", "application/pdf")}
    upload_resp = test_client.post(
        f"/api/v1/payables/{payable['id']}/attachment",
        files=files,
        headers=headers,
    )
    assert upload_resp.status_code == 200
    uploaded = upload_resp.json()
    assert uploaded["attachment_original_filename"] == "boleto.pdf"
    assert uploaded["attachment_mime_type"] == "application/pdf"

    download_resp = test_client.get(
        f"/api/v1/payables/{payable['id']}/attachment/download",
        headers=headers,
    )
    assert download_resp.status_code == 200
    assert download_resp.content == b"%PDF-1.4 test boleto"

    delete_resp = test_client.delete(
        f"/api/v1/payables/{payable['id']}/attachment",
        headers=headers,
    )
    assert delete_resp.status_code == 200
    deleted = delete_resp.json()
    assert deleted["attachment_original_filename"] is None
    assert deleted["attachment_mime_type"] is None
