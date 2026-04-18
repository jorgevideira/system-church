"""Child check-in: unique email + PIN recovery

Revision ID: 030_child_checkin_email_unique_and_recovery
Revises: 029_child_checkin_settings
Create Date: 2026-04-17
"""

from alembic import op
import sqlalchemy as sa


revision = "030_child_checkin_email_unique_and_recovery"
down_revision = "029_child_checkin_settings"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    cols = inspector.get_columns(table) or []
    return any(c.get("name") == column for c in cols)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "child_checkin_families" in tables:
        if not _has_column(inspector, "child_checkin_families", "public_reset_code_hash"):
            op.add_column("child_checkin_families", sa.Column("public_reset_code_hash", sa.String(length=255), nullable=True))
        if not _has_column(inspector, "child_checkin_families", "public_reset_code_expires_at"):
            op.add_column("child_checkin_families", sa.Column("public_reset_code_expires_at", sa.DateTime(timezone=True), nullable=True))

        # Unique email per tenant (case-insensitive). Use a partial unique index to allow NULL/empty.
        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_child_checkin_families_tenant_email_lower
            ON child_checkin_families (tenant_id, lower(email))
            WHERE email IS NOT NULL AND email <> '';
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "child_checkin_families" in tables:
        op.execute("DROP INDEX IF EXISTS uq_child_checkin_families_tenant_email_lower;")
        if _has_column(inspector, "child_checkin_families", "public_reset_code_expires_at"):
            op.drop_column("child_checkin_families", "public_reset_code_expires_at")
        if _has_column(inspector, "child_checkin_families", "public_reset_code_hash"):
            op.drop_column("child_checkin_families", "public_reset_code_hash")

