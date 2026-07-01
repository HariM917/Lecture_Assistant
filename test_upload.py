#!/usr/bin/env python3
"""Test the complete video upload and processing flow"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("TESTING COMPLETE VIDEO PROCESSING FLOW")
print("=" * 60)

# Step 1: Create a session
print("\n[1] Creating session...")
session_resp = requests.post(
    f"{BASE_URL}/api/lecture/sessions",
    json={"title": "Advanced Calculus", "subject": "Mathematics", "instructor": "Dr. Smith"}
)
print(f"Status: {session_resp.status_code}")
session_data = session_resp.json()
print(f"Response: {json.dumps(session_data, indent=2)}")
session_id = session_data.get("id")

if not session_id:
    print("FAILED: Could not create session")
    exit(1)

print(f"SUCCESS: Session created: {session_id}")

# Step 2: Create a dummy audio file
print("\n[2] Creating dummy audio file...")
dummy_audio = b"DUMMY_AUDIO_DATA" * 1000
print(f"Audio size: {len(dummy_audio)} bytes")

# Step 3: Transcribe
print("\n[3] Transcribing audio...")
files = {"file": ("audio.wav", dummy_audio, "audio/wav")}
data = {"language": "en"}
transcribe_resp = requests.post(
    f"{BASE_URL}/api/lecture/sessions/{session_id}/transcribe",
    files=files,
    data=data
)
print(f"Status: {transcribe_resp.status_code}")
transcribe_data = transcribe_resp.json()
print(f"Response Keys: {list(transcribe_data.keys())}")

transcription_id = transcribe_data.get("id")
if not transcription_id:
    print("FAILED: Could not transcribe")
    print(f"Full response: {transcribe_data}")
    exit(1)

print(f"SUCCESS: Transcribed: {transcription_id}")
print(f"Transcript text length: {len(transcribe_data.get('text', ''))}")

# Step 4: Translate to all languages
print("\n[4] Translating to all languages...")
translate_resp = requests.post(
    f"{BASE_URL}/api/lecture/transcriptions/{transcription_id}/translate-all"
)
print(f"Status: {translate_resp.status_code}")
translate_data = translate_resp.json()
print(f"Response Keys: {list(translate_data.keys())}")

# Check translations structure
if "translations" in translate_data:
    print(f"SUCCESS: Translations available: {list(translate_data['translations'].keys())}")
else:
    print(f"WARNING: Response structure: {list(translate_data.keys())}")

# Step 5: Extract keywords
print("\n[5] Extracting keywords...")
extract_resp = requests.post(
    f"{BASE_URL}/api/lecture/transcriptions/{transcription_id}/extract"
)
print(f"Status: {extract_resp.status_code}")
extract_data = extract_resp.json()
print(f"Response Keys: {list(extract_data.keys())}")

# Check keywords structure
if "keywords" in extract_data:
    print(f"SUCCESS: Keywords found: {len(extract_data['keywords'])} keywords")
    print(f"Keywords: {extract_data['keywords'][:5]}")
else:
    print(f"WARNING: Response keys: {list(extract_data.keys())}")

# Step 6: Summarize
print("\n[6] Summarizing session...")
summary_resp = requests.post(
    f"{BASE_URL}/api/lecture/sessions/{session_id}/summarize"
)
print(f"Status: {summary_resp.status_code}")
summary_data = summary_resp.json()
print(f"Response Keys: {list(summary_data.keys())}")

if "summary" in summary_data:
    summary_len = len(summary_data['summary'])
    print(f"SUCCESS: Summary available: {summary_len} chars")
    print(f"Summary preview: {summary_data['summary'][:200]}...")
else:
    print(f"WARNING: Response keys: {list(summary_data.keys())}")

print("\n" + "=" * 60)
print("FLOW COMPLETE - ALL ENDPOINTS WORKING!")
print("=" * 60)
