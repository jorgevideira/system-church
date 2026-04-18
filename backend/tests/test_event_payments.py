import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.db.models.event import Event
from app.schemas.event import EventRegistrationPublicCreate
from app.services import event_service, mercadopago_service
from tests.conftest import get_or_create_test_tenant


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
