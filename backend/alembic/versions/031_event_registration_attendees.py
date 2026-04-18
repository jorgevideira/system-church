"""Event registrations: per-attendee tickets + multi check-in

Revision ID: 031_event_registration_attendees
Revises: 030_child_checkin_email_unique_and_recovery
Create Date: 2026-04-18
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "031_event_registration_attendees"
down_revision = "030_child_checkin_email_unique_and_recovery"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_registration_attendees",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("registration_id", sa.Integer(), sa.ForeignKey("event_registrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attendee_index", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("attendee_name", sa.String(length=255), nullable=False),
        sa.Column("public_token", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("public_token", name="uq_event_registration_attendees_token"),
    )
    op.create_index("ix_event_registration_attendees_tenant_id", "event_registration_attendees", ["tenant_id"])
    op.create_index("ix_event_registration_attendees_event_id", "event_registration_attendees", ["event_id"])
    op.create_index("ix_event_registration_attendees_registration_id", "event_registration_attendees", ["registration_id"])
    op.create_index("ix_event_registration_attendees_public_token", "event_registration_attendees", ["public_token"])

    # Allow multiple check-ins per registration (one per attendee).
    op.add_column("event_checkins", sa.Column("attendee_id", sa.Integer(), nullable=True))
    op.create_index("ix_event_checkins_attendee_id", "event_checkins", ["attendee_id"])
    op.create_foreign_key(
        "fk_event_checkins_attendee",
        "event_checkins",
        "event_registration_attendees",
        ["attendee_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("uq_event_checkins_registration", "event_checkins", type_="unique")
    op.create_unique_constraint("uq_event_checkins_attendee", "event_checkins", ["attendee_id"])

    # Backfill: create attendees for existing registrations.
    bind = op.get_bind()
    registrations = bind.execute(
        sa.text(
            """
            SELECT id, tenant_id, event_id, public_token, attendee_name, quantity
            FROM event_registrations
            ORDER BY id ASC
            """
        )
    ).mappings().all()
    now = datetime.now(timezone.utc)
    for reg in registrations:
        qty = int(reg.get("quantity") or 1)
        qty = max(1, qty)
        for idx in range(1, qty + 1):
            token = str(reg.get("public_token") or "").strip() if idx == 1 else secrets.token_urlsafe(24)
            name = str(reg.get("attendee_name") or "").strip() or "Participante"
            bind.execute(
                sa.text(
                    """
                    INSERT INTO event_registration_attendees
                      (tenant_id, event_id, registration_id, attendee_index, attendee_name, public_token, created_at, updated_at)
                    VALUES
                      (:tenant_id, :event_id, :registration_id, :attendee_index, :attendee_name, :public_token, :created_at, :updated_at)
                    """
                ),
                {
                    "tenant_id": reg.get("tenant_id"),
                    "event_id": reg.get("event_id"),
                    "registration_id": reg.get("id"),
                    "attendee_index": idx,
                    "attendee_name": name,
                    "public_token": token,
                    "created_at": now,
                    "updated_at": now,
                },
            )

    # Backfill existing check-ins to point to the first attendee.
    bind.execute(
        sa.text(
            """
            UPDATE event_checkins c
            SET attendee_id = a.id
            FROM event_registration_attendees a
            WHERE c.attendee_id IS NULL
              AND a.registration_id = c.registration_id
              AND a.attendee_index = 1
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint("uq_event_checkins_attendee", "event_checkins", type_="unique")
    op.create_unique_constraint("uq_event_checkins_registration", "event_checkins", ["registration_id"])
    op.drop_constraint("fk_event_checkins_attendee", "event_checkins", type_="foreignkey")
    op.drop_index("ix_event_checkins_attendee_id", table_name="event_checkins")
    op.drop_column("event_checkins", "attendee_id")

    op.drop_index("ix_event_registration_attendees_public_token", table_name="event_registration_attendees")
    op.drop_index("ix_event_registration_attendees_registration_id", table_name="event_registration_attendees")
    op.drop_index("ix_event_registration_attendees_event_id", table_name="event_registration_attendees")
    op.drop_index("ix_event_registration_attendees_tenant_id", table_name="event_registration_attendees")
    op.drop_table("event_registration_attendees")

