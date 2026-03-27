from fastapi.testclient import TestClient

from app.db.models.user import User
from tests.conftest import auth_headers


def _create_cell(test_client: TestClient, headers: dict, name: str) -> dict:
    response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": name,
            "weekday": "wednesday",
            "meeting_time": "19:30:00",
            "address": "Rua Teste, 100",
            "status": "active",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def _create_member(test_client: TestClient, headers: dict, name: str) -> dict:
    response = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": name, "contact": "11999990000", "status": "active"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_create_meeting_and_attendances(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)
    cell = _create_cell(test_client, headers, "Celula Reuniao")

    member_a = _create_member(test_client, headers, "Membro A")
    member_b = _create_member(test_client, headers, "Membro B")

    assign_a = test_client.post(f"/api/v1/cells/{cell['id']}/members/{member_a['id']}", json={}, headers=headers)
    assign_b = test_client.post(f"/api/v1/cells/{cell['id']}/members/{member_b['id']}", json={}, headers=headers)
    assert assign_a.status_code == 201
    assert assign_b.status_code == 201

    meeting_resp = test_client.post(
        f"/api/v1/cells/{cell['id']}/meetings",
        json={"meeting_date": "2026-03-25", "theme": "Fe", "notes": "Reuniao de quarta"},
        headers=headers,
    )
    assert meeting_resp.status_code == 201
    meeting = meeting_resp.json()

    attendance_resp = test_client.post(
        f"/api/v1/cells/meetings/{meeting['id']}/attendances/bulk",
        json={
            "items": [
                {"member_id": member_a["id"], "attendance_status": "present"},
                {"member_id": member_b["id"], "attendance_status": "absent", "notes": "viagem"},
            ]
        },
        headers=headers,
    )
    assert attendance_resp.status_code == 200
    assert len(attendance_resp.json()) == 2

    get_attendances = test_client.get(f"/api/v1/cells/meetings/{meeting['id']}/attendances", headers=headers)
    assert get_attendances.status_code == 200
    assert len(get_attendances.json()) == 2


def test_add_visitor_and_dashboard(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)
    cell = _create_cell(test_client, headers, "Celula Dashboard")
    member = _create_member(test_client, headers, "Membro Dashboard")

    assign = test_client.post(f"/api/v1/cells/{cell['id']}/members/{member['id']}", json={}, headers=headers)
    assert assign.status_code == 201

    meeting_resp = test_client.post(
        f"/api/v1/cells/{cell['id']}/meetings",
        json={"meeting_date": "2026-03-26", "theme": "Esperanca", "notes": ""},
        headers=headers,
    )
    assert meeting_resp.status_code == 201
    meeting = meeting_resp.json()

    add_visitor = test_client.post(
        f"/api/v1/cells/meetings/{meeting['id']}/visitors",
        json={"full_name": "Visitante 1", "contact": "11988887777", "is_first_time": True},
        headers=headers,
    )
    assert add_visitor.status_code == 201

    list_visitors = test_client.get(f"/api/v1/cells/meetings/{meeting['id']}/visitors", headers=headers)
    assert list_visitors.status_code == 200
    assert len(list_visitors.json()) == 1

    summary = test_client.get("/api/v1/cells/dashboard/summary", headers=headers)
    assert summary.status_code == 200
    assert isinstance(summary.json(), list)
