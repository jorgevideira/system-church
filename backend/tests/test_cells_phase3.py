from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.db.models.user import User
from tests.conftest import auth_headers


def _create_cell(test_client: TestClient, headers: dict, name: str) -> dict:
    response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": name,
            "weekday": "thursday",
            "meeting_time": "20:00:00",
            "address": "Rua Fase 3, 10",
            "status": "active",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def _create_member(test_client: TestClient, headers: dict, name: str) -> dict:
    response = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": name, "contact": "11977776666", "status": "active"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def _create_meeting(test_client: TestClient, headers: dict, cell_id: int, meeting_date: str) -> dict:
    response = test_client.post(
        f"/api/v1/cells/{cell_id}/meetings",
        json={"meeting_date": meeting_date, "theme": "Tema", "notes": ""},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_dashboard_retention_and_history(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)
    cell_a = _create_cell(test_client, headers, "Celula A Fase3")
    cell_b = _create_cell(test_client, headers, "Celula B Fase3")

    member_1 = _create_member(test_client, headers, "Membro Retido")
    member_2 = _create_member(test_client, headers, "Membro Transferido")

    assign_1 = test_client.post(
        f"/api/v1/cells/{cell_a['id']}/members/{member_1['id']}",
        json={"start_date": str(yesterday)},
        headers=headers,
    )
    assign_2 = test_client.post(
        f"/api/v1/cells/{cell_a['id']}/members/{member_2['id']}",
        json={"start_date": str(yesterday)},
        headers=headers,
    )
    assert assign_1.status_code == 201
    assert assign_2.status_code == 201

    transfer = test_client.post(
        f"/api/v1/cells/{cell_a['id']}/members/{member_2['id']}/transfer",
        json={"target_cell_id": cell_b["id"], "transfer_date": str(date.today()), "transfer_reason": "teste"},
        headers=headers,
    )
    assert transfer.status_code == 200

    retention = test_client.get(
        f"/api/v1/cells/{cell_a['id']}/dashboard/retention",
        params={
            "start_date": str(date.today() - timedelta(days=1)),
            "end_date": str(tomorrow),
        },
        headers=headers,
    )
    assert retention.status_code == 200
    payload = retention.json()
    assert payload["active_at_start"] >= 2
    assert payload["retained_members"] >= 1

    history = test_client.get(
        f"/api/v1/cells/{cell_a['id']}/dashboard/history",
        params={"months": 3},
        headers=headers,
    )
    assert history.status_code == 200
    assert len(history.json()) == 3


def test_dashboard_recurring_visitors(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)
    cell = _create_cell(test_client, headers, "Celula Visitantes")

    meeting_1 = _create_meeting(test_client, headers, cell["id"], str(date.today() - timedelta(days=7)))
    meeting_2 = _create_meeting(test_client, headers, cell["id"], str(date.today()))

    visitor_name = "Visitante Recorrente"
    add_visitor_1 = test_client.post(
        f"/api/v1/cells/meetings/{meeting_1['id']}/visitors",
        json={"full_name": visitor_name, "contact": "11966665555", "is_first_time": True},
        headers=headers,
    )
    assert add_visitor_1.status_code == 201

    add_visitor_2 = test_client.post(
        f"/api/v1/cells/meetings/{meeting_2['id']}/visitors",
        json={"full_name": visitor_name, "contact": "11966665555", "is_first_time": False},
        headers=headers,
    )
    assert add_visitor_2.status_code == 201

    recurring = test_client.get(
        f"/api/v1/cells/{cell['id']}/dashboard/visitors-recurring",
        params={
            "start_date": str(date.today() - timedelta(days=30)),
            "end_date": str(date.today()),
        },
        headers=headers,
    )
    assert recurring.status_code == 200
    data = recurring.json()
    assert data["total_recurring_visitors"] >= 1
    assert any(item["full_name"] == visitor_name for item in data["visitors"])
