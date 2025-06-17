from sqlalchemy.orm import Session
import logging

from app.db.models import User
from app.core.password import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class CRUDUser:
    def get(self, db: Session, id: int) -> User | None:
        return db.get(User, id)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, email: str, hashed_password: str) -> User:
        try:
            db_user = User(email=email, hashed_password=hashed_password)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User created: {db_user.email}")
            return db_user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise

    def authenticate(self, db: Session, email: str, password: str) -> User | None:
        user = self.get_by_email(db, email=email)
        if not user:
            logger.warning(f"Authentication failed: user {email} not found")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for {email}")
            return None

        logger.info(f"User authenticated: {email}")
        return user


user = CRUDUser()
