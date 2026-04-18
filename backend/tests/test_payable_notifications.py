from datetime import date, datetime, timezone

from app.db.models.payable import Payable
from app.db.models.payable_notification import PayableNotification
from app.tasks.payable_notifications import process_due_payable_reminders
from app.services import payable_notification_service
from tests.conftest import TestingSessionLocal, get_or_create_test_tenant


def _create_payable(test_db, *, user, tenant_id: int, description: str, due_date: date, status: str = "pending") -> Payable:
    payable = Payable(
        tenant_id=tenant_id,
        user_id=user.id,
        description=description,
        amount="150.00",
        due_date=due_date,
        status=status,
        source_bank_name="Bradesco",
        notes="Lembrete automatico",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    test_db.add(payable)
    test_db.commit()
    test_db.refresh(payable)
    return payable


def test_enqueue_due_payable_notifications_creates_today_and_tomorrow(test_db, test_admin):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)
    test_db.commit()

    today_payable = _create_payable(
        test_db,
        user=test_admin,
        tenant_id=tenant.id,
        description="Conta vence hoje",
        due_date=date(2026, 4, 15),
    )
    tomorrow_payable = _create_payable(
        test_db,
        user=test_admin,
        tenant_id=tenant.id,
        description="Conta vence amanha",
        due_date=date(2026, 4, 16),
    )
    _create_payable(
        test_db,
        user=test_admin,
        tenant_id=tenant.id,
        description="Conta futura",
        due_date=date(2026, 4, 20),
    )
    _create_payable(
        test_db,
        user=test_admin,
        tenant_id=tenant.id,
        description="Conta paga",
        due_date=date(2026, 4, 15),
        status="paid",
    )

    notifications = payable_notification_service.enqueue_due_payable_notifications(
        test_db,
        reference_date=date(2026, 4, 15),
    )

    assert len(notifications) == 2
    keys_by_payable = {item.payable_id: item.template_key for item in notifications}
    assert keys_by_payable[today_payable.id] == "due_today"
    assert keys_by_payable[tomorrow_payable.id] == "due_tomorrow"
    assert {item.recipient for item in notifications} == {test_admin.email}


def test_enqueue_due_payable_notifications_is_idempotent(test_db, test_admin):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)
    test_db.commit()

    payable = _create_payable(
        test_db,
        user=test_admin,
        tenant_id=tenant.id,
        description="Conta sem duplicidade",
        due_date=date(2026, 4, 15),
    )

    first = payable_notification_service.enqueue_due_payable_notifications(
        test_db,
        reference_date=date(2026, 4, 15),
    )
    second = payable_notification_service.enqueue_due_payable_notifications(
        test_db,
        reference_date=date(2026, 4, 15),
    )

    assert len(first) == 1
    assert second == []
    stored = (
        test_db.query(PayableNotification)
        .filter(PayableNotification.payable_id == payable.id)
        .all()
    )
    assert len(stored) == 1


def test_process_due_payable_reminders_dispatches_email(test_db, test_admin, monkeypatch):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)
    test_db.commit()

    payable = _create_payable(
        test_db,
        user=test_admin,
        tenant_id=tenant.id,
        description="Conta para envio",
        due_date=date(2026, 4, 15),
    )

    sent_to: list[str] = []

    def fake_send_email(_db, notification):
        sent_to.append(notification.recipient)

    monkeypatch.setattr("app.db.session.SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(
        "app.services.payable_notification_service._send_email",
        fake_send_email,
    )

    result = process_due_payable_reminders(reference_date_iso="2026-04-15")

    assert result["queued"] == 1
    assert result["sent"] == 1
    assert result["failed"] == 0
    assert sent_to == [test_admin.email]

    stored = (
        test_db.query(PayableNotification)
        .filter(PayableNotification.payable_id == payable.id)
        .first()
    )
    assert stored is not None
    assert stored.status == "sent"
