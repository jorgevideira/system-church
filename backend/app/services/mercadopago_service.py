import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.db.models.payment_account import PaymentAccount
from app.db.models.tenant import Tenant
from app.services import payment_account_service, tenant_service


MERCADOPAGO_API_BASE_URL = "https://api.mercadopago.com"


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        cause = payload.get("cause")
        if isinstance(cause, list) and cause:
            first = cause[0]
            if isinstance(first, dict):
                description = str(first.get("description") or first.get("code") or "").strip()
                if description:
                    return description
        for key in ("message", "error", "status"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        serialized = json.dumps(payload, ensure_ascii=False)
        if serialized:
            return serialized
    return response.text.strip() or f"HTTP {response.status_code}"


def _format_mp_datetime(value: datetime) -> str:
    formatted = value.astimezone().strftime("%Y-%m-%dT%H:%M:%S.000%z")
    return f"{formatted[:-2]}:{formatted[-2:]}"


def _resolve_access_token(tenant: Tenant | None = None, payment_account: PaymentAccount | None = None) -> str | None:
    token = payment_account_service.get_account_access_token(payment_account)
    if token:
        return token
    return tenant_service.get_mercadopago_access_token(tenant)


def _resolve_public_key(tenant: Tenant | None = None, payment_account: PaymentAccount | None = None) -> str | None:
    public_key = payment_account_service.get_account_public_key(payment_account)
    if public_key:
        return public_key
    return tenant_service.get_mercadopago_public_key(tenant)


def _resolve_webhook_secret(tenant: Tenant | None = None, payment_account: PaymentAccount | None = None) -> str | None:
    webhook_secret = payment_account_service.get_account_webhook_secret(payment_account)
    if webhook_secret:
        return webhook_secret
    return tenant_service.get_mercadopago_webhook_secret(tenant)


def _resolve_integrator_id(tenant: Tenant | None = None, payment_account: PaymentAccount | None = None) -> str | None:
    integrator_id = payment_account_service.get_account_integrator_id(payment_account)
    if integrator_id:
        return integrator_id
    return tenant_service.get_mercadopago_integrator_id(tenant)


def is_enabled(tenant: Tenant | None = None, payment_account: PaymentAccount | None = None) -> bool:
    provider = payment_account.provider if payment_account is not None else tenant_service.get_payment_provider(tenant)
    return provider == "mercadopago" and bool(_resolve_access_token(tenant, payment_account))


def _build_headers(
    tenant: Tenant | None = None,
    payment_account: PaymentAccount | None = None,
    *,
    idempotency_key: str | None = None,
) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {_resolve_access_token(tenant, payment_account)}",
        "Content-Type": "application/json",
    }
    integrator_id = _resolve_integrator_id(tenant, payment_account)
    if integrator_id:
        headers["x-integrator-id"] = integrator_id
    if idempotency_key:
        headers["X-Idempotency-Key"] = idempotency_key
    return headers


def create_checkout_preference(
    tenant: Tenant,
    payment_account: PaymentAccount | None,
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
    if not is_enabled(tenant, payment_account):
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
            headers=_build_headers(tenant, payment_account),
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def create_pix_payment(
    tenant: Tenant,
    payment_account: PaymentAccount | None,
    *,
    event_title: str,
    registration_code: str,
    checkout_reference: str,
    amount: Decimal,
    attendee_name: str,
    attendee_email: str,
) -> dict[str, Any]:
    if not is_enabled(tenant, payment_account):
        raise ValueError("Mercado Pago is not configured")

    notification_url = f"{settings.APP_BASE_URL}{settings.API_V1_STR}/events/public/payments/webhook"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    first_name, _, last_name = attendee_name.strip().partition(" ")
    payload = {
        "transaction_amount": float(amount),
        "description": f"{event_title} - {registration_code}",
        "payment_method_id": "pix",
        "external_reference": checkout_reference,
        "notification_url": notification_url,
        "date_of_expiration": _format_mp_datetime(expires_at),
        "payer": {
            "email": attendee_email,
            "first_name": first_name or attendee_name.strip(),
            "last_name": last_name or "-",
        },
    }

    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            f"{MERCADOPAGO_API_BASE_URL}/v1/payments",
            headers=_build_headers(tenant, payment_account, idempotency_key=checkout_reference),
            json=payload,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            error_message = _extract_error_message(exc.response)
            raise ValueError(f"Mercado Pago recusou o PIX transparente: {error_message}") from exc
        return response.json()


def extract_pix_payment_data(payment_data: dict[str, Any]) -> dict[str, str | None]:
    point_of_interaction = payment_data.get("point_of_interaction") or {}
    transaction_data = point_of_interaction.get("transaction_data") or {}
    return {
        "qr_code": transaction_data.get("qr_code"),
        "qr_code_base64": transaction_data.get("qr_code_base64"),
        "ticket_url": transaction_data.get("ticket_url"),
    }


def parse_expires_at(payment_data: dict[str, Any]) -> Optional[datetime]:
    raw = payment_data.get("date_of_expiration")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_payment(payment_id: str, tenant: Tenant | None = None, payment_account: PaymentAccount | None = None) -> dict[str, Any]:
    if not is_enabled(tenant, payment_account):
        raise ValueError("Mercado Pago is not configured")
    with httpx.Client(timeout=20.0) as client:
        response = client.get(
            f"{MERCADOPAGO_API_BASE_URL}/v1/payments/{payment_id}",
            headers=_build_headers(tenant, payment_account),
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
    payment_account: PaymentAccount | None = None,
    *,
    data_id: Optional[str],
    x_signature: Optional[str],
    x_request_id: Optional[str],
) -> bool:
    webhook_secret = _resolve_webhook_secret(tenant, payment_account)
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
