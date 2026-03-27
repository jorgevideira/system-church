from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.db.models.category import Category
    from app.db.models.user import User


class ClassificationFeedback(Base):
    __tablename__ = "classification_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    keyword: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    transaction_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

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

    user: Mapped["User"] = relationship("User")
    category: Mapped["Category | None"] = relationship("Category")

    __table_args__ = (
        UniqueConstraint("user_id", "keyword", "category_id", "transaction_type", name="uq_feedback_rule"),
    )
