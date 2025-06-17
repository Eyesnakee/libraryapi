from .auth import router as auth_router
from .books import router as books_router
from .borrow import router as borrow_router
from .readers import router as readers_router

__all__ = ["auth_router", "books_router", "borrow_router", "readers_router"]
