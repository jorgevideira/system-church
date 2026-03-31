from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_active_user
from app.core.constants import ROLE_ADMIN, ROLE_LEADER
from app.db.models import User
from app.services import lost_sheep_service
from app.schemas.lost_sheep import LostSheepResponse, LostSheepCreateRequest, LostSheepUpdate
from datetime import datetime

router = APIRouter(tags=["lost_sheep"])


@router.post("", response_model=LostSheepResponse)
def mark_as_lost_sheep(
    payload: LostSheepCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Mark a member as lost sheep (removes from cell)"""
    if current_user.role not in (ROLE_ADMIN, ROLE_LEADER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and admins can mark members as lost sheep"
        )
    
    try:
        lost_sheep = lost_sheep_service.mark_member_as_lost_sheep(
            db,
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
):
    """List all active lost sheep"""
    if current_user.role not in (ROLE_ADMIN, ROLE_LEADER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and admins can view lost sheep"
        )
    
    return lost_sheep_service.list_lost_sheep(db)


@router.get("/{lost_sheep_id}", response_model=LostSheepResponse)
def get_lost_sheep(
    lost_sheep_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific lost sheep record"""
    if current_user.role not in (ROLE_ADMIN, ROLE_LEADER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and admins can view lost sheep"
        )
    
    lost_sheep = lost_sheep_service.get_lost_sheep(db, lost_sheep_id)
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
):
    """Record a visit to a lost sheep"""
    if current_user.role not in (ROLE_ADMIN, ROLE_LEADER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and admins can record visits"
        )
    
    try:
        lost_sheep = lost_sheep_service.update_lost_sheep_visit(
            db,
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
):
    """Reinsert a lost sheep back into a cell"""
    if current_user.role not in (ROLE_ADMIN, ROLE_LEADER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and admins can reinsert lost sheep"
        )
    
    try:
        lost_sheep = lost_sheep_service.reinsert_lost_sheep_into_cell(
            db,
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
):
    """Delete a lost sheep record"""
    if current_user.role not in (ROLE_ADMIN, ROLE_LEADER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leaders and admins can delete lost sheep records"
        )
    
    success = lost_sheep_service.delete_lost_sheep(db, lost_sheep_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost sheep record not found"
        )
    
    return {"detail": "Lost sheep record deleted successfully"}
