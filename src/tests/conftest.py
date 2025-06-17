import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
import subprocess

os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = (
    "postgresql://test_user:test_password@localhost/test_library_db"
)
os.environ["JWT_SECRET_KEY"] = "test-secret"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.base import Base
from app.core.password import get_password_hash
from app.crud.user import user as crud_user
from app.schemas.user import UserCreate
from app.db.session import get_db

from app.db.models import User, Book, Reader, BorrowedBook

logger = logging.getLogger(__name__)

engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    logger.info("Creating test database and tables")

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS test_schema"))
        conn.execute(text("GRANT ALL PRIVILEGES ON SCHEMA test_schema TO test_user"))
        conn.execute(text("SET search_path TO test_schema"))
        conn.commit()

    for table in Base.metadata.tables.values():
        table.schema = "test_schema"

    Base.metadata.create_all(bind=engine)
    logger.info("Test database tables created")

    yield

    logger.info("Disposing engine connections")
    engine.dispose()

    temp_engine = create_engine(os.environ["DATABASE_URL"])
    with temp_engine.connect() as conn:
        conn.execute(text("DROP SCHEMA test_schema CASCADE"))
        conn.commit()
    temp_engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def clean_tables(db):
    yield
    try:
        db.execute(
            text("TRUNCATE TABLE test_schema.borrowed_books RESTART IDENTITY CASCADE")
        )
        db.execute(text("TRUNCATE TABLE test_schema.users RESTART IDENTITY CASCADE"))
        db.execute(text("TRUNCATE TABLE test_schema.books RESTART IDENTITY CASCADE"))
        db.execute(text("TRUNCATE TABLE test_schema.readers RESTART IDENTITY CASCADE"))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning tables: {str(e)}")
        raise


@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        db.execute(text("SET search_path TO test_schema"))
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def auth_client(client, db):
    user_in = UserCreate(email="test@example.com", password="testpassword")
    hashed_password = get_password_hash(user_in.password)

    from app.crud.user import user as crud_user

    db_user = crud_user.create(db, email=user_in.email, hashed_password=hashed_password)

    response = client.post(
        "/auth/login", data={"username": user_in.email, "password": user_in.password}
    )

    if response.status_code != 200:
        logger.error(f"Login failed: {response.status_code} {response.text}")
        pytest.fail(f"Login failed: {response.status_code} {response.text}")

    response_data = response.json()
    if "access_token" not in response_data:
        logger.error(f"Access token missing in response: {response_data}")
        pytest.fail(f"Access token missing in response: {response_data}")

    token = response_data["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture(scope="function")
def test_book(db):
    book_data = {"title": "Test Book", "author": "Test Author", "copies_available": 1}

    db_book = Book(**book_data)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@pytest.fixture(scope="function")
def test_reader(db):
    reader_data = {"name": "Test Reader", "email": "reader@example.com"}

    db_reader = Reader(**reader_data)
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader
