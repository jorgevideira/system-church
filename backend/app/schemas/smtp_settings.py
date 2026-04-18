from pydantic import BaseModel, EmailStr, Field, field_validator


SMTP_ENCRYPTION_TYPES = {"tls", "ssl", "none"}


class TenantSmtpSettingsResponse(BaseModel):
    host: str | None = None
    port: int = 587
    username: str | None = None
    from_email: EmailStr | None = None
    encryption: str = "tls"
    is_active: bool = True
    has_password: bool = False


class TenantSmtpSettingsUpdate(BaseModel):
    host: str = Field(..., max_length=255)
    port: int = 587
    username: str | None = Field(None, max_length=255)
    password: str | None = Field(None, max_length=500)
    from_email: EmailStr | None = None
    encryption: str = "tls"
    is_active: bool = True

    @field_validator("encryption")
    @classmethod
    def validate_encryption(cls, value: str) -> str:
        if value not in SMTP_ENCRYPTION_TYPES:
            raise ValueError("encryption must be tls, ssl or none")
        return value


class TenantSmtpTestRequest(BaseModel):
    to_email: EmailStr


class TenantSmtpTestResponse(BaseModel):
    status: str
    message: str
