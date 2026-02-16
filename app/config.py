# app/config.py
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def model_post_init(self, __context) -> None:
        """Validate required fields are set from .env"""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in .env")
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in .env")


@lru_cache
def get_settings() -> Settings:
    """Load settings (env + .env) once and cache for import-time safety."""
    return Settings()


settings = get_settings()