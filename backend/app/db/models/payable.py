from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Payable(Base):
    __tablename__ = "payables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    ministry_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ministries.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    payment_transaction_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True, unique=True, index=True
    )

    source_bank_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    expense_profile: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "fixed" | "variable"
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "pix" | "boleto" | "cash"

    attachment_storage_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    paid_at: Mapped[date | None] = mapped_column(Date, nullable=True)

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

    category: Mapped["Category | None"] = relationship("Category")  # noqa: F821
    ministry: Mapped["Ministry | None"] = relationship("Ministry")  # noqa: F821
    user: Mapped["User"] = relationship("User")  # noqa: F821
    payment_transaction: Mapped["Transaction | None"] = relationship("Transaction")  # noqa: F821
