import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class NLPExtractionService:
    """Handles keyword and formula extraction (mock mode)."""
    
    def __init__(self):
        """Initialize."""
        logger.info("Initialized NLPExtractionService")
    
    def extract_keywords(self, text: str, top_n: int = 20, pos_tags: List[str] = None) -> Dict[str, Any]:
        """Extract keywords (mock)."""
        # Simple extraction: words longer than 3 chars
        words = text.lower().split()
        keywords = list(set([w for w in words if len(w) > 3]))[:top_n]
        
        return {
            "status": "success",
            "keywords": keywords,
            "total_keywords": len(keywords)
        }
    
    def extract_formulas(self, text: str) -> Dict[str, Any]:
        """Extract mathematical formulas (regex-based)."""
        extracted = {}
        
        # Extract equations
        equations = re.findall(r'[a-zA-Z0-9_\s\+\-\*\.\/\(\)]+\s*=\s*[a-zA-Z0-9_\s\+\-\*\.\/\(\)]+', text)
        if equations:
            extracted["equations"] = equations[:5]
        
        # Extract scientific notation
        scientific = re.findall(r'\d+\.?\d*\s*[×x]\s*10\^?\s*[-+]?\d+', text)
        if scientific:
            extracted["scientific_notation"] = scientific
        
        return {
            "status": "success",
            "formulas": extracted,
            "formula_count": sum(len(v) for v in extracted.values())
        }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities (mock)."""
        return {
            "status": "success",
            "entities": {
                "PERSON": ["Dr. Smith"],
                "ORG": ["Stanford University"]
            },
            "total_entities": 2
        }
    
    def comprehensive_extraction(self, text: str) -> Dict[str, Any]:
        """Perform comprehensive extraction (mock)."""
        keywords_result = self.extract_keywords(text)
        formulas_result = self.extract_formulas(text)
        entities_result = self.extract_entities(text)
        
        return {
            "status": "success",
            "keywords": keywords_result.get("keywords", []),
            "formulas": formulas_result.get("formulas", {}),
            "entities": entities_result.get("entities", {})
        }
