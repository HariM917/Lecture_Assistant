from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import datetime
import uuid
from core.database import Base


class LectureSession(Base):
    """Represents a lecture session."""
    __tablename__ = "lecture_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    instructor = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    duration_minutes = Column(Integer, nullable=True)


class TranscriptionNote(Base):
    """Stores raw transcriptions."""
    __tablename__ = "transcription_notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    raw_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    language = Column(String(10), default="en")


class Translation(Base):
    """Stores translations in multiple languages."""
    __tablename__ = "translations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcription_id = Column(UUID(as_uuid=True), nullable=False)
    target_language = Column(String(10), nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Summary(Base):
    """Stores abstractive summaries."""
    __tablename__ = "summaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    summary_text = Column(Text, nullable=False)
    original_length = Column(Integer, nullable=True)
    summary_length = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Insight(Base):
    """Stores extracted keywords and formulas."""
    __tablename__ = "insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    transcription_id = Column(UUID(as_uuid=True), nullable=False)
    keywords = Column(JSON, nullable=True)
    formulas = Column(JSON, nullable=True)
    entities = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentNote(Base):
    """Personal notes taken by students."""
    __tablename__ = "student_notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    student_id = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
