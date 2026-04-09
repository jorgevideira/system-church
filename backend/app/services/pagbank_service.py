from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.db.models.payment_account import PaymentAccount
from app.db.models.tenant import Tenant
from app.services import payment_account_service


PAGBANK_API_BASE_URL = "https://api.pagseguro.com"
PAGBANK_SANDBOX_API_BASE_URL = "https://sandbox.api.pagseguro.com"


def _resolve_access_token(payment_account: PaymentAccount | None = None) -> str | None:
    return payment_account_service.get_account_access_token(payment_account)


def _resolve_environment(payment_account: PaymentAccount | None = None) -> str:
    return payment_account_service.get_account_environment(payment_account)


def _resolve_api_base_url(payment_account: PaymentAccount | None = None) -> str:
    return PAGBANK_SANDBOX_API_BASE_URL if _resolve_environment(payment_account) == "sandbox" else PAGBANK_API_BASE_URL


def is_enabled(_tenant: Tenant | None = None, payment_account: PaymentAccount | None = None) -> bool:
    return payment_account is not None and payment_account.provider == "pagbank" and bool(_resolve_access_token(payment_account))


def _build_headers(payment_account: PaymentAccount | None = None) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_resolve_access_token(payment_account)}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _parse_phone(phone: str | None) -> dict[str, str] | None:
    digits = "".join(ch for ch in str(phone or "") if ch.isdigit())
    if len(digits) < 10:
        return None
    if digits.startswith("55") and len(digits) >= 12:
        digits = digits[2:]
    area = digits[:2]
    number = digits[2:11]
    if len(number) < 8:
        return None
    return {"country": "+55", "area": area, "number": number}


def _build_payment_methods(preferred_method: Optional[str]) -> list[dict[str, Any]]:
    if preferred_method == "pix":
        return [{"type": "PIX"}]
    if preferred_method == "card":
        return [{"type": "CREDIT_CARD"}]
    return [{"type": "PIX"}, {"type": "CREDIT_CARD"}]


def _amount_to_cents(amount: Decimal) -> int:
    return int((amount * 100).quantize(Decimal("1")))


def get_checkout_link(payload: dict[str, Any], rel: str = "PAY") -> str | None:
    links = payload.get("links") or []
    for link in links or []:
        if str(link.get("rel") or "").upper() == rel.upper():
            href = str(link.get("href") or "").strip()
            if href:
                return href
    return None


def create_checkout(
    tenant: Tenant,
    payment_account: PaymentAccount,
    *,
    event_title: str,
    registration_code: str,
    checkout_reference: str,
    amount: Decimal,
    quantity: int,
    attendee_name: str,
    attendee_email: str,
    attendee_phone: str | None,
    preferred_method: Optional[str],
) -> dict[str, Any]:
    if not is_enabled(tenant, payment_account):
        raise ValueError("PagBank is not configured")

    webhook_url = f"{settings.APP_BASE_URL}{settings.API_V1_STR}/events/public/payments/webhook"
    payment_status_url = f"{settings.PUBLIC_APP_URL}/events/registration/{checkout_reference}"
    payload: dict[str, Any] = {
        "reference_id": checkout_reference,
        "redirect_url": payment_status_url,
        "return_url": payment_status_url,
        "expiration_date": (datetime.now(timezone.utc) + timedelta(minutes=30)).replace(microsecond=0).isoformat(),
        "notification_urls": [webhook_url],
        "payment_notification_urls": [webhook_url],
        "customer_modifiable": True,
        "items": [
            {
                "reference_id": registration_code,
                "name": event_title[:100],
                "description": f"Inscricao {registration_code}"[:255],
                "quantity": quantity,
                "unit_amount": _amount_to_cents(amount / quantity),
            }
        ],
        "payment_methods": _build_payment_methods(preferred_method),
    }

    phone = _parse_phone(attendee_phone)
    customer: dict[str, Any] = {"name": attendee_name[:120], "email": attendee_email}
    if phone:
        customer["phone"] = phone
    payload["customer"] = customer

    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            f"{_resolve_api_base_url(payment_account)}/checkouts",
            headers=_build_headers(payment_account),
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def map_payment_status(provider_status: str | None) -> str:
    normalized = str(provider_status or "").strip().upper()
    if normalized in {"PAID", "AUTHORIZED", "AVAILABLE"}:
        return "paid"
    if normalized in {"WAITING", "IN_ANALYSIS"}:
        return "pending"
    if normalized in {"DECLINED"}:
        return "failed"
    if normalized in {"CANCELED", "CANCELLED"}:
        return "cancelled"
    if normalized in {"EXPIRED"}:
        return "expired"
    if normalized in {"REFUNDED"}:
        return "refunded"
    return "pending"


def parse_paid_at(raw_value: str | None) -> Optional[datetime]:
    if not raw_value:
        return None
    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def build_webhook_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    checkout_reference = str(payload.get("reference_id") or "").strip()
    charges = payload.get("charges") or []
    charge = charges[0] if charges else None
    if not checkout_reference and isinstance(charge, dict):
        checkout_reference = str(charge.get("reference_id") or "").strip()
    if not checkout_reference:
        return None

    provider_reference = None
    status = "pending"
    paid_at = None
    if isinstance(charge, dict):
        provider_reference = str(charge.get("id") or charge.get("reference_id") or "").strip() or None
        status = map_payment_status(charge.get("status"))
        paid_at = parse_paid_at(charge.get("paid_at") or charge.get("created_at"))
    elif payload.get("status"):
        status = map_payment_status(payload.get("status"))

    return {
        "checkout_reference": checkout_reference,
        "status": status,
        "provider_reference": provider_reference,
        "paid_at": paid_at,
        "provider_payload": payload,
    }
