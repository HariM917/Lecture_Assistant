"""
Test script for Translation Training endpoints
Validates all translation model training functionality
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_PREFIX = f"{BASE_URL}/api/lecture/translation"


def print_response(title: str, response: requests.Response, show_full: bool = True):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        if show_full:
            print(json.dumps(data, indent=2))
        else:
            # Show abbreviated response
            if isinstance(data, dict):
                for key, value in list(data.items())[:5]:
                    print(f"{key}: {value}")
    except:
        print(response.text if response.text else "[No response body]")


def test_health_check():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_PREFIX}/health")
        print_response("Health Check", response, show_full=True)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_service_info():
    """Test service info endpoint"""
    try:
        response = requests.get(f"{API_PREFIX}/info")
        print_response("Service Info", response, show_full=True)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Service info failed: {e}")
        return False


def test_language_pairs():
    """Test language pairs endpoint"""
    try:
        response = requests.get(f"{API_PREFIX}/language-pairs")
        print_response("Language Pairs", response, show_full=True)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Language pairs failed: {e}")
        return False


def test_get_datasets():
    """Test get datasets endpoint"""
    try:
        response = requests.get(f"{API_PREFIX}/datasets")
        print_response("Available Datasets", response, show_full=True)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get datasets failed: {e}")
        return False


def test_prepare_data():
    """Test prepare translation data endpoint"""
    try:
        response = requests.post(
            f"{API_PREFIX}/prepare",
            params={
                "language_pair": "en-hi",
                "max_samples": 100
            }
        )
        print_response("Prepare Translation Data (English-Hindi, 100 samples)", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Prepare data failed: {e}")
        return False


def test_validate_dataset():
    """Test validate dataset endpoint"""
    try:
        response = requests.post(
            f"{API_PREFIX}/validate-dataset",
            params={
                "dataset_name": "english_hindi_podcast",
                "language_pair": "en-hi"
            }
        )
        print_response("Validate Dataset", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Validate dataset failed: {e}")
        return False


def test_list_models():
    """Test list translation models endpoint"""
    try:
        response = requests.get(f"{API_PREFIX}/training/models")
        print_response("List Translation Models", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ List models failed: {e}")
        return False


def test_start_training():
    """Test start training endpoint"""
    try:
        response = requests.post(
            f"{API_PREFIX}/training/start",
            params={
                "language_pair": "en-hi",
                "batch_size": 16,
                "num_epochs": 3,
                "learning_rate": 5e-5
            }
        )
        print_response("Start Translation Training (English-Hindi)", response)
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            return job_id
        return None
    except Exception as e:
        print(f"❌ Start training failed: {e}")
        return None


def test_training_status(job_id: str):
    """Test get training status endpoint"""
    try:
        response = requests.get(f"{API_PREFIX}/training/status/{job_id}")
        print_response(f"Get Training Status ({job_id})", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Get status failed: {e}")
        return False


def test_evaluate_model():
    """Test evaluate model endpoint"""
    try:
        response = requests.post(
            f"{API_PREFIX}/evaluate",
            params={
                "language_pair": "en-hi",
                "model_version": "latest"
            }
        )
        print_response("Evaluate Translation Model (English-Hindi)", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Evaluate model failed: {e}")
        return False


def test_tamil_translation():
    """Test Tamil translation setup"""
    try:
        response = requests.post(
            f"{API_PREFIX}/prepare",
            params={
                "language_pair": "en-ta",
                "max_samples": 50
            }
        )
        print_response("Prepare Tamil Translation Data (English-Tamil, 50 samples)", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Tamil translation failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("🧪 TRANSLATION TRAINING SERVICE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Service Info", test_service_info),
        ("Language Pairs", test_language_pairs),
        ("Available Datasets", test_get_datasets),
        ("List Models", test_list_models),
        ("Prepare Data (Hindi)", test_prepare_data),
        ("Validate Dataset", test_validate_dataset),
        ("Prepare Tamil Data", test_tamil_translation),
        ("Start Training", test_start_training),
        ("Evaluate Model", test_evaluate_model),
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
            results[test_name] = f"❌ {str(e)[:30]}"
            print(f"❌ {str(e)[:30]}")
    
    # If job_id created, test status
    if job_id:
        try:
            print(f"\n▶ Running: Training Status Check...", end=" ", flush=True)
            result = test_training_status(job_id)
            results["Training Status"] = "✅" if result else "❌"
            print(results["Training Status"])
        except Exception as e:
            results["Training Status"] = f"❌ {str(e)[:30]}"
            print(f"❌ {str(e)[:30]}")
    
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
        print("\n✅ All tests passed! Translation training service is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
    
    return passed == total


if __name__ == "__main__":
    print("\n🚀 Starting Translation Training Service Tests\n")
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
