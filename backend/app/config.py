"""
Application configuration using pydantic-settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "HoloTutor API"
    debug: bool = False
    api_version: str = "v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/holotutor"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7  # 7 days

    # Firebase
    firebase_project_id: Optional[str] = None
    firebase_credentials_path: Optional[str] = None

    # AI APIs
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Avatar APIs
    heygen_api_key: Optional[str] = None
    did_api_key: Optional[str] = None

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://holotutor.app"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()
