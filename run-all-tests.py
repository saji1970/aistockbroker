#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI Stock Trader
Runs all backend and frontend tests with detailed reporting
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'

def log(message, color=Colors.RESET):
    """Print colored message"""
    print(f"{color}{message}{Colors.RESET}")

def run_command(command, cwd=None, timeout=300):
    """Run command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def check_dependencies():
    """Check if required dependencies are installed"""
    log("🔍 Checking dependencies...", Colors.BLUE)
    
    # Check Python dependencies
    python_deps = ['pytest', 'pandas', 'numpy', 'flask', 'requests']
    missing_python = []
    
    for dep in python_deps:
        result = run_command(f"python -c 'import {dep}'")
        if not result['success']:
            missing_python.append(dep)
    
    if missing_python:
        log(f"❌ Missing Python dependencies: {', '.join(missing_python)}", Colors.RED)
        log("Installing missing dependencies...", Colors.YELLOW)
        run_command(f"pip install {' '.join(missing_python)}")
    
    # Check Node.js dependencies
    if not os.path.exists('frontend/node_modules'):
        log("📦 Installing frontend dependencies...", Colors.YELLOW)
        run_command("npm install", cwd="frontend")
    
    log("✅ Dependencies check complete", Colors.GREEN)

def run_backend_tests():
    """Run backend tests"""
    log("🧪 Running Backend Tests", Colors.BLUE)
    log("=" * 50, Colors.BLUE)
    
    results = {}
    
    # Run comprehensive backend tests
    log("Running comprehensive backend tests...", Colors.CYAN)
    result = run_command("python -m pytest backend/test_backend_comprehensive.py -v --tb=short", cwd=".")
    results['comprehensive_tests'] = result
    
    if result['success']:
        log("✅ Comprehensive backend tests passed", Colors.GREEN)
    else:
        log("❌ Comprehensive backend tests failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    # Run agent system tests
    log("Running agent system tests...", Colors.CYAN)
    result = run_command("python -m pytest backend/test_agent_system.py -v --tb=short", cwd=".")
    results['agent_tests'] = result
    
    if result['success']:
        log("✅ Agent system tests passed", Colors.GREEN)
    else:
        log("❌ Agent system tests failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    # Run API tests
    log("Running API endpoint tests...", Colors.CYAN)
    result = run_command("python -m pytest backend/test_backend_comprehensive.py::TestAPIServer -v --tb=short", cwd=".")
    results['api_tests'] = result
    
    if result['success']:
        log("✅ API tests passed", Colors.GREEN)
    else:
        log("❌ API tests failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    return results

def run_frontend_tests():
    """Run frontend tests"""
    log("🧪 Running Frontend Tests", Colors.BLUE)
    log("=" * 50, Colors.BLUE)
    
    results = {}
    
    # Run unit tests
    log("Running frontend unit tests...", Colors.CYAN)
    result = run_command("npm run test:ci", cwd="frontend")
    results['unit_tests'] = result
    
    if result['success']:
        log("✅ Frontend unit tests passed", Colors.GREEN)
    else:
        log("❌ Frontend unit tests failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    # Run integration tests
    log("Running frontend integration tests...", Colors.CYAN)
    result = run_command("npm run test:ci -- --testPathPattern=integration", cwd="frontend")
    results['integration_tests'] = result
    
    if result['success']:
        log("✅ Frontend integration tests passed", Colors.GREEN)
    else:
        log("❌ Frontend integration tests failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    # Run coverage tests
    log("Running frontend coverage tests...", Colors.CYAN)
    result = run_command("npm run test:coverage", cwd="frontend")
    results['coverage_tests'] = result
    
    if result['success']:
        log("✅ Frontend coverage tests passed", Colors.GREEN)
    else:
        log("❌ Frontend coverage tests failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    return results

def run_mobile_tests():
    """Run mobile app tests"""
    log("📱 Running Mobile App Tests", Colors.BLUE)
    log("=" * 50, Colors.BLUE)
    
    results = {}
    
    # Check if mobile app exists
    if not os.path.exists('mobile/AIStockTradingMobile'):
        log("⚠️  Mobile app not found, skipping mobile tests", Colors.YELLOW)
        return results
    
    # Run mobile app tests
    log("Running mobile app tests...", Colors.CYAN)
    result = run_command("npm test", cwd="mobile/AIStockTradingMobile")
    results['mobile_tests'] = result
    
    if result['success']:
        log("✅ Mobile app tests passed", Colors.GREEN)
    else:
        log("❌ Mobile app tests failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    return results

def run_integration_tests():
    """Run integration tests"""
    log("🔗 Running Integration Tests", Colors.BLUE)
    log("=" * 50, Colors.BLUE)
    
    results = {}
    
    # Test backend API server
    log("Testing backend API server...", Colors.CYAN)
    result = run_command("python -c \"import requests; print('API test:', requests.get('http://localhost:8080/api/health').status_code)\"")
    results['api_server_test'] = result
    
    if result['success']:
        log("✅ API server test passed", Colors.GREEN)
    else:
        log("❌ API server test failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    # Test frontend build
    log("Testing frontend build...", Colors.CYAN)
    result = run_command("npm run build", cwd="frontend")
    results['frontend_build'] = result
    
    if result['success']:
        log("✅ Frontend build test passed", Colors.GREEN)
    else:
        log("❌ Frontend build test failed", Colors.RED)
        log(f"Error: {result['stderr']}", Colors.RED)
    
    return results

def generate_test_report(backend_results, frontend_results, mobile_results, integration_results):
    """Generate comprehensive test report"""
    log("📋 Generating test report...", Colors.BLUE)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'duration': 0
        },
        'backend': {
            'comprehensive_tests': backend_results.get('comprehensive_tests', {}),
            'agent_tests': backend_results.get('agent_tests', {}),
            'api_tests': backend_results.get('api_tests', {})
        },
        'frontend': {
            'unit_tests': frontend_results.get('unit_tests', {}),
            'integration_tests': frontend_results.get('integration_tests', {}),
            'coverage_tests': frontend_results.get('coverage_tests', {})
        },
        'mobile': {
            'mobile_tests': mobile_results.get('mobile_tests', {})
        },
        'integration': {
            'api_server_test': integration_results.get('api_server_test', {}),
            'frontend_build': integration_results.get('frontend_build', {})
        }
    }
    
    # Calculate summary
    all_results = [backend_results, frontend_results, mobile_results, integration_results]
    for result_set in all_results:
        for test_name, result in result_set.items():
            report['summary']['total_tests'] += 1
            if result.get('success', False):
                report['summary']['passed'] += 1
            else:
                report['summary']['failed'] += 1
    
    # Save report
    with open('test-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    log(f"📄 Test report saved to: test-report.json", Colors.GREEN)
    
    return report

def main():
    """Main test runner"""
    log("🚀 AI Stock Trader - Comprehensive Test Suite", Colors.BOLD)
    log("=" * 60, Colors.BOLD)
    
    start_time = time.time()
    
    try:
        # Check dependencies
        check_dependencies()
        
        # Run backend tests
        backend_results = run_backend_tests()
        
        # Run frontend tests
        frontend_results = run_frontend_tests()
        
        # Run mobile tests
        mobile_results = run_mobile_tests()
        
        # Run integration tests
        integration_results = run_integration_tests()
        
        # Generate test report
        report = generate_test_report(backend_results, frontend_results, mobile_results, integration_results)
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        log("", Colors.RESET)
        log("🎯 Test Suite Summary", Colors.BOLD)
        log("=" * 60, Colors.BOLD)
        log(f"Total Tests: {report['summary']['total_tests']}", Colors.CYAN)
        log(f"Passed: {report['summary']['passed']}", Colors.GREEN)
        log(f"Failed: {report['summary']['failed']}", Colors.RED)
        log(f"Duration: {duration:.2f} seconds", Colors.CYAN)
        log("", Colors.RESET)
        
        # Print detailed results
        log("📊 Detailed Results", Colors.BOLD)
        log("=" * 60, Colors.BOLD)
        
        # Backend results
        log("Backend Tests:", Colors.BLUE)
        for test_name, result in backend_results.items():
            status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
            log(f"  {test_name}: {status}", Colors.GREEN if result.get('success', False) else Colors.RED)
        
        # Frontend results
        log("Frontend Tests:", Colors.BLUE)
        for test_name, result in frontend_results.items():
            status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
            log(f"  {test_name}: {status}", Colors.GREEN if result.get('success', False) else Colors.RED)
        
        # Mobile results
        if mobile_results:
            log("Mobile Tests:", Colors.BLUE)
            for test_name, result in mobile_results.items():
                status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
                log(f"  {test_name}: {status}", Colors.GREEN if result.get('success', False) else Colors.RED)
        
        # Integration results
        log("Integration Tests:", Colors.BLUE)
        for test_name, result in integration_results.items():
            status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
            log(f"  {test_name}: {status}", Colors.GREEN if result.get('success', False) else Colors.RED)
        
        # Final status
        if report['summary']['failed'] == 0:
            log("", Colors.RESET)
            log("🎉 All Tests Passed!", Colors.GREEN)
            log("=" * 60, Colors.GREEN)
            log("✅ Backend: All tests passed", Colors.GREEN)
            log("✅ Frontend: All tests passed", Colors.GREEN)
            log("✅ Mobile: All tests passed", Colors.GREEN)
            log("✅ Integration: All tests passed", Colors.GREEN)
            log("", Colors.RESET)
            log("🚀 System is ready for production!", Colors.GREEN)
        else:
            log("", Colors.RESET)
            log("❌ Some Tests Failed!", Colors.RED)
            log("=" * 60, Colors.RED)
            log(f"Failed: {report['summary']['failed']} tests", Colors.RED)
            log("Please check the test report for details", Colors.RED)
            sys.exit(1)
    
    except Exception as e:
        log("", Colors.RESET)
        log("❌ Test Suite Failed!", Colors.RED)
        log("=" * 60, Colors.RED)
        log(f"Error: {str(e)}", Colors.RED)
        sys.exit(1)

if __name__ == '__main__':
    main()
