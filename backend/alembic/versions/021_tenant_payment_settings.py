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
    op.add_column("tenants", sa.Column("payment_provider", sa.String(length=50), nullable=False, server_default="internal"))
    op.add_column("tenants", sa.Column("payment_pix_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("tenants", sa.Column("payment_card_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("tenants", sa.Column("mercadopago_access_token", sa.String(length=255), nullable=True))
    op.add_column("tenants", sa.Column("mercadopago_public_key", sa.String(length=255), nullable=True))
    op.add_column("tenants", sa.Column("mercadopago_webhook_secret", sa.String(length=255), nullable=True))
    op.add_column("tenants", sa.Column("mercadopago_integrator_id", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "mercadopago_integrator_id")
    op.drop_column("tenants", "mercadopago_webhook_secret")
    op.drop_column("tenants", "mercadopago_public_key")
    op.drop_column("tenants", "mercadopago_access_token")
    op.drop_column("tenants", "payment_card_enabled")
    op.drop_column("tenants", "payment_pix_enabled")
    op.drop_column("tenants", "payment_provider")
