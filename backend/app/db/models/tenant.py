from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.db.models.tenant_membership import TenantMembership
    from app.db.models.user import User


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    public_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    public_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    secondary_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    support_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    support_whatsapp: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="internal")
    payment_pix_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    payment_card_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mercadopago_access_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mercadopago_public_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mercadopago_webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mercadopago_integrator_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    memberships: Mapped[list["TenantMembership"]] = relationship(
        "TenantMembership",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    active_users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="active_tenant",
        foreign_keys="User.active_tenant_id",
    )
