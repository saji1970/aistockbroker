#!/usr/bin/env python3
"""
User Management Models for AI Stock Trading Platform
Defines database models for users, roles, sessions, and audit logs
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import bcrypt
import secrets
from enum import Enum as PyEnum

Base = declarative_base()

class UserRole(PyEnum):
    ADMIN = "admin"
    AGENT = "agent"
    USER = "user"
    CUSTOMER = "customer"
    GUEST = "guest"

class UserStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class AuditAction(PyEnum):
    LOGIN = "login"
    LOGOUT = "logout"
    SIGNUP = "signup"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    PROFILE_UPDATE = "profile_update"
    ROLE_CHANGE = "role_change"
    ACCOUNT_SUSPEND = "account_suspend"
    ACCOUNT_ACTIVATE = "account_activate"
    LOGIN_FAILED = "login_failed"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)

    # Profile preferences
    trading_experience = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    risk_tolerance = Column(String(50), nullable=True)      # low, medium, high
    investment_goals = Column(Text, nullable=True)
    preferred_sectors = Column(Text, nullable=True)         # JSON string
    initial_capital = Column(Float, default=0.0)

    # Agent relationships
    assigned_agent_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # For customers
    agent_commission_rate = Column(Float, default=0.02)  # 2% default commission

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)

    # OAuth integration
    google_id = Column(String(255), nullable=True, unique=True)
    github_id = Column(String(255), nullable=True, unique=True)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")

    # Agent-Customer relationships
    assigned_agent = relationship("User", remote_side=[id], backref="customers")

    def __init__(self, email, username, password=None, **kwargs):
        self.email = email.lower()
        self.username = username
        if password:
            self.set_password(password)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_password(self, password):
        """Hash and set the user's password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the user's password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def is_admin(self):
        """Check if the user has admin role"""
        return self.role == UserRole.ADMIN

    def is_active(self):
        """Check if the user account is active"""
        return self.status == UserStatus.ACTIVE

    def can_access_trading(self):
        """Check if user can access trading features"""
        return self.is_active() and self.role in [UserRole.USER, UserRole.ADMIN, UserRole.AGENT, UserRole.CUSTOMER]

    def is_agent(self):
        """Check if the user is an agent"""
        return self.role == UserRole.AGENT

    def is_customer(self):
        """Check if the user is a customer"""
        return self.role == UserRole.CUSTOMER

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'status': self.status.value,
            'trading_experience': self.trading_experience,
            'risk_tolerance': self.risk_tolerance,
            'investment_goals': self.investment_goals,
            'preferred_sectors': self.preferred_sectors,
            'initial_capital': self.initial_capital,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'email_verified_at': self.email_verified_at.isoformat() if self.email_verified_at else None,
            'google_id': self.google_id,
            'github_id': self.github_id,
            'assigned_agent_id': self.assigned_agent_id,
            'agent_commission_rate': self.agent_commission_rate
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Session management
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Security flags
    is_remembered = Column(Boolean, default=False)
    logout_all_sessions = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __init__(self, user_id, session_duration_hours=24, remember_me=False, **kwargs):
        self.user_id = user_id
        self.session_token = self._generate_token()
        self.refresh_token = self._generate_token()
        self.is_remembered = remember_me

        # Set expiration time
        duration = timedelta(hours=session_duration_hours)
        if remember_me:
            duration = timedelta(days=30)  # 30 days for remembered sessions
        self.expires_at = datetime.utcnow() + duration

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @staticmethod
    def _generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)

    def is_expired(self):
        """Check if the session is expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if the session is valid (active and not expired)"""
        return self.is_active and not self.is_expired()

    def refresh(self, session_duration_hours=24):
        """Refresh the session with new expiration time"""
        if self.is_remembered:
            duration = timedelta(days=30)
        else:
            duration = timedelta(hours=session_duration_hours)
        self.expires_at = datetime.utcnow() + duration
        self.last_accessed = datetime.utcnow()

    def revoke(self):
        """Revoke the session"""
        self.is_active = False

class PasswordReset(Base):
    __tablename__ = 'password_resets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reset_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)

    # Reset management
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    is_used = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="password_resets")

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.reset_token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiration

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def is_expired(self):
        """Check if the reset token is expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self):
        """Check if the reset token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()

    def use(self):
        """Mark the reset token as used"""
        self.is_used = True
        self.used_at = datetime.utcnow()

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable for system actions
    action = Column(Enum(AuditAction), nullable=False)
    description = Column(Text, nullable=True)

    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    request_method = Column(String(10), nullable=True)

    # Additional data
    extra_data = Column(Text, nullable=True)  # JSON string for additional context
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __init__(self, action, user_id=None, **kwargs):
        self.action = action
        self.user_id = user_id

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        """Convert audit log to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action.value,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'request_method': self.request_method,
            'extra_data': self.extra_data,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }