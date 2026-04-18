import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
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
from app.services import smtp_settings_service


def _build_invitation_url(token: str) -> str:
    return f"{settings.PUBLIC_APP_URL}/invite/{token}"


def _generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _load_invitation_query(db: Session):
    return db.query(TenantInvitation).options(
        joinedload(TenantInvitation.tenant),
        joinedload(TenantInvitation.role_obj),
        joinedload(TenantInvitation.invited_by_user),
        joinedload(TenantInvitation.accepted_user),
    )


def _is_expired(invitation: TenantInvitation) -> bool:
    return invitation.expires_at <= _utc_now()


def _mark_expired_if_needed(db: Session, invitation: TenantInvitation) -> TenantInvitation:
    if invitation.status == "pending" and _is_expired(invitation):
        invitation.status = "expired"
        db.commit()
        db.refresh(invitation)
    return invitation


def _get_invitation_delivery(invitation: TenantInvitation) -> tuple[Optional[str], Optional[str], Optional[datetime]]:
    metadata = invitation.invite_metadata or {}
    return metadata.get("delivery_status"), metadata.get("delivery_error"), metadata.get("last_sent_at")


def _build_invitation_email(invitation: TenantInvitation) -> tuple[str, str]:
    tenant_name = (
        getattr(invitation.tenant, "public_display_name", None)
        or getattr(invitation.tenant, "name", None)
        or "sua igreja"
    )
    role_name = getattr(invitation.role_obj, "name", None) or invitation.role
    invite_url = _build_invitation_url(invitation.invite_token)
    subject = f"{tenant_name} | Convite para acessar a plataforma"
    body = (
        f"Ola,\n\n"
        f"Voce recebeu um convite para acessar a plataforma de {tenant_name}.\n\n"
        f"Perfil sugerido: {role_name}\n"
        f"Validade do convite: {invitation.expires_at.astimezone(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}\n\n"
        f"Aceite seu convite aqui:\n{invite_url}\n\n"
        f"Se voce ja possui conta, use sua senha atual para aceitar.\n"
        f"Se ainda nao possui, sera possivel criar a conta ao abrir o link.\n"
    )
    return subject, body


def _set_delivery_metadata(
    invitation: TenantInvitation,
    *,
    status: str,
    error: str | None = None,
    mark_sent: bool = False,
) -> None:
    metadata = dict(invitation.invite_metadata or {})
    metadata["delivery_status"] = status
    metadata["delivery_error"] = error[:500] if error else None
    if mark_sent:
        metadata["last_sent_at"] = _utc_now().isoformat()
    invitation.invite_metadata = metadata


def dispatch_invitation_email(db: Session, invitation: TenantInvitation) -> TenantInvitation:
    invitation = _mark_expired_if_needed(db, invitation)
    if invitation.status != "pending":
        raise ValueError("Only pending invitations can be sent")

    cfg = smtp_settings_service.resolve_effective_smtp_config(db, invitation.tenant_id)
    if cfg is None or not cfg.host or not cfg.from_email:
        _set_delivery_metadata(invitation, status="manual_share", error=None, mark_sent=False)
        db.commit()
        db.refresh(invitation)
        return invitation

    subject, body = _build_invitation_email(invitation)
    try:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = cfg.from_email
        message["To"] = invitation.email
        message.set_content(body)
        if cfg.encryption == "ssl":
            server: smtplib.SMTP = smtplib.SMTP_SSL(cfg.host, cfg.port, timeout=20)
        else:
            server = smtplib.SMTP(cfg.host, cfg.port, timeout=20)
        try:
            if cfg.encryption == "tls":
                server.starttls()
            if cfg.username and cfg.password:
                server.login(cfg.username, cfg.password)
            server.send_message(message)
        finally:
            try:
                server.quit()
            except Exception:
                server.close()
        _set_delivery_metadata(invitation, status="sent", error=None, mark_sent=True)
    except Exception as exc:
        _set_delivery_metadata(invitation, status="failed", error=str(exc), mark_sent=False)
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
        expires_at=_utc_now() + timedelta(days=payload.expires_in_days or settings.TENANT_INVITATION_EXPIRY_DAYS),
        invited_by_user_id=invited_by_user.id,
        invite_metadata={"expires_in_days": payload.expires_in_days},
    )
    db.add(invitation)
    db.commit()
    invitation = get_invitation_by_id(db, invitation.id, tenant.id)
    if invitation is None:
        raise ValueError("Failed to create invitation")
    return dispatch_invitation_email(db, invitation)


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
    invitation.revoked_at = _utc_now()
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
    invitation.accepted_at = _utc_now()
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
        "delivery_status": _get_invitation_delivery(invitation)[0],
        "delivery_error": _get_invitation_delivery(invitation)[1],
        "last_sent_at": _get_invitation_delivery(invitation)[2],
        "tenant": invitation.tenant,
        "role_obj": invitation.role_obj,
        "invited_by_user": invitation.invited_by_user,
        "accepted_user": invitation.accepted_user,
        "created_at": invitation.created_at,
    }
