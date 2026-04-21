from collections.abc import Iterable
from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.constants import ROLE_ADMIN, ROLE_EDITOR
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.db.session import SessionLocal
from app.db.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

FINANCE_READ_PERMISSIONS = {
    "finance_dashboard_view",
    "finance_transactions_view",
    "finance_categories_view",
    "finance_ministries_view",
    "finance_payables_view",
    "finance_receivables_view",
    "finance_reports_view",
}
FINANCE_WRITE_PERMISSIONS = {
    "finance_transactions_create",
    "finance_transactions_edit",
    "finance_transactions_delete",
    "finance_categories_create",
    "finance_categories_edit",
    "finance_categories_delete",
    "finance_ministries_create",
    "finance_ministries_edit",
    "finance_ministries_delete",
    "finance_payables_create",
    "finance_payables_edit",
    "finance_payables_delete",
    "finance_receivables_create",
    "finance_receivables_edit",
    "finance_receivables_delete",
    "finance_upload_manage",
}
SCHOOL_READ_PERMISSIONS = {
    "school_dashboard_view",
    "school_courses_view",
    "school_classes_view",
    "school_professors_view",
    "school_lessons_view",
    "school_students_view",
    "school_attendance_view",
}
SCHOOL_WRITE_PERMISSIONS = {
    "school_courses_create",
    "school_courses_edit",
    "school_courses_delete",
    "school_classes_create",
    "school_classes_edit",
    "school_classes_delete",
    "school_professors_create",
    "school_professors_edit",
    "school_professors_delete",
    "school_lessons_create",
    "school_lessons_edit",
    "school_lessons_delete",
    "school_students_create",
    "school_students_edit",
    "school_students_delete",
    "school_attendance_manage",
}
EVENTS_READ_PERMISSIONS = {
    "events_events_view",
    "events_registrations_view",
    "events_payments_view",
    "events_analytics_view",
    "events_notifications_view",
}
EVENTS_WRITE_PERMISSIONS = {
    "events_events_create",
    "events_events_edit",
    "events_events_delete",
    "events_payments_manage",
}
USERS_READ_PERMISSIONS = {
    "users_users_view",
    "users_roles_view",
    "users_permissions_view",
}
USERS_WRITE_PERMISSIONS = {
    "users_users_create",
    "users_users_edit",
    "users_users_delete",
    "users_roles_create",
    "users_roles_edit",
    "users_roles_delete",
    "users_permissions_create",
    "users_permissions_edit",
    "users_permissions_delete",
    "users_system_permissions_manage",
}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    return payload


def get_current_user(
    payload: Annotated[dict, Depends(get_token_payload)],
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def get_current_tenant(
    payload: Annotated[dict, Depends(get_token_payload)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
) -> Tenant:
    tenant_id = payload.get("tenant_id") or current_user.active_tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active tenant selected")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active.is_(True)).first()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active tenant not found")
    return tenant


def get_current_membership(
    current_user: Annotated[User, Depends(get_current_active_user)],
    current_tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: Session = Depends(get_db),
) -> TenantMembership:
    membership = (
        db.query(TenantMembership)
        .filter(
            TenantMembership.user_id == current_user.id,
            TenantMembership.tenant_id == current_tenant.id,
            TenantMembership.is_active.is_(True),
        )
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no active membership in this tenant")
    return membership


def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
    current_membership: Annotated[TenantMembership, Depends(get_current_membership)],
) -> User:
    has_admin_role_name = current_user.role == ROLE_ADMIN
    has_admin_role_obj = bool(current_user.role_obj and current_user.role_obj.is_admin)
    has_membership_admin_role_name = current_membership.role == ROLE_ADMIN
    has_membership_admin_role_obj = bool(current_membership.role_obj and current_membership.role_obj.is_admin)
    has_assigned_admin_role = any(role and role.is_admin for role in getattr(current_membership, "roles", []) or [])
    if not (
        has_admin_role_name
        or has_admin_role_obj
        or has_membership_admin_role_name
        or has_membership_admin_role_obj
        or has_assigned_admin_role
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_editor(
    current_user: Annotated[User, Depends(get_current_active_user)],
    current_membership: Annotated[TenantMembership, Depends(get_current_membership)],
) -> User:
    membership_role = current_membership.role
    membership_is_admin = bool(current_membership.role_obj and current_membership.role_obj.is_admin)
    if current_user.role not in (ROLE_ADMIN, ROLE_EDITOR) and membership_role not in (ROLE_ADMIN, ROLE_EDITOR) and not membership_is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor or Admin access required",
        )
    return current_user


def get_active_permission_names(
    current_user: Annotated[User, Depends(get_current_active_user)],
    current_membership: Annotated[TenantMembership, Depends(get_current_membership)],
) -> set[str]:
    names: set[str] = set()

    for role_obj in (current_user.role_obj, current_membership.role_obj):
        permissions = getattr(role_obj, "permissions", None)
        if not permissions:
            continue
        names.update(
            permission.name
            for permission in permissions
            if permission and permission.active and permission.name
        )

    for role_obj in getattr(current_membership, "roles", []) or []:
        permissions = getattr(role_obj, "permissions", None)
        if not permissions:
            continue
        names.update(
            permission.name
            for permission in permissions
            if permission and permission.active and permission.name
        )

    return names


def _is_membership_admin(current_user: User, current_membership: TenantMembership) -> bool:
    return (
        current_user.role == ROLE_ADMIN
        or current_membership.role == ROLE_ADMIN
        or bool(current_user.role_obj and current_user.role_obj.is_admin)
        or bool(current_membership.role_obj and current_membership.role_obj.is_admin)
        or any(role and role.is_admin for role in getattr(current_membership, "roles", []) or [])
    )


def _is_membership_editor(current_user: User, current_membership: TenantMembership) -> bool:
    return (
        current_user.role in (ROLE_ADMIN, ROLE_EDITOR)
        or current_membership.role in (ROLE_ADMIN, ROLE_EDITOR)
        or bool(current_membership.role_obj and current_membership.role_obj.is_admin)
        or any(
            role and (role.is_admin or role.name.lower() in (ROLE_ADMIN, ROLE_EDITOR))
            for role in getattr(current_membership, "roles", []) or []
        )
    )


def require_permissions(
    permission_names: Iterable[str],
    *,
    allow_admin: bool = True,
    allow_editor: bool = False,
    detail: str = "Access denied",
):
    required_names = {name for name in permission_names if name}

    def dependency(
        current_user: Annotated[User, Depends(get_current_active_user)],
        current_membership: Annotated[TenantMembership, Depends(get_current_membership)],
        active_permission_names: Annotated[set[str], Depends(get_active_permission_names)],
    ) -> User:
        if allow_admin and _is_membership_admin(current_user, current_membership):
            return current_user
        if allow_editor and _is_membership_editor(current_user, current_membership):
            return current_user
        if active_permission_names & required_names:
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    return dependency


require_finance_read = require_permissions(FINANCE_READ_PERMISSIONS, allow_editor=True, detail="Finance read access required")
require_finance_write = require_permissions(FINANCE_WRITE_PERMISSIONS, allow_editor=True, detail="Finance write access required")
require_school_read = require_permissions(SCHOOL_READ_PERMISSIONS, allow_editor=True, detail="School read access required")
require_school_write = require_permissions(SCHOOL_WRITE_PERMISSIONS, allow_editor=True, detail="School write access required")
require_events_read = require_permissions(EVENTS_READ_PERMISSIONS, allow_editor=True, detail="Events read access required")
require_events_write = require_permissions(EVENTS_WRITE_PERMISSIONS, allow_editor=True, detail="Events write access required")
require_users_read = require_permissions(USERS_READ_PERMISSIONS, detail="Users read access required")
require_users_write = require_permissions(USERS_WRITE_PERMISSIONS, detail="Users write access required")
