"""Tests for startup bootstrap tenant membership behavior."""

from app.core.security import get_password_hash
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.initial_setup import ensure_default_tenant_memberships


def _create_tenant(test_db, *, name: str, slug: str) -> Tenant:
    existing = test_db.query(Tenant).filter(Tenant.slug == slug).first()
    if existing is not None:
        return existing
    tenant = Tenant(name=name, slug=slug, is_active=True)
    test_db.add(tenant)
    test_db.commit()
    test_db.refresh(tenant)
    return tenant


def _create_user(test_db, *, email: str, active_tenant_id: int | None = None) -> User:
    user = User(
        email=email,
        full_name=email.split("@")[0],
        role="viewer",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        active_tenant_id=active_tenant_id,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


def test_ensure_default_tenant_memberships_does_not_duplicate_existing_membership(test_db):
    default_tenant = _create_tenant(test_db, name="Default Church", slug="default")
    target_tenant = _create_tenant(test_db, name="Videira", slug="videira-sertaozinho")
    user = _create_user(test_db, email="tenant-only@test.com", active_tenant_id=target_tenant.id)

    membership = TenantMembership(
        user_id=user.id,
        tenant_id=target_tenant.id,
        role="super admin",
        is_active=True,
        is_default=True,
    )
    test_db.add(membership)
    test_db.commit()

    ensure_default_tenant_memberships(test_db, default_tenant)

    memberships = (
        test_db.query(TenantMembership)
        .filter(TenantMembership.user_id == user.id)
        .order_by(TenantMembership.tenant_id.asc())
        .all()
    )
    assert len(memberships) == 1
    assert memberships[0].tenant_id == target_tenant.id
    assert memberships[0].is_default is True


def test_ensure_default_tenant_memberships_adds_default_when_user_has_no_membership(test_db):
    default_tenant = _create_tenant(test_db, name="Default Church", slug="default")
    user = _create_user(test_db, email="no-membership@test.com", active_tenant_id=None)

    ensure_default_tenant_memberships(test_db, default_tenant)

    memberships = test_db.query(TenantMembership).filter(TenantMembership.user_id == user.id).all()
    assert len(memberships) == 1
    assert memberships[0].tenant_id == default_tenant.id
    assert memberships[0].is_default is True


def test_ensure_default_tenant_memberships_keeps_single_default_prefer_active_tenant(test_db):
    default_tenant = _create_tenant(test_db, name="Default Church", slug="default")
    second_tenant = _create_tenant(test_db, name="Videira", slug="videira-sertaozinho")
    user = _create_user(test_db, email="multi-default@test.com", active_tenant_id=second_tenant.id)

    test_db.add(
        TenantMembership(
            user_id=user.id,
            tenant_id=default_tenant.id,
            role="viewer",
            is_active=True,
            is_default=True,
        )
    )
    test_db.add(
        TenantMembership(
            user_id=user.id,
            tenant_id=second_tenant.id,
            role="super admin",
            is_active=True,
            is_default=True,
        )
    )
    test_db.commit()

    ensure_default_tenant_memberships(test_db, default_tenant)

    memberships = (
        test_db.query(TenantMembership)
        .filter(TenantMembership.user_id == user.id)
        .order_by(TenantMembership.tenant_id.asc())
        .all()
    )
    defaults = [membership for membership in memberships if membership.is_default]
    assert len(defaults) == 1
    assert defaults[0].tenant_id == second_tenant.id
