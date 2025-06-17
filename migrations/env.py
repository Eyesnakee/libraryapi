from logging.config import fileConfig
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context
import logging

logger = logging.getLogger("alembic")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

from app.db.base import Base

target_metadata = Base.metadata

from app.db.models import Book, Reader, User, BorrowedBook

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_database_url():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        logger.info("Using database URL from environment variable")
        return db_url
    try:
        from app.core.config import settings

        logger.info("Using database URL from app settings")
        return settings.DATABASE_URL
    except ImportError:
        logger.warning("Could not import app settings")

    default_url = "postgresql://library_user:3569@localhost/library_db"
    logger.info(f"Using default database URL: {default_url}")
    return default_url


db_url = get_database_url()
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        db_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        logger.info("Starting migrations")
        with context.begin_transaction():
            context.run_migrations()
        logger.info("Migrations completed")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
