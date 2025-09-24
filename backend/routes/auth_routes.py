#!/usr/bin/env python3
"""
Authentication API Routes for AI Stock Trading Platform
"""

from flask import Blueprint, request, jsonify, g
import logging

from middleware import (
    require_auth, validate_json, rate_limit, log_api_access,
    security_headers, get_request_context
)
from services.auth_service import auth_service, AuthenticationError, ValidationError

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@log_api_access
@security_headers
@rate_limit(max_requests=5, window_seconds=300)  # 5 registrations per 5 minutes
@validate_json(required_fields=['email', 'username', 'password'])
def register():
    """User registration endpoint"""
    try:
        data = g.json_data
        request_context = get_request_context()

        result = auth_service.register_user(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            request_context=request_context
        )

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'message': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Registration failed',
            'message': 'An error occurred during registration'
        }), 500

@auth_bp.route('/login', methods=['POST'])
@log_api_access
@security_headers
@rate_limit(max_requests=10, window_seconds=300)  # 10 login attempts per 5 minutes
@validate_json(required_fields=['email_or_username', 'password'])
def login():
    """User login endpoint"""
    try:
        data = g.json_data
        request_context = get_request_context()

        result = auth_service.authenticate_user(
            email_or_username=data['email_or_username'],
            password=data['password'],
            remember_me=data.get('remember_me', False),
            request_context=request_context
        )

        if result['success']:
            response = jsonify(result)

            # Set HTTP-only cookie for additional security
            if 'token' in result:
                response.set_cookie(
                    'auth_token',
                    result['token'],
                    max_age=86400 if not data.get('remember_me') else 86400 * 30,  # 1 day or 30 days
                    httponly=True,
                    secure=request.is_secure,
                    samesite='Strict'
                )

            return response, 200
        else:
            return jsonify(result), 400

    except AuthenticationError as e:
        return jsonify({
            'success': False,
            'error': 'Authentication failed',
            'message': str(e)
        }), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Login failed',
            'message': 'An error occurred during login'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@log_api_access
@security_headers
@require_auth
def logout():
    """User logout endpoint"""
    try:
        # Extract session token from JWT
        from middleware.auth_middleware import extract_token_from_request
        token = extract_token_from_request()

        if token:
            payload = auth_service.decode_jwt_token(token)
            session_token = payload.get('session_token')

            if session_token:
                request_context = get_request_context()
                logout_all = request.json.get('logout_all', False) if request.is_json else False

                result = auth_service.logout_user(
                    session_token=session_token,
                    logout_all=logout_all,
                    request_context=request_context
                )

                response = jsonify(result)
                response.set_cookie('auth_token', '', expires=0)  # Clear cookie
                return response, 200

        return jsonify({
            'success': False,
            'error': 'Invalid session',
            'message': 'Could not find valid session to logout'
        }), 400

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Logout failed',
            'message': 'An error occurred during logout'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@log_api_access
@security_headers
@require_auth
def get_current_user():
    """Get current user information"""
    try:
        return jsonify({
            'success': True,
            'user': g.current_user
        }), 200

    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user information',
            'message': 'An error occurred while fetching user data'
        }), 500

@auth_bp.route('/verify-session', methods=['POST'])
@log_api_access
@security_headers
def verify_session():
    """Verify session validity"""
    try:
        from middleware.auth_middleware import extract_token_from_request
        token = extract_token_from_request()

        if not token:
            return jsonify({
                'success': False,
                'session_valid': False,
                'message': 'No token provided'
            }), 401

        payload = auth_service.decode_jwt_token(token)
        session_token = payload.get('session_token')

        if session_token:
            result = auth_service.verify_session(session_token)
            return jsonify(result), 200 if result['success'] else 401

        return jsonify({
            'success': False,
            'session_valid': False,
            'message': 'Invalid token format'
        }), 401

    except AuthenticationError as e:
        return jsonify({
            'success': False,
            'session_valid': False,
            'message': str(e)
        }), 401

    except Exception as e:
        logger.error(f"Session verification error: {e}")
        return jsonify({
            'success': False,
            'session_valid': False,
            'message': 'Session verification failed'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
@log_api_access
@security_headers
@rate_limit(max_requests=3, window_seconds=300)  # 3 requests per 5 minutes
@validate_json(required_fields=['email'])
def forgot_password():
    """Request password reset"""
    try:
        data = g.json_data
        request_context = get_request_context()

        result = auth_service.request_password_reset(
            email=data['email'],
            request_context=request_context
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        # Always return success to prevent email enumeration
        return jsonify({
            'success': True,
            'message': 'If the email address exists, a password reset link has been sent.'
        }), 200

@auth_bp.route('/reset-password', methods=['POST'])
@log_api_access
@security_headers
@rate_limit(max_requests=5, window_seconds=300)  # 5 reset attempts per 5 minutes
@validate_json(required_fields=['reset_token', 'new_password'])
def reset_password():
    """Reset password with token"""
    try:
        data = g.json_data
        request_context = get_request_context()

        result = auth_service.reset_password(
            reset_token=data['reset_token'],
            new_password=data['new_password'],
            request_context=request_context
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except (AuthenticationError, ValidationError) as e:
        return jsonify({
            'success': False,
            'error': 'Password reset failed',
            'message': str(e)
        }), 400

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({
            'success': False,
            'error': 'Password reset failed',
            'message': 'An error occurred during password reset'
        }), 500

@auth_bp.route('/refresh-token', methods=['POST'])
@log_api_access
@security_headers
@validate_json(required_fields=['refresh_token'])
def refresh_token():
    """Refresh authentication token"""
    try:
        data = g.json_data
        refresh_token = data['refresh_token']

        # Find session by refresh token
        from database import db_manager
        from models import UserSession, User

        with db_manager.get_session() as session:
            user_session = session.query(UserSession).filter(
                UserSession.refresh_token == refresh_token,
                UserSession.is_active == True
            ).first()

            if not user_session or not user_session.is_valid():
                return jsonify({
                    'success': False,
                    'error': 'Invalid refresh token',
                    'message': 'Refresh token is invalid or expired'
                }), 401

            # Get user
            user = session.query(User).get(user_session.user_id)
            if not user or not user.is_active():
                return jsonify({
                    'success': False,
                    'error': 'User not active',
                    'message': 'User account is not active'
                }), 401

            # Refresh session
            user_session.refresh()

            # Generate new JWT token
            new_token = auth_service._generate_jwt_token(user.id, user_session.session_token)

            return jsonify({
                'success': True,
                'token': new_token,
                'expires_at': user_session.expires_at.isoformat(),
                'user': user.to_dict()
            }), 200

    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'error': 'Token refresh failed',
            'message': 'An error occurred while refreshing token'
        }), 500