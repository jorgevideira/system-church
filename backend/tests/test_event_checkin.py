from datetime import datetime, timezone
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.event import Event
from app.db.models.event_checkin import EventCheckIn
from app.db.models.event_checkin_attempt import EventCheckInAttempt
from app.db.models.event_registration import EventRegistration
from app.db.models.user import User
from tests.conftest import auth_headers, get_or_create_test_tenant


def _seed_event_and_registration(
    test_db: Session,
    *,
    tenant_id: int,
    created_by_user_id: int,
    event_id: int | None = None,
    public_token: str,
    payment_status: str,
    status: str,
) -> EventRegistration:
    event = test_db.query(Event).filter(Event.id == (event_id or 1), Event.tenant_id == tenant_id).first()
    if event is None:
        event = Event(
            tenant_id=tenant_id,
            created_by_user_id=created_by_user_id,
            title="Evento Teste",
            slug="evento-teste",
            summary=None,
            description=None,
            location=None,
            timezone_name="America/Sao_Paulo",
            visibility="private",
            status="published",
            start_at=datetime(2026, 4, 10, 19, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc),
            capacity=100,
            max_registrations_per_order=1,
            price_per_registration=0,
            currency="BRL",
            allow_public_registration=False,
            require_payment=True,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()
        test_db.refresh(event)

    registration = EventRegistration(
        tenant_id=tenant_id,
        event_id=event.id,
        registration_code=f"REG-{uuid.uuid4().hex[:10]}",
        public_token=public_token,
        attendee_name="Participante",
        attendee_email="participante@test.com",
        attendee_phone=None,
        attendee_document=None,
        quantity=1,
        status=status,
        payment_method="pix",
        payment_status=payment_status,
        total_amount=0,
        currency="BRL",
        notes=None,
        confirmed_at=datetime.now(timezone.utc) if status == "confirmed" else None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    test_db.add(registration)
    test_db.commit()
    test_db.refresh(registration)
    return registration


def test_event_checkin_success_duplicate_and_not_paid(
    test_client: TestClient,
    test_db: Session,
    test_admin: User,
):
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.commit()

    headers = auth_headers(test_admin)

    reg_paid = _seed_event_and_registration(
        test_db,
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        public_token="tok-paid-123",
        payment_status="paid",
        status="confirmed",
    )

    # First check-in: success
    resp = test_client.post("/api/v1/events/checkin", json={"token": reg_paid.public_token}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["registration_id"] == reg_paid.id

    # Second check-in: duplicate
    resp2 = test_client.post("/api/v1/events/checkin", json={"token": reg_paid.public_token}, headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "duplicate"

    # Not paid: blocked
    reg_unpaid = _seed_event_and_registration(
        test_db,
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        public_token="tok-unpaid-456",
        payment_status="pending",
        status="pending_payment",
    )
    resp3 = test_client.post("/api/v1/events/checkin", json={"token": reg_unpaid.public_token}, headers=headers)
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "not_paid"

    # Invalid token: invalid
    resp4 = test_client.post("/api/v1/events/checkin", json={"token": "tok-missing"}, headers=headers)
    assert resp4.status_code == 200
    assert resp4.json()["status"] == "invalid"

    # Logs exist
    assert test_db.query(EventCheckIn).filter(EventCheckIn.registration_id == reg_paid.id).count() == 1
    assert test_db.query(EventCheckInAttempt).count() >= 4
