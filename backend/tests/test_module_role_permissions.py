from datetime import datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.db.models.role import Role
from app.db.models.user import User
from app.services import role_templates_service
from tests.conftest import auth_headers, ensure_membership, get_or_create_test_tenant


def _create_user_with_role_name(test_db, *, role_name: str) -> User:
    tenant = get_or_create_test_tenant(test_db)
    role_templates_service.install_default_roles_for_tenant(test_db, tenant.id)
    role = (
        test_db.query(Role)
        .filter(Role.tenant_id == tenant.id, Role.name == role_name)
        .first()
    )
    assert role is not None

    email = f"{role_name.lower()}-{uuid4().hex[:8]}@test.com"
    user = User(
        email=email,
        full_name=role_name,
        role="viewer",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        active_tenant_id=tenant.id,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    membership = ensure_membership(test_db, user, tenant, role="viewer", is_default=True)
    membership.role_id = role.id
    test_db.commit()
    test_db.refresh(user)
    return user


def _create_user_with_role_names(test_db, *, role_names: list[str]) -> User:
    tenant = get_or_create_test_tenant(test_db)
    role_templates_service.install_default_roles_for_tenant(test_db, tenant.id)
    roles = (
        test_db.query(Role)
        .filter(Role.tenant_id == tenant.id, Role.name.in_(role_names))
        .all()
    )
    by_name = {role.name: role for role in roles}
    assert set(role_names).issubset(by_name)

    email = f"multi-role-{uuid4().hex[:8]}@test.com"
    user = User(
        email=email,
        full_name="Multi Role",
        role=role_names[0].lower(),
        role_id=by_name[role_names[0]].id,
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        active_tenant_id=tenant.id,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    membership = ensure_membership(test_db, user, tenant, role=role_names[0].lower(), is_default=True)
    membership.role_id = by_name[role_names[0]].id
    membership.roles = [by_name[name] for name in role_names]
    test_db.commit()
    test_db.refresh(user)
    return user


def test_finance_read_role_can_read_but_not_write_categories(test_client: TestClient, test_db):
    user = _create_user_with_role_name(test_db, role_name="Finance_Read")
    headers = auth_headers(user)

    list_response = test_client.get("/api/v1/categories/", headers=headers)
    assert list_response.status_code == 200

    create_response = test_client.post(
        "/api/v1/categories/",
        json={"name": f"Categoria {uuid4().hex[:6]}", "description": "Teste", "type": "expense"},
        headers=headers,
    )
    assert create_response.status_code == 403


def test_finance_write_role_can_create_category(test_client: TestClient, test_db):
    user = _create_user_with_role_name(test_db, role_name="Finance_Write")
    headers = auth_headers(user)

    response = test_client.post(
        "/api/v1/categories/",
        json={"name": f"Categoria {uuid4().hex[:6]}", "description": "Teste", "type": "expense"},
        headers=headers,
    )
    assert response.status_code == 201


def test_school_read_role_can_read_but_not_write_courses(test_client: TestClient, test_db):
    user = _create_user_with_role_name(test_db, role_name="School_Read")
    headers = auth_headers(user)

    list_response = test_client.get("/api/v1/bible-school/courses", headers=headers)
    assert list_response.status_code == 200

    create_response = test_client.post(
        "/api/v1/bible-school/courses",
        json={"name": f"Curso {uuid4().hex[:6]}", "description": "Leitura", "active": True},
        headers=headers,
    )
    assert create_response.status_code == 403


def test_events_read_role_can_read_but_not_create_events(test_client: TestClient, test_db):
    user = _create_user_with_role_name(test_db, role_name="Events_Read")
    headers = auth_headers(user)

    list_response = test_client.get("/api/v1/events", headers=headers)
    assert list_response.status_code == 200

    now = datetime.utcnow()
    create_response = test_client.post(
        "/api/v1/events",
        json={
            "title": f"Evento {uuid4().hex[:6]}",
            "summary": "Teste",
            "visibility": "public",
            "status": "draft",
            "start_at": now.isoformat(),
            "end_at": (now + timedelta(hours=2)).isoformat(),
            "max_registrations_per_order": 1,
            "price_per_registration": "0.00",
            "currency": "BRL",
            "allow_public_registration": True,
            "require_payment": False,
            "is_active": True,
        },
        headers=headers,
    )
    assert create_response.status_code == 403


def test_users_read_role_can_list_but_not_create_users(test_client: TestClient, test_db):
    user = _create_user_with_role_name(test_db, role_name="Users_Read")
    headers = auth_headers(user)

    list_response = test_client.get("/api/v1/users/", headers=headers)
    assert list_response.status_code == 200

    create_response = test_client.post(
        "/api/v1/users/",
        json={
            "email": f"user-{uuid4().hex[:6]}@test.com",
            "full_name": "Novo Usuario",
            "password": "newpass123",
        },
        headers=headers,
    )
    assert create_response.status_code == 403


def test_user_with_multiple_roles_gets_combined_module_access(test_client: TestClient, test_db):
    user = _create_user_with_role_names(test_db, role_names=["Leader", "School_Read"])
    headers = auth_headers(user)

    cells_response = test_client.get("/api/v1/cells/", headers=headers)
    assert cells_response.status_code == 200

    school_response = test_client.get("/api/v1/bible-school/courses", headers=headers)
    assert school_response.status_code == 200

    create_school_response = test_client.post(
        "/api/v1/bible-school/courses",
        json={"name": f"Curso {uuid4().hex[:6]}", "description": "Leitura", "active": True},
        headers=headers,
    )
    assert create_school_response.status_code == 403


def test_super_admin_role_can_access_users_write(test_client: TestClient, test_db):
    user = _create_user_with_role_name(test_db, role_name="Super_Admin")
    headers = auth_headers(user)

    response = test_client.post(
        "/api/v1/users/",
        json={
            "email": f"super-created-{uuid4().hex[:6]}@test.com",
            "full_name": "Criado por Super",
            "password": "newpass123",
        },
        headers=headers,
    )
    assert response.status_code == 201


def test_discipler_role_can_delete_people_from_supervised_cell(test_client: TestClient, test_db, test_admin: User):
    admin_headers = auth_headers(test_admin)
    discipler_user = _create_user_with_role_name(test_db, role_name="Discipler")
    discipler_headers = auth_headers(discipler_user)

    cell_response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": f"Celula Discipler {uuid4().hex[:6]}",
            "weekday": "wednesday",
            "meeting_time": "19:30:00",
            "address": "Rua Rede, 100",
            "status": "active",
        },
        headers=admin_headers,
    )
    assert cell_response.status_code == 201
    cell_id = cell_response.json()["id"]

    discipler_member = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Discipulador Vinculado", "contact": "11999990000", "status": "active", "user_id": discipler_user.id},
        headers=admin_headers,
    )
    assert discipler_member.status_code == 201
    discipler_member_id = discipler_member.json()["id"]

    assign_discipler_member = test_client.post(
        f"/api/v1/cells/{cell_id}/members/{discipler_member_id}",
        json={},
        headers=admin_headers,
    )
    assert assign_discipler_member.status_code == 201

    assign_discipler_role = test_client.post(
        f"/api/v1/cells/{cell_id}/leaders",
        json={"member_id": discipler_member_id, "role": "co_leader", "is_primary": False},
        headers=admin_headers,
    )
    assert assign_discipler_role.status_code == 201

    person_response = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Pessoa da Celula", "contact": "11911112222", "status": "active", "stage": "assiduo"},
        headers=admin_headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    assign_person = test_client.post(
        f"/api/v1/cells/{cell_id}/members/{person_id}",
        json={},
        headers=admin_headers,
    )
    assert assign_person.status_code == 201

    delete_response = test_client.delete(
        f"/api/v1/cells/{cell_id}/members/{person_id}",
        headers=discipler_headers,
    )
    assert delete_response.status_code == 204


def test_network_pastor_role_can_delete_people_from_supervised_cell(test_client: TestClient, test_db, test_admin: User):
    admin_headers = auth_headers(test_admin)
    network_pastor_user = _create_user_with_role_name(test_db, role_name="Network_Pastor")
    network_pastor_headers = auth_headers(network_pastor_user)

    cell_response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": f"Celula Pastor {uuid4().hex[:6]}",
            "weekday": "thursday",
            "meeting_time": "20:00:00",
            "address": "Rua Rede, 200",
            "status": "active",
        },
        headers=admin_headers,
    )
    assert cell_response.status_code == 201
    cell_id = cell_response.json()["id"]

    network_pastor_member = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Pastor Vinculado", "contact": "11988887777", "status": "active", "user_id": network_pastor_user.id},
        headers=admin_headers,
    )
    assert network_pastor_member.status_code == 201
    network_pastor_member_id = network_pastor_member.json()["id"]

    discipler_member = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Discipulador da Rede", "contact": "11977776666", "status": "active"},
        headers=admin_headers,
    )
    assert discipler_member.status_code == 201
    discipler_member_id = discipler_member.json()["id"]

    assign_network_member = test_client.post(
        f"/api/v1/cells/{cell_id}/members/{network_pastor_member_id}",
        json={},
        headers=admin_headers,
    )
    assert assign_network_member.status_code == 201

    assign_discipler_member = test_client.post(
        f"/api/v1/cells/{cell_id}/members/{discipler_member_id}",
        json={},
        headers=admin_headers,
    )
    assert assign_discipler_member.status_code == 201

    assign_network_role = test_client.post(
        f"/api/v1/cells/{cell_id}/leaders",
        json={
            "member_id": discipler_member_id,
            "discipler_member_id": network_pastor_member_id,
            "role": "co_leader",
            "is_primary": False,
        },
        headers=admin_headers,
    )
    assert assign_network_role.status_code == 201

    person_response = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Visitante da Rede", "contact": "11933334444", "status": "active", "stage": "visitor"},
        headers=admin_headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    assign_person = test_client.post(
        f"/api/v1/cells/{cell_id}/members/{person_id}",
        json={},
        headers=admin_headers,
    )
    assert assign_person.status_code == 201

    delete_response = test_client.delete(
        f"/api/v1/cells/{cell_id}/members/{person_id}",
        headers=network_pastor_headers,
    )
    assert delete_response.status_code == 204


def test_super_admin_role_can_delete_people_from_cell(test_client: TestClient, test_db, test_admin: User):
    admin_headers = auth_headers(test_admin)
    super_admin = _create_user_with_role_name(test_db, role_name="Super_Admin")
    super_admin_headers = auth_headers(super_admin)

    cell_response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": f"Celula Super {uuid4().hex[:6]}",
            "weekday": "friday",
            "meeting_time": "19:00:00",
            "address": "Rua Admin, 300",
            "status": "active",
        },
        headers=admin_headers,
    )
    assert cell_response.status_code == 201
    cell_id = cell_response.json()["id"]

    person_response = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Pessoa Super", "contact": "11955556666", "status": "active", "stage": "member"},
        headers=admin_headers,
    )
    assert person_response.status_code == 201
    person_id = person_response.json()["id"]

    assign_person = test_client.post(
        f"/api/v1/cells/{cell_id}/members/{person_id}",
        json={},
        headers=admin_headers,
    )
    assert assign_person.status_code == 201

    delete_response = test_client.delete(
        f"/api/v1/cells/{cell_id}/members/{person_id}",
        headers=super_admin_headers,
    )
    assert delete_response.status_code == 204


def test_discipler_role_lists_only_lost_sheep_from_supervised_cells(test_client: TestClient, test_db, test_admin: User):
    admin_headers = auth_headers(test_admin)
    discipler_user = _create_user_with_role_name(test_db, role_name="Discipler")
    discipler_headers = auth_headers(discipler_user)

    supervised_cell_response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": f"Celula Supervisionada {uuid4().hex[:6]}",
            "weekday": "monday",
            "meeting_time": "19:00:00",
            "address": "Rua Escopo, 10",
            "status": "active",
        },
        headers=admin_headers,
    )
    assert supervised_cell_response.status_code == 201
    supervised_cell_id = supervised_cell_response.json()["id"]

    other_cell_response = test_client.post(
        "/api/v1/cells/",
        json={
            "name": f"Celula Fora {uuid4().hex[:6]}",
            "weekday": "tuesday",
            "meeting_time": "19:00:00",
            "address": "Rua Escopo, 20",
            "status": "active",
        },
        headers=admin_headers,
    )
    assert other_cell_response.status_code == 201
    other_cell_id = other_cell_response.json()["id"]

    discipler_member_response = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Discipulador Escopo", "contact": "11900001111", "status": "active", "user_id": discipler_user.id},
        headers=admin_headers,
    )
    assert discipler_member_response.status_code == 201
    discipler_member_id = discipler_member_response.json()["id"]

    assign_discipler_member = test_client.post(
        f"/api/v1/cells/{supervised_cell_id}/members/{discipler_member_id}",
        json={},
        headers=admin_headers,
    )
    assert assign_discipler_member.status_code == 201

    assign_discipler_role = test_client.post(
        f"/api/v1/cells/{supervised_cell_id}/leaders",
        json={"member_id": discipler_member_id, "role": "co_leader", "is_primary": False},
        headers=admin_headers,
    )
    assert assign_discipler_role.status_code == 201

    supervised_person = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Pessoa da Minha Rede", "contact": "11910000001", "status": "active", "stage": "member"},
        headers=admin_headers,
    ).json()
    other_person = test_client.post(
        "/api/v1/cells/members/all",
        json={"full_name": "Pessoa de Outra Rede", "contact": "11910000002", "status": "active", "stage": "member"},
        headers=admin_headers,
    ).json()

    assign_supervised_person = test_client.post(
        f"/api/v1/cells/{supervised_cell_id}/members/{supervised_person['id']}",
        json={},
        headers=admin_headers,
    )
    assert assign_supervised_person.status_code == 201

    assign_other_person = test_client.post(
        f"/api/v1/cells/{other_cell_id}/members/{other_person['id']}",
        json={},
        headers=admin_headers,
    )
    assert assign_other_person.status_code == 201

    mark_supervised_lost = test_client.post(
        "/api/v1/lost-sheep",
        json={"member_id": supervised_person["id"], "cell_id": supervised_cell_id, "phone_number": "11910000001"},
        headers=admin_headers,
    )
    assert mark_supervised_lost.status_code == 200

    mark_other_lost = test_client.post(
        "/api/v1/lost-sheep",
        json={"member_id": other_person["id"], "cell_id": other_cell_id, "phone_number": "11910000002"},
        headers=admin_headers,
    )
    assert mark_other_lost.status_code == 200

    lost_sheep_response = test_client.get("/api/v1/lost-sheep", headers=discipler_headers)
    assert lost_sheep_response.status_code == 200
    payload = lost_sheep_response.json()
    assert [item["member_name"] for item in payload] == ["Pessoa da Minha Rede"]
