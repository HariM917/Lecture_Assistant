/**
 * Lecture Assistant — Main Application
 * Orchestrates session management, audio processing pipeline, and UI updates.
 */
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

    // ── Initialization ────────────────────────────────────────────
    async init() {
        this.addLog('Initializing application...');

        try {
            // Check backend
            const healthy = await this.api.checkHealth();

            if (!healthy) {
                this.setConnectionStatus('error', 'Backend offline');
                this.addLog('Backend not responding — check if server is running', 'error');
                return;
            }

            this.setConnectionStatus('connected', 'Connected');
            this.addLog('Backend connected');

            // Init microphone
            const micReady = await this.recorder.init();
            this.addLog(micReady ? 'Microphone ready' : 'Microphone unavailable', micReady ? '' : 'error');

            this.setupEventListeners();
            this.addLog('Application ready', 'success');
        } catch (error) {
            this.addLog(`Init error: ${error.message}`, 'error');
            this.setConnectionStatus('error', 'Error');
        }
    }

    // ── Event Listeners ───────────────────────────────────────────
    setupEventListeners() {
        // Session
        document.getElementById('createSessionBtn').addEventListener('click', () => this.createSession());
        document.getElementById('endSessionBtn').addEventListener('click', () => this.endSession());

        // Recording
        document.getElementById('startRecordBtn').addEventListener('click', () => this.startRecording());
        document.getElementById('stopRecordBtn').addEventListener('click', () => this.stopRecording());

        // Upload
        document.getElementById('uploadAudioBtn').addEventListener('click', () => this.uploadAudio());

        // Drag & drop
        const dropZone = document.getElementById('uploadZone');
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
            dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragover');
                const file = e.dataTransfer.files[0];
                if (file) document.getElementById('audioFile').files = e.dataTransfer.files;
            });
        }

        // WebSocket
        this.api.onMessage((msg) => this.handleWSMessage(msg));
    }

    // ── Connection Status ─────────────────────────────────────────
    setConnectionStatus(status, label) {
        const dot = document.getElementById('statusDot');
        const lbl = document.getElementById('statusLabel');
        dot.className = `status-dot ${status}`;
        lbl.textContent = label;
    }

    // ── Session Management ────────────────────────────────────────
    async createSession() {
        const title = document.getElementById('lectureTitle').value.trim();
        const subject = document.getElementById('subject').value.trim();
        const instructor = document.getElementById('instructor').value.trim();

        if (!title || !subject || !instructor) {
            this.recorder.showToast('Please fill in all fields', 'error');
            return;
        }

        try {
            this.addLog('Creating session...');
            const session = await this.api.createSession(title, subject, instructor);

            if (!session?.id) throw new Error('Invalid session response');

            this.api.sessionId = session.id;
            this.sessionActive = true;
            this.sessionStartTime = Date.now();
            this.chunkCount = 0;
            this.allKeywords = {};
            this.processedLanguages.clear();

            // UI updates
            document.getElementById('createSessionBtn').disabled = true;
            document.getElementById('endSessionBtn').disabled = false;
            document.getElementById('sessionStatus').innerHTML =
                `<span style="color: var(--accent-green)">● Active</span> — ${session.title}`;

            this.startDurationTimer();

            // Try WebSocket (non-blocking)
            this.api.connectWebSocket().catch(() => {});

            this.recorder.showToast(`Session "${title}" started`, 'success');
            this.addLog(`Session started: ${title}`, 'success');
        } catch (error) {
            this.recorder.showToast(`Failed: ${error.message}`, 'error');
            this.addLog(`Session creation failed: ${error.message}`, 'error');
        }
    }

    async endSession() {
        if (!this.sessionActive) return;

        try {
            await this.api.endSession();
            this.sessionActive = false;

            document.getElementById('createSessionBtn').disabled = false;
            document.getElementById('endSessionBtn').disabled = true;
            document.getElementById('sessionStatus').textContent = 'Create a session to begin';

            if (this.sessionDurationInterval) clearInterval(this.sessionDurationInterval);
            this.api.disconnect();

            this.recorder.showToast('Session ended', 'success');
            this.addLog('Session ended', 'success');
        } catch (error) {
            this.recorder.showToast(`Failed: ${error.message}`, 'error');
        }
    }

    // ── Recording ─────────────────────────────────────────────────
    startRecording() {
        if (!this.sessionActive) {
            this.recorder.showToast('Start a session first', 'error');
            return;
        }

        if (this.recorder.start()) {
            document.getElementById('startRecordBtn').disabled = true;
            document.getElementById('stopRecordBtn').disabled = false;
            this.addLog('Recording started');

            // Auto-stop after 30 seconds
            setTimeout(() => {
                if (this.recorder.isRecording) this.stopRecording();
            }, 30000);
        }
    }

    async stopRecording() {
        const blob = this.recorder.stop();
        document.getElementById('startRecordBtn').disabled = false;
        document.getElementById('stopRecordBtn').disabled = true;

        if (blob) {
            this.addLog(`Recording stopped (${this.recorder.getRecordingDuration()}s)`);
            await this.processAudio(blob);
        }
    }

    // ── Upload ────────────────────────────────────────────────────
    async uploadAudio() {
        if (!this.sessionActive) {
            this.recorder.showToast('Start a session first', 'error');
            return;
        }

        const fileInput = document.getElementById('audioFile');
        if (!fileInput.files.length) {
            this.recorder.showToast('Select an audio file', 'error');
            return;
        }

        const file = fileInput.files[0];
        this.addLog(`Uploading: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`);
        await this.processAudio(file);
    }

    // ── Processing Pipeline ───────────────────────────────────────
    async processAudio(audioBlob) {
        if (this.isProcessing) {
            this.addLog('Already processing, please wait...', 'error');
            return;
        }

        this.isProcessing = true;
        const language = document.getElementById('audioLanguage').value;
        this.resetPipeline();

        try {
            // Step 1: TRANSCRIBE
            this.setStepActive('transcribe');
            this.addLog('[1/4] Transcribing audio...');

            const result = await this.api.transcribeAudio(audioBlob, language);
            if (!result?.id) throw new Error('Transcription failed');

            this.lastTranscriptionId = result.id;
            this.chunkCount++;

            const text = result.text || '';
            const confidence = ((result.confidence || 0) * 100).toFixed(1);

            document.getElementById('transcriptMeta').textContent =
                `Confidence: ${confidence}% · Duration: ${result.duration || 'N/A'}s · Language: ${(result.language || language).toUpperCase()}`;
            document.getElementById('transcript').innerHTML =
                `<p>${this.escapeHtml(text)}</p>`;

            this.setStepCompleted('transcribe');
            this.addLog('Transcription complete', 'success');

            // Step 2: TRANSLATE
            this.setStepActive('translate');
            this.addLog('[2/4] Translating to all languages...');

            try {
                const transResp = await this.api.translateToAllLanguages(result.id);
                const translations = transResp.translations || {};

                Object.entries(translations).forEach(([lang, translatedText]) => {
                    const el = document.getElementById(`translation-${lang}`);
                    if (el) {
                        el.textContent = translatedText.substring(0, 200);
                        this.processedLanguages.add(lang);
                    }
                });

                this.setStepCompleted('translate');
                this.addLog(`Translated to ${Object.keys(translations).length} languages`, 'success');
            } catch (e) {
                this.addLog(`Translation failed: ${e.message}`, 'error');
                this.setStepCompleted('translate');
            }

            // Step 3: EXTRACT
            this.setStepActive('extract');
            this.addLog('[3/4] Extracting keywords...');

            try {
                const insights = await this.api.extractKeywords(result.id);
                this.displayKeywords(insights.keywords || [], insights.formulas || []);
                this.setStepCompleted('extract');
                this.addLog(`Extracted ${(insights.keywords || []).length} keywords`, 'success');
            } catch (e) {
                this.addLog(`Extraction failed: ${e.message}`, 'error');
                this.setStepCompleted('extract');
            }

            // Step 4: SUMMARIZE
            this.setStepActive('summarize');
            this.addLog('[4/4] Generating summary...');

            try {
                const summaryResp = await this.api.summarizeSession();
                const summaryText = summaryResp.summary || '';

                document.getElementById('summaryMeta').textContent =
                    `${summaryText.length} chars · Method: ${summaryResp.method || 'auto'}`;
                document.getElementById('summary').innerHTML =
                    `<p>${this.escapeHtml(summaryText)}</p>`;

                this.setStepCompleted('summarize');
                this.addLog('Summary generated', 'success');
            } catch (e) {
                this.addLog(`Summarization failed: ${e.message}`, 'error');
                this.setStepCompleted('summarize');
            }

            this.updateAnalytics();
            this.recorder.showToast('Processing complete!', 'success');
            this.addLog('All processing complete', 'success');

        } catch (error) {
            this.recorder.showToast(`Error: ${error.message}`, 'error');
            this.addLog(`Processing failed: ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
        }
    }

    // ── Pipeline UI ───────────────────────────────────────────────
    resetPipeline() {
        ['transcribe', 'translate', 'extract', 'summarize'].forEach(step => {
            const el = document.getElementById(`step-${step}`);
            if (el) el.className = 'pipeline-step';
        });
        document.querySelectorAll('.pipeline-connector').forEach(c => c.classList.remove('active'));
    }

    setStepActive(step) {
        const el = document.getElementById(`step-${step}`);
        if (el) el.className = 'pipeline-step active';
    }

    setStepCompleted(step) {
        const el = document.getElementById(`step-${step}`);
        if (el) {
            el.className = 'pipeline-step completed';
            // Animate the connector after this step
            const connectors = document.querySelectorAll('.pipeline-connector');
            const steps = ['transcribe', 'translate', 'extract', 'summarize'];
            const idx = steps.indexOf(step);
            if (idx >= 0 && idx < connectors.length) {
                connectors[idx].classList.add('active');
            }
        }
    }

    // ── Display Keywords ──────────────────────────────────────────
    displayKeywords(keywords, formulas) {
        const container = document.getElementById('keywords');
        const tags = [];

        keywords.forEach(kw => {
            this.allKeywords[kw] = (this.allKeywords[kw] || 0) + 1;
            tags.push(`<span class="tag tag-keyword">🏷️ ${this.escapeHtml(kw)}</span>`);
        });

        formulas.forEach(f => {
            const formula = typeof f === 'string' ? f : f.formula;
            if (formula) {
                tags.push(`<span class="tag tag-formula">📐 ${this.escapeHtml(formula)}</span>`);
            }
        });

        container.innerHTML = tags.length
            ? tags.join('')
            : '<p class="placeholder-text">No keywords found</p>';
    }

    // ── Analytics ─────────────────────────────────────────────────
    updateAnalytics() {
        document.getElementById('chunksCount').textContent = this.chunkCount;
        document.getElementById('keywordCount').textContent = Object.keys(this.allKeywords).length;
        document.getElementById('languageCount').textContent = this.processedLanguages.size;

        // Top Keywords
        const sorted = Object.entries(this.allKeywords)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);

        const listEl = document.getElementById('topKeywordsList');
        listEl.innerHTML = sorted.length
            ? sorted.map(([kw, count]) =>
                `<div class="keyword-item">
                    <span class="keyword-item-name">${this.escapeHtml(kw)}</span>
                    <span class="keyword-item-count">×${count}</span>
                </div>`
            ).join('')
            : '<p class="placeholder-text-sm">No keywords yet</p>';
    }

    startDurationTimer() {
        this.sessionDurationInterval = setInterval(() => {
            if (this.sessionStartTime) {
                const secs = Math.floor((Date.now() - this.sessionStartTime) / 1000);
                const min = Math.floor(secs / 60);
                document.getElementById('sessionDuration').textContent =
                    min > 0 ? `${min}m ${secs % 60}s` : `${secs}s`;
            }
        }, 1000);
    }

    // ── WebSocket Handler ─────────────────────────────────────────
    handleWSMessage(msg) {
        if (msg.type) this.addLog(`WS: ${msg.type} update`);
    }

    // ── Activity Log ──────────────────────────────────────────────
    addLog(message, type = '') {
        const container = document.getElementById('processingLog');
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });

        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${time}] ${message}`;
        container.insertBefore(entry, container.firstChild);

        // Keep last 30 entries
        while (container.children.length > 30) {
            container.removeChild(container.lastChild);
        }
    }

    // ── Utilities ─────────────────────────────────────────────────
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ── Boot ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const app = new LectureAssistantApp();
    app.init().catch(console.error);
});
