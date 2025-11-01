#!/usr/bin/env python3
"""
Test script for LMArena API Proxy Server
Tests the server's basic functionality without requiring browser connection
"""
import json
import time
import sys
from pathlib import Path

# Add the server directory to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

# Import server components
import uvicorn
from multiprocessing import Process
import requests

def start_server():
    """Start the proxy server in a separate process"""
    from server.proxy_server import app, Config
    uvicorn.run(app, host="127.0.0.1", port=9080, log_level="warning")

def test_server_endpoints():
    """Test various server endpoints"""
    base_url = "http://127.0.0.1:9080"
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    def add_test_result(name, passed, message=""):
        results["total_tests"] += 1
        if passed:
            results["passed"] += 1
            status = "✓ PASS"
        else:
            results["failed"] += 1
            status = "✗ FAIL"
        
        results["tests"].append({
            "name": name,
            "passed": passed,
            "message": message
        })
        print(f"{status}: {name}")
        if message:
            print(f"  Message: {message}")
    
    # Wait for server to start
    print("\n⏳ Waiting for server to start...")
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                print("✓ Server is ready!\n")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        if i == max_attempts - 1:
            print("✗ Server failed to start in time\n")
            return results
    
    # Test 1: Health Check
    print("Running tests...\n")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        passed = response.status_code == 200 and "status" in response.json()
        data = response.json()
        add_test_result(
            "Health Check Endpoint",
            passed,
            f"Status: {data.get('status', 'N/A')}, Uptime: {data.get('uptime', 0):.2f}s"
        )
    except Exception as e:
        add_test_result("Health Check Endpoint", False, str(e))
    
    # Test 2: Detailed Health
    try:
        response = requests.get(f"{base_url}/api/health/detailed", timeout=5)
        passed = response.status_code == 200
        data = response.json()
        add_test_result(
            "Detailed Health Endpoint",
            passed,
            f"Status: {data.get('status', 'N/A')}, Score: {data.get('health_score', 0)}"
        )
    except Exception as e:
        add_test_result("Detailed Health Endpoint", False, str(e))
    
    # Test 3: Models List
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=5)
        passed = response.status_code == 200 and "data" in response.json()
        data = response.json()
        model_count = len(data.get("data", []))
        add_test_result(
            "Models List Endpoint",
            passed,
            f"Found {model_count} models"
        )
    except Exception as e:
        add_test_result("Models List Endpoint", False, str(e))
    
    # Test 4: Prometheus Metrics
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        passed = response.status_code == 200 and "lmarena" in response.text
        add_test_result(
            "Prometheus Metrics Endpoint",
            passed,
            f"Metrics available: {len(response.text.splitlines())} lines"
        )
    except Exception as e:
        add_test_result("Prometheus Metrics Endpoint", False, str(e))
    
    # Test 5: Stats Summary
    try:
        response = requests.get(f"{base_url}/api/stats/summary", timeout=5)
        passed = response.status_code == 200 and "summary" in response.json()
        data = response.json()
        add_test_result(
            "Stats Summary Endpoint",
            passed,
            f"Active requests: {data.get('active_requests', 0)}"
        )
    except Exception as e:
        add_test_result("Stats Summary Endpoint", False, str(e))
    
    # Test 6: Configuration Endpoint
    try:
        response = requests.get(f"{base_url}/api/config", timeout=5)
        passed = response.status_code == 200 and isinstance(response.json(), dict)
        add_test_result(
            "Configuration Endpoint",
            passed,
            "Configuration retrieved successfully"
        )
    except Exception as e:
        add_test_result("Configuration Endpoint", False, str(e))
    
    # Test 7: System Info
    try:
        response = requests.get(f"{base_url}/api/system/info", timeout=5)
        passed = response.status_code == 200 and "server_urls" in response.json()
        data = response.json()
        add_test_result(
            "System Info Endpoint",
            passed,
            f"Local URL: {data.get('server_urls', {}).get('local', 'N/A')}"
        )
    except Exception as e:
        add_test_result("System Info Endpoint", False, str(e))
    
    # Test 8: Monitor HTML Page
    try:
        response = requests.get(f"{base_url}/monitor", timeout=5)
        passed = response.status_code == 200 and "html" in response.headers.get("content-type", "").lower()
        add_test_result(
            "Monitor Dashboard",
            passed,
            f"Content length: {len(response.text)} bytes"
        )
    except Exception as e:
        add_test_result("Monitor Dashboard", False, str(e))
    
    # Test 9: Request Logs
    try:
        response = requests.get(f"{base_url}/api/logs/requests", timeout=5)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        add_test_result(
            "Request Logs Endpoint",
            passed,
            f"Logs available: {len(response.json())} entries"
        )
    except Exception as e:
        add_test_result("Request Logs Endpoint", False, str(e))
    
    # Test 10: Error Logs
    try:
        response = requests.get(f"{base_url}/api/logs/errors", timeout=5)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        add_test_result(
            "Error Logs Endpoint",
            passed,
            f"Error logs available: {len(response.json())} entries"
        )
    except Exception as e:
        add_test_result("Error Logs Endpoint", False, str(e))
    
    return results

def main():
    """Main test execution"""
    print("=" * 60)
    print("🧪 LMArena API Server Test Suite")
    print("=" * 60)
    
    # Start server in a separate process
    server_process = Process(target=start_server, daemon=True)
    server_process.start()
    
    try:
        # Run tests
        results = test_server_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']} ✓")
        print(f"Failed: {results['failed']} ✗")
        if results['total_tests'] > 0:
            print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
        else:
            print("Success Rate: N/A (no tests run)")
        print("=" * 60)
        
        # Exit with appropriate code
        if results['failed'] == 0:
            print("\n✓ All tests passed! Server is working correctly.")
            return 0
        else:
            print(f"\n✗ {results['failed']} test(s) failed.")
            return 1
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            server_process.kill()
        print("✓ Server stopped")

if __name__ == "__main__":
    sys.exit(main())
