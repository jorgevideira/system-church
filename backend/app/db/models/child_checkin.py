from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ChildCheckinFamily(Base):
    __tablename__ = "child_checkin_families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    family_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    primary_responsible_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    secondary_responsible_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_primary: Mapped[str | None] = mapped_column(String(40), nullable=True)
    phone_secondary: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    family_code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    # Optional PIN for "Kids App" (public) login/reuse. Stored as bcrypt hash.
    public_pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Temporary recovery code for PIN reset (stored as bcrypt hash).
    public_reset_code_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    public_reset_code_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ChildCheckinChild(Base):
    __tablename__ = "child_checkin_children"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("child_checkin_families.id", ondelete="CASCADE"), index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    age_group: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    room_name: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_restrictions: Mapped[str | None] = mapped_column(Text, nullable=True)
    special_needs: Mapped[str | None] = mapped_column(Text, nullable=True)
    behavioral_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_visitor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ChildCheckinGuardian(Base):
    __tablename__ = "child_checkin_guardians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("child_checkin_families.id", ondelete="CASCADE"), index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_authorized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ChildCheckinRecord(Base):
    __tablename__ = "child_checkin_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("child_checkin_families.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[int] = mapped_column(Integer, ForeignKey("child_checkin_children.id", ondelete="CASCADE"), index=True)
    context_type: Mapped[str] = mapped_column(String(20), nullable=False, default="culto", index=True)
    context_name: Mapped[str] = mapped_column(String(255), nullable=False)
    room_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    checkin_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    checkout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    checked_in_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    checked_out_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    accompanied_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pickup_guardian_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("child_checkin_guardians.id", ondelete="SET NULL"), nullable=True)
    pickup_person_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    security_code: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    qr_token: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="checked_in", index=True)
    alert_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    exception_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    manual_override_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ChildCheckinAudit(Base):
    __tablename__ = "child_checkin_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    record_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("child_checkin_records.id", ondelete="CASCADE"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    performed_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)


class ChildCheckinNotification(Base):
    __tablename__ = "child_checkin_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    family_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("child_checkin_families.id", ondelete="SET NULL"), nullable=True, index=True)
    child_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("child_checkin_children.id", ondelete="SET NULL"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default="email")
    message_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued", index=True)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)


class ChildCheckinRoomScope(Base):
    __tablename__ = "child_checkin_room_scopes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    room_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ChildCheckinRoom(Base):
    __tablename__ = "child_checkin_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    age_range_label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Room rules for auto-assignment by birth date (months).
    min_age_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_age_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Optional capacity limit enforced at check-in time (active check-ins in room).
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ChildCheckinSettings(Base):
    __tablename__ = "child_checkin_settings"
    __table_args__ = (UniqueConstraint("tenant_id", name="uq_child_checkin_settings_tenant"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    # JSON text: list of presets for the Ops screen (label + context_name).
    ops_context_presets_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
