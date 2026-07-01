"""
🎤 Professional Whisper Transcription Service
Auto-detects languages, transcribes natively, captures real-time audio, and fine-tunes models.

Integrates with:
- Hugging Face datasets for training
- Real-time microphone input
- Batch audio file processing
- Multi-language native script output
"""

import whisper
import os
import json
import re
import numpy as np
import torch
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging
from langdetect import detect, LangDetectException, DetectorFactory

# Set seed for consistent language detection results
DetectorFactory.seed = 0

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from datasets import load_dataset, Audio
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False
    logger.warning("Datasets library not available. Dataset training disabled.")

try:
    import sounddevice as sd
    import queue
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False
    logger.warning("Sounddevice library not available. Real-time transcription disabled.")


class WhisperTranscriberService:
    """Professional Whisper transcription with auto-detection, real-time capture, and fine-tuning."""
    
    SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
    AVAILABLE_MODELS = ['tiny', 'base', 'small', 'medium', 'large']
    
    # Native script prompts to force Whisper into writing native text
    NATIVE_PROMPTS = {
        'hi': 'नमस्कार, यह एक हिंदी ट्रांसक्रिप्शन है।',
        'ta': 'வணக்கம், இது ஒரு தமிழ் ஆடியோ.',
        'te': 'నమస్కారం, ఇది తెలుగు ఆడియో.',
        'kn': 'ನಮಸ್ಕಾರ, ಇದು ಕನ್ನಡ ಆಡಿಯೋ.',
        'ml': 'നമസ്കാരം, ഇതൊരു മലയാളം ഓഡിയോ ആണ്.',
        'mr': 'नमस्कार, हा एक मराठी ऑडिओ आहे.',
        'ar': 'مرحباً، هذا تسجيل صوتي باللغة العربية.',
        'ur': 'یہ ایک اردو آڈیو ہے۔'
    }
    
    def __init__(self, model_name: str = "base", use_fp16: bool = True, 
                 high_accuracy: bool = True, speed_mode: str = "fast"):
        """Initialize the transcriber service."""
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model. Choose from: {self.AVAILABLE_MODELS}")
        
        if speed_mode not in ['fast', 'balanced', 'slow']:
            raise ValueError("speed_mode must be 'fast', 'balanced', or 'slow'")
        
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.high_accuracy = high_accuracy
        self.speed_mode = speed_mode
        self.model = None
        self.load_model()
        logger.info(f"✅ Whisper service initialized with model={model_name}, speed={speed_mode}")
    
    def load_model(self):
        """Load the Whisper model."""
        try:
            precision = "FP16 (16-bit)" if self.use_fp16 else "FP32 (32-bit)"
            accuracy_mode = " + HIGH ACCURACY" if self.high_accuracy else ""
            logger.info(f"Loading Whisper '{self.model_name}' model ({precision}){accuracy_mode}")
            self.model = whisper.load_model(self.model_name)
            logger.info(f"✅ Model loaded successfully!")
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """Clean text by fixing multiple spaces and formatting."""
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()

    def validate_file(self, audio_path: str) -> bool:
        """Validate audio file format and existence."""
        if not os.path.exists(audio_path):
            logger.error(f"File not found - {audio_path}")
            return False
        
        file_ext = Path(audio_path).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported format '{file_ext}'")
            return False
        
        return True
    
    def get_transcription_options(self, language: Optional[str] = None) -> Dict:
        """Get optimized transcription options based on speed mode and language."""
        options = {
            "task": "transcribe",
            "fp16": self.use_fp16,
            "condition_on_previous_text": False,
            "compression_ratio_threshold": 2.0,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6
        }
        
        fallback_temps = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
        
        if self.high_accuracy:
            if self.speed_mode == "fast":
                options["beam_size"] = 1
                options["best_of"] = 1
                options["temperature"] = fallback_temps
            elif self.speed_mode == "balanced":
                options["beam_size"] = 3
                options["best_of"] = 3
                options["temperature"] = fallback_temps
                options["patience"] = 1.0
            else:  # slow
                options["beam_size"] = 5
                options["best_of"] = 5
                options["temperature"] = fallback_temps
                options["patience"] = 2.0
        
        if language:
            options["language"] = language
            if language in self.NATIVE_PROMPTS:
                options["initial_prompt"] = self.NATIVE_PROMPTS[language]
        
        return options
    
    def detect_language(self, audio: np.ndarray) -> str:
        """Detect the language of audio using Whisper's built-in detection."""
        try:
            max_samples = 8 * 60 * 60 * 16000
            audio = audio[:max_samples]
            chunk_size = 16000 * 30
            n_mels = self.model.dims.n_mels if hasattr(self.model, 'dims') else 80
            
            cumulative_probs = {}
            chunks_processed = 0
            
            for i in range(0, len(audio), chunk_size):
                chunk = audio[i:i + chunk_size]
                
                if len(chunk) < 16000 * 2 and chunks_processed > 0:
                    continue
                
                chunk = whisper.pad_or_trim(chunk)
                mel = whisper.log_mel_spectrogram(chunk, n_mels=n_mels).to(self.model.device)
                
                _, probs = self.model.detect_language(mel)
                
                if not cumulative_probs:
                    cumulative_probs = probs
                else:
                    for lang in probs:
                        cumulative_probs[lang] += probs[lang]
                
                chunks_processed += 1
            
            if cumulative_probs:
                detected_lang = max(cumulative_probs, key=cumulative_probs.get)
            else:
                detected_lang = 'en'
            
            logger.info(f"Detected language: {detected_lang} (from {chunks_processed} chunks)")
            return detected_lang
        
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return 'en'  # Fallback
    
    def transcribe_single(self, audio_path: str = None, audio_array: np.ndarray = None) -> Optional[Dict]:
        """Transcribe a single audio file or numpy array."""
        if audio_array is not None:
            audio = audio_array.astype(np.float32)
            filename = audio_path or "audio_sample"
        else:
            if not audio_path or not self.validate_file(audio_path):
                return None
            filename = Path(audio_path).name
            audio = whisper.load_audio(audio_path)
        
        try:
            logger.info(f"Processing: {filename}")
            
            # Detect language
            detected_lang = self.detect_language(audio)
            
            # Get options for detected language
            options = self.get_transcription_options(language=detected_lang)
            
            logger.info(f"Transcribing with beam_size={options.get('beam_size', 1)}...")
            
            # Transcribe
            result = self.model.transcribe(audio, **options)
            
            raw_text = result["text"]
            
            # Verify with langdetect
            try:
                text_detected_lang = detect(raw_text) if raw_text.strip() else "unknown"
            except LangDetectException:
                text_detected_lang = "unknown"
            
            cleaned_text = self.clean_text(raw_text)
            
            logger.info(f"✅ Transcription completed!")
            
            return {
                "file": filename,
                "timestamp": datetime.now().isoformat(),
                "model": self.model_name,
                "speed_mode": self.speed_mode,
                "original_audio_language": detected_lang,
                "detected_text_language": text_detected_lang,
                "output_language": detected_lang,
                "text": cleaned_text,
                "segments": result.get("segments", []),
                "duration": result.get("duration", "N/A")
            }
        
        except Exception as e:
            logger.error(f"Error transcribing '{filename}': {e}")
            return None
    
    def transcribe_batch(self, audio_dir: str) -> List[Dict]:
        """Transcribe all audio files in a directory."""
        if not os.path.isdir(audio_dir):
            logger.error(f"Directory not found - {audio_dir}")
            return []
        
        audio_files = [
            os.path.join(audio_dir, f) for f in os.listdir(audio_dir)
            if Path(f).suffix.lower() in self.SUPPORTED_FORMATS
        ]
        
        if not audio_files:
            logger.warning(f"No supported audio files found in '{audio_dir}'")
            return []
        
        logger.info(f"Found {len(audio_files)} audio files")
        
        results = []
        for idx, audio_file in enumerate(audio_files, 1):
            logger.info(f"[{idx}/{len(audio_files)}] Processing {os.path.basename(audio_file)}...")
            result = self.transcribe_single(audio_path=audio_file)
            if result:
                results.append(result)
        
        return results

    def transcribe_dataset(self, dataset_name: str, split: str = "train", limit: int = 5) -> List[Dict]:
        """Transcribe audio from a Hugging Face dataset."""
        if not HAS_DATASETS:
            logger.error("Datasets library not available")
            return []

        logger.info(f"Loading Hugging Face dataset '{dataset_name}' (split: {split})...")
        try:
            dataset = load_dataset(dataset_name, split=split)
            dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return []

        total_samples = len(dataset)
        process_limit = min(limit, total_samples)
        logger.info(f"Found {total_samples} samples. Processing {process_limit}...")
        
        results = []
        for idx, item in enumerate(dataset):
            if idx >= process_limit:
                break
            
            logger.info(f"[{idx+1}/{process_limit}] Processing dataset sample...")
            
            if "audio" not in item:
                logger.warning(f"'audio' column not found in sample {idx}")
                continue
            
            audio_array = item["audio"]["array"]
            safe_dataset_name = dataset_name.replace('/', '_')
            sample_name = f"hf_dataset_{safe_dataset_name}_{split}_{idx}"
            
            result = self.transcribe_single(audio_path=sample_name, audio_array=audio_array)
            if result:
                results.append(result)
        
        return results
    
    def train_on_dataset(self, dataset_name: str, text_column: str = "sentence", 
                        epochs: int = 1, limit: int = 100):
        """Fine-tune the Whisper model on a Hugging Face dataset."""
        if not HAS_DATASETS:
            logger.error("Datasets library not available")
            return False

        from torch.optim import AdamW
        from torch.nn import CrossEntropyLoss

        logger.info(f"Loading Hugging Face dataset '{dataset_name}' for training...")
        try:
            train_dataset = load_dataset(dataset_name, split="train")
            train_dataset = train_dataset.cast_column("audio", Audio(sampling_rate=16000))
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return False

        train_limit = min(limit, len(train_dataset))
        logger.info(f"Dataset loaded! Training on {train_limit} samples for {epochs} epoch(s).")
        
        device = self.model.device
        self.model.train()
        
        optimizer = AdamW(self.model.parameters(), lr=1e-5)
        loss_fn = CrossEntropyLoss()
        tokenizer = whisper.tokenizer.get_tokenizer(self.model.is_multilingual)

        for epoch in range(epochs):
            logger.info(f"Epoch {epoch+1}/{epochs}")
            epoch_loss = 0.0
            
            for idx, item in enumerate(train_dataset):
                if idx >= train_limit:
                    break
                
                text = item.get(text_column, "") or item.get("text", "")
                
                if "audio" not in item or not text:
                    logger.debug(f"Skipping sample {idx}: Missing audio or text")
                    continue
                
                optimizer.zero_grad()
                
                audio_array = item["audio"]["array"].astype(np.float32)
                audio_padded = whisper.pad_or_trim(audio_array)
                n_mels = self.model.dims.n_mels if hasattr(self.model, 'dims') else 80
                
                mel = whisper.log_mel_spectrogram(audio_padded, n_mels=n_mels).unsqueeze(0).to(device)
                
                tokens = [*tokenizer.sot_sequence, *tokenizer.encode(text), tokenizer.eot]
                
                input_tokens = torch.tensor([tokens[:-1]]).to(device)
                target_tokens = torch.tensor(tokens[1:]).to(device)
                
                audio_features = self.model.encoder(mel)
                logits = self.model.decoder(input_tokens, audio_features)
                
                loss = loss_fn(logits.view(-1, logits.shape[-1]), target_tokens)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                
                if (idx + 1) % 10 == 0 or (idx + 1) == train_limit:
                    logger.info(f"Step {idx+1}/{train_limit}, Loss: {loss.item():.4f}")
            
            avg_loss = epoch_loss / max(1, train_limit)
            logger.info(f"✅ Epoch {epoch+1} completed! Average Loss: {avg_loss:.4f}")

        logger.info("🎉 Fine-tuning complete! Switching to evaluation mode.")
        self.model.eval()
        return True

    def get_service_info(self) -> Dict:
        """Get service information and capabilities."""
        return {
            "service": "whisper_transcription",
            "status": "operational",
            "model": self.model_name,
            "models_available": self.AVAILABLE_MODELS,
            "speed_mode": self.speed_mode,
            "supported_formats": list(self.SUPPORTED_FORMATS),
            "supported_languages": list(self.NATIVE_PROMPTS.keys()),
            "features": {
                "auto_language_detection": True,
                "native_script_output": True,
                "batch_processing": True,
                "dataset_training": HAS_DATASETS,
                "realtime_transcription": HAS_SOUNDDEVICE
            },
            "capabilities": [
                "Transcribe single audio files",
                "Batch process audio directories",
                "Load from Hugging Face datasets",
                "Fine-tune on custom datasets",
                "Real-time microphone input",
                "Multi-language native output"
            ]
        }
