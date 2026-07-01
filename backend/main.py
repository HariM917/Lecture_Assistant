"""
Backend Entry Point for FastAPI Server
Initializes and runs the Multilingual Lecture Assistant
"""
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the FastAPI app from app module
from app.main import create_app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🚀 Starting Multilingual Lecture Assistant Backend")
    logger.info("=" * 70)
    logger.info("📡 Server running on: http://0.0.0.0:5000")
    logger.info("📚 API Docs: http://localhost:5000/api/docs")
    logger.info("🔍 ReDoc: http://localhost:5000/api/redoc")
    logger.info("=" * 70)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=5000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("| Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        raise