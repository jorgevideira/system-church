"""Allow multiple roles per tenant membership

Revision ID: 032
Revises: 031
Create Date: 2026-04-20 22:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "032_tenant_membership_multi_roles"
down_revision = "031_event_registration_attendees"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_membership_role",
        sa.Column("tenant_membership_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_membership_id"], ["tenant_memberships.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_membership_id", "role_id"),
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_tenant_membership_role_membership_id ON tenant_membership_role (tenant_membership_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tenant_membership_role_role_id ON tenant_membership_role (role_id)")
    op.execute(
        """
        INSERT INTO tenant_membership_role (tenant_membership_id, role_id)
        SELECT id, role_id
        FROM tenant_memberships
        WHERE role_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_tenant_membership_role_role_id", table_name="tenant_membership_role")
    op.drop_index("ix_tenant_membership_role_membership_id", table_name="tenant_membership_role")
    op.drop_table("tenant_membership_role")
