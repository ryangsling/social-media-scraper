import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app


TEST_DB_PATH = "./test_part3.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture()
def db_session_factory():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    try:
        yield SessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)


@pytest.fixture()
def client(db_session_factory):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
