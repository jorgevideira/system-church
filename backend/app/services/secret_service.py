import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


ENCRYPTED_PREFIX = "enc::"


def _build_fernet() -> Fernet:
    raw_key = settings.SECRETS_ENCRYPTION_KEY or settings.SECRET_KEY
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    fernet_key = base64.urlsafe_b64encode(digest)
    return Fernet(fernet_key)


def encrypt_value(value: str | None) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    if normalized.startswith(ENCRYPTED_PREFIX):
        return normalized
    token = _build_fernet().encrypt(normalized.encode("utf-8")).decode("utf-8")
    return f"{ENCRYPTED_PREFIX}{token}"


def decrypt_value(value: str | None) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    if not normalized.startswith(ENCRYPTED_PREFIX):
        return normalized
    encrypted_token = normalized[len(ENCRYPTED_PREFIX):]
    try:
        return _build_fernet().decrypt(encrypted_token.encode("utf-8")).decode("utf-8").strip() or None
    except InvalidToken:
        return None
