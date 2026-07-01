/**
 * API Client — handles all backend communication with retry logic.
 */
class APIClient {
    constructor(baseUrl = 'http://localhost:5000', wsUrl = 'ws://localhost:5000') {
        this.baseUrl = baseUrl;
        this.wsUrl = wsUrl;
        this.ws = null;
        this.wsMessageHandlers = [];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.sessionId = null;
    }

    // ── Internal fetch wrapper with retry ─────────────────────────
    async _fetch(url, options = {}, retries = 2) {
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                const response = await fetch(url, {
                    ...options,
                    signal: AbortSignal.timeout(30000),
                });
                if (!response.ok) {
                    const errorBody = await response.text();
                    throw new Error(`HTTP ${response.status}: ${errorBody}`);
                }
                return await response.json();
            } catch (error) {
                if (attempt === retries) throw error;
                const delay = Math.min(1000 * Math.pow(2, attempt), 5000);
                await new Promise(r => setTimeout(r, delay));
            }
        }
    }

    // ── Session APIs ──────────────────────────────────────────────
    async createSession(title, subject, instructor) {
        const data = await this._fetch(`${this.baseUrl}/api/lecture/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, subject, instructor }),
        });
        this.sessionId = data?.session?.id || data?.id;
        return data?.session || data;
    }

    async endSession() {
        return this._fetch(
            `${this.baseUrl}/api/lecture/sessions/${this.sessionId}/end`,
            { method: 'POST', headers: { 'Content-Type': 'application/json' } }
        );
    }

    // ── Transcription ─────────────────────────────────────────────
    async transcribeAudio(audioBlob, language = 'en') {
        const formData = new FormData();
        formData.append('file', audioBlob, audioBlob.name || 'audio.webm');
        formData.append('language', language);

        return this._fetch(
            `${this.baseUrl}/api/lecture/sessions/${this.sessionId}/transcribe`,
            { method: 'POST', body: formData },
            1 // fewer retries for large uploads
        );
    }

    // ── Translation ───────────────────────────────────────────────
    async translateText(transcriptionId, targetLanguage) {
        return this._fetch(
            `${this.baseUrl}/api/lecture/transcriptions/${transcriptionId}/translate`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_language: targetLanguage }),
            }
        );
    }

    async translateToAllLanguages(transcriptionId) {
        return this._fetch(
            `${this.baseUrl}/api/lecture/transcriptions/${transcriptionId}/translate-all`,
            { method: 'POST', headers: { 'Content-Type': 'application/json' } }
        );
    }

    // ── Analysis ──────────────────────────────────────────────────
    async extractKeywords(transcriptionId) {
        return this._fetch(
            `${this.baseUrl}/api/lecture/transcriptions/${transcriptionId}/extract`,
            { method: 'POST' }
        );
    }

    async summarizeSession() {
        return this._fetch(
            `${this.baseUrl}/api/lecture/sessions/${this.sessionId}/summarize`,
            { method: 'POST' }
        );
    }

    // ── Health ─────────────────────────────────────────────────────
    async checkHealth() {
        try {
            const resp = await fetch(`${this.baseUrl}/health`, {
                signal: AbortSignal.timeout(5000),
            });
            return resp.ok;
        } catch {
            return false;
        }
    }

    // ── WebSocket ─────────────────────────────────────────────────
    connectWebSocket() {
        return new Promise((resolve, reject) => {
            if (!this.sessionId) return reject(new Error('No session ID'));

            const wsPath = `${this.wsUrl}/api/lecture/ws/${this.sessionId}/client_${Date.now()}`;

            try {
                this.ws = new WebSocket(wsPath);
                this.ws.onopen = () => {
                    this.reconnectAttempts = 0;
                    resolve();
                };
                this.ws.onmessage = (event) => {
                    try {
                        const msg = JSON.parse(event.data);
                        this.wsMessageHandlers.forEach(h => h(msg));
                    } catch (e) {
                        console.error('WS parse error:', e);
                    }
                };
                this.ws.onerror = () => reject(new Error('WebSocket error'));
                this.ws.onclose = () => this._attemptReconnect();
            } catch (e) {
                reject(e);
            }
        });
    }

    _attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connectWebSocket().catch(() => {}), this.reconnectDelay);
        }
    }

    onMessage(handler) { this.wsMessageHandlers.push(handler); }

    disconnect() {
        if (this.ws) { this.ws.close(); this.ws = null; }
    }
}

window.APIClient = APIClient;
