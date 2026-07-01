"""
Translation service with real translator and mock fallback.
"""

import logging
from typing import Dict, List, Optional, Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TranslationService:
    """Mock translation service for development."""

    MOCK_TRANSLATIONS = {
        "ta": "இது இயந்திர கற்றல் மற்றும் செயற்கை நுண்ணறிவு பற்றிய ஒரு விளக்கக் சொற்பொழிப்பு ஆகும்.",
        "hi": "यह मशीन लर्निंग और कृत्रिम बुद्धिमत्ता के बारे में एक प्रदर्शन व्याख्यान है।",
        "te": "ఇది యంత్ర అభ్యాసం మరియు కృత్రిమ మేధస్సు గురించిన ప్రదర్శన ఉపన్యాసం.",
        "kn": "ಇದು ಯಂತ್ರ ಕಲಿಕೆ ಮತ್ತು ಕೃತ್ರಿಮ ಬುದ್ಧಿಮತ್ತೆಯ ಕುರಿತು ಪ್ರದರ್ಶನ ಉಪನ್ಯಾಸವಾಗಿದೆ.",
        "ml": "ഇത് മെഷീൻ ലേണിംഗ്, ആർട്ടിഫിഷ്യൽ ഇന്റലിജൻസ് എന്നിവയെക്കുറിച്ചുള്ള ഒരു പ്രദർശന പ്രഭാഷണമാണ്.",
        "de": "Dies ist ein Demonstrationsvortrag über maschinelles Lernen und künstliche Intelligenz.",
        "zh": "这是一场关于机器学习和人工智能的演示讲座。",
        "ja": "これは機械学習と人工知能についてのデモンストレーション講義です。",
    }

    def __init__(self):
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        logger.info("TranslationService initialized (mock mode)")

    def translate_text(self, text: str, target_language: str, source_language: str = "en") -> Dict[str, Any]:
        """Translate text to target language (mock)."""
        if target_language not in self.supported_languages:
            return {"status": "error", "message": f"Unsupported language: {target_language}"}

        if target_language == source_language:
            translated = text
        else:
            translated = self.MOCK_TRANSLATIONS.get(target_language, f"[{target_language}] {text[:100]}...")

        return {
            "status": "success",
            "translated_text": translated,
            "source_language": source_language,
            "target_language": target_language,
            "mode": "mock",
        }

    def translate_to_all_languages(self, text: str, source_language: str = "en") -> Dict[str, Any]:
        """Translate to all supported languages."""
        translations = {}
        for lang_code in self.supported_languages:
            result = self.translate_text(text, lang_code, source_language)
            if result["status"] == "success":
                translations[lang_code] = result["translated_text"]

        return {
            "status": "success",
            "translations": translations,
            "total_languages": len(translations),
            "mode": "mock",
        }


class RealTranslationService(TranslationService):
    """Real translation using deep-translator library (free, no API key)."""

    def __init__(self):
        super().__init__()
        from deep_translator import GoogleTranslator
        self._translator_class = GoogleTranslator
        logger.info("TranslationService initialized (real — deep-translator)")

    def translate_text(self, text: str, target_language: str, source_language: str = "en") -> Dict[str, Any]:
        """Translate using Google Translate (free tier)."""
        if target_language not in self.supported_languages:
            return {"status": "error", "message": f"Unsupported language: {target_language}"}

        if target_language == source_language:
            return {
                "status": "success",
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "mode": "passthrough",
            }

        try:
            # deep-translator uses full language names or ISO codes
            translator = self._translator_class(source=source_language, target=target_language)
            # Translate in chunks if text is long (Google has a 5000 char limit)
            if len(text) > 4500:
                chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated = " ".join(translator.translate(chunk) for chunk in chunks)
            else:
                translated = translator.translate(text)

            return {
                "status": "success",
                "translated_text": translated,
                "source_language": source_language,
                "target_language": target_language,
                "mode": "real",
            }
        except Exception as e:
            logger.error(f"Translation error ({target_language}): {e}")
            # Fall back to mock
            return super().translate_text(text, target_language, source_language)


class TranslationCache:
    """In-memory LRU cache for translations."""

    def __init__(self, max_size: int = 500):
        self._cache: Dict[str, str] = {}
        self._max_size = max_size

    def get(self, text: str, target_lang: str) -> Optional[str]:
        return self._cache.get(f"{target_lang}:{hash(text)}")

    def set(self, text: str, target_lang: str, translated: str):
        if len(self._cache) >= self._max_size:
            # Remove oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[f"{target_lang}:{hash(text)}"] = translated
