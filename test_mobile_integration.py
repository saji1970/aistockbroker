#!/usr/bin/env python3
"""
Mobile App Integration Test Suite
Tests all API endpoints used by mobile applications
"""

import requests
import json
from datetime import datetime
import sys

API_BASE_URL = "http://localhost:8080"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class MobileTestRunner:
    def __init__(self, base_url):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0

    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")

    def test(self, name, endpoint, method='GET', payload=None, expected_fields=None):
        """Run a single mobile API test"""
        try:
            self.log(f"\nTesting: {name}", Colors.BLUE)
            url = f"{self.base_url}{endpoint}"

            if method == 'GET':
                response = requests.get(url, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=payload, timeout=30)

            if response.status_code in [200, 201]:
                data = response.json()
                self.log(f"  ✓ Status: {response.status_code}", Colors.GREEN)

                if expected_fields:
                    for field in expected_fields:
                        if field in data:
                            self.log(f"    ✓ Field '{field}' present", Colors.GREEN)
                        else:
                            self.log(f"    ✗ Field '{field}' missing", Colors.RED)
                            self.failed += 1
                            return False

                self.log(f"  Response preview: {json.dumps(data, indent=2)[:300]}...", Colors.BLUE)
                self.passed += 1
                return True
            else:
                self.log(f"  ✗ Status: {response.status_code}", Colors.RED)
                self.log(f"  Response: {response.text[:200]}", Colors.RED)
                self.failed += 1
                return False

        except Exception as e:
            self.log(f"  ✗ Error: {str(e)}", Colors.RED)
            self.failed += 1
            return False

    def summary(self):
        """Print test summary"""
        self.log(f"\n{'='*60}", Colors.BLUE)
        self.log("MOBILE INTEGRATION TEST SUMMARY", Colors.BLUE)
        self.log(f"{'='*60}", Colors.BLUE)
        self.log(f"Passed: {self.passed}", Colors.GREEN)
        self.log(f"Failed: {self.failed}", Colors.RED if self.failed > 0 else Colors.GREEN)

        if self.failed == 0:
            self.log("\n✓ ALL MOBILE TESTS PASSED", Colors.GREEN)
        else:
            self.log(f"\n✗ {self.failed} MOBILE TESTS FAILED", Colors.RED)

        return self.failed == 0

def main():
    """Main test execution for mobile app integration"""
    runner = MobileTestRunner(API_BASE_URL)

    runner.log("="*60, Colors.BLUE)
    runner.log("MOBILE APP API INTEGRATION TESTS", Colors.BLUE)
    runner.log("="*60, Colors.BLUE)

    # Core API Tests
    runner.test("Health Check", "/api/health", expected_fields=['status'])
    runner.test("Stock Data - AAPL", "/api/stock/data/AAPL?period=1mo",
                expected_fields=['dates', 'prices', 'volume'])
    runner.test("Stock Info - AAPL", "/api/stock/info/AAPL",
                expected_fields=['current_price', 'symbol'])
    runner.test("AI Prediction - AAPL", "/api/prediction/AAPL",
                expected_fields=['prediction', 'sentiment', 'confidence'])

    # Portfolio API Tests
    runner.test("Portfolio Initialization", "/api/portfolio/initialize", method='POST',
                payload={'initial_capital': 100000}, expected_fields=['success'])
    runner.test("Get Portfolio", "/api/portfolio",
                expected_fields=['total_value', 'cash', 'positions'])
    runner.test("Portfolio Performance", "/api/portfolio/performance",
                expected_fields=['total_return'])

    # Trading Bot API Tests
    runner.test("Trading Bot Status", "/api/status",
                expected_fields=['status', 'bot_active'])
    runner.test("Trading Bot Watchlist", "/api/watchlist",
                expected_fields=['watchlist'])
    runner.test("Trading Bot Orders", "/api/orders",
                expected_fields=['orders'])
    runner.test("Trading Bot Performance", "/api/performance")
    runner.test("Trading Bot Strategies", "/api/strategies",
                expected_fields=['strategies'])

    # AI Assistant API Tests
    runner.test("MarketMate Query", "/api/marketmate/query", method='POST',
                payload={'query': 'What is the price of AAPL?'})

    # Market Data API Tests
    runner.test("Stock Search", "/api/stock/search?q=apple",
                expected_fields=['results'])
    runner.test("Technical Indicators - AAPL", "/api/stock/technical/AAPL?period=1mo")
    runner.test("Comprehensive Analysis - AAPL", "/api/analysis/comprehensive?symbol=AAPL")

    # Summary
    success = runner.summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
