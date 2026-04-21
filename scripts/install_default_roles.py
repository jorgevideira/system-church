#!/usr/bin/env python3
"""Install standard role templates for active tenants."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.models.tenant import Tenant  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services import role_templates_service  # noqa: E402


def main() -> int:
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter(Tenant.is_active.is_(True)).order_by(Tenant.id.asc()).all()
        if not tenants:
            print("No active tenants found.")
            return 0

        for tenant in tenants:
            installed = role_templates_service.install_default_roles_for_tenant(db, tenant.id)
            print(f"tenant={tenant.id} slug={tenant.slug or '-'} roles={len(installed)}")

        print(f"Installed/defaulted roles for {len(tenants)} active tenant(s).")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
