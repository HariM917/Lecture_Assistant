"""
Backend entry point for the Multilingual Lecture Assistant.

Usage:
    python main.py              # Start with defaults (port 5000)
    MOCK_MODE=True python main.py   # Force mock services
"""

import uvicorn
import logging
import sys

# Configure logging before anything else
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("lecture-assistant")

# Import the FastAPI app (this triggers create_app → lifespan)
from app.main import app  # noqa: E402, F401
from app.core.config import get_settings  # noqa: E402

settings = get_settings()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🎓 Multilingual Lecture Assistant")
    logger.info(f"   Version     : {settings.APP_VERSION}")
    logger.info(f"   Environment : {settings.APP_ENVIRONMENT}")
    logger.info(f"   Server      : http://localhost:{settings.PORT}")
    logger.info(f"   API Docs    : http://localhost:{settings.PORT}/api/docs")
    logger.info(f"   Database    : {'SQLite' if settings.is_sqlite else 'PostgreSQL'}")
    logger.info("=" * 60)

    try:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)