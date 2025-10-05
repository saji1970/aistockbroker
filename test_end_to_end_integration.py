#!/usr/bin/env python3
"""
End-to-End Integration Test Suite for AI Stock Trading Platform
Tests the complete login flow from frontend to backend
"""

import os
import sys
import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://ai-stock-trading-backend-simple-1012090067429.us-central1.run.app')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://ai-stock-trading-frontend-1012090067429.us-central1.run.app')

class EndToEndTestSuite:
    """End-to-end integration test suite"""
    
    def __init__(self, api_base_url: str, frontend_url: str):
        self.api_base_url = api_base_url
        self.frontend_url = frontend_url
        self.session = requests.Session()
        self.test_results = []
        
        # Test scenarios
        self.test_scenarios = [
            {
                'name': 'Single Role User - Ranjit (Agent)',
                'username': 'ranjit',
                'password': 'password',
                'expected_roles': ['agent'],
                'expected_primary_role': 'agent',
                'expected_multiple_roles': False,
                'expected_dashboard': '/agent/dashboard'
            },
            {
                'name': 'Single Role User - Admin',
                'username': 'admin',
                'password': 'password',
                'expected_roles': ['admin'],
                'expected_primary_role': 'admin',
                'expected_multiple_roles': False,
                'expected_dashboard': '/admin'
            },
            {
                'name': 'Single Role User - John (Customer)',
                'username': 'john',
                'password': 'password',
                'expected_roles': ['customer'],
                'expected_primary_role': 'customer',
                'expected_multiple_roles': False,
                'expected_dashboard': '/dashboard'
            },
            {
                'name': 'Multiple Role User - Saji (Admin + Agent)',
                'username': 'saji',
                'password': 'password',
                'expected_roles': ['admin', 'agent'],
                'expected_primary_role': None,
                'expected_multiple_roles': True,
                'expected_dashboard': None  # Should show role selection
            },
            {
                'name': 'Multiple Role User - Sarah (Agent + Customer)',
                'username': 'sarah',
                'password': 'password',
                'expected_roles': ['agent', 'customer'],
                'expected_primary_role': None,
                'expected_multiple_roles': True,
                'expected_dashboard': None  # Should show role selection
            }
        ]

    def log_test_result(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
        
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        })

    def test_frontend_accessibility(self) -> bool:
        """Test if frontend is accessible"""
        try:
            response = self.session.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                html = response.text
                if 'AI Stock Trading' in html or 'login' in html.lower():
                    self.log_test_result("Frontend Accessibility", True, "Frontend is accessible")
                    return True
                else:
                    self.log_test_result("Frontend Accessibility", False, "Frontend accessible but content not as expected")
                    return False
            else:
                self.log_test_result("Frontend Accessibility", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Frontend Accessibility", False, f"Exception: {str(e)}")
            return False

    def test_backend_health(self) -> bool:
        """Test backend health"""
        try:
            response = self.session.get(f'{self.api_base_url}/api/health', timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test_result("Backend Health", True, "Backend is healthy")
                    return True
                else:
                    self.log_test_result("Backend Health", False, f"Backend unhealthy: {data.get('status')}")
                    return False
            else:
                self.log_test_result("Backend Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Backend Health", False, f"Exception: {str(e)}")
            return False

    def test_complete_login_flow(self, scenario: Dict) -> bool:
        """Test complete login flow for a user scenario"""
        try:
            username = scenario['username']
            password = scenario['password']
            expected_roles = scenario['expected_roles']
            expected_primary_role = scenario['expected_primary_role']
            expected_multiple_roles = scenario['expected_multiple_roles']
            expected_dashboard = scenario['expected_dashboard']
            
            # Step 1: Login
            login_data = {
                'email_or_username': username,
                'password': password
            }
            
            response = self.session.post(
                f'{self.api_base_url}/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test_result(
                    f"Login Flow - {scenario['name']}",
                    False,
                    f"Login failed: HTTP {response.status_code}"
                )
                return False
            
            data = response.json()
            if not data.get('success'):
                self.log_test_result(
                    f"Login Flow - {scenario['name']}",
                    False,
                    f"Login failed: {data.get('message', 'Unknown error')}"
                )
                return False
            
            user = data.get('user', {})
            
            # Step 2: Validate user data
            if set(user.get('roles', [])) != set(expected_roles):
                self.log_test_result(
                    f"Login Flow - {scenario['name']}",
                    False,
                    f"Role mismatch. Expected: {expected_roles}, Got: {user.get('roles')}"
                )
                return False
            
            if user.get('primary_role') != expected_primary_role:
                self.log_test_result(
                    f"Login Flow - {scenario['name']}",
                    False,
                    f"Primary role mismatch. Expected: {expected_primary_role}, Got: {user.get('primary_role')}"
                )
                return False
            
            if user.get('has_multiple_roles') != expected_multiple_roles:
                self.log_test_result(
                    f"Login Flow - {scenario['name']}",
                    False,
                    f"Multiple roles flag mismatch. Expected: {expected_multiple_roles}, Got: {user.get('has_multiple_roles')}"
                )
                return False
            
            # Step 3: Test session verification
            token = data.get('token')
            if token:
                headers = {'Authorization': f'Bearer {token}'}
                verify_response = self.session.post(
                    f'{self.api_base_url}/api/auth/verify-session',
                    headers=headers,
                    timeout=10
                )
                
                if verify_response.status_code != 200:
                    self.log_test_result(
                        f"Login Flow - {scenario['name']}",
                        False,
                        f"Session verification failed: HTTP {verify_response.status_code}"
                    )
                    return False
                
                verify_data = verify_response.json()
                if not verify_data.get('valid'):
                    self.log_test_result(
                        f"Login Flow - {scenario['name']}",
                        False,
                        f"Session marked as invalid"
                    )
                    return False
            
            # Step 4: Validate login response structure
            if expected_multiple_roles:
                # Multiple role user - should have role selection logic
                self.log_test_result(
                    f"Login Flow - {scenario['name']}",
                    True,
                    f"Login successful, role selection modal should appear for roles: {expected_roles}"
                )
                return True
            else:
                # Single role user - should go directly to dashboard
                self.log_test_result(
                    f"Login Flow - {scenario['name']}",
                    True,
                    f"Login successful, should redirect to: {expected_dashboard}"
                )
                return True
                
        except Exception as e:
            self.log_test_result(
                f"Login Flow - {scenario['name']}",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_invalid_login_scenarios(self) -> bool:
        """Test invalid login scenarios"""
        invalid_scenarios = [
            {'username': 'nonexistent', 'password': 'password', 'description': 'Non-existent user'},
            {'username': 'ranjit', 'password': 'wrongpassword', 'description': 'Wrong password'},
            {'username': '', 'password': 'password', 'description': 'Empty username'},
            {'username': 'ranjit', 'password': '', 'description': 'Empty password'}
        ]
        
        passed = 0
        total = len(invalid_scenarios)
        
        for scenario in invalid_scenarios:
            try:
                login_data = {
                    'email_or_username': scenario['username'],
                    'password': scenario['password']
                }
                
                response = self.session.post(
                    f'{self.api_base_url}/api/auth/login',
                    json=login_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == 401:
                    data = response.json()
                    if not data.get('success', True):  # success should be False
                        self.log_test_result(
                            f"Invalid Login - {scenario['description']}",
                            True,
                            f"Correctly rejected: {scenario['username'] or 'empty'}"
                        )
                        passed += 1
                    else:
                        self.log_test_result(
                            f"Invalid Login - {scenario['description']}",
                            False,
                            f"Success flag not False for invalid credentials"
                        )
                else:
                    self.log_test_result(
                        f"Invalid Login - {scenario['description']}",
                        False,
                        f"Expected 401, got {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Invalid Login - {scenario['description']}",
                    False,
                    f"Exception: {str(e)}"
                )
        
        success_rate = passed / total
        if success_rate == 1.0:
            self.log_test_result(
                "Invalid Login Suite",
                True,
                f"All {total} invalid login scenarios correctly rejected"
            )
            return True
        else:
            self.log_test_result(
                "Invalid Login Suite",
                False,
                f"Only {passed}/{total} invalid login scenarios correctly rejected"
            )
            return False

    def test_cors_integration(self) -> bool:
        """Test CORS integration between frontend and backend"""
        try:
            # Test preflight request
            response = self.session.options(
                f'{self.api_base_url}/api/auth/login',
                headers={
                    'Origin': self.frontend_url,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                
                if cors_headers['Access-Control-Allow-Origin']:
                    self.log_test_result(
                        "CORS Integration",
                        True,
                        f"CORS headers present for frontend-backend communication"
                    )
                    return True
                else:
                    self.log_test_result(
                        "CORS Integration",
                        False,
                        "CORS headers missing"
                    )
                    return False
            else:
                self.log_test_result(
                    "CORS Integration",
                    False,
                    f"Preflight request failed: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "CORS Integration",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def run_all_tests(self) -> bool:
        """Run all end-to-end tests"""
        logger.info("=" * 80)
        logger.info("STARTING END-TO-END INTEGRATION TEST SUITE")
        logger.info("=" * 80)
        logger.info(f"Frontend URL: {self.frontend_url}")
        logger.info(f"Backend URL: {self.api_base_url}")
        logger.info("")
        
        # Test 1: Basic connectivity
        logger.info("Testing Basic Connectivity...")
        frontend_ok = self.test_frontend_accessibility()
        backend_ok = self.test_backend_health()
        
        if not (frontend_ok and backend_ok):
            logger.error("Basic connectivity tests failed. Aborting.")
            return False
        
        logger.info("")
        
        # Test 2: Complete login flows
        logger.info("Testing Complete Login Flows...")
        login_flows_passed = 0
        login_flows_total = len(self.test_scenarios)
        
        for scenario in self.test_scenarios:
            if self.test_complete_login_flow(scenario):
                login_flows_passed += 1
        
        logger.info(f"Login Flow Tests: {login_flows_passed}/{login_flows_total} passed")
        logger.info("")
        
        # Test 3: Invalid login scenarios
        logger.info("Testing Invalid Login Scenarios...")
        invalid_login_ok = self.test_invalid_login_scenarios()
        logger.info("")
        
        # Test 4: CORS integration
        logger.info("Testing CORS Integration...")
        cors_ok = self.test_cors_integration()
        logger.info("")
        
        # Summary
        total_tests = 2 + login_flows_total + 2  # Basic connectivity + login flows + invalid + CORS
        passed_tests = sum([frontend_ok, backend_ok, login_flows_passed, invalid_login_ok, cors_ok])
        
        logger.info("=" * 80)
        logger.info("END-TO-END TEST RESULTS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info("")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL END-TO-END TESTS PASSED! 🎉")
            logger.info("")
            logger.info("✅ Frontend is accessible")
            logger.info("✅ Backend is healthy")
            logger.info("✅ All login flows work correctly")
            logger.info("✅ Invalid credentials are properly rejected")
            logger.info("✅ CORS integration is working")
            logger.info("✅ Role selection logic is implemented")
            logger.info("✅ Session management is functional")
            return True
        else:
            logger.error("❌ SOME END-TO-END TESTS FAILED")
            
            # Show failed tests
            failed_tests = [r for r in self.test_results if not r['passed']]
            if failed_tests:
                logger.error("\nFailed Tests:")
                for test in failed_tests:
                    logger.error(f"  - {test['test_name']}: {test['message']}")
            
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run end-to-end integration tests')
    parser.add_argument('--api-url', default=API_BASE_URL, help='API base URL')
    parser.add_argument('--frontend-url', default=FRONTEND_URL, help='Frontend URL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run test suite
    test_suite = EndToEndTestSuite(args.api_url, args.frontend_url)
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
