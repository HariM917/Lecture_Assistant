# 🎓 Multilingual Lecture Assistant

> AI-powered real-time lecture transcription, multi-language translation, keyword extraction, and intelligent summarization.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|------------|
| 🎤 **Speech-to-Text** | Real-time audio transcription via OpenAI Whisper with auto language detection |
| 🌍 **9-Language Translation** | Instant translation to Tamil, Hindi, Telugu, Kannada, Malayalam, German, Chinese, Japanese |
| 🏷️ **Keyword Extraction** | Automatic extraction of key concepts, technical terms, and formulas |
| ✨ **AI Summarization** | Intelligent lecture summaries using extractive and abstractive methods |
| 📊 **Live Analytics** | Real-time dashboard with processing metrics and keyword tracking |
| 🔌 **WebSocket** | Real-time updates for collaborative lecture sessions |

---

## 🏗️ Architecture

```
lecture-assistant/
├── backend/
│   ├── main.py                 # Entry point
│   ├── app/
│   │   ├── main.py             # FastAPI app factory
│   │   ├── core/
│   │   │   ├── config.py       # Environment-aware settings
│   │   │   ├── database.py     # SQLite/PostgreSQL dual support
│   │   │   └── dependencies.py # Service dependency injection
│   │   ├── models/
│   │   │   └── database.py     # SQLAlchemy ORM models
│   │   └── services/
│   │       ├── transcription.py    # Whisper / mock transcription
│   │       ├── translation.py      # Real / mock translation
│   │       ├── summarization.py    # BART / extractive summarization
│   │       ├── nlp_extraction.py   # Keyword & entity extraction
│   │       ├── whisper_service.py  # Full Whisper integration
│   │       └── cache.py           # Redis / in-memory cache
│   ├── api/routes/
│   │   ├── health.py           # Health & status endpoints
│   │   ├── sessions.py         # Session CRUD
│   │   ├── transcription.py    # Audio upload & transcription
│   │   ├── translation.py      # Translation endpoints
│   │   └── analysis.py         # Extraction & summarization
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Premium dark-mode UI
│   ├── styles.css              # Glassmorphism design system
│   ├── app.js                  # Application orchestrator
│   ├── api-client.js           # Backend communication
│   └── audio-recorder.js       # Microphone & waveform
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend dev server)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install core dependencies
pip install -r requirements.txt

# (Optional) Install ML dependencies for real AI features
pip install -r requirements-ml.txt

# Start the server
python main.py
```

The backend starts at **http://localhost:5000** with:
- 📚 API Docs: http://localhost:5000/api/docs
- 🔍 ReDoc: http://localhost:5000/api/redoc

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend starts at **http://localhost:3000**

### 3. Docker (Full Stack)

```bash
docker-compose up -d
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/lecture_assistant.db` | Database connection string |
| `MOCK_MODE` | `False` | Force mock services (no ML required) |
| `WHISPER_MODEL` | `base` | Whisper model size: tiny, base, small, medium, large |
| `DEBUG` | `True` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Service Modes

The app gracefully degrades based on available dependencies:

| Service | Full Mode | Fallback Mode |
|---------|-----------|---------------|
| Transcription | OpenAI Whisper | Demo text |
| Translation | Google Translate (free) | Static translations |
| Summarization | BART transformer | Extractive (TF-based) |
| NLP | spaCy + NLTK | Regex + frequency analysis |
| Database | PostgreSQL | SQLite |
| Cache | Redis | In-memory LRU |

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/lecture/sessions` | Create session |
| `GET` | `/api/lecture/sessions` | List sessions |
| `POST` | `/api/lecture/sessions/{id}/end` | End session |
| `POST` | `/api/lecture/sessions/{id}/transcribe` | Upload & transcribe audio |
| `POST` | `/api/lecture/transcriptions/{id}/translate-all` | Translate to all languages |
| `POST` | `/api/lecture/transcriptions/{id}/extract` | Extract keywords & entities |
| `POST` | `/api/lecture/sessions/{id}/summarize` | Generate session summary |

Full interactive docs at `/api/docs` (Swagger) or `/api/redoc`.

---

## 🛠️ Tech Stack

**Backend:** Python 3.11 · FastAPI · SQLAlchemy · Pydantic · Whisper · Transformers · spaCy  
**Frontend:** Vanilla JS · CSS3 Glassmorphism · Vite · Web Audio API  
**Infrastructure:** Docker · PostgreSQL · Redis · Nginx

---
## Contributors

Hari M, Rathinaprabha G,

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
