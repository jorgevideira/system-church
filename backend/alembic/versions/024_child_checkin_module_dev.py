"""child checkin module dev

Revision ID: 024_child_checkin_module_dev
Revises: 023_tenant_landing_page_settings
Create Date: 2026-04-15
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "024_child_checkin_module_dev"
down_revision = "023_tenant_landing_page_settings"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "child_checkin_families"):
        op.create_table(
            "child_checkin_families",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("family_name", sa.String(length=255), nullable=False),
            sa.Column("primary_responsible_name", sa.String(length=255), nullable=True),
            sa.Column("secondary_responsible_name", sa.String(length=255), nullable=True),
            sa.Column("phone_primary", sa.String(length=40), nullable=True),
            sa.Column("phone_secondary", sa.String(length=40), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("family_code", sa.String(length=40), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_child_checkin_families_tenant_id", "child_checkin_families", ["tenant_id"])
        op.create_index("ix_child_checkin_families_family_name", "child_checkin_families", ["family_name"])
        op.create_index("ix_child_checkin_families_family_code", "child_checkin_families", ["family_code"], unique=True)

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "child_checkin_children"):
        op.create_table(
            "child_checkin_children",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("family_id", sa.Integer(), sa.ForeignKey("child_checkin_families.id", ondelete="CASCADE"), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("birth_date", sa.Date(), nullable=True),
            sa.Column("age_group", sa.String(length=80), nullable=True),
            sa.Column("room_name", sa.String(length=120), nullable=True),
            sa.Column("gender", sa.String(length=20), nullable=True),
            sa.Column("photo_url", sa.String(length=500), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("allergies", sa.Text(), nullable=True),
            sa.Column("medical_restrictions", sa.Text(), nullable=True),
            sa.Column("special_needs", sa.Text(), nullable=True),
            sa.Column("behavioral_notes", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("is_visitor", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_child_checkin_children_tenant_id", "child_checkin_children", ["tenant_id"])
        op.create_index("ix_child_checkin_children_family_id", "child_checkin_children", ["family_id"])
        op.create_index("ix_child_checkin_children_full_name", "child_checkin_children", ["full_name"])
        op.create_index("ix_child_checkin_children_room_name", "child_checkin_children", ["room_name"])

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "child_checkin_guardians"):
        op.create_table(
            "child_checkin_guardians",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("family_id", sa.Integer(), sa.ForeignKey("child_checkin_families.id", ondelete="CASCADE"), nullable=False),
            sa.Column("full_name", sa.String(length=255), nullable=False),
            sa.Column("relationship", sa.String(length=120), nullable=True),
            sa.Column("phone", sa.String(length=40), nullable=True),
            sa.Column("photo_url", sa.String(length=500), nullable=True),
            sa.Column("is_authorized", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_child_checkin_guardians_tenant_id", "child_checkin_guardians", ["tenant_id"])
        op.create_index("ix_child_checkin_guardians_family_id", "child_checkin_guardians", ["family_id"])

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "child_checkin_records"):
        op.create_table(
            "child_checkin_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("family_id", sa.Integer(), sa.ForeignKey("child_checkin_families.id", ondelete="CASCADE"), nullable=False),
            sa.Column("child_id", sa.Integer(), sa.ForeignKey("child_checkin_children.id", ondelete="CASCADE"), nullable=False),
            sa.Column("context_type", sa.String(length=20), nullable=False, server_default="culto"),
            sa.Column("context_name", sa.String(length=255), nullable=False),
            sa.Column("room_name", sa.String(length=120), nullable=False),
            sa.Column("checkin_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("checkout_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("checked_in_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("checked_out_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("accompanied_by_name", sa.String(length=255), nullable=True),
            sa.Column("pickup_guardian_id", sa.Integer(), sa.ForeignKey("child_checkin_guardians.id", ondelete="SET NULL"), nullable=True),
            sa.Column("pickup_person_name", sa.String(length=255), nullable=True),
            sa.Column("security_code", sa.String(length=24), nullable=False),
            sa.Column("qr_token", sa.String(length=120), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="checked_in"),
            sa.Column("alert_snapshot", sa.Text(), nullable=True),
            sa.Column("exception_notes", sa.Text(), nullable=True),
            sa.Column("manual_override_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_child_checkin_records_tenant_id", "child_checkin_records", ["tenant_id"])
        op.create_index("ix_child_checkin_records_family_id", "child_checkin_records", ["family_id"])
        op.create_index("ix_child_checkin_records_child_id", "child_checkin_records", ["child_id"])
        op.create_index("ix_child_checkin_records_room_name", "child_checkin_records", ["room_name"])
        op.create_index("ix_child_checkin_records_status", "child_checkin_records", ["status"])
        op.create_index("ix_child_checkin_records_checkin_at", "child_checkin_records", ["checkin_at"])
        op.create_index("ix_child_checkin_records_checkout_at", "child_checkin_records", ["checkout_at"])
        op.create_index("ix_child_checkin_records_security_code", "child_checkin_records", ["security_code"])
        op.create_index("ix_child_checkin_records_qr_token", "child_checkin_records", ["qr_token"], unique=True)

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "child_checkin_audits"):
        op.create_table(
            "child_checkin_audits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("record_id", sa.Integer(), sa.ForeignKey("child_checkin_records.id", ondelete="CASCADE"), nullable=True),
            sa.Column("action", sa.String(length=80), nullable=False),
            sa.Column("performed_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_child_checkin_audits_tenant_id", "child_checkin_audits", ["tenant_id"])
        op.create_index("ix_child_checkin_audits_record_id", "child_checkin_audits", ["record_id"])
        op.create_index("ix_child_checkin_audits_action", "child_checkin_audits", ["action"])
        op.create_index("ix_child_checkin_audits_created_at", "child_checkin_audits", ["created_at"])

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "child_checkin_notifications"):
        op.create_table(
            "child_checkin_notifications",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("family_id", sa.Integer(), sa.ForeignKey("child_checkin_families.id", ondelete="SET NULL"), nullable=True),
            sa.Column("child_id", sa.Integer(), sa.ForeignKey("child_checkin_children.id", ondelete="SET NULL"), nullable=True),
            sa.Column("channel", sa.String(length=20), nullable=False, server_default="email"),
            sa.Column("message_type", sa.String(length=50), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("delivery_status", sa.String(length=20), nullable=False, server_default="queued"),
            sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_child_checkin_notifications_tenant_id", "child_checkin_notifications", ["tenant_id"])
        op.create_index("ix_child_checkin_notifications_family_id", "child_checkin_notifications", ["family_id"])
        op.create_index("ix_child_checkin_notifications_child_id", "child_checkin_notifications", ["child_id"])
        op.create_index("ix_child_checkin_notifications_message_type", "child_checkin_notifications", ["message_type"])
        op.create_index("ix_child_checkin_notifications_delivery_status", "child_checkin_notifications", ["delivery_status"])
        op.create_index("ix_child_checkin_notifications_created_at", "child_checkin_notifications", ["created_at"])

    inspector = sa.inspect(bind)
    if not _table_exists(inspector, "child_checkin_room_scopes"):
        op.create_table(
            "child_checkin_room_scopes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("room_name", sa.String(length=120), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_child_checkin_room_scopes_tenant_id", "child_checkin_room_scopes", ["tenant_id"])
        op.create_index("ix_child_checkin_room_scopes_user_id", "child_checkin_room_scopes", ["user_id"])
        op.create_index("ix_child_checkin_room_scopes_room_name", "child_checkin_room_scopes", ["room_name"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "child_checkin_room_scopes"):
        op.drop_table("child_checkin_room_scopes")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "child_checkin_notifications"):
        op.drop_table("child_checkin_notifications")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "child_checkin_audits"):
        op.drop_table("child_checkin_audits")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "child_checkin_records"):
        op.drop_table("child_checkin_records")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "child_checkin_guardians"):
        op.drop_table("child_checkin_guardians")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "child_checkin_children"):
        op.drop_table("child_checkin_children")

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "child_checkin_families"):
        op.drop_table("child_checkin_families")
