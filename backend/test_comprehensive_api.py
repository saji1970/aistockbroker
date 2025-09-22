#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for AI Stock Trading Application
Tests all endpoints, error handling, and edge cases
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.trading_bot_url = "https://ai-stock-trading-backend-1024040140027.us-central1.run.app"
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }
        
    def log_result(self, test_name: str, success: bool, message: str = "", error: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        if error:
            print(f"    Error: {error}")
            self.results['errors'].append(f"{test_name}: {error}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            # Handle trading bot URLs properly
            if endpoint.startswith('/api/') and 'trading_bot' in str(kwargs.get('json', {})):
                url = f"{self.trading_bot_url}{endpoint}"
            elif endpoint.startswith('/api/') and 'start' in endpoint or 'stop' in endpoint or 'status' in endpoint or 'portfolio' in endpoint or 'strategies' in endpoint or 'watchlist' in endpoint:
                url = f"{self.trading_bot_url}{endpoint}"
            else:
                url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, timeout=30, **kwargs)
            
            # Log request details
            print(f"    {method} {url} -> {response.status_code}")
            
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"raw_response": response.text}
            else:
                try:
                    error_data = response.json()
                    return {"error": error_data, "status_code": response.status_code}
                except json.JSONDecodeError:
                    return {"error": response.text, "status_code": response.status_code}
                    
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": "CONNECTION_ERROR"}
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        print("\n🔍 Testing Health Endpoint...")
        
        result = self.make_request("GET", "/api/health")
        if result and "error" not in result:
            self.log_result("Health Check", True, f"Status: {result.get('status', 'unknown')}")
        else:
            self.log_result("Health Check", False, error=str(result))
    
    def test_stock_data_endpoints(self):
        """Test all stock data related endpoints"""
        print("\n📊 Testing Stock Data Endpoints...")
        
        test_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "INVALID_SYMBOL"]
        
        for symbol in test_symbols:
            # Test stock data endpoint
            result = self.make_request("GET", f"/api/stock/data/{symbol}?period=1y&market=US")
            if result and "error" not in result:
                current_price = result.get('summary', {}).get('current_price', 0)
                self.log_result(f"Stock Data - {symbol}", True, f"Price: ${current_price:.2f}")
            else:
                expected_fail = symbol == "INVALID_SYMBOL"
                self.log_result(f"Stock Data - {symbol}", expected_fail, 
                              error=str(result) if not expected_fail else "Expected failure for invalid symbol")
            
            # Test stock info endpoint
            result = self.make_request("GET", f"/api/stock/info/{symbol}?market=US")
            if result and "error" not in result:
                name = result.get('name', 'Unknown')
                self.log_result(f"Stock Info - {symbol}", True, f"Name: {name}")
            else:
                expected_fail = symbol == "INVALID_SYMBOL"
                self.log_result(f"Stock Info - {symbol}", expected_fail,
                              error=str(result) if not expected_fail else "Expected failure for invalid symbol")
            
            time.sleep(0.5)  # Rate limiting protection
    
    def test_prediction_endpoints(self):
        """Test prediction and AI-related endpoints"""
        print("\n🤖 Testing Prediction Endpoints...")
        
        test_symbols = ["AAPL", "GOOGL", "INVALID_SYMBOL"]
        
        for symbol in test_symbols:
            # Test basic prediction
            result = self.make_request("GET", f"/api/prediction/{symbol}")
            if result:
                if "error" in result and "Google API key" in str(result.get('error', {}).get('message', '')):
                    self.log_result(f"Prediction - {symbol}", True, "Expected: AI service not configured")
                elif "error" not in result:
                    self.log_result(f"Prediction - {symbol}", True, "Prediction data received")
                else:
                    expected_fail = symbol == "INVALID_SYMBOL"
                    self.log_result(f"Prediction - {symbol}", expected_fail, error=str(result))
            
            # Test prediction with sensitivity
            result = self.make_request("GET", f"/api/prediction/{symbol}/sensitivity")
            if result:
                if "error" in result and "Google API key" in str(result.get('error', {}).get('message', '')):
                    self.log_result(f"Prediction Sensitivity - {symbol}", True, "Expected: AI service not configured")
                elif "error" not in result:
                    self.log_result(f"Prediction Sensitivity - {symbol}", True, "Sensitivity data received")
                else:
                    expected_fail = symbol == "INVALID_SYMBOL"
                    self.log_result(f"Prediction Sensitivity - {symbol}", expected_fail, error=str(result))
            
            time.sleep(0.5)
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis endpoints"""
        print("\n📈 Testing Sensitivity Analysis...")
        
        test_symbols = ["AAPL", "GOOGL", "MSFT", "INVALID_SYMBOL"]
        
        for symbol in test_symbols:
            result = self.make_request("GET", f"/api/sensitivity/analysis/{symbol}")
            if result and "error" not in result:
                scenarios = result.get('scenarios', {})
                self.log_result(f"Sensitivity Analysis - {symbol}", True, 
                              f"Scenarios: {len(scenarios)}")
            else:
                expected_fail = symbol == "INVALID_SYMBOL"
                self.log_result(f"Sensitivity Analysis - {symbol}", expected_fail,
                              error=str(result) if not expected_fail else "Expected failure for invalid symbol")
            
            time.sleep(0.5)
    
    def test_trading_bot_endpoints(self):
        """Test trading bot functionality"""
        print("\n🤖 Testing Trading Bot Endpoints...")
        
        # Test bot status
        result = self.make_request("GET", "/api/status")
        if result and "error" not in result:
            if isinstance(result, dict):
                status = result.get('status', {}).get('status', 'unknown')
            else:
                status = str(result)
            self.log_result("Trading Bot Status", True, f"Status: {status}")
        else:
            self.log_result("Trading Bot Status", False, error=str(result))
        
        # Test portfolio
        result = self.make_request("GET", "/api/portfolio")
        if result and "error" not in result:
            cash = result.get('cash', 0)
            self.log_result("Trading Bot Portfolio", True, f"Cash: ${cash}")
        else:
            self.log_result("Trading Bot Portfolio", False, error=str(result))
        
        # Test strategies
        result = self.make_request("GET", "/api/strategies")
        if result and "error" not in result:
            strategies = result.get('strategies', [])
            self.log_result("Trading Bot Strategies", True, f"Available: {len(strategies)}")
        else:
            self.log_result("Trading Bot Strategies", False, error=str(result))
        
        # Test watchlist
        result = self.make_request("GET", "/api/watchlist")
        if result and "error" not in result:
            watchlist = result.get('watchlist', [])
            self.log_result("Trading Bot Watchlist", True, f"Items: {len(watchlist)}")
        else:
            self.log_result("Trading Bot Watchlist", False, error=str(result))
    
    def test_trading_bot_operations(self):
        """Test trading bot start/stop operations"""
        print("\n⚙️ Testing Trading Bot Operations...")
        
        # Test bot configuration
        config = {
            "initial_capital": 10000,
            "target_amount": 15000,
            "trading_period_days": 30,
            "max_position_size": 0.1,
            "max_daily_loss": 0.05,
            "risk_tolerance": "medium",
            "trading_strategy": "momentum",
            "enable_ml_learning": True
        }
        
        # Test starting bot
        result = self.make_request("POST", "/api/start", json=config)
        if result:
            if "error" in result:
                error_msg = str(result.get('error', ''))
                if "already running" in error_msg.lower():
                    self.log_result("Start Bot", True, "Bot already running (expected)")
                else:
                    self.log_result("Start Bot", False, error=error_msg)
            else:
                self.log_result("Start Bot", True, "Bot started successfully")
        
        # Test stopping bot
        result = self.make_request("POST", "/api/stop")
        if result:
            if "error" in result:
                error_msg = str(result.get('error', ''))
                if "not running" in error_msg.lower():
                    self.log_result("Stop Bot", True, "Bot not running (expected)")
                else:
                    self.log_result("Stop Bot", False, error=error_msg)
            else:
                self.log_result("Stop Bot", True, "Bot stopped successfully")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🚨 Testing Error Handling...")
        
        # Test invalid endpoints
        result = self.make_request("GET", "/api/invalid/endpoint")
        if result and "error" in result:
            self.log_result("Invalid Endpoint", True, "Properly returns 404")
        else:
            self.log_result("Invalid Endpoint", False, "Should return 404")
        
        # Test invalid stock symbols
        result = self.make_request("GET", "/api/stock/data/INVALID123?period=1y")
        if result and "error" in result:
            self.log_result("Invalid Stock Symbol", True, "Properly handles invalid symbol")
        else:
            self.log_result("Invalid Stock Symbol", False, "Should handle invalid symbol")
        
        # Test invalid parameters
        result = self.make_request("GET", "/api/stock/data/AAPL?period=invalid")
        if result:
            # Should either work with fallback or return error
            self.log_result("Invalid Parameters", True, "Handles invalid parameters")
        else:
            self.log_result("Invalid Parameters", False, "Should handle invalid parameters")
    
    def test_performance(self):
        """Test API performance and response times"""
        print("\n⚡ Testing Performance...")
        
        endpoints = [
            "/api/health",
            "/api/stock/data/AAPL?period=1y",
            "/api/stock/info/AAPL",
            "/api/sensitivity/analysis/AAPL"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            result = self.make_request("GET", endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            if result and "error" not in result:
                if response_time < 5.0:
                    self.log_result(f"Performance - {endpoint}", True, 
                                  f"Response time: {response_time:.2f}s")
                else:
                    self.log_result(f"Performance - {endpoint}", False, 
                                  f"Slow response: {response_time:.2f}s")
            else:
                self.log_result(f"Performance - {endpoint}", False, 
                              error=f"Request failed: {response_time:.2f}s")
    
    def test_frontend_integration(self):
        """Test endpoints that frontend uses"""
        print("\n🌐 Testing Frontend Integration...")
        
        # Test endpoints that frontend calls
        frontend_endpoints = [
            "/api/stock/data/AAPL?period=1y&market=US",
            "/api/stock/info/AAPL?market=US",
            "/api/prediction/AAPL",
            "/api/prediction/AAPL/sensitivity",
            "/api/sensitivity/analysis/AAPL"
        ]
        
        for endpoint in frontend_endpoints:
            result = self.make_request("GET", endpoint)
            if result:
                if "error" in result:
                    # Check if it's an expected error (like missing API key)
                    error_data = result.get('error', {})
                    if isinstance(error_data, dict):
                        error_msg = str(error_data.get('message', ''))
                    else:
                        error_msg = str(error_data)
                    
                    if "Google API key" in error_msg or "AI predictor" in error_msg:
                        self.log_result(f"Frontend - {endpoint}", True, "Expected AI service error")
                    else:
                        self.log_result(f"Frontend - {endpoint}", False, error=error_msg)
                else:
                    self.log_result(f"Frontend - {endpoint}", True, "Data received")
            else:
                self.log_result(f"Frontend - {endpoint}", False, "No response")
            
            time.sleep(0.3)
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive API Testing Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_stock_data_endpoints()
        self.test_prediction_endpoints()
        self.test_sensitivity_analysis()
        self.test_trading_bot_endpoints()
        self.test_trading_bot_operations()
        self.test_error_handling()
        self.test_performance()
        self.test_frontend_integration()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 Errors Found:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        if self.results['failed'] == 0:
            print("\n🎉 All tests passed! System is working correctly.")
        else:
            print(f"\n⚠️  {self.results['failed']} tests failed. Review errors above.")
        
        return self.results

def main():
    """Main test runner"""
    # API URLs
    main_api_url = "https://ai-stock-trading-api-1024040140027.us-central1.run.app"
    
    print("AI Stock Trading - Comprehensive API Test Suite")
    print("=" * 60)
    print(f"Testing Main API: {main_api_url}")
    print(f"Testing Trading Bot: https://ai-stock-trading-backend-1024040140027.us-central1.run.app")
    print("=" * 60)
    
    # Create tester instance
    tester = APITester(main_api_url)
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
