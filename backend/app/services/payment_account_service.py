from sqlalchemy.orm import Session

from app.db.models.payment_account import PaymentAccount
from app.schemas.payment_account import PaymentAccountCreate, PaymentAccountResponse, PaymentAccountUpdate


def _normalize_public_config(payload: PaymentAccountCreate | PaymentAccountUpdate) -> dict:
    return {
        "public_key": getattr(payload, "public_key", None) or None,
        "webhook_secret": getattr(payload, "webhook_secret", None) or None,
        "integrator_id": getattr(payload, "integrator_id", None) or None,
        "account_email": getattr(payload, "account_email", None) or None,
        "app_id": getattr(payload, "app_id", None) or None,
    }


def _normalize_secrets(payload: PaymentAccountCreate | PaymentAccountUpdate) -> dict:
    return {
        "access_token": getattr(payload, "access_token", None) or None,
    }


def _build_response(account: PaymentAccount) -> PaymentAccountResponse:
    config = account.config_json or {}
    secrets = account.secrets_json or {}
    access_token = str(secrets.get("access_token") or "").strip()
    webhook_secret = str(config.get("webhook_secret") or "").strip()
    public_key = str(config.get("public_key") or "").strip()
    live_ready = account.provider in {"mercadopago", "pagbank"} and bool(access_token) and bool(public_key)
    return PaymentAccountResponse(
        id=account.id,
        tenant_id=account.tenant_id,
        provider=account.provider,
        label=account.label,
        description=account.description,
        is_default=account.is_default,
        is_active=account.is_active,
        supports_pix=account.supports_pix,
        supports_card=account.supports_card,
        public_key=public_key or None,
        webhook_secret_configured=bool(webhook_secret),
        integrator_id=(config.get("integrator_id") or None),
        account_email=(config.get("account_email") or None),
        app_id=(config.get("app_id") or None),
        access_token_configured=bool(access_token),
        live_ready=live_ready,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


def list_payment_accounts(db: Session, tenant_id: int) -> list[PaymentAccount]:
    return (
        db.query(PaymentAccount)
        .filter(PaymentAccount.tenant_id == tenant_id)
        .order_by(PaymentAccount.is_default.desc(), PaymentAccount.label.asc(), PaymentAccount.id.asc())
        .all()
    )


def list_payment_account_responses(db: Session, tenant_id: int) -> list[PaymentAccountResponse]:
    return [_build_response(account) for account in list_payment_accounts(db, tenant_id)]


def get_payment_account(db: Session, account_id: int, tenant_id: int) -> PaymentAccount | None:
    return (
        db.query(PaymentAccount)
        .filter(PaymentAccount.id == account_id, PaymentAccount.tenant_id == tenant_id)
        .first()
    )


def _ensure_unique_label(db: Session, tenant_id: int, label: str, exclude_id: int | None = None) -> None:
    query = db.query(PaymentAccount.id).filter(PaymentAccount.tenant_id == tenant_id, PaymentAccount.label == label)
    if exclude_id is not None:
        query = query.filter(PaymentAccount.id != exclude_id)
    if query.first() is not None:
        raise ValueError("Payment account label is already in use for this church")


def _clear_other_defaults(db: Session, tenant_id: int, exclude_id: int | None = None) -> None:
    query = db.query(PaymentAccount).filter(PaymentAccount.tenant_id == tenant_id, PaymentAccount.is_default.is_(True))
    if exclude_id is not None:
        query = query.filter(PaymentAccount.id != exclude_id)
    for row in query.all():
        row.is_default = False


def create_payment_account(db: Session, tenant_id: int, payload: PaymentAccountCreate) -> PaymentAccount:
    label = payload.label.strip()
    _ensure_unique_label(db, tenant_id, label)
    if payload.is_default:
        _clear_other_defaults(db, tenant_id)
    account = PaymentAccount(
        tenant_id=tenant_id,
        provider=payload.provider,
        label=label,
        description=(payload.description or "").strip() or None,
        is_default=bool(payload.is_default),
        is_active=bool(payload.is_active),
        supports_pix=bool(payload.supports_pix),
        supports_card=bool(payload.supports_card),
        config_json=_normalize_public_config(payload),
        secrets_json=_normalize_secrets(payload),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_payment_account(db: Session, account: PaymentAccount, payload: PaymentAccountUpdate) -> PaymentAccount:
    changes = payload.model_dump(exclude_unset=True)
    if "label" in changes and changes["label"]:
        changes["label"] = changes["label"].strip()
        _ensure_unique_label(db, account.tenant_id, changes["label"], exclude_id=account.id)

    if changes.get("is_default") is True:
        _clear_other_defaults(db, account.tenant_id, exclude_id=account.id)

    for field in ("provider", "label", "description", "is_default", "is_active", "supports_pix", "supports_card"):
        if field in changes:
            value = changes[field]
            if isinstance(value, str):
                value = value.strip() or None
            setattr(account, field, value)

    config = dict(account.config_json or {})
    for key in ("public_key", "webhook_secret", "integrator_id", "account_email", "app_id"):
        if key in changes:
            config[key] = (changes[key] or "").strip() or None
    if payload.clear_webhook_secret:
        config["webhook_secret"] = None
    account.config_json = config

    secrets = dict(account.secrets_json or {})
    if "access_token" in changes:
        secrets["access_token"] = (changes["access_token"] or "").strip() or None
    if payload.clear_access_token:
        secrets["access_token"] = None
    account.secrets_json = secrets

    db.commit()
    db.refresh(account)
    return account


def delete_payment_account(db: Session, account: PaymentAccount) -> None:
    db.delete(account)
    db.commit()


def to_response(account: PaymentAccount) -> PaymentAccountResponse:
    return _build_response(account)


def get_account_access_token(account: PaymentAccount | None) -> str | None:
    if account is None:
        return None
    secrets = account.secrets_json or {}
    token = str(secrets.get("access_token") or "").strip()
    return token or None


def get_account_public_key(account: PaymentAccount | None) -> str | None:
    if account is None:
        return None
    config = account.config_json or {}
    public_key = str(config.get("public_key") or "").strip()
    return public_key or None


def get_account_webhook_secret(account: PaymentAccount | None) -> str | None:
    if account is None:
        return None
    config = account.config_json or {}
    webhook_secret = str(config.get("webhook_secret") or "").strip()
    return webhook_secret or None


def get_account_integrator_id(account: PaymentAccount | None) -> str | None:
    if account is None:
        return None
    config = account.config_json or {}
    integrator_id = str(config.get("integrator_id") or "").strip()
    return integrator_id or None
