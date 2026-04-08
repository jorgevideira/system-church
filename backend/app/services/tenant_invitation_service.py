import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.db.models.role import Role
from app.db.models.tenant import Tenant
from app.db.models.tenant_invitation import TenantInvitation
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.tenant_invitation import TenantInvitationAcceptRequest, TenantInvitationCreate


def _build_invitation_url(token: str) -> str:
    return f"{settings.PUBLIC_APP_URL}/invite/{token}"


def _generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def _load_invitation_query(db: Session):
    return db.query(TenantInvitation).options(
        joinedload(TenantInvitation.tenant),
        joinedload(TenantInvitation.role_obj),
        joinedload(TenantInvitation.invited_by_user),
        joinedload(TenantInvitation.accepted_user),
    )


def _is_expired(invitation: TenantInvitation) -> bool:
    return invitation.expires_at <= datetime.now(timezone.utc)


def _mark_expired_if_needed(db: Session, invitation: TenantInvitation) -> TenantInvitation:
    if invitation.status == "pending" and _is_expired(invitation):
        invitation.status = "expired"
        db.commit()
        db.refresh(invitation)
    return invitation


def list_invitations(db: Session, tenant_id: int) -> list[TenantInvitation]:
    invitations = (
        _load_invitation_query(db)
        .filter(TenantInvitation.tenant_id == tenant_id)
        .order_by(TenantInvitation.created_at.desc(), TenantInvitation.id.desc())
        .all()
    )
    for invitation in invitations:
        _mark_expired_if_needed(db, invitation)
    return invitations


def create_invitation(db: Session, tenant: Tenant, payload: TenantInvitationCreate, invited_by_user: User) -> TenantInvitation:
    email = str(payload.email).strip().lower()
    role_name = payload.role
    role_id = payload.role_id

    if role_id is not None:
        role_obj = db.query(Role).filter(Role.id == role_id, Role.tenant_id == tenant.id).first()
        if role_obj is None:
            raise ValueError("Role not found for this tenant")
        role_name = role_obj.name.lower()

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user is not None:
        existing_membership = (
            db.query(TenantMembership)
            .filter(TenantMembership.user_id == existing_user.id, TenantMembership.tenant_id == tenant.id)
            .first()
        )
        if existing_membership is not None:
            raise ValueError("User is already linked to this tenant")

    active_invitation = (
        db.query(TenantInvitation)
        .filter(
            TenantInvitation.tenant_id == tenant.id,
            TenantInvitation.email == email,
            TenantInvitation.status == "pending",
        )
        .first()
    )
    if active_invitation is not None and not _is_expired(active_invitation):
        raise ValueError("There is already an active invitation for this email")

    invitation = TenantInvitation(
        tenant_id=tenant.id,
        email=email,
        full_name=payload.full_name,
        role=role_name,
        role_id=role_id,
        invite_token=_generate_invite_token(),
        status="pending",
        is_default=payload.is_default,
        expires_at=datetime.now(timezone.utc) + timedelta(days=payload.expires_in_days or settings.TENANT_INVITATION_EXPIRY_DAYS),
        invited_by_user_id=invited_by_user.id,
        invite_metadata={"expires_in_days": payload.expires_in_days},
    )
    db.add(invitation)
    db.commit()
    return get_invitation_by_id(db, invitation.id, tenant.id)


def get_invitation_by_id(db: Session, invitation_id: int, tenant_id: int) -> Optional[TenantInvitation]:
    invitation = (
        _load_invitation_query(db)
        .filter(TenantInvitation.id == invitation_id, TenantInvitation.tenant_id == tenant_id)
        .first()
    )
    if invitation is None:
        return None
    return _mark_expired_if_needed(db, invitation)


def get_invitation_by_token(db: Session, token: str) -> Optional[TenantInvitation]:
    invitation = _load_invitation_query(db).filter(TenantInvitation.invite_token == token).first()
    if invitation is None:
        return None
    return _mark_expired_if_needed(db, invitation)


def revoke_invitation(db: Session, invitation: TenantInvitation) -> TenantInvitation:
    if invitation.status == "accepted":
        raise ValueError("Accepted invitation cannot be revoked")
    invitation.status = "revoked"
    invitation.revoked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(invitation)
    return invitation


def accept_invitation(db: Session, invitation: TenantInvitation, payload: TenantInvitationAcceptRequest) -> tuple[User, TenantMembership]:
    invitation = _mark_expired_if_needed(db, invitation)
    if invitation.status != "pending":
        raise ValueError("Invitation is no longer available")
    if _is_expired(invitation):
        raise ValueError("Invitation has expired")

    email = invitation.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    password = payload.password
    role_name = invitation.role
    role_id = invitation.role_id

    if user is not None:
        if not user.is_active:
            raise ValueError("User is inactive")
        if not verify_password(password, user.hashed_password):
            raise ValueError("Existing account found. Use the current password to accept this invitation")
        if payload.full_name and not user.full_name:
            user.full_name = payload.full_name.strip()
    else:
        full_name = (payload.full_name or invitation.full_name or "").strip()
        if not full_name:
            raise ValueError("Full name is required to create the account")
        user = User(
            email=email,
            full_name=full_name,
            role=role_name,
            role_id=role_id,
            hashed_password=get_password_hash(password),
            is_active=True,
        )
        db.add(user)
        db.flush()

    membership = (
        db.query(TenantMembership)
        .filter(TenantMembership.user_id == user.id, TenantMembership.tenant_id == invitation.tenant_id)
        .first()
    )
    if membership is None:
        if invitation.is_default:
            (
                db.query(TenantMembership)
                .filter(TenantMembership.user_id == user.id, TenantMembership.is_default.is_(True))
                .update({"is_default": False}, synchronize_session=False)
            )
        has_membership = db.query(TenantMembership.id).filter(TenantMembership.user_id == user.id).first() is not None
        membership = TenantMembership(
            user_id=user.id,
            tenant_id=invitation.tenant_id,
            role=role_name,
            role_id=role_id,
            is_active=True,
            is_default=invitation.is_default or not has_membership,
        )
        db.add(membership)
    else:
        membership.is_active = True
        membership.role = role_name
        membership.role_id = role_id
        if invitation.is_default:
            (
                db.query(TenantMembership)
                .filter(TenantMembership.user_id == user.id, TenantMembership.is_default.is_(True))
                .update({"is_default": False}, synchronize_session=False)
            )
            membership.is_default = True

    if user.active_tenant_id is None or membership.is_default:
        user.active_tenant_id = invitation.tenant_id
    user.role = role_name
    user.role_id = role_id

    invitation.status = "accepted"
    invitation.accepted_at = datetime.now(timezone.utc)
    invitation.accepted_user_id = user.id

    db.commit()
    db.refresh(user)
    db.refresh(membership)
    return user, membership


def serialize_invitation(invitation: TenantInvitation) -> dict:
    return {
        "id": invitation.id,
        "email": invitation.email,
        "full_name": invitation.full_name,
        "role": invitation.role,
        "role_id": invitation.role_id,
        "status": invitation.status,
        "is_default": invitation.is_default,
        "invite_token": invitation.invite_token,
        "invite_url": _build_invitation_url(invitation.invite_token),
        "expires_at": invitation.expires_at,
        "accepted_at": invitation.accepted_at,
        "revoked_at": invitation.revoked_at,
        "tenant": invitation.tenant,
        "role_obj": invitation.role_obj,
        "invited_by_user": invitation.invited_by_user,
        "accepted_user": invitation.accepted_user,
        "created_at": invitation.created_at,
    }
