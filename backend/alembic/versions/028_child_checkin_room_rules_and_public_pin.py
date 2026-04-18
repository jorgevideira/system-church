"""Child check-in room rules + public PIN

Revision ID: 028_child_checkin_room_rules_and_public_pin
Revises: 027_child_checkin_rooms
Create Date: 2026-04-17
"""

from alembic import op
import sqlalchemy as sa


revision = "028_child_checkin_room_rules_and_public_pin"
down_revision = "027_child_checkin_rooms"
branch_labels = None
depends_on = None


def _has_column(inspector: sa.Inspector, table: str, column: str) -> bool:
    cols = inspector.get_columns(table) or []
    return any(c.get("name") == column for c in cols)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "child_checkin_rooms" in tables:
        if not _has_column(inspector, "child_checkin_rooms", "min_age_months"):
            op.add_column("child_checkin_rooms", sa.Column("min_age_months", sa.Integer(), nullable=True))
        if not _has_column(inspector, "child_checkin_rooms", "max_age_months"):
            op.add_column("child_checkin_rooms", sa.Column("max_age_months", sa.Integer(), nullable=True))
        if not _has_column(inspector, "child_checkin_rooms", "capacity"):
            op.add_column("child_checkin_rooms", sa.Column("capacity", sa.Integer(), nullable=True))

    if "child_checkin_families" in tables:
        if not _has_column(inspector, "child_checkin_families", "public_pin_hash"):
            op.add_column("child_checkin_families", sa.Column("public_pin_hash", sa.String(length=255), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "child_checkin_rooms" in tables:
        if _has_column(inspector, "child_checkin_rooms", "capacity"):
            op.drop_column("child_checkin_rooms", "capacity")
        if _has_column(inspector, "child_checkin_rooms", "max_age_months"):
            op.drop_column("child_checkin_rooms", "max_age_months")
        if _has_column(inspector, "child_checkin_rooms", "min_age_months"):
            op.drop_column("child_checkin_rooms", "min_age_months")

    if "child_checkin_families" in tables:
        if _has_column(inspector, "child_checkin_families", "public_pin_hash"):
            op.drop_column("child_checkin_families", "public_pin_hash")

