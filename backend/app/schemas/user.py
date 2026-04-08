from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserPermissionResponse(BaseModel):
    id: int
    name: str
    category: str
    module: str
    active: bool

    model_config = {"from_attributes": True}


class UserRoleResponse(BaseModel):
    id: int
    name: str
    is_admin: bool
    active: bool
    permissions: list[UserPermissionResponse]

    model_config = {"from_attributes": True}


class TenantSummaryResponse(BaseModel):
    id: int
    name: str
    slug: str
    public_display_name: Optional[str] = None
    public_description: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    support_email: Optional[str] = None
    support_whatsapp: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


class TenantMembershipResponse(BaseModel):
    id: int
    tenant_id: int
    role: str
    role_id: Optional[int] = None
    is_active: bool
    is_default: bool
    tenant: TenantSummaryResponse
    role_obj: Optional[UserRoleResponse] = None

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "viewer"
    role_id: Optional[int] = None


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserTenantLinkRequest(BaseModel):
    email: EmailStr
    role: str = "viewer"
    role_id: Optional[int] = None
    is_default: bool = False


class UserResponse(UserBase):
    id: int
    active_tenant_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    active_tenant: Optional[TenantSummaryResponse] = None
    role_obj: Optional[UserRoleResponse] = None
    tenant_memberships: list[TenantMembershipResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    active_tenant_id: Optional[int] = None
    active_tenant_slug: Optional[str] = None


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    tenant_id: Optional[int] = None


class SwitchTenantRequest(BaseModel):
    tenant_id: int
