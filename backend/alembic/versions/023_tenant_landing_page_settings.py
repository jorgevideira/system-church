"""tenant landing page settings

Revision ID: 023_tenant_landing_page_settings
Revises: 022_payment_accounts_and_event_links
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "023_tenant_landing_page_settings"
down_revision = "022_payment_accounts_and_event_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("tenants")}

    columns = [
        ("landing_hero_background_url", sa.String(length=500)),
        ("landing_pix_key", sa.String(length=255)),
        ("landing_bank_name", sa.String(length=255)),
        ("landing_bank_agency", sa.String(length=120)),
        ("landing_bank_account", sa.String(length=120)),
        ("landing_service_times", sa.String(length=2000)),
        ("landing_address", sa.String(length=500)),
        ("landing_location_url", sa.String(length=1000)),
        ("landing_footer_text", sa.String(length=500)),
    ]

    for column_name, column_type in columns:
        if column_name not in existing_columns:
            op.add_column("tenants", sa.Column(column_name, column_type, nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("tenants")}

    for column_name in [
        "landing_footer_text",
        "landing_location_url",
        "landing_address",
        "landing_service_times",
        "landing_bank_account",
        "landing_bank_agency",
        "landing_bank_name",
        "landing_pix_key",
        "landing_hero_background_url",
    ]:
        if column_name in existing_columns:
            op.drop_column("tenants", column_name)
