"""
Data Ingestion Service for Hugging Face Speech-to-Text Dataset
Handles loading, filtering, and preprocessing of multilingual speech data
for STT model fine-tuning and evaluation.
"""

import logging
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datasets import load_dataset, concatenate_datasets
import librosa
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AudioSample:
    """Represents a single audio sample with metadata"""
    audio_path: str
    transcript: str
    language: str
    duration: float
    sample_rate: int
    dataset_source: str
    split: str  # train/test/validation


class DataIngestors:
    """Manages dataset loading and processing"""
    
    # Supported language mappings
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ta': 'Tamil',
        'hi': 'Hindi',
        'te': 'Telugu',
        'kn': 'Kannada',
        'ml': 'Malayalam'
    }
    
    LANGUAGE_ALIASES = {
        'english': 'en',
        'tamil': 'ta',
        'hindi': 'hi',
        'telugu': 'te',
        'kannada': 'kn',
        'malayalam': 'ml'
    }


class HFDatasetLoader:
    """Load and manage Hugging Face speech datasets"""
    
    def __init__(self, cache_dir: str = "./hf_cache"):
        """
        Initialize HF dataset loader
        
        Args:
            cache_dir: Directory to cache downloaded datasets
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.loaded_datasets = {}
        logger.info(f"DatasetLoader initialized with cache: {cache_dir}")
    
    def load_anandhu_dataset(self) -> Dict:
        """
        Load ANANDHU-SCT Speech-to-text dataset from Hugging Face
        
        Returns:
            Dictionary with dataset splits (train, test, validation)
        """
        try:
            logger.info("Loading ANANDHU-SCT/Speech-to-text dataset...")
            ds = load_dataset(
                "ANANDHU-SCT/Speech-to-text",
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            logger.info(f"Dataset loaded successfully. Splits: {ds.column_names if hasattr(ds, 'column_names') else 'N/A'}")
            return ds
        except Exception as e:
            logger.error(f"Failed to load ANANDHU-SCT dataset: {e}")
            return {}
    
    def load_common_voice_multilingual(self) -> Dict:
        """
        Load Common Voice dataset (alternative multilingual source)
        Supports: en, ta, hi, te, kn, ml
        
        Returns:
            Dictionary with multilingual samples
        """
        try:
            logger.info("Loading Common Voice multilingual dataset...")
            supported_langs = list(DataIngestors.SUPPORTED_LANGUAGES.keys())
            datasets_dict = {}
            
            for lang_code in supported_langs:
                try:
                    logger.info(f"  Loading Common Voice for {lang_code}...")
                    ds = load_dataset(
                        "mozilla-foundation/common_voice_13_0",
                        lang_code,
                        cache_dir=self.cache_dir,
                        split="train[:100]",  # Sample subset
                        trust_remote_code=True
                    )
                    datasets_dict[lang_code] = ds
                    logger.info(f"  ✓ Common Voice {lang_code}: {len(ds)} samples")
                except Exception as e:
                    logger.warning(f"  ✗ Common Voice {lang_code} failed: {e}")
            
            return datasets_dict
        except Exception as e:
            logger.error(f"Failed to load Common Voice dataset: {e}")
            return {}


class AudioPreprocessor:
    """Preprocess audio samples for model training"""
    
    # Standard audio configuration for fine-tuning
    TARGET_SAMPLE_RATE = 16000
    MAX_DURATION_SECONDS = 30
    MIN_DURATION_SECONDS = 0.5
    
    def __init__(self):
        self.processed_count = 0
        self.skipped_count = 0
    
    def preprocess_audio(
        self, 
        audio_path: str, 
        transcript: str,
        language: str
    ) -> Optional[Tuple[np.ndarray, int]]:
        """
        Load and preprocess a single audio file
        
        Args:
            audio_path: Path to audio file
            transcript: Text transcription
            language: Language code
            
        Returns:
            Tuple of (audio_array, sample_rate) or None if invalid
        """
        try:
            # Load audio
            audio_array, sample_rate = librosa.load(
                audio_path,
                sr=self.TARGET_SAMPLE_RATE,
                mono=True
            )
            
            # Check duration
            duration = len(audio_array) / self.TARGET_SAMPLE_RATE
            if duration < self.MIN_DURATION_SECONDS or duration > self.MAX_DURATION_SECONDS:
                logger.debug(f"Audio duration {duration}s out of range for {audio_path}")
                self.skipped_count += 1
                return None
            
            # Normalize audio
            audio_array = audio_array.astype(np.float32)
            max_val = np.max(np.abs(audio_array))
            if max_val > 0:
                audio_array = audio_array / max_val
            
            self.processed_count += 1
            return audio_array, self.TARGET_SAMPLE_RATE
            
        except Exception as e:
            logger.debug(f"Error preprocessing {audio_path}: {e}")
            self.skipped_count += 1
            return None
    
    def get_stats(self) -> Dict:
        """Get preprocessing statistics"""
        return {
            "processed": self.processed_count,
            "skipped": self.skipped_count,
            "success_rate": self.processed_count / (self.processed_count + self.skipped_count) 
                          if (self.processed_count + self.skipped_count) > 0 else 0
        }


class DatasetFilter:
    """Filter and curate datasets for multilingual support"""
    
    @staticmethod
    def filter_by_language(
        dataset,
        target_language: str,
        language_field: str = "language"
    ) -> List[Dict]:
        """
        Filter dataset samples by language
        
        Args:
            dataset: Hugging Face dataset
            target_language: Language code or name
            language_field: Field name containing language info
            
        Returns:
            List of filtered samples
        """
        try:
            target_code = DataIngestors.LANGUAGE_ALIASES.get(
                target_language.lower(),
                target_language
            )
            
            filtered_samples = []
            
            # Assuming dataset has language field
            for sample in dataset:
                sample_lang = sample.get(language_field, "").lower()
                if sample_lang == target_code or target_code in sample_lang:
                    filtered_samples.append(sample)
            
            logger.info(f"Filtered {len(filtered_samples)} samples for {target_code}")
            return filtered_samples
            
        except Exception as e:
            logger.error(f"Error filtering by language: {e}")
            return []
    
    @staticmethod
    def create_language_subset(
        dataset,
        max_samples_per_language: int = 500
    ) -> Dict[str, List]:
        """
        Create subset of dataset with balanced language representation
        
        Args:
            dataset: Hugging Face dataset
            max_samples_per_language: Max samples per language
            
        Returns:
            Dictionary mapping language codes to sample lists
        """
        language_subsets = {}
        
        for lang_code in DataIngestors.SUPPORTED_LANGUAGES.keys():
            filtered = DatasetFilter.filter_by_language(
                dataset,
                lang_code
            )
            # Limit samples per language for efficiency
            language_subsets[lang_code] = filtered[:max_samples_per_language]
            logger.info(f"{lang_code}: {len(language_subsets[lang_code])} samples")
        
        return language_subsets


class STTModelTrainer:
    """Orchestrate STT model fine-tuning with dataset"""
    
    def __init__(self):
        self.loader = HFDatasetLoader()
        self.preprocessor = AudioPreprocessor()
        self.training_history = []
        logger.info("STT Model Trainer initialized")
    
    def prepare_training_data(
        self,
        max_samples_per_language: int = 100
    ) -> Dict:
        """
        Prepare complete training dataset
        
        Args:
            max_samples_per_language: Limit samples per language
            
        Returns:
            Prepared dataset with preprocessing stats
        """
        logger.info(f"Preparing training data (max {max_samples_per_language} per language)...")
        
        prepare_stats = {
            "timestamp": datetime.now().isoformat(),
            "max_samples_per_language": max_samples_per_language,
            "languages": DataIngestors.SUPPORTED_LANGUAGES,
            "sources": {},
            "summary": {}
        }
        
        # Try ANANDHU dataset first
        logger.info("Attempting to load ANANDHU-SCT dataset...")
        anandhu_ds = self.loader.load_anandhu_dataset()
        if anandhu_ds:
            prepare_stats["sources"]["anandhu"] = {
                "status": "loaded",
                "split_info": str(len(anandhu_ds) if hasattr(anandhu_ds, '__len__') else 'unknown')
            }
        
        # Fallback to Common Voice if needed
        if not anandhu_ds:
            logger.info("ANANDHU not available, loading Common Voice...")
            cv_datasets = self.loader.load_common_voice_multilingual()
            prepare_stats["sources"]["common_voice"] = {
                "status": "loaded",
                "languages": list(cv_datasets.keys()),
                "sample_counts": {
                    lang: len(ds) for lang, ds in cv_datasets.items()
                }
            }
        
        prepare_stats["preprocessing_stats"] = self.preprocessor.get_stats()
        prepare_stats["summary"] = {
            "status": "ready",
            "process_time": "in_progress",
            "available_languages": list(DataIngestors.SUPPORTED_LANGUAGES.values())
        }
        
        return prepare_stats
    
    def get_dataset_info(self) -> Dict:
        """Get comprehensive dataset information"""
        return {
            "timestamp": datetime.now().isoformat(),
            "dataset_source": "ANANDHU-SCT/Speech-to-text + Common Voice",
            "supported_languages": DataIngestors.SUPPORTED_LANGUAGES,
            "supported_language_codes": list(DataIngestors.SUPPORTED_LANGUAGES.keys()),
            "language_aliases": DataIngestors.LANGUAGE_ALIASES,
            "audio_config": {
                "sample_rate": AudioPreprocessor.TARGET_SAMPLE_RATE,
                "max_duration_seconds": AudioPreprocessor.MAX_DURATION_SECONDS,
                "min_duration_seconds": AudioPreprocessor.MIN_DURATION_SECONDS,
                "format": "WAV/MP3/FLAC"
            },
            "capabilities": [
                "Fine-tune Whisper model",
                "Multi-language support",
                "Audio preprocessing",
                "Batch training",
                "Model evaluation"
            ]
        }


class DatasetAnalyzer:
    """Analyze dataset characteristics and metrics"""
    
    def __init__(self):
        self.analysis_results = {}
    
    def analyze_dataset_composition(
        self,
        dataset_subsets: Dict[str, List]
    ) -> Dict:
        """
        Analyze composition of dataset by language
        
        Args:
            dataset_subsets: Dictionary of language-filtered samples
            
        Returns:
            Analysis report
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "language_distribution": {},
            "total_samples": 0,
            "statistics": {}
        }
        
        total = sum(len(samples) for samples in dataset_subsets.values())
        
        for lang_code, samples in dataset_subsets.items():
            lang_name = DataIngestors.SUPPORTED_LANGUAGES.get(lang_code, lang_code)
            percentage = (len(samples) / total * 100) if total > 0 else 0
            
            analysis["language_distribution"][lang_name] = {
                "code": lang_code,
                "samples": len(samples),
                "percentage": round(percentage, 2)
            }
        
        analysis["total_samples"] = total
        analysis["languages_represented"] = len(
            [s for s in dataset_subsets.values() if len(s) > 0]
        )
        
        return analysis


# Service instance
data_ingestion_service = None


def get_data_ingestion_service() -> STTModelTrainer:
    """Get or create data ingestion service singleton"""
    global data_ingestion_service
    if data_ingestion_service is None:
        data_ingestion_service = STTModelTrainer()
    return data_ingestion_service
