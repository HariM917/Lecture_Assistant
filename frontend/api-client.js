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

    // REST API Calls
    async createSession(title, subject, instructor) {
        try {
            const response = await fetch(`${this.baseUrl}/api/lecture/sessions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, subject, instructor })
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            this.sessionId = data.id;
            return data;
        } catch (error) {
            console.error('CreateSession error:', error);
            this.showToast('Failed to create session', 'error');
            throw error;
        }
    }

    async endSession() {
        try {
            const response = await fetch(`${this.baseUrl}/api/lecture/sessions/${this.sessionId}/end`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('EndSession error:', error);
            this.showToast('Failed to end session', 'error');
            throw error;
        }
    }

    async transcribeAudio(audioBlob, language = 'en') {
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'audio.webm');
            formData.append('language', language);

            const response = await fetch(
                `${this.baseUrl}/api/lecture/sessions/${this.sessionId}/transcribe`,
                {
                    method: 'POST',
                    body: formData
                }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('TranscribeAudio error:', error);
            this.showToast('Failed to transcribe audio', 'error');
            throw error;
        }
    }

    async translateText(transcriptionId, targetLanguage) {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/lecture/transcriptions/${transcriptionId}/translate`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ target_language: targetLanguage })
                }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('TranslateText error:', error);
            throw error;
        }
    }

    async translateToAllLanguages(transcriptionId) {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/lecture/transcriptions/${transcriptionId}/translate-all`,
                { method: 'POST', headers: { 'Content-Type': 'application/json' } }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('TranslateToAll error:', error);
            throw error;
        }
    }

    async extractKeywords(transcriptionId) {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/lecture/transcriptions/${transcriptionId}/extract`,
                { method: 'POST' }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('ExtractKeywords error:', error);
            throw error;
        }
    }

    async summarizeSession() {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/lecture/sessions/${this.sessionId}/summarize`,
                { method: 'POST' }
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('SummarizeSession error:', error);
            throw error;
        }
    }

    async checkHealth() {
        try {
            console.log(`🔍 Checking health at: ${this.baseUrl}/health`);
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            console.log(`✅ Health check response: ${response.status}`);
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Backend health: ${JSON.stringify(data)}`);
                return true;
            }
            console.warn(`⚠️ Health check returned status: ${response.status}`);
            return false;
        } catch (error) {
            console.error(`❌ Health check failed: ${error.message}`, error);
            console.error(`💡 Trying to connect to: ${this.baseUrl}`);
            return false;
        }
    }

    // WebSocket Connection
    connectWebSocket() {
        return new Promise((resolve, reject) => {
            try {
                const wsPath = this.sessionId 
                    ? `${this.wsUrl}/api/lecture/ws/${this.sessionId}/client_${Math.random()}`
                    : null;

                if (!wsPath) {
                    this.showToast('No session ID available', 'error');
                    return reject(new Error('No session ID'));
                }

                this.ws = new WebSocket(wsPath);

                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.reconnectAttempts = 0;
                    this.showToast('Connected to backend', 'success');
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        this.wsMessageHandlers.forEach(handler => handler(message));
                    } catch (error) {
                        console.error('WebSocket message parse error:', error);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.showToast('WebSocket error', 'error');
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.attemptReconnect();
                };

            } catch (error) {
                reject(error);
            }
        });
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connectWebSocket().catch(console.error), this.reconnectDelay);
        } else {
            this.showToast('Failed to reconnect to backend', 'error');
        }
    }

    onMessage(handler) {
        this.wsMessageHandlers.push(handler);
    }

    sendMessage(type, data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, data }));
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.textContent = message;
            toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg ${
                type === 'error' ? 'bg-red-600' : type === 'success' ? 'bg-green-600' : 'bg-blue-600'
            } text-white`;
            
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 3000);
        }
    }
}

window.APIClient = APIClient;
