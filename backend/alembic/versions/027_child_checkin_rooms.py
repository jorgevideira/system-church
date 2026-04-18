"""Add child check-in rooms table

Revision ID: 027_child_checkin_rooms
Revises: 026_merge_heads_child_checkin_and_payables
Create Date: 2026-04-15
"""

from alembic import op
import sqlalchemy as sa


revision = "027_child_checkin_rooms"
down_revision = "026_merge_heads_child_checkin_and_payables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "child_checkin_rooms" not in tables:
        op.create_table(
            "child_checkin_rooms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("age_range_label", sa.String(length=80), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", "name", name="uq_child_checkin_rooms_tenant_name"),
        )
        op.create_index("ix_child_checkin_rooms_id", "child_checkin_rooms", ["id"])
        op.create_index("ix_child_checkin_rooms_tenant_id", "child_checkin_rooms", ["tenant_id"])
        op.create_index("ix_child_checkin_rooms_name", "child_checkin_rooms", ["name"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "child_checkin_rooms" in tables:
        op.drop_index("ix_child_checkin_rooms_name", table_name="child_checkin_rooms")
        op.drop_index("ix_child_checkin_rooms_tenant_id", table_name="child_checkin_rooms")
        op.drop_index("ix_child_checkin_rooms_id", table_name="child_checkin_rooms")
        op.drop_table("child_checkin_rooms")
