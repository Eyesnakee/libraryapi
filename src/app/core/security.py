from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import logging

from app.core.config import settings
from app.core.password import verify_password
from app.schemas.user import UserInDB

logger = logging.getLogger(__name__)

def get_db():
    from app.db.session import get_db as _get_db

    return _get_db()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    try:
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode = {"sub": subject, "exp": expire}
        return jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
    except Exception as e:
        logger.error(f"Token creation failed: {str(e)}")
        raise


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    from app.db.session import get_db
    from app.crud.user import user as crud_user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT token missing 'sub' claim")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
    try:
        db_gen = get_db()
        db = next(db_gen)
        user = crud_user.get(db, id=int(user_id))
        if user is None:
            logger.warning(f"User not found for ID: {user_id}")
            raise credentials_exception
        return UserInDB.model_validate(user)
    except Exception as e:
        logger.error(f"Error retrieving user: {str(e)}")
        raise credentials_exception
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
