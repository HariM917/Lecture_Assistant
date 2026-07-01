import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SummarizationService:
    """Handles text summarization (mock mode for testing)."""
    
    def __init__(self):
        """Initialize."""
        logger.info("Initialized SummarizationService")
    
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> Dict[str, Any]:
        """Summarize text (mock)."""
        if not text or len(text.strip()) < 50:
            return {
                "status": "error",
                "message": "Text too short for summarization",
                "summary": None
            }
        
        # Mock summary
        summary = f"Summary: {text[:100]}..."
        
        return {
            "status": "success",
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": 75.0
        }
    
    def batch_summarize(self, texts: List[str], max_length: int = 150, min_length: int = 50) -> Dict[str, Any]:
        """Summarize multiple texts (mock)."""
        summaries = []
        for text in texts:
            result = self.summarize(text, max_length, min_length)
            if result["status"] == "success":
                summaries.append(result)
        
        return {
            "status": "success",
            "summaries": summaries,
            "count": len(summaries)
        }
    
    def extractive_summary(self, text: str, num_sentences: int = 5) -> Dict[str, Any]:
        """Create extractive summary (mock)."""
        return {
            "status": "success",
            "summary": text,
            "method": "extractive",
            "sentences_extracted": 2
        }
