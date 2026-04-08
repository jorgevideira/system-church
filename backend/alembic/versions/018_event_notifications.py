"""Add event notifications outbox

Revision ID: 018
Revises: 017
Create Date: 2026-04-08 16:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("registration_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("template_key", sa.String(length=50), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("external_reference", sa.String(length=120), nullable=True),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["registration_id"], ["event_registrations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_notifications_id", "event_notifications", ["id"])
    op.create_index("ix_event_notifications_tenant_id", "event_notifications", ["tenant_id"])
    op.create_index("ix_event_notifications_event_id", "event_notifications", ["event_id"])
    op.create_index("ix_event_notifications_registration_id", "event_notifications", ["registration_id"])
    op.create_index("ix_event_notifications_channel", "event_notifications", ["channel"])
    op.create_index("ix_event_notifications_template_key", "event_notifications", ["template_key"])
    op.create_index("ix_event_notifications_recipient", "event_notifications", ["recipient"])
    op.create_index("ix_event_notifications_status", "event_notifications", ["status"])
    op.create_index("ix_event_notifications_external_reference", "event_notifications", ["external_reference"])


def downgrade() -> None:
    op.drop_index("ix_event_notifications_external_reference", table_name="event_notifications")
    op.drop_index("ix_event_notifications_status", table_name="event_notifications")
    op.drop_index("ix_event_notifications_recipient", table_name="event_notifications")
    op.drop_index("ix_event_notifications_template_key", table_name="event_notifications")
    op.drop_index("ix_event_notifications_channel", table_name="event_notifications")
    op.drop_index("ix_event_notifications_registration_id", table_name="event_notifications")
    op.drop_index("ix_event_notifications_event_id", table_name="event_notifications")
    op.drop_index("ix_event_notifications_tenant_id", table_name="event_notifications")
    op.drop_index("ix_event_notifications_id", table_name="event_notifications")
    op.drop_table("event_notifications")
