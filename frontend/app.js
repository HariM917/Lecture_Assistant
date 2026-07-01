// Main Application
class LectureAssistantApp {
    constructor() {
        this.recorder = new AudioRecorder();
        this.api = new APIClient();
        this.sessionActive = false;
        this.sessionStartTime = null;
        this.allKeywords = {};
        this.processedLanguages = new Set();
        this.chunkCount = 0;
        this.sessionDurationInterval = null;
        this.lastTranscriptionId = null;
        this.isProcessing = false;
    }

    async init() {
        console.log('🚀 Initializing Lecture Assistant Application...');
        console.log(`📡 Backend URL: ${this.api.baseUrl}`);
        console.log(`🔗 WebSocket URL: ${this.api.wsUrl}`);
        this.addLog('Initializing application...');
        
        try {
            // Check backend health
            this.addLog(`🔍 Checking backend connection at ${this.api.baseUrl}...`);
            console.log(`🔍 About to check health at: ${this.api.baseUrl}/health`);
            const isHealthy = await this.api.checkHealth();
            
            if (!isHealthy) {
                this.updateConnectionStatus(false, `❌ Failed to connect to backend at ${this.api.baseUrl}`);
                this.addLog(`❌ Backend connection failed - URL: ${this.api.baseUrl}`);
                console.error(`❌ Backend not responding at ${this.api.baseUrl}`);
                return;
            }
            this.updateConnectionStatus(true);
            this.addLog(`✅ Backend connected at ${this.api.baseUrl}`);
            console.log(`✅ Backend healthy at ${this.api.baseUrl}`);

            // Initialize microphone
            const micReady = await this.recorder.init();
            if (!micReady) {
                console.warn('⚠️ Microphone not available');
                this.addLog('⚠️ Microphone not available');
            } else {
                this.addLog('✅ Microphone initialized');
            }

            this.setupEventListeners();
            this.displaySystemInfo();
            console.log('✅ Application ready');
            this.addLog('✅ Application ready');
        } catch (error) {
            console.error('❌ Initialization error:', error);
            this.addLog(`❌ Init error: ${error.message}`);
        }
    }

    displaySystemInfo() {
        const info = `
🖥️  SYSTEM INFORMATION:
═══════════════════════════════════════
Backend Connection:
  📡 URL: ${this.api.baseUrl}
  🟢 Status: Connected
  ✅ Health: OK
  📚 API Docs: ${this.api.baseUrl}/api/docs
  
Frontend Configuration:
  🎨 Status: Running on port 3000
  📍 WebSocket: ${this.api.wsUrl}
  ✅ Status: Operational
  
System Features:
  🗣️  Language Support: 9 languages (EN, TA, HI, TE, KN, ML, DE, ZH, JA)
  🎤 Transcription: Enabled
  🌍 Translation: Enabled
  🏷️  Keyword Extraction: Enabled
  ✨ Summarization: Enabled
═══════════════════════════════════════
        `;
        this.addLog(info);
    }

    setupEventListeners() {
        // Session Management
        document.getElementById('createSessionBtn').addEventListener('click', () => this.createSession());
        document.getElementById('endSessionBtn').addEventListener('click', () => this.endSession());

        // Recording
        document.getElementById('startRecordBtn').addEventListener('click', () => this.startRecording());
        document.getElementById('stopRecordBtn').addEventListener('click', () => this.stopRecording());

        // File Upload
        document.getElementById('uploadAudioBtn').addEventListener('click', () => this.uploadAudio());

        // WebSocket message handler
        this.api.onMessage((message) => this.handleWebSocketMessage(message));
    }

    async createSession() {
        const title = document.getElementById('lectureTitle').value.trim();
        const subject = document.getElementById('subject').value.trim();
        const instructor = document.getElementById('instructor').value.trim();

        if (!title || !subject || !instructor) {
            this.recorder.showToast('❌ Please fill in all session details', 'error');
            this.addLog('⚠️ Missing session details');
            return;
        }

        try {
            this.addLog('📝 Creating new session...');
            const session = await this.api.createSession(title, subject, instructor);
            
            if (!session || !session.id) {
                throw new Error('Invalid session response');
            }

            this.api.sessionId = session.id;
            this.sessionActive = true;
            this.sessionStartTime = Date.now();
            this.chunkCount = 0;
            this.allKeywords = {};
            this.processedLanguages.clear();

            // Update UI
            document.getElementById('createSessionBtn').disabled = true;
            document.getElementById('endSessionBtn').disabled = false;
            document.getElementById('sessionInfo').innerHTML = `
                <div class="text-green-600 font-bold">✅ Session Created</div>
                <div class="text-sm">ID: ${session.id.substring(0, 12)}...</div>
                <div class="text-sm">Title: ${session.title}</div>
                <div class="text-sm">Subject: ${session.subject}</div>
            `;

            // Start session duration timer
            this.startSessionDurationTimer();

            // Connect WebSocket
            await this.api.connectWebSocket();

            this.recorder.showToast(`✅ Session "${title}" created`, 'success');
            this.addLog(`✅ Session created: ${title} (${session.id.substring(0, 8)}...)`);
        } catch (error) {
            this.recorder.showToast(`❌ Failed: ${error.message}`, 'error');
            this.addLog(`❌ Session creation failed: ${error.message}`);
            console.error('Create session error:', error);
        }
    }

    async endSession() {
        if (!this.sessionActive) return;

        try {
            this.addLog('📋 Ending session...');
            await this.api.endSession();
            this.sessionActive = false;
            
            // Update UI
            document.getElementById('createSessionBtn').disabled = false;
            document.getElementById('endSessionBtn').disabled = true;
            document.getElementById('sessionInfo').textContent = '⚪ No active session';

            if (this.sessionDurationInterval) {
                clearInterval(this.sessionDurationInterval);
            }

            this.api.disconnect();
            this.recorder.showToast('✅ Session ended', 'success');
            this.addLog('✅ Session ended successfully');
        } catch (error) {
            this.recorder.showToast(`❌ Failed: ${error.message}`, 'error');
            this.addLog(`❌ End session failed: ${error.message}`);
        }
    }

    async startRecording() {
        if (!this.sessionActive) {
            this.recorder.showToast('❌ Create a session first', 'error');
            return;
        }

        const started = this.recorder.start();
        if (started) {
            document.getElementById('startRecordBtn').disabled = true;
            document.getElementById('stopRecordBtn').disabled = false;
            document.getElementById('recordingStatus').textContent = '🔴 Recording... (max 5s)';
            this.recorder.showToast('🎙️ Recording started', 'info');
            this.addLog('🎙️ Recording started');

            // Auto-stop after 5 seconds
            setTimeout(() => {
                if (this.recorder.isRecording) {
                    this.stopRecording();
                }
            }, 5000);
        }
    }

    async stopRecording() {
        const audioBlob = this.recorder.stop();
        document.getElementById('startRecordBtn').disabled = false;
        document.getElementById('stopRecordBtn').disabled = true;
        document.getElementById('recordingStatus').textContent = `⏹️ Stopped (${this.recorder.getRecordingDuration()}s)`;

        if (audioBlob) {
            this.addLog('⏹️ Recording stopped, processing...');
            this.recorder.showToast('⏹️ Processing audio...', 'info');
            await this.processAudio(audioBlob);
        }
    }

    async uploadAudio() {
        if (!this.sessionActive) {
            this.recorder.showToast('❌ Create a session first', 'error');
            return;
        }

        const fileInput = document.getElementById('audioFile');
        if (!fileInput.files.length) {
            this.recorder.showToast('❌ Select an audio file', 'error');
            return;
        }

        const audioBlob = fileInput.files[0];
        this.addLog(`📁 Uploading file: ${audioBlob.name} (${(audioBlob.size / 1024).toFixed(2)} KB)`);
        this.recorder.showToast('📁 Processing audio file...', 'info');
        await this.processAudio(audioBlob);
    }

    async processAudio(audioBlob) {
        if (this.isProcessing) {
            this.addLog('⚠️ Already processing, please wait...');
            return;
        }

        this.isProcessing = true;
        try {
            const language = document.getElementById('audioLanguage').value;
            this.addLog(`\n${'='.repeat(60)}`);
            this.addLog(`📤 Starting audio processing (Language: ${language})`);
            this.addLog(`${'='.repeat(60)}`);

            // Step 1: TRANSCRIBE
            this.addLog(`\n[1/4] 🎤 Transcribing audio...`);
            const transcriptResult = await this.api.transcribeAudio(audioBlob, language);
            
            if (!transcriptResult || !transcriptResult.id) {
                throw new Error('No transcription response received');
            }

            this.lastTranscriptionId = transcriptResult.id;
            this.chunkCount++;

            const transcript = transcriptResult.text || 'No transcript';
            const confidence = (transcriptResult.confidence * 100).toFixed(1);
            
            document.getElementById('transcript').innerHTML = `
                <div class="text-sm text-gray-600 mb-2">
                    Confidence: ${confidence}% | Duration: ${transcriptResult.duration || 'N/A'}s
                </div>
                <p class="leading-relaxed">${this.escapeHtml(transcript)}</p>
            `;
            
            this.addLog(`✅ Transcription Complete`);
            this.addLog(`   ID: ${transcriptResult.id.substring(0, 12)}...`);
            this.addLog(`   Text: ${transcript.substring(0, 80)}...`);
            this.addLog(`   Confidence: ${confidence}%`);
            this.recorder.showToast('✅ Transcription done! Translating...', 'success');

            // Step 2: TRANSLATE
            this.addLog(`\n[2/4] 🌍 Translating to all languages...`);
            try {
                const translationsResp = await this.api.translateToAllLanguages(this.lastTranscriptionId);
                const translations = translationsResp.translations || {};
                const langCount = Object.keys(translations).length;
                
                this.addLog(`✅ Translation Complete`);
                this.addLog(`   Languages: ${langCount}`);
                
                // Update translation cards with actual translations
                Object.entries(translations).forEach(([lang, text]) => {
                    const elem = document.getElementById(`translation-${lang}`);
                    if (elem) {
                        elem.innerHTML = `
                            <div class="text-xs text-gray-500 mb-1">Language: ${lang.toUpperCase()}</div>
                            <p class="text-sm leading-relaxed">${this.escapeHtml(text.substring(0, 150))}...</p>
                        `;
                        this.processedLanguages.add(lang);
                    }
                });
                
                this.addLog(`   Available: ${Object.keys(translations).join(', ')}`);
                this.recorder.showToast('✅ Translations done! Extracting keywords...', 'success');
            } catch (e) {
                this.addLog(`❌ Translation failed: ${e.message}`, 'warning');
                console.error('Translation error:', e);
            }

            // Step 3: EXTRACT KEYWORDS
            this.addLog(`\n[3/4] 🏷️ Extracting keywords and formulas...`);
            try {
                const insights = await this.api.extractKeywords(this.lastTranscriptionId);
                const keywords = insights.keywords || [];
                const formulas = insights.formulas || [];
                
                this.displayKeywordsAndFormulas(keywords, formulas);
                
                this.addLog(`✅ Extraction Complete`);
                this.addLog(`   Keywords: ${keywords.length}`);
                this.addLog(`   Formulas: ${formulas.length}`);
                this.addLog(`   Keywords: ${keywords.slice(0, 5).join(', ')}...`);
                this.recorder.showToast('✅ Keywords extracted! Summarizing...', 'success');
            } catch (e) {
                this.addLog(`❌ Extraction failed: ${e.message}`, 'warning');
                console.error('Extraction error:', e);
            }

            // Step 4: SUMMARIZE
            this.addLog(`\n[4/4] ✨ Creating session summary...`);
            try {
                const summaryResp = await this.api.summarizeSession();
                const summaryText = summaryResp.summary || 'No summary available';
                const summaryLines = summaryText.split('\n').length;
                
                document.getElementById('summary').innerHTML = `
                    <div class="text-sm text-gray-600 mb-2">
                        Summary Length: ${summaryText.length} characters | ${summaryLines} lines
                    </div>
                    <p class="leading-relaxed whitespace-pre-wrap">${this.escapeHtml(summaryText)}</p>
                `;
                
                this.addLog(`✅ Summary Complete`);
                this.addLog(`   Length: ${summaryText.length} characters`);
                this.addLog(`   Preview: ${summaryText.substring(0, 100)}...`);
                this.recorder.showToast('✅ Processing complete!', 'success');
            } catch (e) {
                this.addLog(`❌ Summarization failed: ${e.message}`, 'warning');
                console.error('Summary error:', e);
            }

            this.updateAnalytics();
            this.addLog(`\n${'='.repeat(60)}`);
            this.addLog(`✅ ALL PROCESSING COMPLETE`);
            this.addLog(`${'='.repeat(60)}\n`);
        } catch (error) {
            console.error('Processing error:', error);
            this.recorder.showToast(`❌ Error: ${error.message}`, 'error');
            this.addLog(`\n❌ PROCESSING FAILED: ${error.message}`);
            this.addLog(`Error details: ${error.toString()}\n`);
        } finally {
            this.isProcessing = false;
        }
    }

    displayKeywordsAndFormulas(keywords, formulas) {
        const container = document.getElementById('keywords');
        const content = [];

        // Add keywords
        if (keywords && Array.isArray(keywords)) {
            keywords.forEach(keyword => {
                this.allKeywords[keyword] = (this.allKeywords[keyword] || 0) + 1;
                content.push(`
                    <span class="inline-block bg-gradient-to-r from-green-100 to-green-200 text-green-800 px-3 py-1 rounded-full text-sm font-medium m-1">
                        🏷️ ${this.escapeHtml(keyword)}
                    </span>
                `);
            });
        }

        // Add formulas
        if (formulas && Array.isArray(formulas)) {
            formulas.forEach(formula => {
                if (formula.formula) {
                    content.push(`
                        <span class="inline-block bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm font-medium m-1">
                            📐 ${this.escapeHtml(formula.formula)}
                        </span>
                    `);
                }
            });
        }

        container.innerHTML = content.length ? content.join('') : `
            <p class="text-gray-500 italic text-center py-4">
                No keywords found yet. Process audio to extract keywords.
            </p>
        `;
    }

    updateAnalytics() {
        // Chunks
        document.getElementById('chunksCount').textContent = this.chunkCount || 0;

        // Keywords
        const uniqueKeywords = Object.keys(this.allKeywords).length;
        document.getElementById('keywordCount').textContent = uniqueKeywords || 0;

        // Languages
        document.getElementById('languageCount').textContent = this.processedLanguages.size || 0;

        // Top Keywords
        const topKeywords = Object.entries(this.allKeywords)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([kw, count]) => `
                <div class="text-sm text-gray-700 mb-1">
                    • <strong>${this.escapeHtml(kw)}</strong> <span class="text-gray-500">(×${count})</span>
                </div>
            `)
            .join('');

        document.getElementById('topKeywordsList').innerHTML = topKeywords || `
            <p class="text-sm text-gray-500 italic">No keywords yet</p>
        `;
        
        this.addLog(`📊 Analytics Updated: ${uniqueKeywords} keywords | ${this.processedLanguages.size} languages | ${this.chunkCount} chunks`);
    }

    startSessionDurationTimer() {
        this.sessionDurationInterval = setInterval(() => {
            if (this.sessionStartTime) {
                const elapsed = Math.floor((Date.now() - this.sessionStartTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                document.getElementById('sessionDuration').textContent = 
                    minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
            }
        }, 1000);
    }

    handleWebSocketMessage(message) {
        console.log('WebSocket message:', message);
        // Messages from backend are logged in processing log
        if (message.type === 'transcription') {
            this.addLog('📨 Received transcription update');
        } else if (message.type === 'translation') {
            this.addLog('📨 Received translation update');
        }
    }

    addLog(message, type = 'info') {
        const logContainer = document.getElementById('processingLog');
        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = `text-xs ${
            type === 'error' ? 'text-red-600' : type === 'warning' ? 'text-yellow-600' : 'text-gray-600'
        }`;
        entry.textContent = `[${timestamp}] ${message}`;
        logContainer.insertBefore(entry, logContainer.firstChild);
        
        // Keep only last 20 logs
        while (logContainer.children.length > 20) {
            logContainer.removeChild(logContainer.lastChild);
        }
    }

    updateConnectionStatus(connected, message = null) {
        const statusDiv = document.getElementById('connectionStatus');
        const connectedDiv = document.getElementById('connectedIndicator');

        if (connected) {
            statusDiv.classList.add('hidden');
            connectedDiv.classList.remove('hidden');
        } else {
            statusDiv.classList.remove('hidden');
            connectedDiv.classList.add('hidden');
            if (message) {
                document.getElementById('statusText').textContent = message;
            }
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, starting application...');
    const app = new LectureAssistantApp();
    app.init().catch(console.error);
});
