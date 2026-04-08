from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class CellVisitor(Base):
    __tablename__ = "cell_visitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact: Mapped[str | None] = mapped_column(String(120), nullable=True)
    count_start_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today, index=True)

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
