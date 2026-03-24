"""Authentication endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from app.db.models.user import User
from tests.conftest import auth_headers


def test_login_success(test_client: TestClient, test_user: User):
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(test_client: TestClient, test_user: User):
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_current_user(test_client: TestClient, test_user: User):
    headers = auth_headers(test_user)
    response = test_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email


def test_token_refresh(test_client: TestClient, test_user: User):
    # First obtain tokens
    login_resp = test_client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "testpass123"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    # Refresh
    response = test_client.post(
        "/api/v1/auth/refresh",
        params={"refresh_token_str": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
