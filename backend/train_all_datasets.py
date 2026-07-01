"""
🚀 Train All Datasets - Comprehensive Training Orchestrator

Trains all available models:
1. Speech-to-Text (STT) - ANANDHU dataset
2. English-Hindi Translation - rajuptvs podcast dataset
3. English-Tamil Translation - english_to_tamil dataset

Usage:
    python train_all_datasets.py
    python train_all_datasets.py --quick        (faster, smaller datasets)
    python train_all_datasets.py --full         (comprehensive, full datasets)
    python train_all_datasets.py --monitor-only (check status without training)
"""

import requests
import asyncio
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Tuple
import time

# Configuration
BASE_URL = "http://localhost:8000/api/lecture"
ENDPOINTS = {
    "DATA_INGESTION": f"{BASE_URL}/data-ingestion",
    "TRANSLATION": f"{BASE_URL}/translation",
}

# Training profiles
PROFILES = {
    "quick": {
        "stt_max_samples": 100,
        "stt_batch_size": 16,
        "stt_epochs": 1,
        "translation_max_samples": 200,
        "translation_batch_size": 32,
        "translation_epochs": 1,
        "learning_rate": 1e-4,
    },
    "balanced": {
        "stt_max_samples": 500,
        "stt_batch_size": 16,
        "stt_epochs": 3,
        "translation_max_samples": 500,
        "translation_batch_size": 16,
        "translation_epochs": 3,
        "learning_rate": 5e-5,
    },
    "full": {
        "stt_max_samples": 2000,
        "stt_batch_size": 8,
        "stt_epochs": 5,
        "translation_max_samples": 2000,
        "translation_batch_size": 8,
        "translation_epochs": 5,
        "learning_rate": 1e-5,
    },
}

# Color codes for terminal
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "END": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}


class TrainingOrchestrator:
    """Orchestrates training of all datasets"""

    def __init__(self, profile: str = "balanced", dry_run: bool = False):
        self.profile = profile
        self.params = PROFILES.get(profile, PROFILES["balanced"])
        self.dry_run = dry_run
        self.training_jobs = {}
        self.results = {"successful": [], "failed": [], "monitoring": []}
        self.start_time = datetime.now()

    def log(self, level: str, message: str):
        """Print colored log messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "INFO": COLORS["CYAN"],
            "SUCCESS": COLORS["GREEN"],
            "WARNING": COLORS["YELLOW"],
            "ERROR": COLORS["RED"],
            "HEADER": COLORS["BOLD"] + COLORS["BLUE"],
        }.get(level, COLORS["END"])

        prefix = f"[{timestamp}]"
        print(f"{color}{prefix} {level:8s}{COLORS['END']} {message}")

    def print_header(self, title: str):
        """Print section header"""
        print(f"\n{COLORS['BOLD']}{COLORS['BLUE']}{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}{COLORS['END']}\n")

    def print_summary(self, title: str, data: Dict):
        """Print formatted summary"""
        print(f"\n{COLORS['BOLD']}{title}{COLORS['END']}")
        for key, value in data.items():
            print(f"  • {key}: {value}")

    def check_backend_health(self) -> bool:
        """Verify backend is running"""
        self.log("INFO", "Checking backend health...")
        try:
            # Check data ingestion health
            response = requests.get(
                f"{ENDPOINTS['DATA_INGESTION']}/health", timeout=5
            )
            if response.status_code != 200:
                self.log("ERROR", "Data Ingestion service not responding")
                return False

            # Check translation health
            response = requests.get(
                f"{ENDPOINTS['TRANSLATION']}/health", timeout=5
            )
            if response.status_code != 200:
                self.log("ERROR", "Translation service not responding")
                return False

            self.log("SUCCESS", "Backend services healthy ✓")
            return True
        except Exception as e:
            self.log("ERROR", f"Backend health check failed: {str(e)}")
            self.log("ERROR", "Ensure Docker containers are running: docker compose up --build")
            return False

    def prepare_stt_data(self) -> bool:
        """Prepare Speech-to-Text training data"""
        self.log("INFO", "📊 Preparing STT data...")
        endpoint = f"{ENDPOINTS['DATA_INGESTION']}/prepare"

        try:
            params = {
                "dataset_name": "ANANDHU-SCT/Speech-to-text",
                "max_samples": self.params["stt_max_samples"],
            }

            if self.dry_run:
                self.log("INFO", f"[DRY-RUN] POST {endpoint} | {params}")
                return True

            response = requests.post(endpoint, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                self.log(
                    "SUCCESS",
                    f"STT data prepared: {data.get('samples_prepared', '?')} samples",
                )
                self.training_jobs["stt_prepare"] = data
                return True
            else:
                self.log("ERROR", f"STT preparation failed: {response.text}")
                return False
        except Exception as e:
            self.log("ERROR", f"STT data preparation error: {str(e)}")
            return False

    def start_stt_training(self) -> Tuple[bool, str]:
        """Start Speech-to-Text model training"""
        self.log("INFO", "🎤 Starting STT training job...")
        endpoint = f"{ENDPOINTS['DATA_INGESTION']}/training/start"

        try:
            params = {
                "batch_size": self.params["stt_batch_size"],
                "num_epochs": self.params["stt_epochs"],
                "learning_rate": self.params["learning_rate"],
            }

            if self.dry_run:
                self.log("INFO", f"[DRY-RUN] POST {endpoint} | {params}")
                return True, "DRY_RUN_JOB_STT"

            response = requests.post(endpoint, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id", "unknown")
                self.log("SUCCESS", f"STT training started: job_id={job_id}")
                self.training_jobs["stt_train"] = {"job_id": job_id, "data": data}
                return True, job_id
            else:
                self.log("ERROR", f"STT training start failed: {response.text}")
                return False, None
        except Exception as e:
            self.log("ERROR", f"STT training start error: {str(e)}")
            return False, None

    def prepare_translation_data(self, language_pair: str) -> bool:
        """Prepare translation training data"""
        pair_display = f"{language_pair}".upper()
        self.log("INFO", f"📊 Preparing {pair_display} translation data...")
        endpoint = f"{ENDPOINTS['TRANSLATION']}/prepare"

        try:
            params = {
                "language_pair": language_pair,
                "max_samples": self.params["translation_max_samples"],
            }

            if self.dry_run:
                self.log("INFO", f"[DRY-RUN] POST {endpoint} | {params}")
                return True

            response = requests.post(endpoint, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()
                samples = data.get("samples_prepared", "?")
                self.log(
                    "SUCCESS", f"{pair_display} data prepared: {samples} samples"
                )
                self.training_jobs[f"trans_prepare_{language_pair}"] = data
                return True
            else:
                self.log(
                    "ERROR", f"{pair_display} preparation failed: {response.text}"
                )
                return False
        except Exception as e:
            self.log("ERROR", f"{pair_display} data preparation error: {str(e)}")
            return False

    def start_translation_training(self, language_pair: str) -> Tuple[bool, str]:
        """Start translation model training"""
        pair_display = f"{language_pair}".upper()
        self.log("INFO", f"🌍 Starting {pair_display} translation training...")
        endpoint = f"{ENDPOINTS['TRANSLATION']}/training/start"

        try:
            params = {
                "language_pair": language_pair,
                "batch_size": self.params["translation_batch_size"],
                "num_epochs": self.params["translation_epochs"],
                "learning_rate": self.params["learning_rate"],
            }

            if self.dry_run:
                self.log("INFO", f"[DRY-RUN] POST {endpoint} | {params}")
                return True, f"DRY_RUN_JOB_{language_pair}"

            response = requests.post(endpoint, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id", "unknown")
                self.log("SUCCESS", f"{pair_display} training started: job_id={job_id}")
                self.training_jobs[f"trans_train_{language_pair}"] = {
                    "job_id": job_id,
                    "data": data,
                }
                return True, job_id
            else:
                self.log(
                    "ERROR", f"{pair_display} training start failed: {response.text}"
                )
                return False, None
        except Exception as e:
            self.log("ERROR", f"{pair_display} training start error: {str(e)}")
            return False, None

    def monitor_job(self, job_type: str, job_id: str) -> Dict:
        """Monitor a training job"""
        if job_type == "stt":
            endpoint = f"{ENDPOINTS['DATA_INGESTION']}/training/status/{job_id}"
        else:  # translation
            endpoint = f"{ENDPOINTS['TRANSLATION']}/training/status/{job_id}"

        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": response.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def monitor_all_jobs(self):
        """Monitor all training jobs"""
        self.print_header("📊 MONITORING TRAINING JOBS")

        # Collect all job IDs
        jobs_to_monitor = {}
        for key, value in self.training_jobs.items():
            if "train" in key:
                job_id = value.get("job_id")
                if job_id:
                    job_type = "stt" if "stt" in key else "translation"
                    language_pair = key.split("_")[-1] if "_" in key else "N/A"
                    jobs_to_monitor[job_id] = {
                        "type": job_type,
                        "pair": language_pair,
                        "key": key,
                    }

        if not jobs_to_monitor:
            self.log("WARNING", "No training jobs to monitor")
            return

        # Monitor with updates
        max_checks = 12  # Check for ~2 minutes (10s intervals)
        check_count = 0

        while check_count < max_checks and jobs_to_monitor:
            check_count += 1
            self.log("INFO", f"Status check {check_count}/{max_checks}...")

            jobs_done = []
            for job_id, job_info in jobs_to_monitor.items():
                status_data = self.monitor_job(job_info["type"], job_id)
                status = status_data.get("status", "unknown")
                progress = status_data.get("progress", 0)

                job_display = f"{job_info['type'].upper()} ({job_info['pair']})"

                if status == "completed":
                    metrics = status_data.get("metrics", {})
                    self.log(
                        "SUCCESS",
                        f"{job_display}: COMPLETED | Metrics: {json.dumps(metrics)}",
                    )
                    self.results["successful"].append(job_id)
                    jobs_done.append(job_id)
                elif status == "running":
                    self.log(
                        "INFO",
                        f"{job_display}: RUNNING ({progress}%) | {status_data.get('current_step', '?')}/{status_data.get('total_steps', '?')} steps",
                    )
                elif status == "error":
                    self.log(
                        "ERROR",
                        f"{job_display}: ERROR | {status_data.get('message', 'Unknown error')}",
                    )
                    self.results["failed"].append(job_id)
                    jobs_done.append(job_id)
                else:
                    self.log("INFO", f"{job_display}: {status.upper()}")

            # Remove completed jobs
            for job_id in jobs_done:
                del jobs_to_monitor[job_id]

            # Wait before next check (unless all done)
            if jobs_to_monitor:
                self.log("INFO", "Waiting 10 seconds before next check...")
                time.sleep(10)

        # Final summary
        if jobs_to_monitor:
            self.log("WARNING", f"Monitoring timeout - {len(jobs_to_monitor)} jobs still running")
            self.log("INFO", "Run 'python train_all_datasets.py --monitor-only' to check status")
            for job_id, job_info in jobs_to_monitor.items():
                self.results["monitoring"].append(job_id)
        else:
            self.log("SUCCESS", "All monitored jobs completed!")

    def get_model_info(self):
        """Retrieve trained model information"""
        self.print_header("📚 MODEL INFORMATION")

        # STT models
        try:
            response = requests.get(
                f"{ENDPOINTS['DATA_INGESTION']}/training/models", timeout=10
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.log("INFO", f"STT Models: {len(models)} available")
                for model in models[:3]:  # Show first 3
                    self.log(
                        "INFO", f"  • {model.get('name', 'Unknown')} (v{model.get('version', '?')})"
                    )
        except Exception as e:
            self.log("WARNING", f"Could not retrieve STT models: {str(e)}")

        # Translation models
        try:
            response = requests.get(
                f"{ENDPOINTS['TRANSLATION']}/training/models", timeout=10
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                self.log("INFO", f"Translation Models: {len(models)} available")
                for model in models[:3]:  # Show first 3
                    self.log(
                        "INFO", f"  • {model.get('name', 'Unknown')} (v{model.get('version', '?')})"
                    )
        except Exception as e:
            self.log("WARNING", f"Could not retrieve translation models: {str(e)}")

    def print_final_report(self):
        """Print comprehensive final report"""
        self.print_header("📋 TRAINING SUMMARY REPORT")

        elapsed_time = datetime.now() - self.start_time
        elapsed_str = f"{elapsed_time.total_seconds():.1f}s"

        self.print_summary(
            "Training Configuration",
            {
                "Profile": self.profile.upper(),
                "Dry Run": "YES" if self.dry_run else "NO",
                "Duration": elapsed_str,
                "Start Time": self.start_time.strftime("%H:%M:%S"),
            },
        )

        self.print_summary(
            "Training Parameters",
            {
                "STT Samples": self.params["stt_max_samples"],
                "STT Batch Size": self.params["stt_batch_size"],
                "STT Epochs": self.params["stt_epochs"],
                "Translation Samples": self.params["translation_max_samples"],
                "Translation Batch Size": self.params["translation_batch_size"],
                "Translation Epochs": self.params["translation_epochs"],
                "Learning Rate": f"{self.params['learning_rate']:.0e}",
            },
        )

        self.print_summary(
            "Results",
            {
                "✅ Successful": len(self.results["successful"]),
                "❌ Failed": len(self.results["failed"]),
                "⏳ Still Monitoring": len(self.results["monitoring"]),
            },
        )

        if self.results["monitoring"]:
            self.print_summary(
                "Monitoring Jobs",
                {
                    f"Job {i+1}": job_id
                    for i, job_id in enumerate(self.results["monitoring"])
                },
            )

    def run_full_training(self):
        """Execute complete training pipeline"""
        self.print_header("🚀 MULTILINGUAL LECTURE ASSISTANT - FULL DATASET TRAINING")

        self.print_summary(
            "Configuration",
            {
                "Profile": self.profile.upper(),
                "Backend URL": BASE_URL,
                "Dry Run": "YES ⚠️" if self.dry_run else "NO",
            },
        )

        # Check backend
        if not self.check_backend_health():
            return

        # ===== SPEECH-TO-TEXT TRAINING =====
        self.print_header("🎤 PHASE 1: SPEECH-TO-TEXT (STT) MODEL TRAINING")

        if self.prepare_stt_data():
            success, job_id = self.start_stt_training()
            if success:
                self.log("SUCCESS", "✅ STT training job queued")
        else:
            self.log("ERROR", "❌ STT data preparation failed - skipping training")

        # ===== ENGLISH-HINDI TRANSLATION TRAINING =====
        self.print_header("🌍 PHASE 2: ENGLISH-HINDI TRANSLATION MODEL TRAINING")

        if self.prepare_translation_data("en-hi"):
            success, job_id = self.start_translation_training("en-hi")
            if success:
                self.log("SUCCESS", "✅ EN-HI translation training job queued")

        else:
            self.log("ERROR", "❌ EN-HI data preparation failed - skipping training")

        # ===== ENGLISH-TAMIL TRANSLATION TRAINING =====
        self.print_header("🌍 PHASE 3: ENGLISH-TAMIL TRANSLATION MODEL TRAINING")

        if self.prepare_translation_data("en-ta"):
            success, job_id = self.start_translation_training("en-ta")
            if success:
                self.log("SUCCESS", "✅ EN-TA translation training job queued")
        else:
            self.log("ERROR", "❌ EN-TA data preparation failed - skipping training")

        # ===== MONITORING =====
        if not self.dry_run:
            self.monitor_all_jobs()
            self.get_model_info()

        # ===== FINAL REPORT =====
        self.print_final_report()

        if self.dry_run:
            self.log("INFO", "🏁 Dry run completed successfully!")
            self.log(
                "INFO",
                "To execute actual training, run: python train_all_datasets.py --quick",
            )
        else:
            self.log("INFO", "🏁 Training pipeline completed!")


def main():
    parser = argparse.ArgumentParser(
        description="Train all available datasets for multilingual lecture assistant"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick training (small datasets, 1 epoch)",
    )
    parser.add_argument(
        "--full", action="store_true", help="Full training (large datasets, 5 epochs)"
    )
    parser.add_argument(
        "--monitor-only",
        action="store_true",
        help="Check status of existing training jobs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate training without actually running",
    )

    args = parser.parse_args()

    # Determine profile
    if args.quick:
        profile = "quick"
    elif args.full:
        profile = "full"
    else:
        profile = "balanced"  # default

    # Create orchestrator
    dry_run = args.dry_run or args.monitor_only
    orchestrator = TrainingOrchestrator(profile=profile, dry_run=dry_run)

    # Run training
    orchestrator.run_full_training()


if __name__ == "__main__":
    main()
