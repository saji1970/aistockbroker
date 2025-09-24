#!/usr/bin/env python3
"""
Trading Authentication Middleware
Handles trading access authentication and authorization
"""

import os
import json
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime

class TradingAuthMiddleware:
    """Middleware for trading access authentication"""
    
    def __init__(self):
        self.access_tokens = self._load_access_tokens()
        self.trading_config = self._load_trading_config()
    
    def _load_access_tokens(self):
        """Load access tokens from file"""
        try:
            with open('access_tokens.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "admin_token": "admin_access_token_123",
                "trader_token": "trader_access_token_456",
                "customer_token": "customer_access_token_789"
            }
    
    def _load_trading_config(self):
        """Load trading configuration"""
        try:
            with open('trading_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "trading_enabled": True,
                "demo_mode": True,
                "access_level": "full"
            }
    
    def check_trading_access(self, required_level="basic"):
        """Check if user has trading access"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Check if trading is enabled
                if not self.trading_config.get("trading_enabled", True):
                    return jsonify({
                        "error": "Trading Access Denied",
                        "message": "Trading features are currently disabled",
                        "status": "disabled"
                    }), 403
                
                # Get access token from request
                access_token = request.headers.get('X-Access-Token') or \
                             request.args.get('access_token') or \
                             request.json.get('access_token') if request.is_json else None
                
                # Check for demo mode (allow access without token)
                if self.trading_config.get("demo_mode", True):
                    g.trading_access = {
                        "level": "demo",
                        "user_type": "demo_user",
                        "permissions": ["read", "trade", "analyze"]
                    }
                    return f(*args, **kwargs)
                
                # Validate access token
                if not access_token:
                    return jsonify({
                        "error": "Trading Access Denied",
                        "message": "Access token required for trading features",
                        "status": "unauthorized"
                    }), 401
                
                # Check token validity
                user_type = None
                for token_type, token_value in self.access_tokens.items():
                    if access_token == token_value:
                        user_type = token_type.replace("_token", "")
                        break
                
                if not user_type:
                    return jsonify({
                        "error": "Trading Access Denied", 
                        "message": "Invalid access token",
                        "status": "invalid_token"
                    }), 401
                
                # Set trading access level
                if user_type == "admin":
                    g.trading_access = {
                        "level": "admin",
                        "user_type": "admin",
                        "permissions": ["read", "trade", "analyze", "manage", "admin"]
                    }
                elif user_type == "trader":
                    g.trading_access = {
                        "level": "trader",
                        "user_type": "trader", 
                        "permissions": ["read", "trade", "analyze", "manage"]
                    }
                elif user_type == "customer":
                    g.trading_access = {
                        "level": "customer",
                        "user_type": "customer",
                        "permissions": ["read", "trade", "analyze"]
                    }
                else:
                    g.trading_access = {
                        "level": "basic",
                        "user_type": "user",
                        "permissions": ["read", "analyze"]
                    }
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def require_trading_permission(self, permission):
        """Require specific trading permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'trading_access'):
                    return jsonify({
                        "error": "Trading Access Denied",
                        "message": "No trading access configured",
                        "status": "no_access"
                    }), 403
                
                if permission not in g.trading_access.get("permissions", []):
                    return jsonify({
                        "error": "Trading Access Denied",
                        "message": f"Insufficient permissions. Required: {permission}",
                        "status": "insufficient_permissions"
                    }), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

# Create global instance
trading_auth = TradingAuthMiddleware()

# Convenience decorators
def trading_access_required(level="basic"):
    """Require trading access"""
    return trading_auth.check_trading_access(level)

def require_trade_permission():
    """Require trade permission"""
    return trading_auth.require_trading_permission("trade")

def require_manage_permission():
    """Require manage permission"""
    return trading_auth.require_trading_permission("manage")

def require_admin_permission():
    """Require admin permission"""
    return trading_auth.require_trading_permission("admin")
