"""
Translation Model Trainer Service
Manages fine-tuning of translation models using Hugging Face datasets
Supports: English-Hindi, English-Tamil, and other language pairs
"""

import logging
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datasets import load_dataset
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class LanguagePair(str, Enum):
    """Supported language pairs for translation"""
    EN_HI = "en-hi"
    EN_TA = "en-ta"
    EN_TE = "en-te"
    EN_KN = "en-kn"
    EN_ML = "en-ml"
    HI_EN = "hi-en"
    TA_EN = "ta-en"
    TE_EN = "te-en"
    KN_EN = "kn-en"
    ML_EN = "ml-en"


class TranslationDatasetSource(str, Enum):
    """Available translation dataset sources"""
    ENGLISH_HINDI = "rajuptvs/English-to-hindi-podcast-translation"
    ENGLISH_TAMIL = "thaslimthoufica/english_to_tamil_translation"
    CUSTOM = "custom"


@dataclass
class TranslationSample:
    """Represents a single translation sample"""
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    domain: str  # podcast, news, technical, etc.
    dataset_source: str
    confidence: float = 1.0  # 0-1 confidence in translation


class HFTranslationDatasetLoader:
    """Load translation datasets from Hugging Face"""
    
    DATASET_SOURCES = {
        LanguagePair.EN_HI: TranslationDatasetSource.ENGLISH_HINDI,
        LanguagePair.EN_TA: TranslationDatasetSource.ENGLISH_TAMIL,
    }
    
    def __init__(self, cache_dir: str = "./hf_cache"):
        """Initialize dataset loader"""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"TranslationDatasetLoader initialized with cache: {cache_dir}")
    
    def load_english_hindi_podcast(self, split: str = "train", max_samples: Optional[int] = None) -> Dict:
        """
        Load English-Hindi podcast translation dataset
        
        Args:
            split: Dataset split (train, validation, test)
            max_samples: Maximum samples to load (None for all)
            
        Returns:
            Loaded dataset
        """
        try:
            logger.info("Loading English-Hindi podcast translation dataset...")
            ds = load_dataset(
                "rajuptvs/English-to-hindi-podcast-translation",
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            if split not in ds:
                logger.warning(f"Split '{split}' not available. Available: {list(ds.keys())}")
                dataset = ds["train"]
            else:
                dataset = ds[split]
            
            if max_samples:
                dataset = dataset.select(range(min(max_samples, len(dataset))))
            
            logger.info(f"✓ English-Hindi dataset loaded: {len(dataset)} samples")
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to load English-Hindi dataset: {e}")
            return None
    
    def load_english_tamil_translation(self, split: str = "train", max_samples: Optional[int] = None) -> Dict:
        """
        Load English-Tamil translation dataset
        
        Args:
            split: Dataset split
            max_samples: Maximum samples to load
            
        Returns:
            Loaded dataset
        """
        try:
            logger.info("Loading English-Tamil translation dataset...")
            ds = load_dataset(
                "thaslimthoufica/english_to_tamil_translation",
                cache_dir=self.cache_dir,
                trust_remote_code=True
            )
            
            if split not in ds:
                logger.warning(f"Split '{split}' not available. Available: {list(ds.keys())}")
                dataset = ds["train"]
            else:
                dataset = ds[split]
            
            if max_samples:
                dataset = dataset.select(range(min(max_samples, len(dataset))))
            
            logger.info(f"✓ English-Tamil dataset loaded: {len(dataset)} samples")
            return dataset
            
        except Exception as e:
            logger.error(f"Failed to load English-Tamil dataset: {e}")
            return None


class TranslationDataProcessor:
    """Process and normalize translation data"""
    
    def __init__(self):
        self.processed_count = 0
        self.skipped_count = 0
    
    def normalize_translation_pair(
        self,
        sample: Dict,
        source_lang: str,
        target_lang: str,
        dataset_type: str = "podcast"
    ) -> Optional[TranslationSample]:
        """
        Normalize a translation sample to standard format
        
        Args:
            sample: Original sample from dataset
            source_lang: Source language code
            target_lang: Target language code
            dataset_type: Type of dataset (podcast, news, etc.)
            
        Returns:
            TranslationSample or None if invalid
        """
        try:
            # Handle different dataset formats
            if dataset_type == "podcast":
                # English-Hindi/Tamil podcast format
                source_text = sample.get("english", sample.get("en", "")).strip()
                target_text = sample.get("hindi", sample.get("hindi_translation", sample.get("ta", ""))).strip()
            elif dataset_type == "translation":
                # Generic translation format
                source_text = sample.get("src", sample.get("source", "")).strip()
                target_text = sample.get("tgt", sample.get("target", "")).strip()
            else:
                source_text = sample.get("source_text", "").strip()
                target_text = sample.get("target_text", "").strip()
            
            # Validation
            if not source_text or not target_text:
                self.skipped_count += 1
                return None
            
            if len(source_text.split()) < 2 or len(target_text.split()) < 2:
                self.skipped_count += 1
                return None
            
            # Create normalized sample
            translation_sample = TranslationSample(
                source_text=source_text,
                target_text=target_text,
                source_lang=source_lang,
                target_lang=target_lang,
                domain=dataset_type,
                dataset_source=f"{source_lang}-{target_lang}",
                confidence=1.0
            )
            
            self.processed_count += 1
            return translation_sample
            
        except Exception as e:
            logger.debug(f"Error normalizing translation pair: {e}")
            self.skipped_count += 1
            return None
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        total = self.processed_count + self.skipped_count
        return {
            "processed": self.processed_count,
            "skipped": self.skipped_count,
            "success_rate": self.processed_count / total if total > 0 else 0
        }


class TranslationQualityFilter:
    """Filter and validate translation quality"""
    
    @staticmethod
    def filter_by_length_similarity(
        translations: List[TranslationSample],
        min_ratio: float = 0.5,
        max_ratio: float = 2.0
    ) -> List[TranslationSample]:
        """
        Filter translations where source/target length ratio is reasonable
        (Good translations typically have similar length ratios)
        
        Args:
            translations: List of translation samples
            min_ratio: Minimum source/target word ratio
            max_ratio: Maximum source/target word ratio
            
        Returns:
            Filtered list
        """
        filtered = []
        
        for trans in translations:
            source_words = len(trans.source_text.split())
            target_words = len(trans.target_text.split())
            
            if source_words > 0:
                ratio = target_words / source_words
                if min_ratio <= ratio <= max_ratio:
                    filtered.append(trans)
        
        logger.info(f"Filtered by length ratio: {len(filtered)}/{len(translations)} samples")
        return filtered
    
    @staticmethod
    def remove_duplicates(translations: List[TranslationSample]) -> List[TranslationSample]:
        """Remove duplicate translation pairs"""
        seen = set()
        unique = []
        
        for trans in translations:
            key = (trans.source_text, trans.target_text)
            if key not in seen:
                seen.add(key)
                unique.append(trans)
        
        logger.info(f"Removed duplicates: {len(unique)}/{len(translations)} samples")
        return unique


class TranslationModelTrainer:
    """Orchestrate translation model training"""
    
    def __init__(self):
        self.loader = HFTranslationDatasetLoader()
        self.processor = TranslationDataProcessor()
        self.filter = TranslationQualityFilter()
        self.training_history = []
        logger.info("TranslationModelTrainer initialized")
    
    def prepare_translation_data(
        self,
        language_pair: str,
        max_samples: int = 200
    ) -> Dict:
        """
        Prepare training data for translation model
        
        Args:
            language_pair: e.g., "en-hi", "en-ta"
            max_samples: Maximum samples to prepare
            
        Returns:
            Preparation stats and metadata
        """
        logger.info(f"Preparing translation data for {language_pair} (max {max_samples})...")
        
        prep_stats = {
            "timestamp": datetime.now().isoformat(),
            "language_pair": language_pair,
            "max_samples": max_samples,
            "source": None,
            "target": None,
            "status": "preparing",
            "samples_prepared": 0,
            "processor_stats": {}
        }
        
        # Parse language pair
        langs = language_pair.split("-")
        if len(langs) != 2:
            prep_stats["status"] = "error"
            prep_stats["error"] = "Invalid language pair format"
            return prep_stats
        
        source_lang, target_lang = langs
        prep_stats["source"] = source_lang
        prep_stats["target"] = target_lang
        
        # Load appropriate dataset
        dataset = None
        dataset_type = "podcast"
        
        if language_pair == "en-hi":
            dataset = self.loader.load_english_hindi_podcast(
                split="train",
                max_samples=max_samples
            )
            prep_stats["dataset_source"] = "rajuptvs/English-to-hindi-podcast-translation"
            
        elif language_pair == "en-ta":
            dataset = self.loader.load_english_tamil_translation(
                split="train",
                max_samples=max_samples
            )
            prep_stats["dataset_source"] = "thaslimthoufica/english_to_tamil_translation"
        else:
            prep_stats["status"] = "error"
            prep_stats["error"] = f"Language pair not supported: {language_pair}"
            return prep_stats
        
        if not dataset:
            prep_stats["status"] = "error"
            prep_stats["error"] = "Failed to load dataset"
            return prep_stats
        
        # Process samples
        processed_samples = []
        for sample in dataset:
            trans_sample = self.processor.normalize_translation_pair(
                sample,
                source_lang,
                target_lang,
                dataset_type
            )
            if trans_sample:
                processed_samples.append(trans_sample)
        
        # Apply quality filters
        filtered_samples = self.filter.filter_by_length_similarity(processed_samples)
        filtered_samples = self.filter.remove_duplicates(filtered_samples)
        
        prep_stats["samples_prepared"] = len(filtered_samples)
        prep_stats["processor_stats"] = self.processor.get_stats()
        prep_stats["status"] = "ready"
        
        return prep_stats
    
    def get_supported_language_pairs(self) -> Dict:
        """Get all supported language pairs"""
        return {
            "en-hi": {
                "name": "English to Hindi",
                "dataset": "English-Hindi Podcast Translation",
                "source": "rajuptvs/English-to-hindi-podcast-translation",
                "domain": "podcast"
            },
            "en-ta": {
                "name": "English to Tamil",
                "dataset": "English-Tamil Translation",
                "source": "thaslimthoufica/english_to_tamil_translation",
                "domain": "general"
            },
            "hi-en": {
                "name": "Hindi to English",
                "note": "Reverse direction supported via bidirectional model"
            },
            "ta-en": {
                "name": "Tamil to English",
                "note": "Reverse direction supported via bidirectional model"
            }
        }
    
    def get_translation_info(self) -> Dict:
        """Get comprehensive translation service info"""
        return {
            "timestamp": datetime.now().isoformat(),
            "service": "translation_trainer",
            "version": "1.0.0",
            "supported_language_pairs": self.get_supported_language_pairs(),
            "available_datasets": {
                "english_hindi_podcast": {
                    "source": "rajuptvs/English-to-hindi-podcast-translation",
                    "pairs": ["en-hi", "hi-en"],
                    "domain": "podcast"
                },
                "english_tamil": {
                    "source": "thaslimthoufica/english_to_tamil_translation",
                    "pairs": ["en-ta", "ta-en"],
                    "domain": "general"
                }
            },
            "capabilities": [
                "Fine-tune translation models",
                "Multi-language pair support",
                "Quality filtering",
                "Batch training",
                "Real-time monitoring"
            ]
        }


class TranslationDataValidator:
    """Validate translation datasets"""
    
    @staticmethod
    def validate_dataset(dataset, min_samples: int = 10) -> Tuple[bool, Dict]:
        """
        Validate a translation dataset
        
        Returns:
            (is_valid, validation_report)
        """
        report = {
            "total_samples": 0,
            "valid_samples": 0,
            "has_required_fields": True,
            "errors": []
        }
        
        if not dataset:
            report["errors"].append("Dataset is empty or None")
            return False, report
        
        try:
            report["total_samples"] = len(dataset)
            
            # Check first sample for required fields
            first_sample = dataset[0]
            logger.info(f"Dataset fields: {first_sample.keys()}")
            
            # Validate samples
            valid_count = 0
            for sample in dataset:
                # Try to extract source and target
                has_source = any(k in sample for k in ["english", "en", "src", "source_text", "source"])
                has_target = any(k in sample for k in ["hindi", "hindi_translation", "ta", "tgt", "target_text", "target"])
                
                if has_source and has_target:
                    valid_count += 1
            
            report["valid_samples"] = valid_count
            
            if valid_count < min_samples:
                report["errors"].append(f"Only {valid_count} valid samples found (minimum: {min_samples})")
                return False, report
            
            return True, report
            
        except Exception as e:
            report["errors"].append(str(e))
            return False, report


# Service instances
translation_trainer_service = None


def get_translation_trainer() -> TranslationModelTrainer:
    """Get or create translation trainer service singleton"""
    global translation_trainer_service
    if translation_trainer_service is None:
        translation_trainer_service = TranslationModelTrainer()
    return translation_trainer_service
