import smtplib
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.payable import Payable
from app.db.models.payable_notification import PayableNotification
from app.db.models.tenant import Tenant
from app.services import smtp_settings_service


def enqueue_due_payable_notifications(
    db: Session,
    *,
    reference_date: date | None = None,
) -> list[PayableNotification]:
    today = reference_date or datetime.now(timezone.utc).date()
    tomorrow = today + timedelta(days=1)

    payables = (
        db.query(Payable)
        .filter(
            Payable.status != "paid",
            Payable.due_date.in_([today, tomorrow]),
        )
        .order_by(Payable.due_date.asc(), Payable.id.asc())
        .all()
    )

    notifications: list[PayableNotification] = []
    for payable in payables:
        if payable.user is None or not payable.user.email:
            continue

        template_key = "due_today" if payable.due_date == today else "due_tomorrow"
        recipient = payable.user.email.strip().lower()
        subject, body = _build_notification_content(db, payable=payable, template_key=template_key)
        payload = {"subject": subject, "body": body}

        existing = (
            db.query(PayableNotification)
            .filter(
                PayableNotification.payable_id == payable.id,
                PayableNotification.channel == "email",
                PayableNotification.template_key == template_key,
                PayableNotification.trigger_date == today,
                PayableNotification.recipient == recipient,
            )
            .order_by(PayableNotification.id.desc())
            .first()
        )
        if existing is not None:
            if existing.status == "failed":
                existing.status = "queued"
                existing.payload = payload
                existing.error_message = None
                notifications.append(existing)
            continue

        notification = PayableNotification(
            tenant_id=payable.tenant_id,
            payable_id=payable.id,
            user_id=payable.user_id,
            channel="email",
            template_key=template_key,
            recipient=recipient,
            trigger_date=today,
            due_date_snapshot=payable.due_date,
            status="queued",
            payload=payload,
        )
        db.add(notification)
        notifications.append(notification)

    if notifications:
        db.commit()
        for notification in notifications:
            db.refresh(notification)

    return notifications


def dispatch_notification(db: Session, notification: PayableNotification) -> None:
    try:
        _send_email(db, notification)
        notification.status = "sent"
        notification.sent_at = datetime.now(timezone.utc)
        notification.error_message = None
    except Exception as exc:
        notification.status = "failed"
        notification.error_message = str(exc)[:500]
    db.commit()


def _build_notification_content(
    db: Session,
    *,
    payable: Payable,
    template_key: str,
) -> tuple[str, str]:
    tenant_name = "sua igreja"
    if payable.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == payable.tenant_id).first()
        if tenant and tenant.name:
            tenant_name = tenant.name

    due_date_formatted = payable.due_date.strftime("%d/%m/%Y")
    amount_formatted = f"R$ {float(payable.amount):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    category_name = payable.category.name if payable.category else "Nao informada"
    ministry_name = payable.ministry.name if payable.ministry else "Nao informado"
    notes = (payable.notes or "").strip()

    if template_key == "due_tomorrow":
        subject = f"{tenant_name} | Conta vence amanha"
        intro = "Este e-mail é um lembrete de que uma conta a pagar vence amanha."
    else:
        subject = f"{tenant_name} | Conta vence hoje"
        intro = "Este e-mail é um lembrete de que uma conta a pagar vence hoje."

    body = (
        f"Ola {payable.user.full_name or payable.user.email},\n\n"
        f"{intro}\n\n"
        f"Descricao: {payable.description}\n"
        f"Valor: {amount_formatted}\n"
        f"Vencimento: {due_date_formatted}\n"
        f"Categoria: {category_name}\n"
        f"Ministerio: {ministry_name}\n"
        f"Banco de origem: {payable.source_bank_name or 'Nao informado'}\n"
        f"Metodo de pagamento sugerido: {payable.payment_method or 'Nao informado'}\n"
        f"Status atual: {payable.status}\n"
    )
    if notes:
        body += f"Observacoes: {notes}\n"
    body += "\nAcesse o modulo financeiro para registrar o pagamento ou ajustar a conta.\n"
    return subject, body


def _send_email(db: Session, notification: PayableNotification) -> None:
    tenant_id = int(notification.tenant_id or 0)
    cfg = smtp_settings_service.resolve_effective_smtp_config(db, tenant_id) if tenant_id else None
    if cfg is None or not cfg.host or not cfg.from_email:
        if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
            raise ValueError("SMTP not configured")
        cfg = smtp_settings_service.EffectiveSmtpConfig(
            host=str(settings.SMTP_HOST),
            port=int(settings.SMTP_PORT or 587),
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            from_email=str(settings.SMTP_FROM_EMAIL),
            encryption="tls" if settings.SMTP_USE_TLS else "none",
        )

    message = EmailMessage()
    message["Subject"] = (notification.payload or {}).get("subject") or "Lembrete de conta a pagar"
    message["From"] = cfg.from_email
    message["To"] = notification.recipient
    message.set_content((notification.payload or {}).get("body") or "Lembrete de conta a pagar")

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
