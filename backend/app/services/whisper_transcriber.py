"""
🎤 Professional Whisper Transcriber Service

Auto-detects language and transcribes in the original native script.
Supports: MP3, MP4, MPEG, M4A, WAV, WebM

Extracted & Refactored for: Multilingual Lecture Assistant v2.0
"""

import whisper
import os
import json
import re
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Union
import logging
from langdetect import detect, LangDetectException, DetectorFactory

# Set seed for consistent language detection results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class WhisperTranscriberPro:
    """Professional Whisper transcription that auto-detects and transcribes in the original language."""
    
    SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
    AVAILABLE_MODELS = ['tiny', 'base', 'small', 'medium', 'large']
    
    def __init__(self, model_name: str = "base", use_fp16: bool = True, 
                 high_accuracy: bool = True, speed_mode: str = "fast"):
        """
        Initialize professional transcriber.
        
        Args:
            model_name: Model size (tiny, base, small, medium, large)
            use_fp16: Use 16-bit precision (faster, less memory)
            high_accuracy: Enable high accuracy mode
            speed_mode: 'fast', 'balanced', or 'slow'
        """
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model. Choose from: {self.AVAILABLE_MODELS}")
        
        if speed_mode not in ['fast', 'balanced', 'slow']:
            raise ValueError("speed_mode must be 'fast', 'balanced', or 'slow'")
        
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.high_accuracy = high_accuracy
        self.speed_mode = speed_mode
        self.model = None
        self._loaded = False
        
        logger.info(f"🔄 Initializing Whisper Transcriber (model={model_name}, speed={speed_mode})")
    
    def load_model(self):
        """Load the Whisper model (lazy loading)."""
        if self._loaded:
            return
        
        try:
            precision = "FP16 (16-bit)" if self.use_fp16 else "FP32 (32-bit)"
            accuracy_mode = " + HIGH ACCURACY" if self.high_accuracy else ""
            logger.info(f"🔄 Loading Whisper '{self.model_name}' model ({precision}){accuracy_mode}")
            logger.info(f"   Speed Mode: {self.speed_mode.upper()}")
            
            self.model = whisper.load_model(self.model_name)
            self._loaded = True
            logger.info(f"✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean the final text by fixing multiple spaces and formatting.
        Keeps all native unicode characters intact.
        """
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()

    def validate_file(self, audio_path: str) -> bool:
        """Validate audio file."""
        if not os.path.exists(audio_path):
            logger.error(f"❌ File not found - {audio_path}")
            return False
        
        file_ext = Path(audio_path).suffix.lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            logger.error(f"❌ Unsupported format '{file_ext}'")
            logger.error(f"   Supported: {', '.join(sorted(self.SUPPORTED_FORMATS))}")
            return False
        
        return True
    
    def get_transcription_options(self) -> Dict:
        """Get optimized transcription options based on speed mode."""
        options = {
            "task": "transcribe",
            "fp16": self.use_fp16,
            
            # Anti-hallucination parameters
            "condition_on_previous_text": False, 
            "compression_ratio_threshold": 2.4,   
            "logprob_threshold": -1.0,            
            "no_speech_threshold": 0.6            
        }
        
        if self.high_accuracy:
            if self.speed_mode == "fast":
                options["beam_size"] = 1
                options["best_of"] = 1
                options["temperature"] = 0.0
            elif self.speed_mode == "balanced":
                options["beam_size"] = 3
                options["best_of"] = 3
                options["temperature"] = 0.0
                options["patience"] = 1.0
            else:  # slow
                options["beam_size"] = 5
                options["best_of"] = 5
                options["temperature"] = 0.0
                options["patience"] = 2.0
            
        return options
    
    def transcribe_single(self, audio_path: str, show_progress: bool = True) -> Optional[Dict]:
        """
        Transcribe a single audio file directly into its detected language.
        
        Args:
            audio_path: Path to audio file
            show_progress: Whether to log progress
            
        Returns:
            Dictionary with transcription results or None if failed
        """
        if not self.validate_file(audio_path):
            return None
        
        # Lazy load model on first use
        if not self._loaded:
            self.load_model()
        
        try:
            filename = Path(audio_path).name
            logger.info(f"⏳ Processing: {filename}")
            
            options = self.get_transcription_options()
            
            if show_progress:
                beam = options.get('beam_size', 1)
                logger.info(f"   🔄 Transcribing (beam_size={beam})...")
            
            # Transcribe with task='transcribe' to keep native language
            result = self.model.transcribe(audio_path, **options)
            
            raw_text = result["text"]
            
            # Audio-based language detection (Whisper's built-in)
            audio_detected_lang = result.get("language", "unknown")
            
            # Text-based language detection (langdetect)
            try:
                text_detected_lang = detect(raw_text) if raw_text.strip() else "unknown"
            except LangDetectException:
                text_detected_lang = "unknown"
            
            if show_progress:
                logger.info(f"   🗣️ Audio language: {audio_detected_lang}")
                logger.info(f"   📝 Text language: {text_detected_lang}")
            
            cleaned_text = self.clean_text(raw_text)
            
            logger.info(f"✅ Transcription completed")
            
            return {
                "file": audio_path,
                "filename": filename,
                "timestamp": datetime.now().isoformat(),
                "model": self.model_name,
                "speed_mode": self.speed_mode,
                "original_audio_language": audio_detected_lang,
                "detected_text_language": text_detected_lang,
                "output_language": audio_detected_lang,
                "text": cleaned_text,
                "segments": result.get("segments", []),
                "duration": result.get("duration", "N/A")
            }
        
        except Exception as e:
            logger.error(f"❌ Error transcribing '{filename}': {e}")
            return None
    
    def transcribe_batch(self, audio_dir: str) -> List[Dict]:
        """Transcribe all audio files in a directory to their detected languages."""
        if not os.path.isdir(audio_dir):
            logger.error(f"❌ Directory not found - {audio_dir}")
            return []
        
        audio_files = [
            os.path.join(audio_dir, f) for f in os.listdir(audio_dir)
            if Path(f).suffix.lower() in self.SUPPORTED_FORMATS
        ]
        
        if not audio_files:
            logger.warning(f"⚠️ No supported audio files found in '{audio_dir}'")
            return []
        
        logger.info(f"📁 Found {len(audio_files)} audio files")
        
        results = []
        for idx, audio_file in enumerate(audio_files, 1):
            logger.info(f"[{idx}/{len(audio_files)}] Processing...")
            result = self.transcribe_single(audio_file, show_progress=False)
            if result:
                results.append(result)
        
        logger.info(f"✅ Batch processing complete: {len(results)}/{len(audio_files)} succeeded")
        return results
    
    def save_results(self, results: Union[Dict, List], output_format: str = "txt",
                    output_file: Optional[str] = None) -> Optional[str]:
        """
        Save transcription results to file.
        
        Args:
            results: Single result dict or list of results
            output_format: 'json', 'txt', or 'csv'
            output_file: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file or None if failed
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"transcription_{timestamp}.{output_format}"
        
        try:
            if output_format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            
            elif output_format == "txt":
                with open(output_file, 'w', encoding='utf-8') as f:
                    if isinstance(results, list):
                        for result in results:
                            f.write(f"FILE: {result['filename']}\n")
                            f.write(f"AUDIO LANGUAGE (Whisper): {result['original_audio_language']}\n")
                            f.write(f"TEXT LANGUAGE (langdetect): {result['detected_text_language']}\n")
                            f.write(f"MODEL: {result['model']}\n")
                            f.write("=" * 80 + "\n")
                            f.write(result['text'])
                            f.write("\n" + "=" * 80 + "\n\n")
                    else:
                        f.write(f"FILE: {results['filename']}\n")
                        f.write(f"AUDIO LANGUAGE (Whisper): {results['original_audio_language']}\n")
                        f.write(f"TEXT LANGUAGE (langdetect): {results['detected_text_language']}\n")
                        f.write(f"MODEL: {results['model']}\n")
                        f.write("=" * 80 + "\n")
                        f.write(results['text'])
            
            elif output_format == "csv":
                import csv
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    if isinstance(results, list) and len(results) > 0:
                        writer = csv.DictWriter(
                            f, 
                            fieldnames=['filename', 'audio_language', 'text_language', 'model', 'duration', 'text']
                        )
                        writer.writeheader()
                        for result in results:
                            writer.writerow({
                                'filename': result['filename'],
                                'audio_language': result['original_audio_language'],
                                'text_language': result['detected_text_language'],
                                'model': result['model'],
                                'duration': result['duration'],
                                'text': result['text'][:100]  # First 100 chars
                            })
            
            logger.info(f"💾 Results saved: {output_file}")
            return output_file
        
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
            return None
    
    def get_service_info(self) -> Dict:
        """Get service information and capabilities."""
        return {
            "service": "whisper_transcriber",
            "status": "operational" if self._loaded else "not_loaded",
            "version": "2.0",
            "model": self.model_name,
            "speed_mode": self.speed_mode,
            "high_accuracy": self.high_accuracy,
            "capabilities": [
                "Single file transcription",
                "Batch processing",
                "Auto language detection",
                "Multiple audio formats",
                "Save as JSON/TXT/CSV"
            ],
            "supported_formats": list(self.SUPPORTED_FORMATS),
            "available_models": self.AVAILABLE_MODELS
        }


# Global instance
_transcriber: Optional[WhisperTranscriberPro] = None


def get_transcriber(model_name: str = "base", speed_mode: str = "fast") -> WhisperTranscriberPro:
    """Get or create transcriber instance."""
    global _transcriber
    if _transcriber is None:
        _transcriber = WhisperTranscriberPro(
            model_name=model_name,
            use_fp16=True,
            high_accuracy=True,
            speed_mode=speed_mode
        )
    return _transcriber


def transcribe_file(audio_path: str, model: str = "base", speed: str = "fast") -> Optional[Dict]:
    """Simple entry point for file transcription."""
    transcriber = get_transcriber(model, speed)
    return transcriber.transcribe_single(audio_path)


def transcribe_batch(audio_dir: str, model: str = "base", speed: str = "fast") -> List[Dict]:
    """Simple entry point for batch transcription."""
    transcriber = get_transcriber(model, speed)
    return transcriber.transcribe_batch(audio_dir)
