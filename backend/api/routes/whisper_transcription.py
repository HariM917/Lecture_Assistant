"""
🎤 Whisper Transcription API Routes

Endpoints for:
- Single file transcription with auto-detect
- Batch processing
- Dataset transcription
- Model fine-tuning
- Service information
"""

import logging
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional, List
import numpy as np
from datetime import datetime
from pathlib import Path

from app.services.whisper_service import WhisperTranscriberService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/lecture/whisper",
    tags=["Whisper Transcription"],
    responses={404: {"description": "Not found"}}
)

# Global service instance
_whisper_service: Optional[WhisperTranscriberService] = None

def get_whisper_service():
    """Get or initialize the Whisper service."""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperTranscriberService(
            model_name="base",
            use_fp16=True,
            high_accuracy=True,
            speed_mode="fast"
        )
    return _whisper_service


# ===== SERVICE INFO ENDPOINTS =====

@router.get("/info")
async def get_service_info():
    """Get Whisper service information and capabilities."""
    try:
        service = get_whisper_service()
        info = service.get_service_info()
        logger.info("Retrieved service info")
        return {
            "status": "success",
            "data": info
        }
    except Exception as e:
        logger.error(f"Error getting service info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """Get list of available Whisper models."""
    try:
        service = get_whisper_service()
        return {
            "status": "success",
            "available_models": service.AVAILABLE_MODELS,
            "current_model": service.model_name,
            "model_descriptions": {
                "tiny": "Fastest, lowest accuracy (~39M params)",
                "base": "Good balance, recommended (~74M params)",
                "small": "Better accuracy (~244M params)",
                "medium": "High accuracy (~769M params)",
                "large": "Highest accuracy (~1.5B params)"
            }
        }
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for native script output."""
    try:
        service = get_whisper_service()
        return {
            "status": "success",
            "supported_languages": list(service.NATIVE_PROMPTS.keys()),
            "language_names": {
                "hi": "Hindi",
                "ta": "Tamil",
                "te": "Telugu",
                "kn": "Kannada",
                "ml": "Malayalam",
                "mr": "Marathi",
                "ar": "Arabic",
                "ur": "Urdu"
            },
            "note": "Whisper will auto-detect and output in native scripts"
        }
    except Exception as e:
        logger.error(f"Error getting languages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Check Whisper service health."""
    try:
        service = get_whisper_service()
        return {
            "status": "healthy",
            "service": "whisper_transcription",
            "model": service.model_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# ===== TRANSCRIPTION ENDPOINTS =====

@router.post("/transcribe")
async def transcribe_file(
    file_path: str = Query(..., description="Path to audio/video file"),
):
    """Transcribe a single audio/video file to its detected native language."""
    try:
        logger.info(f"Transcribing: {file_path}")
        service = get_whisper_service()
        
        result = service.transcribe_single(audio_path=file_path)
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to transcribe file")
        
        logger.info(f"✅ Transcription successful: {result['original_audio_language']}")
        
        return {
            "status": "success",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-transcribe")
async def batch_transcribe(
    directory: str = Query(..., description="Directory containing audio files"),
):
    """Batch transcribe all audio files in a directory."""
    try:
        logger.info(f"Batch transcribing: {directory}")
        service = get_whisper_service()
        
        results = service.transcribe_batch(directory)
        
        if not results:
            raise HTTPException(status_code=400, detail="No files transcribed")
        
        logger.info(f"✅ Batch transcription completed: {len(results)} files")
        
        return {
            "status": "success",
            "count": len(results),
            "data": results
        }
    
    except Exception as e:
        logger.error(f"Batch transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dataset-transcribe")
async def transcribe_from_dataset(
    dataset_name: str = Query(..., description="Hugging Face dataset name (e.g. mozilla-foundation/common_voice_11_0)"),
    split: str = Query("train", description="Dataset split to transcribe"),
    limit: int = Query(5, ge=1, le=1000, description="Max samples to transcribe"),
):
    """Transcribe audio from a Hugging Face dataset."""
    try:
        logger.info(f"Transcribing from dataset: {dataset_name} ({split} split, limit={limit})")
        service = get_whisper_service()
        
        results = service.transcribe_dataset(
            dataset_name=dataset_name,
            split=split,
            limit=limit
        )
        
        if not results:
            raise HTTPException(status_code=400, detail="No samples transcribed from dataset")
        
        logger.info(f"✅ Dataset transcription completed: {len(results)} samples")
        
        return {
            "status": "success",
            "count": len(results),
            "dataset": dataset_name,
            "split": split,
            "data": results
        }
    
    except Exception as e:
        logger.error(f"Dataset transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== TRAINING ENDPOINTS =====

@router.post("/train")
async def train_model(
    dataset_name: str = Query(..., description="Hugging Face dataset name"),
    text_column: str = Query("sentence", description="Column name containing text"),
    epochs: int = Query(1, ge=1, le=10, description="Number of training epochs"),
    limit: int = Query(100, ge=10, le=5000, description="Max samples to train on"),
    background_tasks: BackgroundTasks = None,
):
    """
    Fine-tune Whisper model on a Hugging Face dataset.
    Training runs in background.
    """
    try:
        logger.info(f"Starting Whisper training: {dataset_name} (epochs={epochs}, limit={limit})")
        service = get_whisper_service()
        
        job_id = f"whisper_train_{dataset_name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Run training in background
        if background_tasks:
            background_tasks.add_task(
                service.train_on_dataset,
                dataset_name=dataset_name,
                text_column=text_column,
                epochs=epochs,
                limit=limit
            )
        else:
            # Fallback: run synchronously
            success = service.train_on_dataset(
                dataset_name=dataset_name,
                text_column=text_column,
                epochs=epochs,
                limit=limit
            )
            if not success:
                raise HTTPException(status_code=500, detail="Training failed")
        
        logger.info(f"✅ Training job queued: {job_id}")
        
        return {
            "status": "success",
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "dataset": dataset_name,
            "text_column": text_column,
            "epochs": epochs,
            "limit": limit,
            "message": "Training started. Monitor progress via logs."
        }
    
    except Exception as e:
        logger.error(f"Training initialization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== CONFIGURATION ENDPOINTS =====

@router.get("/config")
async def get_config():
    """Get current Whisper configuration."""
    try:
        service = get_whisper_service()
        return {
            "status": "success",
            "config": {
                "model": service.model_name,
                "speed_mode": service.speed_mode,
                "use_fp16": service.use_fp16,
                "high_accuracy": service.high_accuracy,
                "supported_formats": list(service.SUPPORTED_FORMATS),
                "max_audio_duration_hours": 8,
                "native_prompts_languages": list(service.NATIVE_PROMPTS.keys())
            }
        }
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/speed-mode")
async def set_speed_mode(
    speed_mode: str = Query(..., regex="^(fast|balanced|slow)$", description="Speed mode"),
):
    """Change transcription speed mode."""
    try:
        logger.info(f"Changing speed mode to: {speed_mode}")
        service = get_whisper_service()
        
        if speed_mode not in ["fast", "balanced", "slow"]:
            raise HTTPException(status_code=400, detail="Invalid speed mode")
        
        service.speed_mode = speed_mode
        
        return {
            "status": "success",
            "speed_mode": speed_mode,
            "message": "Speed mode updated successfully"
        }
    
    except Exception as e:
        logger.error(f"Error setting speed mode: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== STATISTICS ENDPOINTS =====

@router.get("/stats")
async def get_statistics():
    """Get Whisper service statistics."""
    try:
        service = get_whisper_service()
        return {
            "status": "success",
            "statistics": {
                "service_name": "Whisper Transcription",
                "model": service.model_name,
                "speed_mode": service.speed_mode,
                "uptime": "Running",
                "supported_formats": len(service.SUPPORTED_FORMATS),
                "supported_languages": len(service.NATIVE_PROMPTS),
                "max_audio_duration_hours": 8,
                "features": {
                    "auto_language_detection": True,
                    "native_script_output": True,
                    "batch_processing": True,
                    "dataset_fine_tuning": True
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
