#!/usr/bin/env python3
"""
Test script for user management system
"""

import os
import sys
import requests
import json
import time
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
API_BASE = os.environ.get('API_BASE_URL', 'http://localhost:8080/api')
TEST_EMAIL = 'test@example.com'
TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'TestPassword123!'

class UserSystemTester:
    def __init__(self, api_base):
        self.api_base = api_base
        self.session = requests.Session()
        self.auth_token = None

    def test_health_check(self):
        """Test API health check"""
        try:
            response = self.session.get(f'{self.api_base}/health')
            if response.status_code == 200:
                logger.info("✅ Health check passed")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        try:
            data = {
                'email': TEST_EMAIL,
                'username': TEST_USERNAME,
                'password': TEST_PASSWORD,
                'first_name': 'Test',
                'last_name': 'User'
            }

            response = self.session.post(f'{self.api_base}/auth/register', json=data)

            if response.status_code == 201:
                logger.info("✅ User registration passed")
                return True
            elif response.status_code == 400 and 'already' in response.json().get('message', ''):
                logger.info("✅ User registration passed (user already exists)")
                return True
            else:
                logger.error(f"❌ User registration failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ User registration error: {e}")
            return False

    def test_user_login(self):
        """Test user login"""
        try:
            data = {
                'email_or_username': TEST_EMAIL,
                'password': TEST_PASSWORD
            }

            response = self.session.post(f'{self.api_base}/auth/login', json=data)

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'token' in result:
                    self.auth_token = result['token']
                    # Set authorization header for future requests
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    logger.info("✅ User login passed")
                    return True
                else:
                    logger.error(f"❌ User login failed: Invalid response format")
                    return False
            else:
                logger.error(f"❌ User login failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ User login error: {e}")
            return False

    def test_get_current_user(self):
        """Test getting current user info"""
        try:
            if not self.auth_token:
                logger.error("❌ Get current user failed: No auth token")
                return False

            response = self.session.get(f'{self.api_base}/auth/me')

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'user' in result:
                    logger.info("✅ Get current user passed")
                    return True
                else:
                    logger.error(f"❌ Get current user failed: Invalid response format")
                    return False
            else:
                logger.error(f"❌ Get current user failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Get current user error: {e}")
            return False

    def test_update_profile(self):
        """Test profile update"""
        try:
            if not self.auth_token:
                logger.error("❌ Update profile failed: No auth token")
                return False

            data = {
                'first_name': 'Updated',
                'last_name': 'Name',
                'trading_experience': 'intermediate',
                'risk_tolerance': 'medium'
            }

            response = self.session.put(f'{self.api_base}/users/profile', json=data)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info("✅ Update profile passed")
                    return True
                else:
                    logger.error(f"❌ Update profile failed: {result.get('message')}")
                    return False
            else:
                logger.error(f"❌ Update profile failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Update profile error: {e}")
            return False

    def test_session_verification(self):
        """Test session verification"""
        try:
            if not self.auth_token:
                logger.error("❌ Session verification failed: No auth token")
                return False

            response = self.session.post(f'{self.api_base}/auth/verify-session')

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('session_valid'):
                    logger.info("✅ Session verification passed")
                    return True
                else:
                    logger.error(f"❌ Session verification failed: Invalid session")
                    return False
            else:
                logger.error(f"❌ Session verification failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Session verification error: {e}")
            return False

    def test_admin_login(self):
        """Test admin login"""
        try:
            admin_data = {
                'email_or_username': os.environ.get('ADMIN_EMAIL', 'admin@aitrading.com'),
                'password': os.environ.get('ADMIN_PASSWORD', 'AdminPassword123!')
            }

            response = self.session.post(f'{self.api_base}/auth/login', json=admin_data)

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('user', {}).get('role') == 'admin':
                    logger.info("✅ Admin login passed")
                    return True
                else:
                    logger.error(f"❌ Admin login failed: Not an admin user")
                    return False
            else:
                logger.error(f"❌ Admin login failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Admin login error: {e}")
            return False

    def test_user_logout(self):
        """Test user logout"""
        try:
            if not self.auth_token:
                logger.error("❌ User logout failed: No auth token")
                return False

            response = self.session.post(f'{self.api_base}/auth/logout')

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Clear auth token
                    self.auth_token = None
                    self.session.headers.pop('Authorization', None)
                    logger.info("✅ User logout passed")
                    return True
                else:
                    logger.error(f"❌ User logout failed: {result.get('message')}")
                    return False
            else:
                logger.error(f"❌ User logout failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ User logout error: {e}")
            return False

    def run_tests(self):
        """Run all tests"""
        logger.info("Starting user management system tests...")
        logger.info(f"API Base URL: {self.api_base}")

        tests = [
            ('Health Check', self.test_health_check),
            ('User Registration', self.test_user_registration),
            ('User Login', self.test_user_login),
            ('Get Current User', self.test_get_current_user),
            ('Update Profile', self.test_update_profile),
            ('Session Verification', self.test_session_verification),
            ('Admin Login', self.test_admin_login),
            ('User Logout', self.test_user_logout)
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            logger.info(f"\n--- Running {test_name} ---")
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"❌ {test_name} crashed: {e}")
                failed += 1

            # Add small delay between tests
            time.sleep(1)

        # Summary
        total = passed + failed
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST RESULTS: {passed}/{total} tests passed")

        if failed > 0:
            logger.info(f"❌ {failed} tests failed")
            return False
        else:
            logger.info("✅ All tests passed!")
            return True

def wait_for_api(api_base, max_wait=30):
    """Wait for API to be available"""
    logger.info(f"Waiting for API at {api_base}...")

    for i in range(max_wait):
        try:
            response = requests.get(f'{api_base}/health', timeout=2)
            if response.status_code == 200:
                logger.info("API is ready!")
                return True
        except Exception:
            pass

        logger.info(f"Waiting... ({i+1}/{max_wait})")
        time.sleep(1)

    logger.error("API did not become available in time")
    return False

if __name__ == '__main__':
    # Check if API is available
    if not wait_for_api(API_BASE):
        logger.error("Cannot connect to API. Make sure the server is running.")
        sys.exit(1)

    # Run tests
    tester = UserSystemTester(API_BASE)
    success = tester.run_tests()

    sys.exit(0 if success else 1)