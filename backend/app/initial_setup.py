"""Initial setup: create default admin user and system categories."""

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_CATEGORIES
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.models.category import Category
from app.db.models.tenant import Tenant
from app.db.models.tenant_membership import TenantMembership
from app.db.models.transaction_attachment import TransactionAttachment
from app.db.models.user import User
from app.db.session import engine
from app.utils.logger import logger


def ensure_runtime_schema_updates() -> None:
    """Apply small forward-compatible schema updates for existing databases."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "alembic_version" not in tables:
        logger.info("Alembic version table not found yet; skipping runtime schema updates until migrations are applied.")
        return

    if "users" in tables:
        user_columns = {col["name"] for col in inspector.get_columns("users")}
        if "active_tenant_id" not in user_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN active_tenant_id INTEGER"))
            logger.info("Schema update applied: users.active_tenant_id added.")

    if "tenants" in tables:
        tenant_columns = {col["name"] for col in inspector.get_columns("tenants")}
        tenant_runtime_columns = [
            ("landing_hero_background_url", "VARCHAR(500)"),
            ("landing_pix_key", "VARCHAR(255)"),
            ("landing_bank_name", "VARCHAR(255)"),
            ("landing_bank_agency", "VARCHAR(120)"),
            ("landing_bank_account", "VARCHAR(120)"),
            ("landing_service_times", "VARCHAR(2000)"),
            ("landing_address", "VARCHAR(500)"),
            ("landing_location_url", "VARCHAR(1000)"),
            ("landing_footer_text", "VARCHAR(500)"),
        ]
        for column_name, sql_type in tenant_runtime_columns:
            if column_name not in tenant_columns:
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE tenants ADD COLUMN {column_name} {sql_type}"))
                logger.info("Schema update applied: tenants.%s added.", column_name)

    if "transactions" not in tables:
        return

    if "categories" in tables:
        category_column_defs = {col["name"]: col for col in inspector.get_columns("categories")}
        category_columns = set(category_column_defs)

        if "color" not in category_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE categories ADD COLUMN color VARCHAR(7)"))
            logger.info("Schema update applied: categories.color added.")

        if "icon" not in category_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE categories ADD COLUMN icon VARCHAR(50)"))
            logger.info("Schema update applied: categories.icon added.")

        if "is_active" not in category_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE categories ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"))
            logger.info("Schema update applied: categories.is_active added.")

        if "is_system" not in category_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE categories ADD COLUMN is_system BOOLEAN NOT NULL DEFAULT FALSE"))
            logger.info("Schema update applied: categories.is_system added.")

        if "user_id" in category_columns and category_column_defs["user_id"].get("nullable") is False:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE categories ALTER COLUMN user_id DROP NOT NULL"))
            logger.info("Schema update applied: categories.user_id is now nullable for tenant-based records.")

    if "ministries" in tables:
        ministry_column_defs = {col["name"]: col for col in inspector.get_columns("ministries")}
        ministry_columns = set(ministry_column_defs)

        if "is_active" not in ministry_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE ministries ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"))
            logger.info("Schema update applied: ministries.is_active added.")

        if "user_id" in ministry_columns and ministry_column_defs["user_id"].get("nullable") is False:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE ministries ALTER COLUMN user_id DROP NOT NULL"))
            logger.info("Schema update applied: ministries.user_id is now nullable for tenant-based records.")

    transaction_columns = {col["name"] for col in inspector.get_columns("transactions")}
    if "tenant_id" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN tenant_id INTEGER"))
        logger.info("Schema update applied: transactions.tenant_id added.")

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

    if "bank_account_id" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN bank_account_id INTEGER"))
        logger.info("Schema update applied: transactions.bank_account_id added.")

    if "statement_file_id" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN statement_file_id INTEGER"))
        logger.info("Schema update applied: transactions.statement_file_id added.")

    if "status" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'confirmed'"))
        logger.info("Schema update applied: transactions.status added.")

    if "ai_category_suggestion" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN ai_category_suggestion VARCHAR(100)"))
        logger.info("Schema update applied: transactions.ai_category_suggestion added.")

    if "ai_confidence" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN ai_confidence DOUBLE PRECISION"))
        logger.info("Schema update applied: transactions.ai_confidence added.")

    if "ai_suggested_category_id" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN ai_suggested_category_id INTEGER"))
        logger.info("Schema update applied: transactions.ai_suggested_category_id added.")

    if "reference" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN reference VARCHAR(255)"))
        logger.info("Schema update applied: transactions.reference added.")

    if "dedup_hash" not in transaction_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN dedup_hash VARCHAR(64)"))
        logger.info("Schema update applied: transactions.dedup_hash added.")

    if "transaction_attachments" not in tables:
        TransactionAttachment.__table__.create(bind=engine, checkfirst=True)
        logger.info("Schema update applied: transaction_attachments table created.")

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
    email = settings.FIRST_SUPERUSER.strip().lower()
    if db.query(User).filter(User.email == email).first():
        logger.info("Admin user already exists, skipping creation.")
        return
    admin = User(
        email=email,
        full_name=(settings.FIRST_SUPERUSER_NAME or "System Administrator").strip() or "System Administrator",
        role="admin",
        hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        is_active=True,
    )
    db.add(admin)
    db.commit()
    logger.info("Default admin user created: %s", email)


def create_default_tenant(db: Session) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
    if tenant:
        return tenant
    tenant = Tenant(
        name="Default Church",
        slug="default",
        is_active=True,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    logger.info("Default tenant created: %s", tenant.slug)
    return tenant


def ensure_default_tenant_memberships(db: Session, default_tenant: Tenant) -> None:
    users = db.query(User).all()
    updated = False
    for user in users:
        membership = (
            db.query(TenantMembership)
            .filter(
                TenantMembership.user_id == user.id,
                TenantMembership.tenant_id == default_tenant.id,
            )
            .first()
        )
        if membership is None:
            membership = TenantMembership(
                user_id=user.id,
                tenant_id=default_tenant.id,
                role=user.role or "viewer",
                role_id=user.role_id,
                is_active=user.is_active,
                is_default=True,
            )
            db.add(membership)
            updated = True
        if user.active_tenant_id is None:
            user.active_tenant_id = default_tenant.id
            updated = True
    if updated:
        db.commit()
        logger.info("Default tenant memberships ensured for existing users.")


def create_default_categories(db: Session) -> None:
    """Create system categories defined in constants if they do not already exist."""
    default_tenant = create_default_tenant(db)
    for cat_data in DEFAULT_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_data["name"], Category.tenant_id == default_tenant.id).first()
        if existing:
            continue
        category = Category(
            tenant_id=default_tenant.id,
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

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    required_tables = {"users", "tenants", "tenant_memberships", "categories"}
    if not required_tables.issubset(tables):
        logger.info("Core tables are not ready yet; skipping initial data setup until migrations are applied.")
        return
    
    # Create default data
    create_default_admin(db)
    default_tenant = create_default_tenant(db)
    ensure_default_tenant_memberships(db, default_tenant)
    create_default_categories(db)


if __name__ == "__main__":
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        setup(db)
    finally:
        db.close()
