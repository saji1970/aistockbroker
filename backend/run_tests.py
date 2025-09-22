#!/usr/bin/env python3
"""
Test Runner for AI Stock Trading Bot
Provides options to run different types of tests
"""

import sys
import os
import argparse
import subprocess
from datetime import datetime

def run_unit_tests():
    """Run unit tests only"""
    print("🧪 Running Unit Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "test_unit_only.py"], 
                              capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Unit tests timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return False

def run_api_tests():
    """Run API integration tests"""
    print("🌐 Running API Integration Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, "test_trading_bot.py"], 
                              capture_output=True, text=True, timeout=600)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ API tests timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running API tests: {e}")
        return False

def run_quick_tests():
    """Run quick tests (unit tests only)"""
    print("⚡ Running Quick Tests...")
    print("=" * 50)
    
    return run_unit_tests()

def run_all_tests():
    """Run all tests"""
    print("🚀 Running All Tests...")
    print("=" * 50)
    
    # Run unit tests first
    unit_success = run_unit_tests()
    
    if not unit_success:
        print("\n❌ Unit tests failed, skipping API tests")
        return False
    
    print("\n" + "=" * 50)
    
    # Run API tests
    api_success = run_api_tests()
    
    return unit_success and api_success

def run_specific_test_class(test_class):
    """Run a specific test class"""
    print(f"🎯 Running {test_class} Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            f"test_trading_bot.{test_class}"
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Test Runner for AI Stock Trading Bot")
    parser.add_argument("--type", choices=["unit", "api", "quick", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--class", dest="test_class", 
                       help="Run specific test class")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    print(f"🧪 AI Stock Trading Bot Test Suite")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success = False
    
    if args.test_class:
        success = run_specific_test_class(args.test_class)
    elif args.type == "unit":
        success = run_unit_tests()
    elif args.type == "api":
        success = run_api_tests()
    elif args.type == "quick":
        success = run_quick_tests()
    elif args.type == "all":
        success = run_all_tests()
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ All tests completed successfully!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)

if __name__ == "__main__":
    main()
