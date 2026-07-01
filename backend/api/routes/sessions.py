"""Session management routes — create, list, get, end sessions."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.core.database import get_db
from app.models.database import LectureSession

router = APIRouter(tags=["Sessions"])
logger = logging.getLogger(__name__)


# ── Request / Response Models ────────────────────────────────────────────────

class SessionCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Lecture title")
    subject: str = Field(..., min_length=1, max_length=100, description="Subject area")
    instructor: str = Field(..., min_length=1, max_length=150, description="Instructor name")


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/sessions", summary="Create Session")
async def create_session(body: SessionCreateRequest, db: Session = Depends(get_db)):
    """Create a new lecture session."""
    session = LectureSession(
        title=body.title,
        subject=body.subject,
        instructor=body.instructor,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info(f"Session created: {session.id} — {body.title}")
    return {"status": "success", "session": session.to_dict()}


@router.get("/sessions", summary="List Sessions")
async def list_sessions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all lecture sessions, most recent first."""
    sessions = (
        db.query(LectureSession)
        .order_by(LectureSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "status": "success",
        "total": len(sessions),
        "sessions": [s.to_dict() for s in sessions],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/sessions/{session_id}", summary="Get Session")
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a specific session by ID."""
    session = db.query(LectureSession).filter(LectureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return {"status": "success", "session": session.to_dict()}


@router.post("/sessions/{session_id}/end", summary="End Session")
async def end_session(session_id: str, db: Session = Depends(get_db)):
    """End an active lecture session."""
    session = db.query(LectureSession).filter(LectureSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    now = datetime.now(timezone.utc)
    session.status = "ended"
    session.ended_at = now
    if session.created_at:
        session.duration_seconds = int((now - session.created_at).total_seconds())

    db.commit()
    db.refresh(session)
    logger.info(f"Session ended: {session_id}")
    return {"status": "success", "message": "Session ended", "session": session.to_dict()}
