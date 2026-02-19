# app/config.py
from __future__ import annotations

from functools import lru_cache
from typing import Literal, Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Metadata
    PROJECT_NAME: str = "Restaurant Management API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"

    # We use None as a placeholder to satisfy Pylance's requirement for a default.
    # We use Any for the default to avoid type-mismatch warnings while keeping 
    # the hint as 'str'.
    DATABASE_URL: str = None  # type: ignore[assignment]
    SECRET_KEY: str = None    # type: ignore[assignment]
    
    # Security
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    def model_post_init(self, __context: Any) -> None:
        """
        Since we gave the fields defaults of None to satisfy the linter,
        we must manually ensure they were actually loaded from the environment.
        """
        if self.DATABASE_URL is None:
            raise ValueError("DATABASE_URL must be set in the environment or .env file")
        if self.SECRET_KEY is None:
            raise ValueError("SECRET_KEY must be set in the environment or .env file")


@lru_cache
def get_settings() -> Settings:
    # Pylance is now happy because Settings() doesn't require arguments.
    return Settings()


settings = get_settings()