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

    model_config = {"from_attributes": True}
