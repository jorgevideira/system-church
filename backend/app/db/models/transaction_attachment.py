from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.db.models.transaction import Transaction
    from app.db.models.user import User


class TransactionAttachment(Base):
    __tablename__ = "transaction_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    storage_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    original_size: Mapped[int] = mapped_column(Integer, nullable=False)
    compressed_size: Mapped[int] = mapped_column(Integer, nullable=False)
    compression: Mapped[str] = mapped_column(String(20), nullable=False, default="gzip")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    transaction: Mapped["Transaction"] = relationship(  # noqa: F821
        "Transaction",
        back_populates="attachments",
    )
    user: Mapped["User"] = relationship("User")  # noqa: F821
