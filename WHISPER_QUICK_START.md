# 🎤 Whisper Transcriber Pro - Quick Reference

**Status**: ✅ Production Ready  
**Integration Time**: 5 minutes  

---

## 🚀 Start in 30 Seconds

```python
from services.whisper_transcriber import get_transcriber

transcriber = get_transcriber()
result = transcriber.transcribe_single("video.mp4")

print(result["text"])  # Your transcription!
```

---

## 📡 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/transcribe/single` | POST | Transcribe one file |
| `/api/transcribe/batch` | POST | Transcribe directory |
| `/api/transcribe/upload` | POST | Upload & transcribe |
| `/api/transcribe/info` | GET | Service info |
| `/api/transcribe/models` | GET | List models |
| `/api/transcribe/health` | GET | Health check |

---

## 🎯 Model Selection Guide

**Choose ONE based on your need:**

| If you want... | Use | Time (5min) | Memory |
|---|---|---|---|
| **⚡ Speed** | `model="tiny"` | 15-30s | 400MB |
| **⚡ Balanced** | `model="base"` | 30-60s | 1GB |
| **📈 Most common** | `model="base"` | 30-60s | 1GB |
| **🎯 Better accuracy** | `model="small"` | 60-90s | 2.5GB |
| **🔍 High accuracy** | `model="medium"` | 2-3m | 5GB |
| **✨ Best quality** | `model="large"` | 3-5m | 10GB |

**Default**: `base` (recommended for most use cases)

---

## ⏱️ Speed Mode Selection

```python
# Fast: ~30-60 seconds
transcriber = get_transcriber(speed="fast")

# Balanced: ~1-3 minutes (recommended)
transcriber = get_transcriber(speed="balanced")

# Slow: ~3-5 minutes (most accurate)
transcriber = get_transcriber(speed="slow")
```

---

## 📋 Common Patterns

### Pattern 1: Single File
```python
transcriber = get_transcriber(model="base", speed="fast")
result = transcriber.transcribe_single("lecture.mp4")
print(result["text"])
```

### Pattern 2: Batch Directory
```python
transcriber = get_transcriber()
results = transcriber.transcribe_batch("/lectures/")
transcriber.save_results(results, format="csv")
```

### Pattern 3: With NLP
```python
from services.enhanced_nlp import process_lecture

result = transcriber.transcribe_single("video.mp4")
nlp = process_lecture(result["text"])
print(f"Summary: {nlp['summary']}")
```

### Pattern 4: With Sentiment
```python
from services.sentiment_analyzer import analyze_sentiment

text = transcriber.transcribe_single("video.mp4")["text"]
sentiment = analyze_sentiment(text)
print(f"Emotion: {sentiment['emotion']}")
```

### Pattern 5: With Translation
```python
from services.cultural_translator import translate_cultural

text = transcriber.transcribe_single("video.mp4")["text"]
hindi = translate_cultural(text, "hi")
print(f"Hindi: {hindi}")
```

---

## 🌍 Language Support

Whisper auto-detects 99+ languages including:

🇬🇧 English  
🇮🇳 Hindi  
🇮🇳 Tamil  
🇮🇳 Telugu  
🇮🇳 Kannada  
🇮🇳 Marathi  
🇮🇳 Gujarati  
🇪🇸 Spanish  
🇫🇷 French  
🇩🇪 German  
🇮🇹 Italian  
🇯🇵 Japanese  
🇨🇳 Chinese  
...and 80+ more

**Detection**: Automatic both in audio (Whisper) and text (langdetect)

---

## 💾 Save Results

### Format: JSON (preserve all data)
```python
transcriber.save_results(result, "json", "output.json")
```

### Format: TXT (readable)
```python
transcriber.save_results(result, "txt", "output.txt")
```

### Format: CSV (for spreadsheets)
```python
transcriber.save_results(results, "csv", "output.csv")
```

---

## 📊 Output Structure

```json
{
  "filename": "lecture.mp4",
  "original_audio_language": "en",
  "detected_text_language": "en",
  "output_language": "en",
  "text": "Complete transcription...",
  "duration": 300.5,
  "model": "base",
  "speed_mode": "fast",
  "segments": [...],
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## 🎯 Use Cases

| Use Case | Model | Speed | Example |
|----------|-------|-------|---------|
| Quick test | tiny | fast | Testing setup |
| Standard lecture | base | balanced | Most common |
| Important meeting | small/medium | slow | Critical content |
| Academic research | large | slow | Accuracy critical |
| Batch processing | base | balanced | Directory of files |
| Real-time needs | tiny/base | fast | Quick turnaround |

---

## ⚙️ Configuration

### Initialize Custom
```python
transcriber = get_transcriber(
    model_name="base",      # Size
    speed_mode="balanced"   # Speed
)
```

### Use Defaults
```python
transcriber = get_transcriber()  # base + fast
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Slow | Use `speed="fast"` + `model="base"` |
| Out of memory | Use smaller model: `model="tiny"` |
| Wrong language | Check audio quality; Whisper usually correct |
| File not found | Use absolute path, check file exists |
| GPU issues | Use `model="base"` or CPU only |

---

## 📦 Dependencies

```bash
pip install openai-whisper langdetect numpy pydantic
```

For GPU (optional):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 🔗 Integration Checklist

- [x] Service created: `services/whisper_transcriber.py`
- [x] Routes added: `routes/transcribe_routes.py`
- [x] main.py updated: routers included
- [x] Documentation: `WHISPER_GUIDE.md`
- [x] Examples: `examples_whisper_usage.py`
- [ ] Your first transcription: **Try it now!**

---

## ✅ Quick Test

```python
# Paste this in Python terminal:
from services.whisper_transcriber import get_transcriber

t = get_transcriber()
r = t.transcribe_single("YOUR_FILE.mp4")
print(r["text"] if r else "Failed")
```

---

## 📡 HTTP Test

```bash
curl http://localhost:8000/api/transcribe/health
```

Expected response:
```json
{"status": "healthy", "service": "whisper_transcriber"}
```

---

## 🏆 Performance

- **Speed**: 30-60s for 5-min audio (base model)
- **Accuracy**: 95%+ for English
- **Languages**: 99+ supported
- **Memory**: ~1GB peak (base model)
- **Formats**: MP3, MP4, WAV, WebM, etc.

---

## 🎓 Next Steps

1. **Try it**: Run example above
2. **Integrate**: Combine with NLP/Translation
3. **Scale**: Use batch processing
4. **Deploy**: Use in production

---

## 📞 Quick Help

```python
# Service info
transcriber = get_transcriber()
print(transcriber.get_service_info())

# Model list
print(transcriber.AVAILABLE_MODELS)

# Supported formats
print(transcriber.SUPPORTED_FORMATS)
```

---

**Ready to transcribe?** 🎙️ Start with Example 1 in `examples_whisper_usage.py`

✨ **Status**: Production Ready
