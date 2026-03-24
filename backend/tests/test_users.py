"""User endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from app.db.models.user import User
from tests.conftest import auth_headers


def test_create_user_admin(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)
    response = test_client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@test.com",
            "full_name": "New User",
            "role": "viewer",
            "password": "newpass123",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"


def test_create_user_forbidden(test_client: TestClient, test_user: User):
    headers = auth_headers(test_user)
    response = test_client.post(
        "/api/v1/users/",
        json={
            "email": "another@test.com",
            "full_name": "Another",
            "role": "viewer",
            "password": "somepass123",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_get_users(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)
    response = test_client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_user(test_client: TestClient, test_admin: User, test_user: User):
    headers = auth_headers(test_admin)
    response = test_client.put(
        f"/api/v1/users/{test_user.id}",
        json={"full_name": "Updated Name"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
