"""Initial setup: create default admin user and system categories."""

from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_CATEGORIES
from app.core.security import get_password_hash
from app.db.models.category import Category
from app.db.models.user import User
from app.utils.logger import logger


def create_default_admin(db: Session) -> None:
    """Create the default admin user if it does not already exist."""
    email = "admin@church.com"
    if db.query(User).filter(User.email == email).first():
        logger.info("Admin user already exists, skipping creation.")
        return
    admin = User(
        email=email,
        full_name="System Administrator",
        role="admin",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
    )
    db.add(admin)
    db.commit()
    logger.info("Default admin user created: %s", email)


def create_default_categories(db: Session) -> None:
    """Create system categories defined in constants if they do not already exist."""
    for cat_data in DEFAULT_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if existing:
            continue
        category = Category(
            name=cat_data["name"],
            description=cat_data.get("description"),
            type=cat_data.get("type", "both"),
            is_system=cat_data.get("is_system", True),
            is_active=True,
        )
        db.add(category)
    db.commit()
    logger.info("Default categories created/verified.")


def setup(db: Session) -> None:
    create_default_admin(db)
    create_default_categories(db)


if __name__ == "__main__":
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        setup(db)
    finally:
        db.close()
