"""Add tenants and tenant memberships foundation

Revision ID: 013
Revises: 012
Create Date: 2026-04-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "tenants" not in inspector.get_table_names():
        op.create_table(
            "tenants",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("slug", sa.String(length=120), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
            sa.UniqueConstraint("slug"),
        )

    op.execute("CREATE INDEX IF NOT EXISTS ix_tenants_id ON tenants (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tenants_name ON tenants (name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tenants_slug ON tenants (slug)")

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "active_tenant_id" not in user_columns:
        op.add_column("users", sa.Column("active_tenant_id", sa.Integer(), nullable=True))
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE constraint_name = 'fk_users_active_tenant_id'
            ) THEN
                ALTER TABLE users
                ADD CONSTRAINT fk_users_active_tenant_id
                FOREIGN KEY (active_tenant_id) REFERENCES tenants(id);
            END IF;
        END $$;
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_active_tenant_id ON users (active_tenant_id)")

    if "tenant_memberships" not in inspector.get_table_names():
        op.create_table(
            "tenant_memberships",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False),
            sa.Column("role_id", sa.Integer(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "tenant_id", name="uq_tenant_memberships_user_tenant"),
        )

    op.execute("CREATE INDEX IF NOT EXISTS ix_tenant_memberships_id ON tenant_memberships (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tenant_memberships_user_id ON tenant_memberships (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tenant_memberships_tenant_id ON tenant_memberships (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tenant_memberships_role_id ON tenant_memberships (role_id)")


def downgrade() -> None:
    op.drop_index("ix_tenant_memberships_role_id", table_name="tenant_memberships")
    op.drop_index("ix_tenant_memberships_tenant_id", table_name="tenant_memberships")
    op.drop_index("ix_tenant_memberships_user_id", table_name="tenant_memberships")
    op.drop_index("ix_tenant_memberships_id", table_name="tenant_memberships")
    op.drop_table("tenant_memberships")

    op.drop_index("ix_users_active_tenant_id", table_name="users")
    op.drop_constraint("fk_users_active_tenant_id", "users", type_="foreignkey")
    op.drop_column("users", "active_tenant_id")

    op.drop_index("ix_tenants_slug", table_name="tenants")
    op.drop_index("ix_tenants_name", table_name="tenants")
    op.drop_index("ix_tenants_id", table_name="tenants")
    op.drop_table("tenants")
