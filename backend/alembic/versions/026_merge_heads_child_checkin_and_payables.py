"""Merge child check-in and payables migration heads.

Revision ID: 026_merge_heads_child_checkin_and_payables
Revises: 024_child_checkin_module_dev, 025_payable_notifications
Create Date: 2026-04-15
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "026_merge_heads_child_checkin_and_payables"
down_revision = ("024_child_checkin_module_dev", "025_payable_notifications")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Merge migration only: no schema changes.
    pass


def downgrade() -> None:
    # No-op because this revision only merges branches.
    pass
