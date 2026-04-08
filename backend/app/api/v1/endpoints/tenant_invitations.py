from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant, get_db, require_admin
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.tenant_invitation import (
    TenantInvitationAcceptRequest,
    TenantInvitationAcceptResponse,
    TenantInvitationCreate,
    TenantInvitationPublicResponse,
    TenantInvitationResponse,
)
from app.services import tenant_invitation_service

router = APIRouter()


def _issue_token_pair(user: User, tenant_id: int, tenant_slug: str | None) -> dict:
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "tenant_id": tenant_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "tenant_id": tenant_id})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "active_tenant_id": tenant_id,
        "active_tenant_slug": tenant_slug,
    }


@router.get("/", response_model=List[TenantInvitationResponse])
def list_tenant_invitations(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[dict]:
    invitations = tenant_invitation_service.list_invitations(db, current_tenant.id)
    return [tenant_invitation_service.serialize_invitation(item) for item in invitations]


@router.post("/", response_model=TenantInvitationResponse, status_code=status.HTTP_201_CREATED)
def create_tenant_invitation(
    payload: TenantInvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> dict:
    try:
        invitation = tenant_invitation_service.create_invitation(db, current_tenant, payload, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return tenant_invitation_service.serialize_invitation(invitation)


@router.delete("/{invitation_id}", response_model=TenantInvitationResponse)
def revoke_tenant_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> dict:
    invitation = tenant_invitation_service.get_invitation_by_id(db, invitation_id, current_tenant.id)
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    try:
        invitation = tenant_invitation_service.revoke_invitation(db, invitation)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return tenant_invitation_service.serialize_invitation(invitation)


@router.get("/public/{invite_token}", response_model=TenantInvitationPublicResponse)
def get_public_invitation(invite_token: str, db: Session = Depends(get_db)):
    invitation = tenant_invitation_service.get_invitation_by_token(db, invite_token)
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    if invitation.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is no longer available")
    return invitation


@router.post("/public/{invite_token}/accept", response_model=TenantInvitationAcceptResponse)
def accept_public_invitation(
    invite_token: str,
    payload: TenantInvitationAcceptRequest,
    db: Session = Depends(get_db),
) -> TenantInvitationAcceptResponse:
    invitation = tenant_invitation_service.get_invitation_by_token(db, invite_token)
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    try:
        user, membership = tenant_invitation_service.accept_invitation(db, invitation, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    token_pair = _issue_token_pair(user, membership.tenant_id, invitation.tenant.slug if invitation.tenant else None)
    return TenantInvitationAcceptResponse(user=user, **token_pair)
