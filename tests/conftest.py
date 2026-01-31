import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db, engine as prod_engine
from app.models.document import Document  # noqa: F401
from app.models.reaction import Reaction  # noqa: F401
from app.main import app as fastapi_app


@pytest.fixture()
def db_session():
    """Create a new database session for a test."""
    # Use an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # Create a new session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """Create a test client."""
    # Ensure tables exist in production database before TestClient startup
    Base.metadata.create_all(bind=prod_engine)

    with TestClient(fastapi_app) as c:
        yield c
