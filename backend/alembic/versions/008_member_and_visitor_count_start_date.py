"""Add count_start_date to cell members and visitors

Revision ID: 008
Revises: 007
Create Date: 2026-03-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "cell_members",
        sa.Column("count_start_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
    )
    op.create_index(op.f("ix_cell_members_count_start_date"), "cell_members", ["count_start_date"], unique=False)

    op.add_column(
        "cell_visitors",
        sa.Column("count_start_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
    )
    op.create_index(op.f("ix_cell_visitors_count_start_date"), "cell_visitors", ["count_start_date"], unique=False)

    op.alter_column("cell_members", "count_start_date", server_default=None)
    op.alter_column("cell_visitors", "count_start_date", server_default=None)


def downgrade():
    op.drop_index(op.f("ix_cell_visitors_count_start_date"), table_name="cell_visitors")
    op.drop_column("cell_visitors", "count_start_date")

    op.drop_index(op.f("ix_cell_members_count_start_date"), table_name="cell_members")
    op.drop_column("cell_members", "count_start_date")
