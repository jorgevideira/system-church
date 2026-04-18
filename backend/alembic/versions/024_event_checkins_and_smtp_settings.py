"""Event check-ins and tenant SMTP settings

Revision ID: 024_event_checkins_and_smtp_settings
Revises: 023_tenant_landing_page_settings
Create Date: 2026-04-14
"""

from alembic import op
import sqlalchemy as sa


revision = "024_event_checkins_and_smtp_settings"
down_revision = "023_tenant_landing_page_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "tenant_smtp_settings" not in tables:
        op.create_table(
            "tenant_smtp_settings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("host", sa.String(length=255), nullable=False),
            sa.Column("port", sa.Integer(), nullable=False, server_default="587"),
            sa.Column("username", sa.String(length=255), nullable=True),
            sa.Column("password", sa.String(length=1024), nullable=True),
            sa.Column("from_email", sa.String(length=255), nullable=True),
            sa.Column("encryption", sa.String(length=10), nullable=False, server_default="tls"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", name="uq_tenant_smtp_settings_tenant"),
        )
        op.create_index("ix_tenant_smtp_settings_id", "tenant_smtp_settings", ["id"])
        op.create_index("ix_tenant_smtp_settings_tenant_id", "tenant_smtp_settings", ["tenant_id"])

    if "event_checkins" not in tables:
        op.create_table(
            "event_checkins",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=True),
            sa.Column("event_id", sa.Integer(), nullable=False),
            sa.Column("registration_id", sa.Integer(), nullable=False),
            sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("checked_in_by_user_id", sa.Integer(), nullable=True),
            sa.Column("source", sa.String(length=20), nullable=False, server_default="qr"),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["registration_id"], ["event_registrations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["checked_in_by_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("registration_id", name="uq_event_checkins_registration"),
        )
        op.create_index("ix_event_checkins_id", "event_checkins", ["id"])
        op.create_index("ix_event_checkins_tenant_id", "event_checkins", ["tenant_id"])
        op.create_index("ix_event_checkins_event_id", "event_checkins", ["event_id"])
        op.create_index("ix_event_checkins_registration_id", "event_checkins", ["registration_id"])
        op.create_index("ix_event_checkins_checked_in_at", "event_checkins", ["checked_in_at"])
        op.create_index("ix_event_checkins_checked_in_by_user_id", "event_checkins", ["checked_in_by_user_id"])

    if "event_checkin_attempts" not in tables:
        op.create_table(
            "event_checkin_attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=True),
            sa.Column("event_id", sa.Integer(), nullable=True),
            sa.Column("registration_id", sa.Integer(), nullable=True),
            sa.Column("checked_in_by_user_id", sa.Integer(), nullable=True),
            sa.Column("token_hash", sa.String(length=128), nullable=True),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("error_message", sa.String(length=500), nullable=True),
            sa.Column("ip_address", sa.String(length=64), nullable=True),
            sa.Column("user_agent", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["registration_id"], ["event_registrations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["checked_in_by_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_event_checkin_attempts_id", "event_checkin_attempts", ["id"])
        op.create_index("ix_event_checkin_attempts_tenant_id", "event_checkin_attempts", ["tenant_id"])
        op.create_index("ix_event_checkin_attempts_event_id", "event_checkin_attempts", ["event_id"])
        op.create_index("ix_event_checkin_attempts_registration_id", "event_checkin_attempts", ["registration_id"])
        op.create_index("ix_event_checkin_attempts_checked_in_by_user_id", "event_checkin_attempts", ["checked_in_by_user_id"])
        op.create_index("ix_event_checkin_attempts_token_hash", "event_checkin_attempts", ["token_hash"])
        op.create_index("ix_event_checkin_attempts_status", "event_checkin_attempts", ["status"])
        op.create_index("ix_event_checkin_attempts_created_at", "event_checkin_attempts", ["created_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "event_checkin_attempts" in tables:
        for ix in [
            "ix_event_checkin_attempts_created_at",
            "ix_event_checkin_attempts_status",
            "ix_event_checkin_attempts_token_hash",
            "ix_event_checkin_attempts_checked_in_by_user_id",
            "ix_event_checkin_attempts_registration_id",
            "ix_event_checkin_attempts_event_id",
            "ix_event_checkin_attempts_tenant_id",
            "ix_event_checkin_attempts_id",
        ]:
            op.drop_index(ix, table_name="event_checkin_attempts")
        op.drop_table("event_checkin_attempts")

    if "event_checkins" in tables:
        for ix in [
            "ix_event_checkins_checked_in_by_user_id",
            "ix_event_checkins_checked_in_at",
            "ix_event_checkins_registration_id",
            "ix_event_checkins_event_id",
            "ix_event_checkins_tenant_id",
            "ix_event_checkins_id",
        ]:
            op.drop_index(ix, table_name="event_checkins")
        op.drop_table("event_checkins")

    if "tenant_smtp_settings" in tables:
        for ix in ["ix_tenant_smtp_settings_tenant_id", "ix_tenant_smtp_settings_id"]:
            op.drop_index(ix, table_name="tenant_smtp_settings")
        op.drop_table("tenant_smtp_settings")

