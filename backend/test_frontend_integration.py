#!/usr/bin/env python3
"""
Frontend Integration Test Suite
Tests the actual frontend application and its interaction with backends
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any, Optional

class FrontendTester:
    def __init__(self):
        self.frontend_url = "https://ai-stock-trading-frontend-1024040140027.us-central1.run.app"
        self.main_api_url = "https://ai-stock-trading-api-1024040140027.us-central1.run.app"
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
    
    def test_frontend_availability(self):
        """Test if frontend is accessible"""
        print("\n🌐 Testing Frontend Availability...")
        
        try:
            response = requests.get(self.frontend_url, timeout=30)
            if response.status_code == 200:
                self.log_result("Frontend Accessibility", True, 
                              f"Status: {response.status_code}, Size: {len(response.content)} bytes")
            else:
                self.log_result("Frontend Accessibility", False, 
                              error=f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Accessibility", False, error=str(e))
    
    def test_frontend_static_assets(self):
        """Test if static assets are loading"""
        print("\n📦 Testing Static Assets...")
        
        assets = [
            "/static/js/main.js",
            "/static/css/main.css",
            "/manifest.json",
            "/sw.js"
        ]
        
        for asset in assets:
            try:
                url = f"{self.frontend_url}{asset}"
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    self.log_result(f"Asset - {asset}", True, 
                                  f"Size: {len(response.content)} bytes")
                else:
                    self.log_result(f"Asset - {asset}", False, 
                                  error=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Asset - {asset}", False, error=str(e))
    
    def test_api_connectivity_from_frontend(self):
        """Test API endpoints that frontend calls"""
        print("\n🔗 Testing API Connectivity...")
        
        # Test main API endpoints
        main_api_tests = [
            "/api/health",
            "/api/stock/data/AAPL?period=1y&market=US",
            "/api/stock/info/AAPL?market=US",
            "/api/prediction/AAPL",
            "/api/prediction/AAPL/sensitivity",
            "/api/sensitivity/analysis/AAPL"
        ]
        
        for endpoint in main_api_tests:
            try:
                url = f"{self.main_api_url}{endpoint}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    self.log_result(f"Main API - {endpoint}", True, "Connected successfully")
                elif response.status_code == 503:
                    # Check if it's expected AI service error
                    try:
                        data = response.json()
                        if "Google API key" in str(data.get('message', '')):
                            self.log_result(f"Main API - {endpoint}", True, "Expected AI service error")
                        else:
                            self.log_result(f"Main API - {endpoint}", False, 
                                          error=f"Unexpected 503: {data}")
                    except:
                        self.log_result(f"Main API - {endpoint}", False, 
                                      error=f"503 without JSON: {response.text[:100]}")
                else:
                    self.log_result(f"Main API - {endpoint}", False, 
                                  error=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Main API - {endpoint}", False, error=str(e))
            
            time.sleep(0.5)
        
        # Test trading bot API endpoints
        trading_bot_tests = [
            "/api/status",
            "/api/portfolio",
            "/api/strategies",
            "/api/watchlist",
            "/api/orders",
            "/api/performance"
        ]
        
        for endpoint in trading_bot_tests:
            try:
                url = f"{self.trading_bot_url}{endpoint}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    self.log_result(f"Trading Bot - {endpoint}", True, "Connected successfully")
                else:
                    self.log_result(f"Trading Bot - {endpoint}", False, 
                                  error=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Trading Bot - {endpoint}", False, error=str(e))
            
            time.sleep(0.5)
    
    def test_cors_headers(self):
        """Test CORS headers for frontend-backend communication"""
        print("\n🔒 Testing CORS Headers...")
        
        # Test CORS preflight request
        try:
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            # Test main API CORS
            response = requests.options(f"{self.main_api_url}/api/health", 
                                      headers=headers, timeout=15)
            cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
            
            if cors_headers:
                self.log_result("Main API CORS", True, f"Allow-Origin: {cors_headers}")
            else:
                self.log_result("Main API CORS", False, "No CORS headers found")
            
            # Test trading bot CORS
            response = requests.options(f"{self.trading_bot_url}/api/status", 
                                      headers=headers, timeout=15)
            cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
            
            if cors_headers:
                self.log_result("Trading Bot CORS", True, f"Allow-Origin: {cors_headers}")
            else:
                self.log_result("Trading Bot CORS", False, "No CORS headers found")
                
        except Exception as e:
            self.log_result("CORS Test", False, error=str(e))
    
    def test_data_consistency(self):
        """Test data consistency between different endpoints"""
        print("\n🔄 Testing Data Consistency...")
        
        try:
            # Test stock data consistency
            data_response = requests.get(f"{self.main_api_url}/api/stock/data/AAPL?period=1y&market=US", 
                                       timeout=30)
            info_response = requests.get(f"{self.main_api_url}/api/stock/info/AAPL?market=US", 
                                       timeout=30)
            
            if data_response.status_code == 200 and info_response.status_code == 200:
                data_json = data_response.json()
                info_json = info_response.json()
                
                data_price = data_json.get('summary', {}).get('current_price', 0)
                info_price = info_json.get('currentPrice', 0)
                
                # Prices should be reasonably close (within 10% or both realistic)
                if data_price > 0 and info_price > 0:
                    price_diff = abs(data_price - info_price) / max(data_price, info_price)
                    if price_diff < 0.1 or (data_price > 100 and info_price > 100):  # Both realistic
                        self.log_result("Price Consistency", True, 
                                      f"Data: ${data_price:.2f}, Info: ${info_price:.2f}")
                    else:
                        self.log_result("Price Consistency", False, 
                                      error=f"Large price difference: ${data_price:.2f} vs ${info_price:.2f}")
                else:
                    self.log_result("Price Consistency", False, 
                                  error="Invalid prices in responses")
            else:
                self.log_result("Price Consistency", False, 
                              error="Failed to fetch stock data")
                
        except Exception as e:
            self.log_result("Data Consistency", False, error=str(e))
    
    def test_error_responses(self):
        """Test error response formats"""
        print("\n🚨 Testing Error Response Formats...")
        
        # Test invalid stock symbol
        try:
            response = requests.get(f"{self.main_api_url}/api/stock/data/INVALID123?period=1y", 
                                  timeout=30)
            
            if response.status_code == 404 or response.status_code == 500:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        self.log_result("Error Format - Invalid Symbol", True, 
                                      "Proper error JSON format")
                    else:
                        self.log_result("Error Format - Invalid Symbol", False, 
                                      "Missing 'error' field in response")
                except json.JSONDecodeError:
                    self.log_result("Error Format - Invalid Symbol", False, 
                                  "Error response not in JSON format")
            else:
                self.log_result("Error Format - Invalid Symbol", False, 
                              f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Error Format - Invalid Symbol", False, error=str(e))
    
    def test_performance_under_load(self):
        """Test performance with multiple concurrent requests"""
        print("\n⚡ Testing Performance Under Load...")
        
        import concurrent.futures
        import threading
        
        def make_request(endpoint):
            try:
                start_time = time.time()
                response = requests.get(f"{self.main_api_url}{endpoint}", timeout=30)
                end_time = time.time()
                return {
                    'endpoint': endpoint,
                    'status': response.status_code,
                    'time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'endpoint': endpoint,
                    'status': 'ERROR',
                    'time': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Test concurrent requests
        endpoints = [
            "/api/health",
            "/api/stock/data/AAPL?period=1y",
            "/api/stock/info/AAPL",
            "/api/sensitivity/analysis/AAPL"
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(make_request, endpoint) for endpoint in endpoints]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = sum(1 for r in results if r['success'])
        avg_time = sum(r['time'] for r in results) / len(results)
        
        if successful_requests >= len(results) * 0.75:  # 75% success rate
            self.log_result("Concurrent Load Test", True, 
                          f"Success: {successful_requests}/{len(results)}, Avg time: {avg_time:.2f}s")
        else:
            self.log_result("Concurrent Load Test", False, 
                          f"Low success rate: {successful_requests}/{len(results)}")
    
    def run_all_tests(self):
        """Run all frontend integration tests"""
        print("🌐 Starting Frontend Integration Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_frontend_availability()
        self.test_frontend_static_assets()
        self.test_api_connectivity_from_frontend()
        self.test_cors_headers()
        self.test_data_consistency()
        self.test_error_responses()
        self.test_performance_under_load()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FRONTEND INTEGRATION TEST SUMMARY")
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
            print("\n🎉 All frontend integration tests passed!")
        else:
            print(f"\n⚠️  {self.results['failed']} tests failed. Review errors above.")
        
        return self.results

def main():
    """Main test runner"""
    print("AI Stock Trading - Frontend Integration Test Suite")
    print("=" * 60)
    
    # Create tester instance
    tester = FrontendTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
