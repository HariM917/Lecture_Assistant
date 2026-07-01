from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class LectureSessionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=100)
    instructor: str = Field(..., min_length=1, max_length=150)


class LectureSessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    subject: str
    instructor: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class TranscriptionResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    raw_text: str
    timestamp: datetime
    language: str
    confidence: Optional[float] = None
    
    class Config:
        from_attributes = True


class TranslationResponse(BaseModel):
    id: uuid.UUID
    transcription_id: uuid.UUID
    target_language: str
    translated_text: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SummaryResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    summary_text: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InsightResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    keywords: Optional[List[str]] = []
    formulas: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProcessingResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheck(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
