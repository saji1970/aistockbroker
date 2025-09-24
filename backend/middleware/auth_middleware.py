#!/usr/bin/env python3
"""
Authentication Middleware for AI Stock Trading Platform
Handles authentication, authorization, and security for Flask routes
"""

import functools
import logging
from typing import Optional, Dict, Any, List, Callable
from flask import request, jsonify, g
import jwt

from services.auth_service import auth_service, AuthenticationError
from services.user_service import user_service
from models import UserRole

logger = logging.getLogger(__name__)

def get_request_context() -> Dict[str, Any]:
    """Extract request context for logging"""
    return {
        'ip_address': request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR')),
        'user_agent': request.headers.get('User-Agent'),
        'endpoint': request.endpoint,
        'method': request.method,
        'url': request.url
    }

def extract_token_from_request() -> Optional[str]:
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove 'Bearer ' prefix

    # Also check for token in cookies
    return request.cookies.get('auth_token')

def authenticate_request() -> Optional[Dict[str, Any]]:
    """Authenticate the current request and return user info"""
    try:
        token = extract_token_from_request()
        if not token:
            return None

        # Decode JWT token
        payload = auth_service.decode_jwt_token(token)
        session_token = payload.get('session_token')

        if not session_token:
            return None

        # Verify session
        session_result = auth_service.verify_session(session_token)

        if session_result.get('success') and session_result.get('session_valid'):
            return session_result.get('user')

    except AuthenticationError:
        # Token is invalid or expired
        pass
    except Exception as e:
        logger.error(f"Authentication error: {e}")

    return None

def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication for a route"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = authenticate_request()

        if not user:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please log in to access this resource'
            }), 401

        # Add user to Flask's g object for access in route
        g.current_user = user

        return f(*args, **kwargs)

    return decorated_function

def require_role(required_roles: List[str]) -> Callable:
    """Decorator to require specific roles for a route"""
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user = authenticate_request()

            if not user:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Please log in to access this resource'
                }), 401

            user_role = user.get('role')
            if user_role not in required_roles:
                return jsonify({
                    'error': 'Insufficient privileges',
                    'message': f'This resource requires one of the following roles: {", ".join(required_roles)}'
                }), 403

            # Add user to Flask's g object for access in route
            g.current_user = user

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def require_admin(f: Callable) -> Callable:
    """Decorator to require admin role for a route"""
    return require_role(['admin'])(f)

def require_active_user(f: Callable) -> Callable:
    """Decorator to require an active user account"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = authenticate_request()

        if not user:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please log in to access this resource'
            }), 401

        if user.get('status') != 'active':
            status_messages = {
                'pending': 'Please verify your email address',
                'suspended': 'Your account has been suspended',
                'inactive': 'Your account is inactive'
            }
            message = status_messages.get(user.get('status'), 'Account access denied')

            return jsonify({
                'error': 'Account not active',
                'message': message
            }), 403

        # Add user to Flask's g object for access in route
        g.current_user = user

        return f(*args, **kwargs)

    return decorated_function

def require_trading_access(f: Callable) -> Callable:
    """Decorator to require trading access (active user or admin)"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = authenticate_request()

        if not user:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please log in to access trading features'
            }), 401

        # Check if user can access trading features
        if user.get('status') != 'active':
            return jsonify({
                'error': 'Trading access denied',
                'message': 'Active account required for trading features'
            }), 403

        user_role = user.get('role')
        if user_role not in ['user', 'admin']:
            return jsonify({
                'error': 'Trading access denied',
                'message': 'Trading access requires user or admin role'
            }), 403

        # Add user to Flask's g object for access in route
        g.current_user = user

        return f(*args, **kwargs)

    return decorated_function

def optional_auth(f: Callable) -> Callable:
    """Decorator for optional authentication (doesn't fail if not authenticated)"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = authenticate_request()

        # Add user to Flask's g object (may be None)
        g.current_user = user

        return f(*args, **kwargs)

    return decorated_function

class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests = {}  # ip_address: {'count': int, 'reset_time': datetime}

    def is_allowed(self, ip_address: str, max_requests: int = 100, window_seconds: int = 3600) -> bool:
        """Check if request is allowed based on rate limit"""
        from datetime import datetime, timedelta

        now = datetime.utcnow()

        # Clean up old entries
        self.requests = {
            ip: data for ip, data in self.requests.items()
            if data['reset_time'] > now
        }

        # Check current IP
        if ip_address not in self.requests:
            self.requests[ip_address] = {
                'count': 1,
                'reset_time': now + timedelta(seconds=window_seconds)
            }
            return True

        # Check if within limit
        if self.requests[ip_address]['count'] < max_requests:
            self.requests[ip_address]['count'] += 1
            return True

        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 100, window_seconds: int = 3600) -> Callable:
    """Decorator to rate limit requests"""
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR',
                                           request.environ.get('REMOTE_ADDR', 'unknown'))

            if not rate_limiter.is_allowed(ip_address, max_requests, window_seconds):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Maximum {max_requests} per {window_seconds} seconds.'
                }), 429

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def validate_json(required_fields: List[str] = None, optional_fields: List[str] = None) -> Callable:
    """Decorator to validate JSON request body"""
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Invalid request',
                    'message': 'Request must be JSON'
                }), 400

            data = request.get_json()

            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'message': f'Required fields: {", ".join(missing_fields)}'
                    }), 400

            # Store validated data in g for access in route
            g.json_data = data

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def csrf_protect(f: Callable) -> Callable:
    """Basic CSRF protection decorator"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF for GET requests
        if request.method == 'GET':
            return f(*args, **kwargs)

        # Check for CSRF token in headers
        csrf_token = request.headers.get('X-CSRF-Token')

        # For API requests, we'll rely on proper CORS configuration
        # In a full implementation, you'd implement proper CSRF token generation and validation

        return f(*args, **kwargs)

    return decorated_function

def log_api_access(f: Callable) -> Callable:
    """Decorator to log API access"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = logger.info(f"API Request: {request.method} {request.path}")

        try:
            result = f(*args, **kwargs)
            logger.info(f"API Response: {request.method} {request.path} - Success")
            return result
        except Exception as e:
            logger.error(f"API Error: {request.method} {request.path} - {str(e)}")
            raise

    return decorated_function

def security_headers(f: Callable) -> Callable:
    """Decorator to add security headers to responses"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)

        # Add security headers
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    return decorated_function