"""
Transcription service with Whisper integration and mock fallback.
"""

import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class MockTranscriptionService:
    """Mock transcription service for development/demo without ML dependencies."""

    DEMO_TRANSCRIPTS = {
        "en": (
            "This is a demonstration lecture about machine learning and artificial intelligence. "
            "We will cover fundamental concepts including neural networks, deep learning, and various applications. "
            "Machine learning has become essential in modern technology, powering recommendation systems, "
            "image recognition, and natural language processing among many other applications. "
            "Today we'll explore supervised learning, where models learn from labeled data, "
            "and unsupervised learning, where patterns are discovered in unlabeled datasets."
        ),
        "ta": "இது இயந்திர கற்றல் மற்றும் செயற்கை நுண்ணறிவு பற்றிய ஒரு விளக்கக் சொற்பொழிப்பு ஆகும்.",
        "hi": "यह मशीन लर्निंग और कृत्रिम बुद्धिमत्ता के बारे में एक प्रदर्शन व्याख्यान है।",
    }

    def transcribe_audio(self, audio_bytes: bytes, language: str = "en",
                         filename: str = "audio.webm") -> Dict:
        """Return a realistic mock transcription result."""
        text = self.DEMO_TRANSCRIPTS.get(language, self.DEMO_TRANSCRIPTS["en"])
        logger.info(f"[MOCK] Transcribed {len(audio_bytes)} bytes ({language})")
        return {
            "status": "success",
            "text": text,
            "language": language,
            "confidence": 0.94,
            "duration": round(len(audio_bytes) / 32000, 1),  # rough estimate
            "model": "mock",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_service_info(self) -> Dict:
        return {
            "service": "transcription",
            "mode": "mock",
            "status": "operational",
        }
