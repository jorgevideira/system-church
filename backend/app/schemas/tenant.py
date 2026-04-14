from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    name: str
    slug: str
    public_display_name: Optional[str] = Field(None, max_length=255)
    public_description: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, max_length=20)
    secondary_color: Optional[str] = Field(None, max_length=20)
    logo_url: Optional[str] = Field(None, max_length=500)
    support_email: Optional[str] = Field(None, max_length=255)
    support_whatsapp: Optional[str] = Field(None, max_length=50)
    landing_hero_background_url: Optional[str] = Field(None, max_length=500)
    landing_pix_key: Optional[str] = Field(None, max_length=255)
    landing_bank_name: Optional[str] = Field(None, max_length=255)
    landing_bank_agency: Optional[str] = Field(None, max_length=120)
    landing_bank_account: Optional[str] = Field(None, max_length=120)
    landing_service_times: Optional[str] = Field(None, max_length=2000)
    landing_address: Optional[str] = Field(None, max_length=500)
    landing_location_url: Optional[str] = Field(None, max_length=1000)
    landing_footer_text: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class TenantResponse(TenantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TenantCreate(BaseModel):
    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=120)
    public_display_name: Optional[str] = Field(None, max_length=255)
    public_description: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, max_length=20)
    secondary_color: Optional[str] = Field(None, max_length=20)
    logo_url: Optional[str] = Field(None, max_length=500)
    support_email: Optional[str] = Field(None, max_length=255)
    support_whatsapp: Optional[str] = Field(None, max_length=50)
    landing_hero_background_url: Optional[str] = Field(None, max_length=500)
    landing_pix_key: Optional[str] = Field(None, max_length=255)
    landing_bank_name: Optional[str] = Field(None, max_length=255)
    landing_bank_agency: Optional[str] = Field(None, max_length=120)
    landing_bank_account: Optional[str] = Field(None, max_length=120)
    landing_service_times: Optional[str] = Field(None, max_length=2000)
    landing_address: Optional[str] = Field(None, max_length=500)
    landing_location_url: Optional[str] = Field(None, max_length=1000)
    landing_footer_text: Optional[str] = Field(None, max_length=500)


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=120)
    public_display_name: Optional[str] = Field(None, max_length=255)
    public_description: Optional[str] = Field(None, max_length=500)
    primary_color: Optional[str] = Field(None, max_length=20)
    secondary_color: Optional[str] = Field(None, max_length=20)
    logo_url: Optional[str] = Field(None, max_length=500)
    support_email: Optional[str] = Field(None, max_length=255)
    support_whatsapp: Optional[str] = Field(None, max_length=50)
    landing_hero_background_url: Optional[str] = Field(None, max_length=500)
    landing_pix_key: Optional[str] = Field(None, max_length=255)
    landing_bank_name: Optional[str] = Field(None, max_length=255)
    landing_bank_agency: Optional[str] = Field(None, max_length=120)
    landing_bank_account: Optional[str] = Field(None, max_length=120)
    landing_service_times: Optional[str] = Field(None, max_length=2000)
    landing_address: Optional[str] = Field(None, max_length=500)
    landing_location_url: Optional[str] = Field(None, max_length=1000)
    landing_footer_text: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class TenantBrandingResponse(BaseModel):
    id: int
    slug: str
    name: str
    public_display_name: Optional[str] = None
    public_description: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    support_email: Optional[str] = None
    support_whatsapp: Optional[str] = None
    landing_hero_background_url: Optional[str] = None
    landing_pix_key: Optional[str] = None
    landing_bank_name: Optional[str] = None
    landing_bank_agency: Optional[str] = None
    landing_bank_account: Optional[str] = None
    landing_service_times: Optional[str] = None
    landing_address: Optional[str] = None
    landing_location_url: Optional[str] = None
    landing_footer_text: Optional[str] = None

    model_config = {"from_attributes": True}


class TenantPaymentSettingsResponse(BaseModel):
    payment_provider: str = "internal"
    payment_pix_enabled: bool = True
    payment_card_enabled: bool = True
    mercadopago_public_key: Optional[str] = None
    mercadopago_integrator_id: Optional[str] = None
    mercadopago_access_token_configured: bool = False
    mercadopago_webhook_secret_configured: bool = False
    mercadopago_live_ready: bool = False
    checkout_mode: str = "internal"

    model_config = {"from_attributes": True}


class TenantPaymentSettingsUpdate(BaseModel):
    payment_provider: Optional[str] = Field(None, max_length=50)
    payment_pix_enabled: Optional[bool] = None
    payment_card_enabled: Optional[bool] = None
    mercadopago_public_key: Optional[str] = Field(None, max_length=255)
    mercadopago_integrator_id: Optional[str] = Field(None, max_length=255)
    mercadopago_access_token: Optional[str] = Field(None, max_length=255)
    mercadopago_webhook_secret: Optional[str] = Field(None, max_length=255)
    clear_mercadopago_access_token: bool = False
    clear_mercadopago_webhook_secret: bool = False
