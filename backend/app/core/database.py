"""
Database engine and session management.

Supports SQLite (development) and PostgreSQL (production) with
automatic detection from DATABASE_URL.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def _build_engine():
    """Build the SQLAlchemy engine with driver-appropriate options."""
    url = settings.DATABASE_URL

    if settings.is_sqlite:
        # Ensure the data directory exists
        db_path = url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        engine = create_engine(
            url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
        )

        # Enable WAL mode and foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

        logger.info(f"Database: SQLite at {db_path}")
    else:
        engine = create_engine(
            url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        logger.info("Database: PostgreSQL")

    return engine


engine = _build_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Safe to call multiple times."""
    from app.models.database import (  # noqa: F401 – force model registration
        LectureSession,
        TranscriptionNote,
        Translation,
        Summary,
        Insight,
        StudentNote,
    )
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")
