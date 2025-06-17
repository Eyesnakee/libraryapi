from sqlalchemy.orm import declarative_base
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

logger.info("SQLAlchemy Base class created")
