from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, get_current_active_user, require_admin
from app.db.models.user import User
from app.schemas.role import (
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
)
from app.services import role_service

router = APIRouter()


# ========================
# PERMISSIONS - ENDPOINTS
# ========================


@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> List[PermissionResponse]:
    """Listar todas as permissões"""
    return role_service.get_permissions(db, skip=skip, limit=limit)


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_in: PermissionCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> PermissionResponse:
    """Criar uma nova permissão"""
    existing = role_service.get_permission_by_name(db, permission_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permissão com este nome já existe",
        )
    return role_service.create_permission(db, permission_in)


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> PermissionResponse:
    """Obter detalhes de uma permissão"""
    permission = role_service.get_permission(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissão não encontrada",
        )
    return permission


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> PermissionResponse:
    """Atualizar uma permissão"""
    permission = role_service.update_permission(db, permission_id, permission_in)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissão não encontrada",
        )
    return permission


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    """Deletar uma permissão"""
    if not role_service.delete_permission(db, permission_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissão não encontrada",
        )


# ========================
# ROLES - ENDPOINTS
# ========================


@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> List[RoleResponse]:
    """Listar todas as roles"""
    return role_service.get_roles(db, skip=skip, limit=limit)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> RoleResponse:
    """Criar uma nova role"""
    existing = role_service.get_role_by_name(db, role_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role com este nome já existe",
        )
    return role_service.create_role(db, role_in)


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> RoleResponse:
    """Obter detalhes de uma role"""
    role = role_service.get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrada",
        )
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> RoleResponse:
    """Atualizar uma role"""
    role = role_service.update_role(db, role_id, role_in)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrada",
        )
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    """Deletar uma role"""
    if not role_service.delete_role(db, role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrada",
        )


@router.post("/roles/{role_id}/permissions", response_model=RoleResponse)
def assign_permissions(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> RoleResponse:
    """Atribuir permissões a uma role"""
    role = role_service.assign_permissions_to_role(db, role_id, permission_ids)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrada",
        )
    return role


@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> List[PermissionResponse]:
    """Obter permissões de uma role"""
    return role_service.get_role_permissions(db, role_id)
