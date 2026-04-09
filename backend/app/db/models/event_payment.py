from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class EventPayment(Base):
    __tablename__ = "event_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    registration_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("event_registrations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_account_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("payment_accounts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    transaction_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(30), nullable=False, default="internal")
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="BRL")
    checkout_reference: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    checkout_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pix_copy_paste: Mapped[str | None] = mapped_column(String(500), nullable=True)
    provider_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
