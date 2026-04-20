from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx

from app.core.config import settings


def _resolve_gateway_base_url() -> str | None:
    raw = (settings.WHATSAPP_WEBHOOK_URL or "").strip()
    if not raw:
        return None

    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        return None

    path = parsed.path.rstrip("/")
    if path.endswith("/send"):
        path = path[:-5]
    base_path = path.rstrip("/")
    return urlunparse((parsed.scheme, parsed.netloc, base_path, "", "", "")).rstrip("/")


def is_gateway_enabled() -> bool:
    return bool(_resolve_gateway_base_url())


def _request(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    include_gateway_token: bool = False,
) -> Any:
    base_url = _resolve_gateway_base_url()
    if not base_url:
        raise RuntimeError("WhatsApp gateway is not configured in this environment.")

    url = f"{base_url}{path}"
    headers: dict[str, str] = {}
    if include_gateway_token and settings.WHATSAPP_WEBHOOK_TOKEN:
        headers["Authorization"] = f"Bearer {settings.WHATSAPP_WEBHOOK_TOKEN}"
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.request(method, url, json=payload, headers=headers or None)
    except Exception as exc:
        raise RuntimeError(f"Could not reach WhatsApp gateway: {exc}") from exc

    try:
        data = response.json() if response.content else {}
    except ValueError:
        data = {"raw": response.text}

    if response.is_error:
        detail = data.get("detail") if isinstance(data, dict) else None
        if isinstance(detail, str) and detail:
            raise RuntimeError(detail)
        raise RuntimeError(f"WhatsApp gateway returned {response.status_code}.")
    return data


def get_status() -> dict[str, Any]:
    if not is_gateway_enabled():
        return {
            "enabled": False,
            "configured": False,
            "mode": "disabled",
            "instance_exists": False,
            "reachable": False,
        }
    data = _request("GET", "/evolution/status")
    if isinstance(data, dict):
        data.setdefault("enabled", True)
        data.setdefault("configured", True)
    return data


def setup_instance() -> dict[str, Any]:
    return _request("POST", "/evolution/setup")


def connect_instance(number: str | None = None) -> dict[str, Any]:
    payload = {"number": number} if number else {}
    return _request("POST", "/evolution/connect", payload=payload)


def logout_instance() -> dict[str, Any]:
    return _request("POST", "/evolution/logout")


def send_test_message(to_phone: str) -> dict[str, Any]:
    sanitized_phone = "".join(char for char in str(to_phone or "") if char.isdigit())
    if len(sanitized_phone) < 8:
        raise RuntimeError("Informe um telefone valido para enviar o teste.")

    sent_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    payload = {
        "to": sanitized_phone,
        "message": (
            "Teste do WhatsApp em dev enviado pelo System Church.\n"
            f"Horario do disparo: {sent_at}"
        ),
    }
    return _request("POST", "/send", payload=payload, include_gateway_token=True)
