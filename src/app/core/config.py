from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    API_PREFIX: str = Field(
        default="",
        json_schema_extra={
            "env": "API_PREFIX",
            "description": "Prefix for all API routes"
        }
    )
    JWT_SECRET_KEY: str = Field(
        default="super-secret-key", 
        json_schema_extra={
            "env": "JWT_SECRET_KEY",
            "description": "Secret key for JWT token generation"
        }
    )
    JWT_ALGORITHM: str = Field(
        default="HS256", 
        json_schema_extra={
            "env": "JWT_ALGORITHM",
            "description": "Algorithm for JWT token signing"
        }
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, 
        json_schema_extra={
            "env": "ACCESS_TOKEN_EXPIRE_MINUTES",
            "description": "Access token lifetime in minutes"
        }
    )
    
    DEBUG: bool = Field(
        default=False, 
        json_schema_extra={
            "env": "DEBUG",
            "description": "Enable debug mode"
        }
    )
    PROJECT_NAME: str = Field(
        default="Library Management API", 
        json_schema_extra={
            "env": "PROJECT_NAME",
            "description": "Name of the project"
        }
    )

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()