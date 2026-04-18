from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, model_validator


class ChildCheckinFamilyBase(BaseModel):
    family_name: str = Field(min_length=2, max_length=255)
    primary_responsible_name: Optional[str] = None
    secondary_responsible_name: Optional[str] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class ChildCheckinFamilyCreate(ChildCheckinFamilyBase):
    pass


class ChildCheckinFamilyUpdate(BaseModel):
    family_name: Optional[str] = None
    primary_responsible_name: Optional[str] = None
    secondary_responsible_name: Optional[str] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ChildCheckinFamilyResponse(ChildCheckinFamilyBase):
    id: int
    family_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChildCheckinChildBase(BaseModel):
    family_id: int
    full_name: str = Field(min_length=2, max_length=255)
    birth_date: Optional[date] = None
    age_group: Optional[str] = None
    room_name: Optional[str] = None
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    allergies: Optional[str] = None
    medical_restrictions: Optional[str] = None
    special_needs: Optional[str] = None
    behavioral_notes: Optional[str] = None


class ChildCheckinChildCreate(ChildCheckinChildBase):
    is_visitor: bool = False


class ChildCheckinChildUpdate(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    age_group: Optional[str] = None
    room_name: Optional[str] = None
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    allergies: Optional[str] = None
    medical_restrictions: Optional[str] = None
    special_needs: Optional[str] = None
    behavioral_notes: Optional[str] = None
    is_active: Optional[bool] = None


class ChildCheckinChildResponse(ChildCheckinChildBase):
    id: int
    is_active: bool
    is_visitor: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChildCheckinGuardianBase(BaseModel):
    family_id: int
    full_name: str = Field(min_length=2, max_length=255)
    relationship: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None


class ChildCheckinGuardianCreate(ChildCheckinGuardianBase):
    is_authorized: bool = True


class ChildCheckinGuardianUpdate(BaseModel):
    full_name: Optional[str] = None
    relationship: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    is_authorized: Optional[bool] = None
    notes: Optional[str] = None


class ChildCheckinGuardianResponse(ChildCheckinGuardianBase):
    id: int
    is_authorized: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChildCheckinCreate(BaseModel):
    family_id: int
    child_ids: list[int] = Field(min_length=1)
    context_type: str = "culto"
    context_name: str
    room_name: str
    accompanied_by_name: Optional[str] = None


class ChildCheckinCheckoutRequest(BaseModel):
    security_code: Optional[str] = None
    qr_token: Optional[str] = None
    pickup_guardian_id: Optional[int] = None
    pickup_person_name: Optional[str] = None
    exception_notes: Optional[str] = None


class ChildCheckinRecordResponse(BaseModel):
    id: int
    family_id: int
    child_id: int
    context_type: str
    context_name: str
    room_name: str
    checkin_at: datetime
    checkout_at: Optional[datetime] = None
    status: str
    security_code: str
    qr_token: str
    accompanied_by_name: Optional[str] = None
    pickup_guardian_id: Optional[int] = None
    pickup_person_name: Optional[str] = None
    exception_notes: Optional[str] = None
    alert_snapshot: Optional[str] = None

    model_config = {"from_attributes": True}


class ChildCheckinVisitorQuickCreate(BaseModel):
    child_name: str
    child_age: Optional[int] = None
    responsible_name: str
    phone: str
    room_name: str
    context_name: str
    context_type: str = "culto"
    important_notes: Optional[str] = None


class ChildCheckinNotificationCreate(BaseModel):
    family_id: Optional[int] = None
    child_id: Optional[int] = None
    channel: str = "email"
    message_type: str
    message: str


class ChildCheckinNotificationResponse(BaseModel):
    id: int
    tenant_id: int
    family_id: Optional[int] = None
    child_id: Optional[int] = None
    channel: str
    message_type: str
    message: str
    delivery_status: str
    created_by_user_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChildCheckinRoomScopeCreate(BaseModel):
    user_id: int
    room_name: str


class ChildCheckinRoomScopeResponse(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    room_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChildCheckinSummaryResponse(BaseModel):
    total_checkins: int
    active_checkins: int
    completed_checkouts: int
    unique_children: int
    visitors: int
    alerts_count: int


class ChildCheckinPublicGuardianCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    relationship: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    is_authorized: bool = True


class ChildCheckinPublicChildCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    birth_date: Optional[date] = None
    age_group: Optional[str] = None
    room_name: Optional[str] = None
    gender: Optional[str] = None
    photo_url: Optional[str] = None
    allergies: Optional[str] = None
    medical_restrictions: Optional[str] = None
    special_needs: Optional[str] = None
    behavioral_notes: Optional[str] = None
    notes: Optional[str] = None


class ChildCheckinPublicChildUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    birth_date: Optional[date] = None
    allergies: Optional[str] = None
    notes: Optional[str] = None
    medical_restrictions: Optional[str] = None
    special_needs: Optional[str] = None
    behavioral_notes: Optional[str] = None
    gender: Optional[str] = None


class ChildCheckinPublicPreRegistrationCreate(BaseModel):
    family_name: str = Field(min_length=2, max_length=255)
    primary_responsible_name: Optional[str] = None
    secondary_responsible_name: Optional[str] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    email: EmailStr
    notes: Optional[str] = None
    # Optional PIN to allow the responsible to "log in" later and reuse the data (Kids App).
    public_pin: Optional[str] = Field(default=None, min_length=4, max_length=12)
    children: list[ChildCheckinPublicChildCreate] = Field(min_length=1)
    guardians: list[ChildCheckinPublicGuardianCreate] = Field(default_factory=list)


class ChildCheckinVirtualCardGuardianResponse(BaseModel):
    guardian_id: int
    full_name: str
    relationship: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    is_authorized: bool


class ChildCheckinVirtualCardResponse(BaseModel):
    child_id: int
    child_name: str
    family_name: str
    family_code: str
    room_name: Optional[str] = None
    child_photo_url: Optional[str] = None
    qr_payload: str
    guardians: list[ChildCheckinVirtualCardGuardianResponse]


class ChildCheckinPublicPreRegistrationResponse(BaseModel):
    tenant_slug: str
    family_id: int
    family_code: str
    cards: list[ChildCheckinVirtualCardResponse]
    token: Optional[str] = None
    email_sent: bool = False
    email_error: Optional[str] = None


class ChildCheckinPublicLoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=6, max_length=40)
    pin: str = Field(min_length=4, max_length=12)

    @model_validator(mode="after")
    def validate_identifier(self):
        if not self.email and not self.phone:
            raise ValueError("Informe o e-mail.")
        return self


class ChildCheckinPublicRecoveryRequest(BaseModel):
    email: EmailStr


class ChildCheckinPublicRecoveryVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)


class ChildCheckinPublicRecoveryConfirm(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)
    new_pin: str = Field(min_length=4, max_length=12)


class ChildCheckinPublicLoginResponse(BaseModel):
    tenant_slug: str
    family_id: int
    family_code: str
    token: str


class ChildCheckinPublicMeResponse(BaseModel):
    tenant_slug: str
    family: ChildCheckinFamilyResponse
    children: list[ChildCheckinChildResponse]
    guardians: list[ChildCheckinGuardianResponse]

    model_config = {"from_attributes": True}


class ChildCheckinVirtualCardSearchResponse(BaseModel):
    tenant_slug: str
    family_id: int
    family_code: str
    cards: list[ChildCheckinVirtualCardResponse]


class ChildCheckinRoomMonitorEntryResponse(BaseModel):
    checkin_id: int
    child_id: int
    child_name: str
    child_photo_url: Optional[str] = None
    family_id: int
    family_name: str
    primary_responsible_name: Optional[str] = None
    phone_primary: Optional[str] = None
    whatsapp_link: Optional[str] = None
    room_name: str
    checkin_at: datetime
    alert_snapshot: Optional[str] = None
    security_code: str


class ChildCheckinRoomBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    age_range_label: Optional[str] = None
    min_age_months: Optional[int] = Field(default=None, ge=0, le=240)
    max_age_months: Optional[int] = Field(default=None, ge=0, le=240)
    capacity: Optional[int] = Field(default=None, ge=1, le=500)
    description: Optional[str] = None


class ChildCheckinRoomCreate(ChildCheckinRoomBase):
    pass


class ChildCheckinRoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    age_range_label: Optional[str] = None
    min_age_months: Optional[int] = Field(default=None, ge=0, le=240)
    max_age_months: Optional[int] = Field(default=None, ge=0, le=240)
    capacity: Optional[int] = Field(default=None, ge=1, le=500)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ChildCheckinRoomResponse(ChildCheckinRoomBase):
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChildCheckinQrScanRequest(BaseModel):
    qr_payload: str = Field(min_length=6, max_length=255)
    context_name: str = Field(min_length=2, max_length=255)
    context_type: str = "culto"
    room_name_override: Optional[str] = None
    accompanied_by_name: Optional[str] = None


class ChildCheckinLabelPayloadResponse(BaseModel):
    checkin_id: int
    child_name: str
    family_name: str
    room_name: str
    context_name: str
    security_code: str
    qr_token: str
    checkin_at: datetime


class ChildCheckinCheckoutContextGuardianResponse(BaseModel):
    id: int
    full_name: str
    relationship: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    is_authorized: bool


class ChildCheckinCheckoutContextResponse(BaseModel):
    checkin_id: int
    child_id: int
    child_name: str
    child_photo_url: Optional[str] = None
    family_id: int
    family_name: str
    primary_responsible_name: Optional[str] = None
    phone_primary: Optional[str] = None
    room_name: str
    checkin_at: datetime
    security_code: str
    qr_token: str
    guardians: list[ChildCheckinCheckoutContextGuardianResponse]


class ChildCheckinAuditResponse(BaseModel):
    id: int
    tenant_id: int
    record_id: Optional[int] = None
    action: str
    performed_by_user_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChildCheckinOpsContextPreset(BaseModel):
    label: str = Field(min_length=1, max_length=40)
    context_name: str = Field(min_length=2, max_length=255)


class ChildCheckinSettingsResponse(BaseModel):
    ops_context_presets: list[ChildCheckinOpsContextPreset]


class ChildCheckinSettingsUpdate(BaseModel):
    ops_context_presets: list[ChildCheckinOpsContextPreset] = Field(default_factory=list, max_length=12)
