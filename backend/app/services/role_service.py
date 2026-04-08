from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models.role import Role, Permission
from app.schemas.role import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate


def get_permissions(db: Session, skip: int = 0, limit: int = 20) -> List[Permission]:
    return db.query(Permission).offset(skip).limit(limit).all()


def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.name == name).first()


def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    db_permission = Permission(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def update_permission(db: Session, permission_id: int, permission_in: PermissionUpdate) -> Optional[Permission]:
    db_permission = get_permission(db, permission_id)
    if not db_permission:
        return None
    update_data = permission_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_permission, field, value)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def delete_permission(db: Session, permission_id: int) -> bool:
    db_permission = get_permission(db, permission_id)
    if not db_permission:
        return False
    db.delete(db_permission)
    db.commit()
    return True


def get_roles_for_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 20) -> List[Role]:
    return (
        db.query(Role)
        .filter(Role.tenant_id == tenant_id)
        .order_by(Role.name.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_role(db: Session, role_id: int, tenant_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id, Role.tenant_id == tenant_id).first()


def get_role_by_name(db: Session, name: str, tenant_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name, Role.tenant_id == tenant_id).first()


def create_role(db: Session, role_in: RoleCreate, tenant_id: int) -> Role:
    permissions = []
    if role_in.permission_ids:
        permissions = db.query(Permission).filter(Permission.id.in_(role_in.permission_ids)).all()

    db_role = Role(
        tenant_id=tenant_id,
        name=role_in.name,
        description=role_in.description,
        is_admin=role_in.is_admin,
        active=role_in.active,
        permissions=permissions,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role_in: RoleUpdate, tenant_id: int) -> Optional[Role]:
    db_role = get_role(db, role_id, tenant_id)
    if not db_role:
        return None

    update_data = role_in.model_dump(exclude_unset=True)
    permission_ids = update_data.pop("permission_ids", None)

    for field, value in update_data.items():
        setattr(db_role, field, value)

    if permission_ids is not None:
        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        db_role.permissions = permissions

    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int, tenant_id: int) -> bool:
    db_role = get_role(db, role_id, tenant_id)
    if not db_role:
        return False
    db.delete(db_role)
    db.commit()
    return True


def assign_permissions_to_role(db: Session, role_id: int, permission_ids: List[int], tenant_id: int) -> Optional[Role]:
    db_role = get_role(db, role_id, tenant_id)
    if not db_role:
        return None
    permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
    db_role.permissions = permissions
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_role_permissions(db: Session, role_id: int, tenant_id: int) -> List[Permission]:
    db_role = get_role(db, role_id, tenant_id)
    if not db_role:
        return []
    return db_role.permissions
