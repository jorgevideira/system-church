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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("tenants")}

    columns = [
        ("public_display_name", sa.String(length=255)),
        ("public_description", sa.String(length=500)),
        ("primary_color", sa.String(length=20)),
        ("secondary_color", sa.String(length=20)),
        ("logo_url", sa.String(length=500)),
        ("support_email", sa.String(length=255)),
        ("support_whatsapp", sa.String(length=50)),
    ]

    for column_name, column_type in columns:
        if column_name not in existing_columns:
            op.add_column("tenants", sa.Column(column_name, column_type, nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("tenants")}

    for column_name in [
        "support_whatsapp",
        "support_email",
        "logo_url",
        "secondary_color",
        "primary_color",
        "public_description",
        "public_display_name",
    ]:
        if column_name in existing_columns:
            op.drop_column("tenants", column_name)
