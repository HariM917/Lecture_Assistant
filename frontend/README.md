# Multilingual Lecture Assistant - Frontend

A modern, responsive web application for real-time lecture transcription, translation, and analysis.

## Features

✅ **Real-time Speech-to-Text**
- Microphone recording (5-second chunks)
- Audio file upload (WAV, MP3, WebM)
- Multiple language support

✅ **Multi-Language Translation**
- English → Tamil, Hindi, Telugu, Kannada, Malayalam
- Real-time WebSocket updates

✅ **Advanced NLP**
- Keyword extraction with frequency tracking
- Formula detection (equations, scientific notation, units)
- Entity recognition

✅ **Text Summarization**
- Abstractive summaries of lecture content
- Session-wide aggregation

✅ **Analytics Dashboard**
- Chunks processed counter
- Session duration tracking
- Unique keyword count
- Language coverage
- Top keywords list
- Real-time processing log

✅ **Responsive UI**
- Mobile-friendly design
- Tailwind CSS styling
- Dark mode support

## Installation

### 1. Prerequisites

- Docker Desktop (running the backend)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Microphone support for audio capture

### 2. Running Locally

No build step required! The frontend is a pure HTML/CSS/JavaScript application.

#### Option A: Using Python HTTP Server

```bash
cd frontend
python -m http.server 8080
```

Then open: http://localhost:8080

#### Option B: Using Node.js HTTP Server

```bash
cd frontend
npx http-server
```

#### Option C: Using Live Server (VS Code)

1. Install "Live Server" extension in VS Code
2. Right-click `index.html` → "Open with Live Server"

#### Option D: Direct File Access

Simply open `frontend/index.html` directly in your browser (limited functionality without HTTP server for CORS).

## Backend Setup

The frontend requires the FastAPI backend to be running:

```bash
cd multilingual-lecture-assistant
docker compose up --build
```

The backend will be available at `http://localhost:8000/docs` (API documentation).

## Usage

1. **Create a Session**
   - Enter lecture title, subject, and instructor name
   - Click "Start Session"

2. **Record or Upload Audio**
   - Select audio language from dropdown
   - Either:
     - Click "Start Recording" → "Stop Recording" (max 5 seconds)
     - Upload an audio file and click "Upload & Transcribe"

3. **View Results in Real-Time**
   - See transcript appear instantly
   - Watch translations appear for all languages
   - View extracted keywords and formulas
   - Get AI-generated summary

4. **Track Analytics**
   - Monitor chunks processed
   - Watch session duration
   - See unique keywords
   - Track covered languages

5. **End Session**
   - Click "End Session" when finished
   - Data is persisted in PostgreSQL

## File Structure

```
frontend/
├── index.html          # Main UI
├── app.js             # Application logic & event handling
├── api-client.js      # REST API & WebSocket integration
├── audio-recorder.js  # Microphone capture & Web Audio API
├── styles.css         # Tailwind + custom styling
├── README.md          # This file
└── .env.example       # (if needed for local API config)
```

## Key Classes

### `LectureAssistantApp`
Main application controller that manages:
- Session lifecycle
- Audio processing workflow
- Analytics updates
- UI state management

### `AudioRecorder`
Handles:
- Microphone access & permission handling
- Real-time waveform visualization
- Audio blob generation
- Recording duration tracking

### `APIClient`
Manages:
- REST API calls (create session, transcribe, translate, etc.)
- WebSocket connection with auto-reconnect
- Message routing & error handling
- Toast notifications

## Browser Compatibility

| Browser | Version | Support |
|---------|---------|---------|
| Chrome  | 80+     | ✅ Full |
| Firefox | 75+     | ✅ Full |
| Safari  | 13+     | ✅ Full |
| Edge    | 80+     | ✅ Full |

## Troubleshooting

### "Failed to connect to backend"
- Ensure Docker containers are running: `docker ps`
- Check backend is listening: `curl http://localhost:8000/health`
- Verify CORS settings in backend

### "Microphone access denied"
- Grant microphone permission in browser settings
- Use HTTPS or localhost for secure context
- Check privacy settings

### "WebSocket connection failed"
- Verify backend WebSocket is enabled
- Check firewall rules don't block port 8000
- Ensure no corporate proxy interferes

### Translations showing "-"
- Backend may be in mock mode
- Check backend logs: `docker logs multilingual-lecture-assistant-api-1`
- Verify Google Cloud credentials if using real translation

## API Endpoints Used

- `POST /api/lecture/sessions` - Create session
- `POST /api/lecture/sessions/{id}/end` - End session
- `POST /api/lecture/sessions/{id}/transcribe` - Transcribe audio
- `POST /api/lecture/transcriptions/{id}/translate-all` - Translate to all languages
- `POST /api/lecture/transcriptions/{id}/extract` - Extract keywords
- `POST /api/lecture/sessions/{id}/summarize` - Generate summary
- `WS /api/lecture/ws/{session_id}/{user_id}` - WebSocket for real-time updates
- `GET /health` - Backend health check

## Performance Tips

1. **Recording Quality**: Speak clearly, avoid background noise
2. **File Format**: MP3 or WebM recommended for smaller file size
3. **Browser Resources**: Close other tabs for better performance
4. **Backend**: Ensure PostgreSQL and Redis are running well

## Development

To extend the application:

1. **Add new language**: Update `audioLanguage` select in `index.html`
2. **Add new API endpoint**: Create method in `APIClient` class
3. **Add new feature**: Add event listener in `LectureAssistantApp.setupEventListeners()`
4. **Styling**: Modify `styles.css` or add Tailwind classes

## License

MIT

## Support

For issues or questions:
1. Check backend logs: `docker logs multilingual-lecture-assistant-api-1`
2. Check browser console: Press `F12` → Console tab
3. Review API documentation: http://localhost:8000/docs
