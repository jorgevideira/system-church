from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_membership, get_current_tenant, get_db
from app.api.v1.endpoints.cells import (
    _get_allowed_cell_ids_for_user,
    _has_any_cell_manage_permission,
    _has_any_cell_view_permission,
    _is_role_obj_admin,
    _membership_role_names,
    _require_cell_access,
)
from app.core.constants import ROLE_ADMIN, ROLE_DISCIPLER, ROLE_LEADER, ROLE_NETWORK_PASTOR
from app.db.models import User
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.schemas.lost_sheep import LostSheepCreateRequest, LostSheepResponse, LostSheepUpdate
from app.services import lost_sheep_service

router = APIRouter(tags=["lost_sheep"])


def _require_lost_sheep_view_access(user: User, membership: TenantMembership) -> None:
    role_names = _membership_role_names(membership)
    if (
        user.role in (ROLE_ADMIN, ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR)
        or role_names & {ROLE_ADMIN, ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR}
        or _is_role_obj_admin(membership)
        or _has_any_cell_view_permission(membership)
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Lost sheep access not allowed",
    )


def _require_lost_sheep_manage_access(user: User, membership: TenantMembership) -> None:
    role_names = _membership_role_names(membership)
    if (
        user.role in (ROLE_ADMIN, ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR)
        or role_names & {ROLE_ADMIN, ROLE_LEADER, ROLE_DISCIPLER, ROLE_NETWORK_PASTOR}
        or _is_role_obj_admin(membership)
        or _has_any_cell_manage_permission(membership)
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Lost sheep management not allowed",
    )


@router.post("", response_model=LostSheepResponse)
def mark_as_lost_sheep(
    payload: LostSheepCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Mark a member as lost sheep (removes from cell)"""
    _require_lost_sheep_manage_access(current_user, current_membership)
    _require_cell_access(db, current_user, current_membership, current_tenant, payload.cell_id)

    try:
        lost_sheep = lost_sheep_service.mark_member_as_lost_sheep(
            db,
            tenant_id=current_tenant.id,
            member_id=payload.member_id,
            cell_id=payload.cell_id,
            phone_number=payload.phone_number,
            observation=payload.observation,
        )
        return lost_sheep
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[LostSheepResponse])
def list_lost_sheep(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """List all active lost sheep"""
    _require_lost_sheep_view_access(current_user, current_membership)
    allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
    return lost_sheep_service.list_lost_sheep(db, current_tenant.id, allowed_cell_ids=allowed_cell_ids)


@router.get("/{lost_sheep_id}", response_model=LostSheepResponse)
def get_lost_sheep(
    lost_sheep_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Get a specific lost sheep record"""
    _require_lost_sheep_view_access(current_user, current_membership)
    allowed_cell_ids = _get_allowed_cell_ids_for_user(db, current_user, current_membership, current_tenant)
    lost_sheep = lost_sheep_service.get_lost_sheep(db, current_tenant.id, lost_sheep_id, allowed_cell_ids=allowed_cell_ids)
    if not lost_sheep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost sheep record not found"
        )
    
    return lost_sheep


@router.put("/{lost_sheep_id}/visit", response_model=LostSheepResponse)
def record_visit(
    lost_sheep_id: int,
    visit_observation: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Record a visit to a lost sheep"""
    _require_lost_sheep_manage_access(current_user, current_membership)
    lost_sheep = lost_sheep_service.get_lost_sheep(db, current_tenant.id, lost_sheep_id)
    if not lost_sheep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lost sheep record not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, lost_sheep["previous_cell_id"])

    try:
        lost_sheep = lost_sheep_service.update_lost_sheep_visit(
            db,
            tenant_id=current_tenant.id,
            lost_sheep_id=lost_sheep_id,
            visit_date=datetime.utcnow(),
            visit_observation=visit_observation,
        )
        return lost_sheep
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{lost_sheep_id}/reinsert", response_model=LostSheepResponse)
def reinsert_into_cell(
    lost_sheep_id: int,
    target_cell_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Reinsert a lost sheep back into a cell"""
    _require_lost_sheep_manage_access(current_user, current_membership)
    lost_sheep = lost_sheep_service.get_lost_sheep(db, current_tenant.id, lost_sheep_id)
    if not lost_sheep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lost sheep record not found")
    _require_cell_access(db, current_user, current_membership, current_tenant, lost_sheep["previous_cell_id"])
    _require_cell_access(db, current_user, current_membership, current_tenant, target_cell_id)

    try:
        lost_sheep = lost_sheep_service.reinsert_lost_sheep_into_cell(
            db,
            tenant_id=current_tenant.id,
            lost_sheep_id=lost_sheep_id,
            target_cell_id=target_cell_id,
        )
        return lost_sheep
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{lost_sheep_id}")
def delete_lost_sheep(
    lost_sheep_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_membership: TenantMembership = Depends(get_current_membership),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """Delete a lost sheep record"""
    _require_lost_sheep_manage_access(current_user, current_membership)
    lost_sheep = lost_sheep_service.get_lost_sheep(db, current_tenant.id, lost_sheep_id)
    if not lost_sheep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost sheep record not found"
        )
    _require_cell_access(db, current_user, current_membership, current_tenant, lost_sheep["previous_cell_id"])

    success = lost_sheep_service.delete_lost_sheep(db, current_tenant.id, lost_sheep_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost sheep record not found"
        )
    
    return {"detail": "Lost sheep record deleted successfully"}
