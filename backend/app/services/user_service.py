from typing import Optional

from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash, verify_password
from app.db.models.role import Role
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def get_users_for_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 20) -> list[User]:
    return (
        db.query(User)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .options(
            selectinload(User.tenant_memberships).selectinload(TenantMembership.role_obj),
            selectinload(User.tenant_memberships).selectinload(TenantMembership.tenant),
            selectinload(User.active_tenant),
            selectinload(User.role_obj),
        )
        .filter(TenantMembership.tenant_id == tenant_id, TenantMembership.is_active.is_(True))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_for_tenant(db: Session, user_id: int, tenant_id: int) -> Optional[User]:
    return (
        db.query(User)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .options(
            selectinload(User.tenant_memberships).selectinload(TenantMembership.role_obj),
            selectinload(User.tenant_memberships).selectinload(TenantMembership.tenant),
            selectinload(User.active_tenant),
            selectinload(User.role_obj),
        )
        .filter(User.id == user_id, TenantMembership.tenant_id == tenant_id, TenantMembership.is_active.is_(True))
        .first()
    )


def create_user(db: Session, user_create: UserCreate, tenant_id: int | None = None) -> User:
    hashed = get_password_hash(user_create.password)
    role_name = user_create.role
    if user_create.role_id and tenant_id is not None:
        role_obj = db.query(Role).filter(Role.id == user_create.role_id, Role.tenant_id == tenant_id).first()
        if role_obj:
            role_name = role_obj.name.lower()
    user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        role=role_name,
        role_id=user_create.role_id,
        hashed_password=hashed,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    if tenant_id is not None:
        membership = TenantMembership(
            user_id=user.id,
            tenant_id=tenant_id,
            role=role_name,
            role_id=user_create.role_id,
            is_active=True,
            is_default=True,
        )
        db.add(membership)
        user.active_tenant_id = tenant_id
        db.commit()
        db.refresh(user)
    return user


def update_user_for_tenant(db: Session, user_id: int, tenant_id: int, user_update: UserUpdate) -> Optional[User]:
    user = get_user_for_tenant(db, user_id, tenant_id)
    if not user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    membership = (
        db.query(TenantMembership)
        .filter(TenantMembership.user_id == user.id, TenantMembership.tenant_id == tenant_id)
        .first()
    )

    resolved_role_name = None
    role_id = update_data.get("role_id")
    if role_id:
        role_obj = db.query(Role).filter(Role.id == role_id, Role.tenant_id == tenant_id).first()
        if role_obj:
            resolved_role_name = role_obj.name.lower()

    for field, value in update_data.items():
        if field in {"role", "role_id"}:
            continue
        setattr(user, field, value)

    if membership:
        if role_id is not None:
            membership.role_id = role_id
        if "role" in update_data and update_data["role"] is not None:
            membership.role = update_data["role"]
        elif resolved_role_name is not None:
            membership.role = resolved_role_name
        if "is_active" in update_data and update_data["is_active"] is not None:
            membership.is_active = update_data["is_active"]

    if resolved_role_name is not None:
        user.role = resolved_role_name
        user.role_id = role_id
    elif "role" in update_data and update_data["role"] is not None:
        user.role = update_data["role"]

    db.commit()
    db.refresh(user)
    return user


def delete_user_for_tenant(db: Session, user_id: int, tenant_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False

    membership = (
        db.query(TenantMembership)
        .filter(TenantMembership.user_id == user_id, TenantMembership.tenant_id == tenant_id)
        .first()
    )
    if membership is None:
        return False

    db.delete(membership)
    db.flush()

    next_membership = db.query(TenantMembership).filter(TenantMembership.user_id == user_id).first()
    if user.active_tenant_id == tenant_id:
        user.active_tenant_id = next_membership.tenant_id if next_membership else None

    remaining_memberships = db.query(TenantMembership).filter(TenantMembership.user_id == user_id).count()
    if remaining_memberships == 0:
        db.delete(user)

    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
