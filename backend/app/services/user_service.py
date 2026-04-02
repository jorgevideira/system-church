from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.models.role import Role
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_create: UserCreate) -> User:
    hashed = get_password_hash(user_create.password)
    role_name = user_create.role
    if user_create.role_id:
        role_obj = db.query(Role).filter(Role.id == user_create.role_id).first()
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
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    if "role_id" in update_data and update_data["role_id"]:
        role_obj = db.query(Role).filter(Role.id == update_data["role_id"]).first()
        if role_obj:
            update_data["role"] = role_obj.name.lower()
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
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
