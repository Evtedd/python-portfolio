import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.core.deps import get_db
from app.db.base import Base
from app.main import app
from app.models.comment import Comment
from app.models.ticket import Ticket
from app.models.user import User, UserRole
from app.services.users import create_user


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_header(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )
    return auth_header(client, "user@example.com", "password123")


@pytest.fixture()
def admin_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    create_user(
        db_session,
        "admin@example.com",
        "password123",
        role=UserRole.admin,
    )
    return auth_header(client, "admin@example.com", "password123")
