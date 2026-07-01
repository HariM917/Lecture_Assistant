import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # FastAPI
    APP_NAME: str = "Multilingual Lecture Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://lecture_user:lecture_pass@localhost:5432/lecture_db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_EXPIRY: int = 3600
    
    # API Keys
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    
    # Models
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    
    # Supported Languages
    SUPPORTED_LANGUAGES: dict = {
        "ta": "Tamil",
        "hi": "Hindi",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "en": "English"
    }
    
    # NLP Settings
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
