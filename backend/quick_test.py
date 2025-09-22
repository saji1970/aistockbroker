#!/usr/bin/env python3
"""
Quick Test Suite - Tests key functionality
"""

import requests
import time

def test_endpoint(url, name):
    """Test a single endpoint"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ {name}: {response.status_code} ({response_time:.2f}s)")
            return True
        else:
            print(f"❌ {name}: {response.status_code} ({response_time:.2f}s)")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
        return False

def main():
    print("🚀 Quick Functionality Test")
    print("=" * 50)
    
    # Test endpoints
    tests = [
        ("https://ai-stock-trading-api-1024040140027.us-central1.run.app/api/health", "Main API Health"),
        ("https://ai-stock-trading-api-1024040140027.us-central1.run.app/api/stock/data/AAPL?period=1y", "Stock Data"),
        ("https://ai-stock-trading-api-1024040140027.us-central1.run.app/api/stock/info/AAPL", "Stock Info"),
        ("https://ai-stock-trading-api-1024040140027.us-central1.run.app/api/sensitivity/analysis/AAPL", "Sensitivity Analysis"),
        ("https://ai-stock-trading-backend-1024040140027.us-central1.run.app/api/status", "Trading Bot Status"),
        ("https://ai-stock-trading-backend-1024040140027.us-central1.run.app/api/portfolio", "Trading Bot Portfolio"),
        ("https://ai-stock-trading-frontend-1024040140027.us-central1.run.app/", "Frontend"),
    ]
    
    passed = 0
    total = len(tests)
    
    for url, name in tests:
        if test_endpoint(url, name):
            passed += 1
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
    elif passed >= total * 0.8:
        print("👍 Most tests passed! System is mostly functional.")
    else:
        print("⚠️  Several tests failed. System needs attention.")

if __name__ == "__main__":
    main()
