"""Add lost_sheep table

Revision ID: 007
Revises: 006
Create Date: 2026-03-30 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'lost_sheep',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('previous_cell_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('observation', sa.Text(), nullable=True),
        sa.Column('visit_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('visit_date', sa.DateTime(), nullable=True),
        sa.Column('visit_observation', sa.Text(), nullable=True),
        sa.Column('marked_as_lost_date', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('re_inserted_date', sa.DateTime(), nullable=True),
        sa.Column('current_cell_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['member_id'], ['cell_members.id'], ),
        sa.ForeignKeyConstraint(['previous_cell_id'], ['cells.id'], ),
        sa.ForeignKeyConstraint(['current_cell_id'], ['cells.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lost_sheep_member_id'), 'lost_sheep', ['member_id'])
    op.create_index(op.f('ix_lost_sheep_previous_cell_id'), 'lost_sheep', ['previous_cell_id'])
    op.create_index(op.f('ix_lost_sheep_current_cell_id'), 'lost_sheep', ['current_cell_id'])


def downgrade():
    op.drop_index(op.f('ix_lost_sheep_current_cell_id'), table_name='lost_sheep')
    op.drop_index(op.f('ix_lost_sheep_previous_cell_id'), table_name='lost_sheep')
    op.drop_index(op.f('ix_lost_sheep_member_id'), table_name='lost_sheep')
    op.drop_table('lost_sheep')
