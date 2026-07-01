# Data Ingestion Quick Reference

## 🚀 5-Minute Setup

```bash
# 1. Requirements are already added to requirements.txt
# 2. Start backend
cd multilingual-lecture-assistant
docker compose up --build

# 3. In another terminal, test the service
python test_data_ingestion.py
```

---

## 📋 Essential API Endpoints

### Get Information
```bash
# All available info
curl http://localhost:8000/api/lecture/data/dataset/info

# Supported languages
curl http://localhost:8000/api/lecture/data/dataset/languages
```

### Prepare Data
```bash
# Prepare 100 samples per language
curl -X POST http://localhost:8000/api/lecture/data/dataset/prepare \
  -G --data-urlencode "max_samples_per_language=100"

# Prepare 500 samples (for production)
curl -X POST http://localhost:8000/api/lecture/data/dataset/prepare \
  -G --data-urlencode "max_samples_per_language=500"
```

### Train Models
```bash
# Train on English (32 batch, 3 epochs)
curl -X POST http://localhost:8000/api/lecture/data/training/start \
  -G \
  --data-urlencode "language=en" \
  --data-urlencode "batch_size=32" \
  --data-urlencode "num_epochs=3"

# Train on Tamil (smaller batch for memory efficiency)
curl -X POST http://localhost:8000/api/lecture/data/training/start \
  -G \
  --data-urlencode "language=ta" \
  --data-urlencode "batch_size=16" \
  --data-urlencode "num_epochs=5"
```

### Monitor Training
```bash
# Check job status (replace with actual job_id)
curl http://localhost:8000/api/lecture/data/training/status/train_en_32b_3e

# List all models
curl http://localhost:8000/api/lecture/data/training/models
```

---

## 🎯 Common Use Cases

### Use Case 1: Fine-tune English Model
```bash
# 1. Get available info
curl http://localhost:8000/api/lecture/data/dataset/info

# 2. Prepare data
curl -X POST http://localhost:8000/api/lecture/data/dataset/prepare \
  -G --data-urlencode "max_samples_per_language=200"

# 3. Start training
curl -X POST http://localhost:8000/api/lecture/data/training/start \
  -G \
  --data-urlencode "language=en" \
  --data-urlencode "batch_size=32" \
  --data-urlencode "num_epochs=3"

# 4. Monitor (every 30 seconds)
watch -n 30 'curl http://localhost:8000/api/lecture/data/training/status/train_en_32b_3e'
```

### Use Case 2: Train All 6 Languages
```bash
# Prepare once
curl -X POST http://localhost:8000/api/lecture/data/dataset/prepare \
  -G --data-urlencode "max_samples_per_language=100"

# Start training for each language
for lang in en ta hi te kn ml; do
  echo "Training $lang..."
  curl -X POST http://localhost:8000/api/lecture/data/training/start \
    -G \
    --data-urlencode "language=$lang" \
    --data-urlencode "batch_size=16" \
    --data-urlencode "num_epochs=3"
  sleep 5  # Wait between requests
done
```

### Use Case 3: Download Dataset Only
```bash
# Download specific languages
curl -X POST http://localhost:8000/api/lecture/data/dataset/download \
  -G \
  --data-urlencode "source=auto" \
  --data-urlencode "languages=en,ta,hi"

# Download all
curl -X POST http://localhost:8000/api/lecture/data/dataset/download \
  -G --data-urlencode "source=anandhu"
```

---

## 🔧 Python Snippets

### Load Dataset Directly
```python
from datasets import load_dataset

# Load ANANDHU dataset
ds = load_dataset("ANANDHU-SCT/Speech-to-text")

# Access a sample
sample = ds['train'][0]
print(f"Audio: {sample['audio']}")
print(f"Text: {sample['sentence']}")
```

### Using the Service (Python)
```python
from services.data_ingestion import STTModelTrainer

# Initialize
trainer = STTModelTrainer()

# Get info
info = trainer.get_dataset_info()
print(info)

# Prepare data
prep_stats = trainer.prepare_training_data(max_samples_per_language=100)
print(prep_stats)
```

### API Client (Python)
```python
import requests

api = "http://localhost:8000/api/lecture/data"

# Get languages
langs = requests.get(f"{api}/dataset/languages").json()
print(langs["languages"])

# Start training
job = requests.post(
    f"{api}/training/start",
    params={"language": "en", "batch_size": 32, "num_epochs": 3}
).json()
print(f"Job ID: {job['job_id']}")

# Monitor
status = requests.get(f"{api}/training/status/{job['job_id']}").json()
print(f"Progress: {status['progress']['percentage']}%")
```

### Frontend Integration (JavaScript)
```javascript
const API = 'http://localhost:8000/api/lecture/data';

// Get supported languages
async function getLanguages() {
    const res = await fetch(`${API}/dataset/languages`);
    return (await res.json()).languages;
}

// Start training
async function trainModel(language = 'en') {
    const res = await fetch(
        `${API}/training/start?language=${language}&batch_size=32&num_epochs=3`,
        { method: 'POST' }
    );
    return await res.json();
}

// Get job status
async function getStatus(jobId) {
    const res = await fetch(`${API}/training/status/${jobId}`);
    return await res.json();
}

// Usage
const jobData = await trainModel('ta');
console.log(`Training started: ${jobData.job_id}`);

// Monitor every 5 seconds
const interval = setInterval(async () => {
    const status = await getStatus(jobData.job_id);
    console.log(`${status.progress.percentage}% - Loss: ${status.metrics.train_loss}`);
    if (status.training_status === 'completed') {
        clearInterval(interval);
        console.log('Training complete!');
    }
}, 5000);
```

---

## 📊 Supported Languages

| Code | Language | Status | WER Target |
|------|----------|--------|-----------|
| en | English | ✅ | 0.08 |
| ta | Tamil | ✅ | 0.15 |
| hi | Hindi | ✅ | 0.18 |
| te | Telugu | ✅ | 0.20 |
| kn | Kannada | ✅ | 0.22 |
| ml | Malayalam | ✅ | 0.25 |

---

## ⚙️ Configuration Values

```bash
# Dataset samples per language
--data-urlencode "max_samples_per_language=100"  # Default
# Range: 10-1000

# Training batch size
--data-urlencode "batch_size=32"  # Default
# Range: 8-256
# Use 8-16 for large models or limited RAM
# Use 64-128 for GPU training

# Number of epochs
--data-urlencode "num_epochs=3"  # Default
# Range: 1-10
# Typical: 3-5 epochs for good convergence
```

---

## 🐛 Quick Troubleshooting

### Service not responding
```bash
# Check if backend is running
curl http://localhost:8000/api/lecture/health

# If not, restart
docker compose restart api
```

### Dataset download fails
```bash
# Check internet connection
ping huggingface.co

# Clear cache and retry
rm -rf hf_cache/

# Restart and re-prepare
curl -X POST http://localhost:8000/api/lecture/data/dataset/prepare
```

### Training job stuck
```bash
# Check job status
curl http://localhost:8000/api/lecture/data/training/status/{job_id}

# If stuck, restart backend
docker compose restart api
```

### Out of memory during training
```bash
# Reduce batch size
curl -X POST http://localhost:8000/api/lecture/data/training/start \
  -G \
  --data-urlencode "language=en" \
  --data-urlencode "batch_size=8"  # Reduced from 32
```

---

## 📁 File Structure

```
multilingual-lecture-assistant/
├── services/
│   └── data_ingestion.py          # ← Data ingestion service
├── api/routes/
│   └── data_ingestion.py          # ← API endpoints
├── main.py                         # ← Routes registered here
├── requirements.txt                # ← New dependencies added
├── DATA_INGESTION.md              # ← Full documentation
├── test_data_ingestion.py         # ← Test script
└── docker-compose.yml             # ← Container config
```

---

## 🚀 Next Steps

1. **Run tests**: `python test_data_ingestion.py`
2. **Prepare data**: `POST /api/lecture/data/dataset/prepare`
3. **Start training**: `POST /api/lecture/data/training/start`
4. **Monitor job**: `GET /api/lecture/data/training/status/{job_id}`
5. **Deploy model**: Use trained model in production

---

## 📚 Resources

- Full Documentation: `DATA_INGESTION.md`
- System Overview: `COMPLETE_SYSTEM.md`
- API Docs: http://localhost:8000/docs
- Hugging Face: https://huggingface.co/ANANDHU-SCT/Speech-to-text

---

**Ready?** Start the backend and run the test script! 🎓
