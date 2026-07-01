"""Transcription routes — upload audio and transcribe."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.dependencies import get_transcription_service
from app.models.database import LectureSession, TranscriptionNote

router = APIRouter(tags=["Transcription"])
logger = logging.getLogger(__name__)


@router.post("/sessions/{session_id}/transcribe", summary="Transcribe Audio")
async def transcribe_audio(
    session_id: str,
    file: UploadFile = File(...),
    language: str = Form("en"),
    db: Session = Depends(get_db),
    transcription_svc=Depends(get_transcription_service),
):
    """Upload an audio file and transcribe it to text."""
    # Verify session exists
    session = db.query(LectureSession).filter(LectureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Read uploaded file
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # Transcribe
    result = transcription_svc.transcribe_audio(
        audio_bytes=content,
        language=language,
        filename=file.filename or "audio.webm",
    )

    if result.get("status") != "success":
        raise HTTPException(status_code=500, detail="Transcription failed")

    # Persist to database
    note = TranscriptionNote(
        session_id=session_id,
        raw_text=result["text"],
        language=result.get("language", language),
        confidence=result.get("confidence"),
        duration=result.get("duration"),
        filename=file.filename,
        file_size=len(content),
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    logger.info(f"Transcription saved: {note.id} ({len(content)} bytes)")

    return {
        "status": "success",
        "id": note.id,
        "session_id": session_id,
        "text": note.raw_text,
        "language": note.language,
        "confidence": note.confidence,
        "duration": note.duration,
        "filename": note.filename,
        "file_size": note.file_size,
        "created_at": note.created_at.isoformat() if note.created_at else None,
    }


@router.get("/sessions/{session_id}/transcriptions", summary="List Transcriptions")
async def list_transcriptions(session_id: str, db: Session = Depends(get_db)):
    """Get all transcriptions for a session."""
    session = db.query(LectureSession).filter(LectureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    notes = (
        db.query(TranscriptionNote)
        .filter(TranscriptionNote.session_id == session_id)
        .order_by(TranscriptionNote.created_at.asc())
        .all()
    )
    return {
        "status": "success",
        "transcriptions": [n.to_dict() for n in notes],
        "total": len(notes),
    }
