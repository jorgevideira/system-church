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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "budgets" not in existing_tables:
        op.create_table(
            "budgets",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("month", sa.String(length=7), nullable=False),
            sa.Column("budget_type", sa.String(length=20), nullable=False),
            sa.Column("reference_id", sa.Integer(), nullable=False),
            sa.Column("target_amount", sa.Numeric(15, 2), nullable=False),
            sa.Column("alert_threshold_percent", sa.Integer(), nullable=False, server_default="80"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_budgets_id", "budgets", ["id"], unique=False)
        op.create_index("ix_budgets_tenant_id", "budgets", ["tenant_id"], unique=False)
        op.create_index("ix_budgets_user_id", "budgets", ["user_id"], unique=False)
        op.create_index("ix_budgets_month", "budgets", ["month"], unique=False)
        op.create_index("ix_budgets_reference_id", "budgets", ["reference_id"], unique=False)
        existing_tables.add("budgets")

    if "classification_feedback" not in existing_tables:
        op.create_table(
            "classification_feedback",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("tenant_id", sa.Integer(), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("keyword", sa.String(length=80), nullable=False),
            sa.Column("category_id", sa.Integer(), nullable=True),
            sa.Column("transaction_type", sa.String(length=20), nullable=True),
            sa.Column("weight", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "keyword", "category_id", "transaction_type", name="uq_feedback_rule"),
        )
        op.create_index("ix_classification_feedback_id", "classification_feedback", ["id"], unique=False)
        op.create_index("ix_classification_feedback_tenant_id", "classification_feedback", ["tenant_id"], unique=False)
        op.create_index("ix_classification_feedback_user_id", "classification_feedback", ["user_id"], unique=False)
        op.create_index("ix_classification_feedback_keyword", "classification_feedback", ["keyword"], unique=False)
        op.create_index("ix_classification_feedback_category_id", "classification_feedback", ["category_id"], unique=False)
        existing_tables.add("classification_feedback")

    inspector = sa.inspect(bind)

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
        if table_name not in existing_tables:
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        if "tenant_id" not in existing_columns:
            op.add_column(table_name, sa.Column("tenant_id", sa.Integer(), nullable=True))
        op.execute(f"CREATE INDEX IF NOT EXISTS ix_{table_name}_tenant_id ON {table_name} (tenant_id)")
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.table_constraints
                    WHERE constraint_name = 'fk_{table_name}_tenant_id'
                ) THEN
                    ALTER TABLE {table_name}
                    ADD CONSTRAINT fk_{table_name}_tenant_id
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;
                END IF;
            END $$;
            """
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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())
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
        if table_name not in existing_tables:
            continue
        op.drop_constraint(f"fk_{table_name}_tenant_id", table_name, type_="foreignkey")
        op.drop_index(f"ix_{table_name}_tenant_id", table_name=table_name)
        op.drop_column(table_name, "tenant_id")
