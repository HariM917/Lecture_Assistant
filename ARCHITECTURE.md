# 🎓 Multilingual Lecture Assistant - Architecture Guide

A professional real-time multilingual lecture processing system with speech-to-text, translation, summarization, and NLP capabilities.

## 📁 Project Structure

```
multilingual-lecture-assistant/
├── backend/                              # Backend FastAPI application
│   ├── app/
│   │   ├── main.py                      # FastAPI app factory
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py          # Dependency injection
│   │   │   └── routes/                  # API endpoints
│   │   │       ├── __init__.py
│   │   │       ├── health.py            # Health checks
│   │   │       ├── lecture.py           # Lecture management
│   │   │       ├── advanced.py          # Advanced features
│   │   │       ├── data_ingestion.py    # Data management
│   │   │       └── translation_training.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py                # Settings & configuration
│   │   │   ├── database.py              # Database setup
│   │   │   └── websocket_manager.py     # WebSocket management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── database.py              # SQLAlchemy models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py               # Pydantic models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── transcription.py         # Speech-to-text
│   │   │   ├── translation.py           # Translation service
│   │   │   ├── summarization.py         # Text summarization
│   │   │   └── nlp_extraction.py        # NLP features
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── session_repository.py    # Data access layer
│   ├── tests/                            # Test suite
│   ├── requirements.txt                  # Python dependencies
│   ├── .env.example                      # Environment template
│   └── run.py                            # Backend entry point
│
├── frontend/                             # Vue/React frontend application
│   ├── src/
│   │   ├── components/                   # Reusable components
│   │   ├── pages/                        # Page components
│   │   ├── utils/                        # Helper functions
│   │   ├── styles/                       # CSS/styling
│   │   ├── main.js                       # Entry point
│   │   └── api.js                        # API client
│   ├── public/                           # Static assets
│   ├── index.html                        # HTML template
│   ├── package.json                      # Node dependencies
│   ├── vite.config.js                    # Vite configuration
│   ├── .env.example                      # Environment template
│   └── README.md                         # Frontend documentation
│
├── docker-compose.yml                    # Multi-container orchestration
├── .env                                  # Environment variables
└── README.md                             # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- Python 3.9+ (for local development)
- Node.js 16+ (for frontend development)
- PostgreSQL (for production)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd multilingual-lecture-assistant

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker-compose up -d

# Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/api/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Copy environment file
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run backend server
python run.py
# Backend will be available at http://localhost:8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Copy environment file
cp .env.example .env

# Install dependencies
npm install

# Run development server
npm run dev
# Frontend will be available at http://localhost:3000
```

## 🏗️ Architecture Overview

### Backend Architecture

**Technology Stack:**
- FastAPI 0.104+ for REST API
- SQLAlchemy 2.0+ for ORM
- PostgreSQL for data persistence
- Redis for caching
- OpenAI Whisper for speech-to-text
- Hugging Face Transformers for NLP

**Key Components:**

1. **API Routes (`app/api/routes/`)**
   - Modular endpoint organization
   - RESTful conventions
   - WebSocket support

2. **Core Services (`app/core/`)**
   - Configuration management
   - Database connectivity
   - WebSocket management
   - Session handling

3. **Business Logic (`app/services/`)**
   - Speech-to-text transcription
   - Multi-language translation
   - Text summarization
   - NLP extraction (keywords, formulas)

4. **Data Access (`app/repositories/`)**
   - Session management
   - Transcription storage
   - Translation records
   - Summary persistence

5. **Data Models (`app/models/`)**
   - LectureSession
   - TranscriptionNote
   - Translation
   - Summary
   - Insight
   - StudentNote

### Frontend Architecture

**Technology Stack:**
- HTML5, CSS3, JavaScript
- Fetch API for HTTP requests
- WebSocket for real-time updates
- Vite for dev build tool

**Key Components:**

1. **Pages (`src/pages/`)**
   - Dashboard
   - Lecture viewer
   - Settings

2. **Components (`src/components/`)**
   - Audio recorder
   - Transcription display
   - Translation panel
   - Summary viewer
   - Insights display

3. **Utilities (`src/utils/`)**
   - API client configuration
   - WebSocket manager
   - Helper functions

## 📡 API Endpoints

### Health & Status
- `GET /` - Root information
- `GET /api/health/` - Health check
- `GET /api/health/live` - Liveness probe
- `GET /api/health/ready` - Readiness probe
- `GET /api/v1/status` - API status

### Lectures
- `GET /api/lectures/` - List lectures
- `POST /api/lectures/` - Create lecture
- `GET /api/lectures/{id}` - Get lecture details
- `WebSocket /ws/lecture/{id}` - Real-time updates

### Transcription
- `POST /api/transcribe/` - Transcribe audio
- `GET /api/transcriptions/{id}` - Get transcription

### Translation
- `POST /api/translate/` - Translate text
- `GET /api/translations/{id}` - Get translation

### Summarization
- `POST /api/summarize/` - Summarize text
- `GET /api/summaries/{id}` - Get summary

### NLP
- `POST /api/nlp/extract` - Extract keywords/formulas
- `GET /api/nlp/insights/{id}` - Get insights

## 🔄 Integration Points

### Frontend ↔ Backend Communication

1. **REST APIs**
   - HTTP requests for CRUD operations
   - Request/response with JSON payloads
   - Error handling with status codes

2. **WebSockets**
   - Real-time transcription updates
   - Live translation streaming
   - Summary notifications
   - Insights broadcasting

3. **CORS Configuration**
   - Enabled for frontend URL
   - Credentials supported
   - All methods and headers allowed

### Service Integration

```
Audio Input
    ↓
Whisper Transcriber → Transcription Service
    ↓
Translation Service → Multi-language output
    ↓
Summarization Service → Key points extraction
    ↓
NLP Service → Keywords & Formulas
    ↓
WebSocket Broadcasting → Real-time UI updates
    ↓
Database Storage → Persistence
```

## 🔐 Security Features

- CORS middleware for cross-origin requests
- TrustedHost middleware for host validation
- Database connection pooling
- Environment-based configuration
- Request/response validation with Pydantic
- Error handling and logging

## 📊 Database Schema

### Tables
- `lecture_sessions` - Lecture metadata
- `transcription_notes` - Audio transcriptions
- `translations` - Translated content
- `summaries` - Abstractive summaries
- `insights` - Extracted keywords/formulas
- `student_notes` - User annotations

## 🧪 Testing

Run tests from the backend directory:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_transcription.py

# Run with coverage
pytest --cov=app tests/
```

## 📦 Deployment

### Docker Deployment
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create `.env` file with:
```
DATABASE_URL=postgresql://user:password@db:5432/lecture
REDIS_URL=redis://redis:6379/0
FRONTEND_URL=http://frontend:3000
DEBUG=False
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -am 'Add feature'`
3. Push branch: `git push origin feature/name`
4. Submit pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- Documentation: See individual README files in backend/ and frontend/
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## 🎯 Roadmap

- [ ] Advanced caching layer optimization
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration features
- [ ] Custom model fine-tuning
- [ ] Advanced analytics dashboard
- [ ] Multi-language UI support
