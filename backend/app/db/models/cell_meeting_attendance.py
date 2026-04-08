from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class CellMeetingAttendance(Base):
    __tablename__ = "cell_meeting_attendances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cell_meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cell_members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attendance_status: Mapped[str] = mapped_column(String(20), nullable=False, default="present")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

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
