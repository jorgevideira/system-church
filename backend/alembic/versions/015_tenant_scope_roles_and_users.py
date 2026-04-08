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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("roles")}
    if "tenant_id" not in existing_columns:
        op.add_column("roles", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.execute("CREATE INDEX IF NOT EXISTS ix_roles_tenant_id ON roles (tenant_id)")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_roles_tenant_id'
            ) THEN
                ALTER TABLE roles
                ADD CONSTRAINT fk_roles_tenant_id
                FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;
            END IF;
        END $$;
        """
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
