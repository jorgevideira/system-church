from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.db.models.audit_log import AuditLog
    from app.db.models.role import Role
    from app.db.models.tenant import Tenant
    from app.db.models.tenant_membership import TenantMembership
    from app.db.models.transaction import Transaction


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)      
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)   
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)   
    role: Mapped[str] = mapped_column(String(50), default="viewer", nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    active_tenant_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
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

    role_obj: Mapped["Role"] = relationship(  # noqa: F821
        "Role",
        back_populates="users",
        foreign_keys=[role_id],
    )
    active_tenant: Mapped["Tenant | None"] = relationship(  # noqa: F821
        "Tenant",
        back_populates="active_users",
        foreign_keys=[active_tenant_id],
    )
    tenant_memberships: Mapped[list["TenantMembership"]] = relationship(  # noqa: F821
        "TenantMembership",
        back_populates="user",
        foreign_keys="TenantMembership.user_id",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction",
        back_populates="user",
        foreign_keys="Transaction.user_id",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(  # noqa: F821
        "AuditLog",
        back_populates="user",
    )
