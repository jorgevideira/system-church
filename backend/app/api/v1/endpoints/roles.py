from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_tenant, get_db, require_admin
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.schemas.role import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.services import role_service, role_templates_service

router = APIRouter()


@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _tenant: Tenant = Depends(get_current_tenant),
) -> List[PermissionResponse]:
    return role_service.get_permissions(db, skip=skip, limit=limit)


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_in: PermissionCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _tenant: Tenant = Depends(get_current_tenant),
) -> PermissionResponse:
    existing = role_service.get_permission_by_name(db, permission_in.name)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission with this name already exists")
    return role_service.create_permission(db, permission_in)


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _tenant: Tenant = Depends(get_current_tenant),
) -> PermissionResponse:
    permission = role_service.get_permission(db, permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _tenant: Tenant = Depends(get_current_tenant),
) -> PermissionResponse:
    permission = role_service.update_permission(db, permission_id, permission_in)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    _tenant: Tenant = Depends(get_current_tenant),
) -> None:
    if not role_service.delete_permission(db, permission_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")


@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[RoleResponse]:
    return role_service.get_roles_for_tenant(db, current_tenant.id, skip=skip, limit=limit)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> RoleResponse:
    existing = role_service.get_role_by_name(db, role_in.name, current_tenant.id)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role with this name already exists")
    return role_service.create_role(db, role_in, current_tenant.id)


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> RoleResponse:
    role = role_service.get_role(db, role_id, current_tenant.id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> RoleResponse:
    role = role_service.update_role(db, role_id, role_in, current_tenant.id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> None:
    if not role_service.delete_role(db, role_id, current_tenant.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")


@router.post("/roles/{role_id}/permissions", response_model=RoleResponse)
def assign_permissions(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> RoleResponse:
    role = role_service.assign_permissions_to_role(db, role_id, permission_ids, current_tenant.id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse])
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> List[PermissionResponse]:
    return role_service.get_role_permissions(db, role_id, current_tenant.id)


@router.post("/templates/install-cells-hierarchy")
def install_cells_hierarchy_templates(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> dict:
    """Install default roles for church hierarchy (Líder, Discipulador, Pastor de Rede)."""
    role_ids = role_templates_service.install_cells_hierarchy_roles(db, current_tenant.id)
    return {"installed": role_ids}
