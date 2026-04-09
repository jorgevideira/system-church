"""add tenant payment settings

Revision ID: 021_tenant_payment_settings
Revises: 020_tenant_invitations
Create Date: 2026-04-08
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "021_tenant_payment_settings"
down_revision = "020_tenant_invitations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("tenants")}

    columns = [
        ("payment_provider", sa.String(length=50), {"nullable": False, "server_default": "internal"}),
        ("payment_pix_enabled", sa.Boolean(), {"nullable": False, "server_default": sa.true()}),
        ("payment_card_enabled", sa.Boolean(), {"nullable": False, "server_default": sa.true()}),
        ("mercadopago_access_token", sa.String(length=255), {"nullable": True}),
        ("mercadopago_public_key", sa.String(length=255), {"nullable": True}),
        ("mercadopago_webhook_secret", sa.String(length=255), {"nullable": True}),
        ("mercadopago_integrator_id", sa.String(length=255), {"nullable": True}),
    ]

    for column_name, column_type, kwargs in columns:
        if column_name not in existing_columns:
            op.add_column("tenants", sa.Column(column_name, column_type, **kwargs))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("tenants")}

    for column_name in [
        "mercadopago_integrator_id",
        "mercadopago_webhook_secret",
        "mercadopago_public_key",
        "mercadopago_access_token",
        "payment_card_enabled",
        "payment_pix_enabled",
        "payment_provider",
    ]:
        if column_name in existing_columns:
            op.drop_column("tenants", column_name)
