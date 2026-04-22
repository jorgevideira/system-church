import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.db.models.event import Event
from app.db.models.event_payment import EventPayment
from app.db.models.event_registration import EventRegistration
from app.db.models.transaction import Transaction
from app.schemas.event import EventRegistrationPublicCreate
from app.services import event_service, mercadopago_service
from tests.conftest import auth_headers, get_or_create_test_tenant


def public_registration_address_payload() -> dict:
    return {
        "address_zip_code": "01310-100",
        "address_street": "Avenida Paulista",
        "address_number": "1000",
        "address_neighborhood": "Bela Vista",
        "address_country": "Brasil",
        "address_state": "SP",
        "address_city": "São Paulo",
        "lgpd_data_sharing_consent": True,
    }


def test_create_public_registration_uses_transparent_pix_for_mercadopago(test_db, test_admin, monkeypatch):
    unique_suffix = secrets.token_hex(3)
    tenant = get_or_create_test_tenant(test_db)
    tenant.payment_provider = "mercadopago"
    tenant.payment_pix_enabled = True
    tenant.payment_card_enabled = True
    tenant.mercadopago_access_token = "TEST-TOKEN"
    tenant.mercadopago_public_key = "TEST-PUBLIC-KEY"

    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)

    event = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Conferencia de Jovens",
        slug=f"conferencia-jovens-{unique_suffix}",
        summary="Evento para testes de pagamento",
        description="Fluxo com PIX transparente",
        location="Templo Central",
        visibility="public",
        status="published",
        start_at=datetime.now(timezone.utc) + timedelta(days=7),
        end_at=datetime.now(timezone.utc) + timedelta(days=7, hours=2),
        price_per_registration=Decimal("49.90"),
        currency="BRL",
        allow_public_registration=True,
        require_payment=True,
        is_active=True,
    )
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)

    monkeypatch.setattr(mercadopago_service, "is_enabled", lambda tenant_arg, payment_account_arg=None: True)
    monkeypatch.setattr(
        mercadopago_service,
        "create_pix_payment",
        lambda **kwargs: {
            "id": 987654,
            "status": "pending",
            "date_of_expiration": "2026-04-14T18:30:00+00:00",
            "point_of_interaction": {
                "transaction_data": {
                    "qr_code": "000201010212PIX-COPIA-COLA",
                    "qr_code_base64": "ZmFrZS1xci1iYXNlNjQ=",
                    "ticket_url": "https://www.mercadopago.com.br/payments/test-ticket",
                }
            },
        },
    )

    payload = EventRegistrationPublicCreate(
        attendee_name="Maria de Betania",
        attendee_email="maria@example.com",
        quantity=1,
        payment_method="pix",
        notes="Teste",
        **public_registration_address_payload(),
    )

    registration, payment = event_service.create_public_registration(test_db, tenant, event, payload)

    assert registration.id is not None
    assert payment is not None
    assert payment.provider == "mercadopago"
    assert payment.payment_method == "pix"
    assert payment.provider_reference == "987654"
    assert payment.pix_copy_paste == "000201010212PIX-COPIA-COLA"
    assert payment.checkout_url == "https://www.mercadopago.com.br/payments/test-ticket"
    assert payment.provider_payload["checkout_mode"] == "transparent_pix"
    assert payment.provider_payload["qr_code_base64"] == "ZmFrZS1xci1iYXNlNjQ="
    assert registration.address_zip_code == "01310-100"
    assert registration.address_city == "São Paulo"
    assert registration.lgpd_data_sharing_consent is True
    assert registration.lgpd_data_sharing_consented_at is not None


def test_create_public_registration_falls_back_to_redirect_when_transparent_pix_fails(test_db, test_admin, monkeypatch):
    unique_suffix = secrets.token_hex(3)
    tenant = get_or_create_test_tenant(test_db)
    tenant.payment_provider = "mercadopago"
    tenant.payment_pix_enabled = True
    tenant.payment_card_enabled = True
    tenant.mercadopago_access_token = "TEST-TOKEN"
    tenant.mercadopago_public_key = "TEST-PUBLIC-KEY"

    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)

    event = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Conferencia Infantil",
        slug=f"conferencia-infantil-{unique_suffix}",
        summary="Evento para fallback",
        description="Fallback para checkout por link",
        location="Campus Kids",
        visibility="public",
        status="published",
        start_at=datetime.now(timezone.utc) + timedelta(days=10),
        end_at=datetime.now(timezone.utc) + timedelta(days=10, hours=3),
        price_per_registration=Decimal("29.90"),
        currency="BRL",
        allow_public_registration=True,
        require_payment=True,
        is_active=True,
    )
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)

    monkeypatch.setattr(mercadopago_service, "is_enabled", lambda tenant_arg, payment_account_arg=None: True)
    monkeypatch.setattr(
        mercadopago_service,
        "create_pix_payment",
        lambda **kwargs: (_ for _ in ()).throw(ValueError("Mercado Pago recusou o PIX transparente: configuração inválida")),
    )
    monkeypatch.setattr(
        mercadopago_service,
        "create_checkout_preference",
        lambda **kwargs: {
            "id": "pref-123",
            "init_point": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref-123",
        },
    )

    payload = EventRegistrationPublicCreate(
        attendee_name="Joquebede",
        attendee_email="joquebede@example.com",
        quantity=1,
        payment_method="pix",
        **public_registration_address_payload(),
    )

    registration, payment = event_service.create_public_registration(test_db, tenant, event, payload)

    assert registration.id is not None
    assert payment is not None
    assert payment.provider == "mercadopago"
    assert payment.payment_method == "pix"
    assert payment.pix_copy_paste is None
    assert payment.checkout_url == "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref-123"
    assert payment.provider_payload["checkout_mode"] == "redirect"
    assert "transparent_pix_error" in payment.provider_payload


def test_event_registrations_and_payments_listing_supports_pagination_and_event_filter(test_db, test_client, test_admin):
    unique_suffix = secrets.token_hex(3)
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)

    event_a = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Retiro de Casais",
        slug=f"retiro-casais-{unique_suffix}",
        visibility="public",
        status="published",
        start_at=datetime.now(timezone.utc) + timedelta(days=3),
        end_at=datetime.now(timezone.utc) + timedelta(days=3, hours=4),
        price_per_registration=Decimal("60.00"),
        currency="BRL",
        allow_public_registration=True,
        require_payment=True,
        is_active=True,
    )
    event_b = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Congresso Teen",
        slug=f"congresso-teen-{unique_suffix}",
        visibility="public",
        status="published",
        start_at=datetime.now(timezone.utc) + timedelta(days=10),
        end_at=datetime.now(timezone.utc) + timedelta(days=10, hours=3),
        price_per_registration=Decimal("45.00"),
        currency="BRL",
        allow_public_registration=True,
        require_payment=True,
        is_active=True,
    )
    test_db.add_all([event_a, event_b])
    test_db.commit()
    test_db.refresh(event_a)
    test_db.refresh(event_b)

    registration_a1 = EventRegistration(
        tenant_id=tenant.id,
        event_id=event_a.id,
        registration_code=f"REG-A1-{unique_suffix}",
        public_token=f"token-a1-{unique_suffix}",
        attendee_name="Ana",
        attendee_email="ana@example.com",
        quantity=1,
        status="confirmed",
        payment_method="pix",
        payment_status="paid",
        total_amount=Decimal("60.00"),
        currency="BRL",
        confirmed_at=datetime.now(timezone.utc),
    )
    registration_a2 = EventRegistration(
        tenant_id=tenant.id,
        event_id=event_a.id,
        registration_code=f"REG-A2-{unique_suffix}",
        public_token=f"token-a2-{unique_suffix}",
        attendee_name="Bruno",
        attendee_email="bruno@example.com",
        quantity=1,
        status="pending_payment",
        payment_method="card",
        payment_status="pending",
        total_amount=Decimal("60.00"),
        currency="BRL",
    )
    registration_b1 = EventRegistration(
        tenant_id=tenant.id,
        event_id=event_b.id,
        registration_code=f"REG-B1-{unique_suffix}",
        public_token=f"token-b1-{unique_suffix}",
        attendee_name="Clara",
        attendee_email="clara@example.com",
        quantity=1,
        status="confirmed",
        payment_method="pix",
        payment_status="paid",
        total_amount=Decimal("45.00"),
        currency="BRL",
        confirmed_at=datetime.now(timezone.utc),
    )
    test_db.add_all([registration_a1, registration_a2, registration_b1])
    test_db.commit()
    test_db.refresh(registration_a1)
    test_db.refresh(registration_a2)
    test_db.refresh(registration_b1)

    payment_a1 = EventPayment(
        tenant_id=tenant.id,
        event_id=event_a.id,
        registration_id=registration_a1.id,
        provider="internal",
        payment_method="pix",
        status="paid",
        amount=Decimal("60.00"),
        currency="BRL",
        checkout_reference=f"checkout-a1-{unique_suffix}",
        paid_at=datetime.now(timezone.utc),
    )
    payment_a2 = EventPayment(
        tenant_id=tenant.id,
        event_id=event_a.id,
        registration_id=registration_a2.id,
        provider="internal",
        payment_method="card",
        status="pending",
        amount=Decimal("60.00"),
        currency="BRL",
        checkout_reference=f"checkout-a2-{unique_suffix}",
    )
    payment_b1 = EventPayment(
        tenant_id=tenant.id,
        event_id=event_b.id,
        registration_id=registration_b1.id,
        provider="internal",
        payment_method="pix",
        status="paid",
        amount=Decimal("45.00"),
        currency="BRL",
        checkout_reference=f"checkout-b1-{unique_suffix}",
        paid_at=datetime.now(timezone.utc),
    )
    test_db.add_all([payment_a1, payment_a2, payment_b1])
    test_db.commit()

    response = test_client.get(
        f"/api/v1/events/registrations?event_id={event_a.id}&page=1&size=1",
        headers=auth_headers(test_admin),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 2
    assert payload["pages"] == 2
    assert len(payload["items"]) == 1
    assert payload["items"][0]["event_title"] == event_a.title

    response = test_client.get(
        f"/api/v1/events/payments?event_id={event_a.id}&status=paid&page=1&size=10",
        headers=auth_headers(test_admin),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["event_title"] == event_a.title
    assert payload["items"][0]["can_refund"] is True


def test_refund_event_payment_creates_refund_transaction(test_db, test_client, test_admin):
    unique_suffix = secrets.token_hex(3)
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)

    event = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Workshop de Liderança",
        slug=f"workshop-lideranca-{unique_suffix}",
        visibility="public",
        status="published",
        start_at=datetime.now(timezone.utc) + timedelta(days=5),
        end_at=datetime.now(timezone.utc) + timedelta(days=5, hours=2),
        price_per_registration=Decimal("80.00"),
        currency="BRL",
        allow_public_registration=True,
        require_payment=True,
        is_active=True,
    )
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)

    registration = EventRegistration(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_code=f"REG-RF-{unique_suffix}",
        public_token=f"token-rf-{unique_suffix}",
        attendee_name="Daniel",
        attendee_email="daniel@example.com",
        quantity=1,
        status="confirmed",
        payment_method="pix",
        payment_status="paid",
        total_amount=Decimal("80.00"),
        currency="BRL",
        confirmed_at=datetime.now(timezone.utc),
    )
    test_db.add(registration)
    test_db.commit()
    test_db.refresh(registration)

    payment = EventPayment(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_id=registration.id,
        provider="internal",
        payment_method="pix",
        status="paid",
        amount=Decimal("80.00"),
        currency="BRL",
        checkout_reference=f"checkout-rf-{unique_suffix}",
        paid_at=datetime.now(timezone.utc),
    )
    test_db.add(payment)
    test_db.commit()
    test_db.refresh(payment)

    response = test_client.post(
        f"/api/v1/events/payments/{payment.id}/refund",
        headers=auth_headers(test_admin),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "refunded"
    assert payload["can_refund"] is False

    test_db.refresh(payment)
    test_db.refresh(registration)
    assert payment.status == "refunded"
    assert registration.status == "refunded"
    assert registration.payment_status == "refunded"

    refund_tx = (
        test_db.query(Transaction)
        .filter(Transaction.tenant_id == tenant.id, Transaction.reference == f"event_refund:{payment.id}")
        .first()
    )
    assert refund_tx is not None
    assert refund_tx.transaction_type == "expense"
    assert refund_tx.amount == Decimal("80.00")

    second_response = test_client.post(
        f"/api/v1/events/payments/{payment.id}/refund",
        headers=auth_headers(test_admin),
    )
    assert second_response.status_code == 400


def test_refund_event_payment_uses_provider_service_when_configured(test_db, test_admin, monkeypatch):
    unique_suffix = secrets.token_hex(3)
    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.add(test_admin)

    event = Event(
        tenant_id=tenant.id,
        created_by_user_id=test_admin.id,
        title="Conferência Global",
        slug=f"conferencia-global-{unique_suffix}",
        visibility="public",
        status="published",
        start_at=datetime.now(timezone.utc) + timedelta(days=12),
        end_at=datetime.now(timezone.utc) + timedelta(days=12, hours=3),
        price_per_registration=Decimal("99.90"),
        currency="BRL",
        allow_public_registration=True,
        require_payment=True,
        is_active=True,
    )
    test_db.add(event)
    test_db.commit()
    test_db.refresh(event)

    registration = EventRegistration(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_code=f"REG-MP-{unique_suffix}",
        public_token=f"token-mp-{unique_suffix}",
        attendee_name="Ester",
        attendee_email="ester@example.com",
        quantity=1,
        status="confirmed",
        payment_method="pix",
        payment_status="paid",
        total_amount=Decimal("99.90"),
        currency="BRL",
        confirmed_at=datetime.now(timezone.utc),
    )
    test_db.add(registration)
    test_db.commit()
    test_db.refresh(registration)

    payment = EventPayment(
        tenant_id=tenant.id,
        event_id=event.id,
        registration_id=registration.id,
        provider="mercadopago",
        payment_method="pix",
        status="paid",
        amount=Decimal("99.90"),
        currency="BRL",
        checkout_reference=f"checkout-mp-{unique_suffix}",
        provider_reference="123456789",
        paid_at=datetime.now(timezone.utc),
    )
    test_db.add(payment)
    test_db.commit()
    test_db.refresh(payment)

    monkeypatch.setattr(
        mercadopago_service,
        "refund_payment",
        lambda provider_reference, tenant_arg, payment_account_arg=None: {
            "id": "refund-123",
            "payment_id": provider_reference,
            "status": "approved",
        },
    )

    updated = event_service.refund_payment(test_db, payment)

    test_db.refresh(updated)
    test_db.refresh(registration)
    assert updated.status == "refunded"
    assert registration.status == "refunded"
    assert updated.provider_payload["provider_refund"]["id"] == "refund-123"
