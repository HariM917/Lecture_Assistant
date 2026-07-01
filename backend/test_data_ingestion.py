"""
Test script for Data Ingestion & Model Training endpoints
Run this to verify all endpoints are working correctly
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_PREFIX = f"{BASE_URL}/api/lecture/data"


def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{API_PREFIX}/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_dataset_info():
    """Test dataset info endpoint"""
    response = requests.get(f"{API_PREFIX}/dataset/info")
    print_response("Get Dataset Info", response)
    return response.status_code == 200


def test_supported_languages():
    """Test supported languages endpoint"""
    response = requests.get(f"{API_PREFIX}/dataset/languages")
    print_response("Get Supported Languages", response)
    return response.status_code == 200


def test_prepare_training_data():
    """Test prepare training data endpoint"""
    response = requests.post(
        f"{API_PREFIX}/dataset/prepare",
        params={"max_samples_per_language": 50}
    )
    print_response("Prepare Training Data (50 samples/language)", response)
    return response.status_code == 200


def test_analyze_dataset():
    """Test analyze dataset endpoint"""
    response = requests.get(f"{API_PREFIX}/dataset/analyze")
    print_response("Analyze Dataset", response)
    return response.status_code == 200


def test_analyze_language():
    """Test analyze specific language"""
    response = requests.get(
        f"{API_PREFIX}/dataset/analyze",
        params={"language": "ta"}
    )
    print_response("Analyze Dataset (Tamil)", response)
    return response.status_code == 200


def test_list_models():
    """Test list available models endpoint"""
    response = requests.get(f"{API_PREFIX}/training/models")
    print_response("List Available Models", response)
    return response.status_code == 200


def test_start_training():
    """Test start training endpoint"""
    response = requests.post(
        f"{API_PREFIX}/training/start",
        params={
            "language": "en",
            "batch_size": 32,
            "num_epochs": 3
        }
    )
    print_response("Start Training (English)", response)
    
    if response.status_code == 200:
        return response.json().get("job_id")
    return None


def test_training_status(job_id: str):
    """Test get training status endpoint"""
    response = requests.get(f"{API_PREFIX}/training/status/{job_id}")
    print_response(f"Get Training Status ({job_id})", response)
    return response.status_code == 200 if job_id else False


def test_download_dataset():
    """Test download dataset endpoint"""
    response = requests.post(
        f"{API_PREFIX}/dataset/download",
        params={
            "source": "auto",
            "languages": "en,ta,hi"
        }
    )
    print_response("Download Dataset (English, Tamil, Hindi)", response)
    return response.status_code == 200


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("🧪 DATA INGESTION SERVICE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Dataset Info", test_dataset_info),
        ("Supported Languages", test_supported_languages),
        ("Analyze Dataset", test_analyze_dataset),
        ("Analyze Language", test_analyze_language),
        ("List Models", test_list_models),
        ("Prepare Training Data", test_prepare_training_data),
        ("Start Training", test_start_training),
        ("Download Dataset", test_download_dataset),
    ]
    
    results = {}
    job_id = None
    
    for test_name, test_func in tests:
        try:
            print(f"\n▶ Running: {test_name}...", end=" ", flush=True)
            
            # Special handling for test_start_training which returns job_id
            if test_name == "Start Training":
                job_id = test_func()
                results[test_name] = "✅" if job_id else "❌"
                print(results[test_name])
            else:
                result = test_func()
                results[test_name] = "✅" if result else "❌"
                print(results[test_name])
        except Exception as e:
            results[test_name] = f"❌ {str(e)}"
            print(f"❌ {str(e)}")
    
    # If job_id created, test status
    if job_id:
        try:
            print(f"\n▶ Running: Training Status Check...", end=" ", flush=True)
            result = test_training_status(job_id)
            results["Training Status"] = "✅" if result else "❌"
            print(results["Training Status"])
        except Exception as e:
            results["Training Status"] = f"❌ {str(e)}"
            print(f"❌ {str(e)}")
    
    # Summary report
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v == "✅")
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{result} {test_name}")
    
    print(f"\n🎯 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Data ingestion service is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
    
    return passed == total


if __name__ == "__main__":
    print("\n🚀 Starting Data Ingestion Service Tests\n")
    print("Prerequisites:")
    print("  1. Backend running: docker compose up --build")
    print("  2. API accessible at: http://localhost:8000")
    print("  3. Database connected")
    
    input("\nPress Enter to start tests...")
    
    try:
        success = run_all_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        exit_code = 1
    
    print(f"\n{'='*60}")
    print("Test run complete!")
    print(f"{'='*60}\n")
    
    exit(exit_code)
