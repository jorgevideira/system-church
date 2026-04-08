"""Add events, registrations and payment domain

Revision ID: 017
Revises: 016
Create Date: 2026-04-08 13:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=True),
        sa.Column("description", sa.String(length=4000), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("timezone_name", sa.String(length=80), nullable=False, server_default="America/Sao_Paulo"),
        sa.Column("visibility", sa.String(length=20), nullable=False, server_default="public"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registration_opens_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("registration_closes_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("max_registrations_per_order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("price_per_registration", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="BRL"),
        sa.Column("allow_public_registration", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("require_payment", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_events_tenant_slug"),
    )
    op.create_index("ix_events_id", "events", ["id"])
    op.create_index("ix_events_tenant_id", "events", ["tenant_id"])
    op.create_index("ix_events_created_by_user_id", "events", ["created_by_user_id"])
    op.create_index("ix_events_title", "events", ["title"])
    op.create_index("ix_events_slug", "events", ["slug"])
    op.create_index("ix_events_status", "events", ["status"])
    op.create_index("ix_events_visibility", "events", ["visibility"])
    op.create_index("ix_events_start_at", "events", ["start_at"])
    op.create_index("ix_events_end_at", "events", ["end_at"])

    op.create_table(
        "event_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("registration_code", sa.String(length=32), nullable=False),
        sa.Column("public_token", sa.String(length=64), nullable=False),
        sa.Column("attendee_name", sa.String(length=255), nullable=False),
        sa.Column("attendee_email", sa.String(length=255), nullable=False),
        sa.Column("attendee_phone", sa.String(length=40), nullable=True),
        sa.Column("attendee_document", sa.String(length=40), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending_payment"),
        sa.Column("payment_method", sa.String(length=20), nullable=True),
        sa.Column("payment_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("total_amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="BRL"),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_registrations_id", "event_registrations", ["id"])
    op.create_index("ix_event_registrations_tenant_id", "event_registrations", ["tenant_id"])
    op.create_index("ix_event_registrations_event_id", "event_registrations", ["event_id"])
    op.create_index("ix_event_registrations_registration_code", "event_registrations", ["registration_code"], unique=True)
    op.create_index("ix_event_registrations_public_token", "event_registrations", ["public_token"], unique=True)
    op.create_index("ix_event_registrations_attendee_email", "event_registrations", ["attendee_email"])
    op.create_index("ix_event_registrations_status", "event_registrations", ["status"])
    op.create_index("ix_event_registrations_payment_status", "event_registrations", ["payment_status"])

    op.create_table(
        "event_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("registration_id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("provider", sa.String(length=30), nullable=False, server_default="internal"),
        sa.Column("payment_method", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="BRL"),
        sa.Column("checkout_reference", sa.String(length=64), nullable=False),
        sa.Column("provider_reference", sa.String(length=120), nullable=True),
        sa.Column("checkout_url", sa.String(length=500), nullable=True),
        sa.Column("pix_copy_paste", sa.String(length=500), nullable=True),
        sa.Column("provider_payload", sa.JSON(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["registration_id"], ["event_registrations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_payments_id", "event_payments", ["id"])
    op.create_index("ix_event_payments_tenant_id", "event_payments", ["tenant_id"])
    op.create_index("ix_event_payments_event_id", "event_payments", ["event_id"])
    op.create_index("ix_event_payments_registration_id", "event_payments", ["registration_id"])
    op.create_index("ix_event_payments_transaction_id", "event_payments", ["transaction_id"])
    op.create_index("ix_event_payments_status", "event_payments", ["status"])
    op.create_index("ix_event_payments_checkout_reference", "event_payments", ["checkout_reference"], unique=True)
    op.create_index("ix_event_payments_provider_reference", "event_payments", ["provider_reference"])
    op.create_index("ix_event_payments_expires_at", "event_payments", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_event_payments_expires_at", table_name="event_payments")
    op.drop_index("ix_event_payments_provider_reference", table_name="event_payments")
    op.drop_index("ix_event_payments_checkout_reference", table_name="event_payments")
    op.drop_index("ix_event_payments_status", table_name="event_payments")
    op.drop_index("ix_event_payments_transaction_id", table_name="event_payments")
    op.drop_index("ix_event_payments_registration_id", table_name="event_payments")
    op.drop_index("ix_event_payments_event_id", table_name="event_payments")
    op.drop_index("ix_event_payments_tenant_id", table_name="event_payments")
    op.drop_index("ix_event_payments_id", table_name="event_payments")
    op.drop_table("event_payments")

    op.drop_index("ix_event_registrations_payment_status", table_name="event_registrations")
    op.drop_index("ix_event_registrations_status", table_name="event_registrations")
    op.drop_index("ix_event_registrations_attendee_email", table_name="event_registrations")
    op.drop_index("ix_event_registrations_public_token", table_name="event_registrations")
    op.drop_index("ix_event_registrations_registration_code", table_name="event_registrations")
    op.drop_index("ix_event_registrations_event_id", table_name="event_registrations")
    op.drop_index("ix_event_registrations_tenant_id", table_name="event_registrations")
    op.drop_index("ix_event_registrations_id", table_name="event_registrations")
    op.drop_table("event_registrations")

    op.drop_index("ix_events_end_at", table_name="events")
    op.drop_index("ix_events_start_at", table_name="events")
    op.drop_index("ix_events_visibility", table_name="events")
    op.drop_index("ix_events_status", table_name="events")
    op.drop_index("ix_events_slug", table_name="events")
    op.drop_index("ix_events_title", table_name="events")
    op.drop_index("ix_events_created_by_user_id", table_name="events")
    op.drop_index("ix_events_tenant_id", table_name="events")
    op.drop_index("ix_events_id", table_name="events")
    op.drop_table("events")
