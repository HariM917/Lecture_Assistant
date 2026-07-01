"""
NLP extraction service — keyword, formula, and entity extraction.
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Common English stop words
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "this", "that",
    "these", "those", "i", "me", "my", "we", "our", "you", "your",
    "he", "she", "it", "they", "them", "their", "what", "which", "who",
    "when", "where", "how", "not", "no", "nor", "but", "and", "or",
    "if", "then", "than", "too", "very", "just", "about", "above",
    "after", "again", "all", "also", "any", "because", "before",
    "between", "both", "each", "for", "from", "get", "got", "into",
    "its", "more", "most", "much", "many", "of", "on", "only", "other",
    "out", "over", "own", "same", "so", "some", "such", "to", "up",
    "with", "there", "here", "through", "during", "until", "while",
}


class NLPExtractionService:
    """Keyword, formula, and entity extraction without ML dependencies."""

    def __init__(self):
        logger.info("NLPExtractionService initialized (rule-based)")

    def extract_keywords(self, text: str, top_n: int = 15) -> Dict[str, Any]:
        """Extract keywords using TF-based scoring."""
        if not text:
            return {"status": "success", "keywords": [], "total_keywords": 0}

        # Tokenize and filter
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words = [w for w in words if w not in STOP_WORDS]

        # Count frequencies
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1

        # Also extract bigrams (two-word phrases)
        bigrams = []
        word_list = text.lower().split()
        for i in range(len(word_list) - 1):
            w1 = re.sub(r'[^\w]', '', word_list[i])
            w2 = re.sub(r'[^\w]', '', word_list[i + 1])
            if w1 not in STOP_WORDS and w2 not in STOP_WORDS and len(w1) > 2 and len(w2) > 2:
                bigram = f"{w1} {w2}"
                freq[bigram] = freq.get(bigram, 0) + 2  # boost bigrams

        # Sort by frequency
        sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [kw for kw, _ in sorted_kw[:top_n]]

        return {
            "status": "success",
            "keywords": keywords,
            "total_keywords": len(keywords),
        }

    def extract_formulas(self, text: str) -> Dict[str, Any]:
        """Extract mathematical formulas and equations."""
        formulas = []

        # Match equations like "y = mx + b", "E = mc²"
        equations = re.findall(
            r'[A-Za-z_]\w*\s*=\s*[A-Za-z0-9_\s\+\-\*\/\^\(\)\.σΣ∑]+',
            text
        )
        for eq in equations[:10]:
            eq_clean = eq.strip()
            if len(eq_clean) > 3:
                formulas.append({
                    "formula": eq_clean,
                    "type": "equation",
                    "context": self._get_context(text, eq_clean),
                })

        # Match scientific notation
        sci = re.findall(r'\d+\.?\d*\s*[×x]\s*10\^?\s*[-+]?\d+', text)
        for s in sci[:5]:
            formulas.append({"formula": s.strip(), "type": "scientific_notation", "context": ""})

        return {
            "status": "success",
            "formulas": formulas,
            "formula_count": len(formulas),
        }

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities using pattern matching."""
        entities: Dict[str, List[str]] = {
            "concepts": [],
            "technologies": [],
            "persons": [],
        }

        # Capitalize phrases (likely proper nouns or concepts)
        caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
        for c in caps:
            if len(c.split()) <= 4:
                entities["concepts"].append(c)

        # Tech-related terms
        tech_patterns = [
            r'\b(?:machine learning|deep learning|neural network|artificial intelligence|'
            r'natural language processing|computer vision|data science|blockchain|cloud computing)\b'
        ]
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities["technologies"].extend(set(matches))

        # Titles + Names (Dr., Prof., Mr., Mrs.)
        persons = re.findall(r'\b(?:Dr|Prof|Mr|Mrs|Ms)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', text)
        entities["persons"] = list(set(persons))

        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))

        return {
            "status": "success",
            "entities": entities,
            "total_entities": sum(len(v) for v in entities.values()),
        }

    def comprehensive_extraction(self, text: str) -> Dict[str, Any]:
        """Full extraction pipeline: keywords + formulas + entities."""
        kw = self.extract_keywords(text)
        formulas = self.extract_formulas(text)
        ents = self.extract_entities(text)

        return {
            "status": "success",
            "keywords": kw.get("keywords", []),
            "formulas": formulas.get("formulas", []),
            "entities": ents.get("entities", {}),
            "keyword_count": kw.get("total_keywords", 0),
            "formula_count": formulas.get("formula_count", 0),
            "entity_count": ents.get("total_entities", 0),
        }

    @staticmethod
    def _get_context(text: str, target: str, window: int = 50) -> str:
        """Get surrounding context for a match."""
        idx = text.find(target)
        if idx == -1:
            return ""
        start = max(0, idx - window)
        end = min(len(text), idx + len(target) + window)
        return text[start:end].strip()
