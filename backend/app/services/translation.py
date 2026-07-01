import logging
from typing import Dict, List, Optional, Any
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TranslationService:
    """Handles text translation using mock mode for testing."""
    
    def __init__(self):
        """Initialize."""
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        logger.info("Initialized TranslationService")
    
    def translate_text(self, text: str, target_language: str, source_language: str = "en") -> Dict[str, Any]:
        """Translate text to target language (mock)."""
        if target_language not in self.supported_languages:
            return {
                "status": "error",
                "message": f"Unsupported language: {target_language}",
                "translated_text": None
            }
        
        # Mock translations
        mock_translations = {
            "ta": "மாணவர்களைத் ஆதரிப்பதற்கான நரம்ப நெட்வொர்க்குகள்",
            "hi": "विद्यार्थियों का समर्थन करने के लिए तंत्रिका नेटवर्क",
            "te": "విద్యార్థుల సపోర్టటర్ నెట్‌వర్కులు",
            "kn": "ವಿದ್ಯಾರ್ಥಿ ಸಹಾಯಕ ನರಮೊದೆಲ್ವಂಚೆ",
            "ml": "കണ്ണാഡ ഭാഷ വിദ്യാര്ത്ഥി സഹായ"
        }
        
        translated = mock_translations.get(target_language, f"[{target_language}] {text}")
        
        return {
            "status": "success",
            "translated_text": translated,
            "source_language": source_language,
            "target_language": target_language
        }
    
    def translate_to_all_languages(self, text: str, exclude_languages: Optional[List[str]] = None) -> Dict[str, Any]:
        """Translate to all supported languages (mock)."""
        exclude = exclude_languages or []
        translations = {}
        
        for lang_code in self.supported_languages.keys():
            if lang_code not in exclude:
                result = self.translate_text(text, lang_code)
                translations[lang_code] = result["translated_text"]
        
        return {
            "status": "success",
            "translations": translations,
            "total_languages": len(translations)
        }


class TranslationCache:
    """In-memory cache for translations."""
    
    def __init__(self, max_cache_size: int = 1000):
        self.cache = {}
        self.max_size = max_cache_size
    
    def get(self, text: str, target_lang: str) -> Optional[str]:
        """Get cached translation."""
        key = f"{target_lang}:{hash(text)}"
        return self.cache.get(key)
    
    def set(self, text: str, target_lang: str, translated: str):
        """Cache translation."""
        if len(self.cache) >= self.max_size:
            self.cache.pop(next(iter(self.cache)))
        
        key = f"{target_lang}:{hash(text)}"
        self.cache[key] = translated
