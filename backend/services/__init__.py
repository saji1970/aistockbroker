#!/usr/bin/env python3
"""
Services Package for AI Stock Trading Platform
"""

from .auth_service import AuthService, auth_service
from .user_service import UserService, user_service

__all__ = [
    'AuthService',
    'auth_service',
    'UserService',
    'user_service'
]