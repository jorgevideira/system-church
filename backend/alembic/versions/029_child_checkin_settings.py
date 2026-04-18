"""Child check-in settings (ops presets)

Revision ID: 029_child_checkin_settings
Revises: 028_child_checkin_room_rules_and_public_pin
Create Date: 2026-04-17
"""

from alembic import op
import sqlalchemy as sa


revision = "029_child_checkin_settings"
down_revision = "028_child_checkin_room_rules_and_public_pin"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "child_checkin_settings" not in tables:
        op.create_table(
            "child_checkin_settings",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("ops_context_presets_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("tenant_id", name="uq_child_checkin_settings_tenant"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "child_checkin_settings" in tables:
        op.drop_table("child_checkin_settings")

