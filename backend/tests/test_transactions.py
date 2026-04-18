from typing import List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.models.category import Category
from app.db.models.user import User
from tests.conftest import auth_headers, ensure_membership, get_or_create_test_tenant


@pytest.fixture
def editor_user(test_db: Session) -> User:
    existing = test_db.query(User).filter(User.email == "editor@test.com").first()
    if existing:
        return existing
    tenant = get_or_create_test_tenant(test_db)
    user = User(
        email="editor@test.com",
        full_name="Editor User",
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


def _create_tx(test_client, headers, suffix=""):
    import uuid
    desc = f"Test tithe payment {suffix or uuid.uuid4().hex[:8]}"
    return test_client.post(
        "/api/v1/transactions/",
        json={
            "description": desc,
            "amount": "150.00",
            "transaction_type": "income",
            "transaction_date": "2024-01-15",
        },
        headers=headers,
    )


def test_create_transaction(test_client: TestClient, editor_user: User):
    headers = auth_headers(editor_user)
    response = _create_tx(test_client, headers)
    assert response.status_code == 201
    data = response.json()
    assert data["description"].startswith("Test tithe payment")
    assert float(data["amount"]) == 150.0


def test_get_transactions(test_client: TestClient, editor_user: User):
    headers = auth_headers(editor_user)
    _create_tx(test_client, headers)
    response = test_client.get("/api/v1/transactions/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_filter_transactions(test_client: TestClient, editor_user: User):
    headers = auth_headers(editor_user)
    _create_tx(test_client, headers)
    response = test_client.get(
        "/api/v1/transactions/",
        params={"transaction_type": "income", "start_date": "2024-01-01"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["transaction_type"] == "income"


def test_update_transaction(test_client: TestClient, editor_user: User):
    headers = auth_headers(editor_user)
    create_resp = _create_tx(test_client, headers)
    assert create_resp.status_code == 201
    tx_id = create_resp.json()["id"]

    response = test_client.put(
        f"/api/v1/transactions/{tx_id}",
        json={"description": "Updated description"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


def test_delete_transaction_admin_only(
    test_client: TestClient, editor_user: User, test_admin: User
):
    editor_headers = auth_headers(editor_user)
    create_resp = _create_tx(test_client, editor_headers)
    assert create_resp.status_code == 201
    tx_id = create_resp.json()["id"]

    # Non-admin should be forbidden
    response = test_client.delete(f"/api/v1/transactions/{tx_id}", headers=editor_headers)
    assert response.status_code == 403

    # Admin should succeed
    admin_headers = auth_headers(test_admin)
    response = test_client.delete(f"/api/v1/transactions/{tx_id}", headers=admin_headers)
    assert response.status_code == 204
