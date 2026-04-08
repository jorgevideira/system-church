from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db, require_admin
from app.core.config import settings
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.tenant import TenantBrandingResponse, TenantCreate, TenantResponse, TenantUpdate
from app.services import tenant_service

router = APIRouter()


@router.get("/current", response_model=TenantResponse)
def get_current_tenant_profile(
    _user: User = Depends(get_current_active_user),
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
    _admin: User = Depends(require_admin),
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
    _admin: User = Depends(require_admin),
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


@router.get("/public/{tenant_slug}/branding", response_model=TenantBrandingResponse)
def get_public_tenant_branding(
    tenant_slug: str,
    db: Session = Depends(get_db),
) -> TenantBrandingResponse:
    tenant = tenant_service.get_tenant_by_slug(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant
