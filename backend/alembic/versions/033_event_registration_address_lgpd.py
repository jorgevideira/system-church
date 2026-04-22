"""Add public registration address and LGPD consent

Revision ID: 033_event_registration_address_lgpd
Revises: 032_tenant_membership_multi_roles
Create Date: 2026-04-22
"""

from alembic import op
import sqlalchemy as sa


revision = "033_event_registration_address_lgpd"
down_revision = "032_tenant_membership_multi_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("event_registrations", sa.Column("address_zip_code", sa.String(length=16), nullable=True))
    op.add_column("event_registrations", sa.Column("address_street", sa.String(length=255), nullable=True))
    op.add_column("event_registrations", sa.Column("address_number", sa.String(length=40), nullable=True))
    op.add_column("event_registrations", sa.Column("address_neighborhood", sa.String(length=120), nullable=True))
    op.add_column("event_registrations", sa.Column("address_country", sa.String(length=80), nullable=True))
    op.add_column("event_registrations", sa.Column("address_state", sa.String(length=80), nullable=True))
    op.add_column("event_registrations", sa.Column("address_city", sa.String(length=120), nullable=True))
    op.add_column(
        "event_registrations",
        sa.Column("lgpd_data_sharing_consent", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "event_registrations",
        sa.Column("lgpd_data_sharing_consented_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("event_registrations", "lgpd_data_sharing_consented_at")
    op.drop_column("event_registrations", "lgpd_data_sharing_consent")
    op.drop_column("event_registrations", "address_city")
    op.drop_column("event_registrations", "address_state")
    op.drop_column("event_registrations", "address_country")
    op.drop_column("event_registrations", "address_neighborhood")
    op.drop_column("event_registrations", "address_number")
    op.drop_column("event_registrations", "address_street")
    op.drop_column("event_registrations", "address_zip_code")
