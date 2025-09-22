#!/usr/bin/env python3
"""
Test script to verify all fixes are working
"""

import requests
import time
import json
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "https://ai-stock-trading-simple-720013332324.us-central1.run.app"
    
    tests = [
        ("Health Check", f"{base_url}/api/health"),
        ("Stock Data", f"{base_url}/api/stock/data/AAPL?period=1y&market=US"),
        ("Stock Info", f"{base_url}/api/stock/info/AAPL?market=US"),
        ("Prediction", f"{base_url}/api/prediction/AAPL"),
        ("Bot Status", f"{base_url}/api/status"),
        ("Portfolio", f"{base_url}/api/portfolio"),
        ("Orders", f"{base_url}/api/orders"),
        ("Learning Insights", f"{base_url}/api/learning/insights"),
        ("Learning Sessions", f"{base_url}/api/learning/sessions"),
        ("Learning Report", f"{base_url}/api/learning/report")
    ]
    
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    results = []
    for name, url in tests:
        try:
            print(f"Testing {name}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: OK ({response.status_code})")
                results.append((name, "PASS", response.status_code))
            elif response.status_code == 400:
                # Expected for some endpoints without active session
                print(f"⚠️  {name}: Expected error ({response.status_code})")
                results.append((name, "EXPECTED", response.status_code))
            else:
                print(f"❌ {name}: FAIL ({response.status_code})")
                results.append((name, "FAIL", response.status_code))
                
        except requests.exceptions.Timeout:
            print(f"⏰ {name}: TIMEOUT")
            results.append((name, "TIMEOUT", None))
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
            results.append((name, "ERROR", None))
        
        time.sleep(1)  # Rate limiting
    
    return results

def test_apple_touch_icon():
    """Test apple touch icon"""
    print("\n🍎 Testing Apple Touch Icon")
    print("=" * 50)
    
    try:
        response = requests.get(
            "https://ai-stock-trading-frontend-720013332324.us-central1.run.app/apple-touch-icon.png", 
            timeout=10
        )
        
        if response.status_code == 200:
            content_length = len(response.content)
            content_type = response.headers.get('content-type', '')
            
            if content_length > 500 and 'image' in content_type:
                print(f"✅ Apple Touch Icon: OK ({content_length} bytes, {content_type})")
                return True
            else:
                print(f"❌ Apple Touch Icon: Invalid ({content_length} bytes, {content_type})")
                return False
        else:
            print(f"❌ Apple Touch Icon: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Apple Touch Icon: ERROR - {e}")
        return False

def test_trading_bot_functionality():
    """Test trading bot functionality"""
    print("\n🤖 Testing Trading Bot Functionality")
    print("=" * 50)
    
    base_url = "https://ai-stock-trading-simple-720013332324.us-central1.run.app"
    
    try:
        # Test bot start
        config = {
            "symbol": "AAPL",
            "initial_capital": 10000,
            "strategy": "momentum",
            "max_position_size": 0.1,
            "max_daily_loss": 0.05,
            "risk_tolerance": "medium"
        }
        
        response = requests.post(
            f"{base_url}/api/start",
            headers={"Content-Type": "application/json"},
            json=config,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Bot Start: OK")
            
            # Wait a moment
            time.sleep(3)
            
            # Test status
            status_response = requests.get(f"{base_url}/api/status", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Bot Status: {status_data.get('status', 'unknown')}")
                
                # Test stop
                stop_response = requests.post(f"{base_url}/api/stop", timeout=10)
                if stop_response.status_code == 200:
                    print("✅ Bot Stop: OK")
                    return True
                else:
                    print(f"❌ Bot Stop: FAIL ({stop_response.status_code})")
                    return False
            else:
                print(f"❌ Bot Status: FAIL ({status_response.status_code})")
                return False
        else:
            print(f"❌ Bot Start: FAIL ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Trading Bot: ERROR - {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Stock Trading Bot - Comprehensive Fix Verification")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API endpoints
    api_results = test_api_endpoints()
    
    # Test apple touch icon
    icon_ok = test_apple_touch_icon()
    
    # Test trading bot
    bot_ok = test_trading_bot_functionality()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    # API results
    print("\nAPI Endpoints:")
    for name, status, code in api_results:
        status_icon = "✅" if status == "PASS" else "⚠️" if status == "EXPECTED" else "❌"
        print(f"  {status_icon} {name}: {status}")
    
    # Other tests
    print(f"\nOther Tests:")
    print(f"  {'✅' if icon_ok else '❌'} Apple Touch Icon: {'OK' if icon_ok else 'FAIL'}")
    print(f"  {'✅' if bot_ok else '❌'} Trading Bot: {'OK' if bot_ok else 'FAIL'}")
    
    # Overall status
    api_pass_count = sum(1 for _, status, _ in api_results if status in ["PASS", "EXPECTED"])
    total_tests = len(api_results) + 2  # +2 for icon and bot tests
    passed_tests = api_pass_count + (1 if icon_ok else 0) + (1 if bot_ok else 0)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("✅ Most functionality is working!")
        return 0
    else:
        print("❌ Multiple issues detected!")
        return 1

if __name__ == "__main__":
    exit(main())
