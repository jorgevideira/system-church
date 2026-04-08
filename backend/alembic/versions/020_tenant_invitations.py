"""add tenant invitations

Revision ID: 020_tenant_invitations
Revises: 019_tenant_branding_profile
Create Date: 2026-04-08
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "020_tenant_invitations"
down_revision = "019_tenant_branding_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("invite_token", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invited_by_user_id", sa.Integer(), nullable=True),
        sa.Column("accepted_user_id", sa.Integer(), nullable=True),
        sa.Column("invite_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["accepted_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenant_invitations_id"), "tenant_invitations", ["id"], unique=False)
    op.create_index(op.f("ix_tenant_invitations_tenant_id"), "tenant_invitations", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_tenant_invitations_email"), "tenant_invitations", ["email"], unique=False)
    op.create_index(op.f("ix_tenant_invitations_role_id"), "tenant_invitations", ["role_id"], unique=False)
    op.create_index(op.f("ix_tenant_invitations_status"), "tenant_invitations", ["status"], unique=False)
    op.create_index(op.f("ix_tenant_invitations_expires_at"), "tenant_invitations", ["expires_at"], unique=False)
    op.create_index(op.f("ix_tenant_invitations_invite_token"), "tenant_invitations", ["invite_token"], unique=True)
    op.create_index(op.f("ix_tenant_invitations_invited_by_user_id"), "tenant_invitations", ["invited_by_user_id"], unique=False)
    op.create_index(op.f("ix_tenant_invitations_accepted_user_id"), "tenant_invitations", ["accepted_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tenant_invitations_accepted_user_id"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_invited_by_user_id"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_invite_token"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_expires_at"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_status"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_role_id"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_email"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_tenant_id"), table_name="tenant_invitations")
    op.drop_index(op.f("ix_tenant_invitations_id"), table_name="tenant_invitations")
    op.drop_table("tenant_invitations")
