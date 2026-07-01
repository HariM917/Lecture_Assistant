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
    }

    async init() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            source.connect(this.analyser);
            return true;
        } catch (error) {
            console.error('Microphone access denied:', error);
            this.showToast('Microphone access denied. Enable in browser settings.', 'error');
            return false;
        }
    }

    start() {
        if (!this.mediaStream) return;

        this.audioChunks = [];
        this.isRecording = true;
        this.recordingStartTime = Date.now();

        this.mediaRecorder = new MediaRecorder(this.mediaStream);
        this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = () => {
            this.isRecording = false;
            this.animationId && cancelAnimationFrame(this.animationId);
        };

        this.mediaRecorder.start();
        this.drawWaveform();
        return true;
    }

    stop() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            return this.getAudioBlob();
        }
        return null;
    }

    getAudioBlob() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        return audioBlob;
    }

    getRecordingDuration() {
        if (!this.recordingStartTime) return 0;
        return Math.floor((Date.now() - this.recordingStartTime) / 1000);
    }

    drawWaveform() {
        const canvas = document.getElementById('waveform');
        if (!canvas) return;

        const canvasCtx = canvas.getContext('2d');
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            this.animationId = requestAnimationFrame(draw);

            this.analyser.getByteFrequencyData(dataArray);

            canvasCtx.fillStyle = 'rgb(241 245 250)';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

            const barWidth = (canvas.width / bufferLength) * 2.5;
            let x = 0;

            canvasCtx.fillStyle = 'rgb(79 70 229)';
            for (let i = 0; i < bufferLength; i++) {
                const barHeight = (dataArray[i] / 255) * canvas.height;
                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                x += barWidth + 1;
            }
        };

        draw();
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg visible ${
            type === 'error' ? 'bg-red-600' : type === 'success' ? 'bg-green-600' : 'bg-blue-600'
        } text-white`;
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    dispose() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// Make it globally available
window.AudioRecorder = AudioRecorder;
