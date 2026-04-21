from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash, verify_password
from app.db.models.role import Role, tenant_membership_role
from app.db.models.tenant_membership import TenantMembership
from app.db.models.user import User
from app.schemas.user import UserCreate, UserTenantLinkRequest, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def _normalize_role_ids(role_id: int | None, role_ids: list[int] | None) -> list[int]:
    raw_ids = []
    if role_ids is not None:
        raw_ids.extend(role_ids)
    if role_id is not None:
        raw_ids.insert(0, role_id)

    normalized: list[int] = []
    for item in raw_ids:
        try:
            value = int(item)
        except (TypeError, ValueError):
            continue
        if value > 0 and value not in normalized:
            normalized.append(value)
    return normalized


def _get_roles_for_tenant(db: Session, tenant_id: int, role_ids: list[int]) -> list[Role]:
    if not role_ids:
        return []
    roles = (
        db.query(Role)
        .filter(Role.tenant_id == tenant_id, Role.id.in_(role_ids), Role.active.is_(True))
        .all()
    )
    by_id = {role.id: role for role in roles}
    return [by_id[role_id] for role_id in role_ids if role_id in by_id]


def get_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def get_users_for_tenant(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
    role_id: int | None = None,
    is_active: bool | None = None,
    membership_active_only: bool = True,
) -> list[User]:
    query = (
        db.query(User)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .options(
            selectinload(User.tenant_memberships).selectinload(TenantMembership.role_obj),
            selectinload(User.tenant_memberships).selectinload(TenantMembership.roles).selectinload(Role.permissions),
            selectinload(User.tenant_memberships).selectinload(TenantMembership.tenant),
            selectinload(User.active_tenant),
            selectinload(User.role_obj),
        )
        .filter(TenantMembership.tenant_id == tenant_id)
    )

    if membership_active_only:
        query = query.filter(TenantMembership.is_active.is_(True))

    if search:
        normalized = search.strip().lower()
        if normalized:
            like_pattern = f"%{normalized}%"
            query = query.filter(
                or_(
                    func.lower(User.email).like(like_pattern),
                    func.lower(func.coalesce(User.full_name, "")).like(like_pattern),
                )
            )

    if role_id is not None:
        query = (
            query.outerjoin(
                tenant_membership_role,
                tenant_membership_role.c.tenant_membership_id == TenantMembership.id,
            )
            .filter(or_(TenantMembership.role_id == role_id, tenant_membership_role.c.role_id == role_id))
            .distinct()
        )

    if is_active is not None:
        query = query.filter(User.is_active.is_(is_active))

    return query.order_by(User.created_at.desc(), User.id.desc()).offset(skip).limit(limit).all()


def get_user_for_tenant(db: Session, user_id: int, tenant_id: int) -> Optional[User]:
    return (
        db.query(User)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .options(
            selectinload(User.tenant_memberships).selectinload(TenantMembership.role_obj),
            selectinload(User.tenant_memberships).selectinload(TenantMembership.roles).selectinload(Role.permissions),
            selectinload(User.tenant_memberships).selectinload(TenantMembership.tenant),
            selectinload(User.active_tenant),
            selectinload(User.role_obj),
        )
        .filter(User.id == user_id, TenantMembership.tenant_id == tenant_id)
        .first()
    )


def create_user(db: Session, user_create: UserCreate, tenant_id: int | None = None) -> User:
    hashed = get_password_hash(user_create.password)
    role_name = user_create.role
    selected_roles: list[Role] = []
    if tenant_id is not None:
        selected_role_ids = _normalize_role_ids(user_create.role_id, user_create.role_ids)
        selected_roles = _get_roles_for_tenant(db, tenant_id, selected_role_ids)
        if selected_role_ids and len(selected_roles) != len(selected_role_ids):
            raise ValueError("One or more roles were not found for this tenant")
        if selected_roles:
            role_name = selected_roles[0].name.lower()

    user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        role=role_name,
        role_id=selected_roles[0].id if selected_roles else user_create.role_id,
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
            role_id=selected_roles[0].id if selected_roles else user_create.role_id,
            is_active=True,
            is_default=True,
        )
        db.add(membership)
        membership.roles = selected_roles
        user.active_tenant_id = tenant_id
        db.commit()
        db.refresh(user)
    return user


def link_user_to_tenant(db: Session, link_request: UserTenantLinkRequest, tenant_id: int) -> Optional[User]:
    user = get_user_by_email(db, link_request.email)
    if user is None:
        return None

    existing_membership = (
        db.query(TenantMembership)
        .filter(
            TenantMembership.user_id == user.id,
            TenantMembership.tenant_id == tenant_id,
        )
        .first()
    )
    if existing_membership is not None:
        raise ValueError("User is already linked to this tenant")

    role_name = link_request.role
    selected_role_ids = _normalize_role_ids(link_request.role_id, link_request.role_ids)
    selected_roles = _get_roles_for_tenant(db, tenant_id, selected_role_ids)
    if selected_role_ids and len(selected_roles) != len(selected_role_ids):
        raise ValueError("One or more roles were not found for this tenant")
    if selected_roles:
        role_name = selected_roles[0].name.lower()

    if link_request.is_default:
        (
            db.query(TenantMembership)
            .filter(TenantMembership.user_id == user.id, TenantMembership.is_default.is_(True))
            .update({"is_default": False}, synchronize_session=False)
        )

    has_membership = db.query(TenantMembership.id).filter(TenantMembership.user_id == user.id).first() is not None
    membership = TenantMembership(
        user_id=user.id,
        tenant_id=tenant_id,
        role=role_name,
        role_id=selected_roles[0].id if selected_roles else link_request.role_id,
        is_active=True,
        is_default=link_request.is_default or not has_membership,
    )
    db.add(membership)
    membership.roles = selected_roles

    if user.active_tenant_id is None or membership.is_default:
        user.active_tenant_id = tenant_id

    db.commit()
    return get_user_for_tenant(db, user.id, tenant_id)


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
    role_ids = update_data.get("role_ids")
    roles_should_update = "role_id" in update_data or "role_ids" in update_data
    selected_roles: list[Role] = []
    if roles_should_update:
        selected_role_ids = _normalize_role_ids(role_id, role_ids)
        selected_roles = _get_roles_for_tenant(db, tenant_id, selected_role_ids)
        if selected_role_ids and len(selected_roles) != len(selected_role_ids):
            raise ValueError("One or more roles were not found for this tenant")
        if selected_roles:
            resolved_role_name = selected_roles[0].name.lower()

    for field, value in update_data.items():
        if field in {"role", "role_id", "role_ids"}:
            continue
        setattr(user, field, value)

    if membership:
        if roles_should_update:
            membership.roles = selected_roles
            membership.role_id = selected_roles[0].id if selected_roles else None
        if "role" in update_data and update_data["role"] is not None:
            membership.role = update_data["role"]
        elif resolved_role_name is not None:
            membership.role = resolved_role_name
        if "is_active" in update_data and update_data["is_active"] is not None:
            membership.is_active = update_data["is_active"]

    if resolved_role_name is not None:
        user.role = resolved_role_name
        user.role_id = selected_roles[0].id if selected_roles else role_id
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
