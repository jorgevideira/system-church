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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "payment_accounts" not in existing_tables:
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
    op.execute("CREATE INDEX IF NOT EXISTS ix_payment_accounts_id ON payment_accounts (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payment_accounts_provider ON payment_accounts (provider)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_payment_accounts_tenant_id ON payment_accounts (tenant_id)")

    event_columns = {column["name"] for column in inspector.get_columns("events")}
    if "payment_account_id" not in event_columns:
        op.add_column("events", sa.Column("payment_account_id", sa.Integer(), nullable=True))
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_payment_account_id ON events (payment_account_id)")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_events_payment_account_id_payment_accounts'
            ) THEN
                ALTER TABLE events
                ADD CONSTRAINT fk_events_payment_account_id_payment_accounts
                FOREIGN KEY (payment_account_id) REFERENCES payment_accounts(id) ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )

    event_payment_columns = {column["name"] for column in inspector.get_columns("event_payments")}
    if "payment_account_id" not in event_payment_columns:
        op.add_column("event_payments", sa.Column("payment_account_id", sa.Integer(), nullable=True))
    op.execute("CREATE INDEX IF NOT EXISTS ix_event_payments_payment_account_id ON event_payments (payment_account_id)")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_event_payments_payment_account_id_payment_accounts'
            ) THEN
                ALTER TABLE event_payments
                ADD CONSTRAINT fk_event_payments_payment_account_id_payment_accounts
                FOREIGN KEY (payment_account_id) REFERENCES payment_accounts(id) ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "event_payments" in existing_tables:
        event_payment_columns = {column["name"] for column in inspector.get_columns("event_payments")}
        event_payment_fks = {fk["name"] for fk in inspector.get_foreign_keys("event_payments")}
        if "fk_event_payments_payment_account_id_payment_accounts" in event_payment_fks:
            op.drop_constraint("fk_event_payments_payment_account_id_payment_accounts", "event_payments", type_="foreignkey")
        op.execute("DROP INDEX IF EXISTS ix_event_payments_payment_account_id")
        if "payment_account_id" in event_payment_columns:
            op.drop_column("event_payments", "payment_account_id")

    if "events" in existing_tables:
        event_columns = {column["name"] for column in inspector.get_columns("events")}
        event_fks = {fk["name"] for fk in inspector.get_foreign_keys("events")}
        if "fk_events_payment_account_id_payment_accounts" in event_fks:
            op.drop_constraint("fk_events_payment_account_id_payment_accounts", "events", type_="foreignkey")
        op.execute("DROP INDEX IF EXISTS ix_events_payment_account_id")
        if "payment_account_id" in event_columns:
            op.drop_column("events", "payment_account_id")

    if "payment_accounts" in existing_tables:
        op.execute("DROP INDEX IF EXISTS ix_payment_accounts_tenant_id")
        op.execute("DROP INDEX IF EXISTS ix_payment_accounts_provider")
        op.execute("DROP INDEX IF EXISTS ix_payment_accounts_id")
        op.drop_table("payment_accounts")
