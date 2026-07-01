"""
🎓 Enhanced NLP - Practical Examples & Recipes

Real-world usage patterns for the Enhanced NLP Service
"""

# ============================================================================
# EXAMPLE 1: Basic Lecture Processing
# ============================================================================

from app.services.enhanced_nlp import process_lecture

lecture_text = """
Machine learning is a subset of artificial intelligence that focuses on 
the development of algorithms and statistical models that enable computers 
to improve their performance on tasks through experience. The fundamental 
concept of machine learning is that systems can learn from data, identify 
patterns, and make decisions with minimal human intervention.

There are three main types of machine learning: supervised learning, 
unsupervised learning, and reinforcement learning. Supervised learning 
involves training on labeled data where the correct answers are provided. 
This technique is widely used in practical applications like image 
classification and spam detection.

The key advantage of machine learning is automation. Machine learning models 
can process large datasets efficiently and find patterns that humans might 
miss. Another important benefit is that these models improve over time as 
they encounter more data. This adaptive nature makes machine learning 
particularly valuable for dynamic environments where conditions change rapidly.

Mathematical foundations are critical. The formula for gradient descent is:
w = w - α * ∇J(w)

Where w represents weights, α is the learning rate, and ∇J(w) is the gradient.
"""

# Process with defaults
result = process_lecture(lecture_text)

print("📋 Summary:")
print(result["summary"])
print(f"\n📊 Compression: {result['stats']['compression_ratio']}%")
print(f"\n🔑 Keywords: {', '.join(result['keywords'][:5])}")
print(f"\n📐 Formulas detected: {len(result['formulas'])}")


# ============================================================================
# EXAMPLE 2: Heavy Compression for Mobile/Notifications
# ============================================================================

# Create short summaries for mobile apps
mobile_summary = process_lecture(
    lecture_text,
    compression_ratio=0.25,  # Only 25% of original
    num_keywords=5,
    include_formulas=True
)

print("\n" + "="*60)
print("📱 Mobile Summary (25% compression):")
print(mobile_summary["summary"])


# ============================================================================
# EXAMPLE 3: Detailed Analysis for Academic Papers
# ============================================================================

# Extract maximum information for research papers
academic_result = process_lecture(
    lecture_text,
    compression_ratio=0.6,    # Keep 60% for detail
    num_keywords=20,           # More keywords for indexing
    include_formulas=True,
    language="en"
)

print("\n" + "="*60)
print("🎓 Academic Analysis (60% retention):")
print(f"Keywords: {academic_result['keywords'][:10]}")


# ============================================================================
# EXAMPLE 4: Multilingual Lecture Processing (Hindi)
# ============================================================================

hindi_lecture = """
मशीन लर्निंग कृत्रिम बुद्धिमत्ता का एक उपसमुच्चय है जो एल्गोरिदम और 
सांख्यिकीय मॉडल के विकास पर केंद्रित है। मशीन लर्निंग की मौलिक 
अवधारणा यह है कि सिस्टम डेटा से सीख सकते हैं और न्यूनतम मानव 
हस्तक्षेप के साथ निर्णय ले सकते हैं।

मशीन लर्निंग के तीन मुख्य प्रकार हैं: निरीक्षित शिक्षा, अनिरीक्षित 
शिक्षा और सुदृढीकरण शिक्षा। महत्वपूर्ण अवधारणा यह है कि मॉडल 
अधिक डेटा के साथ सुधरते हैं।
"""

hindi_result = process_lecture(
    hindi_lecture,
    language="hi"  # Specify Hindi
)

print("\n" + "="*60)
print("🇮🇳 Hindi Lecture Processing:")
print(f"Summary: {hindi_result['summary'][:100]}...")
print(f"Keywords: {', '.join(hindi_result['keywords'][:5])}")


# ============================================================================
# EXAMPLE 5: Batch Processing Multiple Lectures
# ============================================================================

lectures = [
    {"title": "Machine Learning Basics", "text": lecture_text},
    {"title": "Deep Learning", "text": "Deep learning models with neural networks..."},
    {"title": "NLP Fundamentals", "text": "Natural language processing enables computers..."}
]

processed_batch = []
for lecture in lectures:
    result = process_lecture(lecture["text"])
    processed_batch.append({
        "title": lecture["title"],
        "keywords": result["keywords"],
        "summary": result["summary"][:80] + "..."
    })

print("\n" + "="*60)
print("📚 Batch Processing Results:")
for item in processed_batch:
    print(f"\n📖 {item['title']}")
    print(f"   Keywords: {', '.join(item['keywords'][:3])}")
    print(f"   Summary: {item['summary']}")


# ============================================================================
# EXAMPLE 6: Keyword-Focused Research
# ============================================================================

from app.services.enhanced_nlp import get_nlp_processor

processor = get_nlp_processor()

# Extract comprehensive keyword set for research indexing
research_keywords = processor.keyword_extractor.extract(
    lecture_text,
    min_length=5,   # Only longer, more significant terms
    top_n=15        # Top 15 keywords
)

print("\n" + "="*60)
print("🔬 Research Keywords (min length 5):")
print(research_keywords)


# ============================================================================
# EXAMPLE 7: Formula Extraction for Problem Sets
# ============================================================================

math_lecture = """
Basic Physics Formulas:

The velocity formula is: v = d/t

Where v is velocity, d is distance, and t is time.

For acceleration: a = (v₂ - v₁)/t

Newton's second law: F = ma

The kinetic energy formula: E = ½mv²

These are fundamental equations in classical mechanics.
"""

formulas = processor.formula_detector.detect(math_lecture)

print("\n" + "="*60)
print("📐 Extracted Formulas:")
for formula in formulas:
    print(f"  • {formula}")


# ============================================================================
# EXAMPLE 8: Integration with Sentiment Analysis
# ============================================================================

from app.services.sentiment_analysis import analyze_sentiment

# Process lecture AND analyze emotional tone
nlp_result = process_lecture(lecture_text)
sentiment = analyze_sentiment(nlp_result["summary"])

print("\n" + "="*60)
print("😊 Combined Analysis:")
print(f"Summary: {nlp_result['summary'][:100]}...")
print(f"Sentiment: {sentiment.get('emotion', 'unknown')}")


# ============================================================================
# EXAMPLE 9: Creating Study Guide from Lecture
# ============================================================================

def create_study_guide(lecture_text: str) -> dict:
    """Generate a complete study guide from lecture material."""
    
    result = process_lecture(
        lecture_text,
        compression_ratio=0.5,
        num_keywords=15,
        include_formulas=True
    )
    
    study_guide = {
        "key_concepts": result["keywords"][:5],
        "important_terms": result["keywords"],
        "essential_equations": result["formulas"],
        "quick_summary": result["summary"],
        "self_check_questions": [
            f"Explain: {kw}" for kw in result["keywords"][:3]
        ]
    }
    
    return study_guide

guide = create_study_guide(lecture_text)

print("\n" + "="*60)
print("📖 Study Guide Generated:")
print(f"Key Concepts: {', '.join(guide['key_concepts'])}")
print(f"Self-Check Questions:")
for q in guide["self_check_questions"]:
    print(f"  • {q}")


# ============================================================================
# EXAMPLE 10: API Usage (FastAPI)
# ============================================================================

"""
To use via HTTP API:

# 1. Summarization
curl -X POST http://localhost:8000/api/nlp/summarize \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Long lecture text...",
    "compression_ratio": 0.4
  }'

# 2. Extract Keywords
curl -X POST http://localhost:8000/api/nlp/extract-keywords \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "...",
    "num_keywords": 10
  }'

# 3. Complete Processing
curl -X POST http://localhost:8000/api/nlp/process \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "...",
    "compression_ratio": 0.4,
    "num_keywords": 10,
    "include_formulas": true
  }'

# 4. Service Info
curl http://localhost:8000/api/nlp/info
"""

# Python requests example
import requests

def process_via_api(lecture_text: str):
    """Call NLP service via HTTP API."""
    
    response = requests.post(
        "http://localhost:8000/api/nlp/process",
        json={
            "text": lecture_text,
            "compression_ratio": 0.4,
            "num_keywords": 10,
            "include_formulas": True
        }
    )
    
    return response.json()

# result = process_via_api(lecture_text)


# ============================================================================
# EXAMPLE 11: Comparison - Different Compression Ratios
# ============================================================================

print("\n" + "="*60)
print("📊 Compression Comparison:")

for ratio in [0.2, 0.4, 0.6]:
    result = process_lecture(lecture_text, compression_ratio=ratio)
    words = result["stats"]["summary_words"]
    print(f"\nRatio {ratio*100:.0f}%: {words} words")
    print(f"Summary: {result['summary'][:60]}...")


# ============================================================================
# EXAMPLE 12: Error Handling
# ============================================================================

def safe_process_lecture(text: str, retries: int = 3) -> dict:
    """Process lecture with error handling."""
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Validation
    if not text or len(text.split()) < 50:
        logger.warning("Text too short for processing")
        return {"status": "error", "message": "Text too short"}
    
    # Attempt processing with retries
    for attempt in range(retries):
        try:
            result = process_lecture(text)
            logger.info(f"✅ Processing succeeded on attempt {attempt + 1}")
            return result
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries - 1:
                return {"status": "error", "message": str(e)}
    
    return {"status": "error", "message": "Max retries exceeded"}


# ============================================================================
# Running the Examples
# ============================================================================

if __name__ == "__main__":
    print("🚀 Enhanced NLP Service Examples")
    print("="*60)
    print("Run individual examples above or all together for full demo")
