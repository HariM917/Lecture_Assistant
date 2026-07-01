"""
🎤 Whisper Transcriber Pro - Practical Examples

Real-world usage patterns for professional transcription service
"""

# ============================================================================
# EXAMPLE 1: Basic Single File Transcription
# ============================================================================

from app.services.whisper_transcriber import get_transcriber

# Initialize transcriber
transcriber = get_transcriber(model="base", speed="fast")

# Transcribe a lecture video
result = transcriber.transcribe_single("lecture.mp4")

if result:
    print(f"📁 File: {result['filename']}")
    print(f"🗣️ Audio Language: {result['original_audio_language']}")
    print(f"📝 Text Language: {result['detected_text_language']}")
    print(f"⏱️ Duration: {result['duration']} seconds")
    print(f"\n📄 Transcription:\n{result['text'][:500]}...")


# ============================================================================
# EXAMPLE 2: High Accuracy Transcription (Important Content)
# ============================================================================

# For critical content: use large model + slow speed
transcriber_accurate = get_transcriber(model="large", speed="slow")

result_accurate = transcriber_accurate.transcribe_single("important_lecture.mp4")

if result_accurate:
    print(f"✅ High-accuracy transcription complete")
    print(f"Model: {result_accurate['model']} (best accuracy)")
    print(f"Text: {result_accurate['text']}")


# ============================================================================
# EXAMPLE 3: Quick Transcription (Fast Processing)
# ============================================================================

# For quick turnaround: use tiny/base model + fast speed
transcriber_fast = get_transcriber(model="base", speed="fast")

result_fast = transcriber_fast.transcribe_single("quick_video.mp4")

print(f"⚡ Processed in ~30-60 seconds")
print(f"Text preview: {result_fast['text'][:100]}...")


# ============================================================================
# EXAMPLE 4: Batch Processing Directory
# ============================================================================

transcriber = get_transcriber(model="base", speed="balanced")

# Process entire directory
results = transcriber.transcribe_batch("/path/to/lectures/")

print(f"📊 Batch Results:")
print(f"✅ Total files processed: {len(results)}")

for result in results:
    print(f"\n📁 {result['filename']}")
    print(f"   Language: {result['original_audio_language']}")
    print(f"   Characters: {len(result['text'])}")
    print(f"   Preview: {result['text'][:80]}...")


# ============================================================================
# EXAMPLE 5: Save Results in Multiple Formats
# ============================================================================

# Process
result = transcriber.transcribe_single("lecture.mp4")

if result:
    # Save as JSON (preserve all metadata)
    transcriber.save_results(
        result, 
        output_format="json",
        output_file="transcription.json"
    )
    
    # Save as TXT (readable format)
    transcriber.save_results(
        result,
        output_format="txt",
        output_file="transcription.txt"
    )
    
    # Save batch results as CSV
    transcriber.save_results(
        results,  # Multiple results
        output_format="csv",
        output_file="batch_transcriptions.csv"
    )


# ============================================================================
# EXAMPLE 6: Multilingual Processing
# ============================================================================

# Different languages auto-detected
files = [
    "english_lecture.mp4",
    "hindi_lecture.mp4",
    "tamil_lecture.mp4",
    "spanish_lecture.mp4"
]

transcriber = get_transcriber()

for file in files:
    result = transcriber.transcribe_single(file)
    if result:
        print(f"📁 {result['filename']}")
        print(f"   🗣️ Detected Language: {result['original_audio_language']}")
        print(f"   ✅ Text Language: {result['detected_text_language']}")


# ============================================================================
# EXAMPLE 7: Integration with Enhanced NLP Service
# ============================================================================

from app.services.whisper_transcriber import get_transcriber
from app.services.enhanced_nlp import process_lecture

# Step 1: Transcribe
transcriber = get_transcriber()
transcription = transcriber.transcribe_single("full_lecture.mp4")

# Step 2: Summarize & Extract Keywords
nlp_result = process_lecture(
    transcription["text"],
    compression_ratio=0.4,
    num_keywords=10
)

print(f"📄 Original Length: {len(transcription['text'])} characters")
print(f"📝 Summary Length: {len(nlp_result['summary'])} characters")
print(f"🔑 Keywords: {', '.join(nlp_result['keywords'][:5])}")


# ============================================================================
# EXAMPLE 8: Integration with Sentiment Analysis
# ============================================================================

from app.services.whisper_transcriber import get_transcriber
from app.services.sentiment_analysis import analyze_sentiment

# Transcribe
transcriber = get_transcriber()
result = transcriber.transcribe_single("speaker_video.mp4")

# Analyze emotional tone
sentiment = analyze_sentiment(result["text"])

print(f"📄 Content: {result['text'][:100]}...")
print(f"😊 Detected Emotion: {sentiment.get('emotion', 'neutral')}")
print(f"💯 Confidence: {sentiment.get('confidence', 'N/A')}")


# ============================================================================
# EXAMPLE 9: Integration with Translation
# ============================================================================

from app.services.whisper_transcriber import get_transcriber
from app.services.cultural_translator import translate_cultural

# Transcribe English lecture
transcriber = get_transcriber()
english_text = transcriber.transcribe_single("english_lecture.mp4")["text"]

# Translate to Hindi
hindi_translation = translate_cultural(english_text, target_lang="hi")

# Translate to Tamil
tamil_translation = translate_cultural(english_text, target_lang="ta")

print(f"🇬🇧 English: {english_text[:100]}...")
print(f"🇮🇳 Hindi: {hindi_translation[:100]}...")
print(f"🇮🇳 Tamil: {tamil_translation[:100]}...")


# ============================================================================
# EXAMPLE 10: Complete Analysis Pipeline
# ============================================================================

async def analyze_lecture_complete(video_path: str):
    """Complete lecture analysis pipeline."""
    
    print("🚀 Starting complete analysis pipeline...")
    
    # 1. Transcription
    print("\n1️⃣ Transcribing...")
    transcriber = get_transcriber(model="base", speed="balanced")
    transcription = transcriber.transcribe_single(video_path)
    if not transcription:
        return None
    
    # 2. NLP Processing
    print("2️⃣ Processing with NLP...")
    nlp_result = process_lecture(
        transcription["text"],
        compression_ratio=0.4,
        num_keywords=15
    )
    
    # 3. Sentiment Analysis
    print("3️⃣ Analyzing sentiment...")
    from app.services.sentiment_analysis import analyze_sentiment
    sentiment = analyze_sentiment(nlp_result["summary"])
    
    # 4. Translation
    print("4️⃣ Translating to Hindi...")
    from app.services.cultural_translator import translate_cultural
    hindi_summary = translate_cultural(nlp_result["summary"], "hi")
    
    print("\n✅ Analysis complete!")
    
    return {
        "metadata": {
            "file": transcription['filename'],
            "language": transcription['original_audio_language'],
            "duration": transcription['duration']
        },
        "transcription": transcription["text"][:500],
        "summary": nlp_result["summary"],
        "keywords": nlp_result["keywords"][:10],
        "sentiment": sentiment.get("emotion", "neutral"),
        "hindi_summary": hindi_summary[:500]
    }

# Usage (in async context):
# result = await analyze_lecture_complete("lecture.mp4")


# ============================================================================
# EXAMPLE 11: API Usage via HTTP
# ============================================================================

"""
# Single file transcription
curl -X POST http://localhost:8000/api/transcribe/single \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/audio.mp4",
    "model": "base",
    "speed": "fast"
  }'

# Batch processing
curl -X POST http://localhost:8000/api/transcribe/batch \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/path/to/audio/files",
    "model": "base",
    "speed": "balanced"
  }'

# Upload and transcribe
curl -X POST http://localhost:8000/api/transcribe/upload \
  -F "file=@lecture.mp4" \
  -F "model=base" \
  -F "speed=fast"

# Get service info
curl http://localhost:8000/api/transcribe/info

# Health check
curl http://localhost:8000/api/transcribe/health
"""

# Python requests example:
import requests

def transcribe_via_api(audio_path: str):
    """Call transcriber via HTTP API."""
    
    response = requests.post(
        "http://localhost:8000/api/transcribe/single",
        json={
            "file_path": audio_path,
            "model": "base",
            "speed": "fast"
        }
    )
    
    return response.json()

# Usage:
# result = transcribe_via_api("/path/to/audio.mp4")


# ============================================================================
# EXAMPLE 12: Production Setup with Error Handling
# ============================================================================

def transcribe_safely(audio_path: str, retries: int = 3) -> dict:
    """Transcribe with error handling and retries."""
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Validate file
    from pathlib import Path
    if not Path(audio_path).exists():
        logger.error(f"File not found: {audio_path}")
        return {"status": "error", "message": "File not found"}
    
    # Try transcription with retries
    for attempt in range(retries):
        try:
            transcriber = get_transcriber()
            result = transcriber.transcribe_single(audio_path)
            
            if result:
                logger.info(f"✅ Transcription succeeded")
                return {"status": "success", "data": result}
            else:
                logger.warning(f"Attempt {attempt + 1} returned None")
        
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed after {retries} attempts")
                return {"status": "error", "message": str(e)}
    
    return {"status": "error", "message": "Max retries exceeded"}

# Usage:
# result = transcribe_safely("audio.mp4")


# ============================================================================
# EXAMPLE 13: Batch Processing with Progress
# ============================================================================

def batch_transcribe_with_progress(directory: str, model: str = "base"):
    """Batch transcribe with progress tracking."""
    
    from pathlib import Path
    import json
    
    transcriber = get_transcriber(model=model, speed="balanced")
    
    # Find all audio files
    audio_files = []
    for ext in ['.mp3', '.mp4', '.wav', '.webm']:
        audio_files.extend(Path(directory).glob(f"**/*{ext}"))
    
    print(f"📁 Found {len(audio_files)} files\n")
    
    results = []
    
    for idx, audio_file in enumerate(audio_files, 1):
        print(f"[{idx}/{len(audio_files)}] {audio_file.name}...", end=" ")
        
        try:
            result = transcriber.transcribe_single(str(audio_file))
            
            if result:
                results.append(result)
                print(f"✅ ({len(result['text'])} chars)")
            else:
                print("⚠️ Failed")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Complete: {len(results)}/{len(audio_files)} succeeded")
    
    # Save results
    transcriber.save_results(results, "json", "batch_results.json")
    transcriber.save_results(results, "csv", "batch_results.csv")
    
    return results


# ============================================================================
# Running Examples
# ============================================================================

if __name__ == "__main__":
    print("🎤 Whisper Transcriber Pro - Examples")
    print("="*60)
    print("Choose examples to run above")
    print("Each example is independent and can be run separately")
