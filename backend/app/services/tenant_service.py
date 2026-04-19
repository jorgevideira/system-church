import re
import unicodedata
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.core.config import settings
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.tenant import TenantCreate
from app.schemas.tenant import TenantPaymentSettingsResponse, TenantPaymentSettingsUpdate
from app.schemas.tenant import TenantUpdate
from app.services import secret_service


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "tenant"


def _remove_local_logo_if_managed(logo_url: str | None) -> None:
    if not logo_url or not logo_url.startswith("/media/tenant-logos/"):
        return
    filename = logo_url.rsplit("/", 1)[-1].strip()
    if not filename:
        return
    target = Path(settings.TENANT_LOGO_DIR) / filename
    try:
        if target.exists():
            target.unlink()
    except OSError:
        return


def get_tenant(db: Session, tenant_id: int) -> Optional[Tenant]:
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()


def get_tenant_by_slug(db: Session, slug: str) -> Optional[Tenant]:
    return db.query(Tenant).filter(Tenant.slug == slug, Tenant.is_active.is_(True)).first()


def resolve_public_tenant(db: Session, tenant_slug: str) -> Optional[Tenant]:
    """
    Resolve the tenant for public (unauthenticated) pages.

    The frontend defaults to the slug "default" on first visit. In single-tenant
    deployments that slug may not exist (e.g. "videira-sertaozinho"), which
    breaks branding/logo loading. To keep the UX smooth, we fallback to the only
    active tenant when and only when there is exactly one.
    """
    def has_branding(tenant: Tenant) -> bool:
        return bool(
            tenant.public_display_name
            or tenant.logo_url
            or tenant.public_description
            or tenant.support_email
            or tenant.support_whatsapp
            or tenant.primary_color
            or tenant.secondary_color
        )

    normalized = str(tenant_slug or "").strip()
    if normalized:
        tenant = get_tenant_by_slug(db, normalized)
        if tenant is not None:
            # Many installs end up with a placeholder "Default Church" tenant
            # with slug "default" and no branding, while the real tenant has a
            # different slug. If the request asks for "default", prefer the
            # real tenant when it is unambiguous.
            if normalized == "default":
                name_key = str(tenant.name or "").strip().lower()
                is_placeholder = name_key in {"default church", "default tenant", "default"} and not has_branding(tenant)
                if is_placeholder:
                    others = (
                        db.query(Tenant)
                        .filter(Tenant.is_active.is_(True), Tenant.id != tenant.id)
                        .order_by(Tenant.id.asc())
                        .all()
                    )
                    if len(others) == 1:
                        return others[0]
                    branded = [row for row in others if has_branding(row)]
                    if len(branded) == 1:
                        return branded[0]
                    if branded:
                        return branded[0]
            return tenant

    if normalized not in {"", "default"}:
        return None

    tenants = (
        db.query(Tenant)
        .filter(Tenant.is_active.is_(True))
        .order_by(Tenant.id.asc())
        .all()
    )
    if len(tenants) == 1:
        return tenants[0]
    return None


def get_payment_provider(tenant: Tenant | None) -> str:
    provider = ""
    if tenant is not None:
        provider = str(tenant.payment_provider or "").strip().lower()
    if not provider:
        provider = str(settings.PAYMENT_PROVIDER or "internal").strip().lower()
    return provider or "internal"


def get_mercadopago_access_token(tenant: Tenant | None) -> str | None:
    if tenant is not None and tenant.mercadopago_access_token:
        return secret_service.decrypt_value(tenant.mercadopago_access_token)
    return settings.MERCADOPAGO_ACCESS_TOKEN


def get_mercadopago_public_key(tenant: Tenant | None) -> str | None:
    if tenant is not None and tenant.mercadopago_public_key:
        return tenant.mercadopago_public_key.strip()
    return settings.MERCADOPAGO_PUBLIC_KEY


def get_mercadopago_webhook_secret(tenant: Tenant | None) -> str | None:
    if tenant is not None and tenant.mercadopago_webhook_secret:
        return secret_service.decrypt_value(tenant.mercadopago_webhook_secret)
    return settings.MERCADOPAGO_WEBHOOK_SECRET


def get_mercadopago_integrator_id(tenant: Tenant | None) -> str | None:
    if tenant is not None and tenant.mercadopago_integrator_id:
        return tenant.mercadopago_integrator_id.strip()
    return settings.MERCADOPAGO_INTEGRATOR_ID


def build_payment_settings_response(tenant: Tenant) -> TenantPaymentSettingsResponse:
    provider = get_payment_provider(tenant)
    access_token = get_mercadopago_access_token(tenant)
    public_key = get_mercadopago_public_key(tenant)
    webhook_secret = get_mercadopago_webhook_secret(tenant)
    integrator_id = get_mercadopago_integrator_id(tenant)
    live_ready = provider == "mercadopago" and bool(access_token) and bool(public_key)
    return TenantPaymentSettingsResponse(
        payment_provider=provider,
        payment_pix_enabled=bool(tenant.payment_pix_enabled),
        payment_card_enabled=bool(tenant.payment_card_enabled),
        mercadopago_public_key=public_key,
        mercadopago_integrator_id=integrator_id,
        mercadopago_access_token_configured=bool(access_token),
        mercadopago_webhook_secret_configured=bool(webhook_secret),
        mercadopago_live_ready=live_ready,
        checkout_mode="live" if live_ready else "internal",
    )


def create_tenant(db: Session, payload: TenantCreate, current_user: User) -> Tenant:
    name = payload.name.strip()
    slug = _slugify(payload.slug)

    existing_name = db.query(Tenant.id).filter(Tenant.name == name).first()
    if existing_name is not None:
        raise ValueError("Tenant name is already in use")

    existing_slug = db.query(Tenant.id).filter(Tenant.slug == slug).first()
    if existing_slug is not None:
        raise ValueError("Tenant slug is already in use")

    for color_field in ("primary_color", "secondary_color"):
        color_value = getattr(payload, color_field, None)
        if color_value and not HEX_COLOR_RE.match(color_value):
            raise ValueError(f"{color_field} must be a hex color like #1565C0")

    tenant = Tenant(
        name=name,
        slug=slug,
        public_display_name=payload.public_display_name,
        public_description=payload.public_description,
        primary_color=payload.primary_color,
        secondary_color=payload.secondary_color,
        logo_url=payload.logo_url,
        support_email=payload.support_email,
        support_whatsapp=payload.support_whatsapp,
        landing_hero_background_url=payload.landing_hero_background_url,
        landing_pix_key=payload.landing_pix_key,
        landing_bank_name=payload.landing_bank_name,
        landing_bank_agency=payload.landing_bank_agency,
        landing_bank_account=payload.landing_bank_account,
        landing_service_times=payload.landing_service_times,
        landing_address=payload.landing_address,
        landing_location_url=payload.landing_location_url,
        landing_footer_text=payload.landing_footer_text,
        is_active=True,
    )
    db.add(tenant)
    db.flush()

    membership = TenantMembership(
        user_id=current_user.id,
        tenant_id=tenant.id,
        role=ROLE_ADMIN,
        role_id=current_user.role_id,
        is_active=True,
        is_default=False,
    )
    db.add(membership)
    db.commit()
    db.refresh(tenant)
    return tenant


def update_tenant(db: Session, tenant: Tenant, payload: TenantUpdate) -> Tenant:
    changes = payload.model_dump(exclude_unset=True)
    previous_logo_url = tenant.logo_url

    if "slug" in changes and changes["slug"]:
        changes["slug"] = _slugify(changes["slug"])
    elif "name" in changes and changes["name"] and not tenant.slug:
        changes["slug"] = _slugify(changes["name"])

    for color_field in ("primary_color", "secondary_color"):
        color_value = changes.get(color_field)
        if color_value:
            if not HEX_COLOR_RE.match(color_value):
                raise ValueError(f"{color_field} must be a hex color like #1565C0")

    if "name" in changes and changes["name"]:
        existing_name = db.query(Tenant.id).filter(Tenant.name == changes["name"], Tenant.id != tenant.id).first()
        if existing_name is not None:
            raise ValueError("Tenant name is already in use")

    if "slug" in changes and changes["slug"]:
        existing_slug = db.query(Tenant.id).filter(Tenant.slug == changes["slug"], Tenant.id != tenant.id).first()
        if existing_slug is not None:
            raise ValueError("Tenant slug is already in use")

    for field, value in changes.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)
    if "logo_url" in changes and changes["logo_url"] != previous_logo_url:
        _remove_local_logo_if_managed(previous_logo_url)
    return tenant


def update_tenant_payment_settings(db: Session, tenant: Tenant, payload: TenantPaymentSettingsUpdate) -> Tenant:
    provider = payload.payment_provider if payload.payment_provider is not None else tenant.payment_provider
    normalized_provider = str(provider or "internal").strip().lower()
    if normalized_provider not in {"internal", "mercadopago"}:
        raise ValueError("payment_provider must be internal or mercadopago")

    tenant.payment_provider = normalized_provider
    if payload.payment_pix_enabled is not None:
        tenant.payment_pix_enabled = bool(payload.payment_pix_enabled)
    if payload.payment_card_enabled is not None:
        tenant.payment_card_enabled = bool(payload.payment_card_enabled)

    if payload.mercadopago_public_key is not None:
        tenant.mercadopago_public_key = payload.mercadopago_public_key.strip() or None
    if payload.mercadopago_integrator_id is not None:
        tenant.mercadopago_integrator_id = payload.mercadopago_integrator_id.strip() or None
    if payload.clear_mercadopago_access_token:
        tenant.mercadopago_access_token = None
    elif payload.mercadopago_access_token is not None:
        tenant.mercadopago_access_token = secret_service.encrypt_value(payload.mercadopago_access_token.strip() or None)
    if payload.clear_mercadopago_webhook_secret:
        tenant.mercadopago_webhook_secret = None
    elif payload.mercadopago_webhook_secret is not None:
        tenant.mercadopago_webhook_secret = secret_service.encrypt_value(payload.mercadopago_webhook_secret.strip() or None)

    db.commit()
    db.refresh(tenant)
    return tenant
