from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.config import settings
from app.core.security import create_access_token
from app.core.password import get_password_hash
from app.crud.user import user as crud_user
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = crud_user.create(db, email=user_in.email, hashed_password=hashed_password)
    logger.info(f"New user registered: {db_user.email}")

    access_token = create_access_token(
        subject=str(db_user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}
