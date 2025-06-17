from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator
import logging
import os

logger = logging.getLogger(__name__)


def get_database_url():
    if os.getenv("TESTING"):
        return os.getenv(
            "DATABASE_URL",
            "postgresql://test_user:test_password@localhost/test_library_db",
        )
    return os.getenv(
        "DATABASE_URL", "postgresql://library_user:3569@localhost/library_db"
    )


database_url = get_database_url()

try:
    engine = create_engine(database_url, pool_pre_ping=True)
    logger.info(f"Database engine created for: {database_url}")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger.info("Session factory created")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        logger.debug("Database session started")
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        logger.debug("Database session closed")
        db.close()


def create_tables():
    if os.getenv("TESTING"):
        logger.info("Skipping table creation in testing mode")
        return

    try:
        from .base import Base
        from .models import User, Book, Reader, BorrowedBook

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise
