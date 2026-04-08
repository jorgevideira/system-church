"""Add tenant scoping to cells and bible school modules

Revision ID: 016
Revises: 015
Create Date: 2026-04-08 11:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


TENANT_TABLES = [
    "cells",
    "cell_members",
    "cell_member_links",
    "cell_leader_assignments",
    "cell_meetings",
    "cell_meeting_attendances",
    "cell_visitors",
    "cell_meeting_visitors",
    "lost_sheep",
    "bible_school_courses",
    "bible_school_classes",
    "bible_school_professors",
    "bible_school_lessons",
    "bible_school_students",
    "bible_school_attendance",
]


def _default_tenant_sql() -> str:
    return "(SELECT id FROM tenants WHERE slug = 'default' LIMIT 1)"


def upgrade() -> None:
    for table_name in TENANT_TABLES:
        op.add_column(table_name, sa.Column("tenant_id", sa.Integer(), nullable=True))
        op.create_index(f"ix_{table_name}_tenant_id", table_name, ["tenant_id"])
        op.create_foreign_key(
            f"fk_{table_name}_tenant_id",
            table_name,
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )

    op.execute(f"UPDATE cells SET tenant_id = {_default_tenant_sql()} WHERE tenant_id IS NULL")
    op.execute(f"UPDATE cell_members SET tenant_id = {_default_tenant_sql()} WHERE tenant_id IS NULL")
    op.execute(f"UPDATE cell_visitors SET tenant_id = {_default_tenant_sql()} WHERE tenant_id IS NULL")
    op.execute(f"UPDATE bible_school_courses SET tenant_id = {_default_tenant_sql()} WHERE tenant_id IS NULL")
    op.execute(f"UPDATE bible_school_professors SET tenant_id = {_default_tenant_sql()} WHERE tenant_id IS NULL")

    op.execute(
        f"""
        UPDATE cell_member_links cml
        SET tenant_id = COALESCE(c.tenant_id, cm.tenant_id, {_default_tenant_sql()})
        FROM cells c, cell_members cm
        WHERE cml.cell_id = c.id
          AND cml.member_id = cm.id
          AND cml.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE cell_leader_assignments cla
        SET tenant_id = COALESCE(c.tenant_id, cm.tenant_id, {_default_tenant_sql()})
        FROM cells c, cell_members cm
        WHERE cla.cell_id = c.id
          AND cla.member_id = cm.id
          AND cla.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE cell_meetings mt
        SET tenant_id = COALESCE(c.tenant_id, {_default_tenant_sql()})
        FROM cells c
        WHERE mt.cell_id = c.id
          AND mt.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE cell_meeting_attendances cma
        SET tenant_id = COALESCE(mt.tenant_id, cm.tenant_id, {_default_tenant_sql()})
        FROM cell_meetings mt, cell_members cm
        WHERE cma.meeting_id = mt.id
          AND cma.member_id = cm.id
          AND cma.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE cell_meeting_visitors cmv
        SET tenant_id = COALESCE(mt.tenant_id, cv.tenant_id, {_default_tenant_sql()})
        FROM cell_meetings mt, cell_visitors cv
        WHERE cmv.meeting_id = mt.id
          AND cmv.visitor_id = cv.id
          AND cmv.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE lost_sheep ls
        SET tenant_id = COALESCE(
            (SELECT tenant_id FROM cells WHERE id = ls.previous_cell_id),
            (SELECT tenant_id FROM cells WHERE id = ls.current_cell_id),
            (SELECT tenant_id FROM cell_members WHERE id = ls.member_id),
            {_default_tenant_sql()}
        )
        WHERE ls.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE bible_school_classes bsc
        SET tenant_id = COALESCE(bc.tenant_id, {_default_tenant_sql()})
        FROM bible_school_courses bc
        WHERE bsc.course_id = bc.id
          AND bsc.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE bible_school_lessons bsl
        SET tenant_id = COALESCE(
            (SELECT tenant_id FROM bible_school_classes WHERE id = bsl.class_id),
            (SELECT tenant_id FROM bible_school_professors WHERE id = bsl.professor_id),
            {_default_tenant_sql()}
        )
        WHERE bsl.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE bible_school_students bss
        SET tenant_id = COALESCE(bsc.tenant_id, {_default_tenant_sql()})
        FROM bible_school_classes bsc
        WHERE bss.class_id = bsc.id
          AND bss.tenant_id IS NULL
        """
    )
    op.execute(
        f"""
        UPDATE bible_school_attendance bsa
        SET tenant_id = COALESCE(bsl.tenant_id, bss.tenant_id, {_default_tenant_sql()})
        FROM bible_school_lessons bsl, bible_school_students bss
        WHERE bsa.lesson_id = bsl.id
          AND bsa.student_id = bss.id
          AND bsa.tenant_id IS NULL
        """
    )

    op.execute("ALTER TABLE roles DROP CONSTRAINT IF EXISTS roles_name_key")
    op.execute("DROP INDEX IF EXISTS ix_roles_name")
    op.create_unique_constraint("uq_roles_tenant_name", "roles", ["tenant_id", "name"])
    op.execute("CREATE INDEX IF NOT EXISTS ix_roles_name ON roles (name)")

    op.execute("ALTER TABLE categories DROP CONSTRAINT IF EXISTS categories_name_key")
    op.create_unique_constraint("uq_categories_tenant_name", "categories", ["tenant_id", "name"])

    op.execute("ALTER TABLE ministries DROP CONSTRAINT IF EXISTS ministries_name_key")
    op.create_unique_constraint("uq_ministries_tenant_name", "ministries", ["tenant_id", "name"])


def downgrade() -> None:
    op.drop_constraint("uq_ministries_tenant_name", "ministries", type_="unique")
    op.execute("ALTER TABLE ministries ADD CONSTRAINT ministries_name_key UNIQUE (name)")

    op.drop_constraint("uq_categories_tenant_name", "categories", type_="unique")
    op.execute("ALTER TABLE categories ADD CONSTRAINT categories_name_key UNIQUE (name)")

    op.drop_constraint("uq_roles_tenant_name", "roles", type_="unique")
    op.execute("DROP INDEX IF EXISTS ix_roles_name")
    op.execute("ALTER TABLE roles ADD CONSTRAINT roles_name_key UNIQUE (name)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_roles_name ON roles (name)")

    for table_name in reversed(TENANT_TABLES):
        op.drop_constraint(f"fk_{table_name}_tenant_id", table_name, type_="foreignkey")
        op.drop_index(f"ix_{table_name}_tenant_id", table_name=table_name)
        op.drop_column(table_name, "tenant_id")
