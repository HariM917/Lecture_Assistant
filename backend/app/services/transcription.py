import logging
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


class TranscriptionService:
    """Handles speech-to-text using OpenAI Whisper."""
    
    def __init__(self):
        """Initialize (simplified for Docker testing)."""
        logger.info("Initialized TranscriptionService (mock mode)")
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio file to text (mock)."""
        return {
            "status": "success",
            "text": "Sample transcription - Neural networks and deep learning fundamentals",
            "language": language or "en",
            "duration": 120.5,
            "confidence": 0.95
        }
    
    def transcribe_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio bytes (mock)."""
        return self.transcribe_audio("", language)
