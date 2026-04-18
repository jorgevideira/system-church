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


def test_get_users_returns_newest_first(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)

    first_payload = {
        "email": "order-test-user-1@test.com",
        "full_name": "Order Test User 1",
        "role": "viewer",
        "password": "orderpass123",
    }
    second_payload = {
        "email": "order-test-user-2@test.com",
        "full_name": "Order Test User 2",
        "role": "viewer",
        "password": "orderpass123",
    }

    first = test_client.post("/api/v1/users/", json=first_payload, headers=headers)
    second = test_client.post("/api/v1/users/", json=second_payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 201

    response = test_client.get("/api/v1/users/?q=order-test-user&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert [item["email"] for item in data][:2] == ["order-test-user-2@test.com", "order-test-user-1@test.com"]


def test_get_users_filters_by_search_status_and_role(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)

    role_response = test_client.post(
        "/api/v1/roles/roles",
        json={
            "name": "TestFiltroUsuarios",
            "description": "Role para filtro de usuários",
            "is_admin": False,
            "active": True,
            "permission_ids": [],
        },
        headers=headers,
    )
    assert role_response.status_code == 201
    role_id = role_response.json()["id"]

    active_response = test_client.post(
        "/api/v1/users/",
        json={
            "email": "status-filter-user-active@test.com",
            "full_name": "Status Filter User Active",
            "role_id": role_id,
            "password": "statuspass123",
        },
        headers=headers,
    )
    inactive_response = test_client.post(
        "/api/v1/users/",
        json={
            "email": "status-filter-user-inactive@test.com",
            "full_name": "Status Filter User Inactive",
            "role_id": role_id,
            "password": "statuspass123",
        },
        headers=headers,
    )
    assert active_response.status_code == 201
    assert inactive_response.status_code == 201

    inactive_id = inactive_response.json()["id"]
    deactivate = test_client.put(
        f"/api/v1/users/{inactive_id}",
        json={"is_active": False},
        headers=headers,
    )
    assert deactivate.status_code == 200

    search_response = test_client.get(
        "/api/v1/users/?q=status-filter-user-inactive&limit=10",
        headers=headers,
    )
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert len(search_data) == 1
    assert search_data[0]["email"] == "status-filter-user-inactive@test.com"

    status_response = test_client.get(
        "/api/v1/users/?q=status-filter-user&is_active=false&limit=10",
        headers=headers,
    )
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert len(status_data) == 1
    assert status_data[0]["email"] == "status-filter-user-inactive@test.com"
    assert status_data[0]["is_active"] is False

    role_response = test_client.get(
        f"/api/v1/users/?q=status-filter-user&role_id={role_id}&limit=10",
        headers=headers,
    )
    assert role_response.status_code == 200
    role_data = role_response.json()
    assert len(role_data) == 2
    assert {item["email"] for item in role_data} == {
        "status-filter-user-active@test.com",
        "status-filter-user-inactive@test.com",
    }


def test_update_user(test_client: TestClient, test_admin: User, test_user: User):
    headers = auth_headers(test_admin)
    response = test_client.put(
        f"/api/v1/users/{test_user.id}",
        json={"full_name": "Updated Name"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
