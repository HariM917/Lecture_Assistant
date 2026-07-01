"""Analysis routes — keyword extraction, summarization."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.dependencies import get_nlp_service, get_summarization_service
from app.models.database import (
    LectureSession, TranscriptionNote, Insight, Summary,
)

router = APIRouter(tags=["Analysis"])
logger = logging.getLogger(__name__)


@router.post("/transcriptions/{transcription_id}/extract", summary="Extract Keywords & Entities")
async def extract_keywords(
    transcription_id: str,
    db: Session = Depends(get_db),
    nlp_svc=Depends(get_nlp_service),
):
    """Extract keywords, formulas, and entities from a transcription."""
    note = db.query(TranscriptionNote).filter(TranscriptionNote.id == transcription_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Transcription not found")

    result = nlp_svc.comprehensive_extraction(note.raw_text)

    # Persist
    insight = Insight(
        transcription_id=transcription_id,
        keywords=result.get("keywords", []),
        formulas=result.get("formulas", []),
        entities=result.get("entities", {}),
    )
    db.add(insight)
    db.commit()

    logger.info(
        f"Extracted {result.get('keyword_count', 0)} keywords, "
        f"{result.get('formula_count', 0)} formulas from {transcription_id}"
    )

    return {
        "status": "success",
        "keywords": result.get("keywords", []),
        "formulas": result.get("formulas", []),
        "entities": result.get("entities", {}),
        "keyword_count": result.get("keyword_count", 0),
        "formula_count": result.get("formula_count", 0),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/sessions/{session_id}/summarize", summary="Summarize Session")
async def summarize_session(
    session_id: str,
    db: Session = Depends(get_db),
    summarization_svc=Depends(get_summarization_service),
):
    """Generate a summary from all transcriptions in a session."""
    session = db.query(LectureSession).filter(LectureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Gather all transcription texts
    notes = (
        db.query(TranscriptionNote)
        .filter(TranscriptionNote.session_id == session_id)
        .order_by(TranscriptionNote.created_at.asc())
        .all()
    )

    if not notes:
        return {
            "status": "success",
            "summary": "No transcriptions found in this session.",
            "session_title": session.title,
            "transcription_count": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    combined_text = " ".join(n.raw_text for n in notes)
    result = summarization_svc.summarize(combined_text)

    summary_text = result.get("summary", combined_text[:500])

    # Add session context header
    full_summary = (
        f"LECTURE SUMMARY: {session.title}\n"
        f"Instructor: {session.instructor} | Subject: {session.subject}\n"
        f"Transcriptions: {len(notes)}\n\n"
        f"{summary_text}"
    )

    # Persist
    summary_record = Summary(
        session_id=session_id,
        summary_text=full_summary,
        original_length=len(combined_text),
        summary_length=len(full_summary),
    )
    db.add(summary_record)
    db.commit()

    logger.info(f"Summary generated for session {session_id}")

    return {
        "status": "success",
        "summary": full_summary,
        "session_title": session.title,
        "transcription_count": len(notes),
        "method": result.get("method", "unknown"),
        "original_length": len(combined_text),
        "summary_length": len(full_summary),
        "compression_ratio": result.get("compression_ratio"),
        "timestamp": datetime.utcnow().isoformat(),
    }
