"""Payable reminder notifications

Revision ID: 025_payable_notifications
Revises: 024_event_checkins_and_smtp_settings
Create Date: 2026-04-15
"""

from alembic import op
import sqlalchemy as sa


revision = "025_payable_notifications"
down_revision = "024_event_checkins_and_smtp_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "payable_notifications" not in tables:
        op.create_table(
            "payable_notifications",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=True),
            sa.Column("payable_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("channel", sa.String(length=20), nullable=False, server_default="email"),
            sa.Column("template_key", sa.String(length=50), nullable=False),
            sa.Column("recipient", sa.String(length=255), nullable=False),
            sa.Column("trigger_date", sa.Date(), nullable=False),
            sa.Column("due_date_snapshot", sa.Date(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("error_message", sa.String(length=500), nullable=True),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["payable_id"], ["payables.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "payable_id",
                "channel",
                "template_key",
                "trigger_date",
                "recipient",
                name="uq_payable_notifications_dispatch",
            ),
        )
        op.create_index("ix_payable_notifications_id", "payable_notifications", ["id"])
        op.create_index("ix_payable_notifications_tenant_id", "payable_notifications", ["tenant_id"])
        op.create_index("ix_payable_notifications_payable_id", "payable_notifications", ["payable_id"])
        op.create_index("ix_payable_notifications_user_id", "payable_notifications", ["user_id"])
        op.create_index("ix_payable_notifications_channel", "payable_notifications", ["channel"])
        op.create_index("ix_payable_notifications_template_key", "payable_notifications", ["template_key"])
        op.create_index("ix_payable_notifications_recipient", "payable_notifications", ["recipient"])
        op.create_index("ix_payable_notifications_trigger_date", "payable_notifications", ["trigger_date"])
        op.create_index("ix_payable_notifications_due_date_snapshot", "payable_notifications", ["due_date_snapshot"])
        op.create_index("ix_payable_notifications_status", "payable_notifications", ["status"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "payable_notifications" in tables:
        for ix in [
            "ix_payable_notifications_status",
            "ix_payable_notifications_due_date_snapshot",
            "ix_payable_notifications_trigger_date",
            "ix_payable_notifications_recipient",
            "ix_payable_notifications_template_key",
            "ix_payable_notifications_channel",
            "ix_payable_notifications_user_id",
            "ix_payable_notifications_payable_id",
            "ix_payable_notifications_tenant_id",
            "ix_payable_notifications_id",
        ]:
            op.drop_index(ix, table_name="payable_notifications")
        op.drop_table("payable_notifications")
