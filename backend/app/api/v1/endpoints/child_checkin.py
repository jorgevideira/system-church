from datetime import date

import os
import uuid
import mimetypes

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_membership, get_current_tenant, get_db
from app.core.config import settings
from app.core.constants import ROLE_ADMIN, ROLE_EDITOR
from app.db.models.child_checkin import ChildCheckinChild, ChildCheckinFamily, ChildCheckinGuardian
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.child_checkin import (
    ChildCheckinAuditResponse,
    ChildCheckinCheckoutRequest,
    ChildCheckinChildCreate,
    ChildCheckinChildResponse,
    ChildCheckinChildUpdate,
    ChildCheckinCreate,
    ChildCheckinFamilyCreate,
    ChildCheckinFamilyResponse,
    ChildCheckinFamilyUpdate,
    ChildCheckinGuardianCreate,
    ChildCheckinGuardianResponse,
    ChildCheckinGuardianUpdate,
    ChildCheckinNotificationCreate,
    ChildCheckinNotificationResponse,
    ChildCheckinRecordResponse,
    ChildCheckinLabelPayloadResponse,
    ChildCheckinQrScanRequest,
    ChildCheckinRoomCreate,
    ChildCheckinRoomScopeCreate,
    ChildCheckinRoomMonitorEntryResponse,
    ChildCheckinRoomResponse,
    ChildCheckinRoomScopeResponse,
    ChildCheckinRoomUpdate,
    ChildCheckinSummaryResponse,
    ChildCheckinCheckoutContextResponse,
    ChildCheckinPublicPreRegistrationCreate,
    ChildCheckinPublicPreRegistrationResponse,
    ChildCheckinPublicChildCreate,
    ChildCheckinPublicChildUpdate,
    ChildCheckinPublicGuardianCreate,
    ChildCheckinPublicLoginRequest,
    ChildCheckinPublicLoginResponse,
    ChildCheckinPublicMeResponse,
    ChildCheckinPublicRecoveryRequest,
    ChildCheckinPublicRecoveryVerify,
    ChildCheckinPublicRecoveryConfirm,
    ChildCheckinVirtualCardSearchResponse,
    ChildCheckinVisitorQuickCreate,
    ChildCheckinSettingsResponse,
    ChildCheckinSettingsUpdate,
)
from app.services import child_checkin_service, child_checkin_settings_service, child_checkin_email_service

router = APIRouter()
public_router = APIRouter()

KIDS_VIEW_PERMISSIONS = {
    "cells_kids_view",
    "cells_kids_checkin",
    "cells_kids_checkout",
}

KIDS_MANAGE_PERMISSIONS = {
    "cells_kids_create",
    "cells_kids_edit",
    "cells_kids_manage",
    "cells_kids_manual_override",
    "cells_kids_reports",
}


def _ensure_dev_enabled() -> None:
    if not settings.CHILD_CHECKIN_DEV_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child check-in module is disabled")


def _bearer_token(authorization: str | None) -> str:
    raw = str(authorization or "").strip()
    if not raw:
        return ""
    if raw.lower().startswith("bearer "):
        return raw[7:].strip()
    return ""


def _get_public_family(
    db: Session,
    authorization: str | None,
) -> tuple[Tenant, ChildCheckinFamily]:
    token = _bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente.")
    payload = child_checkin_service.decode_public_family_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    tenant_id = int(payload["tenant_id"])
    family_id = int(payload["family_id"])
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active.is_(True)).first()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Igreja nao encontrada.")

    family = db.query(ChildCheckinFamily).filter(ChildCheckinFamily.tenant_id == tenant_id, ChildCheckinFamily.id == family_id).first()
    if family is None or not family.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Familia nao encontrada.")
    return tenant, family


def _permission_names(membership: TenantMembership) -> set[str]:
    role_obj = getattr(membership, "role_obj", None)
    permissions = getattr(role_obj, "permissions", None)
    if not permissions:
        return set()
    return {
        permission.name
        for permission in permissions
        if permission and permission.active and permission.name
    }


def _is_admin_or_editor(user: User, membership: TenantMembership) -> bool:
    return (
        user.role in {ROLE_ADMIN, ROLE_EDITOR}
        or membership.role in {ROLE_ADMIN, ROLE_EDITOR}
        or bool(getattr(getattr(membership, "role_obj", None), "is_admin", False))
    )


def _can_view(user: User, membership: TenantMembership) -> bool:
    if _is_admin_or_editor(user, membership):
        return True
    permissions = _permission_names(membership)
    return bool(permissions & KIDS_VIEW_PERMISSIONS)


def _can_manage(user: User, membership: TenantMembership) -> bool:
    if _is_admin_or_editor(user, membership):
        return True
    permissions = _permission_names(membership)
    return bool(permissions & KIDS_MANAGE_PERMISSIONS)


def _can_manual_override(user: User, membership: TenantMembership) -> bool:
    if _is_admin_or_editor(user, membership):
        return True
    return "cells_kids_manual_override" in _permission_names(membership)


def _room_scope_for_user(db: Session, tenant: Tenant, user: User, membership: TenantMembership) -> set[str] | None:
    if _is_admin_or_editor(user, membership):
        return None
    scopes = child_checkin_service.get_user_room_scopes(db, tenant.id, user.id)
    return scopes or None


def _tenant_by_slug(db: Session, tenant_slug: str) -> Tenant | None:
    return (
        db.query(Tenant)
        .filter(Tenant.slug == tenant_slug, Tenant.is_active.is_(True))
        .first()
    )


@router.get("/summary", response_model=ChildCheckinSummaryResponse)
def get_summary(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinSummaryResponse:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.build_summary(db, current_tenant.id, start_date, end_date)


@router.get("/settings", response_model=ChildCheckinSettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinSettingsResponse:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_settings_service.get_settings(db, current_tenant.id)


@router.put("/settings", response_model=ChildCheckinSettingsResponse)
def update_settings(
    payload: ChildCheckinSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinSettingsResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_settings_service.upsert_settings(db, current_tenant.id, payload.ops_context_presets)


@public_router.post(
    "/public/tenants/{tenant_slug}/pre-register",
    response_model=ChildCheckinPublicPreRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def public_pre_register(
    tenant_slug: str,
    payload: ChildCheckinPublicPreRegistrationCreate,
    db: Session = Depends(get_db),
) -> ChildCheckinPublicPreRegistrationResponse:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    try:
        family, cards = child_checkin_service.create_public_pre_registration(
            db,
            tenant_id=tenant.id,
            tenant_slug=tenant.slug,
            payload=payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    token = child_checkin_service.create_public_family_token(tenant_id=tenant.id, family_id=family.id) if payload.public_pin else None
    email_sent = False
    email_error = None
    try:
        child_checkin_email_service.send_virtual_cards_email(
            db,
            tenant_id=tenant.id,
            tenant_slug=tenant.slug,
            to_email=str(payload.email),
            family_code=family.family_code,
            cards=cards,
        )
        email_sent = True
    except Exception as exc:
        email_sent = False
        email_error = str(exc)[:200]
    return ChildCheckinPublicPreRegistrationResponse(
        tenant_slug=tenant.slug,
        family_id=family.id,
        family_code=family.family_code,
        cards=cards,
        token=token,
        email_sent=email_sent,
        email_error=email_error,
    )


@public_router.post(
    "/public/tenants/{tenant_slug}/login",
    response_model=ChildCheckinPublicLoginResponse,
)
def public_login(
    tenant_slug: str,
    payload: ChildCheckinPublicLoginRequest,
    db: Session = Depends(get_db),
) -> ChildCheckinPublicLoginResponse:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")
    try:
        family = child_checkin_service.public_login_family(
            db,
            tenant_id=tenant.id,
            email=str(payload.email) if payload.email else None,
            phone=str(payload.phone) if payload.phone else None,
            pin=payload.pin,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    token = child_checkin_service.create_public_family_token(tenant_id=tenant.id, family_id=family.id)
    return ChildCheckinPublicLoginResponse(
        tenant_slug=tenant.slug,
        family_id=family.id,
        family_code=family.family_code,
        token=token,
    )


@public_router.post(
    "/public/tenants/{tenant_slug}/recover/request",
    status_code=status.HTTP_204_NO_CONTENT,
)
def public_recover_request(
    tenant_slug: str,
    payload: ChildCheckinPublicRecoveryRequest,
    db: Session = Depends(get_db),
) -> Response:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    fam, code = child_checkin_service.request_public_pin_recovery(db, tenant_id=tenant.id, email=str(payload.email))
    # Avoid leaking account existence: always return 204.
    if fam is not None and code:
        child_checkin_email_service.send_recovery_code_email(
            db,
            tenant_id=tenant.id,
            to_email=str(payload.email),
            code=code,
            minutes_valid=15,
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@public_router.post(
    "/public/tenants/{tenant_slug}/recover/verify",
    status_code=status.HTTP_204_NO_CONTENT,
)
def public_recover_verify(
    tenant_slug: str,
    payload: ChildCheckinPublicRecoveryVerify,
    db: Session = Depends(get_db),
) -> Response:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")
    try:
        child_checkin_service.verify_public_pin_recovery(
            db,
            tenant_id=tenant.id,
            email=str(payload.email),
            code=payload.code,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@public_router.post(
    "/public/tenants/{tenant_slug}/recover/confirm",
    response_model=ChildCheckinPublicLoginResponse,
)
def public_recover_confirm(
    tenant_slug: str,
    payload: ChildCheckinPublicRecoveryConfirm,
    db: Session = Depends(get_db),
) -> ChildCheckinPublicLoginResponse:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")
    try:
        family = child_checkin_service.confirm_public_pin_recovery(
            db,
            tenant_id=tenant.id,
            email=str(payload.email),
            code=payload.code,
            new_pin=payload.new_pin,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    token = child_checkin_service.create_public_family_token(tenant_id=tenant.id, family_id=family.id)
    return ChildCheckinPublicLoginResponse(
        tenant_slug=tenant.slug,
        family_id=family.id,
        family_code=family.family_code,
        token=token,
    )


@public_router.get(
    "/public/me",
    response_model=ChildCheckinPublicMeResponse,
)
def public_me(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> ChildCheckinPublicMeResponse:
    _ensure_dev_enabled()
    tenant, family = _get_public_family(db, authorization)

    children = (
        db.query(ChildCheckinChild)
        .filter(ChildCheckinChild.tenant_id == tenant.id, ChildCheckinChild.family_id == family.id, ChildCheckinChild.is_active.is_(True))
        .order_by(ChildCheckinChild.full_name.asc())
        .all()
    )
    guardians = (
        db.query(ChildCheckinGuardian)
        .filter(ChildCheckinGuardian.tenant_id == tenant.id, ChildCheckinGuardian.family_id == family.id)
        .order_by(ChildCheckinGuardian.full_name.asc())
        .all()
    )

    return ChildCheckinPublicMeResponse(
        tenant_slug=tenant.slug,
        family=family,
        children=children,
        guardians=guardians,
    )


@public_router.post(
    "/public/me/children",
    response_model=ChildCheckinChildResponse,
    status_code=status.HTTP_201_CREATED,
)
def public_create_child(
    payload: ChildCheckinPublicChildCreate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> ChildCheckinChildResponse:
    _ensure_dev_enabled()
    tenant, family = _get_public_family(db, authorization)
    created = child_checkin_service.create_child(
        db,
        tenant.id,
        ChildCheckinChildCreate(
            family_id=family.id,
            full_name=payload.full_name,
            birth_date=payload.birth_date,
            age_group=payload.age_group,
            room_name=payload.room_name,
            gender=payload.gender,
            photo_url=payload.photo_url,
            notes=payload.notes,
            allergies=payload.allergies,
            medical_restrictions=payload.medical_restrictions,
            special_needs=payload.special_needs,
            behavioral_notes=payload.behavioral_notes,
            is_visitor=False,
        ),
        actor_user_id=None,
    )
    return created


@public_router.patch(
    "/public/me/children/{child_id}",
    response_model=ChildCheckinChildResponse,
)
def public_update_child(
    child_id: int,
    payload: ChildCheckinPublicChildUpdate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> ChildCheckinChildResponse:
    _ensure_dev_enabled()
    tenant, family = _get_public_family(db, authorization)
    child = (
        db.query(ChildCheckinChild)
        .filter(
            ChildCheckinChild.tenant_id == tenant.id,
            ChildCheckinChild.family_id == family.id,
            ChildCheckinChild.id == child_id,
            ChildCheckinChild.is_active.is_(True),
        )
        .first()
    )
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crianca nao encontrada")

    updated = child_checkin_service.update_child(
        db,
        tenant.id,
        child_id,
        ChildCheckinChildUpdate(**payload.model_dump(exclude_unset=True)),
        actor_user_id=None,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crianca nao encontrada")
    return updated


@public_router.post(
    "/public/me/guardians",
    response_model=ChildCheckinGuardianResponse,
    status_code=status.HTTP_201_CREATED,
)
def public_create_guardian(
    payload: ChildCheckinPublicGuardianCreate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> ChildCheckinGuardianResponse:
    _ensure_dev_enabled()
    tenant, family = _get_public_family(db, authorization)
    created = child_checkin_service.create_guardian(
        db,
        tenant.id,
        ChildCheckinGuardianCreate(
            family_id=family.id,
            full_name=payload.full_name,
            relationship=payload.relationship,
            phone=payload.phone,
            photo_url=payload.photo_url,
            is_authorized=payload.is_authorized,
            notes=None,
        ),
        actor_user_id=None,
    )
    return created


@public_router.get(
    "/public/tenants/{tenant_slug}/virtual-cards",
    response_model=ChildCheckinVirtualCardSearchResponse,
)
def public_virtual_cards(
    tenant_slug: str,
    family_code: str = Query(..., min_length=4),
    db: Session = Depends(get_db),
) -> ChildCheckinVirtualCardSearchResponse:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    family, cards = child_checkin_service.get_virtual_cards_by_family_code(
        db,
        tenant_id=tenant.id,
        tenant_slug=tenant.slug,
        family_code=family_code,
    )
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familia nao encontrada")

    return ChildCheckinVirtualCardSearchResponse(
        tenant_slug=tenant.slug,
        family_id=family.id,
        family_code=family.family_code,
        cards=cards,
    )


@public_router.get(
    "/public/tenants/{tenant_slug}/families/{family_code}/children/{child_id}/qr.png",
    response_class=Response,
)
def public_virtual_card_qr_png(
    tenant_slug: str,
    family_code: str,
    child_id: int,
    db: Session = Depends(get_db),
) -> Response:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    family = child_checkin_service.get_family_by_code(db, tenant_id=tenant.id, family_code=family_code)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familia nao encontrada")

    child = (
        db.query(ChildCheckinChild)
        .filter(
            ChildCheckinChild.tenant_id == tenant.id,
            ChildCheckinChild.family_id == family.id,
            ChildCheckinChild.id == child_id,
        )
        .first()
    )
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crianca nao encontrada")

    png = child_checkin_service.build_virtual_card_qr_png(
        tenant_slug=tenant.slug,
        family_code=family.family_code,
        child_id=child.id,
    )
    return Response(content=png, media_type="image/png")


def _save_public_kids_photo(*, tenant_id: int, folder: str, file: UploadFile) -> str:
    # We store under UPLOAD_DIR and serve via /media/uploads/.
    allowed = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    content_type = (file.content_type or "").lower().strip()
    ext = allowed.get(content_type)
    if not ext:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de imagem nao suportado. Use JPG, PNG ou WEBP.")

    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio.")
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Maximo {settings.MAX_FILE_SIZE // (1024 * 1024)} MB.",
        )

    rel_dir = os.path.join("child-checkin", f"tenant-{tenant_id}", folder)
    abs_dir = os.path.join(settings.UPLOAD_DIR, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{ext}"
    abs_path = os.path.join(abs_dir, filename)
    with open(abs_path, "wb") as fp:
        fp.write(contents)
    return f"/media/uploads/{rel_dir}/{filename}"


def _resolve_upload_file(photo_url: str | None) -> str | None:
    url = str(photo_url or "")
    prefix = "/media/uploads/"
    if not url.startswith(prefix):
        return None
    rel = url[len(prefix):].lstrip("/")
    upload_root = os.path.abspath(settings.UPLOAD_DIR)
    abs_path = os.path.abspath(os.path.join(settings.UPLOAD_DIR, rel))
    if not abs_path.startswith(upload_root + os.sep) and abs_path != upload_root:
        return None
    if not os.path.exists(abs_path):
        return None
    return abs_path


@public_router.get("/public/tenants/{tenant_slug}/families/{family_code}/children/{child_id}/photo")
def public_get_child_photo(
    tenant_slug: str,
    family_code: str,
    child_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    family = child_checkin_service.get_family_by_code(db, tenant_id=tenant.id, family_code=family_code)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familia nao encontrada")

    child = (
        db.query(ChildCheckinChild)
        .filter(
            ChildCheckinChild.tenant_id == tenant.id,
            ChildCheckinChild.family_id == family.id,
            ChildCheckinChild.id == child_id,
        )
        .first()
    )
    if child is None or not child.photo_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto nao encontrada")

    abs_path = _resolve_upload_file(child.photo_url)
    if abs_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto nao encontrada")

    media_type, _enc = mimetypes.guess_type(abs_path)
    return FileResponse(abs_path, media_type=media_type or "application/octet-stream")


@public_router.get("/public/tenants/{tenant_slug}/families/{family_code}/guardians/{guardian_id}/photo")
def public_get_guardian_photo(
    tenant_slug: str,
    family_code: str,
    guardian_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    family = child_checkin_service.get_family_by_code(db, tenant_id=tenant.id, family_code=family_code)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familia nao encontrada")

    guardian = (
        db.query(ChildCheckinGuardian)
        .filter(
            ChildCheckinGuardian.tenant_id == tenant.id,
            ChildCheckinGuardian.family_id == family.id,
            ChildCheckinGuardian.id == guardian_id,
        )
        .first()
    )
    if guardian is None or not guardian.photo_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto nao encontrada")

    abs_path = _resolve_upload_file(guardian.photo_url)
    if abs_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto nao encontrada")

    media_type, _enc = mimetypes.guess_type(abs_path)
    return FileResponse(abs_path, media_type=media_type or "application/octet-stream")


@public_router.post("/public/tenants/{tenant_slug}/families/{family_code}/children/{child_id}/photo")
def public_set_child_photo(
    tenant_slug: str,
    family_code: str,
    child_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    family = child_checkin_service.get_family_by_code(db, tenant_id=tenant.id, family_code=family_code)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familia nao encontrada")

    photo_url = _save_public_kids_photo(tenant_id=tenant.id, folder="children", file=file)
    updated = child_checkin_service.set_child_photo_url(
        db,
        tenant_id=tenant.id,
        family_id=family.id,
        child_id=child_id,
        photo_url=photo_url,
        actor_user_id=None,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crianca nao encontrada")
    return {"photo_url": photo_url}


@public_router.post("/public/tenants/{tenant_slug}/families/{family_code}/guardians/{guardian_id}/photo")
def public_set_guardian_photo(
    tenant_slug: str,
    family_code: str,
    guardian_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    _ensure_dev_enabled()
    tenant = _tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant nao encontrado")

    family = child_checkin_service.get_family_by_code(db, tenant_id=tenant.id, family_code=family_code)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Familia nao encontrada")

    photo_url = _save_public_kids_photo(tenant_id=tenant.id, folder="guardians", file=file)
    updated = child_checkin_service.set_guardian_photo_url(
        db,
        tenant_id=tenant.id,
        family_id=family.id,
        guardian_id=guardian_id,
        photo_url=photo_url,
        actor_user_id=None,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Responsavel nao encontrado")
    return {"photo_url": photo_url}


@router.get("/families", response_model=list[ChildCheckinFamilyResponse])
def list_families(
    q: str | None = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinFamilyResponse]:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.list_families(db, current_tenant.id, q, include_inactive=include_inactive)


@router.post("/families", response_model=ChildCheckinFamilyResponse, status_code=status.HTTP_201_CREATED)
def create_family(
    payload: ChildCheckinFamilyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinFamilyResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.create_family(db, current_tenant.id, payload, current_user.id)


@router.put("/families/{family_id}", response_model=ChildCheckinFamilyResponse)
def update_family(
    family_id: int,
    payload: ChildCheckinFamilyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinFamilyResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    updated = child_checkin_service.update_family(db, current_tenant.id, family_id, payload, current_user.id)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    return updated


@router.get("/children", response_model=list[ChildCheckinChildResponse])
def list_children(
    family_id: int | None = Query(None),
    room_name: str | None = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinChildResponse]:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    room_scope = _room_scope_for_user(db, current_tenant, current_user, current_membership)
    effective_room_name = room_name
    if room_scope and not room_name:
        # scoped users without explicit room only see first room scope by default
        effective_room_name = sorted(list(room_scope))[0]

    return child_checkin_service.list_children(
        db,
        current_tenant.id,
        family_id=family_id,
        room_name=effective_room_name,
        include_inactive=include_inactive,
    )


@router.post("/children", response_model=ChildCheckinChildResponse, status_code=status.HTTP_201_CREATED)
def create_child(
    payload: ChildCheckinChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinChildResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.create_child(db, current_tenant.id, payload, current_user.id)


@router.put("/children/{child_id}", response_model=ChildCheckinChildResponse)
def update_child(
    child_id: int,
    payload: ChildCheckinChildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinChildResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    updated = child_checkin_service.update_child(db, current_tenant.id, child_id, payload, current_user.id)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    return updated


@router.get("/guardians", response_model=list[ChildCheckinGuardianResponse])
def list_guardians(
    family_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinGuardianResponse]:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.list_guardians(db, current_tenant.id, family_id)


@router.post("/guardians", response_model=ChildCheckinGuardianResponse, status_code=status.HTTP_201_CREATED)
def create_guardian(
    payload: ChildCheckinGuardianCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinGuardianResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.create_guardian(db, current_tenant.id, payload, current_user.id)


@router.put("/guardians/{guardian_id}", response_model=ChildCheckinGuardianResponse)
def update_guardian(
    guardian_id: int,
    payload: ChildCheckinGuardianUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinGuardianResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    updated = child_checkin_service.update_guardian(db, current_tenant.id, guardian_id, payload, current_user.id)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian not found")
    return updated


@router.get("/checkins", response_model=list[ChildCheckinRecordResponse])
def list_checkins(
    status_filter: str | None = Query(None, alias="status"),
    room_name: str | None = Query(None),
    target_date: date | None = Query(None, alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinRecordResponse]:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    room_scope = _room_scope_for_user(db, current_tenant, current_user, current_membership)
    return child_checkin_service.list_checkins(
        db,
        tenant_id=current_tenant.id,
        status_filter=status_filter,
        room_name=room_name,
        target_date=target_date,
        room_scope_restriction=room_scope,
    )


@router.post("/checkins/scan-qr", response_model=ChildCheckinRecordResponse, status_code=status.HTTP_201_CREATED)
def scan_qr_checkin(
    payload: ChildCheckinQrScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinRecordResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    room_scope = _room_scope_for_user(db, current_tenant, current_user, current_membership)
    try:
        return child_checkin_service.create_checkin_from_qr(
            db,
            tenant_id=current_tenant.id,
            tenant_slug=current_tenant.slug,
            payload=payload,
            actor_user_id=current_user.id,
            room_scope_restriction=room_scope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/checkins/{checkin_id}/checkout-context", response_model=ChildCheckinCheckoutContextResponse)
def checkout_context(
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinCheckoutContextResponse:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    row = child_checkin_service.get_checkout_context(db, tenant_id=current_tenant.id, checkin_id=checkin_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    return ChildCheckinCheckoutContextResponse(**row)


@router.get("/checkins/{checkin_id}/label", response_model=ChildCheckinLabelPayloadResponse)
def checkin_label(
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinLabelPayloadResponse:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    payload = child_checkin_service.build_label_payload(db, tenant_id=current_tenant.id, checkin_id=checkin_id)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    return ChildCheckinLabelPayloadResponse(**payload)


@router.get("/checkins/{checkin_id}/label/qr.png", response_class=Response)
def checkin_label_qr_png(
    checkin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> Response:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    qr_png = child_checkin_service.build_label_qr_png(db, tenant_id=current_tenant.id, checkin_id=checkin_id)
    if qr_png is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    return Response(content=qr_png, media_type="image/png")


@router.get("/rooms/{room_name}/monitoring", response_model=list[ChildCheckinRoomMonitorEntryResponse])
def room_monitoring(
    room_name: str,
    day: date | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinRoomMonitorEntryResponse]:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    room_scope = _room_scope_for_user(db, current_tenant, current_user, current_membership)
    try:
        return child_checkin_service.list_room_active_children(
            db,
            tenant_id=current_tenant.id,
            room_name=room_name,
            target_date=day,
            room_scope_restriction=room_scope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/checkins", response_model=list[ChildCheckinRecordResponse], status_code=status.HTTP_201_CREATED)
def create_checkin(
    payload: ChildCheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinRecordResponse]:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    room_scope = _room_scope_for_user(db, current_tenant, current_user, current_membership)
    try:
        rows = child_checkin_service.create_checkins(
            db,
            tenant_id=current_tenant.id,
            payload=payload,
            actor_user_id=current_user.id,
            room_scope_restriction=room_scope,
        )
        if not rows:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nenhum check-in foi criado")
        return rows
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/checkins/{checkin_id}/checkout", response_model=ChildCheckinRecordResponse)
def checkout_checkin(
    checkin_id: int,
    payload: ChildCheckinCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinRecordResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    room_scope = _room_scope_for_user(db, current_tenant, current_user, current_membership)
    try:
        updated = child_checkin_service.checkout_checkin(
            db,
            tenant_id=current_tenant.id,
            checkin_id=checkin_id,
            payload=payload,
            actor_user_id=current_user.id,
            can_manual_override=_can_manual_override(current_user, current_membership),
            room_scope_restriction=room_scope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    return updated


@router.post("/visitors/quick-checkin", response_model=list[ChildCheckinRecordResponse], status_code=status.HTTP_201_CREATED)
def visitor_quick_checkin(
    payload: ChildCheckinVisitorQuickCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinRecordResponse]:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    room_scope = _room_scope_for_user(db, current_tenant, current_user, current_membership)
    try:
        return child_checkin_service.create_visitor_quick_checkin(
            db,
            tenant_id=current_tenant.id,
            payload=payload,
            actor_user_id=current_user.id,
            room_scope_restriction=room_scope,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/notifications", response_model=list[ChildCheckinNotificationResponse])
def list_notifications(
    limit: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinNotificationResponse]:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.list_notifications(db, current_tenant.id, limit=limit)


@router.post("/notifications", response_model=ChildCheckinNotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: ChildCheckinNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinNotificationResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.create_notification(db, current_tenant.id, payload, current_user.id)


@router.get("/room-scopes", response_model=list[ChildCheckinRoomScopeResponse])
def list_room_scopes(
    user_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinRoomScopeResponse]:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.list_room_scopes(db, current_tenant.id, user_id=user_id)


@router.get("/rooms", response_model=list[ChildCheckinRoomResponse])
def list_rooms(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinRoomResponse]:
    _ensure_dev_enabled()
    if not _can_view(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.list_rooms(db, current_tenant.id, include_inactive=include_inactive)


@router.post("/rooms", response_model=ChildCheckinRoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: ChildCheckinRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinRoomResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.create_room(db, current_tenant.id, payload, current_user.id)


@router.put("/rooms/{room_id}", response_model=ChildCheckinRoomResponse)
def update_room(
    room_id: int,
    payload: ChildCheckinRoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinRoomResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    row = child_checkin_service.update_room(db, current_tenant.id, room_id, payload, current_user.id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala nao encontrada")
    return row


@router.get("/audits", response_model=list[ChildCheckinAuditResponse])
def list_audits(
    record_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[ChildCheckinAuditResponse]:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return child_checkin_service.list_audits(db, tenant_id=current_tenant.id, limit=limit, record_id=record_id)


@router.post("/room-scopes", response_model=ChildCheckinRoomScopeResponse, status_code=status.HTTP_201_CREATED)
def create_room_scope(
    payload: ChildCheckinRoomScopeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> ChildCheckinRoomScopeResponse:
    _ensure_dev_enabled()
    if not _can_manage(current_user, current_membership):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        child_checkin_service.validate_scope_users_exist(db, current_tenant.id, [payload.user_id])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return child_checkin_service.create_room_scope(db, current_tenant.id, payload)
