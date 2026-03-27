"""add discipler link to leader assignments

Revision ID: 004
Revises: 003
Create Date: 2026-03-27 18:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cell_leader_assignments",
        sa.Column("discipler_member_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_cell_leader_assignments_discipler_member_id"),
        "cell_leader_assignments",
        ["discipler_member_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_cell_leader_assignments_discipler_member_id",
        "cell_leader_assignments",
        "cell_members",
        ["discipler_member_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_cell_leader_assignments_discipler_member_id",
        "cell_leader_assignments",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_cell_leader_assignments_discipler_member_id"),
        table_name="cell_leader_assignments",
    )
    op.drop_column("cell_leader_assignments", "discipler_member_id")
