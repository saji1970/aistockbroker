#!/usr/bin/env python3
"""
Test Runner for Login Functionality
Runs all login-related tests and provides a comprehensive report
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_test(test_name: str, test_file: str, args: list = None) -> dict:
    """Run a test file and return results"""
    logger.info(f"Running {test_name}...")
    
    cmd = [sys.executable, test_file]
    if args:
        cmd.extend(args)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'name': test_name,
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'name': test_name,
            'success': False,
            'duration': 300,
            'stdout': '',
            'stderr': 'Test timed out after 5 minutes',
            'returncode': -1
        }
    except Exception as e:
        return {
            'name': test_name,
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def main():
    """Main test runner"""
    logger.info("=" * 80)
    logger.info("LOGIN FUNCTIONALITY TEST RUNNER")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Define test suites
    test_suites = [
        {
            'name': 'Comprehensive Login Tests',
            'file': 'test_login_comprehensive.py',
            'args': []
        },
        {
            'name': 'End-to-End Integration Tests',
            'file': 'test_end_to_end_integration.py',
            'args': []
        }
    ]
    
    # Run tests
    results = []
    total_duration = 0
    
    for suite in test_suites:
        if os.path.exists(suite['file']):
            result = run_test(suite['name'], suite['file'], suite['args'])
            results.append(result)
            total_duration += result['duration']
        else:
            logger.warning(f"Test file not found: {suite['file']}")
            results.append({
                'name': suite['name'],
                'success': False,
                'duration': 0,
                'stdout': '',
                'stderr': f'Test file not found: {suite["file"]}',
                'returncode': -1
            })
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    logger.info(f"Total Test Suites: {len(results)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success Rate: {(passed/len(results)*100):.1f}%")
    logger.info(f"Total Duration: {total_duration:.2f} seconds")
    logger.info("")
    
    # Detailed results
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        logger.info(f"{status} - {result['name']} ({result['duration']:.2f}s)")
        
        if not result['success'] and result['stderr']:
            logger.error(f"  Error: {result['stderr']}")
    
    logger.info("")
    
    # Overall result
    if passed == len(results):
        logger.info("🎉 ALL TEST SUITES PASSED! 🎉")
        logger.info("")
        logger.info("Login functionality is working correctly:")
        logger.info("✅ Single role users can login directly")
        logger.info("✅ Multiple role users see role selection modal")
        logger.info("✅ Invalid credentials are properly rejected")
        logger.info("✅ Session management is functional")
        logger.info("✅ CORS integration is working")
        logger.info("✅ Frontend and backend are properly integrated")
        return 0
    else:
        logger.error("❌ SOME TEST SUITES FAILED")
        logger.error("")
        logger.error("Please review the failed tests and fix the issues.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
