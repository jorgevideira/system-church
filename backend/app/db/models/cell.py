from datetime import datetime, time, timezone

from sqlalchemy import DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Cell(Base):
    __tablename__ = "cells"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weekday: Mapped[str] = mapped_column(String(20), nullable=False)
    meeting_time: Mapped[time] = mapped_column(Time, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)

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
