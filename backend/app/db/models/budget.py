from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM
    budget_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "category" or "ministry"
    reference_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # category_id or ministry_id
    target_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    alert_threshold_percent: Mapped[int] = mapped_column(Integer, default=80)  # Alert when 80% spent
    
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

    user: Mapped["User"] = relationship("User")  # noqa: F821
