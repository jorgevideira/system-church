from datetime import datetime, timezone

import httpx
import pytest

from app.db.models.event import Event
from app.db.models.event_notification import EventNotification
from app.services import event_notification_service
from tests.conftest import auth_headers, get_or_create_test_tenant


class _FakeHttpxClient:
    def __init__(self, response: httpx.Response, sink: dict):
        self._response = response
        self._sink = sink

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, headers=None, json=None):
        self._sink["url"] = url
        self._sink["headers"] = headers
        self._sink["json"] = json
        return self._response


def _build_notification(recipient: str) -> EventNotification:
    return EventNotification(
        id=321,
        tenant_id=1,
        event_id=10,
        registration_id=20,
        channel="whatsapp",
        template_key="payment_confirmed",
        recipient=recipient,
        status="queued",
        payload={"message": "Pagamento confirmado."},
    )


def test_send_whatsapp_surfaces_gateway_detail(monkeypatch):
    monkeypatch.setattr(event_notification_service.settings, "WHATSAPP_WEBHOOK_URL", "http://whatsapp-gateway:8090/send")
    monkeypatch.setattr(event_notification_service.settings, "WHATSAPP_WEBHOOK_TOKEN", "secret-token")

    request = httpx.Request("POST", "http://whatsapp-gateway:8090/send")
    response = httpx.Response(500, json={"detail": "WhatsApp Web ainda nao esta conectado."}, request=request)
    sink: dict = {}

    monkeypatch.setattr(
        event_notification_service.httpx,
        "Client",
        lambda timeout=20.0: _FakeHttpxClient(response, sink),
    )

    with pytest.raises(RuntimeError, match="WhatsApp Web ainda nao esta conectado."):
        event_notification_service._send_whatsapp(_build_notification("(11) 99999-9999"))

    assert sink["url"] == "http://whatsapp-gateway:8090/send"
    assert sink["headers"] == {"Authorization": "Bearer secret-token"}
    assert sink["json"]["to"] == "11999999999"


def test_send_whatsapp_rejects_invalid_recipient(monkeypatch):
    monkeypatch.setattr(event_notification_service.settings, "WHATSAPP_WEBHOOK_URL", "http://whatsapp-gateway:8090/send")
    monkeypatch.setattr(event_notification_service.settings, "WHATSAPP_WEBHOOK_TOKEN", None)

    with pytest.raises(ValueError, match="Telefone do destinatario de WhatsApp invalido."):
        event_notification_service._send_whatsapp(_build_notification("abc"))


def test_retry_notification_endpoint_requeues_only_the_target_failed_item(test_client, test_db, test_admin, monkeypatch):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)
    test_db.commit()

    event = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Conferencia de Casais",
        slug="conferencia-casais-retry",
        visibility="private",
        status="published",
        start_at=datetime(2026, 4, 30, 19, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 4, 30, 22, 0, tzinfo=timezone.utc),
        allow_public_registration=False,
        require_payment=False,
        is_active=True,
    )
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)

    failed_a = EventNotification(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_id=101,
        channel="whatsapp",
        template_key="payment_confirmed",
        recipient="5511999999999",
        status="failed",
        payload={"message": "Falha 1"},
        error_message="Gateway offline",
    )
    failed_b = EventNotification(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_id=102,
        channel="email",
        template_key="registration_created",
        recipient="casal@example.com",
        status="failed",
        payload={"message": "Falha 2"},
        error_message="SMTP timeout",
    )
    sent = EventNotification(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_id=103,
        channel="email",
        template_key="registration_created",
        recipient="ok@example.com",
        status="sent",
        payload={"message": "OK"},
        error_message=None,
        sent_at=datetime.now(timezone.utc),
    )
    test_db.add_all([failed_a, failed_b, sent])
    test_db.commit()
    test_db.refresh(failed_a)
    test_db.refresh(failed_b)
    test_db.refresh(sent)

    queued_ids: list[int] = []
    monkeypatch.setattr(
        event_notification_service,
        "_enqueue_dispatch",
        lambda notification_id: queued_ids.append(notification_id),
    )

    response = test_client.post(
        f"/api/v1/events/{event.id}/notifications/{failed_a.id}/retry",
        headers=auth_headers(test_admin),
    )

    assert response.status_code == 200
    assert response.json() == {"notification_id": failed_a.id, "status": "queued"}

    test_db.refresh(failed_a)
    test_db.refresh(failed_b)
    test_db.refresh(sent)

    assert failed_a.status == "queued"
    assert failed_b.status == "failed"
    assert failed_a.error_message is None
    assert failed_b.error_message == "SMTP timeout"
    assert sent.status == "sent"
    assert queued_ids == [failed_a.id]


def test_retry_notification_endpoint_rejects_non_failed_item(test_client, test_db, test_admin, monkeypatch):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)
    test_db.commit()

    event = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Conferencia de Louvor",
        slug="conferencia-louvor-retry",
        visibility="private",
        status="published",
        start_at=datetime(2026, 5, 2, 19, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 5, 2, 22, 0, tzinfo=timezone.utc),
        allow_public_registration=False,
        require_payment=False,
        is_active=True,
    )
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)

    sent = EventNotification(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_id=201,
        channel="email",
        template_key="registration_created",
        recipient="ok@example.com",
        status="sent",
        payload={"message": "OK"},
        sent_at=datetime.now(timezone.utc),
    )
    test_db.add(sent)
    test_db.commit()
    test_db.refresh(sent)

    queued_ids: list[int] = []
    monkeypatch.setattr(
        event_notification_service,
        "_enqueue_dispatch",
        lambda notification_id: queued_ids.append(notification_id),
    )

    response = test_client.post(
        f"/api/v1/events/{event.id}/notifications/{sent.id}/retry",
        headers=auth_headers(test_admin),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only failed notifications can be retried."
    assert queued_ids == []
