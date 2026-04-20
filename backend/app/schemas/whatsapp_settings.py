from typing import Any

from pydantic import BaseModel, Field


class TenantWhatsappStatusResponse(BaseModel):
    enabled: bool = False
    configured: bool = False
    mode: str = "simulated"
    instance_name: str | None = None
    webhook_url: str | None = None
    manager_url: str | None = None
    manager_api_key: str | None = None
    webhook_enabled: bool = False
    connection_state: str | None = None
    pairing_code: str | None = None
    qr_image: str | None = None
    qr_updated_at: str | None = None
    last_qr_source: str | None = None
    last_error: str | None = None
    last_event: str | None = None
    last_event_at: str | None = None
    last_webhook_payload: Any = None
    instance_exists: bool = False
    reachable: bool = False
    instance: Any = None


class TenantWhatsappConnectRequest(BaseModel):
    number: str | None = None


class TenantWhatsappActionResponse(BaseModel):
    accepted: bool = True
    message: str | None = None
    response: Any = None
    status: TenantWhatsappStatusResponse | None = None


class TenantWhatsappTestRequest(BaseModel):
    to_phone: str = Field(..., min_length=8, max_length=30)


class TenantWhatsappTestResponse(BaseModel):
    accepted: bool = True
    message: str
    recipient: str
    provider: str | None = None
    gateway_message_id: str | None = None
