from datetime import date

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
            "address": "Rua Leader, 123",
            "status": "active",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def _create_member(test_client: TestClient, headers: dict, name: str, user_id: int | None = None) -> dict:
    payload = {"full_name": name, "contact": "11999990000", "status": "active", "user_id": user_id}
    response = test_client.post(
        "/api/v1/cells/members/all",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_leader_sees_only_owned_cells_and_can_create_meeting(
    test_client: TestClient,
    test_admin: User,
    test_leader: User,
):
    admin_headers = auth_headers(test_admin)
    leader_headers = auth_headers(test_leader)

    owned_cell = _create_cell(test_client, admin_headers, "Celula Lider")
    other_cell = _create_cell(test_client, admin_headers, "Celula Outra")

    leader_member = _create_member(test_client, admin_headers, "Lider Vinculado", user_id=test_leader.id)
    test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/members/{leader_member['id']}",
        json={},
        headers=admin_headers,
    )
    assign_leader_resp = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/leaders",
        json={"member_id": leader_member["id"], "role": "leader", "is_primary": True},
        headers=admin_headers,
    )
    assert assign_leader_resp.status_code == 201

    list_resp = test_client.get("/api/v1/cells/my", headers=leader_headers)
    assert list_resp.status_code == 200
    ids = [row["id"] for row in list_resp.json()]
    assert owned_cell["id"] in ids
    assert other_cell["id"] not in ids

    meeting_resp = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/meetings",
        json={"meeting_date": str(date.today()), "theme": "Reuniao do lider", "notes": ""},
        headers=leader_headers,
    )
    assert meeting_resp.status_code == 201

    forbidden_resp = test_client.post(
        f"/api/v1/cells/{other_cell['id']}/meetings",
        json={"meeting_date": str(date.today()), "theme": "Nao pode", "notes": ""},
        headers=leader_headers,
    )
    assert forbidden_resp.status_code == 403


def test_leader_adds_and_promotes_people_in_own_cell(
    test_client: TestClient,
    test_admin: User,
    test_leader: User,
):
    admin_headers = auth_headers(test_admin)
    leader_headers = auth_headers(test_leader)

    owned_cell = _create_cell(test_client, admin_headers, "Celula Promocao")
    leader_member = _create_member(test_client, admin_headers, "Lider Promotor", user_id=test_leader.id)
    test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/members/{leader_member['id']}",
        json={},
        headers=admin_headers,
    )
    assign_leader_resp = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/leaders",
        json={"member_id": leader_member["id"], "role": "leader", "is_primary": True},
        headers=admin_headers,
    )
    assert assign_leader_resp.status_code == 201

    visitor_create = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Visitante Teste", "contact": "11911112222", "status": "active", "stage": "visitor"},
        headers=leader_headers,
    )
    assert visitor_create.status_code == 201
    visitor_id = visitor_create.json()["id"]

    assign_visitor = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/members/{visitor_id}",
        json={},
        headers=leader_headers,
    )
    assert assign_visitor.status_code == 201

    visitors_resp = test_client.get(
        f"/api/v1/cells/{owned_cell['id']}/people",
        params={"stage": "visitor"},
        headers=leader_headers,
    )
    assert visitors_resp.status_code == 200
    assert any(item["id"] == visitor_id for item in visitors_resp.json())

    promote_to_assiduo = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/members/{visitor_id}/promote",
        json={"target_stage": "assiduo"},
        headers=leader_headers,
    )
    assert promote_to_assiduo.status_code == 200
    assert promote_to_assiduo.json()["stage"] == "assiduo"

    promote_to_member = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/members/{visitor_id}/promote",
        json={"target_stage": "member"},
        headers=leader_headers,
    )
    assert promote_to_member.status_code == 200
    assert promote_to_member.json()["stage"] == "member"


def test_leader_cannot_delete_or_deactivate_people_in_own_cell(
    test_client: TestClient,
    test_admin: User,
    test_leader: User,
):
    admin_headers = auth_headers(test_admin)
    leader_headers = auth_headers(test_leader)

    owned_cell = _create_cell(test_client, admin_headers, "Celula Restrita")
    leader_member = _create_member(test_client, admin_headers, "Lider Restrito", user_id=test_leader.id)
    test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/members/{leader_member['id']}",
        json={},
        headers=admin_headers,
    )
    assign_leader_resp = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/leaders",
        json={"member_id": leader_member["id"], "role": "leader", "is_primary": True},
        headers=admin_headers,
    )
    assert assign_leader_resp.status_code == 201

    person = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Pessoa Protegida", "contact": "11922223333", "status": "active", "stage": "visitor"},
        headers=admin_headers,
    ).json()
    assign_person = test_client.post(
        f"/api/v1/cells/{owned_cell['id']}/members/{person['id']}",
        json={},
        headers=admin_headers,
    )
    assert assign_person.status_code == 201

    delete_resp = test_client.delete(
        f"/api/v1/cells/{owned_cell['id']}/members/{person['id']}",
        headers=leader_headers,
    )
    assert delete_resp.status_code == 403

    deactivate_resp = test_client.put(
        f"/api/v1/cells/members/{person['id']}",
        json={"status": "inactive"},
        headers=leader_headers,
    )
    assert deactivate_resp.status_code == 403
