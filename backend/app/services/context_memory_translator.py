"""
AI Context Memory Translator
Maintains conversation context and translates while preserving semantic meaning
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class ContextMemory:
    """Maintains context across translation operations"""

    def __init__(self, max_history: int = 50):
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self.context_stack: List[Dict[str, Any]] = []
        self.entity_memory: Dict[str, str] = {}  # Entity → Translation mapping
        self.terminology: Dict[str, Dict[str, str]] = {}  # Term → Lang translations

    def add_to_history(self, original: str, translated: str, language_pair: tuple, context: str = None):
        """Add translation to history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'original': original,
            'translated': translated,
            'language_pair': language_pair,
            'context': context,
            'entities': self._extract_entities(original),
            'terminology': self._extract_terminology(original)
        }
        self.history.append(entry)

        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        # Update entity and terminology memories
        self._update_memories(entry)

    def get_context(self, lookback_seconds: int = 300) -> List[Dict[str, Any]]:
        """Get recent context within time window"""
        cutoff_time = datetime.now() - timedelta(seconds=lookback_seconds)
        recent = [
            entry for entry in self.history
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        return recent

    def push_context(self, context: Dict[str, Any]):
        """Push context onto stack"""
        self.context_stack.append(context)

    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop context from stack"""
        return self.context_stack.pop() if self.context_stack else None

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """Get current context without removing"""
        return self.context_stack[-1] if self.context_stack else None

    def add_entity_translation(self, original: str, translation: str, language_code: str):
        """Add/update entity translation for future consistency"""
        key = f"{original}_{language_code}"
        self.entity_memory[key] = translation

    def get_entity_translation(self, original: str, language_code: str) -> Optional[str]:
        """Get previously translated entity"""
        key = f"{original}_{language_code}"
        return self.entity_memory.get(key)

    def add_terminology(self, term: str, translations: Dict[str, str]):
        """Add term and its translations across languages"""
        self.terminology[term.lower()] = translations

    def get_terminology(self, term: str) -> Optional[Dict[str, str]]:
        """Get terminology translations"""
        return self.terminology.get(term.lower())

    def _extract_entities(self, text: str) -> List[str]:
        """Simple entity extraction (proper nouns, numbers)"""
        import re
        # Find capitalized words
        entities = re.findall(r'\b[A-Z][a-z]+\b', text)
        # Find numbers
        entities.extend(re.findall(r'\d+', text))
        return list(set(entities))

    def _extract_terminology(self, text: str) -> List[str]:
        """Extract technical terminology"""
        # Simple heuristic: words in ALL_CAPS or with underscores
        import re
        terms = re.findall(r'\b[A-Z_]+\b', text)
        return list(set(terms))

    def _update_memories(self, entry: Dict[str, Any]):
        """Update entity and terminology memories from entry"""
        for entity in entry['entities']:
            # Try to find corresponding translation
            self.add_entity_translation(entity, entity, entry['language_pair'][1])

        for term in entry['terminology']:
            if term not in self.terminology:
                self.terminology[term.lower()] = {
                    entry['language_pair'][0]: term,
                    entry['language_pair'][1]: term
                }

    def clear_memory(self):
        """Clear all memory"""
        self.history.clear()
        self.context_stack.clear()
        self.entity_memory.clear()
        self.terminology.clear()

    def export_memory(self) -> Dict[str, Any]:
        """Export memory for inspection/debugging"""
        return {
            'history_size': len(self.history),
            'context_stack_depth': len(self.context_stack),
            'entities_learned': len(self.entity_memory),
            'terminology_learned': len(self.terminology),
            'recent_history': self.history[-10:]
        }


class ContextAwareTranslator:
    """Translator that uses context memory for better translations"""

    def __init__(self):
        self.memory = ContextMemory()
        self.language_profiles = {
            'technical': ['algorithm', 'neural', 'machine', 'learning', 'compute', 'system'],
            'academic': ['research', 'study', 'hypothesis', 'conclusion', 'analysis', 'theory'],
            'casual': ['like', 'think', 'maybe', 'probably', 'kind of', 'sort of'],
            'formal': ['hereby', 'therefore', 'furthermore', 'concluded', 'established']
        }

    def translate_with_context(self, text: str, source_lang: str, target_lang: str, 
                              context_type: str = 'general') -> Dict[str, Any]:
        """
        Translate text while maintaining context consistency
        """
        try:
            # Get relevant context
            recent_context = self.memory.get_context(lookback_seconds=600)

            # Check for previously translated entities
            entity_translations = {}
            for word in text.split():
                existing = self.memory.get_entity_translation(word, target_lang)
                if existing:
                    entity_translations[word] = existing

            # Check for terminology
            terminology_used = self._detect_terminology(text, context_type)

            # Perform translation (mock)
            translated = self._perform_translation(
                text, source_lang, target_lang,
                entity_translations, terminology_used
            )

            # Store in memory for future context
            self.memory.add_to_history(text, translated, (source_lang, target_lang), context_type)

            return {
                'original': text,
                'translated': translated,
                'source_language': source_lang,
                'target_language': target_lang,
                'context_type': context_type,
                'context_consistency': self._calculate_consistency(recent_context, text),
                'entities_used': list(entity_translations.keys()),
                'terminology_used': terminology_used,
                'confidence': 0.88,
                'memory_snapshot': self.memory.export_memory()
            }

        except Exception as e:
            logger.error(f"Context-aware translation error: {e}")
            return {
                'original': text,
                'translated': text,
                'error': str(e)
            }

    def _detect_terminology(self, text: str, context_type: str) -> List[str]:
        """Detect terminology based on context"""
        detected = []
        text_lower = text.lower()

        for profile_type, keywords in self.language_profiles.items():
            if context_type == profile_type or any(kw in text_lower for kw in keywords):
                detected.extend([kw for kw in keywords if kw in text_lower])

        return list(set(detected))

    def _perform_translation(self, text: str, source_lang: str, target_lang: str,
                            entity_translations: Dict, terminology: List[str]) -> str:
        """Perform the actual translation with context"""
        translated = text

        # Replace known entities
        for entity, translation in entity_translations.items():
            translated = translated.replace(entity, translation)

        # Simple mock translation
        culture_map = {
            ('en', 'ta'): f"[Tamil]: {translated[:50]}...",
            ('en', 'hi'): f"[Hindi]: {translated[:50]}...",
        }

        if (source_lang, target_lang) in culture_map:
            translated = culture_map[(source_lang, target_lang)]

        return translated

    def _calculate_consistency(self, context: List[Dict], new_text: str) -> float:
        """Calculate how consistent new translation is with context"""
        if not context:
            return 0.5  # No context to compare

        # Check entity consistency
        context_entities = set()
        for entry in context:
            context_entities.update(entry.get('entities', []))

        new_entities = set()
        import re
        new_entities.update(re.findall(r'\b[A-Z][a-z]+\b', new_text))

        if not context_entities or not new_entities:
            return 0.7

        overlap = len(context_entities & new_entities) / len(context_entities | new_entities)
        return overlap

    def batch_translate_with_memory(self, texts: List[str], source_lang: str, 
                                   target_lang: str, context_type: str = 'general') -> List[Dict]:
        """Translate multiple texts while building up context"""
        results = []

        for text in texts:
            result = self.translate_with_context(text, source_lang, target_lang, context_type)
            results.append(result)

        return results

    def get_translation_memory_report(self) -> Dict[str, Any]:
        """Generate report on translation memory usage"""
        memory_export = self.memory.export_memory()
        
        return {
            'total_translations': memory_export['history_size'],
            'context_level': memory_export['context_stack_depth'],
            'entities_consistency_maintained': memory_export['entities_learned'],
            'terminology_consistency_maintained': memory_export['terminology_learned'],
            'last_translations': memory_export['recent_history'],
            'memory_efficiency': (memory_export['entities_learned'] + 
                                memory_export['terminology_learned']) / max(memory_export['history_size'], 1),
            'timestamp': datetime.now().isoformat()
        }
