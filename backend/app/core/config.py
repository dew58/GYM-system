"""
Application settings loaded from environment variables.
Uses pydantic-settings for type-safe configuration.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Central configuration for the Gym Management System."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "Gym Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./gym.db"

    # ── JWT ──────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ── File Uploads ─────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 5

    # ── First Admin ──────────────────────────────────────
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_EMAIL: str = "admin@gym.local"
    FIRST_ADMIN_PASSWORD: str = "Admin@123"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
