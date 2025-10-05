#!/usr/bin/env python3
"""
Comprehensive Login Test Suite for AI Stock Trading Platform
Tests all login scenarios including single role, multiple roles, and role selection
"""

import os
import sys
import requests
import json
import time
import logging
import unittest
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

class LoginTestSuite:
    """Comprehensive test suite for login functionality"""
    
    def __init__(self, api_base_url: str, frontend_url: str):
        self.api_base_url = api_base_url
        self.frontend_url = frontend_url
        self.session = requests.Session()
        self.test_results = []
        
        # Test users from the backend
        self.test_users = {
            'single_role': {
                'ranjit': {'password': 'password', 'expected_roles': ['agent'], 'primary_role': 'agent'},
                'admin': {'password': 'password', 'expected_roles': ['admin'], 'primary_role': 'admin'},
                'john': {'password': 'password', 'expected_roles': ['customer'], 'primary_role': 'customer'}
            },
            'multiple_roles': {
                'saji': {'password': 'password', 'expected_roles': ['admin', 'agent'], 'primary_role': None},
                'sarah': {'password': 'password', 'expected_roles': ['agent', 'customer'], 'primary_role': None},
                'mike': {'password': 'password', 'expected_roles': ['admin', 'agent'], 'primary_role': None}
            }
        }
        
        # Invalid credentials for testing
        self.invalid_credentials = [
            {'username': 'nonexistent', 'password': 'password'},
            {'username': 'ranjit', 'password': 'wrongpassword'},
            {'username': '', 'password': 'password'},
            {'username': 'ranjit', 'password': ''},
            {'username': '', 'password': ''}
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

    def test_health_check(self) -> bool:
        """Test API health check"""
        try:
            response = self.session.get(f'{self.api_base_url}/api/health', timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test_result("Health Check", True, "API is healthy")
                    return True
                else:
                    self.log_test_result("Health Check", False, f"Unexpected status: {data.get('status')}")
                    return False
            else:
                self.log_test_result("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test_result("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_single_role_login(self, username: str, user_data: Dict) -> bool:
        """Test login for single role users"""
        try:
            login_data = {
                'email_or_username': username,
                'password': user_data['password']
            }
            
            response = self.session.post(
                f'{self.api_base_url}/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'token', 'refresh_token', 'user', 'expires_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(
                        f"Single Role Login - {username}",
                        False,
                        f"Missing fields: {missing_fields}",
                        {'response': data}
                    )
                    return False
                
                # Check user data
                user = data['user']
                expected_roles = user_data['expected_roles']
                expected_primary = user_data['primary_role']
                
                # Validate roles
                if user.get('roles') != expected_roles:
                    self.log_test_result(
                        f"Single Role Login - {username}",
                        False,
                        f"Roles mismatch. Expected: {expected_roles}, Got: {user.get('roles')}",
                        {'response': data}
                    )
                    return False
                
                # Validate primary role
                if user.get('primary_role') != expected_primary:
                    self.log_test_result(
                        f"Single Role Login - {username}",
                        False,
                        f"Primary role mismatch. Expected: {expected_primary}, Got: {user.get('primary_role')}",
                        {'response': data}
                    )
                    return False
                
                # Validate multiple roles flag
                if user.get('has_multiple_roles') != False:
                    self.log_test_result(
                        f"Single Role Login - {username}",
                        False,
                        f"has_multiple_roles should be False for single role user",
                        {'response': data}
                    )
                    return False
                
                self.log_test_result(
                    f"Single Role Login - {username}",
                    True,
                    f"Login successful with role: {user.get('primary_role')}",
                    {'user_id': user.get('id'), 'roles': user.get('roles')}
                )
                return True
            else:
                self.log_test_result(
                    f"Single Role Login - {username}",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {'status_code': response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                f"Single Role Login - {username}",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_multiple_role_login(self, username: str, user_data: Dict) -> bool:
        """Test login for multiple role users"""
        try:
            login_data = {
                'email_or_username': username,
                'password': user_data['password']
            }
            
            response = self.session.post(
                f'{self.api_base_url}/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['success', 'token', 'refresh_token', 'user', 'expires_at']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(
                        f"Multiple Role Login - {username}",
                        False,
                        f"Missing fields: {missing_fields}",
                        {'response': data}
                    )
                    return False
                
                # Check user data
                user = data['user']
                expected_roles = user_data['expected_roles']
                
                # Validate roles
                if set(user.get('roles', [])) != set(expected_roles):
                    self.log_test_result(
                        f"Multiple Role Login - {username}",
                        False,
                        f"Roles mismatch. Expected: {expected_roles}, Got: {user.get('roles')}",
                        {'response': data}
                    )
                    return False
                
                # Validate multiple roles flag
                if user.get('has_multiple_roles') != True:
                    self.log_test_result(
                        f"Multiple Role Login - {username}",
                        False,
                        f"has_multiple_roles should be True for multiple role user",
                        {'response': data}
                    )
                    return False
                
                # Validate primary role is None (should trigger role selection)
                if user.get('primary_role') is not None:
                    self.log_test_result(
                        f"Multiple Role Login - {username}",
                        False,
                        f"primary_role should be None for multiple role user, got: {user.get('primary_role')}",
                        {'response': data}
                    )
                    return False
                
                self.log_test_result(
                    f"Multiple Role Login - {username}",
                    True,
                    f"Login successful with roles: {user.get('roles')} (requires role selection)",
                    {'user_id': user.get('id'), 'roles': user.get('roles'), 'multiple_roles': user.get('has_multiple_roles')}
                )
                return True
            else:
                self.log_test_result(
                    f"Multiple Role Login - {username}",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {'status_code': response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                f"Multiple Role Login - {username}",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_invalid_credentials(self) -> bool:
        """Test invalid login attempts"""
        passed_tests = 0
        total_tests = len(self.invalid_credentials)
        
        for i, creds in enumerate(self.invalid_credentials):
            try:
                response = self.session.post(
                    f'{self.api_base_url}/api/auth/login',
                    json=creds,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                # Should return 401 for invalid credentials
                if response.status_code == 401:
                    data = response.json()
                    if not data.get('success', True):  # success should be False
                        self.log_test_result(
                            f"Invalid Credentials Test {i+1}",
                            True,
                            f"Correctly rejected: {creds.get('username', 'empty')}"
                        )
                        passed_tests += 1
                    else:
                        self.log_test_result(
                            f"Invalid Credentials Test {i+1}",
                            False,
                            f"Success flag not False for invalid credentials: {creds}"
                        )
                else:
                    self.log_test_result(
                        f"Invalid Credentials Test {i+1}",
                        False,
                        f"Expected 401, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Invalid Credentials Test {i+1}",
                    False,
                    f"Exception: {str(e)}"
                )
        
        success_rate = passed_tests / total_tests
        if success_rate == 1.0:
            self.log_test_result(
                "Invalid Credentials Suite",
                True,
                f"All {total_tests} invalid credential tests passed"
            )
            return True
        else:
            self.log_test_result(
                "Invalid Credentials Suite",
                False,
                f"Only {passed_tests}/{total_tests} invalid credential tests passed"
            )
            return False

    def test_session_verification(self) -> bool:
        """Test session verification endpoint"""
        try:
            # First login to get a token
            login_data = {
                'email_or_username': 'ranjit',
                'password': 'password'
            }
            
            login_response = self.session.post(
                f'{self.api_base_url}/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.log_test_result(
                    "Session Verification",
                    False,
                    f"Login failed: {login_response.status_code}"
                )
                return False
            
            token = login_response.json().get('token')
            if not token:
                self.log_test_result(
                    "Session Verification",
                    False,
                    "No token received from login"
                )
                return False
            
            # Test session verification
            headers = {'Authorization': f'Bearer {token}'}
            verify_response = self.session.post(
                f'{self.api_base_url}/api/auth/verify-session',
                headers=headers,
                timeout=10
            )
            
            if verify_response.status_code == 200:
                data = verify_response.json()
                if data.get('valid'):
                    self.log_test_result(
                        "Session Verification",
                        True,
                        "Session verification successful"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Session Verification",
                        False,
                        f"Session marked as invalid: {data.get('message', 'No message')}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Session Verification",
                    False,
                    f"HTTP {verify_response.status_code}: {verify_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Session Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_refresh_token(self) -> bool:
        """Test refresh token functionality"""
        try:
            # Test refresh token endpoint
            refresh_data = {
                'refresh_token': 'demo_refresh_token_456'
            }
            
            response = self.session.post(
                f'{self.api_base_url}/api/auth/refresh-token',
                json=refresh_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'token' in data:
                    self.log_test_result(
                        "Refresh Token",
                        True,
                        "Token refresh successful"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Refresh Token",
                        False,
                        f"Invalid refresh response: {data}"
                    )
                    return False
            else:
                self.log_test_result(
                    "Refresh Token",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Refresh Token",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_cors_headers(self) -> bool:
        """Test CORS headers for login endpoint"""
        try:
            # Test preflight request
            response = self.session.options(
                f'{self.api_base_url}/api/auth/login',
                headers={
                    'Origin': 'https://example.com',
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
                        "CORS Headers",
                        True,
                        f"CORS headers present: {cors_headers}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "CORS Headers",
                        False,
                        "CORS headers missing"
                    )
                    return False
            else:
                self.log_test_result(
                    "CORS Headers",
                    False,
                    f"Preflight request failed: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "CORS Headers",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def run_all_tests(self) -> bool:
        """Run all test suites"""
        logger.info("=" * 80)
        logger.info("STARTING COMPREHENSIVE LOGIN TEST SUITE")
        logger.info("=" * 80)
        logger.info(f"API Base URL: {self.api_base_url}")
        logger.info(f"Frontend URL: {self.frontend_url}")
        logger.info("")
        
        # Test 1: Health Check
        if not self.test_health_check():
            logger.error("Health check failed. Aborting tests.")
            return False
        
        logger.info("")
        
        # Test 2: Single Role Users
        logger.info("Testing Single Role Users...")
        single_role_passed = 0
        single_role_total = len(self.test_users['single_role'])
        
        for username, user_data in self.test_users['single_role'].items():
            if self.test_single_role_login(username, user_data):
                single_role_passed += 1
        
        logger.info(f"Single Role Tests: {single_role_passed}/{single_role_total} passed")
        logger.info("")
        
        # Test 3: Multiple Role Users
        logger.info("Testing Multiple Role Users...")
        multiple_role_passed = 0
        multiple_role_total = len(self.test_users['multiple_roles'])
        
        for username, user_data in self.test_users['multiple_roles'].items():
            if self.test_multiple_role_login(username, user_data):
                multiple_role_passed += 1
        
        logger.info(f"Multiple Role Tests: {multiple_role_passed}/{multiple_role_total} passed")
        logger.info("")
        
        # Test 4: Invalid Credentials
        logger.info("Testing Invalid Credentials...")
        invalid_creds_passed = self.test_invalid_credentials()
        logger.info("")
        
        # Test 5: Session Management
        logger.info("Testing Session Management...")
        session_passed = self.test_session_verification()
        refresh_passed = self.test_refresh_token()
        logger.info("")
        
        # Test 6: CORS
        logger.info("Testing CORS Headers...")
        cors_passed = self.test_cors_headers()
        logger.info("")
        
        # Summary - Count actual test results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['passed']])
        failed_tests = total_tests - passed_tests
        
        logger.info("=" * 80)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info("")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! 🎉")
            return True
        else:
            logger.error("❌ SOME TESTS FAILED")
            
            # Show failed tests
            failed_tests_list = [r for r in self.test_results if not r['passed']]
            if failed_tests_list:
                logger.error("\nFailed Tests:")
                for test in failed_tests_list:
                    logger.error(f"  - {test['test_name']}: {test['message']}")
            
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run comprehensive login tests')
    parser.add_argument('--api-url', default=API_BASE_URL, help='API base URL')
    parser.add_argument('--frontend-url', default=FRONTEND_URL, help='Frontend URL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run test suite
    test_suite = LoginTestSuite(args.api_url, args.frontend_url)
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
