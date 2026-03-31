from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, field_validator


class CellBase(BaseModel):
    name: str
    weekday: str
    meeting_time: time
    address: Optional[str] = None

    @field_validator("weekday")
    @classmethod
    def validate_weekday(cls, value: str) -> str:
        allowed = {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        }
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("weekday must be monday to sunday")
        return normalized


class CellCreate(CellBase):
    status: str = "active"


class CellUpdate(BaseModel):
    name: Optional[str] = None
    weekday: Optional[str] = None
    meeting_time: Optional[time] = None
    address: Optional[str] = None
    status: Optional[str] = None

    @field_validator("weekday")
    @classmethod
    def validate_weekday(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        }
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("weekday must be monday to sunday")
        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {"active", "inactive", "multiplied"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("status must be active, inactive or multiplied")
        return normalized


class CellStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"active", "inactive", "multiplied"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("status must be active, inactive or multiplied")
        return normalized


class CellResponse(CellBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellMemberBase(BaseModel):
    full_name: str
    contact: Optional[str] = None


def _normalize_member_stage(value: str) -> str:
    allowed = {"visitor", "assiduo", "member"}
    normalized = value.strip().lower()
    if normalized not in allowed:
        raise ValueError("stage must be visitor, assiduo or member")
    return normalized


class CellMemberCreate(CellMemberBase):
    status: str = "active"
    user_id: Optional[int] = None
    stage: str = "member"

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, value: str) -> str:
        return _normalize_member_stage(value)


class CellMemberUpdate(BaseModel):
    full_name: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    user_id: Optional[int] = None
    stage: Optional[str] = None

    @field_validator("stage")
    @classmethod
    def validate_stage(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return _normalize_member_stage(value)


class CellMemberResponse(CellMemberBase):
    id: int
    user_id: Optional[int] = None
    stage: str
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellMemberLinkCreate(BaseModel):
    start_date: Optional[date] = None


class CellMemberLinkResponse(BaseModel):
    id: int
    cell_id: int
    member_id: int
    start_date: date
    end_date: Optional[date] = None
    active: bool
    transfer_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellLeaderAssignmentCreate(BaseModel):
    member_id: int
    discipler_member_id: Optional[int] = None
    role: str = "co_leader"
    is_primary: bool = False
    start_date: Optional[date] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        allowed = {"leader", "co_leader"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("role must be leader or co_leader")
        return normalized


class CellLeaderAssignmentUpdate(BaseModel):
    discipler_member_id: Optional[int] = None
    role: Optional[str] = None
    is_primary: Optional[bool] = None
    active: Optional[bool] = None
    end_date: Optional[date] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        allowed = {"leader", "co_leader"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("role must be leader or co_leader")
        return normalized


class CellLeaderAssignmentResponse(BaseModel):
    id: int
    cell_id: int
    member_id: int
    discipler_member_id: Optional[int] = None
    role: str
    is_primary: bool
    start_date: date
    end_date: Optional[date] = None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellMemberTransferRequest(BaseModel):
    target_cell_id: int
    transfer_date: Optional[date] = None
    transfer_reason: Optional[str] = None


class CellMemberPromoteRequest(BaseModel):
    target_stage: str

    @field_validator("target_stage")
    @classmethod
    def validate_target_stage(cls, value: str) -> str:
        return _normalize_member_stage(value)


class CellMeetingBase(BaseModel):
    meeting_date: date
    theme: Optional[str] = None
    notes: Optional[str] = None


class CellMeetingCreate(CellMeetingBase):
    pass


class CellMeetingUpdate(BaseModel):
    meeting_date: Optional[date] = None
    theme: Optional[str] = None
    notes: Optional[str] = None


class CellMeetingResponse(CellMeetingBase):
    id: int
    cell_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellMeetingAttendanceItem(BaseModel):
    member_id: int
    attendance_status: str = "present"
    notes: Optional[str] = None

    @field_validator("attendance_status")
    @classmethod
    def validate_attendance_status(cls, value: str) -> str:
        allowed = {"present", "absent", "justified"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("attendance_status must be present, absent or justified")
        return normalized


class CellMeetingAttendancesBulkRequest(BaseModel):
    items: list[CellMeetingAttendanceItem]


class CellMeetingAttendanceResponse(BaseModel):
    id: int
    meeting_id: int
    member_id: int
    attendance_status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellVisitorCreate(BaseModel):
    full_name: str
    contact: Optional[str] = None
    is_first_time: bool = True
    notes: Optional[str] = None


class CellVisitorResponse(BaseModel):
    id: int
    full_name: str
    contact: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellMeetingVisitorResponse(BaseModel):
    id: int
    meeting_id: int
    visitor_id: int
    is_first_time: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CellSummaryResponse(BaseModel):
    cell_id: int
    cell_name: str
    active_members: int
    meetings_count: int
    visitors_count: int
    average_frequency_percent: float


class CellGrowthResponse(BaseModel):
    cell_id: int
    period_start: date
    period_end: date
    new_members: int
    retained_members: int
    recurrent_visitors: int


class CellFrequencyPoint(BaseModel):
    meeting_id: int
    meeting_date: date
    present: int
    active_members: int
    frequency_percent: float


class CellRetentionResponse(BaseModel):
    cell_id: int
    period_start: date
    period_end: date
    active_at_start: int
    active_at_end: int
    retained_members: int
    retention_rate_percent: float


class CellRecurringVisitorItem(BaseModel):
    visitor_id: int
    full_name: str
    contact: Optional[str] = None
    visits_count: int


class CellRecurringVisitorsResponse(BaseModel):
    cell_id: int
    period_start: date
    period_end: date
    total_recurring_visitors: int
    visitors: list[CellRecurringVisitorItem]


class CellHistoryPoint(BaseModel):
    month: str
    meetings_count: int
    presents_count: int
    visitors_count: int
    new_members_count: int
    average_frequency_percent: float


class CellMissingReportWeek(BaseModel):
    week_start: date
    week_end: date


class CellDashboardInsightsResponse(BaseModel):
    cell_id: int
    period_start: date
    period_end: date
    meetings_count: int
    total_visitors: int
    member_frequency_percent: float
    assiduous_members_count: int
    visitors_average_per_meeting: float
    low_frequency_meetings_count: int
    weeks_without_reports_count: int
    weeks_without_reports: list[CellMissingReportWeek]


class CellVisitorsByDatePoint(BaseModel):
    date: date
    visitors_count: int


class CellWeeklyPresencePoint(BaseModel):
    week_start: date
    week_end: date
    present_total: int
    absent_total: int
    justified_total: int
    expected_total: int


class CellVisitorRetentionBucket(BaseModel):
    bucket_label: str
    visitors_count: int


class CellCompositionSlice(BaseModel):
    label: str
    count: int
    percent: float


class CellDashboardChartsResponse(BaseModel):
    cell_id: int
    period_start: date
    period_end: date
    visitors_by_date: list[CellVisitorsByDatePoint]
    weekly_presence: list[CellWeeklyPresencePoint]
    visitor_retention: list[CellVisitorRetentionBucket]
    composition: list[CellCompositionSlice]
