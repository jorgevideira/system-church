"""add payment accounts and event links

Revision ID: 022_payment_accounts_evt
Revises: 021_tenant_payment_settings
Create Date: 2026-04-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "022_payment_accounts_evt"
down_revision = "021_tenant_payment_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payment_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("supports_pix", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("supports_card", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("config_json", sa.JSON(), nullable=True),
        sa.Column("secrets_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "label", name="uq_payment_accounts_tenant_label"),
    )
    op.create_index(op.f("ix_payment_accounts_id"), "payment_accounts", ["id"], unique=False)
    op.create_index(op.f("ix_payment_accounts_provider"), "payment_accounts", ["provider"], unique=False)
    op.create_index(op.f("ix_payment_accounts_tenant_id"), "payment_accounts", ["tenant_id"], unique=False)

    op.add_column("events", sa.Column("payment_account_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_events_payment_account_id"), "events", ["payment_account_id"], unique=False)
    op.create_foreign_key(
        "fk_events_payment_account_id_payment_accounts",
        "events",
        "payment_accounts",
        ["payment_account_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("event_payments", sa.Column("payment_account_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_event_payments_payment_account_id"), "event_payments", ["payment_account_id"], unique=False)
    op.create_foreign_key(
        "fk_event_payments_payment_account_id_payment_accounts",
        "event_payments",
        "payment_accounts",
        ["payment_account_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_event_payments_payment_account_id_payment_accounts", "event_payments", type_="foreignkey")
    op.drop_index(op.f("ix_event_payments_payment_account_id"), table_name="event_payments")
    op.drop_column("event_payments", "payment_account_id")

    op.drop_constraint("fk_events_payment_account_id_payment_accounts", "events", type_="foreignkey")
    op.drop_index(op.f("ix_events_payment_account_id"), table_name="events")
    op.drop_column("events", "payment_account_id")

    op.drop_index(op.f("ix_payment_accounts_tenant_id"), table_name="payment_accounts")
    op.drop_index(op.f("ix_payment_accounts_provider"), table_name="payment_accounts")
    op.drop_index(op.f("ix_payment_accounts_id"), table_name="payment_accounts")
    op.drop_table("payment_accounts")
