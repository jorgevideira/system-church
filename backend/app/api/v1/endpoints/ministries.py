from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user, require_admin, require_editor
from app.db.models.ministry import Ministry
from app.db.models.user import User
from app.schemas.ministry import MinistryCreate, MinistryResponse, MinistryUpdate

router = APIRouter()


@router.get("/", response_model=List[MinistryResponse])
def list_ministries(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
) -> List[Ministry]:
    return db.query(Ministry).filter(Ministry.is_active.is_(True)).all()


@router.post("/", response_model=MinistryResponse, status_code=status.HTTP_201_CREATED)
def create_ministry(
    ministry_in: MinistryCreate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_editor),
) -> Ministry:
    existing = db.query(Ministry).filter(Ministry.name == ministry_in.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ministry name already exists")
    ministry = Ministry(**ministry_in.model_dump())
    db.add(ministry)
    db.commit()
    db.refresh(ministry)
    return ministry


@router.get("/{ministry_id}", response_model=MinistryResponse)
def get_ministry(
    ministry_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_active_user),
) -> Ministry:
    ministry = db.query(Ministry).filter(Ministry.id == ministry_id).first()
    if not ministry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ministry not found")
    return ministry


@router.put("/{ministry_id}", response_model=MinistryResponse)
def update_ministry(
    ministry_id: int,
    ministry_in: MinistryUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_editor),
) -> Ministry:
    ministry = db.query(Ministry).filter(Ministry.id == ministry_id).first()
    if not ministry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ministry not found")
    update_data = ministry_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ministry, field, value)
    db.commit()
    db.refresh(ministry)
    return ministry


@router.delete("/{ministry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ministry(
    ministry_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    ministry = db.query(Ministry).filter(Ministry.id == ministry_id).first()
    if not ministry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ministry not found")
    db.delete(ministry)
    db.commit()
