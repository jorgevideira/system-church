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
    if not (has_admin_role_name or has_admin_role_obj or has_membership_admin_role_name or has_membership_admin_role_obj):
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
