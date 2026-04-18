"""
Preflight check for production migrations.

Why:
- Migration 030 creates a unique index on (tenant_id, lower(email)) for child_checkin_families.
- If there are duplicate emails (case-insensitive) within the same tenant, the migration will fail.

Run inside the backend container (recommended):
  python backend/scripts/preflight_child_checkin_email_uniqueness.py

Exit codes:
- 0: OK (no duplicates found, or table doesn't exist yet)
- 2: Duplicates found (migration would likely fail)
"""

from __future__ import annotations

import sys

from sqlalchemy import create_engine, text

from app.core.config import settings


def main() -> int:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    with engine.connect() as conn:
        # If the table doesn't exist yet, nothing to validate.
        has_table = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = 'child_checkin_families'
                LIMIT 1
                """
            )
        ).scalar()
        if not has_table:
            print("OK: tabela child_checkin_families ainda nao existe; nada para validar.")
            return 0

        rows = conn.execute(
            text(
                """
                SELECT
                  tenant_id,
                  lower(email) AS email_lower,
                  COUNT(*) AS qtd
                FROM child_checkin_families
                WHERE email IS NOT NULL
                  AND email <> ''
                GROUP BY tenant_id, lower(email)
                HAVING COUNT(*) > 1
                ORDER BY qtd DESC, tenant_id ASC, email_lower ASC
                LIMIT 50
                """
            )
        ).fetchall()

    if not rows:
        print("OK: nenhum e-mail duplicado (case-insensitive) encontrado por tenant.")
        return 0

    print("ERRO: existem e-mails duplicados (case-insensitive) por tenant em child_checkin_families.")
    print("A migration 030 vai falhar ate corrigir esses dados.")
    print("")
    print("Exemplos (tenant_id | email_lower | qtd):")
    for r in rows:
        print(f"- {r.tenant_id} | {r.email_lower} | {r.qtd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

