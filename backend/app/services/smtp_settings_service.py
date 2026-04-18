from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy.orm import Session

from app.core.config import settings as global_settings
from app.db.models.tenant_smtp_settings import TenantSmtpSettings
from app.services import secret_service

import smtplib
from email.message import EmailMessage


@dataclass(frozen=True)
class EffectiveSmtpConfig:
    host: str
    port: int
    username: str | None
    password: str | None
    from_email: str | None
    encryption: str  # "tls" | "ssl" | "none"


def get_tenant_smtp_settings(db: Session, tenant_id: int) -> Optional[TenantSmtpSettings]:
    try:
        return db.query(TenantSmtpSettings).filter(TenantSmtpSettings.tenant_id == tenant_id).first()
    except (ProgrammingError, OperationalError):
        # Table might not exist yet if migrations haven't been applied in this environment.
        return None


def upsert_tenant_smtp_settings(
    db: Session,
    *,
    tenant_id: int,
    host: str,
    port: int,
    username: str | None,
    password: str | None,
    from_email: str | None,
    encryption: str,
    is_active: bool,
) -> TenantSmtpSettings:
    try:
        current = db.query(TenantSmtpSettings).filter(TenantSmtpSettings.tenant_id == tenant_id).first()
    except (ProgrammingError, OperationalError) as exc:
        raise ValueError("SMTP schema is not ready yet. Apply migrations and restart the backend.") from exc
    if current is None:
        current = TenantSmtpSettings(tenant_id=tenant_id, host=host.strip(), port=int(port or 587))
        db.add(current)

    current.host = host.strip()
    current.port = int(port or 587)
    current.username = (username or "").strip() or None
    current.from_email = (from_email or "").strip() or None
    current.encryption = (encryption or "tls").strip().lower()
    current.is_active = bool(is_active)

    # Password update semantics:
    # - None => keep as-is
    # - ""   => clear
    # - value => set encrypted
    if password is not None:
        normalized = str(password).strip()
        current.password = secret_service.encrypt_value(normalized or None)

    db.commit()
    db.refresh(current)
    return current


def resolve_effective_smtp_config(db: Session, tenant_id: int) -> EffectiveSmtpConfig | None:
    tenant_cfg = get_tenant_smtp_settings(db, tenant_id)
    if tenant_cfg and tenant_cfg.is_active and tenant_cfg.host:
        return EffectiveSmtpConfig(
            host=tenant_cfg.host,
            port=int(tenant_cfg.port or 587),
            username=tenant_cfg.username,
            password=secret_service.decrypt_value(tenant_cfg.password),
            from_email=tenant_cfg.from_email,
            encryption=(tenant_cfg.encryption or "tls").strip().lower(),
        )

    # Fallback to global env configuration (legacy behavior).
    if not global_settings.SMTP_HOST:
        return None
    return EffectiveSmtpConfig(
        host=str(global_settings.SMTP_HOST),
        port=int(global_settings.SMTP_PORT or 587),
        username=global_settings.SMTP_USERNAME,
        password=global_settings.SMTP_PASSWORD,
        from_email=global_settings.SMTP_FROM_EMAIL,
        encryption="tls" if global_settings.SMTP_USE_TLS else "none",
    )


def send_test_email(db: Session, tenant_id: int, *, to_email: str) -> None:
    cfg = resolve_effective_smtp_config(db, tenant_id)
    if cfg is None or not cfg.host or not cfg.from_email:
        raise ValueError("SMTP not configured for this church")

    message = EmailMessage()
    message["Subject"] = "Teste de SMTP | Sistema Church"
    message["From"] = cfg.from_email
    message["To"] = to_email
    message.set_content(
        "Este e-mail é um teste de envio SMTP.\n\n"
        "Se você recebeu esta mensagem, a configuração de SMTP está funcionando corretamente.\n"
    )

    if cfg.encryption == "ssl":
        server: smtplib.SMTP = smtplib.SMTP_SSL(cfg.host, cfg.port, timeout=20)
    else:
        server = smtplib.SMTP(cfg.host, cfg.port, timeout=20)
    try:
        if cfg.encryption == "tls":
            server.starttls()
        if cfg.username and cfg.password:
            server.login(cfg.username, cfg.password)
        server.send_message(message)
    finally:
        try:
            server.quit()
        except Exception:
            server.close()
