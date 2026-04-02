"""Add Bible School professors and lessons tables

Revision ID: 010
Revises: 009
Create Date: 2026-03-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create professors table
    op.create_table(
        "bible_school_professors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("contact", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("bio", sa.String(500), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bible_school_professors_name", "bible_school_professors", ["name"])
    op.create_index("ix_bible_school_professors_email", "bible_school_professors", ["email"], unique=True)
    op.create_index("ix_bible_school_professors_active", "bible_school_professors", ["active"])

    # Create lessons table
    op.create_table(
        "bible_school_lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("professor_id", sa.Integer(), nullable=True),
        sa.Column("lesson_date", sa.Date(), nullable=False),
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="scheduled"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["bible_school_classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["professor_id"], ["bible_school_professors.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bible_school_lessons_class_id", "bible_school_lessons", ["class_id"])
    op.create_index("ix_bible_school_lessons_professor_id", "bible_school_lessons", ["professor_id"])
    op.create_index("ix_bible_school_lessons_lesson_date", "bible_school_lessons", ["lesson_date"])
    op.create_index("ix_bible_school_lessons_status", "bible_school_lessons", ["status"])
    op.create_index("ix_bible_school_lessons_active", "bible_school_lessons", ["active"])


def downgrade() -> None:
    op.drop_table("bible_school_lessons")
    op.drop_table("bible_school_professors")
