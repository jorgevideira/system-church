import secrets
from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import settings


MERCADOPAGO_AUTH_BASE_URL = "https://auth.mercadopago.com/authorization"
MERCADOPAGO_API_BASE_URL = "https://api.mercadopago.com"


def is_enabled() -> bool:
    return bool(settings.MERCADOPAGO_OAUTH_CLIENT_ID and settings.MERCADOPAGO_OAUTH_CLIENT_SECRET)


def get_redirect_uri() -> str:
    return settings.MERCADOPAGO_OAUTH_REDIRECT_URI or f"{settings.APP_BASE_URL}{settings.API_V1_STR}/payment-accounts/oauth/mercadopago/callback"


def build_authorize_url(state: str) -> str:
    if not is_enabled():
        raise ValueError("Mercado Pago OAuth is not configured")
    query = urlencode(
        {
            "client_id": settings.MERCADOPAGO_OAUTH_CLIENT_ID,
            "response_type": "code",
            "platform_id": "mp",
            "state": state,
            "redirect_uri": get_redirect_uri(),
        }
    )
    return f"{MERCADOPAGO_AUTH_BASE_URL}?{query}"


def generate_state() -> str:
    return secrets.token_urlsafe(24)


def exchange_code(code: str) -> dict[str, Any]:
    if not is_enabled():
        raise ValueError("Mercado Pago OAuth is not configured")
    payload = {
        "client_id": settings.MERCADOPAGO_OAUTH_CLIENT_ID,
        "client_secret": settings.MERCADOPAGO_OAUTH_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": get_redirect_uri(),
    }
    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            f"{MERCADOPAGO_API_BASE_URL}/oauth/token",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def refresh_access_token(refresh_token: str) -> dict[str, Any]:
    if not is_enabled():
        raise ValueError("Mercado Pago OAuth is not configured")
    payload = {
        "client_id": settings.MERCADOPAGO_OAUTH_CLIENT_ID,
        "client_secret": settings.MERCADOPAGO_OAUTH_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            f"{MERCADOPAGO_API_BASE_URL}/oauth/token",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def fetch_user_profile(access_token: str) -> dict[str, Any]:
    with httpx.Client(timeout=20.0) as client:
        response = client.get(
            f"{MERCADOPAGO_API_BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()
