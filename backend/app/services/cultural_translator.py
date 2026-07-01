"""
Cultural Context Translator
Handles idioms, slangs, cultural references, and emotions with cultural awareness
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class CulturalContextTranslator:
    """Translate text with cultural context awareness"""

    def __init__(self):
        # Cultural idioms and expressions mapping
        self.cultural_idioms = {
            # English idioms
            'en': {
                'piece of cake': {'ta': 'மிகவும் சுலபமான விஷயம்', 'hi': 'बहुत आसान काम', 'te': 'చాలా సులభమైన విషయం'},
                'break the ice': {'ta': 'முதல் படி எடுத்துவைக்க', 'hi': 'पहला कदम उठाना', 'te': 'మొదటి దశ తీసుకోవడం'},
                'hit the books': {'ta': 'படிப்பதற்கு கவனம் செலுத்த', 'hi': 'पढ़ाई पर ध्यान देना', 'te': 'అధ్యయనానికి దృష్టి సారించండి'},
                'piece of mind': {'ta': 'தெளிவாக கூற வேண்டியது சொல்ல', 'hi': 'अपनी बात स्पष्ट करना', 'te': 'మీ అభిప్రాయాన్ని స్పష్టంగా చెప్పండి'},
                'learning curve': {'ta': 'கற்றல் காலம்', 'hi': 'सीखने का समय', 'te': 'నేర్చుకోవటకు సమయం'},
            },
            # Tamil idioms
            'ta': {
                'மூக்கை சிணுங்கவைக்க': {'en': 'to make someone angry', 'hi': 'किसी को गुस्से में करना'},
                'கணணீர் வடிய': {'en': 'to cry', 'hi': 'रोना'},
                'உள்ளம் கொட்டாரை': {'en': 'to be heartbroken', 'hi': 'दिल टूटना'},
            },
            # Hindi idioms
            'hi': {
                'आँख का तारा': {'en': 'apple of my eye', 'ta': 'கண்ணின் ஒளி'},
                'हाथ धो बैठना': {'en': 'to give up', 'ta': 'கைவிட்டுவிட'},
                'दिल टूटना': {'en': 'to be heartbroken', 'ta': 'உள்ளம் நோகிற'},
            }
        }

        # Cultural emotions and expressions
        self.cultural_emotions = {
            'en': {
                'gratitude': ['thank you', 'grateful', 'appreciate', 'thank goodness'],
                'respect': ['honor', 'respect', 'admire', 'dignified'],
                'affection': ['love', 'care', 'hold dear', 'cherish'],
                'shame': ['embarrassed', 'ashamed', 'disgrace'],
                'pride': ['proud', 'confident', 'dignified'],
            },
            'ta': {
                'நன்றி': ['நன்றி', 'எனக்கு நன்றி', 'மிக்க நன்றி'],
                'மரியாதை': ['மரியாதை', 'வணக்கம்', 'பெருமை'],
                'பாசம்': ['அன்பு', 'பாசம்', 'ஆசை'],
                'கூச்சம்': ['கூச்சபடுகிறேன்', '부끄럽다', 'அவமானம்'],
                'பெருமை': ['பெருமை', 'நன்றாக', 'கர்வம்'],
            },
            'hi': {
                'कृतज्ञता': ['धन्यवाद', 'आभारी', 'मेहरबानी'],
                'सम्मान': ['सम्मान', 'प्रणाम', 'आदर'],
                'स्नेह': ['प्रेम', 'प्यार', 'लगाव'],
                'शर्म': ['शर्मिंदा', 'शर्म', 'लाज'],
                'गर्व': ['गर्व', 'अभिमान', 'फख्र'],
            }
        }

        # Slang mapping
        self.slang_map = {
            'en': {
                'lol': {'ta': 'சிரிப்பு', 'hi': 'हँसी'},
                'omg': {'ta': 'இறைவா! ', 'hi': 'हे ईश्वर!'},
                'cool': {'ta': 'அద్భుతమైనది', 'hi': 'शानदार'},
                'awesome': {'ta': 'அற்புதமான', 'hi': 'शानदार'},
                'gonna': {'ta': 'என்று சொல்லலாம்', 'hi': 'कहा जा सकता है'},
                'wanna': {'ta': 'வேண்டுமல்ல?', 'hi': 'क्या चाहते हो?'},
            }
        }

        # Formal/Informal context mappings
        self.formality_levels = {
            'formal': {
                'en': 'Professional language, formal grammar, formal address',
                'ta': 'நெறிப்படுத்தப்பட்ட மொழி, முறையான தொடர్భ, சம்மానம்',
                'hi': 'पेशेवारी भाषा, औपचारिक संबोधन, सम्मान',
            },
            'informal': {
                'en': 'Casual language, conversational grammar, friendly tone',
                'ta': 'நிரந்தர மொழி, உரையாடல், நட்பு தொனி',
                'hi': 'आरामदायक भाषा, बातचीत की शैली, मित्रवत स्वर',
            },
            'academic': {
                'en': 'Technical terms, citations, formal structure',
                'ta': 'தொழில்நுட்ப சொற்., மேற்கோள்கள், முறையான கட்டமைப்பு',
                'hi': 'तकनीकी शब्द, उद्धरण, औपचारिक संरचना',
            }
        }

    def translate_with_culture(self, text: str, source_lang: str, target_lang: str, context: str = "general") -> Dict[str, Any]:
        """
        Translate text with cultural awareness
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, ta, hi, te, kn, ml)
            target_lang: Target language code
            context: Context (general, academic, casual)
        """
        try:
            # Check for idioms
            idiom_match = self._find_idiom(text, source_lang)
            
            # Check for slang
            slang_processed = self._process_slang(text, source_lang, target_lang)
            
            # Check for cultural emotions
            emotions_detected = self._detect_cultural_emotions(text, source_lang)
            
            # Get appropriate formality level
            formality_context = self._get_formality_level(context)
            
            # Perform translation (mock)
            translated = self._mock_translate(text, source_lang, target_lang)
            
            # Apply cultural adjustments
            if idiom_match:
                translated = self._apply_idiom_translation(translated, idiom_match, target_lang)
            
            if slang_processed:
                translated = slang_processed.get('translated', translated)
            
            return {
                'original_text': text,
                'translated_text': translated,
                'source_language': source_lang,
                'target_language': target_lang,
                'idioms_detected': idiom_match,
                'slang_detected': slang_processed['slang'] if slang_processed else [],
                'emotions_detected': emotions_detected,
                'formality_level': formality_context,
                'cultural_notes': self._generate_cultural_notes(text, source_lang, target_lang),
                'confidence': 0.85
            }
        except Exception as e:
            logger.error(f"Cultural translation error: {e}")
            return {
                'original_text': text,
                'translated_text': text,
                'error': str(e)
            }

    def _find_idiom(self, text: str, language: str) -> Optional[Dict[str, Any]]:
        """Find if text contains idioms"""
        if language not in self.cultural_idioms:
            return None
        
        for idiom in self.cultural_idioms[language]:
            if idiom.lower() in text.lower():
                return {
                    'idiom': idiom,
                    'translations': self.cultural_idioms[language][idiom]
                }
        return None

    def _process_slang(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """Process slang in text"""
        if source_lang not in self.slang_map:
            return None
        
        slang_found = []
        processed_text = text
        
        for slang, translations in self.slang_map[source_lang].items():
            if slang in text.lower():
                slang_found.append(slang)
                if target_lang in translations:
                    processed_text = processed_text.replace(slang, translations[target_lang])
        
        return {
            'slang': slang_found,
            'translated': processed_text
        } if slang_found else None

    def _detect_cultural_emotions(self, text: str, language: str) -> List[str]:
        """Detect cultural emotions in text"""
        if language not in self.cultural_emotions:
            return []
        
        detected = []
        text_lower = text.lower()
        
        for emotion, keywords in self.cultural_emotions[language].items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    detected.append(emotion)
                    break
        
        return list(set(detected))

    def _get_formality_level(self, context: str) -> str:
        """Determine appropriate formality"""
        if 'academic' in context.lower():
            return 'academic'
        elif 'casual' in context.lower():
            return 'informal'
        else:
            return 'formal'

    def _mock_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock translation (placeholder for real ML model)"""
        # This would be replaced with actual ML translation
        culture_translations = {
            ('en', 'ta'): f"(தமிழ்: {text})",
            ('en', 'hi'): f"(हिंदी: {text})",
            ('en', 'te'): f"(తెలుగు: {text})",
            ('en', 'kn'): f"(ಕನ್ನಡ: {text})",
            ('en', 'ml'): f"(മലയാളം: {text})",
        }
        return culture_translations.get((source_lang, target_lang), text)

    def _apply_idiom_translation(self, text: str, idiom_match: Dict, target_lang: str) -> str:
        """Replace idiom with culturally appropriate translation"""
        if target_lang in idiom_match['translations']:
            return text.replace(
                idiom_match['idiom'],
                idiom_match['translations'][target_lang]
            )
        return text

    def _generate_cultural_notes(self, text: str, source_lang: str, target_lang: str) -> List[str]:
        """Generate notes about cultural differences"""
        notes = []
        
        if source_lang == 'en' and target_lang in ['ta', 'hi', 'te']:
            notes.append(f"Indian language detected - consider cultural context")
        
        if self._find_idiom(text, source_lang):
            notes.append("Contains idiomatic expressions - literal translation may not convey meaning")
        
        emotions = self._detect_cultural_emotions(text, source_lang)
        if emotions:
            notes.append(f"Strong emotional content detected: {', '.join(emotions)}")
        
        return notes
