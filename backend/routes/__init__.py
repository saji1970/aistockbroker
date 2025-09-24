#!/usr/bin/env python3
"""
API Routes Package for AI Stock Trading Platform
"""

from .auth_routes import auth_bp
from .user_routes import user_bp

__all__ = [
    'auth_bp',
    'user_bp'
]