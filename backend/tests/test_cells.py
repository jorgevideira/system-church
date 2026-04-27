from fastapi.testclient import TestClient

from app.db.models.user import User
from app.core.security import get_password_hash
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


def test_create_member_rejects_duplicate_user_link(test_client: TestClient, test_admin: User, test_leader: User):
    headers = auth_headers(test_admin)

    first_response = test_client.post(
        "/api/v1/cells/members/all",
        json={
            "full_name": "Anderson",
            "contact": "11999990001",
            "status": "active",
            "user_id": test_leader.id,
        },
        headers=headers,
    )
    assert first_response.status_code == 201

    duplicate_response = test_client.post(
        "/api/v1/cells/members/all",
        json={
            "full_name": "Emilly",
            "contact": "11999990002",
            "status": "active",
            "user_id": test_leader.id,
        },
        headers=headers,
    )
    assert duplicate_response.status_code == 400
    assert "already linked" in duplicate_response.json()["detail"]


def test_update_member_rejects_switching_to_user_already_linked(
    test_client: TestClient,
    test_db,
    test_admin: User,
    test_user: User,
):
    headers = auth_headers(test_admin)

    leader_user = User(
        email="cells-dup-leader@test.com",
        full_name="Leader Duplicate",
        role="leader",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        active_tenant_id=test_admin.active_tenant_id,
    )
    test_db.add(leader_user)
    test_db.commit()
    test_db.refresh(leader_user)

    leader_member_response = test_client.post(
        "/api/v1/cells/members/all",
        json={
            "full_name": "Emilly",
            "contact": "11999990003",
            "status": "active",
            "user_id": leader_user.id,
        },
        headers=headers,
    )
    assert leader_member_response.status_code == 201
    leader_member_id = leader_member_response.json()["id"]

    other_member_response = test_client.post(
        "/api/v1/cells/members/all",
        json={
            "full_name": "Sara",
            "contact": "11999990004",
            "status": "active",
            "user_id": test_user.id,
        },
        headers=headers,
    )
    assert other_member_response.status_code == 201
    other_member_id = other_member_response.json()["id"]

    update_response = test_client.put(
        f"/api/v1/cells/members/{other_member_id}",
        json={
            "full_name": "Emilly",
            "contact": "11999990005",
            "status": "active",
            "user_id": leader_user.id,
        },
        headers=headers,
    )
    assert update_response.status_code == 400
    assert "already linked" in update_response.json()["detail"]

    unchanged_response = test_client.get(
        "/api/v1/cells/members/all",
        params={"status": "active"},
        headers=headers,
    )
    assert unchanged_response.status_code == 200
    members = {row["id"]: row for row in unchanged_response.json()}
    assert members[leader_member_id]["full_name"] == "Emilly"
    assert members[other_member_id]["full_name"] == "Sara"


def test_deactivating_member_deactivates_active_leadership_assignment(test_client: TestClient, test_admin: User):
    headers = auth_headers(test_admin)

    cell_response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": "Celula Lideranca",
            "weekday": "wednesday",
            "meeting_time": "19:30:00",
            "address": "Rua Lider, 123",
            "status": "active",
        },
        headers=headers,
    )
    assert cell_response.status_code == 201
    cell_id = cell_response.json()["id"]

    member_response = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Anderson", "contact": "11999990006", "status": "active"},
        headers=headers,
    )
    assert member_response.status_code == 201
    member_id = member_response.json()["id"]

    link_response = test_client.post(
        f"/api/v1/cells/{cell_id}/members/{member_id}",
        json={},
        headers=headers,
    )
    assert link_response.status_code == 201

    assignment_response = test_client.post(
        f"/api/v1/cells/{cell_id}/leaders",
        json={"member_id": member_id, "role": "leader", "is_primary": True},
        headers=headers,
    )
    assert assignment_response.status_code == 201
    assignment_id = assignment_response.json()["id"]

    deactivate_response = test_client.put(
        f"/api/v1/cells/members/{member_id}",
        json={"status": "inactive"},
        headers=headers,
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    assignments_response = test_client.get(
        f"/api/v1/cells/{cell_id}/leaders",
        headers=headers,
    )
    assert assignments_response.status_code == 200
    assignment = next(row for row in assignments_response.json() if row["id"] == assignment_id)
    assert assignment["active"] is False
    assert assignment["end_date"] is not None
