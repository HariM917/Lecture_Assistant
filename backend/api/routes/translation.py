"""Translation routes — translate transcriptions to multiple languages."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.dependencies import get_translation_service
from app.models.database import TranscriptionNote, Translation

router = APIRouter(tags=["Translation"])
logger = logging.getLogger(__name__)


class TranslateRequest(BaseModel):
    target_language: str = Field(..., description="ISO 639-1 language code")


@router.post("/transcriptions/{transcription_id}/translate", summary="Translate to Language")
async def translate_transcription(
    transcription_id: str,
    body: TranslateRequest,
    db: Session = Depends(get_db),
    translation_svc=Depends(get_translation_service),
):
    """Translate a transcription to a specific language."""
    note = db.query(TranscriptionNote).filter(TranscriptionNote.id == transcription_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Transcription not found")

    result = translation_svc.translate_text(
        text=note.raw_text,
        target_language=body.target_language,
        source_language=note.language or "en",
    )

    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message", "Translation failed"))

    # Persist
    trans = Translation(
        transcription_id=transcription_id,
        target_language=body.target_language,
        translated_text=result["translated_text"],
    )
    db.add(trans)
    db.commit()

    return {
        "status": "success",
        "translation": result["translated_text"],
        "target_language": body.target_language,
        "original_text": note.raw_text,
        "mode": result.get("mode", "unknown"),
    }


@router.post("/transcriptions/{transcription_id}/translate-all", summary="Translate to All Languages")
async def translate_to_all(
    transcription_id: str,
    db: Session = Depends(get_db),
    translation_svc=Depends(get_translation_service),
):
    """Translate a transcription to all supported languages."""
    note = db.query(TranscriptionNote).filter(TranscriptionNote.id == transcription_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Transcription not found")

    result = translation_svc.translate_to_all_languages(
        text=note.raw_text,
        source_language=note.language or "en",
    )

    translations = result.get("translations", {})

    # Persist all translations
    for lang_code, translated_text in translations.items():
        trans = Translation(
            transcription_id=transcription_id,
            target_language=lang_code,
            translated_text=translated_text,
        )
        db.add(trans)
    db.commit()

    logger.info(f"Translated {transcription_id} to {len(translations)} languages")

    return {
        "status": "success",
        "translations": translations,
        "original_text": note.raw_text,
        "original_language": note.language or "en",
        "languages_count": len(translations),
        "mode": result.get("mode", "unknown"),
    }
