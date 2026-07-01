from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from models.database import LectureSession, TranscriptionNote
import logging

logger = logging.getLogger(__name__)


class SessionRepository:
    """Repository for lecture sessions."""
    
    @staticmethod
    def create(db: Session, title: str, subject: str, instructor: str) -> LectureSession:
        """Create a new lecture session."""
        session = LectureSession(title=title, subject=subject, instructor=instructor)
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created session: {session.id}")
        return session
    
    @staticmethod
    def get_by_id(db: Session, session_id: UUID) -> Optional[LectureSession]:
        """Get session by ID."""
        return db.query(LectureSession).filter(LectureSession.id == session_id).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[LectureSession]:
        """Get all sessions."""
        return db.query(LectureSession).order_by(desc(LectureSession.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def deactivate(db: Session, session_id: UUID) -> bool:
        """Mark session as inactive."""
        result = db.query(LectureSession).filter(LectureSession.id == session_id).update({"is_active": False})
        db.commit()
        return result > 0


class TranscriptionRepository:
    """Repository for transcription notes."""
    
    @staticmethod
    def create(db: Session, session_id: UUID, raw_text: str, duration: Optional[float] = None,
               confidence: Optional[float] = None, language: str = "en") -> TranscriptionNote:
        """Create a new transcription note."""
        note = TranscriptionNote(session_id=session_id, raw_text=raw_text, duration=duration,
                                confidence=confidence, language=language)
        db.add(note)
        db.commit()
        db.refresh(note)
        logger.info(f"Created transcription: {note.id}")
        return note
    
    @staticmethod
    def get_by_id(db: Session, note_id: UUID) -> Optional[TranscriptionNote]:
        """Get transcription by ID."""
        return db.query(TranscriptionNote).filter(TranscriptionNote.id == note_id).first()
    
    @staticmethod
    def get_by_session(db: Session, session_id: UUID, limit: int = 100) -> List[TranscriptionNote]:
        """Get all transcriptions for a session."""
        return db.query(TranscriptionNote).filter(TranscriptionNote.session_id == session_id)\
            .order_by(desc(TranscriptionNote.timestamp)).limit(limit).all()
