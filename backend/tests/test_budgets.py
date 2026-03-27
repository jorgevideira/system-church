"""Budget endpoint tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.models.category import Category
from app.db.models.ministry import Ministry
from app.db.models.user import User
from tests.conftest import auth_headers


@pytest.fixture
def editor_user(test_db: Session) -> User:
    email = "budget-editor@test.com"
    existing = test_db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    user = User(
        email=email,
        full_name="Budget Editor",
        role="editor",
        hashed_password=get_password_hash("editorpass123"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def other_editor_user(test_db: Session) -> User:
    email = "budget-editor-2@test.com"
    existing = test_db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    user = User(
        email=email,
        full_name="Budget Editor 2",
        role="editor",
        hashed_password=get_password_hash("editorpass123"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def expense_category(test_db: Session) -> Category:
    name = f"BudgetCat-{uuid.uuid4().hex[:8]}"
    category = Category(
        name=name,
        description="Category for budget tests",
        type="expense",
        is_active=True,
        is_system=False,
    )
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)
    return category


@pytest.fixture
def ministry(test_db: Session) -> Ministry:
    name = f"BudgetMin-{uuid.uuid4().hex[:8]}"
    ministry = Ministry(
        name=name,
        description="Ministry for budget tests",
        is_active=True,
    )
    test_db.add(ministry)
    test_db.commit()
    test_db.refresh(ministry)
    return ministry


def _create_expense(
    test_client: TestClient,
    headers: dict,
    amount: str,
    transaction_date: str,
    category_id: int | None = None,
    ministry_id: int | None = None,
):
    payload = {
        "description": f"Budget expense {uuid.uuid4().hex[:6]}",
        "amount": amount,
        "transaction_type": "expense",
        "transaction_date": transaction_date,
        "category_id": category_id,
        "ministry_id": ministry_id,
    }
    return test_client.post("/api/v1/transactions/", json=payload, headers=headers)


def test_create_and_list_budgets(
    test_client: TestClient,
    editor_user: User,
    expense_category: Category,
):
    headers = auth_headers(editor_user)
    create_resp = test_client.post(
        "/api/v1/budgets/",
        json={
            "month": "2026-03",
            "budget_type": "category",
            "reference_id": expense_category.id,
            "target_amount": "1000.00",
            "alert_threshold_percent": 80,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    budget = create_resp.json()
    assert budget["month"] == "2026-03"
    assert budget["budget_type"] == "category"

    list_resp = test_client.get("/api/v1/budgets/?month=2026-03", headers=headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert any(item["id"] == budget["id"] for item in data)


def test_budget_health_warning_and_simulation(
    test_client: TestClient,
    editor_user: User,
    expense_category: Category,
):
    headers = auth_headers(editor_user)
    create_resp = test_client.post(
        "/api/v1/budgets/",
        json={
            "month": "2026-03",
            "budget_type": "category",
            "reference_id": expense_category.id,
            "target_amount": "1000.00",
            "alert_threshold_percent": 80,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    budget_id = create_resp.json()["id"]

    tx_resp = _create_expense(
        test_client,
        headers,
        amount="850.00",
        transaction_date="2026-03-10",
        category_id=expense_category.id,
    )
    assert tx_resp.status_code == 201

    health_resp = test_client.get("/api/v1/budgets/2026-03/health", headers=headers)
    assert health_resp.status_code == 200
    health_items = health_resp.json()
    current = next(item for item in health_items if item["budget_id"] == budget_id)
    assert current["alert_level"] == "warning"
    assert round(float(current["percent_spent"]), 2) == 85.0

    sim_resp = test_client.post(
        f"/api/v1/budgets/{budget_id}/simulate",
        json={"projected_expense": "200.00"},
        headers=headers,
    )
    assert sim_resp.status_code == 200
    sim = sim_resp.json()
    assert sim["will_trigger_alert"] is True
    assert sim["will_exceed"] is True
    assert round(float(sim["new_percent"]), 2) == 105.0


def test_budget_monthly_adherence(
    test_client: TestClient,
    editor_user: User,
    expense_category: Category,
    ministry: Ministry,
):
    headers = auth_headers(editor_user)

    b1 = test_client.post(
        "/api/v1/budgets/",
        json={
            "month": "2026-04",
            "budget_type": "category",
            "reference_id": expense_category.id,
            "target_amount": "1000.00",
            "alert_threshold_percent": 80,
        },
        headers=headers,
    )
    assert b1.status_code == 201

    b2 = test_client.post(
        "/api/v1/budgets/",
        json={
            "month": "2026-04",
            "budget_type": "ministry",
            "reference_id": ministry.id,
            "target_amount": "500.00",
            "alert_threshold_percent": 80,
        },
        headers=headers,
    )
    assert b2.status_code == 201

    tx_cat = _create_expense(
        test_client,
        headers,
        amount="200.00",
        transaction_date="2026-04-03",
        category_id=expense_category.id,
    )
    assert tx_cat.status_code == 201

    tx_min = _create_expense(
        test_client,
        headers,
        amount="550.00",
        transaction_date="2026-04-08",
        ministry_id=ministry.id,
    )
    assert tx_min.status_code == 201

    adherence_resp = test_client.get("/api/v1/budgets/2026-04/adherence", headers=headers)
    assert adherence_resp.status_code == 200
    adherence = adherence_resp.json()
    assert adherence["total_budgets"] == 2
    assert adherence["healthy_count"] == 1
    assert adherence["critical_count"] == 1
    assert round(float(adherence["total_spent"]), 2) == 750.0


def test_budget_user_isolation(
    test_client: TestClient,
    editor_user: User,
    other_editor_user: User,
    expense_category: Category,
):
    editor_headers = auth_headers(editor_user)
    other_headers = auth_headers(other_editor_user)

    create_resp = test_client.post(
        "/api/v1/budgets/",
        json={
            "month": "2026-05",
            "budget_type": "category",
            "reference_id": expense_category.id,
            "target_amount": "999.00",
            "alert_threshold_percent": 80,
        },
        headers=editor_headers,
    )
    assert create_resp.status_code == 201
    budget_id = create_resp.json()["id"]

    forbidden_read = test_client.get(f"/api/v1/budgets/{budget_id}", headers=other_headers)
    assert forbidden_read.status_code == 404

    forbidden_delete = test_client.delete(f"/api/v1/budgets/{budget_id}", headers=other_headers)
    assert forbidden_delete.status_code == 404
