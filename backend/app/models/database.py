"""
SQLAlchemy ORM models for the Lecture Assistant database.

All models use UUID primary keys and track creation/update timestamps.
Compatible with both SQLite and PostgreSQL backends.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.core.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _new_uuid():
    return str(uuid.uuid4())


class LectureSession(Base):
    """A lecture recording session."""
    __tablename__ = "lecture_sessions"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    title = Column(String(255), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    instructor = Column(String(150), nullable=False)
    status = Column(String(20), default="active")  # active, ended, archived
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Relationships
    transcriptions = relationship(
        "TranscriptionNote", back_populates="session",
        cascade="all, delete-orphan", order_by="TranscriptionNote.created_at",
    )
    summaries = relationship(
        "Summary", back_populates="session",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subject": self.subject,
            "instructor": self.instructor,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "transcription_count": len(self.transcriptions) if self.transcriptions else 0,
        }


class TranscriptionNote(Base):
    """A single transcription segment within a session."""
    __tablename__ = "transcription_notes"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    session_id = Column(String(36), ForeignKey("lecture_sessions.id"), nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    confidence = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # Relationships
    session = relationship("LectureSession", back_populates="transcriptions")
    translations = relationship(
        "Translation", back_populates="transcription",
        cascade="all, delete-orphan",
    )
    insights = relationship(
        "Insight", back_populates="transcription",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "text": self.raw_text,
            "language": self.language,
            "confidence": self.confidence,
            "duration": self.duration,
            "filename": self.filename,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Translation(Base):
    """A translation of a transcription into a target language."""
    __tablename__ = "translations"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    transcription_id = Column(String(36), ForeignKey("transcription_notes.id"), nullable=False, index=True)
    target_language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    # Relationships
    transcription = relationship("TranscriptionNote", back_populates="translations")

    def to_dict(self):
        return {
            "id": self.id,
            "transcription_id": self.transcription_id,
            "target_language": self.target_language,
            "translated_text": self.translated_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Summary(Base):
    """An AI-generated summary of a session's transcriptions."""
    __tablename__ = "summaries"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    session_id = Column(String(36), ForeignKey("lecture_sessions.id"), nullable=False, index=True)
    summary_text = Column(Text, nullable=False)
    original_length = Column(Integer, nullable=True)
    summary_length = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # Relationships
    session = relationship("LectureSession", back_populates="summaries")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "summary_text": self.summary_text,
            "original_length": self.original_length,
            "summary_length": self.summary_length,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Insight(Base):
    """Extracted keywords, formulas, and entities from a transcription."""
    __tablename__ = "insights"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    transcription_id = Column(String(36), ForeignKey("transcription_notes.id"), nullable=False, index=True)
    keywords = Column(JSON, nullable=True)
    formulas = Column(JSON, nullable=True)
    entities = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    # Relationships
    transcription = relationship("TranscriptionNote", back_populates="insights")

    def to_dict(self):
        return {
            "id": self.id,
            "transcription_id": self.transcription_id,
            "keywords": self.keywords or [],
            "formulas": self.formulas or [],
            "entities": self.entities or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class StudentNote(Base):
    """Personal notes taken by students during a session."""
    __tablename__ = "student_notes"

    id = Column(String(36), primary_key=True, default=_new_uuid)
    session_id = Column(String(36), ForeignKey("lecture_sessions.id"), nullable=False, index=True)
    student_id = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
