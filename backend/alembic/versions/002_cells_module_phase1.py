"""Create cells module phase 1 tables.

Revision ID: 002
Revises: 001
Create Date: 2026-03-27 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cells",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("weekday", sa.String(length=20), nullable=False),
        sa.Column("meeting_time", sa.Time(), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cells_id"), "cells", ["id"], unique=False)
    op.create_index(op.f("ix_cells_status"), "cells", ["status"], unique=False)

    op.create_table(
        "cell_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("contact", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cell_members_id"), "cell_members", ["id"], unique=False)
    op.create_index(op.f("ix_cell_members_status"), "cell_members", ["status"], unique=False)

    op.create_table(
        "cell_member_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("transfer_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["cell_id"], ["cells.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["cell_members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cell_member_links_id"), "cell_member_links", ["id"], unique=False)
    op.create_index(op.f("ix_cell_member_links_cell_id"), "cell_member_links", ["cell_id"], unique=False)
    op.create_index(op.f("ix_cell_member_links_member_id"), "cell_member_links", ["member_id"], unique=False)
    op.create_index(op.f("ix_cell_member_links_active"), "cell_member_links", ["active"], unique=False)

    op.create_table(
        "cell_leader_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="co_leader"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["cell_id"], ["cells.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["cell_members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cell_leader_assignments_id"),
        "cell_leader_assignments",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_leader_assignments_cell_id"),
        "cell_leader_assignments",
        ["cell_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_leader_assignments_member_id"),
        "cell_leader_assignments",
        ["member_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_leader_assignments_active"),
        "cell_leader_assignments",
        ["active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_leader_assignments_is_primary"),
        "cell_leader_assignments",
        ["is_primary"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("cell_leader_assignments")
    op.drop_table("cell_member_links")
    op.drop_table("cell_members")
    op.drop_table("cells")
