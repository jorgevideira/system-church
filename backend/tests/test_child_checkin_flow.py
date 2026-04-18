from app.core.config import settings
from app.services import child_checkin_service
from tests.conftest import auth_headers, get_or_create_test_tenant


def test_child_checkin_full_flow(test_client, test_db, test_admin, monkeypatch):
    monkeypatch.setattr(settings, "CHILD_CHECKIN_DEV_ENABLED", True)

    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.commit()

    headers = auth_headers(test_admin)

    # 1) Create family
    family_resp = test_client.post(
        "/api/v1/child-checkin/families",
        json={
            "family_name": "Familia Souza",
            "primary_responsible_name": "Maria Souza",
            "phone_primary": "16999990000",
            "email": "maria.souza@test.com",
        },
        headers=headers,
    )
    assert family_resp.status_code == 201
    family = family_resp.json()
    assert family["family_name"] == "Familia Souza"
    family_id = int(family["id"])

    # 2) Create child
    child_resp = test_client.post(
        "/api/v1/child-checkin/children",
        json={
            "family_id": family_id,
            "full_name": "Lucas Souza",
            "age_group": "6-8",
            "room_name": "Sala Kids A",
            "allergies": "Lactose",
        },
        headers=headers,
    )
    assert child_resp.status_code == 201
    child = child_resp.json()
    child_id = int(child["id"])

    # 3) Create authorized guardian
    guardian_resp = test_client.post(
        "/api/v1/child-checkin/guardians",
        json={
            "family_id": family_id,
            "full_name": "Joao Souza",
            "relationship": "Pai",
            "phone": "16988887777",
            "is_authorized": True,
        },
        headers=headers,
    )
    assert guardian_resp.status_code == 201
    guardian = guardian_resp.json()
    guardian_id = int(guardian["id"])

    # 4) Check-in
    checkin_resp = test_client.post(
        "/api/v1/child-checkin/checkins",
        json={
            "family_id": family_id,
            "child_ids": [child_id],
            "context_type": "culto",
            "context_name": "Culto Domingo Noite",
            "room_name": "Sala Kids A",
            "accompanied_by_name": "Maria Souza",
        },
        headers=headers,
    )
    assert checkin_resp.status_code == 201
    checkins = checkin_resp.json()
    assert len(checkins) == 1
    record = checkins[0]
    assert record["status"] == "checked_in"
    assert record["alert_snapshot"] and "Lactose" in record["alert_snapshot"]

    checkin_id = int(record["id"])
    security_code = record["security_code"]

    # 5) Checkout
    checkout_resp = test_client.post(
        f"/api/v1/child-checkin/checkins/{checkin_id}/checkout",
        json={
            "security_code": security_code,
            "pickup_guardian_id": guardian_id,
            "pickup_person_name": "Joao Souza",
        },
        headers=headers,
    )
    assert checkout_resp.status_code == 200
    checked_out = checkout_resp.json()
    assert checked_out["status"] == "checked_out"
    assert checked_out["pickup_guardian_id"] == guardian_id

    # 6) Summary and open-checkins list
    summary_resp = test_client.get("/api/v1/child-checkin/summary", headers=headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["total_checkins"] >= 1
    assert summary["completed_checkouts"] >= 1

    open_resp = test_client.get("/api/v1/child-checkin/checkins?status=checked_in", headers=headers)
    assert open_resp.status_code == 200
    open_rows = open_resp.json()
    assert all(row["id"] != checkin_id for row in open_rows)


def test_child_checkin_public_registration_and_virtual_cards(test_client, test_db, test_admin, monkeypatch):
    monkeypatch.setattr(settings, "CHILD_CHECKIN_DEV_ENABLED", True)

    tenant = get_or_create_test_tenant(test_db)
    if not tenant.slug:
        tenant.slug = "igreja-teste"
        test_db.commit()
        test_db.refresh(tenant)

    register_resp = test_client.post(
        f"/api/v1/child-checkin/public/tenants/{tenant.slug}/pre-register",
        json={
            "family_name": "Familia Publica",
            "primary_responsible_name": "Carla Publica",
            "phone_primary": "16999998888",
            "email": "carla.publica@example.com",
            "children": [
                {
                    "full_name": "Ana Publica",
                    "room_name": "Jardim A",
                    "allergies": "Amendoim",
                }
            ],
            "guardians": [
                {
                    "full_name": "Roberto Publico",
                    "relationship": "Pai",
                    "phone": "16977776666",
                    "is_authorized": True,
                }
            ],
        },
    )
    assert register_resp.status_code == 201
    body = register_resp.json()
    assert body["family_code"]
    assert len(body["cards"]) == 1
    assert body["cards"][0]["child_name"] == "Ana Publica"

    lookup_resp = test_client.get(
        f"/api/v1/child-checkin/public/tenants/{tenant.slug}/virtual-cards",
        params={"family_code": body["family_code"]},
    )
    assert lookup_resp.status_code == 200
    lookup_body = lookup_resp.json()
    assert lookup_body["family_code"] == body["family_code"]
    assert len(lookup_body["cards"]) == 1


def test_child_checkin_public_pin_recovery_verify_and_confirm(test_client, test_db, monkeypatch):
    monkeypatch.setattr(settings, "CHILD_CHECKIN_DEV_ENABLED", True)

    tenant = get_or_create_test_tenant(test_db)
    if not tenant.slug:
        tenant.slug = "igreja-teste"
        test_db.commit()
        test_db.refresh(tenant)

    # Create a family with email and pin.
    register_resp = test_client.post(
        f"/api/v1/child-checkin/public/tenants/{tenant.slug}/pre-register",
        json={
            "family_name": "Familia Recovery",
            "primary_responsible_name": "Joana Recovery",
            "phone_primary": "16911112222",
            "email": "joana.recovery@example.com",
            "public_pin": "1234",
            "children": [{"full_name": "Bebe Recovery"}],
            "guardians": [{"full_name": "Joana Recovery", "relationship": "Responsavel principal", "is_authorized": True}],
        },
    )
    assert register_resp.status_code == 201

    # Request code using service to capture it (endpoint intentionally returns 204 without code).
    fam, code = child_checkin_service.request_public_pin_recovery(
        test_db,
        tenant_id=tenant.id,
        email="joana.recovery@example.com",
    )
    assert fam is not None
    assert code

    verify_resp = test_client.post(
        f"/api/v1/child-checkin/public/tenants/{tenant.slug}/recover/verify",
        json={"email": "joana.recovery@example.com", "code": code},
    )
    assert verify_resp.status_code == 204

    confirm_resp = test_client.post(
        f"/api/v1/child-checkin/public/tenants/{tenant.slug}/recover/confirm",
        json={"email": "joana.recovery@example.com", "code": code, "new_pin": "9999"},
    )
    assert confirm_resp.status_code == 200
    body = confirm_resp.json()
    assert body["token"]

def test_child_checkin_room_monitoring(test_client, test_db, test_admin, monkeypatch):
    monkeypatch.setattr(settings, "CHILD_CHECKIN_DEV_ENABLED", True)

    tenant = get_or_create_test_tenant(test_db)
    test_admin.active_tenant_id = tenant.id
    test_db.commit()
    headers = auth_headers(test_admin)

    family_resp = test_client.post(
        "/api/v1/child-checkin/families",
        json={
            "family_name": "Familia Monitor",
            "primary_responsible_name": "Marcos Monitor",
            "phone_primary": "16955554444",
        },
        headers=headers,
    )
    assert family_resp.status_code == 201
    family_id = int(family_resp.json()["id"])

    child_resp = test_client.post(
        "/api/v1/child-checkin/children",
        json={
            "family_id": family_id,
            "full_name": "Nina Monitor",
            "room_name": "Jardim B",
        },
        headers=headers,
    )
    assert child_resp.status_code == 201
    child_id = int(child_resp.json()["id"])

    checkin_resp = test_client.post(
        "/api/v1/child-checkin/checkins",
        json={
            "family_id": family_id,
            "child_ids": [child_id],
            "context_type": "culto",
            "context_name": "Culto Manha",
            "room_name": "Jardim B",
        },
        headers=headers,
    )
    assert checkin_resp.status_code == 201

    monitor_resp = test_client.get("/api/v1/child-checkin/rooms/Jardim%20B/monitoring", headers=headers)
    assert monitor_resp.status_code == 200
    rows = monitor_resp.json()
    assert len(rows) >= 1
    assert any(row["child_name"] == "Nina Monitor" for row in rows)


def test_child_checkin_room_setup_qr_scan_and_checkout_context(test_client, test_db, test_admin, monkeypatch):
    monkeypatch.setattr(settings, "CHILD_CHECKIN_DEV_ENABLED", True)

    tenant = get_or_create_test_tenant(test_db)
    if not tenant.slug:
        tenant.slug = "igreja-kids"
    test_admin.active_tenant_id = tenant.id
    test_db.commit()
    headers = auth_headers(test_admin)

    room_resp = test_client.post(
        "/api/v1/child-checkin/rooms",
        json={
            "name": "Jardim C",
            "age_range_label": "4-7 anos",
            "description": "Sala principal infantil",
        },
        headers=headers,
    )
    assert room_resp.status_code == 201
    room = room_resp.json()
    assert room["name"] == "Jardim C"

    family_resp = test_client.post(
        "/api/v1/child-checkin/families",
        json={
            "family_name": "Familia QR",
            "primary_responsible_name": "Paula QR",
            "phone_primary": "16977770000",
        },
        headers=headers,
    )
    assert family_resp.status_code == 201
    family = family_resp.json()

    child_resp = test_client.post(
        "/api/v1/child-checkin/children",
        json={
            "family_id": int(family["id"]),
            "full_name": "Bia QR",
            "room_name": "Jardim C",
            "photo_url": "https://example.com/bia.jpg",
            "allergies": "Corante",
        },
        headers=headers,
    )
    assert child_resp.status_code == 201
    child = child_resp.json()

    guardian_resp = test_client.post(
        "/api/v1/child-checkin/guardians",
        json={
            "family_id": int(family["id"]),
            "full_name": "Carlos QR",
            "relationship": "Pai",
            "phone": "16966665555",
            "photo_url": "https://example.com/carlos.jpg",
            "is_authorized": True,
        },
        headers=headers,
    )
    assert guardian_resp.status_code == 201
    guardian = guardian_resp.json()

    qr_payload = f"KIDS:{tenant.slug}:{family['family_code']}:{child['id']}"
    scan_resp = test_client.post(
        "/api/v1/child-checkin/checkins/scan-qr",
        json={
            "qr_payload": qr_payload,
            "context_name": "Culto Noite",
            "context_type": "culto",
            "accompanied_by_name": "Paula QR",
        },
        headers=headers,
    )
    assert scan_resp.status_code == 201
    record = scan_resp.json()
    assert record["status"] == "checked_in"
    assert record["room_name"] == "Jardim C"

    checkout_ctx_resp = test_client.get(
        f"/api/v1/child-checkin/checkins/{record['id']}/checkout-context",
        headers=headers,
    )
    assert checkout_ctx_resp.status_code == 200
    checkout_ctx = checkout_ctx_resp.json()
    assert checkout_ctx["child_name"] == "Bia QR"
    assert len(checkout_ctx["guardians"]) >= 1
    assert any(row["id"] == guardian["id"] for row in checkout_ctx["guardians"])

    label_resp = test_client.get(f"/api/v1/child-checkin/checkins/{record['id']}/label", headers=headers)
    assert label_resp.status_code == 200
    label = label_resp.json()
    assert label["child_name"] == "Bia QR"
    assert label["security_code"] == record["security_code"]

    checkout_resp = test_client.post(
        f"/api/v1/child-checkin/checkins/{record['id']}/checkout",
        json={
            "security_code": record["security_code"],
            "pickup_guardian_id": int(guardian["id"]),
            "pickup_person_name": "Carlos QR",
        },
        headers=headers,
    )
    assert checkout_resp.status_code == 200
    assert checkout_resp.json()["status"] == "checked_out"

    audit_resp = test_client.get("/api/v1/child-checkin/audits?limit=20", headers=headers)
    assert audit_resp.status_code == 200
    audits = audit_resp.json()
    assert len(audits) >= 1
    assert any(item["action"] in {"checkin_created", "checkout_completed"} for item in audits)
