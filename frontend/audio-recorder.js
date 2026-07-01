/**
 * Audio Recorder — microphone capture with waveform visualization.
 */
class AudioRecorder {
    constructor() {
        this.mediaStream = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.recordingStartTime = null;
        this.audioContext = null;
        this.analyser = null;
        this.animationId = null;
        this.timerInterval = null;
    }

    async init() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            source.connect(this.analyser);
            return true;
        } catch (error) {
            console.error('Microphone access denied:', error);
            return false;
        }
    }

    start() {
        if (!this.mediaStream) return false;

        this.audioChunks = [];
        this.isRecording = true;
        this.recordingStartTime = Date.now();

        this.mediaRecorder = new MediaRecorder(this.mediaStream);
        this.mediaRecorder.ondataavailable = (e) => this.audioChunks.push(e.data);
        this.mediaRecorder.onstop = () => {
            this.isRecording = false;
            this._stopVisuals();
        };

        this.mediaRecorder.start();
        this._startVisuals();
        this._startTimer();

        // Add recording class to button
        const btn = document.getElementById('startRecordBtn');
        if (btn) btn.classList.add('recording');

        return true;
    }

    stop() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this._stopTimer();

            const btn = document.getElementById('startRecordBtn');
            if (btn) btn.classList.remove('recording');

            return new Blob(this.audioChunks, { type: 'audio/webm' });
        }
        return null;
    }

    getRecordingDuration() {
        if (!this.recordingStartTime) return 0;
        return Math.floor((Date.now() - this.recordingStartTime) / 1000);
    }

    // ── Waveform Visualization ────────────────────────────────────
    _startVisuals() {
        const canvas = document.getElementById('waveform');
        if (!canvas || !this.analyser) return;

        const ctx = canvas.getContext('2d');
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        // Set canvas resolution
        canvas.width = canvas.offsetWidth * 2;
        canvas.height = canvas.offsetHeight * 2;
        ctx.scale(2, 2);

        const w = canvas.offsetWidth;
        const h = canvas.offsetHeight;

        const draw = () => {
            this.animationId = requestAnimationFrame(draw);
            this.analyser.getByteFrequencyData(dataArray);

            // Clear with dark background
            ctx.fillStyle = 'rgba(10, 10, 20, 0.85)';
            ctx.fillRect(0, 0, w, h);

            const barWidth = (w / bufferLength) * 2.5;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const normalized = dataArray[i] / 255;
                const barHeight = normalized * h * 0.9;

                // Gradient from purple to blue
                const hue = 260 + (normalized * 40);
                const lightness = 40 + (normalized * 30);
                ctx.fillStyle = `hsl(${hue}, 70%, ${lightness}%)`;

                const yPos = h - barHeight;
                ctx.fillRect(x, yPos, barWidth - 1, barHeight);

                // Mirror reflection
                ctx.globalAlpha = 0.15;
                ctx.fillRect(x, 0, barWidth - 1, barHeight * 0.3);
                ctx.globalAlpha = 1;

                x += barWidth + 1;
            }
        };

        draw();
    }

    _stopVisuals() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    // ── Timer ─────────────────────────────────────────────────────
    _startTimer() {
        const timerEl = document.getElementById('recordingTimer');
        if (!timerEl) return;

        this.timerInterval = setInterval(() => {
            const secs = this.getRecordingDuration();
            const min = Math.floor(secs / 60).toString().padStart(2, '0');
            const sec = (secs % 60).toString().padStart(2, '0');
            timerEl.textContent = `${min}:${sec}`;
        }, 200);
    }

    _stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    dispose() {
        this._stopVisuals();
        this._stopTimer();
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(t => t.stop());
        }
    }

    // ── Toast Helper ──────────────────────────────────────────────
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        if (!toast) return;

        toast.textContent = message;
        toast.className = `toast ${type}`;

        clearTimeout(this._toastTimeout);
        this._toastTimeout = setTimeout(() => {
            toast.classList.add('hidden');
        }, 3500);
    }
}

window.AudioRecorder = AudioRecorder;
