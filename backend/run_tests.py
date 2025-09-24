"""
Test Runner for Agent System
Runs all unit tests and integration tests locally
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        end_time = time.time()
        
        print(f"Exit code: {result.returncode}")
        print(f"Duration: {end_time - start_time:.2f} seconds")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'duration': end_time - start_time,
            'exit_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"Command timed out after 5 minutes")
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Command timed out',
            'duration': 300,
            'exit_code': -1
        }
    except Exception as e:
        print(f"Error running command: {e}")
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'duration': 0,
            'exit_code': -1
        }

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'pytest',
        'pandas',
        'numpy',
        'yfinance',
        'flask',
        'aiohttp',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        install_command = f"pip install {' '.join(missing_packages)}"
        result = run_command(install_command, "Installing missing packages")
        
        if not result['success']:
            print("Failed to install missing packages. Please install them manually.")
            return False
    
    return True

def run_unit_tests():
    """Run unit tests"""
    print("\n" + "="*80)
    print("RUNNING UNIT TESTS")
    print("="*80)
    
    # Run pytest on the test file
    test_command = "python -m pytest backend/test_agent_system.py -v --tb=short"
    result = run_command(test_command, "Unit Tests")
    
    return result

def run_integration_tests():
    """Run integration tests"""
    print("\n" + "="*80)
    print("RUNNING INTEGRATION TESTS")
    print("="*80)
    
    # Run specific integration tests
    integration_command = "python -m pytest backend/test_agent_system.py::TestIntegration -v --tb=short"
    result = run_command(integration_command, "Integration Tests")
    
    return result

def run_performance_tests():
    """Run performance tests"""
    print("\n" + "="*80)
    print("RUNNING PERFORMANCE TESTS")
    print("="*80)
    
    # Run performance tests
    performance_command = "python -m pytest backend/test_agent_system.py::TestPerformance -v --tb=short"
    result = run_command(performance_command, "Performance Tests")
    
    return result

def test_api_endpoints():
    """Test API endpoints"""
    print("\n" + "="*80)
    print("TESTING API ENDPOINTS")
    print("="*80)
    
    # Start the API server in background
    print("Starting API server...")
    server_process = subprocess.Popen(
        ["python", "api_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test health endpoint
        health_command = "curl -s http://localhost:8080/api/agent/health"
        health_result = run_command(health_command, "Health Check")
        
        # Test agent login
        login_command = 'curl -s -X POST http://localhost:8080/api/agent/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@aistockbroker.com","password":"admin123"}\''
        login_result = run_command(login_command, "Agent Login")
        
        return {
            'health': health_result,
            'login': login_result
        }
        
    finally:
        # Stop the server
        print("Stopping API server...")
        server_process.terminate()
        server_process.wait()

def generate_test_report(results):
    """Generate test report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'duration': 0
        },
        'results': results
    }
    
    # Calculate summary
    for test_type, result in results.items():
        if isinstance(result, dict) and 'success' in result:
            report['summary']['total_tests'] += 1
            if result['success']:
                report['summary']['passed'] += 1
            else:
                report['summary']['failed'] += 1
            report['summary']['duration'] += result.get('duration', 0)
    
    # Save report
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

def main():
    """Main test runner"""
    print("AI Stock Trading Agent System - Test Runner")
    print("=" * 80)
    
    # Check if we're in the right directory
    if not os.path.exists('backend'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Change to backend directory
    os.chdir('backend')
    
    # Check dependencies
    if not check_dependencies():
        print("Dependency check failed. Exiting.")
        sys.exit(1)
    
    # Run tests
    results = {}
    
    # Unit tests
    print("\n" + "="*80)
    print("STARTING TEST EXECUTION")
    print("="*80)
    
    unit_result = run_unit_tests()
    results['unit_tests'] = unit_result
    
    # Integration tests
    integration_result = run_integration_tests()
    results['integration_tests'] = integration_result
    
    # Performance tests
    performance_result = run_performance_tests()
    results['performance_tests'] = performance_result
    
    # API endpoint tests
    api_result = test_api_endpoints()
    results['api_tests'] = api_result
    
    # Generate report
    report = generate_test_report(results)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Duration: {report['summary']['duration']:.2f} seconds")
    print(f"Report saved to: test_report.json")
    
    # Print detailed results
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)
    
    for test_type, result in results.items():
        print(f"\n{test_type.upper()}:")
        if isinstance(result, dict):
            if result.get('success'):
                print(f"  ✓ PASSED ({result.get('duration', 0):.2f}s)")
            else:
                print(f"  ✗ FAILED ({result.get('duration', 0):.2f}s)")
                if result.get('stderr'):
                    print(f"    Error: {result['stderr']}")
        else:
            print(f"  ? UNKNOWN")
    
    # Exit with appropriate code
    if report['summary']['failed'] > 0:
        print(f"\n❌ {report['summary']['failed']} test(s) failed")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed!")
        sys.exit(0)

if __name__ == '__main__':
    main()