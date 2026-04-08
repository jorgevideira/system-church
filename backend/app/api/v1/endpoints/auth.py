from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.user import SwitchTenantRequest, Token, UserResponse
from app.services.user_service import authenticate_user

router = APIRouter()


def _resolve_active_membership(db: Session, user: User) -> TenantMembership | None:
    memberships = (
        db.query(TenantMembership)
        .filter(TenantMembership.user_id == user.id, TenantMembership.is_active.is_(True))
        .order_by(TenantMembership.is_default.desc(), TenantMembership.id.asc())
        .all()
    )
    if not memberships:
        return None

    if user.active_tenant_id is not None:
        for membership in memberships:
            if membership.tenant_id == user.active_tenant_id:
                return membership

    default_membership = next((membership for membership in memberships if membership.is_default), None)
    if default_membership is not None:
        return default_membership
    return memberships[0]


def _issue_token_pair(user: User, active_membership: TenantMembership | None) -> Token:
    active_tenant_id = active_membership.tenant_id if active_membership else None
    active_tenant_slug = active_membership.tenant.slug if active_membership and active_membership.tenant else None
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "tenant_id": active_tenant_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "tenant_id": active_tenant_id})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        active_tenant_id=active_tenant_id,
        active_tenant_slug=active_tenant_slug,
    )


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    active_membership = _resolve_active_membership(db, user)
    if active_membership and user.active_tenant_id != active_membership.tenant_id:
        user.active_tenant_id = active_membership.tenant_id
        db.commit()
        db.refresh(user)
    return _issue_token_pair(user, active_membership)


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token_str: str, db: Session = Depends(get_db)) -> Token:
    payload = decode_token(refresh_token_str)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    email: str | None = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    requested_tenant_id = payload.get("tenant_id")
    active_membership = _resolve_active_membership(db, user)
    if requested_tenant_id is not None:
        selected_membership = (
            db.query(TenantMembership)
            .filter(
                TenantMembership.user_id == user.id,
                TenantMembership.tenant_id == requested_tenant_id,
                TenantMembership.is_active.is_(True),
            )
            .first()
        )
        if selected_membership is not None:
            active_membership = selected_membership
    if active_membership and user.active_tenant_id != active_membership.tenant_id:
        user.active_tenant_id = active_membership.tenant_id
        db.commit()
        db.refresh(user)
    return _issue_token_pair(user, active_membership)


@router.post("/logout")
def logout() -> dict:
    # JWT is stateless; client should discard the token.
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user


@router.post("/switch-tenant", response_model=Token)
def switch_tenant(
    payload: SwitchTenantRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
) -> Token:
    membership = (
        db.query(TenantMembership)
        .filter(
            TenantMembership.user_id == current_user.id,
            TenantMembership.tenant_id == payload.tenant_id,
            TenantMembership.is_active.is_(True),
        )
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no access to the requested tenant")
    current_user.active_tenant_id = membership.tenant_id
    db.commit()
    db.refresh(current_user)
    return _issue_token_pair(current_user, membership)
