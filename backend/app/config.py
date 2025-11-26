"""
Application configuration using pydantic-settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import Optional
import secrets
import warnings


class Settings(BaseSettings):
    # App
    app_name: str = "HoloTutor API"
    debug: bool = False
    api_version: str = "v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/holotutor"
    database_echo: bool = False

    # Redis (for token blacklist and rate limiting)
    redis_url: str = "redis://localhost:6379"

    # JWT Configuration
    jwt_secret_key: str = ""  # MUST be set via environment variable
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60  # 1 hour for access tokens
    jwt_refresh_token_expire_days: int = 7  # 7 days for refresh tokens

    @field_validator('jwt_secret_key', mode='before')
    @classmethod
    def validate_jwt_secret(cls, v):
        """Ensure JWT secret is properly configured"""
        insecure_defaults = ['', 'your-secret-key-change-in-production', 'secret', 'changeme']
        if v in insecure_defaults:
            # Generate a secure random key for development, warn in production
            generated_key = secrets.token_urlsafe(32)
            warnings.warn(
                "JWT_SECRET_KEY not set or using insecure default! "
                "Set JWT_SECRET_KEY environment variable in production. "
                f"Using generated key for this session.",
                UserWarning
            )
            return generated_key
        if len(v) < 32:
            warnings.warn(
                "JWT_SECRET_KEY should be at least 32 characters for security.",
                UserWarning
            )
        return v

    # Firebase
    firebase_project_id: Optional[str] = None
    firebase_credentials_path: Optional[str] = None
    firebase_api_key: Optional[str] = None
    firebase_auth_domain: Optional[str] = None
    firebase_storage_bucket: Optional[str] = None
    firebase_messaging_sender_id: Optional[str] = None
    firebase_app_id: Optional[str] = None

    # AI APIs
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-haiku-20240307"  # Configurable AI model
    openai_api_key: Optional[str] = None

    # Kimi (Moonshot AI) - Primary AI for grading
    kimi_api_key: Optional[str] = None
    kimi_model: str = "moonshot-v1-8k"  # Options: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
    kimi_base_url: str = "https://api.moonshot.cn/v1"

    # ACE Framework (Agentic Context Engine)
    ace_enabled: bool = True  # Enable adaptive learning
    ace_playbook_dir: str = "playbooks"  # Directory for storing learned strategies

    # Avatar APIs
    heygen_api_key: Optional[str] = None
    did_api_key: Optional[str] = None

    # Rate Limiting
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window_seconds: int = 60  # window size

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://holotutor.app"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()
