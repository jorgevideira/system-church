"""Scope roles and user administration by tenant

Revision ID: 015
Revises: 014
Create Date: 2026-04-08 01:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("roles", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])
    op.create_foreign_key(
        "fk_roles_tenant_id",
        "roles",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        UPDATE roles
        SET tenant_id = (SELECT id FROM tenants WHERE slug = 'default' LIMIT 1)
        WHERE tenant_id IS NULL
        """
    )


def downgrade() -> None:
    op.drop_constraint("fk_roles_tenant_id", "roles", type_="foreignkey")
    op.drop_index("ix_roles_tenant_id", table_name="roles")
    op.drop_column("roles", "tenant_id")
