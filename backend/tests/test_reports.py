"""Report endpoint tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.models.user import User
from tests.conftest import auth_headers


@pytest.fixture
def report_editor(test_db: Session) -> User:
    email = "report-editor@test.com"
    existing = test_db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    user = User(
        email=email,
        full_name="Report Editor",
        role="editor",
        hashed_password=get_password_hash("editorpass123"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def report_other_editor(test_db: Session) -> User:
    email = "report-editor-2@test.com"
    existing = test_db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    user = User(
        email=email,
        full_name="Report Other Editor",
        role="editor",
        hashed_password=get_password_hash("editorpass123"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


def _create_income(test_client: TestClient, headers: dict, amount: str, tx_date: str):
    payload = {
        "description": f"Income {uuid.uuid4().hex[:6]}",
        "amount": amount,
        "transaction_type": "income",
        "transaction_date": tx_date,
    }
    return test_client.post("/api/v1/transactions/", json=payload, headers=headers)


def _create_expense(test_client: TestClient, headers: dict, amount: str, tx_date: str):
    payload = {
        "description": f"Expense {uuid.uuid4().hex[:6]}",
        "amount": amount,
        "transaction_type": "expense",
        "transaction_date": tx_date,
    }
    return test_client.post("/api/v1/transactions/", json=payload, headers=headers)


def test_summary_report_is_user_scoped(
    test_client: TestClient,
    report_editor: User,
    report_other_editor: User,
):
    headers_a = auth_headers(report_editor)
    headers_b = auth_headers(report_other_editor)

    r1 = _create_income(test_client, headers_a, amount="1000.00", tx_date="2026-03-01")
    r2 = _create_expense(test_client, headers_a, amount="250.00", tx_date="2026-03-02")
    r3 = _create_income(test_client, headers_b, amount="9999.00", tx_date="2026-03-03")
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 201

    summary = test_client.get("/api/v1/reports/summary", headers=headers_a)
    assert summary.status_code == 200
    data = summary.json()
    assert round(float(data["total_income"]), 2) == 1000.0
    assert round(float(data["total_expenses"]), 2) == 250.0
    assert round(float(data["balance"]), 2) == 750.0


def test_monthly_report_is_user_scoped(
    test_client: TestClient,
    report_editor: User,
    report_other_editor: User,
):
    headers_a = auth_headers(report_editor)
    headers_b = auth_headers(report_other_editor)

    r1 = _create_income(test_client, headers_a, amount="300.00", tx_date="2026-02-12")
    r2 = _create_expense(test_client, headers_b, amount="700.00", tx_date="2026-02-15")
    assert r1.status_code == 201
    assert r2.status_code == 201

    monthly = test_client.get("/api/v1/reports/monthly?year=2026", headers=headers_a)
    assert monthly.status_code == 200
    rows = monthly.json()
    assert any((row["month"] == 2 and row["transaction_type"] == "income") for row in rows)
    assert not any((row["month"] == 2 and row["transaction_type"] == "expense" and float(row["total"]) == 700.0) for row in rows)


def test_cash_flow_report_structure(
    test_client: TestClient,
    report_editor: User,
):
    headers = auth_headers(report_editor)

    # Insert recent transactions so history has meaningful values.
    i1 = _create_income(test_client, headers, amount="500.00", tx_date="2026-01-10")
    e1 = _create_expense(test_client, headers, amount="200.00", tx_date="2026-02-09")
    i2 = _create_income(test_client, headers, amount="900.00", tx_date="2026-03-11")
    assert i1.status_code == 201
    assert e1.status_code == 201
    assert i2.status_code == 201

    response = test_client.get(
        "/api/v1/reports/cash-flow?months_history=6&months_forecast=2",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()

    assert body["months_history"] == 6
    assert body["months_forecast"] == 2
    assert isinstance(body["history"], list)
    assert len(body["history"]) == 6
    assert isinstance(body["forecast"], list)
    assert len(body["forecast"]) == 2
    assert "current_month" in body
    assert "average_net_last_months" in body
