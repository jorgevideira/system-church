import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.child_checkin import ChildCheckinSettings


DEFAULT_OPS_CONTEXT_PRESETS: list[dict[str, str]] = [
    {"label": "Dom 09h", "context_name": "Culto Domingo 09h"},
    {"label": "Dom 19h", "context_name": "Culto Domingo 19h"},
    {"label": "Qua 20h", "context_name": "Culto Quarta 20h"},
]


def _safe_json_loads(raw: str | None) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def _normalize_presets(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []

    out: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        context_name = str(item.get("context_name") or "").strip()
        if not label or not context_name:
            continue
        out.append(
            {
                "label": label[:40],
                "context_name": context_name[:255],
            }
        )
        if len(out) >= 12:
            break
    return out


def get_settings(db: Session, tenant_id: int) -> dict[str, Any]:
    row = (
        db.query(ChildCheckinSettings)
        .filter(ChildCheckinSettings.tenant_id == tenant_id)
        .first()
    )
    if row is None or row.ops_context_presets_json is None:
        return {"ops_context_presets": list(DEFAULT_OPS_CONTEXT_PRESETS)}

    loaded = _safe_json_loads(row.ops_context_presets_json)
    if loaded is None:
        return {"ops_context_presets": list(DEFAULT_OPS_CONTEXT_PRESETS)}

    presets = _normalize_presets(loaded)
    return {"ops_context_presets": presets}


def upsert_settings(db: Session, tenant_id: int, ops_context_presets: Any) -> dict[str, Any]:
    presets = _normalize_presets(ops_context_presets)
    payload_json = json.dumps(presets, ensure_ascii=True)

    row = (
        db.query(ChildCheckinSettings)
        .filter(ChildCheckinSettings.tenant_id == tenant_id)
        .first()
    )
    now = datetime.now(timezone.utc)
    if row is None:
        row = ChildCheckinSettings(
            tenant_id=tenant_id,
            ops_context_presets_json=payload_json,
            created_at=now,
            updated_at=now,
        )
        db.add(row)
    else:
        row.ops_context_presets_json = payload_json
        row.updated_at = now

    db.commit()
    return {"ops_context_presets": presets}
