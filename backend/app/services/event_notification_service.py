import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Optional

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.event import Event
from app.db.models.event_notification import EventNotification
from app.db.models.event_registration import EventRegistration
from app.services import qr_service, smtp_settings_service


def list_notifications(db: Session, event_id: int, tenant_id: int) -> list[EventNotification]:
    return (
        db.query(EventNotification)
        .filter(EventNotification.tenant_id == tenant_id, EventNotification.event_id == event_id)
        .order_by(EventNotification.created_at.desc(), EventNotification.id.desc())
        .all()
    )


def build_event_analytics(db: Session, event: Event) -> dict:
    registrations = (
        db.query(EventRegistration)
        .filter(EventRegistration.tenant_id == event.tenant_id, EventRegistration.event_id == event.id)
        .all()
    )
    reserved_slots = int(sum(item.quantity for item in registrations if item.status in {"pending_payment", "confirmed"}))
    confirmed = [item for item in registrations if item.status == "confirmed"]
    pending = [item for item in registrations if item.status == "pending_payment"]

    payment_status_rows = (
        db.query(
            EventRegistration.payment_status,
            func.count(EventRegistration.id),
        )
        .filter(EventRegistration.tenant_id == event.tenant_id, EventRegistration.event_id == event.id)
        .group_by(EventRegistration.payment_status)
        .all()
    )
    payment_method_rows = (
        db.query(
            EventRegistration.payment_method,
            func.count(EventRegistration.id),
        )
        .filter(EventRegistration.tenant_id == event.tenant_id, EventRegistration.event_id == event.id)
        .group_by(EventRegistration.payment_method)
        .all()
    )
    daily_rows = (
        db.query(
            func.date(EventRegistration.created_at).label("day"),
            func.count(EventRegistration.id).label("count"),
        )
        .filter(EventRegistration.tenant_id == event.tenant_id, EventRegistration.event_id == event.id)
        .group_by(func.date(EventRegistration.created_at))
        .order_by(func.date(EventRegistration.created_at))
        .all()
    )

    return {
        "event_id": event.id,
        "title": event.title,
        "capacity": event.capacity,
        "reserved_slots": reserved_slots,
        "confirmed_registrations": len(confirmed),
        "pending_registrations": len(pending),
        "total_revenue_confirmed": float(sum(item.total_amount for item in confirmed)),
        "total_revenue_pending": float(sum(item.total_amount for item in pending)),
        "payment_status_breakdown": [
            {"status": row[0] or "unknown", "count": int(row[1])}
            for row in payment_status_rows
        ],
        "payment_method_breakdown": [
            {"payment_method": row[0] or "unknown", "count": int(row[1])}
            for row in payment_method_rows
        ],
        "registrations_by_day": [
            {"day": str(row.day), "count": int(row.count)}
            for row in daily_rows
        ],
    }


def enqueue_registration_notifications(
    db: Session,
    *,
    event: Event,
    registration: EventRegistration,
    phase: str,
) -> list[EventNotification]:
    notifications: list[EventNotification] = []
    email_subject, email_body, whatsapp_message, qr_data = _build_notification_content(
        event=event,
        registration=registration,
        phase=phase,
    )

    # Avoid duplicate sends if webhook retries or admin confirms twice.
    existing_email = (
        db.query(EventNotification)
        .filter(
            EventNotification.tenant_id == event.tenant_id,
            EventNotification.event_id == event.id,
            EventNotification.registration_id == registration.id,
            EventNotification.channel == "email",
            EventNotification.template_key == phase,
        )
        .order_by(EventNotification.id.desc())
        .first()
    )
    if existing_email is not None:
        if existing_email.status == "failed":
            existing_email.status = "queued"
            existing_email.error_message = None
            notifications.append(existing_email)
    else:
        payload = {"subject": email_subject, "body": email_body}
        if qr_data:
            payload["qr_data"] = qr_data
        notifications.append(
            EventNotification(
                tenant_id=event.tenant_id,
                event_id=event.id,
                registration_id=registration.id,
                channel="email",
                template_key=phase,
                recipient=registration.attendee_email,
                status="queued",
                payload=payload,
            )
        )

    if registration.attendee_phone:
        existing_whatsapp = (
            db.query(EventNotification)
            .filter(
                EventNotification.tenant_id == event.tenant_id,
                EventNotification.event_id == event.id,
                EventNotification.registration_id == registration.id,
                EventNotification.channel == "whatsapp",
                EventNotification.template_key == phase,
            )
            .order_by(EventNotification.id.desc())
            .first()
        )
        if existing_whatsapp is not None:
            if existing_whatsapp.status == "failed":
                existing_whatsapp.status = "queued"
                existing_whatsapp.error_message = None
                notifications.append(existing_whatsapp)
        else:
            notifications.append(
                EventNotification(
                    tenant_id=event.tenant_id,
                    event_id=event.id,
                    registration_id=registration.id,
                    channel="whatsapp",
                    template_key=phase,
                    recipient=registration.attendee_phone,
                    status="queued",
                    payload={"message": whatsapp_message},
                )
            )

    if not notifications:
        return []

    for notification in notifications:
        db.add(notification)
    db.commit()
    for notification in notifications:
        db.refresh(notification)
    return notifications


def _build_notification_content(*, event: Event, registration: EventRegistration, phase: str) -> tuple[str, str, str, str | None]:
    event_line = f"Evento: {event.title}"
    code_line = f"Codigo da inscricao: {registration.registration_code}"
    attendee_line = f"Participante: {registration.attendee_name}"
    amount_line = f"Valor total: {registration.total_amount} {registration.currency}"
    support_line = "Se precisar de ajuda, responda este contato da igreja."

    if phase == "payment_confirmed":
        qr_data = registration.public_token
        subject = f"{event.title} | Pagamento confirmado"
        body = (
            f"Ola {registration.attendee_name},\n\n"
            f"Seu pagamento foi confirmado e sua vaga esta garantida.\n\n"
            f"{event_line}\n"
            f"{code_line}\n"
            f"{attendee_line}\n"
            f"{amount_line}\n"
            f"Status da inscricao: confirmada\n\n"
            f"Apresente o QR Code anexado na entrada do evento.\n"
            f"Token do QR Code (caso precise digitar): {qr_data}\n\n"
            f"{support_line}\n"
        )
        whatsapp = (
            f"{event.title}: pagamento confirmado para a inscricao {registration.registration_code}. "
            f"Sua vaga esta garantida."
        )
        return subject, body, whatsapp, qr_data

    subject = f"{event.title} | Inscricao recebida"
    body = (
        f"Ola {registration.attendee_name},\n\n"
        f"Recebemos sua inscricao e reservamos sua vaga temporariamente.\n\n"
        f"{event_line}\n"
        f"{code_line}\n"
        f"{attendee_line}\n"
        f"{amount_line}\n"
        f"Status da inscricao: aguardando pagamento\n\n"
        f"Conclua o pagamento para confirmar sua participacao.\n"
        f"{support_line}\n"
    )
    whatsapp = (
        f"{event.title}: recebemos sua inscricao {registration.registration_code}. "
        f"Conclua o pagamento para confirmar sua vaga."
    )
    return subject, body, whatsapp, None


def dispatch_notification(db: Session, notification: EventNotification) -> None:
    _dispatch_notification(db, notification)


def _dispatch_notification(db: Session, notification: EventNotification) -> None:
    try:
        if notification.channel == "email":
            _send_email(db, notification)
        elif notification.channel == "whatsapp":
            _send_whatsapp(notification)
        else:
            return
        notification.status = "sent"
        notification.sent_at = datetime.now(timezone.utc)
        notification.error_message = None
    except Exception as exc:
        notification.status = "failed"
        notification.error_message = str(exc)[:500]
    db.commit()


def _send_email(db: Session, notification: EventNotification) -> None:
    tenant_id = int(notification.tenant_id or 0)
    cfg = smtp_settings_service.resolve_effective_smtp_config(db, tenant_id) if tenant_id else None
    if cfg is None or not cfg.host or not cfg.from_email:
        # Backwards-compatible env config.
        if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
            raise ValueError("SMTP not configured")
        # Normalize env config into the same behavior surface.
        encryption = "tls" if settings.SMTP_USE_TLS else "none"
        cfg = smtp_settings_service.EffectiveSmtpConfig(
            host=str(settings.SMTP_HOST),
            port=int(settings.SMTP_PORT or 587),
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            from_email=str(settings.SMTP_FROM_EMAIL),
            encryption=encryption,
        )

    message = EmailMessage()
    message["Subject"] = (notification.payload or {}).get("subject") or "Notificacao de evento"
    message["From"] = cfg.from_email
    message["To"] = notification.recipient
    message.set_content((notification.payload or {}).get("body") or "Notificacao")

    qr_data = (notification.payload or {}).get("qr_data")
    if isinstance(qr_data, str) and qr_data.strip():
        qr_png = qr_service.build_qr_png(qr_data.strip())
        message.add_attachment(qr_png, maintype="image", subtype="png", filename="qrcode.png")

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


def _send_whatsapp(notification: EventNotification) -> None:
    if not settings.WHATSAPP_WEBHOOK_URL:
        raise ValueError("WhatsApp webhook not configured")

    headers = {}
    if settings.WHATSAPP_WEBHOOK_TOKEN:
        headers["Authorization"] = f"Bearer {settings.WHATSAPP_WEBHOOK_TOKEN}"

    with httpx.Client(timeout=20.0) as client:
        response = client.post(
            settings.WHATSAPP_WEBHOOK_URL,
            headers=headers,
            json={
                "to": notification.recipient,
                "message": (notification.payload or {}).get("message") or "Notificacao de evento",
                "event_notification_id": notification.id,
            },
        )
        response.raise_for_status()
