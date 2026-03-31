"""add user link to cell members

Revision ID: 005
Revises: 004
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cell_members",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_cell_members_user_id"),
        "cell_members",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_cell_members_user_id",
        "cell_members",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_cell_members_user_id",
        "cell_members",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_cell_members_user_id"), table_name="cell_members")
    op.drop_column("cell_members", "user_id")
