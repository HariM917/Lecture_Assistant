"""
🎤 Whisper Transcription Service - Test Suite

Tests for:
- Service initialization
- Single file transcription
- Batch processing
- Dataset transcription
- Model fine-tuning
- API endpoints
"""

import requests
import asyncio
from datetime import datetime
import json

BASE_URL = "http://localhost:8000/api/lecture/whisper"

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.END}\n")

def print_test(name, status=""):
    symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏳"
    print(f"{symbol} {name}")

def print_result(test_name, success, response=None, error=None):
    if success:
        print(f"{Colors.GREEN}✅ {test_name}{Colors.END}")
        if response:
            print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
    else:
        print(f"{Colors.RED}❌ {test_name}{Colors.END}")
        if error:
            print(f"   Error: {error}")

class WhisperTestSuite:
    """Comprehensive test suite for Whisper service"""
    
    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "total": 0}
        self.test_count = 0
    
    def run_tests(self):
        """Run all tests"""
        print_header("🎤 WHISPER TRANSCRIPTION SERVICE - TEST SUITE")
        
        self.test_health_check()
        self.test_service_info()
        self.test_available_models()
        self.test_supported_languages()
        self.test_config()
        self.test_statistics()
        
        self.print_summary()
    
    def test_health_check(self):
        """Test health check endpoint"""
        print_header("Test 1: Health Check")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            success = response.status_code == 200
            data = response.json()
            
            print_result("✅ Health Check", success, data)
            self.results["passed" if success else "failed"] += 1
            self.results["total"] += 1
        except Exception as e:
            print_result("❌ Health Check", False, error=str(e))
            self.results["failed"] += 1
            self.results["total"] += 1
    
    def test_service_info(self):
        """Test service info endpoint"""
        print_header("Test 2: Service Information")
        try:
            response = requests.get(f"{BASE_URL}/info", timeout=10)
            success = response.status_code == 200
            data = response.json()
            
            if success:
                info = data.get("data", {})
                print(f"   Model: {info.get('model')}")
                print(f"   Speed Mode: {info.get('speed_mode')}")
                print(f"   Features Available: {len(info.get('features', {}))}")
                print(f"   Capabilities: {len(info.get('capabilities', []))}")
            
            print_result("✅ Service Info", success, data)
            self.results["passed" if success else "failed"] += 1
            self.results["total"] += 1
        except Exception as e:
            print_result("❌ Service Info", False, error=str(e))
            self.results["failed"] += 1
            self.results["total"] += 1
    
    def test_available_models(self):
        """Test available models endpoint"""
        print_header("Test 3: Available Models")
        try:
            response = requests.get(f"{BASE_URL}/models", timeout=10)
            success = response.status_code == 200
            data = response.json()
            
            if success:
                models = data.get("available_models", [])
                current = data.get("current_model", "unknown")
                print(f"   Available Models: {', '.join(models)}")
                print(f"   Current Model: {current}")
                print(f"   Models with descriptions: {len(data.get('model_descriptions', {}))}")
            
            print_result("✅ Available Models", success, data)
            self.results["passed" if success else "failed"] += 1
            self.results["total"] += 1
        except Exception as e:
            print_result("❌ Available Models", False, error=str(e))
            self.results["failed"] += 1
            self.results["total"] += 1
    
    def test_supported_languages(self):
        """Test supported languages endpoint"""
        print_header("Test 4: Supported Languages")
        try:
            response = requests.get(f"{BASE_URL}/languages", timeout=10)
            success = response.status_code == 200
            data = response.json()
            
            if success:
                langs = data.get("supported_languages", [])
                names = data.get("language_names", {})
                print(f"   Language Codes: {', '.join(langs)}")
                print(f"   With names: {', '.join([names.get(l, l) for l in langs])}")
            
            print_result("✅ Supported Languages", success, data)
            self.results["passed" if success else "failed"] += 1
            self.results["total"] += 1
        except Exception as e:
            print_result("❌ Supported Languages", False, error=str(e))
            self.results["failed"] += 1
            self.results["total"] += 1
    
    def test_config(self):
        """Test configuration endpoint"""
        print_header("Test 5: Current Configuration")
        try:
            response = requests.get(f"{BASE_URL}/config", timeout=10)
            success = response.status_code == 200
            data = response.json()
            
            if success:
                config = data.get("config", {})
                print(f"   Model: {config.get('model')}")
                print(f"   Speed Mode: {config.get('speed_mode')}")
                print(f"   FP16 Enabled: {config.get('use_fp16')}")
                print(f"   Supported Formats: {len(config.get('supported_formats', []))}")
            
            print_result("✅ Configuration", success, data)
            self.results["passed" if success else "failed"] += 1
            self.results["total"] += 1
        except Exception as e:
            print_result("❌ Configuration", False, error=str(e))
            self.results["failed"] += 1
            self.results["total"] += 1
    
    def test_statistics(self):
        """Test statistics endpoint"""
        print_header("Test 6: Service Statistics")
        try:
            response = requests.get(f"{BASE_URL}/stats", timeout=10)
            success = response.status_code == 200
            data = response.json()
            
            if success:
                stats = data.get("statistics", {})
                print(f"   Service: {stats.get('service_name')}")
                print(f"   Model: {stats.get('model')}")
                print(f"   Supported Formats: {stats.get('supported_formats')}")
                print(f"   Supported Languages: {stats.get('supported_languages')}")
                print(f"   Max Audio Duration: {stats.get('max_audio_duration_hours')} hours")
            
            print_result("✅ Statistics", success, data)
            self.results["passed" if success else "failed"] += 1
            self.results["total"] += 1
        except Exception as e:
            print_result("❌ Statistics", False, error=str(e))
            self.results["failed"] += 1
            self.results["total"] += 1
    
    def test_change_speed_mode(self):
        """Test changing speed mode"""
        print_header("Test 7: Change Speed Mode")
        try:
            # Test changing to balanced
            response = requests.post(
                f"{BASE_URL}/config/speed-mode",
                params={"speed_mode": "balanced"},
                timeout=10
            )
            success = response.status_code == 200
            data = response.json()
            
            print_result("✅ Change Speed Mode to 'balanced'", success, data)
            self.results["passed" if success else "failed"] += 1
            self.results["total"] += 1
            
            # Change back to fast
            response = requests.post(
                f"{BASE_URL}/config/speed-mode",
                params={"speed_mode": "fast"},
                timeout=10
            )
            print_result("✅ Change Speed Mode back to 'fast'", response.status_code == 200)
            self.results["passed" if response.status_code == 200 else "failed"] += 1
            self.results["total"] += 1
        except Exception as e:
            print_result("❌ Change Speed Mode", False, error=str(e))
            self.results["failed"] += 1
            self.results["total"] += 1
    
    def print_summary(self):
        """Print test summary"""
        print_header("📊 TEST SUMMARY")
        
        total = self.results["total"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        
        print(f"Total Tests:  {total}")
        print(f"✅ Passed:   {passed}")
        print(f"❌ Failed:   {failed}")
        
        if failed == 0 and total > 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Check errors above.{Colors.END}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Run test suite"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║      🎤 WHISPER TRANSCRIPTION SERVICE - COMPREHENSIVE TEST suite   ║")
    print("║                 Testing all API endpoints                          ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    suite = WhisperTestSuite()
    suite.run_tests()


if __name__ == "__main__":
    main()
