"""add stage field to cell members

Revision ID: 006
Revises: 005
Create Date: 2026-03-30 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cell_members",
        sa.Column("stage", sa.String(length=20), nullable=False, server_default="member"),
    )
    op.create_index(op.f("ix_cell_members_stage"), "cell_members", ["stage"], unique=False)
    op.alter_column("cell_members", "stage", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_cell_members_stage"), table_name="cell_members")
    op.drop_column("cell_members", "stage")
