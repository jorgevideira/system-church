"""Add roles and permissions tables

Revision ID: 012
Revises: 011
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create permissions table
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),  # view, edit, delete, etc
        sa.Column("module", sa.String(50), nullable=False),  # finance, cells, school, users, etc
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_permissions_name", "permissions", ["name"])
    op.create_index("ix_permissions_category", "permissions", ["category"])
    op.create_index("ix_permissions_module", "permissions", ["module"])
    op.create_index("ix_permissions_active", "permissions", ["active"])

    # Create roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_roles_name", "roles", ["name"])
    op.create_index("ix_roles_is_admin", "roles", ["is_admin"])
    op.create_index("ix_roles_active", "roles", ["active"])

    # Create role_permission association table
    op.create_table(
        "role_permission",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )
    op.create_index("ix_role_permission_role_id", "role_permission", ["role_id"])
    op.create_index("ix_role_permission_permission_id", "role_permission", ["permission_id"])

    # Add role_id column to users table
    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_users_role_id", "users", "roles", ["role_id"], ["id"])
    op.create_index("ix_users_role_id", "users", ["role_id"])

    # Insert default roles and permissions
    # Admin role (full access)
    op.execute("""
        INSERT INTO roles (name, description, is_admin, active, created_at, updated_at)
        VALUES ('Admin', 'Administrador com acesso total', true, true, NOW(), NOW())
    """)

    # Viewer role (read-only)
    op.execute("""
        INSERT INTO roles (name, description, is_admin, active, created_at, updated_at)
        VALUES ('Viewer', 'Apenas visualização de dados', false, true, NOW(), NOW())
    """)

    # Default permissions
    permissions = [
        # Finance module
        ('view_finance', 'Visualizar módulo de Financeiro', 'view', 'finance'),
        ('edit_finance', 'Editar dados do Financeiro', 'edit', 'finance'),
        ('delete_finance', 'Deletar dados do Financeiro', 'delete', 'finance'),
        
        # Cells module
        ('view_cells', 'Visualizar módulo de Células', 'view', 'cells'),
        ('edit_cells', 'Editar dados de Células', 'edit', 'cells'),
        ('delete_cells', 'Deletar dados de Células', 'delete', 'cells'),
        
        # School module
        ('view_school', 'Visualizar módulo de Escola Bíblica', 'view', 'school'),
        ('edit_school', 'Editar dados de Escola Bíblica', 'edit', 'school'),
        ('delete_school', 'Deletar dados de Escola Bíblica', 'delete', 'school'),
        
        # Users module
        ('view_users', 'Visualizar usuários', 'view', 'users'),
        ('edit_users', 'Editar usuários', 'edit', 'users'),
        ('delete_users', 'Deletar usuários', 'delete', 'users'),
    ]

    for name, description, category, module in permissions:
        op.execute(f"""
            INSERT INTO permissions (name, description, category, module, active, created_at, updated_at)
            VALUES ('{name}', '{description}', '{category}', '{module}', true, NOW(), NOW())
        """)

    # Insert permissions for Admin role (all permissions)
    op.execute("""
        INSERT INTO role_permission (role_id, permission_id)
        SELECT 1, id FROM permissions WHERE active = true
    """)

    # Insert permissions for Viewer role (only view permissions)
    op.execute("""
        INSERT INTO role_permission (role_id, permission_id)
        SELECT 2, id FROM permissions WHERE category = 'view' AND active = true
    """)


def downgrade() -> None:
    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_constraint("fk_users_role_id", "users", type_="foreignkey")
    op.drop_column("users", "role_id")
    
    op.drop_index("ix_role_permission_permission_id", table_name="role_permission")
    op.drop_index("ix_role_permission_role_id", table_name="role_permission")
    op.drop_table("role_permission")
    
    op.drop_index("ix_roles_active", table_name="roles")
    op.drop_index("ix_roles_is_admin", table_name="roles")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")
    
    op.drop_index("ix_permissions_active", table_name="permissions")
    op.drop_index("ix_permissions_module", table_name="permissions")
    op.drop_index("ix_permissions_category", table_name="permissions")
    op.drop_index("ix_permissions_name", table_name="permissions")
    op.drop_table("permissions")
