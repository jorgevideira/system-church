"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.user import User
from app.api.v1.deps import get_db
from app.core.security import get_password_hash, create_access_token
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool ensures all sessions share a single underlying connection,
# which is necessary for in-memory SQLite to persist across sessions.
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def test_client(test_db: Session) -> TestClient:
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db: Session) -> User:
    existing = test_db.query(User).filter(User.email == "user@test.com").first()
    if existing:
        return existing
    user = User(
        email="user@test.com",
        full_name="Test User",
        role="viewer",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_admin(test_db: Session) -> User:
    existing = test_db.query(User).filter(User.email == "admin@test.com").first()
    if existing:
        return existing
    admin = User(
        email="admin@test.com",
        full_name="Test Admin",
        role="admin",
        hashed_password=get_password_hash("adminpass123"),
        is_active=True,
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def test_leader(test_db: Session) -> User:
    existing = test_db.query(User).filter(User.email == "leader@test.com").first()
    if existing:
        return existing
    leader = User(
        email="leader@test.com",
        full_name="Test Leader",
        role="leader",
        hashed_password=get_password_hash("leaderpass123"),
        is_active=True,
    )
    test_db.add(leader)
    test_db.commit()
    test_db.refresh(leader)
    return leader


def auth_headers(user: User) -> dict:
    """Return Authorization headers for *user*."""
    token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"Authorization": f"Bearer {token}"}
