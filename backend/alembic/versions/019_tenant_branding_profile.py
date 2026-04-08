"""tenant branding profile

Revision ID: 019_tenant_branding_profile
Revises: 018_event_notifications
Create Date: 2026-04-08
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "019_tenant_branding_profile"
down_revision = "018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("public_display_name", sa.String(length=255), nullable=True))
    op.add_column("tenants", sa.Column("public_description", sa.String(length=500), nullable=True))
    op.add_column("tenants", sa.Column("primary_color", sa.String(length=20), nullable=True))
    op.add_column("tenants", sa.Column("secondary_color", sa.String(length=20), nullable=True))
    op.add_column("tenants", sa.Column("logo_url", sa.String(length=500), nullable=True))
    op.add_column("tenants", sa.Column("support_email", sa.String(length=255), nullable=True))
    op.add_column("tenants", sa.Column("support_whatsapp", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "support_whatsapp")
    op.drop_column("tenants", "support_email")
    op.drop_column("tenants", "logo_url")
    op.drop_column("tenants", "secondary_color")
    op.drop_column("tenants", "primary_color")
    op.drop_column("tenants", "public_description")
    op.drop_column("tenants", "public_display_name")
