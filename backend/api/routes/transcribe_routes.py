"""
📡 Whisper Transcriber Routes - API Integration Layer

Routes for accessing professional transcription:
- /api/transcribe/single - Transcribe single file
- /api/transcribe/batch - Transcribe directory
- /api/transcribe/upload - Upload and transcribe
- /api/transcribe/info - Service information
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import tempfile
import shutil
from pathlib import Path

from app.services.whisper_transcriber import get_transcriber

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transcribe", tags=["whisper-transcriber"])


# ==================== Request Models ====================

class TranscribeFileRequest(BaseModel):
    """File transcription request."""
    file_path: str = Field(..., description="Path to audio file")
    model: str = Field("base", description="Model size: tiny, base, small, medium, large")
    speed: str = Field("fast", description="Speed mode: fast, balanced, slow")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/audio.mp4",
                "model": "base",
                "speed": "fast"
            }
        }


class TranscribeBatchRequest(BaseModel):
    """Batch transcription request."""
    directory: str = Field(..., description="Directory containing audio files")
    model: str = Field("base", description="Model size: tiny, base, small, medium, large")
    speed: str = Field("fast", description="Speed mode: fast, balanced, slow")
    
    class Config:
        json_schema_extra = {
            "example": {
                "directory": "/path/to/audio/files",
                "model": "base",
                "speed": "fast"
            }
        }


# ==================== Response Models ====================

class TranscriptionResult(BaseModel):
    """Single transcription result."""
    file: str
    filename: str
    timestamp: str
    model: str
    speed_mode: str
    original_audio_language: str
    detected_text_language: str
    output_language: str
    text: str
    duration: Any
    segments_count: int = 0


class BatchTranscriptionResponse(BaseModel):
    """Batch transcription response."""
    status: str
    total_files: int
    successful: int
    failed: int
    results: List[TranscriptionResult]


# ==================== Endpoints ====================

@router.post("/single", response_model=TranscriptionResult)
async def transcribe_file(request: TranscribeFileRequest) -> TranscriptionResult:
    """
    Transcribe a single audio/video file to its detected native language.
    
    Supports: MP3, MP4, MPEG, M4A, WAV, WebM
    
    - **file_path**: Full path to audio file
    - **model**: Model size (base=default, large=most accurate)
    - **speed**: fast=~30-60s, balanced=~1-3m, slow=most accurate
    
    Returns transcription with both Whisper and langdetect language detection.
    """
    try:
        # Validate model and speed
        if request.model not in ['tiny', 'base', 'small', 'medium', 'large']:
            raise ValueError("Invalid model")
        if request.speed not in ['fast', 'balanced', 'slow']:
            raise ValueError("Invalid speed mode")
        
        transcriber = get_transcriber(request.model, request.speed)
        result = transcriber.transcribe_single(request.file_path)
        
        if not result:
            raise HTTPException(status_code=400, detail="Transcription failed")
        
        return TranscriptionResult(
            file=result['file'],
            filename=result['filename'],
            timestamp=result['timestamp'],
            model=result['model'],
            speed_mode=result['speed_mode'],
            original_audio_language=result['original_audio_language'],
            detected_text_language=result['detected_text_language'],
            output_language=result['output_language'],
            text=result['text'],
            duration=result['duration'],
            segments_count=len(result.get('segments', []))
        )
    except Exception as e:
        logger.error(f"Transcribe single error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchTranscriptionResponse)
async def transcribe_batch(request: TranscribeBatchRequest) -> BatchTranscriptionResponse:
    """
    Batch transcribe all audio files in a directory to their detected languages.
    
    - **directory**: Path to directory containing audio files
    - **model**: Model size (base=default, large=most accurate)
    - **speed**: fast, balanced, or slow
    
    Returns results for all successfully transcribed files.
    """
    try:
        if request.model not in ['tiny', 'base', 'small', 'medium', 'large']:
            raise ValueError("Invalid model")
        if request.speed not in ['fast', 'balanced', 'slow']:
            raise ValueError("Invalid speed mode")
        
        transcriber = get_transcriber(request.model, request.speed)
        results = transcriber.transcribe_batch(request.directory)
        
        successful = len(results)
        # Try to count total files
        total_files = len(results)  # Conservative count
        
        return BatchTranscriptionResponse(
            status="success" if successful > 0 else "no_files",
            total_files=total_files,
            successful=successful,
            failed=total_files - successful,
            results=[
                TranscriptionResult(
                    file=r['file'],
                    filename=r['filename'],
                    timestamp=r['timestamp'],
                    model=r['model'],
                    speed_mode=r['speed_mode'],
                    original_audio_language=r['original_audio_language'],
                    detected_text_language=r['detected_text_language'],
                    output_language=r['output_language'],
                    text=r['text'],
                    duration=r['duration'],
                    segments_count=len(r.get('segments', []))
                )
                for r in results
            ]
        )
    except Exception as e:
        logger.error(f"Batch transcribe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def transcribe_upload(
    file: UploadFile = File(...),
    model: str = Query("base", description="Model: tiny, base, small, medium, large"),
    speed: str = Query("fast", description="Speed: fast, balanced, slow")
):
    """
    Upload and transcribe an audio/video file.
    
    - **file**: Audio/video file to upload
    - **model**: Model size
    - **speed**: Speed mode
    
    Returns transcription result.
    """
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = Path(temp_dir) / file.filename
    
    try:
        # Save uploaded file
        with open(temp_path, 'wb') as f:
            contents = await file.read()
            f.write(contents)
        
        # Transcribe
        transcriber = get_transcriber(model, speed)
        result = transcriber.transcribe_single(str(temp_path))
        
        if not result:
            raise HTTPException(status_code=400, detail="Transcription failed")
        
        return {
            "status": "success",
            "filename": result['filename'],
            "audio_language": result['original_audio_language'],
            "text_language": result['detected_text_language'],
            "text": result['text'],
            "duration": result['duration']
        }
    
    except Exception as e:
        logger.error(f"Upload transcribe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp file
        try:
            if temp_path.exists():
                temp_path.unlink()
        except:
            pass


@router.get("/info")
async def service_info() -> Dict[str, Any]:
    """Get transcriber service information and capabilities."""
    try:
        transcriber = get_transcriber()
        return transcriber.get_service_info()
    except Exception as e:
        logger.error(f"Info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "whisper_transcriber"
    }


@router.get("/models")
async def list_models() -> Dict[str, List[str]]:
    """List available models."""
    return {
        "models": ['tiny', 'base', 'small', 'medium', 'large'],
        "recommended": "base",
        "speeds": ['fast', 'balanced', 'slow'],
        "formats": ['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm']
    }
