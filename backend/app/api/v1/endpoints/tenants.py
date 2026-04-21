from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant, get_db, require_admin, require_users_read, require_users_write
from app.core.config import settings
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.tenant import (
    TenantBrandingResponse,
    TenantCreate,
    TenantPaymentSettingsResponse,
    TenantPaymentSettingsUpdate,
    TenantResponse,
    TenantUpdate,
)
from app.schemas.smtp_settings import (
    TenantSmtpSettingsResponse,
    TenantSmtpSettingsUpdate,
    TenantSmtpTestRequest,
    TenantSmtpTestResponse,
)
from app.schemas.whatsapp_settings import (
    TenantWhatsappActionResponse,
    TenantWhatsappConnectRequest,
    TenantWhatsappStatusResponse,
    TenantWhatsappTestRequest,
    TenantWhatsappTestResponse,
)
from app.services import tenant_service
from app.services import smtp_settings_service
from app.services import whatsapp_gateway_service

router = APIRouter()


@router.get("/current", response_model=TenantResponse)
def get_current_tenant_profile(
    _user: User = Depends(require_users_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantResponse:
    return current_tenant


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> TenantResponse:
    try:
        return tenant_service.create_tenant(db, payload, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/current", response_model=TenantResponse)
def update_current_tenant_profile(
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_users_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantResponse:
    try:
        return tenant_service.update_tenant(db, current_tenant, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/current/logo", response_model=TenantResponse)
async def upload_current_tenant_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_users_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantResponse:
    content_type = (file.content_type or "").lower()
    if content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PNG, JPEG or WEBP images are supported")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file upload")
    if len(raw) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds maximum upload size")

    extension = ".png"
    if content_type == "image/jpeg":
        extension = ".jpg"
    elif content_type == "image/webp":
        extension = ".webp"

    target_dir = Path(settings.TENANT_LOGO_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"tenant-{current_tenant.id}-{uuid4().hex}{extension}"
    target_path = target_dir / filename
    target_path.write_bytes(raw)

    previous_logo_url = current_tenant.logo_url
    current_tenant.logo_url = f"/media/tenant-logos/{filename}"
    db.commit()
    db.refresh(current_tenant)
    if previous_logo_url != current_tenant.logo_url:
        tenant_service._remove_local_logo_if_managed(previous_logo_url)
    return current_tenant


@router.get("/current/payments", response_model=TenantPaymentSettingsResponse)
def get_current_tenant_payment_settings(
    _user: User = Depends(require_users_read),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantPaymentSettingsResponse:
    return tenant_service.build_payment_settings_response(current_tenant)


@router.put("/current/payments", response_model=TenantPaymentSettingsResponse)
def update_current_tenant_payment_settings(
    payload: TenantPaymentSettingsUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_users_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantPaymentSettingsResponse:
    try:
        tenant = tenant_service.update_tenant_payment_settings(db, current_tenant, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return tenant_service.build_payment_settings_response(tenant)


@router.get("/current/smtp", response_model=TenantSmtpSettingsResponse)
def get_current_tenant_smtp_settings(
    _user: User = Depends(require_users_read),
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantSmtpSettingsResponse:
    cfg = smtp_settings_service.get_tenant_smtp_settings(db, current_tenant.id)
    if cfg is None:
        return TenantSmtpSettingsResponse()
    return TenantSmtpSettingsResponse(
        host=cfg.host,
        port=int(cfg.port or 587),
        username=cfg.username,
        from_email=cfg.from_email,
        encryption=(cfg.encryption or "tls"),
        is_active=bool(cfg.is_active),
        has_password=bool(cfg.password),
    )


@router.put("/current/smtp", response_model=TenantSmtpSettingsResponse)
def update_current_tenant_smtp_settings(
    payload: TenantSmtpSettingsUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_users_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantSmtpSettingsResponse:
    cfg = smtp_settings_service.upsert_tenant_smtp_settings(
        db,
        tenant_id=current_tenant.id,
        host=payload.host,
        port=payload.port,
        username=payload.username,
        password=payload.password,
        from_email=str(payload.from_email) if payload.from_email else None,
        encryption=payload.encryption,
        is_active=payload.is_active,
    )
    return TenantSmtpSettingsResponse(
        host=cfg.host,
        port=int(cfg.port or 587),
        username=cfg.username,
        from_email=cfg.from_email,
        encryption=(cfg.encryption or "tls"),
        is_active=bool(cfg.is_active),
        has_password=bool(cfg.password),
    )


@router.post("/current/smtp/test", response_model=TenantSmtpTestResponse)
def test_current_tenant_smtp_settings(
    payload: TenantSmtpTestRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_users_write),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantSmtpTestResponse:
    try:
        smtp_settings_service.send_test_email(db, current_tenant.id, to_email=str(payload.to_email))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TenantSmtpTestResponse(status="sent", message="E-mail de teste enviado.")


@router.get("/current/whatsapp", response_model=TenantWhatsappStatusResponse)
def get_current_tenant_whatsapp_status(
    _user: User = Depends(require_users_read),
    _current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantWhatsappStatusResponse:
    try:
        return TenantWhatsappStatusResponse(**whatsapp_gateway_service.get_status())
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/current/whatsapp/setup", response_model=TenantWhatsappActionResponse)
def setup_current_tenant_whatsapp(
    _admin: User = Depends(require_users_write),
    _current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantWhatsappActionResponse:
    try:
        result = whatsapp_gateway_service.setup_instance()
        status_payload = result.get("status") if isinstance(result, dict) else None
        return TenantWhatsappActionResponse(
            accepted=True,
            message="Instância do WhatsApp preparada com sucesso.",
            response=result,
            status=TenantWhatsappStatusResponse(**status_payload) if isinstance(status_payload, dict) else None,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/current/whatsapp/connect", response_model=TenantWhatsappActionResponse)
def connect_current_tenant_whatsapp(
    payload: TenantWhatsappConnectRequest,
    _admin: User = Depends(require_users_write),
    _current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantWhatsappActionResponse:
    try:
        result = whatsapp_gateway_service.connect_instance(payload.number)
        status_payload = result.get("status") if isinstance(result, dict) else None
        return TenantWhatsappActionResponse(
            accepted=True,
            message="Solicitação de QR Code enviada.",
            response=result,
            status=TenantWhatsappStatusResponse(**status_payload) if isinstance(status_payload, dict) else None,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/current/whatsapp/logout", response_model=TenantWhatsappActionResponse)
def logout_current_tenant_whatsapp(
    _admin: User = Depends(require_users_write),
    _current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantWhatsappActionResponse:
    try:
        result = whatsapp_gateway_service.logout_instance()
        status_payload = result.get("status") if isinstance(result, dict) else None
        return TenantWhatsappActionResponse(
            accepted=True,
            message="Instância do WhatsApp desconectada.",
            response=result,
            status=TenantWhatsappStatusResponse(**status_payload) if isinstance(status_payload, dict) else None,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/current/whatsapp/test", response_model=TenantWhatsappTestResponse)
def test_current_tenant_whatsapp(
    payload: TenantWhatsappTestRequest,
    _admin: User = Depends(require_users_write),
    _current_tenant: Tenant = Depends(get_current_tenant),
) -> TenantWhatsappTestResponse:
    try:
        result = whatsapp_gateway_service.send_test_message(payload.to_phone)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    response_payload = result if isinstance(result, dict) else {}
    return TenantWhatsappTestResponse(
        accepted=bool(response_payload.get("accepted", True)),
        message="Mensagem de teste enviada com sucesso.",
        recipient=str(response_payload.get("recipient") or payload.to_phone),
        provider=str(response_payload["provider"]) if response_payload.get("provider") else None,
        gateway_message_id=str(response_payload["gateway_message_id"]) if response_payload.get("gateway_message_id") else None,
    )


@router.get("/public/{tenant_slug}/branding", response_model=TenantBrandingResponse)
def get_public_tenant_branding(
    tenant_slug: str,
    db: Session = Depends(get_db),
) -> TenantBrandingResponse:
    tenant = tenant_service.resolve_public_tenant(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant
