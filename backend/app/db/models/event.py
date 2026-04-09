from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_events_tenant_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_by_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_account_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("payment_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone_name: Mapped[str] = mapped_column(String(80), nullable=False, default="America/Sao_Paulo")
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="public", index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    registration_opens_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    registration_closes_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_registrations_per_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price_per_registration: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="BRL")
    allow_public_registration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    require_payment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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
