"""Create cells module phase 2 meetings and visitors tables.

Revision ID: 003
Revises: 002
Create Date: 2026-03-27 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cell_meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cell_id", sa.Integer(), nullable=False),
        sa.Column("meeting_date", sa.Date(), nullable=False),
        sa.Column("theme", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["cell_id"], ["cells.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cell_meetings_id"), "cell_meetings", ["id"], unique=False)
    op.create_index(op.f("ix_cell_meetings_cell_id"), "cell_meetings", ["cell_id"], unique=False)
    op.create_index(op.f("ix_cell_meetings_meeting_date"), "cell_meetings", ["meeting_date"], unique=False)

    op.create_table(
        "cell_meeting_attendances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("attendance_status", sa.String(length=20), nullable=False, server_default="present"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["cell_meetings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id"], ["cell_members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meeting_id", "member_id", name="uq_cell_meeting_member"),
    )
    op.create_index(
        op.f("ix_cell_meeting_attendances_id"),
        "cell_meeting_attendances",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_meeting_attendances_meeting_id"),
        "cell_meeting_attendances",
        ["meeting_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_meeting_attendances_member_id"),
        "cell_meeting_attendances",
        ["member_id"],
        unique=False,
    )

    op.create_table(
        "cell_visitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("contact", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cell_visitors_id"), "cell_visitors", ["id"], unique=False)

    op.create_table(
        "cell_meeting_visitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meeting_id", sa.Integer(), nullable=False),
        sa.Column("visitor_id", sa.Integer(), nullable=False),
        sa.Column("is_first_time", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["cell_meetings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["visitor_id"], ["cell_visitors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cell_meeting_visitors_id"),
        "cell_meeting_visitors",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_meeting_visitors_meeting_id"),
        "cell_meeting_visitors",
        ["meeting_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cell_meeting_visitors_visitor_id"),
        "cell_meeting_visitors",
        ["visitor_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("cell_meeting_visitors")
    op.drop_table("cell_visitors")
    op.drop_table("cell_meeting_attendances")
    op.drop_table("cell_meetings")
