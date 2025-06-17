from fastapi import APIRouter
import logging

from .auth import router as auth_router
from .books import router as books_router
from .borrow import router as borrow_router
from .readers import router as readers_router

logger = logging.getLogger(__name__)

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(books_router, prefix="/books", tags=["Books"])
api_router.include_router(borrow_router, prefix="/borrow", tags=["Borrow"])
api_router.include_router(readers_router, prefix="/readers", tags=["Readers"])

logger.info("API router initialized with all endpoints")

__all__ = ["api_router"]
