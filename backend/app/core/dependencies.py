"""
Centralized dependency injection for FastAPI routes.

Each service is instantiated once (cached) and injected via Depends().
Services degrade gracefully when heavy ML dependencies are unavailable.
"""

import logging
from functools import lru_cache
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Transcription Service ────────────────────────────────────────────────────

@lru_cache()
def _create_transcription_service():
    """Create the transcription service (real Whisper or mock)."""
    if settings.MOCK_MODE:
        logger.info("Transcription: MOCK mode (forced by config)")
        from app.services.transcription import MockTranscriptionService
        return MockTranscriptionService()

    try:
        from app.services.whisper_service import WhisperTranscriberService
        service = WhisperTranscriberService(model_name=settings.WHISPER_MODEL)
        logger.info(f"Transcription: Whisper ({settings.WHISPER_MODEL})")
        return service
    except Exception as e:
        logger.warning(f"Transcription: Falling back to mock — {e}")
        from app.services.transcription import MockTranscriptionService
        return MockTranscriptionService()


def get_transcription_service():
    """FastAPI dependency for transcription."""
    return _create_transcription_service()


# ── Translation Service ──────────────────────────────────────────────────────

@lru_cache()
def _create_translation_service():
    """Create the translation service (real or mock)."""
    if settings.MOCK_MODE:
        logger.info("Translation: MOCK mode (forced by config)")
        from app.services.translation import TranslationService
        return TranslationService()

    try:
        from deep_translator import GoogleTranslator  # noqa: F401
        from app.services.translation import RealTranslationService
        logger.info("Translation: Google Translator (via deep-translator)")
        return RealTranslationService()
    except ImportError:
        logger.warning("Translation: Falling back to mock (install deep-translator for real translations)")
        from app.services.translation import TranslationService
        return TranslationService()


def get_translation_service():
    """FastAPI dependency for translation."""
    return _create_translation_service()


# ── NLP Extraction Service ───────────────────────────────────────────────────

@lru_cache()
def _create_nlp_service():
    """Create the NLP extraction service (spaCy or mock)."""
    if settings.MOCK_MODE:
        logger.info("NLP: MOCK mode (forced by config)")
        from app.services.nlp_extraction import NLPExtractionService
        return NLPExtractionService()

    try:
        from app.services.enhanced_nlp import EnhancedNLPService
        service = EnhancedNLPService()
        logger.info("NLP: Enhanced (spaCy + NLTK)")
        return service
    except Exception as e:
        logger.warning(f"NLP: Falling back to basic extraction — {e}")
        from app.services.nlp_extraction import NLPExtractionService
        return NLPExtractionService()


def get_nlp_service():
    """FastAPI dependency for NLP extraction."""
    return _create_nlp_service()


# ── Summarization Service ────────────────────────────────────────────────────

@lru_cache()
def _create_summarization_service():
    """Create the summarization service (transformers or mock)."""
    if settings.MOCK_MODE:
        logger.info("Summarization: MOCK mode (forced by config)")
        from app.services.summarization import SummarizationService
        return SummarizationService()

    try:
        from transformers import pipeline  # noqa: F401
        from app.services.summarization import RealSummarizationService
        logger.info("Summarization: Transformers (BART)")
        return RealSummarizationService()
    except Exception as e:
        logger.warning(f"Summarization: Falling back to extractive — {e}")
        from app.services.summarization import SummarizationService
        return SummarizationService()


def get_summarization_service():
    """FastAPI dependency for summarization."""
    return _create_summarization_service()


# ── Redis Cache ──────────────────────────────────────────────────────────────

@lru_cache()
def _create_cache():
    """Create the cache service (Redis or in-memory)."""
    try:
        from app.services.cache import RedisCache
        cache = RedisCache()
        if cache.health_check():
            logger.info("Cache: Redis")
            return cache
        raise ConnectionError("Redis ping failed")
    except Exception as e:
        logger.warning(f"Cache: In-memory fallback — {e}")
        from app.services.cache import InMemoryCache
        return InMemoryCache()


def get_cache():
    """FastAPI dependency for cache."""
    return _create_cache()
