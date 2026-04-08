from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class BibleSchoolLesson(Base):
    __tablename__ = "bible_school_lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    class_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bible_school_classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    professor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("bible_school_professors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    lesson_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled", index=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

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
