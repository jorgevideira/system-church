from fastapi.testclient import TestClient

from app.db.models.user import User
from tests.conftest import auth_headers


def test_create_cell(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)
    response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": "Celula Centro",
            "weekday": "wednesday",
            "meeting_time": "19:30:00",
            "address": "Rua A, 100",
            "status": "active",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Celula Centro"


def test_assign_primary_leader(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)

    cell_resp = test_client.post(
        "/api/v1/cells/",
        json={
            "name": "Celula Sul",
            "weekday": "thursday",
            "meeting_time": "20:00:00",
            "address": "Rua B, 200",
            "status": "active",
        },
        headers=headers,
    )
    cell_id = cell_resp.json()["id"]

    member_resp = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Lider 1", "contact": "11999990000", "status": "active"},
        headers=headers,
    )
    member_id = member_resp.json()["id"]

    assign_resp = test_client.post(
        f"/api/v1/cells/{cell_id}/leaders",
        json={"member_id": member_id, "role": "leader", "is_primary": True},
        headers=headers,
    )
    assert assign_resp.status_code == 201
    assert assign_resp.json()["is_primary"] is True


def test_transfer_member_between_cells(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)

    cell_a = test_client.post(
        "/api/v1/cells/",
        json={
            "name": "Celula Norte",
            "weekday": "monday",
            "meeting_time": "19:00:00",
            "address": "Rua C, 300",
            "status": "active",
        },
        headers=headers,
    ).json()

    cell_b = test_client.post(
        "/api/v1/cells/",
        json={
            "name": "Celula Leste",
            "weekday": "tuesday",
            "meeting_time": "19:00:00",
            "address": "Rua D, 400",
            "status": "active",
        },
        headers=headers,
    ).json()

    member = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Membro 1", "contact": "11988887777", "status": "active"},
        headers=headers,
    ).json()

    assign = test_client.post(
        f"/api/v1/cells/{cell_a['id']}/members/{member['id']}",
        json={},
        headers=headers,
    )
    assert assign.status_code == 201

    transfer = test_client.post(
        f"/api/v1/cells/{cell_a['id']}/members/{member['id']}/transfer",
        json={
            "target_cell_id": cell_b["id"],
            "transfer_reason": "Mudanca de endereco",
        },
        headers=headers,
    )
    assert transfer.status_code == 200
    assert transfer.json()["cell_id"] == cell_b["id"]
