"""Initial setup: create default admin user and system categories."""

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_CATEGORIES
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.models.category import Category
from app.db.models.user import User
from app.db.session import engine
from app.utils.logger import logger


def ensure_runtime_schema_updates() -> None:
    """Apply small forward-compatible schema updates for existing databases."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "transactions" not in tables:
        return

    transaction_columns = {col["name"] for col in inspector.get_columns("transactions")}
    if "source_bank_name" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN source_bank_name VARCHAR(120)"))
        logger.info("Schema update applied: transactions.source_bank_name added.")

    if "expense_profile" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN expense_profile VARCHAR(20)"))
        logger.info("Schema update applied: transactions.expense_profile added.")

    if "ministry_id" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN ministry_id INTEGER"))
        logger.info("Schema update applied: transactions.ministry_id added.")

    if "payables" in tables:
        payable_columns = {col["name"] for col in inspector.get_columns("payables")}

        if "expense_profile" not in payable_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE payables ADD COLUMN expense_profile VARCHAR(20)"))
            logger.info("Schema update applied: payables.expense_profile added.")

        if "payment_method" not in payable_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE payables ADD COLUMN payment_method VARCHAR(20)"))
            logger.info("Schema update applied: payables.payment_method added.")

        if "attachment_storage_filename" not in payable_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE payables ADD COLUMN attachment_storage_filename VARCHAR(255)"))
            logger.info("Schema update applied: payables.attachment_storage_filename added.")

        if "attachment_original_filename" not in payable_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE payables ADD COLUMN attachment_original_filename VARCHAR(255)"))
            logger.info("Schema update applied: payables.attachment_original_filename added.")

        if "attachment_mime_type" not in payable_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE payables ADD COLUMN attachment_mime_type VARCHAR(100)"))
            logger.info("Schema update applied: payables.attachment_mime_type added.")


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
    # Note: Tables are now created via Alembic migrations, not SQLAlchemy
    # Base.metadata.create_all(bind=engine) should not be called here
    # to avoid conflicts with Alembic version control
    
    # Only run runtime schema updates if needed (for backward compatibility)
    ensure_runtime_schema_updates()
    
    # Create default data
    create_default_admin(db)
    create_default_categories(db)


if __name__ == "__main__":
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        setup(db)
    finally:
        db.close()
