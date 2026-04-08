import hashlib
import hmac
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.db.models.tenant import Tenant
from app.services import tenant_service


MERCADOPAGO_API_BASE_URL = "https://api.mercadopago.com"


def is_enabled(tenant: Tenant | None = None) -> bool:
    return tenant_service.get_payment_provider(tenant) == "mercadopago" and bool(tenant_service.get_mercadopago_access_token(tenant))


def _build_headers(tenant: Tenant | None = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {tenant_service.get_mercadopago_access_token(tenant)}",
        "Content-Type": "application/json",
    }
    integrator_id = tenant_service.get_mercadopago_integrator_id(tenant)
    if integrator_id:
        headers["x-integrator-id"] = integrator_id
    return headers


def create_checkout_preference(
    tenant: Tenant,
    *,
    event_title: str,
    registration_code: str,
    checkout_reference: str,
    amount: Decimal,
    quantity: int,
    attendee_name: str,
    attendee_email: str,
    preferred_method: Optional[str],
) -> dict[str, Any]:
    if not is_enabled(tenant):
        raise ValueError("Mercado Pago is not configured")

    notification_url = f"{settings.APP_BASE_URL}{settings.API_V1_STR}/events/public/payments/webhook"
    success_url = f"{settings.PUBLIC_APP_URL}/events/registration/{checkout_reference}?status=success"
    pending_url = f"{settings.PUBLIC_APP_URL}/events/registration/{checkout_reference}?status=pending"
    failure_url = f"{settings.PUBLIC_APP_URL}/events/registration/{checkout_reference}?status=failure"

    excluded_payment_types: list[dict[str, str]] = []
    if preferred_method == "pix":
        excluded_payment_types = [{"id": "credit_card"}, {"id": "debit_card"}]
    elif preferred_method == "card":
        excluded_payment_types = [{"id": "bank_transfer"}, {"id": "ticket"}, {"id": "atm"}]

    payload = {
        "external_reference": checkout_reference,
        "notification_url": notification_url,
        "back_urls": {
            "success": success_url,
            "pending": pending_url,
            "failure": failure_url,
        },
        "items": [
            {
                "id": registration_code,
                "title": event_title,
                "description": f"Inscricao {registration_code}",
                "quantity": quantity,
                "currency_id": "BRL",
                "unit_price": float(amount / quantity),
            }
        ],
        "payer": {
            "name": attendee_name,
            "email": attendee_email,
        },
        "metadata": {
            "tenant_slug": tenant.slug,
            "checkout_reference": checkout_reference,
            "preferred_method": preferred_method,
        },
        "payment_methods": {
            "excluded_payment_types": excluded_payment_types,
            "installments": 1 if preferred_method == "pix" else 12,
        },
    }

    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            f"{MERCADOPAGO_API_BASE_URL}/checkout/preferences",
            headers=_build_headers(tenant),
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def fetch_payment(payment_id: str, tenant: Tenant | None = None) -> dict[str, Any]:
    if not is_enabled(tenant):
        raise ValueError("Mercado Pago is not configured")
    with httpx.Client(timeout=20.0) as client:
        response = client.get(
            f"{MERCADOPAGO_API_BASE_URL}/v1/payments/{payment_id}",
            headers=_build_headers(tenant),
        )
        response.raise_for_status()
        return response.json()


def map_payment_status(provider_status: str) -> str:
    normalized = (provider_status or "").lower()
    if normalized == "approved":
        return "paid"
    if normalized in {"pending", "in_process", "in_mediation"}:
        return "pending"
    if normalized in {"authorized"}:
        return "pending"
    if normalized in {"cancelled"}:
        return "cancelled"
    if normalized in {"refunded", "charged_back"}:
        return "refunded"
    if normalized in {"rejected"}:
        return "failed"
    return "pending"


def parse_paid_at(payment_data: dict[str, Any]) -> Optional[datetime]:
    raw = payment_data.get("date_approved") or payment_data.get("date_last_updated")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def validate_webhook_signature(
    tenant: Tenant | None = None,
    *,
    data_id: Optional[str],
    x_signature: Optional[str],
    x_request_id: Optional[str],
) -> bool:
    webhook_secret = tenant_service.get_mercadopago_webhook_secret(tenant)
    if not webhook_secret:
        return True
    if not data_id or not x_signature or not x_request_id:
        return False

    parts = {}
    for chunk in x_signature.split(","):
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        parts[key.strip()] = value.strip()

    ts = parts.get("ts")
    expected_hash = parts.get("v1")
    if not ts or not expected_hash:
        return False

    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    digest = hmac.new(
        webhook_secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(digest, expected_hash)
