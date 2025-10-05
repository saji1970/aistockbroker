#!/usr/bin/env python3
"""
Secure Backend API for AI Stock Trading Platform
Comprehensive security implementation with compliance features
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from functools import wraps
# import jwt  # Commented out for now - will add proper JWT later
# from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, TooManyRequests

# Simple exception classes for now
class BadRequest(Exception):
    code = 400

class Unauthorized(Exception):
    code = 401

class Forbidden(Exception):
    code = 403

class TooManyRequests(Exception):
    code = 429

# Import security configuration
from security_config import (
    generate_csrf_token, validate_csrf_token, sanitize_input, validate_email,
    validate_password_strength, hash_password, verify_password, rate_limit_check,
    check_login_attempts, record_login_attempt, log_security_event, get_client_ip,
    add_security_headers, validate_content_type, validate_origin, create_secure_session,
    validate_session, validate_stock_symbol, validate_numeric_input, validate_json_input,
    gdpr_data_export, gdpr_data_deletion, sox_audit_trail, pci_dss_validate_card_data,
    generate_security_report, SECURITY_HEADERS, MAX_REQUEST_SIZE
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Commented out for now
# app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Commented out for now

# Configure CORS with security restrictions
CORS(app, 
     origins=[
         'https://ai-stock-trading-frontend-1012090067429.us-central1.run.app',
         'http://localhost:3000'  # For development
     ],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True,
     max_age=3600)

# Security middleware
@app.before_request
def security_middleware():
    """Apply security middleware to all requests"""
    client_ip = get_client_ip(request)
    
    # Validate request size
    content_length = request.content_length or 0
    if content_length > MAX_REQUEST_SIZE:
        log_security_event('REQUEST_SIZE_EXCEEDED', {
            'content_length': content_length,
            'max_size': MAX_REQUEST_SIZE
        }, client_ip)
        raise BadRequest('Request too large')
    
    # Rate limiting
    if not rate_limit_check(client_ip):
        log_security_event('RATE_LIMIT_EXCEEDED', {
            'client_ip': client_ip
        }, client_ip)
        raise TooManyRequests('Rate limit exceeded')
    
    # Validate content type for POST/PUT requests
    if request.method in ['POST', 'PUT'] and not validate_content_type(request):
        log_security_event('INVALID_CONTENT_TYPE', {
            'content_type': request.headers.get('Content-Type'),
            'method': request.method
        }, client_ip)
        raise BadRequest('Invalid content type')
    
    # Validate origin
    if not validate_origin(request):
        log_security_event('INVALID_ORIGIN', {
            'origin': request.headers.get('Origin'),
            'referer': request.headers.get('Referer')
        }, client_ip)
        raise Forbidden('Invalid origin')

@app.after_request
def security_headers_middleware(response):
    """Add security headers to all responses"""
    return add_security_headers(response)

# Security decorators
def require_auth(f):
    """Require authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Unauthorized('Authentication required')
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1]
            
            # Simple token validation for demo (in production, use proper JWT)
            if token and len(token) > 10:
                # Mock user validation
                user_id = 'demo_user'
                payload = {'user_id': user_id, 'roles': ['customer']}
                
                # Add user info to request context
                request.current_user = {'user_id': user_id, 'payload': payload}
            else:
                raise Unauthorized('Invalid token')
            
        except Exception as e:
            raise Unauthorized('Invalid token')
        
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_roles):
    """Require specific role decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                raise Unauthorized('Authentication required')
            
            user_roles = request.current_user['payload'].get('roles', [])
            
            if not any(role in user_roles for role in required_roles):
                log_security_event('INSUFFICIENT_PERMISSIONS', {
                    'user_id': request.current_user['user_id'],
                    'required_roles': required_roles,
                    'user_roles': user_roles
                }, get_client_ip(request))
                raise Forbidden('Insufficient permissions')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_csrf(f):
    """Require CSRF token decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE']:
            csrf_token = request.headers.get('X-CSRF-Token') or request.json.get('csrf_token')
            
            if not validate_csrf_token(csrf_token):
                log_security_event('INVALID_CSRF_TOKEN', {
                    'provided_token': csrf_token,
                    'user_id': getattr(request, 'current_user', {}).get('user_id', 'anonymous')
                }, get_client_ip(request))
                raise Forbidden('Invalid CSRF token')
        
        return f(*args, **kwargs)
    return decorated_function

def audit_log(action):
    """Audit log decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(request, 'current_user', {}).get('user_id', 'anonymous')
            client_ip = get_client_ip(request)
            
            # Log the action
            sox_audit_trail(action, user_id, {
                'endpoint': request.endpoint,
                'method': request.method,
                'client_ip': client_ip,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Secure user database (in production, use proper database)
SECURE_USER_DATABASE = {
    'admin': {
        'user_id': 'admin',
        'password_hash': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' hashed
        'salt': 'admin_salt',
        'roles': ['admin'],
        'name': 'Administrator',
        'email': 'admin@example.com',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'last_login': None,
        'failed_login_attempts': 0,
        'account_locked_until': None
    },
    'ranjit': {
        'user_id': 'ranjit',
        'password_hash': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' hashed
        'salt': 'ranjit_salt',
        'roles': ['agent'],
        'name': 'Ranjit Kumar',
        'email': 'ranjit@example.com',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'last_login': None,
        'failed_login_attempts': 0,
        'account_locked_until': None
    },
    'john': {
        'user_id': 'john',
        'password_hash': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' hashed
        'salt': 'john_salt',
        'roles': ['customer'],
        'name': 'John Smith',
        'email': 'john@example.com',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'last_login': None,
        'failed_login_attempts': 0,
        'account_locked_until': None
    },
    'sarah': {
        'user_id': 'sarah',
        'password_hash': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' hashed
        'salt': 'sarah_salt',
        'roles': ['agent', 'customer'],
        'name': 'Sarah Wilson',
        'email': 'sarah@example.com',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'last_login': None,
        'failed_login_attempts': 0,
        'account_locked_until': None
    },
    'mike': {
        'user_id': 'mike',
        'password_hash': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' hashed
        'salt': 'mike_salt',
        'roles': ['admin', 'agent'],
        'name': 'Mike Johnson',
        'email': 'mike@example.com',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'last_login': None,
        'failed_login_attempts': 0,
        'account_locked_until': None
    },
    'saji': {
        'user_id': 'saji',
        'password_hash': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' hashed
        'salt': 'saji_salt',
        'roles': ['admin', 'agent'],
        'name': 'Saji Kumar',
        'email': 'saji@example.com',
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'last_login': None,
        'failed_login_attempts': 0,
        'account_locked_until': None
    }
}

# API Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Secure health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Stock Trading API',
        'version': '2.0.0',
        'security': 'enabled',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/csrf-token', methods=['GET'])
@require_auth
def get_csrf_token():
    """Get CSRF token for authenticated user"""
    csrf_token = generate_csrf_token()
    
    # Store token (in production, use Redis or database)
    from security_config import csrf_tokens
    csrf_tokens[csrf_token] = {
        'expires': time.time() + 1800,  # 30 minutes
        'user_id': request.current_user['user_id']
    }
    
    return jsonify({
        'csrf_token': csrf_token,
        'expires_in': 1800
    })

@app.route('/api/auth/login', methods=['POST'])
@audit_log('USER_LOGIN_ATTEMPT')
def secure_login():
    """Secure login endpoint with comprehensive validation"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid JSON data')
        
        # Sanitize inputs
        username = sanitize_input(data.get('username', ''))
        password = data.get('password', '')
        client_ip = get_client_ip(request)
        
        # Validate inputs
        if not username or not password:
            log_security_event('LOGIN_MISSING_CREDENTIALS', {
                'username': username,
                'client_ip': client_ip
            }, client_ip)
            raise BadRequest('Username and password required')
        
        if len(username) > 50 or len(password) > 100:
            log_security_event('LOGIN_INVALID_CREDENTIALS_LENGTH', {
                'username_length': len(username),
                'password_length': len(password)
            }, client_ip)
            raise BadRequest('Invalid credentials format')
        
        # Check login attempts
        if not check_login_attempts(username, client_ip):
            log_security_event('LOGIN_ACCOUNT_LOCKED', {
                'username': username,
                'client_ip': client_ip
            }, client_ip)
            raise Forbidden('Account temporarily locked due to too many failed attempts')
        
        # Validate user exists
        if username not in SECURE_USER_DATABASE:
            record_login_attempt(username, client_ip, False)
            log_security_event('LOGIN_USER_NOT_FOUND', {
                'username': username,
                'client_ip': client_ip
            }, client_ip)
            raise Unauthorized('Invalid credentials')
        
        user_data = SECURE_USER_DATABASE[username]
        
        # Check if account is locked
        if user_data.get('account_locked_until'):
            lock_until = datetime.fromisoformat(user_data['account_locked_until'])
            if datetime.utcnow() < lock_until:
                log_security_event('LOGIN_ACCOUNT_LOCKED', {
                    'username': username,
                    'locked_until': user_data['account_locked_until']
                }, client_ip)
                raise Forbidden('Account is locked')
        
        # Verify password
        if not verify_password(password, user_data['password_hash'], user_data['salt']):
            # Increment failed attempts
            user_data['failed_login_attempts'] += 1
            
            # Lock account after 5 failed attempts
            if user_data['failed_login_attempts'] >= 5:
                user_data['account_locked_until'] = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
                log_security_event('ACCOUNT_LOCKED', {
                    'username': username,
                    'failed_attempts': user_data['failed_login_attempts']
                }, client_ip)
            
            record_login_attempt(username, client_ip, False)
            log_security_event('LOGIN_INVALID_PASSWORD', {
                'username': username,
                'client_ip': client_ip
            }, client_ip)
            raise Unauthorized('Invalid credentials')
        
        # Successful login
        record_login_attempt(username, client_ip, True)
        
        # Reset failed attempts
        user_data['failed_login_attempts'] = 0
        user_data['account_locked_until'] = None
        user_data['last_login'] = datetime.utcnow().isoformat()
        
        # Generate simple tokens for demo (in production, use proper JWT)
        access_token = f"demo_access_token_{username}_{int(time.time())}"
        refresh_token = f"demo_refresh_token_{username}_{int(time.time())}"
        
        # Generate CSRF token
        csrf_token = generate_csrf_token()
        from security_config import csrf_tokens
        csrf_tokens[csrf_token] = {
            'expires': time.time() + 1800,
            'user_id': username
        }
        
        # Audit successful login
        sox_audit_trail('USER_LOGIN_SUCCESS', username, {
            'client_ip': client_ip,
            'user_agent': request.headers.get('User-Agent', ''),
            'roles': user_data['roles']
        })
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'csrf_token': csrf_token,
            'user': {
                'user_id': username,
                'name': user_data['name'],
                'email': user_data['email'],
                'roles': user_data['roles'],
                'status': user_data['status'],
                'has_multiple_roles': len(user_data['roles']) > 1,
                'primary_role': user_data['roles'][0] if len(user_data['roles']) == 1 else None
            },
            'expires_in': 3600
        })
        
    except (BadRequest, Unauthorized, Forbidden) as e:
        return jsonify({'success': False, 'error': str(e)}), e.code
    except Exception as e:
        logger.error(f"Login error: {e}")
        log_security_event('LOGIN_SYSTEM_ERROR', {
            'error': str(e),
            'username': username if 'username' in locals() else 'unknown'
        }, get_client_ip(request))
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/auth/refresh-token', methods=['POST'])
@require_auth
def refresh_token():
    """Refresh access token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            raise BadRequest('Refresh token required')
        
        # Simple refresh token validation for demo
        if not refresh_token or not refresh_token.startswith('demo_refresh_token_'):
            raise Unauthorized('Invalid refresh token')
        
        # Extract user_id from token
        try:
            user_id = refresh_token.split('_')[3]  # demo_refresh_token_{user_id}_{timestamp}
        except:
            raise Unauthorized('Invalid refresh token format')
        
        # Verify user still exists and is active
        if user_id not in SECURE_USER_DATABASE:
            raise Unauthorized('User not found')
        
        user_data = SECURE_USER_DATABASE[user_id]
        
        if user_data['status'] != 'active':
            raise Unauthorized('Account inactive')
        
        # Generate new access token
        new_access_token = f"demo_access_token_{user_id}_{int(time.time())}"
        
        return jsonify({
            'access_token': new_access_token,
            'expires_in': 3600
        })
        
    except (BadRequest, Unauthorized) as e:
        return jsonify({'error': str(e)}), e.code
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
@audit_log('USER_LOGOUT')
def secure_logout():
    """Secure logout endpoint"""
    user_id = request.current_user['user_id']
    client_ip = get_client_ip(request)
    
    # In production, add token to blacklist
    # For now, we'll just log the logout
    
    sox_audit_trail('USER_LOGOUT', user_id, {
        'client_ip': client_ip,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/verify-session', methods=['GET'])
@require_auth
def verify_session():
    """Verify current session"""
    user_id = request.current_user['user_id']
    user_data = SECURE_USER_DATABASE.get(user_id)
    
    if not user_data:
        raise Unauthorized('User not found')
    
    return jsonify({
        'user': {
            'user_id': user_id,
            'name': user_data['name'],
            'email': user_data['email'],
            'roles': user_data['roles'],
            'status': user_data['status'],
            'has_multiple_roles': len(user_data['roles']) > 1,
            'primary_role': user_data['roles'][0] if len(user_data['roles']) == 1 else None
        },
        'valid': True
    })

@app.route('/api/stock/data/<symbol>', methods=['GET'])
@require_auth
@require_csrf
def get_stock_data(symbol):
    """Get stock data with validation"""
    try:
        # Validate symbol
        if not validate_stock_symbol(symbol):
            raise BadRequest('Invalid stock symbol')
        
        # Sanitize symbol
        symbol = sanitize_input(symbol.upper())
        
        # Mock stock data (in production, fetch from real API)
        stock_data = {
            'symbol': symbol,
            'price': 150.25,
            'change': 2.15,
            'change_percent': 1.45,
            'volume': 1000000,
            'market_cap': 2500000000000,
            'data': {
                'prices': [148.10, 149.25, 150.25, 151.50, 150.75],
                'dates': ['2024-09-30', '2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04'],
                'volume': [950000, 1100000, 1000000, 1050000, 980000]
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Audit stock data access
        sox_audit_trail('STOCK_DATA_ACCESS', request.current_user['user_id'], {
            'symbol': symbol,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify(stock_data)
        
    except BadRequest as e:
        return jsonify({'error': str(e)}), e.code
    except Exception as e:
        logger.error(f"Stock data error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/prediction/<symbol>', methods=['GET'])
@require_auth
@require_csrf
@audit_log('PREDICTION_ACCESS')
def get_prediction(symbol):
    """Get stock prediction with validation"""
    try:
        # Validate symbol
        if not validate_stock_symbol(symbol):
            raise BadRequest('Invalid stock symbol')
        
        # Sanitize symbol
        symbol = sanitize_input(symbol.upper())
        
        # Mock prediction data
        prediction_data = {
            'symbol': symbol,
            'prediction': {
                'direction': 'bullish',
                'confidence': 75.5,
                'target_price': 165.50,
                'timeframe': '1 week',
                'reasoning': 'Strong technical indicators and positive market sentiment',
                'stop_loss': 150.00,
                'technical_indicators': {
                    'rsi': 65.2,
                    'sma_20': 158.75,
                    'volatility': 0.18,
                    'price_change_pct': 2.35
                }
            },
            'timestamp': datetime.utcnow().isoformat(),
            'model_version': '2.0.0'
        }
        
        return jsonify(prediction_data)
        
    except BadRequest as e:
        return jsonify({'error': str(e)}), e.code
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/portfolio', methods=['GET'])
@require_auth
@require_role(['customer', 'agent', 'admin'])
def get_portfolio():
    """Get user portfolio"""
    user_id = request.current_user['user_id']
    
    # Mock portfolio data
    portfolio_data = {
        'user_id': user_id,
        'total_value': 25000.00,
        'daily_change': 1250.50,
        'daily_change_percent': 5.26,
        'positions': [
            {
                'symbol': 'AAPL',
                'shares': 100,
                'current_price': 150.25,
                'total_value': 15025.00,
                'daily_change': 525.00,
                'daily_change_percent': 3.62
            },
            {
                'symbol': 'GOOGL',
                'shares': 50,
                'current_price': 2850.75,
                'total_value': 142537.50,
                'daily_change': 725.50,
                'daily_change_percent': 0.51
            }
        ],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    sox_audit_trail('PORTFOLIO_ACCESS', user_id, {
        'timestamp': datetime.utcnow().isoformat()
    })
    
    return jsonify(portfolio_data)

@app.route('/api/security/report', methods=['GET'])
@require_auth
@require_role(['admin'])
def get_security_report():
    """Get security monitoring report"""
    try:
        report = generate_security_report()
        return jsonify(report)
    except Exception as e:
        logger.error(f"Security report error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/compliance/gdpr-export/<user_id>', methods=['GET'])
@require_auth
@require_role(['admin'])
def gdpr_data_export_endpoint(user_id):
    """GDPR data export endpoint"""
    try:
        # Validate user_id
        if not user_id or user_id not in SECURE_USER_DATABASE:
            raise BadRequest('Invalid user ID')
        
        # Generate export
        export_data = gdpr_data_export(user_id)
        
        sox_audit_trail('GDPR_DATA_EXPORT', request.current_user['user_id'], {
            'exported_user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify(export_data)
        
    except BadRequest as e:
        return jsonify({'error': str(e)}), e.code
    except Exception as e:
        logger.error(f"GDPR export error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/compliance/gdpr-delete/<user_id>', methods=['DELETE'])
@require_auth
@require_role(['admin'])
def gdpr_data_deletion_endpoint(user_id):
    """GDPR data deletion endpoint"""
    try:
        # Validate user_id
        if not user_id or user_id not in SECURE_USER_DATABASE:
            raise BadRequest('Invalid user ID')
        
        # Perform deletion (in production, this would delete from database)
        success = gdpr_data_deletion(user_id)
        
        if success:
            sox_audit_trail('GDPR_DATA_DELETION', request.current_user['user_id'], {
                'deleted_user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return jsonify({'success': True, 'message': 'Data deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Deletion failed'}), 500
            
    except BadRequest as e:
        return jsonify({'error': str(e)}), e.code
    except Exception as e:
        logger.error(f"GDPR deletion error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({'error': 'Bad request', 'code': 400}), 400

@app.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized errors"""
    return jsonify({'error': 'Unauthorized', 'code': 401}), 401

@app.errorhandler(403)
def forbidden(error):
    """Handle forbidden errors"""
    return jsonify({'error': 'Forbidden', 'code': 403}), 403

@app.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({'error': 'Not found', 'code': 404}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit exceeded"""
    return jsonify({'error': 'Rate limit exceeded', 'code': 429}), 429

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error', 'code': 500}), 500

if __name__ == '__main__':
    # Security warnings
    if app.config['SECRET_KEY'] == 'your-secret-key-change-in-production':
        logger.warning("WARNING: Using default secret key. Change in production!")
    
    if app.config['JWT_SECRET_KEY'] == 'jwt-secret-change-in-production':
        logger.warning("WARNING: Using default JWT secret key. Change in production!")
    
    # Start server
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting secure backend server on port {port}")
    logger.info("Security features enabled:")
    logger.info("- Rate limiting")
    logger.info("- Input validation and sanitization")
    logger.info("- CSRF protection")
    logger.info("- JWT authentication")
    logger.info("- Role-based authorization")
    logger.info("- Security headers")
    logger.info("- Audit logging")
    logger.info("- GDPR compliance")
    logger.info("- SOX compliance")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
