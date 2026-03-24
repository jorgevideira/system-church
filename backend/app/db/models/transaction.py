from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "income" | "expense"
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    bank_account_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("bank_accounts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statement_file_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("statement_files.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(String(20), default="confirmed", nullable=False)

    # AI categorization fields
    ai_category_suggestion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_suggested_category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Nullable unique hash used for import deduplication
    hash: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)

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

    # Relationships
    category: Mapped["Category"] = relationship(  # noqa: F821
        "Category",
        back_populates="transactions",
        foreign_keys=[category_id],
    )
    ai_suggested_category: Mapped["Category | None"] = relationship(  # noqa: F821
        "Category",
        foreign_keys=[ai_suggested_category_id],
    )
    bank_account: Mapped["BankAccount | None"] = relationship(  # noqa: F821
        "BankAccount",
        back_populates="transactions",
    )
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        back_populates="transactions",
        foreign_keys=[user_id],
    )
    statement_file: Mapped["StatementFile | None"] = relationship(  # noqa: F821
        "StatementFile",
        back_populates="transactions",
    )

    __table_args__ = (
        UniqueConstraint("hash", name="uq_transaction_hash"),
    )
