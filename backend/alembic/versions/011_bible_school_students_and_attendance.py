"""Add Bible School students and attendance tables

Revision ID: 011
Revises: 010
Create Date: 2026-04-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bible_school_students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("contact", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["bible_school_classes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bible_school_students_class_id", "bible_school_students", ["class_id"])
    op.create_index("ix_bible_school_students_name", "bible_school_students", ["name"])
    op.create_index("ix_bible_school_students_active", "bible_school_students", ["active"])

    op.create_table(
        "bible_school_attendance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("notes", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["bible_school_lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["bible_school_students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id", "student_id", name="uq_bible_school_attendance_lesson_student"),
    )
    op.create_index("ix_bible_school_attendance_lesson_id", "bible_school_attendance", ["lesson_id"])
    op.create_index("ix_bible_school_attendance_student_id", "bible_school_attendance", ["student_id"])
    op.create_index("ix_bible_school_attendance_status", "bible_school_attendance", ["status"])


def downgrade() -> None:
    op.drop_table("bible_school_attendance")
    op.drop_table("bible_school_students")
