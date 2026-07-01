"""
Advanced Features API Routes
Sentiment analysis, cultural translation, meeting summarizer, context memory, questions, rewards
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
import logging
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.services.sentiment_analysis import SentimentAnalysisService
from app.services.cultural_translator import CulturalContextTranslator
from app.services.meeting_summarizer import MeetingSummarizer
from app.services.context_memory_translator import ContextAwareTranslator
from app.services.question_generator import QuestionGenerator, QuestionType, RewardsSystem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lecture/advanced", tags=["advanced"])

# Initialize services
sentiment_service = SentimentAnalysisService()
cultural_translator = CulturalContextTranslator()
meeting_summarizer = MeetingSummarizer()
context_translator = ContextAwareTranslator()
question_generator = QuestionGenerator()

# Store rewards systems in memory (in production, use database)
rewards_systems: dict = {}


# ============== SENTIMENT ANALYSIS ==============

@router.post("/sentiment/analyze")
async def analyze_sentiment(text: str = Query(...), context: str = Query("lecture", regex="^(lecture|meeting|casual)$")):
    """Analyze sentiment and emotions in text"""
    try:
        result = sentiment_service.analyze(text, context)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/analyze-batch")
async def analyze_batch_sentiment(texts: List[str], context: str = Query("lecture")):
    """Analyze sentiment for multiple texts"""
    try:
        results = sentiment_service.batch_analyze(texts, context)
        return {
            "status": "success",
            "count": len(results),
            "data": results
        }
    except Exception as e:
        logger.error(f"Batch sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/analyze-sentences")
async def analyze_sentence_sentiment(text: str = Query(...)):
    """Analyze sentiment at sentence level"""
    try:
        result = sentiment_service.analyze_by_sentences(text)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Sentence sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== CULTURAL TRANSLATION ==============

@router.post("/translate/cultural")
async def translate_with_culture(
    text: str = Query(...),
    source_lang: str = Query("en"),
    target_lang: str = Query("ta"),
    context: str = Query("general")
):
    """Translate text with cultural context awareness"""
    try:
        result = cultural_translator.translate_with_culture(text, source_lang, target_lang, context)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Cultural translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== MEETING SUMMARIZER ==============

@router.post("/meeting/summarize")
async def summarize_meeting(
    transcript: str = Query(...),
    title: Optional[str] = Query(None),
    duration: Optional[int] = Query(None)
):
    """Summarize a meeting transcript"""
    try:
        metadata = {
            'title': title or 'Meeting',
            'duration_minutes': duration or 0
        }
        result = meeting_summarizer.summarize_meeting(transcript, metadata)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Meeting summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meeting/summarize-batch")
async def summarize_multiple_meetings(
    transcripts: List[str],
    thread_id: Optional[str] = Query(None)
):
    """Summarize multiple related meetings"""
    try:
        result = meeting_summarizer.summarize_multiple_meetings(transcripts, thread_id)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Batch meeting summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== CONTEXT MEMORY TRANSLATION ==============

@router.post("/translate/context-aware")
async def translate_with_context(
    text: str = Query(...),
    source_lang: str = Query("en"),
    target_lang: str = Query("ta"),
    context_type: str = Query("general")
):
    """Translate with AI context memory"""
    try:
        result = context_translator.translate_with_context(text, source_lang, target_lang, context_type)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Context-aware translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translate/memory-report")
async def get_translation_memory_report():
    """Get report on translation memory usage"""
    try:
        report = context_translator.get_translation_memory_report()
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Memory report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate/batch-with-context")
async def batch_translate_with_context(
    texts: List[str],
    source_lang: str = Query("en"),
    target_lang: str = Query("ta"),
    context_type: str = Query("general")
):
    """Batch translate with context tracking"""
    try:
        results = context_translator.batch_translate_with_memory(texts, source_lang, target_lang, context_type)
        return {
            "status": "success",
            "count": len(results),
            "data": results
        }
    except Exception as e:
        logger.error(f"Batch context translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== QUESTION GENERATION ==============

@router.post("/questions/generate")
async def generate_questions(
    content: str = Query(...),
    num_questions: int = Query(5, ge=1, le=20),
    question_types: Optional[List[str]] = Query(["multiple_choice", "short_answer"]),
    bloom_level: str = Query("understand")
):
    """Generate questions from lecture content"""
    try:
        q_types = [QuestionType[qt.upper()] for qt in question_types if qt.upper() in QuestionType.__members__]
        if not q_types:
            q_types = [QuestionType.MULTIPLE_CHOICE, QuestionType.SHORT_ANSWER]

        questions = question_generator.generate_questions(
            content, num_questions, q_types, bloom_level
        )
        return {
            "status": "success",
            "count": len(questions),
            "data": questions
        }
    except Exception as e:
        logger.error(f"Question generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== REWARDS SYSTEM ==============

@router.post("/rewards/init")
async def initialize_rewards(user_id: str = Query(...)):
    """Initialize rewards system for user"""
    try:
        if user_id not in rewards_systems:
            rewards_systems[user_id] = RewardsSystem(user_id)
        return {
            "status": "success",
            "message": f"Rewards system initialized for {user_id}"
        }
    except Exception as e:
        logger.error(f"Rewards init error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewards/submit-answer")
async def submit_answer(
    user_id: str = Query(...),
    question_id: str = Query(...),
    is_correct: bool = Query(...),
    time_taken: int = Query(0)
):
    """Submit answer and get rewards"""
    try:
        if user_id not in rewards_systems:
            rewards_systems[user_id] = RewardsSystem(user_id)

        rewards = rewards_systems[user_id].submit_answer(question_id, is_correct, time_taken)
        return {
            "status": "success",
            "data": rewards,
            "user_stats": rewards_systems[user_id].get_user_stats()
        }
    except Exception as e:
        logger.error(f"Answer submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rewards/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user reward statistics"""
    try:
        if user_id not in rewards_systems:
            return {
                "status": "error",
                "message": "User not found in rewards system"
            }

        stats = rewards_systems[user_id].get_user_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Stats retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rewards/leaderboard")
async def get_leaderboard(limit: int = Query(10, ge=1, le=100)):
    """Get leaderboard of top users"""
    try:
        entries = [
            rewards_systems[uid].leaderboard_entry()
            for uid in rewards_systems
        ]
        # Sort by points descending
        entries.sort(key=lambda x: x['points'], reverse=True)
        return {
            "status": "success",
            "count": len(entries[:limit]),
            "data": entries[:limit]
        }
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewards/award-points")
async def award_points(user_id: str = Query(...), points: int = Query(...), reason: str = Query(...)):
    """Manually award points to user"""
    try:
        if user_id not in rewards_systems:
            rewards_systems[user_id] = RewardsSystem(user_id)

        result = rewards_systems[user_id].award_points(points, reason)
        return {
            "status": "success",
            "data": result,
            "user_stats": rewards_systems[user_id].get_user_stats()
        }
    except Exception as e:
        logger.error(f"Award points error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== HEALTH CHECK ==============

@router.get("/health")
async def advanced_health_check():
    """Health check for advanced features"""
    return {
        "status": "healthy",
        "services": {
            "sentiment_analysis": "ready",
            "cultural_translator": "ready",
            "meeting_summarizer": "ready",
            "context_memory_translator": "ready",
            "question_generator": "ready",
            "rewards_system": "ready"
        },
        "active_users": len(rewards_systems)
    }
