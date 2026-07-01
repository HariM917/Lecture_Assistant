from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
import logging
from typing import Optional

from app.core.database import get_db
from app.core.websocket_manager import manager
from app.schemas.schemas import LectureSessionCreate, LectureSessionResponse, HealthCheck
from app.repositories.session_repository import SessionRepository, TranscriptionRepository
from app.services.transcription import TranscriptionService
from app.services.translation import TranslationService
from app.services.summarization import SummarizationService
from app.services.nlp_extraction import NLPExtractionService
from app.services.cache import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lecture", tags=["lecture"])

# Initialize services
transcription_service = TranscriptionService()
translation_service = TranslationService()
summarization_service = SummarizationService()
nlp_service = NLPExtractionService()


# ==================== Session Management ====================

@router.post("/sessions", response_model=LectureSessionResponse)
async def create_session(session_data: LectureSessionCreate, db: Session = Depends(get_db)):
    """Create a new lecture session."""
    try:
        session = SessionRepository.create(db, session_data.title, session_data.subject, session_data.instructor)
        logger.info(f"Created session: {session.id}")
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=list[LectureSessionResponse])
async def list_sessions(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """List all lecture sessions."""
    sessions = SessionRepository.get_all(db, skip=skip, limit=limit)
    return sessions


@router.get("/sessions/{session_id}", response_model=LectureSessionResponse)
async def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """Get session details."""
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: UUID, db: Session = Depends(get_db)):
    """End a lecture session."""
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    SessionRepository.deactivate(db, session_id)
    redis_cache.clear_session_cache(str(session_id))
    
    return {"message": f"Session {session_id} ended", "status": "success"}


# ==================== Transcription ====================

@router.post("/sessions/{session_id}/transcribe")
async def transcribe_audio(session_id: UUID, file: UploadFile = File(...), language: Optional[str] = Query("en"),
                          db: Session = Depends(get_db)):
    """Transcribe audio file."""
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        audio_content = await file.read()
        result = transcription_service.transcribe_bytes(audio_content, language)
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        transcription = TranscriptionRepository.create(
            db, session_id=session_id, raw_text=result["text"],
            duration=result.get("duration"), confidence=result.get("confidence"),
            language=result.get("language", language)
        )
        
        redis_cache.set(f"session:{session_id}:last_transcription", result)
        
        await manager.broadcast_transcription(str(session_id), {
            "id": str(transcription.id), "text": result["text"], "confidence": result.get("confidence")
        })
        
        logger.info(f"Transcribed audio for session {session_id}")
        return transcription
    
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/transcriptions")
async def get_transcriptions(session_id: UUID, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Get all transcriptions for a session."""
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    transcriptions = TranscriptionRepository.get_by_session(db, session_id, limit)
    return [{"id": str(t.id), "text": t.raw_text, "timestamp": t.timestamp, "confidence": t.confidence}
            for t in transcriptions]


# ==================== Translation ====================

@router.post("/transcriptions/{transcription_id}/translate")
async def translate_transcription(transcription_id: UUID, target_language: str = Query(...), db: Session = Depends(get_db)):
    """Translate a transcription."""
    transcription = TranscriptionRepository.get_by_id(db, transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    try:
        result = translation_service.translate_text(transcription.raw_text, target_language, transcription.language)
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        await manager.broadcast_translation(str(transcription.session_id), {
            "language": target_language, "text": result["translated_text"]
        })
        
        logger.info(f"Translated to {target_language}")
        return {"status": "success", "translation": result["translated_text"], "target_language": target_language}
    
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Summarization ====================

@router.post("/sessions/{session_id}/summarize")
async def summarize_session(session_id: UUID, max_length: int = Query(150, ge=50),
                           min_length: int = Query(50, ge=10), db: Session = Depends(get_db)):
    """Summarize all transcriptions in a session."""
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        transcriptions = TranscriptionRepository.get_by_session(db, session_id)
        if not transcriptions:
            raise HTTPException(status_code=400, detail="No transcriptions found")
        
        combined_text = " ".join([t.raw_text for t in transcriptions])
        result = summarization_service.summarize(combined_text, max_length, min_length)
        
        if result["status"] != "success":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        await manager.broadcast_summary(str(session_id), {
            "text": result["summary"], "compression_ratio": result["compression_ratio"]
        })
        
        logger.info(f"Summarized session {session_id}")
        return {"status": "success", "summary": result["summary"]}
    
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== NLP Extraction ====================

@router.post("/transcriptions/{transcription_id}/extract")
async def extract_insights(transcription_id: UUID, db: Session = Depends(get_db)):
    """Extract keywords, formulas, and entities."""
    transcription = TranscriptionRepository.get_by_id(db, transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    try:
        result = nlp_service.comprehensive_extraction(transcription.raw_text)
        
        await manager.broadcast_insights(str(transcription.session_id), {
            "keywords": result.get("keywords", []),
            "formulas": result.get("formulas", {}),
            "entities": result.get("entities", {})
        })
        
        logger.info(f"Extracted insights from transcription {transcription_id}")
        return result
    
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket ====================

@router.websocket("/ws/{session_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, session_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received from {user_id}: {data}")
            
            await websocket.send_json({
                "type": "connection_confirmed",
                "user_id": user_id,
                "active_users": manager.get_active_users_count(session_id)
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id, user_id)
        logger.info(f"User {user_id} disconnected from {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id, user_id)
