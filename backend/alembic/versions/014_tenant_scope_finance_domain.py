"""Add tenant scope to finance domain tables

Revision ID: 014
Revises: 013
Create Date: 2026-04-08 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = [
        "categories",
        "ministries",
        "transactions",
        "statement_files",
        "payables",
        "receivables",
        "budgets",
        "classification_feedback",
    ]

    for table_name in tables:
        op.add_column(table_name, sa.Column("tenant_id", sa.Integer(), nullable=True))
        op.create_index(f"ix_{table_name}_tenant_id", table_name, ["tenant_id"])
        op.create_foreign_key(
            f"fk_{table_name}_tenant_id",
            table_name,
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.execute(
        """
        UPDATE categories
        SET tenant_id = (SELECT id FROM tenants WHERE slug = 'default' LIMIT 1)
        WHERE tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE ministries
        SET tenant_id = (SELECT id FROM tenants WHERE slug = 'default' LIMIT 1)
        WHERE tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE transactions t
        SET tenant_id = u.active_tenant_id
        FROM users u
        WHERE t.user_id = u.id AND t.tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE statement_files sf
        SET tenant_id = u.active_tenant_id
        FROM users u
        WHERE sf.user_id = u.id AND sf.tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE payables p
        SET tenant_id = u.active_tenant_id
        FROM users u
        WHERE p.user_id = u.id AND p.tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE receivables r
        SET tenant_id = u.active_tenant_id
        FROM users u
        WHERE r.user_id = u.id AND r.tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE budgets b
        SET tenant_id = u.active_tenant_id
        FROM users u
        WHERE b.user_id = u.id AND b.tenant_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE classification_feedback cf
        SET tenant_id = u.active_tenant_id
        FROM users u
        WHERE cf.user_id = u.id AND cf.tenant_id IS NULL
        """
    )


def downgrade() -> None:
    tables = [
        "classification_feedback",
        "budgets",
        "receivables",
        "payables",
        "statement_files",
        "transactions",
        "ministries",
        "categories",
    ]

    for table_name in tables:
        op.drop_constraint(f"fk_{table_name}_tenant_id", table_name, type_="foreignkey")
        op.drop_index(f"ix_{table_name}_tenant_id", table_name=table_name)
        op.drop_column(table_name, "tenant_id")
