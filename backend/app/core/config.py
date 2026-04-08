from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./church_finance.db"

    # JWT / Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # File uploads
    UPLOAD_DIR: str = "uploads"
    ATTACHMENT_DIR: str = "uploads/transaction_attachments"
    TENANT_LOGO_DIR: str = "uploads/tenant_logos"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Project metadata
    PROJECT_NAME: str = "Church Financial Management System"
    API_V1_STR: str = "/api/v1"
    APP_BASE_URL: str = "http://localhost:8000"
    PUBLIC_APP_URL: str = "http://localhost"

    # Payments
    PAYMENT_PROVIDER: str = "internal"
    MERCADOPAGO_ACCESS_TOKEN: str | None = None
    MERCADOPAGO_PUBLIC_KEY: str | None = None
    MERCADOPAGO_WEBHOOK_SECRET: str | None = None
    MERCADOPAGO_INTEGRATOR_ID: str | None = None

    # Notifications
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_USE_TLS: bool = True
    WHATSAPP_WEBHOOK_URL: str | None = None
    WHATSAPP_WEBHOOK_TOKEN: str | None = None

    # Tenant invitations
    TENANT_INVITATION_EXPIRY_DAYS: int = 7

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()
