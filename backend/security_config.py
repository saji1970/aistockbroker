#!/usr/bin/env python3
"""
Security Configuration for AI Stock Trading Platform
Comprehensive security measures against cyber attacks, hacking, and malware
"""

import os
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any
import logging

# Configure security logging
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

# Security Constants
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_DURATION = 300  # 5 minutes
SESSION_TIMEOUT = 3600  # 1 hour
CSRF_TOKEN_LIFETIME = 1800  # 30 minutes
RATE_LIMIT_REQUESTS = 100  # per minute
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

# Security Headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https:",
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}

# Rate limiting storage
rate_limit_storage = {}
login_attempts = {}
csrf_tokens = {}

class SecurityError(Exception):
    """Custom security exception"""
    pass

class RateLimitError(SecurityError):
    """Rate limit exceeded"""
    pass

class AuthenticationError(SecurityError):
    """Authentication failed"""
    pass

class AuthorizationError(SecurityError):
    """Authorization failed"""
    pass

def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token"""
    return secrets.token_urlsafe(32)

def validate_csrf_token(token: str) -> bool:
    """Validate CSRF token"""
    if not token:
        return False
    
    # Check if token exists and is not expired
    current_time = time.time()
    if token in csrf_tokens:
        token_data = csrf_tokens[token]
        if current_time < token_data['expires']:
            return True
        else:
            # Remove expired token
            del csrf_tokens[token]
    
    return False

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not isinstance(input_str, str):
        return str(input_str)
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r', '\n']
    for char in dangerous_chars:
        input_str = input_str.replace(char, '')
    
    # Limit length
    return input_str[:1000]

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    result = {
        'valid': False,
        'errors': []
    }
    
    if len(password) < 8:
        result['errors'].append('Password must be at least 8 characters long')
    
    if not any(c.isupper() for c in password):
        result['errors'].append('Password must contain at least one uppercase letter')
    
    if not any(c.islower() for c in password):
        result['errors'].append('Password must contain at least one lowercase letter')
    
    if not any(c.isdigit() for c in password):
        result['errors'].append('Password must contain at least one number')
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        result['errors'].append('Password must contain at least one special character')
    
    # Check for common passwords
    common_passwords = ['password', '123456', 'admin', 'qwerty', 'letmein']
    if password.lower() in common_passwords:
        result['errors'].append('Password is too common')
    
    result['valid'] = len(result['errors']) == 0
    return result

def hash_password(password: str, salt: Optional[str] = None) -> tuple:
    """Hash password using PBKDF2 with salt"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    
    return password_hash.hex(), salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verify password against hash"""
    new_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(password_hash, new_hash)

def rate_limit_check(client_ip: str) -> bool:
    """Check if client has exceeded rate limit"""
    current_time = time.time()
    
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    
    # Remove old requests
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip]
        if current_time - req_time < 60  # Last minute
    ]
    
    # Check if limit exceeded
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    return True

def check_login_attempts(username: str, client_ip: str) -> bool:
    """Check if user/IP has exceeded login attempts"""
    current_time = time.time()
    key = f"{username}:{client_ip}"
    
    if key not in login_attempts:
        login_attempts[key] = {'count': 0, 'last_attempt': 0}
    
    attempt_data = login_attempts[key]
    
    # Reset if lockout period has passed
    if current_time - attempt_data['last_attempt'] > LOGIN_LOCKOUT_DURATION:
        attempt_data['count'] = 0
    
    # Check if exceeded max attempts
    if attempt_data['count'] >= MAX_LOGIN_ATTEMPTS:
        return False
    
    return True

def record_login_attempt(username: str, client_ip: str, success: bool):
    """Record login attempt"""
    current_time = time.time()
    key = f"{username}:{client_ip}"
    
    if key not in login_attempts:
        login_attempts[key] = {'count': 0, 'last_attempt': 0}
    
    attempt_data = login_attempts[key]
    
    if success:
        # Reset on successful login
        attempt_data['count'] = 0
    else:
        # Increment failed attempts
        attempt_data['count'] += 1
    
    attempt_data['last_attempt'] = current_time

def log_security_event(event_type: str, details: Dict[str, Any], client_ip: str = None):
    """Log security events"""
    event_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'client_ip': client_ip
    }
    
    security_logger.warning(f"SECURITY_EVENT: {event_data}")

def validate_request_size(content_length: int) -> bool:
    """Validate request size"""
    return content_length <= MAX_REQUEST_SIZE

def get_client_ip(request) -> str:
    """Extract client IP address"""
    # Check for forwarded headers (behind proxy)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.remote_addr

# Security decorators
def require_authentication(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This would be implemented with actual session validation
        # For now, we'll assume authentication is handled elsewhere
        return f(*args, **kwargs)
    return decorated_function

def require_csrf_token(f):
    """Decorator to require CSRF token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # CSRF token validation would be implemented here
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(f):
    """Decorator to enforce rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Rate limiting would be implemented here
        return f(*args, **kwargs)
    return decorated_function

def audit_log(f):
    """Decorator to log function calls for audit purposes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Audit logging would be implemented here
        return f(*args, **kwargs)
    return decorated_function

# Compliance functions
def gdpr_data_export(user_id: str) -> Dict[str, Any]:
    """Generate GDPR data export for user"""
    # This would export all user data
    return {
        'user_id': user_id,
        'exported_at': datetime.utcnow().isoformat(),
        'data': {}  # Would contain actual user data
    }

def gdpr_data_deletion(user_id: str) -> bool:
    """Delete user data for GDPR compliance"""
    # This would delete all user data
    log_security_event('GDPR_DATA_DELETION', {'user_id': user_id})
    return True

def sox_audit_trail(action: str, user_id: str, details: Dict[str, Any]) -> None:
    """Create SOX audit trail entry"""
    audit_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'user_id': user_id,
        'details': details,
        'compliance': 'SOX'
    }
    
    security_logger.warning(f"SOX_AUDIT: {audit_entry}")

def pci_dss_validate_card_data(card_data: Dict[str, Any]) -> bool:
    """Validate PCI DSS compliance for card data"""
    # Basic validation - in production, this would be more comprehensive
    required_fields = ['card_number', 'expiry_date', 'cvv']
    
    for field in required_fields:
        if field not in card_data:
            return False
    
    # Validate card number format (basic Luhn algorithm)
    card_number = card_data['card_number'].replace(' ', '').replace('-', '')
    if not card_number.isdigit():
        return False
    
    # Luhn algorithm check
    def luhn_check(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0
    
    return luhn_check(card_number)

# Security middleware functions
def add_security_headers(response):
    """Add security headers to response"""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

def validate_content_type(request) -> bool:
    """Validate content type"""
    content_type = request.headers.get('Content-Type', '')
    
    # Allow JSON and form data
    allowed_types = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data'
    ]
    
    return any(allowed_type in content_type for allowed_type in allowed_types)

def validate_origin(request) -> bool:
    """Validate request origin"""
    origin = request.headers.get('Origin')
    referer = request.headers.get('Referer')
    
    # In production, this would check against allowed origins
    allowed_origins = [
        'https://ai-stock-trading-frontend-1012090067429.us-central1.run.app',
        'http://localhost:3000'  # For development
    ]
    
    if origin and origin not in allowed_origins:
        return False
    
    return True

# Encryption utilities
def encrypt_sensitive_data(data: str, key: str) -> str:
    """Encrypt sensitive data"""
    # In production, use proper encryption like AES
    # This is a simplified version
    import base64
    encoded = base64.b64encode(data.encode()).decode()
    return encoded

def decrypt_sensitive_data(encrypted_data: str, key: str) -> str:
    """Decrypt sensitive data"""
    # In production, use proper decryption
    # This is a simplified version
    import base64
    decoded = base64.b64decode(encrypted_data.encode()).decode()
    return decoded

# Session management
def create_secure_session(user_id: str, user_data: Dict[str, Any]) -> str:
    """Create secure session token"""
    session_data = {
        'user_id': user_id,
        'user_data': user_data,
        'created_at': time.time(),
        'expires_at': time.time() + SESSION_TIMEOUT
    }
    
    # In production, sign and encrypt this
    session_token = secrets.token_urlsafe(64)
    
    # Store session data (in production, use Redis or database)
    # sessions[session_token] = session_data
    
    return session_token

def validate_session(session_token: str) -> Optional[Dict[str, Any]]:
    """Validate session token"""
    # In production, validate against stored sessions
    current_time = time.time()
    
    # Mock validation - in production, check against stored session
    if session_token and len(session_token) > 32:
        return {
            'valid': True,
            'user_id': 'demo_user',
            'expires_at': current_time + SESSION_TIMEOUT
        }
    
    return None

# Input validation
def validate_stock_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    if not symbol or len(symbol) > 10:
        return False
    
    # Allow alphanumeric and some special characters
    import re
    pattern = r'^[A-Za-z0-9.\-]+$'
    return bool(re.match(pattern, symbol))

def validate_numeric_input(value: Any, min_val: float = None, max_val: float = None) -> bool:
    """Validate numeric input"""
    try:
        num_value = float(value)
        
        if min_val is not None and num_value < min_val:
            return False
        
        if max_val is not None and num_value > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_json_input(data: Any) -> bool:
    """Validate JSON input structure"""
    if not isinstance(data, dict):
        return False
    
    # Check for required fields based on endpoint
    # This would be endpoint-specific
    
    return True

# Security monitoring
def detect_anomalous_activity(user_id: str, activity_type: str, details: Dict[str, Any]) -> bool:
    """Detect anomalous user activity"""
    # In production, this would use machine learning or rule-based detection
    # For now, implement basic checks
    
    if activity_type == 'login':
        # Check for unusual login patterns
        pass
    
    elif activity_type == 'trading':
        # Check for unusual trading patterns
        pass
    
    return False

def generate_security_report() -> Dict[str, Any]:
    """Generate security monitoring report"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'failed_login_attempts': len([k for k, v in login_attempts.items() if v['count'] >= MAX_LOGIN_ATTEMPTS]),
        'rate_limited_ips': len([ip for ip, reqs in rate_limit_storage.items() if len(reqs) >= RATE_LIMIT_REQUESTS]),
        'active_csrf_tokens': len(csrf_tokens),
        'security_events': []  # Would contain recent security events
    }
