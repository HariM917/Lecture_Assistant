from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.cache import redis_cache
from app.schemas.schemas import HealthCheck
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    redis_status = "healthy" if redis_cache.health_check() else "unhealthy"
    
    return HealthCheck(
        status="healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        version="1.0.0",
        database=db_status,
        redis=redis_status,
        timestamp=datetime.utcnow()
    )


@router.get("/info")
async def info():
    """Get application info."""
    return {
        "name": "Multilingual Lecture Assistant",
        "version": "1.0.0",
        "description": "Real-time speech-to-text, translation, summarization, and NLP extraction",
        "features": [
            "Speech-to-Text (Whisper)",
            "Machine Translation (Google Translate)",
            "Text Summarization (BART)",
            "Keyword Extraction (spaCy)",
            "Formula Detection (Regex)",
            "Real-time WebSocket Streaming",
            "Session Management",
            "Multi-language Support"
        ]
    }
