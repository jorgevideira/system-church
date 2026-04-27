from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_membership, get_current_tenant, get_db, require_editor
from app.core.constants import ROLE_ADMIN, ROLE_EDITOR, ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.cell import (
    CellCreate,
    CellLeaderAssignmentCreate,
    CellLeaderAssignmentResponse,
    CellLeaderAssignmentUpdate,
    CellMemberCreate,
    CellMemberLinkCreate,
    CellMemberLinkUpdate,
    CellMemberLinkResponse,
    CellMemberResponse,
    CellMemberTransferRequest,
    CellMeetingAttendancesBulkRequest,
    CellMeetingAttendanceResponse,
    CellMeetingCreate,
    CellMeetingResponse,
    CellMeetingUpdate,
    CellMeetingVisitorResponse,
    CellSummaryResponse,
    PublicCellResponse,
    CellFrequencyPoint,
    CellGrowthResponse,
    CellRetentionResponse,
    CellRecurringVisitorsResponse,
    CellHistoryPoint,
    CellDashboardInsightsResponse,
    CellDashboardChartsResponse,
    CellVisitorCreate,
    CellMemberUpdate,
    CellResponse,
    CellStatusUpdate,
    CellUpdate,
    CellMemberPromoteRequest,
)
from app.schemas.cell_orgchart import OrgChartResponse
from app.schemas.user import UserResponse
from app.services import cell_service, user_service

router = APIRouter()

CELL_VIEW_PERMISSIONS = {
    "cells_dashboard_view",
    "cells_cells_view",
    "cells_people_view",
    "cells_meetings_view",
    "cells_leaders_view",
    "cells_disciplers_view",
    "cells_network_pastors_view",
    "cells_orgchart_view",
    "cells_lost_sheep_view",
}

CELL_MANAGE_PERMISSIONS = {
    "cells_cells_create",
    "cells_cells_edit",
    "cells_cells_delete",
    "cells_people_add_visitor",
    "cells_people_add_assiduo",
    "cells_people_add_member",
    "cells_people_promote_member",
    "cells_people_transfer_member",
    "cells_people_disable_member",
    "cells_meetings_create",
    "cells_attendance_manage",
    "cells_leaders_create",
    "cells_leaders_edit",
    "cells_leaders_delete",
    "cells_disciplers_create",
    "cells_disciplers_edit",
    "cells_disciplers_delete",
    "cells_network_pastors_create",
    "cells_network_pastors_edit",
    "cells_network_pastors_delete",
    "cells_lost_sheep_manage",
}


def _active_permission_names(membership: TenantMembership) -> set[str]:
    names: set[str] = set()
    for role_obj in [getattr(membership, "role_obj", None), *(getattr(membership, "roles", []) or [])]:
        permissions = getattr(role_obj, "permissions", None)
        if not permissions:
            continue
        names.update(
            permission.name
            for permission in permissions
            if permission and permission.active and permission.name
        )
    return names


def _is_role_obj_admin(membership: TenantMembership) -> bool:
    return any(
        role_obj and role_obj.is_admin
        for role_obj in [getattr(membership, "role_obj", None), *(getattr(membership, "roles", []) or [])]
    )


def _membership_role_names(membership: TenantMembership) -> set[str]:
    names = {str(getattr(membership, "role", "") or "").lower()}
    role_obj = getattr(membership, "role_obj", None)
    if role_obj and role_obj.name:
        names.add(role_obj.name.lower())
    names.update(role.name.lower() for role in getattr(membership, "roles", []) or [] if role and role.name)
    return names


def _has_any_cell_view_permission(membership: TenantMembership) -> bool:
    return bool(_active_permission_names(membership) & CELL_VIEW_PERMISSIONS)


def _has_any_cell_manage_permission(membership: TenantMembership) -> bool:
    return bool(_active_permission_names(membership) & CELL_MANAGE_PERMISSIONS)


def _is_editor_user(user: User, membership: TenantMembership) -> bool:
    role_names = _membership_role_names(membership)
    return (
        user.role in (ROLE_ADMIN, ROLE_EDITOR)
        or role_names & {ROLE_ADMIN, ROLE_EDITOR}
        or _is_role_obj_admin(membership)
    )


def _get_allowed_cell_ids_for_user(db: Session, user: User, membership: TenantMembership, tenant: Tenant) -> Optional[list[int]]:
    if _is_editor_user(user, membership):
        return None
    role_names = _membership_role_names(membership)
    if user.role == ROLE_LEADER or ROLE_LEADER in role_names:
        return cell_service.list_cell_ids_led_by_user(db, user, tenant.id)
    if user.role == ROLE_DISCIPLER or ROLE_DISCIPLER in role_names:
        return cell_service.list_cell_ids_supervised_by_discipler_user(db, user, tenant.id)
    if user.role == ROLE_NETWORK_PASTOR or ROLE_NETWORK_PASTOR in role_names:
        return cell_service.list_cell_ids_supervised_by_network_pastor_user(db, user, tenant.id)
    if _has_any_cell_view_permission(membership):
        return None
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cell access not allowed")


def _require_cell_access(db: Session, user: User, membership: TenantMembership, tenant: Tenant, cell_id: int) -> None:
    if _is_editor_user(user, membership):
        return
    mode = None
    role_names = _membership_role_names(membership)
    if user.role == ROLE_LEADER or ROLE_LEADER in role_names:
        mode = "leader"
    elif user.role == ROLE_DISCIPLER or ROLE_DISCIPLER in role_names:
        mode = "discipler"
    elif user.role == ROLE_NETWORK_PASTOR or ROLE_NETWORK_PASTOR in role_names:
        mode = "network_pastor"
    if mode:
        if not cell_service.user_has_access_to_cell(db, user, tenant.id, cell_id, mode=mode):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this cell")
        return
    if _has_any_cell_view_permission(membership):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cell access not allowed")


def _require_editor_or_leader(user: User, membership: TenantMembership) -> None:
    role_names = _membership_role_names(membership)
    if (
        user.role in (ROLE_ADMIN, ROLE_EDITOR, ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR)
        or role_names & {ROLE_ADMIN, ROLE_EDITOR, ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR}
        or _is_role_obj_admin(membership)
        or _has_any_cell_manage_permission(membership)
    ):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Editor or leader access required")


def _require_people_delete_access(user: User, membership: TenantMembership) -> None:
    role_names = _membership_role_names(membership)
    if (
        user.role in (ROLE_ADMIN, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR)
        or role_names & {ROLE_ADMIN, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR}
        or _is_role_obj_admin(membership)
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only discipler, network pastor, or super admin can delete people from a cell",
    )

@router.get("/", response_model=list[CellResponse])
def list_cells(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellResponse]:
    allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
    return cell_service.list_cells(db, current_tenant.id, status_filter=status_filter, allowed_cell_ids=allowed_cell_ids)


@router.get("/public/tenants/{tenant_slug}/cells", response_model=list[PublicCellResponse])
def list_public_cells(
    tenant_slug: str,
    db: Session = Depends(get_db),
) -> list[PublicCellResponse]:
    tenant, cells = cell_service.list_public_cells(db, tenant_slug)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return [PublicCellResponse.model_validate(cell) for cell in cells]


@router.get("/my", response_model=list[CellResponse])
def list_my_cells(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellResponse]:
    allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
    return cell_service.list_cells(db, current_tenant.id, status_filter=status_filter, allowed_cell_ids=allowed_cell_ids)


@router.get("/orgchart", response_model=OrgChartResponse)
def get_org_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> OrgChartResponse:
    # Access is controlled by org-chart role scope or by view permissions for admins/editors.
    allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
    return cell_service.get_cells_org_chart(db, current_tenant.id, allowed_cell_ids=allowed_cell_ids)


@router.post("/", response_model=CellResponse, status_code=status.HTTP_201_CREATED)
def create_cell(
    payload: CellCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellResponse:
    return cell_service.create_cell(db, payload, current_tenant.id)


@router.get("/{cell_id}", response_model=CellResponse)
def get_cell(
    cell_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellResponse:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell


@router.put("/{cell_id}", response_model=CellResponse)
def update_cell(
    cell_id: int,
    payload: CellUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellResponse:
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.update_cell(db, cell, payload)


@router.patch("/{cell_id}/status", response_model=CellResponse)
def update_cell_status(
    cell_id: int,
    payload: CellStatusUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellResponse:
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.update_cell(db, cell, CellUpdate(status=payload.status))


@router.delete("/{cell_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cell(
    cell_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    cell_service.delete_cell(db, cell)


@router.get("/members/all", response_model=list[CellMemberResponse])
def list_members(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellMemberResponse]:
    allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
    return cell_service.list_members(db, current_tenant.id, status_filter=status_filter, allowed_cell_ids=allowed_cell_ids)


@router.post("/members/all", response_model=CellMemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: CellMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMemberResponse:
    _require_editor_or_leader(current_user, current_membership)
    try:
        return cell_service.create_member(db, payload, current_tenant.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/members/user-candidates", response_model=list[UserResponse])
def list_member_user_candidates(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[UserResponse]:
    _require_editor_or_leader(current_user, current_membership)
    return user_service.get_users_for_tenant(db, current_tenant.id, skip=skip, limit=limit)


@router.put("/members/{member_id}", response_model=CellMemberResponse)
def update_member(
    member_id: int,
    payload: CellMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMemberResponse:
    _require_editor_or_leader(current_user, current_membership)
    requested_status = str(payload.status or "").strip().lower() if payload.status is not None else None
    if requested_status == "inactive" or payload.is_active is False:
        _require_people_delete_access(current_user, current_membership)
    if current_user.role in (ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR) or current_membership.role in (ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR):
        allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
        if not cell_service.member_is_in_cells(db, member_id, current_tenant.id, allowed_cell_ids):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this member")
    member = cell_service.get_member(db, member_id, current_tenant.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    try:
        return cell_service.update_member(db, member, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{cell_id}/members", response_model=list[CellMemberLinkResponse])
def list_cell_members(
    cell_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellMemberLinkResponse]:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.list_cell_members(db, current_tenant.id, cell_id)


@router.get("/{cell_id}/people", response_model=list[CellMemberResponse])
def list_cell_people(
    cell_id: int,
    stage_filter: Optional[str] = Query(None, alias="stage"),
    on_date: Optional[date] = Query(None, alias="on_date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellMemberResponse]:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.list_cell_people(db, current_tenant.id, cell_id, stage_filter=stage_filter, on_date=on_date)


@router.post("/{cell_id}/members/{member_id}", response_model=CellMemberLinkResponse, status_code=status.HTTP_201_CREATED)
def assign_member_to_cell(
    cell_id: int,
    member_id: int,
    payload: CellMemberLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMemberLinkResponse:
    _require_editor_or_leader(current_user, current_membership)
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")

    member = cell_service.get_member(db, member_id, current_tenant.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    try:
        return cell_service.assign_member_to_cell(db, current_tenant.id, cell_id, member_id, start_date=payload.start_date)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/{cell_id}/members/{member_id}", response_model=CellMemberLinkResponse)
def update_member_link(
    cell_id: int,
    member_id: int,
    payload: CellMemberLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMemberLinkResponse:
    _require_editor_or_leader(current_user, current_membership)
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")

    member = cell_service.get_member(db, member_id, current_tenant.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    try:
        return cell_service.update_member_link(
            db,
            current_tenant.id,
            cell_id=cell_id,
            member_id=member_id,
            start_date=payload.start_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{cell_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_member_from_cell(
    cell_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    _require_people_delete_access(current_user, current_membership)
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")

    member = cell_service.get_member(db, member_id, current_tenant.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    try:
        cell_service.unassign_member_from_cell(db, current_tenant.id, cell_id=cell_id, member_id=member_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{cell_id}/members/{member_id}/transfer", response_model=CellMemberLinkResponse)
def transfer_member(
    cell_id: int,
    member_id: int,
    payload: CellMemberTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMemberLinkResponse:
    _require_editor_or_leader(current_user, current_membership)
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    _require_cell_access(db, current_user, current_membership, current_tenant, payload.target_cell_id)
    current_cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not current_cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Current cell not found")

    target_cell = cell_service.get_cell(db, payload.target_cell_id, current_tenant.id)
    if not target_cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target cell not found")

    member = cell_service.get_member(db, member_id, current_tenant.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    try:
        return cell_service.transfer_member(
            db,
            current_tenant.id,
            member_id=member_id,
            target_cell_id=payload.target_cell_id,
            transfer_date=payload.transfer_date,
            transfer_reason=payload.transfer_reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{cell_id}/members/{member_id}/promote", response_model=CellMemberResponse)
def promote_member(
    cell_id: int,
    member_id: int,
    payload: CellMemberPromoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMemberResponse:
    _require_editor_or_leader(current_user, current_membership)
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)

    member = cell_service.get_member(db, member_id, current_tenant.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    try:
        return cell_service.promote_member_stage(
            db,
            tenant_id=current_tenant.id,
            cell_id=cell_id,
            member=member,
            target_stage=payload.target_stage,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{cell_id}/leaders", response_model=list[CellLeaderAssignmentResponse])
def list_leaders(
    cell_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellLeaderAssignmentResponse]:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.list_leader_assignments(db, current_tenant.id, cell_id)


@router.post("/{cell_id}/leaders", response_model=CellLeaderAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_leader(
    cell_id: int,
    payload: CellLeaderAssignmentCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellLeaderAssignmentResponse:
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")

    member = cell_service.get_member(db, payload.member_id, current_tenant.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if payload.discipler_member_id is not None:
        discipler = cell_service.get_member(db, payload.discipler_member_id, current_tenant.id)
        if not discipler:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discipler member not found")

    try:
        return cell_service.assign_leader(db, current_tenant.id, cell_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{cell_id}/leaders/{assignment_id}", response_model=CellLeaderAssignmentResponse)
def update_leader_assignment(
    cell_id: int,
    assignment_id: int,
    payload: CellLeaderAssignmentUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellLeaderAssignmentResponse:
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")

    assignment = cell_service.get_leader_assignment(db, assignment_id, current_tenant.id)
    if not assignment or assignment.cell_id != cell_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leader assignment not found")

    return cell_service.update_leader_assignment(db, assignment, payload)


@router.delete("/{cell_id}/leaders/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leader_assignment(
    cell_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")

    assignment = cell_service.get_leader_assignment(db, assignment_id, current_tenant.id)
    if not assignment or assignment.cell_id != cell_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leader assignment not found")

    cell_service.delete_leader_assignment(db, assignment)


@router.get("/{cell_id}/meetings", response_model=list[CellMeetingResponse])
def list_meetings(
    cell_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellMeetingResponse]:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")

    return cell_service.list_meetings(db, current_tenant.id, cell_id, start_date=start_date, end_date=end_date)


@router.post("/{cell_id}/meetings", response_model=CellMeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    cell_id: int,
    payload: CellMeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMeetingResponse:
    _require_editor_or_leader(current_user, current_membership)
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.create_meeting(db, current_tenant.id, cell_id, payload)


@router.get("/meetings/{meeting_id}", response_model=CellMeetingResponse)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMeetingResponse:
    meeting = cell_service.get_meeting(db, meeting_id, current_tenant.id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, meeting.cell_id)
    return meeting


@router.put("/meetings/{meeting_id}", response_model=CellMeetingResponse)
def update_meeting(
    meeting_id: int,
    payload: CellMeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMeetingResponse:
    _require_editor_or_leader(current_user, current_membership)
    meeting = cell_service.get_meeting(db, meeting_id, current_tenant.id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, meeting.cell_id)
    return cell_service.update_meeting(db, meeting, payload)


@router.post("/meetings/{meeting_id}/attendances/bulk", response_model=list[CellMeetingAttendanceResponse])
def upsert_meeting_attendances(
    meeting_id: int,
    payload: CellMeetingAttendancesBulkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellMeetingAttendanceResponse]:
    _require_editor_or_leader(current_user, current_membership)
    meeting = cell_service.get_meeting(db, meeting_id, current_tenant.id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, meeting.cell_id)
    return cell_service.upsert_meeting_attendances(db, current_tenant.id, meeting_id, payload.items)


@router.get("/meetings/{meeting_id}/attendances", response_model=list[CellMeetingAttendanceResponse])
def list_meeting_attendances(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellMeetingAttendanceResponse]:
    meeting = cell_service.get_meeting(db, meeting_id, current_tenant.id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, meeting.cell_id)
    return cell_service.list_meeting_attendances(db, current_tenant.id, meeting_id)


@router.post("/meetings/{meeting_id}/visitors", response_model=CellMeetingVisitorResponse, status_code=status.HTTP_201_CREATED)
def add_meeting_visitor(
    meeting_id: int,
    payload: CellVisitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellMeetingVisitorResponse:
    _require_editor_or_leader(current_user, current_membership)
    meeting = cell_service.get_meeting(db, meeting_id, current_tenant.id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, meeting.cell_id)
    return cell_service.add_meeting_visitor(db, current_tenant.id, meeting_id, payload)


@router.get("/meetings/{meeting_id}/visitors", response_model=list[CellMeetingVisitorResponse])
def list_meeting_visitors(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellMeetingVisitorResponse]:
    meeting = cell_service.get_meeting(db, meeting_id, current_tenant.id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, meeting.cell_id)
    return cell_service.list_meeting_visitors(db, current_tenant.id, meeting_id)


@router.get("/dashboard/summary", response_model=list[CellSummaryResponse])
def dashboard_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellSummaryResponse]:
    allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
    return cell_service.get_cells_summary(
        db,
        current_tenant.id,
        start_date=start_date,
        end_date=end_date,
        allowed_cell_ids=allowed_cell_ids,
    )


@router.get("/{cell_id}/dashboard/frequency", response_model=list[CellFrequencyPoint])
def dashboard_frequency(
    cell_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellFrequencyPoint]:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.get_cell_frequency(db, cell_id, start_date=start_date, end_date=end_date)


@router.get("/{cell_id}/dashboard/growth", response_model=CellGrowthResponse)
def dashboard_growth(
    cell_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellGrowthResponse:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return cell_service.get_cell_growth(db, cell_id, start_date, end_date)


@router.get("/{cell_id}/dashboard/retention", response_model=CellRetentionResponse)
def dashboard_retention(
    cell_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellRetentionResponse:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be >= start_date")
    return cell_service.get_cell_retention(db, cell_id, start_date, end_date)


@router.get("/{cell_id}/dashboard/visitors-recurring", response_model=CellRecurringVisitorsResponse)
def dashboard_visitors_recurring(
    cell_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellRecurringVisitorsResponse:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be >= start_date")
    return cell_service.get_cell_recurring_visitors(db, cell_id, start_date, end_date)


@router.get("/{cell_id}/dashboard/history", response_model=list[CellHistoryPoint])
def dashboard_history(
    cell_id: int,
    months: int = Query(6, ge=1, le=24),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> list[CellHistoryPoint]:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    if (start_date and not end_date) or (end_date and not start_date):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_date and end_date must be provided together")
    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be >= start_date")
    return cell_service.get_cell_history(db, cell_id, months=months, start_date=start_date, end_date=end_date)


@router.get("/{cell_id}/dashboard/insights", response_model=CellDashboardInsightsResponse)
def dashboard_insights(
    cell_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellDashboardInsightsResponse:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be >= start_date")
    return cell_service.get_cell_dashboard_insights(db, cell_id, start_date, end_date)


@router.get("/{cell_id}/dashboard/charts", response_model=CellDashboardChartsResponse)
def dashboard_charts(
    cell_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> CellDashboardChartsResponse:
    _require_cell_access(db, current_user, current_membership, current_tenant, cell_id)
    cell = cell_service.get_cell(db, cell_id, current_tenant.id)
    if not cell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be >= start_date")
    return cell_service.get_cell_dashboard_charts(db, cell_id, start_date, end_date)


@router.post("/sync-member-links", status_code=status.HTTP_200_OK)
def sync_member_links(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_editor),
) -> dict:
    """Sincroniza CellMemberLink com dados de presença. Admin only."""
    return cell_service.sync_cell_member_links_from_attendance(db)
