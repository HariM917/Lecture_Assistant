"""Health and system status routes."""

from fastapi import APIRouter
from datetime import datetime
from app.core.config import get_settings

router = APIRouter(tags=["System"])
settings = get_settings()


@router.get("/", include_in_schema=False)
async def root():
    """Root endpoint — API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "environment": settings.APP_ENVIRONMENT,
        "docs": "/api/docs",
        "supported_languages": list(settings.SUPPORTED_LANGUAGES.keys()),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health", summary="Health Check")
async def health():
    """Liveness probe for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/api/health/", summary="Health Check (API path)")
async def health_api():
    """Alternate health endpoint used by Docker healthcheck."""
    return await health()


@router.get("/api/v1/status", summary="Detailed Status")
async def detailed_status():
    """Detailed system status including service capabilities."""
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENVIRONMENT,
        "mock_mode": settings.MOCK_MODE,
        "database": "sqlite" if settings.is_sqlite else "postgresql",
        "supported_languages": settings.SUPPORTED_LANGUAGES,
        "features": {
            "transcription": True,
            "translation": True,
            "summarization": True,
            "keyword_extraction": True,
            "websocket": True,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
