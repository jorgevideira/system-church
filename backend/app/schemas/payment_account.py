from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


SUPPORTED_PAYMENT_ACCOUNT_PROVIDERS = {"internal", "mercadopago", "pagbank"}


class PaymentAccountBase(BaseModel):
    provider: str = "internal"
    environment: str = "production"
    label: str = Field(..., max_length=120)
    description: Optional[str] = Field(None, max_length=255)
    is_default: bool = False
    is_active: bool = True
    supports_pix: bool = True
    supports_card: bool = True
    public_key: Optional[str] = Field(None, max_length=255)
    webhook_secret: Optional[str] = Field(None, max_length=255)
    integrator_id: Optional[str] = Field(None, max_length=255)
    account_email: Optional[str] = Field(None, max_length=255)
    app_id: Optional[str] = Field(None, max_length=255)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = str(value or "").strip().lower()
        if normalized not in SUPPORTED_PAYMENT_ACCOUNT_PROVIDERS:
            raise ValueError("provider must be internal, mercadopago or pagbank")
        return normalized

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = str(value or "").strip().lower()
        if normalized not in {"sandbox", "production"}:
            raise ValueError("environment must be sandbox or production")
        return normalized


class PaymentAccountCreate(PaymentAccountBase):
    access_token: Optional[str] = Field(None, max_length=255)


class PaymentAccountUpdate(BaseModel):
    provider: Optional[str] = Field(None, max_length=30)
    environment: Optional[str] = Field(None, max_length=20)
    label: Optional[str] = Field(None, max_length=120)
    description: Optional[str] = Field(None, max_length=255)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    supports_pix: Optional[bool] = None
    supports_card: Optional[bool] = None
    public_key: Optional[str] = Field(None, max_length=255)
    webhook_secret: Optional[str] = Field(None, max_length=255)
    integrator_id: Optional[str] = Field(None, max_length=255)
    account_email: Optional[str] = Field(None, max_length=255)
    app_id: Optional[str] = Field(None, max_length=255)
    access_token: Optional[str] = Field(None, max_length=255)
    clear_access_token: bool = False
    clear_webhook_secret: bool = False

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value or "").strip().lower()
        if normalized not in SUPPORTED_PAYMENT_ACCOUNT_PROVIDERS:
            raise ValueError("provider must be internal, mercadopago or pagbank")
        return normalized

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = str(value or "").strip().lower()
        if normalized not in {"sandbox", "production"}:
            raise ValueError("environment must be sandbox or production")
        return normalized


class PaymentAccountResponse(BaseModel):
    id: int
    tenant_id: int
    provider: str
    environment: str = "production"
    label: str
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    supports_pix: bool
    supports_card: bool
    public_key: Optional[str] = None
    webhook_secret_configured: bool = False
    integrator_id: Optional[str] = None
    account_email: Optional[str] = None
    app_id: Optional[str] = None
    access_token_configured: bool = False
    live_ready: bool = False
    created_at: datetime
    updated_at: datetime


class PaymentAccountSummaryResponse(BaseModel):
    id: int
    provider: str
    label: str
    is_default: bool
    is_active: bool
    supports_pix: bool
    supports_card: bool
