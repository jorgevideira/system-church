"""Create bible school courses and classes tables

Revision ID: 009
Revises: 008
Create Date: 2026-03-31 20:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bible_school_courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("total_lessons", sa.Integer(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bible_school_courses_id"), "bible_school_courses", ["id"], unique=False)
    op.create_index(op.f("ix_bible_school_courses_name"), "bible_school_courses", ["name"], unique=False)
    op.create_index(op.f("ix_bible_school_courses_active"), "bible_school_courses", ["active"], unique=False)

    op.create_table(
        "bible_school_classes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("weekday", sa.String(length=20), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("professor_name", sa.String(length=255), nullable=True),
        sa.Column("contact", sa.String(length=255), nullable=True),
        sa.Column("classroom", sa.String(length=255), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["bible_school_courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bible_school_classes_id"), "bible_school_classes", ["id"], unique=False)
    op.create_index(op.f("ix_bible_school_classes_course_id"), "bible_school_classes", ["course_id"], unique=False)
    op.create_index(op.f("ix_bible_school_classes_name"), "bible_school_classes", ["name"], unique=False)
    op.create_index(op.f("ix_bible_school_classes_active"), "bible_school_classes", ["active"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_bible_school_classes_active"), table_name="bible_school_classes")
    op.drop_index(op.f("ix_bible_school_classes_name"), table_name="bible_school_classes")
    op.drop_index(op.f("ix_bible_school_classes_course_id"), table_name="bible_school_classes")
    op.drop_index(op.f("ix_bible_school_classes_id"), table_name="bible_school_classes")
    op.drop_table("bible_school_classes")

    op.drop_index(op.f("ix_bible_school_courses_active"), table_name="bible_school_courses")
    op.drop_index(op.f("ix_bible_school_courses_name"), table_name="bible_school_courses")
    op.drop_index(op.f("ix_bible_school_courses_id"), table_name="bible_school_courses")
    op.drop_table("bible_school_courses")
