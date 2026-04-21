from app.db.models.role import Permission, Role
from app.schemas.tenant import TenantCreate
from app.services import role_templates_service, tenant_service
from tests.conftest import get_or_create_test_tenant


def test_install_default_roles_for_tenant_creates_standard_and_cells_roles(test_db):
    tenant = get_or_create_test_tenant(test_db)

    installed = role_templates_service.install_default_roles_for_tenant(test_db, tenant.id)

    assert "finance_read" in installed
    assert "super_admin" in installed
    assert "finance_write" in installed
    assert "kids_read" in installed
    assert "kids_write" in installed
    assert "school_read" in installed
    assert "school_write" in installed
    assert "events_read" in installed
    assert "events_write" in installed
    assert "users_read" in installed
    assert "users_write" in installed
    assert "leader" in installed
    assert "discipler" in installed
    assert "network_pastor" in installed

    finance_read = (
        test_db.query(Role)
        .filter(Role.tenant_id == tenant.id, Role.name == "Finance_Read")
        .first()
    )
    assert finance_read is not None
    assert {permission.name for permission in finance_read.permissions} == {
        "finance_dashboard_view",
        "finance_transactions_view",
        "finance_categories_view",
        "finance_ministries_view",
        "finance_payables_view",
        "finance_receivables_view",
        "finance_reports_view",
    }

    finance_write = (
        test_db.query(Role)
        .filter(Role.tenant_id == tenant.id, Role.name == "Finance_Write")
        .first()
    )
    assert finance_write is not None
    finance_write_permissions = {permission.name for permission in finance_write.permissions}
    assert "finance_transactions_create" in finance_write_permissions
    assert "finance_upload_manage" in finance_write_permissions
    assert "finance_reports_view" in finance_write_permissions

    leader = (
        test_db.query(Role)
        .filter(Role.tenant_id == tenant.id, Role.name == "Leader")
        .first()
    )
    assert leader is not None
    leader_permissions = {permission.name for permission in leader.permissions}
    assert "cells_people_add_member" in leader_permissions
    assert "cells_attendance_manage" in leader_permissions
    assert "cells_lost_sheep_manage" in leader_permissions

    kids_manage = test_db.query(Permission).filter(Permission.name == "cells_kids_manage").first()
    assert kids_manage is not None
    assert kids_manage.active is True

    super_admin = (
        test_db.query(Role)
        .filter(Role.tenant_id == tenant.id, Role.name == "Super_Admin")
        .first()
    )
    assert super_admin is not None
    assert super_admin.is_admin is True
    assert "users_system_permissions_manage" in {permission.name for permission in super_admin.permissions}


def test_install_default_roles_for_tenant_is_idempotent(test_db):
    tenant = get_or_create_test_tenant(test_db)

    first = role_templates_service.install_default_roles_for_tenant(test_db, tenant.id)
    second = role_templates_service.install_default_roles_for_tenant(test_db, tenant.id)

    assert first == second
    roles = test_db.query(Role).filter(Role.tenant_id == tenant.id).all()
    assert len([role for role in roles if role.name == "Finance_Read"]) == 1
    assert len([role for role in roles if role.name == "Super_Admin"]) == 1
    assert len([role for role in roles if role.name == "Leader"]) == 1


def test_create_tenant_installs_default_roles(test_db, test_admin):
    payload = TenantCreate(name="Tenant Roles", slug="tenant-roles")

    tenant = tenant_service.create_tenant(test_db, payload, test_admin)

    role_names = {
        role.name
        for role in test_db.query(Role).filter(Role.tenant_id == tenant.id).all()
    }
    assert "Finance_Read" in role_names
    assert "Super_Admin" in role_names
    assert "Finance_Write" in role_names
    assert "Leader" in role_names
    assert "Network_Pastor" in role_names


def test_install_default_roles_for_tenant_persists_after_session_commit(test_db):
    tenant = get_or_create_test_tenant(test_db)

    role_templates_service.install_default_roles_for_tenant(test_db, tenant.id)
    test_db.commit()
    test_db.expire_all()

    role_names = {
        role.name
        for role in test_db.query(Role).filter(Role.tenant_id == tenant.id).all()
    }
    assert "Finance_Read" in role_names
    assert "Super_Admin" in role_names
    assert "Users_Write" in role_names
    assert "Network_Pastor" in role_names
