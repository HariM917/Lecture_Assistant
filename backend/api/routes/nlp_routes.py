"""
📡 Enhanced NLP Routes - Integration Layer

Routes for accessing advanced NLP processing:
- /api/nlp/summarize - Extractive summarization
- /api/nlp/extract-keywords - Semantic keyword extraction  
- /api/nlp/detect-formulas - Mathematical formula detection
- /api/nlp/process - Complete pipeline
- /api/nlp/info - Service information
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.services.enhanced_nlp import get_nlp_processor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nlp", tags=["enhanced-nlp"])


# ==================== Request Models ====================

class SummarizeRequest(BaseModel):
    """Summarization request."""
    text: str = Field(..., min_length=50, description="Input lecture text (min 50 chars)")
    compression_ratio: float = Field(0.4, ge=0.2, le=0.7, description="Target compression ratio")
    language: Optional[str] = Field(None, description="Language code (auto-detect if null)")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "This lecture covers fundamental concepts of machine learning...",
                "compression_ratio": 0.4,
                "language": "en"
            }
        }


class KeywordRequest(BaseModel):
    """Keyword extraction request."""
    text: str = Field(..., min_length=50, description="Input text")
    num_keywords: int = Field(10, ge=3, le=30, description="Number of keywords")
    min_word_length: int = Field(4, ge=3, le=8, description="Minimum word length")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "...",
                "num_keywords": 10,
                "min_word_length": 4
            }
        }


class FormulaRequest(BaseModel):
    """Formula detection request."""
    text: str = Field(..., min_length=10, description="Input text containing formulas")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The distance formula is d = √((x₂-x₁)² + (y₂-y₁)²)"
            }
        }


class ProcessRequest(BaseModel):
    """Complete NLP processing request."""
    text: str = Field(..., min_length=50, description="Input lecture text")
    compression_ratio: float = Field(0.4, ge=0.2, le=0.7, description="Summarization compression ratio")
    num_keywords: int = Field(10, ge=3, le=30, description="Number of keywords")
    include_formulas: bool = Field(True, description="Detect formulas")
    language: Optional[str] = Field(None, description="Language code")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "...",
                "compression_ratio": 0.4,
                "num_keywords": 10,
                "include_formulas": True,
                "language": "en"
            }
        }


# ==================== Response Models ====================

class ProcessResponse(BaseModel):
    """Complete processing response."""
    status: str
    summary: str
    keywords: List[str]
    formulas: List[str]
    stats: Dict[str, Any]


# ==================== Endpoints ====================

@router.post("/summarize", response_model=ProcessResponse)
async def summarize_text(request: SummarizeRequest) -> ProcessResponse:
    """
    Generate extractive summary of lecture text.
    
    - **text**: Input lecture text (min 50 characters)
    - **compression_ratio**: Fraction of sentences to keep (0.2-0.7)
    - **language**: Language code or auto-detect
    
    Returns summary and compression statistics.
    """
    try:
        processor = get_nlp_processor()
        result = processor.process(
            request.text,
            compression_ratio=request.compression_ratio,
            num_keywords=0,
            include_formulas=False,
            language=request.language
        )
        return ProcessResponse(**result)
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-keywords")
async def extract_keywords(request: KeywordRequest) -> Dict[str, Any]:
    """
    Extract semantically important keywords.
    
    - **text**: Input text
    - **num_keywords**: Number of keywords (3-30)
    - **min_word_length**: Minimum word length (3-8)
    
    Returns ranked list of keywords with importance scores.
    """
    try:
        processor = get_nlp_processor()
        keywords = processor.keyword_extractor.extract(
            request.text,
            min_length=request.min_word_length,
            top_n=request.num_keywords
        )
        return {
            "status": "success",
            "keywords": keywords,
            "count": len(keywords)
        }
    except Exception as e:
        logger.error(f"Keyword extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-formulas")
async def detect_formulas(request: FormulaRequest) -> Dict[str, Any]:
    """
    Detect mathematical formulas in text.
    
    - **text**: Input text containing formulas
    
    Returns detected formulas with positions.
    """
    try:
        processor = get_nlp_processor()
        formulas = processor.formula_detector.detect(request.text)
        return {
            "status": "success",
            "formulas": formulas,
            "count": len(formulas)
        }
    except Exception as e:
        logger.error(f"Formula detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process", response_model=ProcessResponse)
async def process_lecture(request: ProcessRequest) -> ProcessResponse:
    """
    Complete NLP processing pipeline.
    
    Performs: Summarization → Keywords → Formula Detection
    
    - **text**: Input lecture text
    - **compression_ratio**: Summarization ratio (0.2-0.7)
    - **num_keywords**: Number of keywords (3-30)
    - **include_formulas**: Enable formula detection
    - **language**: Language code or auto-detect
    
    Returns comprehensive analysis with statistics.
    """
    try:
        processor = get_nlp_processor()
        result = processor.process(
            request.text,
            compression_ratio=request.compression_ratio,
            num_keywords=request.num_keywords,
            include_formulas=request.include_formulas,
            language=request.language
        )
        return ProcessResponse(**result)
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def service_info() -> Dict[str, Any]:
    """Get service information and capabilities."""
    try:
        processor = get_nlp_processor()
        return processor.get_service_info()
    except Exception as e:
        logger.error(f"Info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "enhanced_nlp"
    }
