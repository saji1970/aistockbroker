#!/usr/bin/env python3
"""
Stress Test Suite for AI Stock Trading Application
Tests system performance under various load conditions
"""

import requests
import json
import time
import sys
import threading
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics

class StressTester:
    def __init__(self):
        self.main_api_url = "https://ai-stock-trading-api-1024040140027.us-central1.run.app"
        self.trading_bot_url = "https://ai-stock-trading-backend-1024040140027.us-central1.run.app"
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'response_times': [],
            'concurrent_tests': []
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
    
    def make_request(self, url: str, timeout: int = 30) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        try:
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response_time,
                'url': url,
                'error': None
            }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': False,
                'status_code': 'ERROR',
                'response_time': response_time,
                'url': url,
                'error': str(e)
            }
    
    def test_single_endpoint_load(self, endpoint: str, num_requests: int = 10):
        """Test single endpoint under load"""
        print(f"\n🔄 Testing {endpoint} with {num_requests} requests...")
        
        url = f"{self.main_api_url}{endpoint}"
        response_times = []
        successes = 0
        
        for i in range(num_requests):
            result = self.make_request(url)
            response_times.append(result['response_time'])
            
            if result['success']:
                successes += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        success_rate = (successes / num_requests) * 100
        
        self.results['response_times'].extend(response_times)
        
        if success_rate >= 90 and avg_time < 5.0:
            self.log_result(f"Load Test - {endpoint}", True, 
                          f"Success: {success_rate:.1f}%, Avg: {avg_time:.2f}s, Max: {max_time:.2f}s")
        else:
            self.log_result(f"Load Test - {endpoint}", False, 
                          f"Success: {success_rate:.1f}%, Avg: {avg_time:.2f}s, Max: {max_time:.2f}s")
    
    def test_concurrent_requests(self, num_threads: int = 5, requests_per_thread: int = 5):
        """Test concurrent requests from multiple threads"""
        print(f"\n⚡ Testing {num_threads} concurrent threads with {requests_per_thread} requests each...")
        
        endpoints = [
            "/api/health",
            "/api/stock/data/AAPL?period=1y",
            "/api/stock/info/AAPL",
            "/api/sensitivity/analysis/AAPL"
        ]
        
        def worker_thread(thread_id: int):
            """Worker thread function"""
            thread_results = []
            for i in range(requests_per_thread):
                endpoint = endpoints[i % len(endpoints)]
                url = f"{self.main_api_url}{endpoint}"
                result = self.make_request(url)
                result['thread_id'] = thread_id
                result['request_id'] = i
                thread_results.append(result)
                time.sleep(0.1)
            return thread_results
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        total_requests = len(all_results)
        successful_requests = sum(1 for r in all_results if r['success'])
        response_times = [r['response_time'] for r in all_results]
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        success_rate = (successful_requests / total_requests) * 100
        
        self.results['concurrent_tests'].append({
            'threads': num_threads,
            'requests_per_thread': requests_per_thread,
            'total_requests': total_requests,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'total_time': total_time
        })
        
        if success_rate >= 85 and avg_response_time < 10.0:
            self.log_result("Concurrent Load Test", True, 
                          f"Success: {success_rate:.1f}%, Avg: {avg_response_time:.2f}s, Total: {total_time:.2f}s")
        else:
            self.log_result("Concurrent Load Test", False, 
                          f"Success: {success_rate:.1f}%, Avg: {avg_response_time:.2f}s, Total: {total_time:.2f}s")
    
    def test_mixed_workload(self):
        """Test mixed workload with different types of requests"""
        print("\n🎯 Testing Mixed Workload...")
        
        # Define different types of requests
        requests_config = [
            {"endpoint": "/api/health", "weight": 0.2, "expected_time": 1.0},
            {"endpoint": "/api/stock/data/AAPL?period=1y", "weight": 0.3, "expected_time": 3.0},
            {"endpoint": "/api/stock/info/AAPL", "weight": 0.2, "expected_time": 2.0},
            {"endpoint": "/api/sensitivity/analysis/AAPL", "weight": 0.3, "expected_time": 4.0}
        ]
        
        total_requests = 20
        results = []
        
        # Generate requests based on weights
        for config in requests_config:
            num_requests = int(total_requests * config['weight'])
            for i in range(num_requests):
                url = f"{self.main_api_url}{config['endpoint']}"
                result = self.make_request(url)
                result['expected_time'] = config['expected_time']
                result['endpoint'] = config['endpoint']
                results.append(result)
                time.sleep(0.1)
        
        # Analyze results by endpoint type
        endpoint_stats = {}
        for result in results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'times': [], 'successes': 0, 'total': 0}
            
            endpoint_stats[endpoint]['times'].append(result['response_time'])
            endpoint_stats[endpoint]['total'] += 1
            if result['success']:
                endpoint_stats[endpoint]['successes'] += 1
        
        all_passed = True
        for endpoint, stats in endpoint_stats.items():
            avg_time = statistics.mean(stats['times'])
            success_rate = (stats['successes'] / stats['total']) * 100
            
            # Check if performance is acceptable
            if success_rate >= 80 and avg_time < 8.0:
                self.log_result(f"Mixed Workload - {endpoint}", True, 
                              f"Success: {success_rate:.1f}%, Avg: {avg_time:.2f}s")
            else:
                self.log_result(f"Mixed Workload - {endpoint}", False, 
                              f"Success: {success_rate:.1f}%, Avg: {avg_time:.2f}s")
                all_passed = False
        
        if all_passed:
            self.log_result("Mixed Workload Overall", True, "All endpoints performed well")
        else:
            self.log_result("Mixed Workload Overall", False, "Some endpoints underperformed")
    
    def test_trading_bot_load(self):
        """Test trading bot endpoints under load"""
        print("\n🤖 Testing Trading Bot Load...")
        
        endpoints = [
            "/api/status",
            "/api/portfolio",
            "/api/strategies",
            "/api/watchlist"
        ]
        
        results = []
        for endpoint in endpoints:
            url = f"{self.trading_bot_url}{endpoint}"
            result = self.make_request(url)
            result['endpoint'] = endpoint
            results.append(result)
            time.sleep(0.2)
        
        successful_requests = sum(1 for r in results if r['success'])
        response_times = [r['response_time'] for r in results]
        avg_time = statistics.mean(response_times)
        success_rate = (successful_requests / len(results)) * 100
        
        if success_rate >= 90 and avg_time < 5.0:
            self.log_result("Trading Bot Load Test", True, 
                          f"Success: {success_rate:.1f}%, Avg: {avg_time:.2f}s")
        else:
            self.log_result("Trading Bot Load Test", False, 
                          f"Success: {success_rate:.1f}%, Avg: {avg_time:.2f}s")
    
    def test_error_recovery(self):
        """Test system recovery from errors"""
        print("\n🔄 Testing Error Recovery...")
        
        # Test with invalid requests followed by valid ones
        invalid_requests = [
            "/api/stock/data/INVALID123?period=1y",
            "/api/stock/info/NONEXISTENT",
            "/api/prediction/INVALID"
        ]
        
        valid_requests = [
            "/api/health",
            "/api/stock/data/AAPL?period=1y",
            "/api/stock/info/AAPL"
        ]
        
        # Make invalid requests
        for endpoint in invalid_requests:
            url = f"{self.main_api_url}{endpoint}"
            result = self.make_request(url)
            time.sleep(0.1)
        
        # Make valid requests to test recovery
        recovery_results = []
        for endpoint in valid_requests:
            url = f"{self.main_api_url}{endpoint}"
            result = self.make_request(url)
            recovery_results.append(result)
            time.sleep(0.1)
        
        successful_recovery = sum(1 for r in recovery_results if r['success'])
        recovery_rate = (successful_recovery / len(recovery_results)) * 100
        
        if recovery_rate >= 90:
            self.log_result("Error Recovery Test", True, 
                          f"Recovery rate: {recovery_rate:.1f}%")
        else:
            self.log_result("Error Recovery Test", False, 
                          f"Recovery rate: {recovery_rate:.1f}%")
    
    def test_sustained_load(self, duration_minutes: int = 2):
        """Test sustained load over time"""
        print(f"\n⏱️ Testing Sustained Load for {duration_minutes} minutes...")
        
        endpoints = [
            "/api/health",
            "/api/stock/data/AAPL?period=1y",
            "/api/stock/info/AAPL"
        ]
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        request_count = 0
        success_count = 0
        response_times = []
        
        while time.time() < end_time:
            endpoint = endpoints[request_count % len(endpoints)]
            url = f"{self.main_api_url}{endpoint}"
            result = self.make_request(url)
            
            request_count += 1
            if result['success']:
                success_count += 1
            response_times.append(result['response_time'])
            
            time.sleep(1)  # 1 request per second
        
        actual_duration = time.time() - start_time
        success_rate = (success_count / request_count) * 100
        avg_response_time = statistics.mean(response_times)
        
        if success_rate >= 85 and avg_response_time < 5.0:
            self.log_result("Sustained Load Test", True, 
                          f"Duration: {actual_duration:.1f}s, Requests: {request_count}, Success: {success_rate:.1f}%")
        else:
            self.log_result("Sustained Load Test", False, 
                          f"Duration: {actual_duration:.1f}s, Requests: {request_count}, Success: {success_rate:.1f}%")
    
    def run_all_tests(self):
        """Run all stress tests"""
        print("⚡ Starting Stress Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_single_endpoint_load("/api/health", 10)
        self.test_single_endpoint_load("/api/stock/data/AAPL?period=1y", 5)
        self.test_concurrent_requests(3, 3)
        self.test_mixed_workload()
        self.test_trading_bot_load()
        self.test_error_recovery()
        self.test_sustained_load(1)  # 1 minute sustained load
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Print detailed summary
        print("\n" + "=" * 60)
        print("📊 STRESS TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        # Performance statistics
        if self.results['response_times']:
            avg_response_time = statistics.mean(self.results['response_times'])
            max_response_time = max(self.results['response_times'])
            min_response_time = min(self.results['response_times'])
            print(f"\n📊 Performance Statistics:")
            print(f"   Average Response Time: {avg_response_time:.2f}s")
            print(f"   Max Response Time: {max_response_time:.2f}s")
            print(f"   Min Response Time: {min_response_time:.2f}s")
        
        # Concurrent test results
        if self.results['concurrent_tests']:
            print(f"\n🔄 Concurrent Test Results:")
            for test in self.results['concurrent_tests']:
                print(f"   {test['threads']} threads: {test['success_rate']:.1f}% success, {test['avg_response_time']:.2f}s avg")
        
        if self.results['errors']:
            print(f"\n🚨 Errors Found:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        if self.results['failed'] == 0:
            print("\n🎉 All stress tests passed! System handles load well.")
        else:
            print(f"\n⚠️  {self.results['failed']} tests failed. System may need optimization.")
        
        return self.results

def main():
    """Main test runner"""
    print("AI Stock Trading - Stress Test Suite")
    print("=" * 60)
    
    # Create tester instance
    tester = StressTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
