from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_categories_tenant_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # "income" | "expense" | "both"
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="both")
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)   # hex, e.g. "#4CAF50"
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction",
        back_populates="category",
        foreign_keys="Transaction.category_id",
    )
