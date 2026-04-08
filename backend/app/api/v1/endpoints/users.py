from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_current_tenant, get_db, require_admin
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserTenantLinkRequest, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[User]:
    return user_service.get_users_for_tenant(db, current_tenant.id, skip=skip, limit=limit)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> User:
    existing = user_service.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return user_service.create_user(db, user_in, tenant_id=current_tenant.id)


@router.post("/link-existing", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def link_existing_user(
    payload: UserTenantLinkRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> User:
    try:
        user = user_service.link_user_to_tenant(db, payload, current_tenant.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> User:
    user = user_service.get_user_for_tenant(db, user_id, current_tenant.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> User:
    user = user_service.update_user_for_tenant(db, user_id, current_tenant.id, user_in)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    deleted = user_service.delete_user_for_tenant(db, user_id, current_tenant.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
