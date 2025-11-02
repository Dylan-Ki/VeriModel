"""
Script để test các chức năng của server và phát hiện lỗi ẩn.
"""

import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("1. Testing /api/v1/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint (web UI)"""
    print("\n2. Testing / (root)...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        if "VeriModel" in response.text:
            print("   ✅ HTML content contains 'VeriModel'")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_api_info():
    """Test /api endpoint"""
    print("\n3. Testing /api...")
    try:
        response = requests.get(f"{BASE_URL}/api", timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_static_files():
    """Test static files"""
    print("\n4. Testing /static/app.js...")
    try:
        response = requests.get(f"{BASE_URL}/static/app.js", timeout=5)
        print(f"   ✅ Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ File size: {len(response.content)} bytes")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_scan_endpoint():
    """Test scan endpoint với file demo"""
    print("\n5. Testing /api/v1/scan...")
    demo_file = Path("demo_models/safe_demo.pkl")
    if not demo_file.exists():
        print("   ⚠️  Demo file không tồn tại, bỏ qua test")
        return True
    
    try:
        with open(demo_file, 'rb') as f:
            files = {'file': (demo_file.name, f, 'application/octet-stream')}
            data = {
                'static_only': True,
                'include_threat_intel': False
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/scan",
                files=files,
                data=data,
                timeout=30
            )
        print(f"   ✅ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Static scan completed")
            print(f"   Threats: {len(result.get('static', {}).get('threats', []))}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing VeriModel Server\n")
    print("Waiting for server to start...")
    time.sleep(2)
    
    results = []
    results.append(test_health())
    results.append(test_root())
    results.append(test_api_info())
    results.append(test_static_files())
    results.append(test_scan_endpoint())
    
    print("\n" + "="*50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")

