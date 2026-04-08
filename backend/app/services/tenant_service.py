import re
import unicodedata
from typing import Optional

from sqlalchemy.orm import Session

from app.core.constants import ROLE_ADMIN
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.tenant import TenantCreate
from app.schemas.tenant import TenantUpdate


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "tenant"


def get_tenant(db: Session, tenant_id: int) -> Optional[Tenant]:
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()


def get_tenant_by_slug(db: Session, slug: str) -> Optional[Tenant]:
    return db.query(Tenant).filter(Tenant.slug == slug, Tenant.is_active.is_(True)).first()


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
    return tenant
