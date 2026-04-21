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
