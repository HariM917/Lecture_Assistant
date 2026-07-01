"""
Application configuration with environment-aware settings.

Supports development (SQLite, mock services) and production (PostgreSQL, real ML)
modes via environment variables.
"""

import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # ── Application ──────────────────────────────────────────────────
    APP_NAME: str = "Multilingual Lecture Assistant"
    APP_VERSION: str = "2.0.0"
    APP_ENVIRONMENT: str = os.getenv("APP_ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # ── Database ─────────────────────────────────────────────────────
    # SQLite by default for local dev; PostgreSQL for production
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'data' / 'lecture_assistant.db'}",
    )

    # ── Redis ────────────────────────────────────────────────────────
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_EXPIRY: int = 3600

    # ── Service Mode ─────────────────────────────────────────────────
    # When True, services return intelligent mock data even if ML libs are installed
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "False").lower() in ("true", "1", "yes")

    # ── ML Models ────────────────────────────────────────────────────
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    SPACY_MODEL: str = "en_core_web_sm"

    # ── API Keys (optional — services degrade gracefully) ────────────
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")

    # ── Supported Languages ──────────────────────────────────────────
    SUPPORTED_LANGUAGES: dict = {
        "en": "English",
        "ta": "Tamil",
        "hi": "Hindi",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
    }

    # ── Server ───────────────────────────────────────────────────────
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "5000"))

    # ── CORS ─────────────────────────────────────────────────────────
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ]

    # ── File Upload ──────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        str(Path(__file__).resolve().parent.parent.parent / "data" / "uploads"),
    )

    # ── Logging ──────────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def is_production(self) -> bool:
        return self.APP_ENVIRONMENT == "production"

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
