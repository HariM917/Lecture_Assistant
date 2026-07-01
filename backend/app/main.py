"""
FastAPI application factory.

This is the single source of truth for app creation. All route handlers
are in api/routes/. Services are injected via dependencies.py.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import traceback

from app.core.config import get_settings
from app.core.database import init_db

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"   Environment : {settings.APP_ENVIRONMENT}")
    logger.info(f"   Mock Mode   : {'ON' if settings.MOCK_MODE else 'OFF'}")
    logger.info(f"   Database    : {'SQLite' if settings.is_sqlite else 'PostgreSQL'}")
    logger.info(f"   Languages   : {len(settings.SUPPORTED_LANGUAGES)}")
    logger.info("=" * 60)

    # Initialize database tables
    init_db()

    yield

    logger.info("👋 Shutting down — Goodbye!")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Real-time multilingual lecture assistant with speech-to-text, "
            "translation, summarization, and NLP extraction."
        ),
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # ── Middlewares ──────────────────────────────────────────────
    from app.middleware.request_logging import RequestLoggingMiddleware
    from app.middleware.rate_limiter import RateLimitMiddleware
    from app.middleware.error_handler import register_error_handlers

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, limit=100, window_secs=60)

    # ── CORS ─────────────────────────────────────────────────────
    origins = settings.CORS_ORIGINS
    if settings.DEBUG:
        origins.append("*")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global Exception Handlers ────────────────────────────────
    register_error_handlers(app)

    # ── Include Routers ──────────────────────────────────────────
    from api.routes.health import router as health_router
    from api.routes.sessions import router as sessions_router
    from api.routes.transcription import router as transcription_router
    from api.routes.translation import router as translation_router
    from api.routes.analysis import router as analysis_router

    app.include_router(health_router)
    app.include_router(sessions_router, prefix="/api/lecture")
    app.include_router(transcription_router, prefix="/api/lecture")
    app.include_router(translation_router, prefix="/api/lecture")
    app.include_router(analysis_router, prefix="/api/lecture")

    return app


# Module-level app instance (used by uvicorn `app.main:app`)
app = create_app()
