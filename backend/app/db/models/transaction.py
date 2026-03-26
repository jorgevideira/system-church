from datetime import date, datetime, timezone
from decimal import Decimal
import re

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Numeric, String
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
    ministry_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ministries.id", ondelete="SET NULL"), nullable=True, index=True
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
    source_bank_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    expense_profile: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "fixed" | "variable"
    # Nullable unique hash used for import deduplication
    dedup_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)

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
    ministry: Mapped["Ministry | None"] = relationship(  # noqa: F821
        "Ministry",
        back_populates="transactions",
        foreign_keys=[ministry_id],
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
    attachments: Mapped[list["TransactionAttachment"]] = relationship(  # noqa: F821
        "TransactionAttachment",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )

    __table_args__ = ()

    @property
    def source_bank(self) -> str | None:
        """Best-effort bank source for UI display."""
        if self.source_bank_name:
            return self.source_bank_name
        if self.bank_account and getattr(self.bank_account, "name", None):
            return self.bank_account.name

        original_filename = ""
        if self.statement_file and getattr(self.statement_file, "original_filename", None):
            original_filename = self.statement_file.original_filename

        lower_name = original_filename.lower()
        if "pagseguro" in lower_name:
            return "PagSeguro"
        if "bradesco" in lower_name:
            return "Bradesco"
        if "itau" in lower_name or "itaú" in lower_name:
            return "Itau"
        if "santander" in lower_name:
            return "Santander"
        if "caixa" in lower_name:
            return "Caixa"
        if "nubank" in lower_name:
            return "Nubank"
        if "banco do brasil" in lower_name or re.search(r"\bbb\b", lower_name):
            return "Banco do Brasil"

        return None

    @property
    def attachment_count(self) -> int:
        return len(self.attachments or [])

    @property
    def has_attachments(self) -> bool:
        return self.attachment_count > 0
