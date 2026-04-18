from __future__ import annotations

from email.message import EmailMessage
import smtplib

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import qr_service, smtp_settings_service


def _smtp_or_raise(db: Session, tenant_id: int) -> smtp_settings_service.EffectiveSmtpConfig:
    cfg = smtp_settings_service.resolve_effective_smtp_config(db, tenant_id)
    if cfg is None or not cfg.host or not cfg.from_email:
        raise ValueError("SMTP nao configurado para esta igreja.")
    return cfg


def _send_message(cfg: smtp_settings_service.EffectiveSmtpConfig, message: EmailMessage) -> None:
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


def send_virtual_cards_email(
    db: Session,
    *,
    tenant_id: int,
    tenant_slug: str,
    to_email: str,
    family_code: str,
    cards: list[dict],
) -> None:
    cfg = _smtp_or_raise(db, tenant_id)

    public_base = str(settings.PUBLIC_APP_URL or "").rstrip("/")
    pass_link = ""
    if public_base and tenant_slug and family_code:
        pass_link = f"{public_base}/kids-pass.html?tenant={tenant_slug}&code={family_code}"

    message = EmailMessage()
    message["Subject"] = f"AppKids | Carteirinha ({family_code})"
    message["From"] = cfg.from_email
    message["To"] = to_email

    lines: list[str] = []
    lines.append("Sua carteirinha do AppKids foi gerada com sucesso.")
    lines.append("")
    lines.append(f"Codigo da familia: {family_code}")
    if pass_link:
        lines.append(f"Link para imprimir a carteirinha: {pass_link}")
    lines.append("")
    lines.append("QR Codes (um por crianca) seguem anexados neste e-mail.")
    message.set_content("\n".join(lines))

    for card in cards or []:
        qr_payload = str(card.get("qr_payload") or "").strip()
        child_name = str(card.get("child_name") or "crianca").strip()
        if not qr_payload:
            continue
        png = qr_service.build_qr_png(qr_payload)
        safe_name = "".join(ch for ch in child_name if ch.isalnum() or ch in {" ", "-", "_"}).strip().replace(" ", "_")[:40] or "crianca"
        message.add_attachment(png, maintype="image", subtype="png", filename=f"appkids_qr_{safe_name}.png")

    _send_message(cfg, message)


def send_recovery_code_email(
    db: Session,
    *,
    tenant_id: int,
    to_email: str,
    code: str,
    minutes_valid: int,
) -> None:
    cfg = _smtp_or_raise(db, tenant_id)

    message = EmailMessage()
    message["Subject"] = "AppKids | Codigo de recuperacao"
    message["From"] = cfg.from_email
    message["To"] = to_email
    message.set_content(
        "Recebemos uma solicitacao de recuperacao de senha (PIN) do AppKids.\n\n"
        f"Seu codigo: {code}\n"
        f"Validade: {minutes_valid} minutos\n\n"
        "Se voce nao solicitou, ignore este e-mail.\n"
    )

    _send_message(cfg, message)

