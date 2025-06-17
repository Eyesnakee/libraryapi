import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from app.api.router import api_router
from app.db.session import create_tables

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("TESTING"):
        try:
            create_tables()
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    else:
        logger.info("Running in TESTING mode, skipping table creation")
    yield


app = FastAPI(
    title="Library Management API",
    version="11.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Library API", "docs": "/docs", "redoc": "/redoc"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Library Management API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}


app.include_router(api_router)
