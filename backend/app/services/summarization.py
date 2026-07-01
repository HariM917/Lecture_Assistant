"""
Summarization service with transformers integration and extractive fallback.
"""

import logging
import re
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SummarizationService:
    """Extractive summarization (no ML dependencies required)."""

    def __init__(self):
        logger.info("SummarizationService initialized (extractive mode)")

    def summarize(self, text: str, max_sentences: int = 8) -> Dict[str, Any]:
        """Create an extractive summary by scoring sentences."""
        if not text or len(text.strip()) < 50:
            return {
                "status": "error",
                "message": "Text too short for summarization",
                "summary": text or "",
            }

        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        if len(sentences) <= max_sentences:
            return {
                "status": "success",
                "summary": text.strip(),
                "method": "extractive",
                "original_length": len(text),
                "summary_length": len(text),
            }

        # Score sentences by word frequency (simple TF-based)
        word_freq: Dict[str, int] = {}
        for sentence in sentences:
            for word in sentence.lower().split():
                word = re.sub(r'[^\w]', '', word)
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1

        scored = []
        for i, sentence in enumerate(sentences):
            score = sum(word_freq.get(re.sub(r'[^\w]', '', w.lower()), 0)
                        for w in sentence.split())
            # Boost first and last sentences (usually most important)
            if i == 0:
                score *= 1.5
            elif i == len(sentences) - 1:
                score *= 1.2
            scored.append((i, sentence, score))

        # Pick top sentences, maintain original order
        top = sorted(scored, key=lambda x: x[2], reverse=True)[:max_sentences]
        top = sorted(top, key=lambda x: x[0])  # restore order

        summary = " ".join(s[1] for s in top)

        return {
            "status": "success",
            "summary": summary,
            "method": "extractive",
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": round((1 - len(summary) / len(text)) * 100, 1),
        }

    def batch_summarize(self, texts: List[str]) -> Dict[str, Any]:
        """Summarize multiple texts."""
        results = [self.summarize(t) for t in texts]
        successful = [r for r in results if r["status"] == "success"]
        return {"status": "success", "summaries": successful, "count": len(successful)}


class RealSummarizationService(SummarizationService):
    """Abstractive summarization using HuggingFace transformers."""

    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        super().__init__()
        try:
            from transformers import pipeline
            self._summarizer = pipeline("summarization", model=model_name)
            logger.info(f"SummarizationService initialized (transformers: {model_name})")
        except Exception as e:
            logger.warning(f"Failed to load summarization model: {e}")
            self._summarizer = None

    def summarize(self, text: str, max_sentences: int = 8) -> Dict[str, Any]:
        """Abstractive summary using BART, with extractive fallback."""
        if not self._summarizer or not text or len(text.strip()) < 50:
            return super().summarize(text, max_sentences)

        try:
            max_len = min(150, len(text.split()) // 2)
            min_len = max(30, max_len // 3)

            result = self._summarizer(
                text,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
            )
            summary = result[0]["summary_text"]

            return {
                "status": "success",
                "summary": summary,
                "method": "abstractive",
                "model": "facebook/bart-large-cnn",
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": round((1 - len(summary) / len(text)) * 100, 1),
            }
        except Exception as e:
            logger.error(f"Abstractive summarization failed: {e}")
            return super().summarize(text, max_sentences)
