from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import TenantSummaryResponse, UserResponse, UserRoleResponse


class TenantInvitationCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    role: str = "viewer"
    role_id: Optional[int] = None
    is_default: bool = False
    expires_in_days: int = Field(7, ge=1, le=30)


class TenantInvitationAcceptRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)

    @field_validator("password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class TenantInvitationResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    role_id: Optional[int] = None
    status: str
    is_default: bool
    invite_token: str
    invite_url: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    tenant: TenantSummaryResponse
    role_obj: Optional[UserRoleResponse] = None
    invited_by_user: Optional[UserResponse] = None
    accepted_user: Optional[UserResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantInvitationPublicResponse(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    status: str
    expires_at: datetime
    is_default: bool
    tenant: TenantSummaryResponse
    role: str
    role_obj: Optional[UserRoleResponse] = None

    model_config = {"from_attributes": True}


class TenantInvitationAcceptResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    active_tenant_id: Optional[int] = None
    active_tenant_slug: Optional[str] = None
    user: UserResponse
