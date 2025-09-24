#!/usr/bin/env python3
"""
Authentication Service for AI Stock Trading Platform
Handles user authentication, registration, password reset, and session management
"""

import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import jwt
import re
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import User, UserSession, PasswordReset, AuditLog, UserRole, UserStatus, AuditAction
from database import db_manager

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class AuthService:
    def __init__(self):
        self.jwt_secret = os.environ.get('JWT_SECRET_KEY', self._generate_jwt_secret())
        self.jwt_algorithm = 'HS256'
        self.session_duration_hours = int(os.environ.get('SESSION_DURATION_HOURS', '24'))

        # Email configuration
        self.smtp_server = os.environ.get('SMTP_SERVER')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_username)

    def _generate_jwt_secret(self):
        """Generate a random JWT secret if not provided"""
        secret = secrets.token_urlsafe(32)
        logger.warning("JWT_SECRET_KEY not found in environment. Generated temporary secret. "
                      "Set JWT_SECRET_KEY environment variable for production.")
        return secret

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"

        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"

        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"

        return True, "Password is valid"

    def _log_audit_event(self, session: Session, action: AuditAction, user_id: Optional[int] = None,
                        success: bool = True, description: str = None,
                        metadata: Dict[str, Any] = None, **kwargs):
        """Log audit event"""
        try:
            audit_log = AuditLog(
                action=action,
                user_id=user_id,
                success=success,
                description=description,
                extra_data=str(metadata) if metadata else None,
                **kwargs
            )
            session.add(audit_log)
            session.flush()  # Ensure it's written to DB
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    def register_user(self, email: str, username: str, password: str,
                     first_name: str = None, last_name: str = None,
                     request_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a new user"""
        with db_manager.get_session() as session:
            try:
                # Validate input
                if not self._validate_email(email):
                    raise ValidationError("Invalid email format")

                is_valid, password_msg = self._validate_password(password)
                if not is_valid:
                    raise ValidationError(password_msg)

                if len(username) < 3:
                    raise ValidationError("Username must be at least 3 characters long")

                # Check if user already exists
                existing_user = session.query(User).filter(
                    (User.email == email.lower()) | (User.username == username)
                ).first()

                if existing_user:
                    error_msg = "Email already registered" if existing_user.email == email.lower() else "Username already taken"
                    self._log_audit_event(
                        session, AuditAction.SIGNUP, success=False,
                        description=f"Registration failed: {error_msg}",
                        ip_address=request_context.get('ip_address') if request_context else None
                    )
                    raise ValidationError(error_msg)

                # Create new user
                user = User(
                    email=email,
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    status=UserStatus.PENDING if self._email_verification_enabled() else UserStatus.ACTIVE
                )

                session.add(user)
                session.flush()  # Get the user ID

                # Log successful registration
                self._log_audit_event(
                    session, AuditAction.SIGNUP, user_id=user.id,
                    description="User registered successfully",
                    ip_address=request_context.get('ip_address') if request_context else None,
                    user_agent=request_context.get('user_agent') if request_context else None
                )

                # Send verification email if enabled
                if self._email_verification_enabled():
                    self._send_verification_email(user.email, user.username)

                return {
                    'success': True,
                    'message': 'User registered successfully. Please check your email for verification.'
                              if self._email_verification_enabled() else 'User registered successfully.',
                    'user': user.to_dict()
                }

            except (ValidationError, AuthenticationError) as e:
                raise e
            except IntegrityError:
                raise ValidationError("Email or username already exists")
            except Exception as e:
                logger.error(f"Registration error: {e}")
                raise AuthenticationError("Registration failed. Please try again.")

    def authenticate_user(self, email_or_username: str, password: str,
                         remember_me: bool = False,
                         request_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Authenticate user and create session"""
        with db_manager.get_session() as session:
            try:
                # Find user by email or username
                user = session.query(User).filter(
                    (User.email == email_or_username.lower()) |
                    (User.username == email_or_username)
                ).first()

                if not user or not user.check_password(password):
                    self._log_audit_event(
                        session, AuditAction.LOGIN_FAILED,
                        description=f"Failed login attempt for: {email_or_username}",
                        ip_address=request_context.get('ip_address') if request_context else None,
                        success=False
                    )
                    raise AuthenticationError("Invalid email/username or password")

                if user.status != UserStatus.ACTIVE:
                    status_messages = {
                        UserStatus.PENDING: "Please verify your email address",
                        UserStatus.SUSPENDED: "Your account has been suspended",
                        UserStatus.INACTIVE: "Your account is inactive"
                    }
                    self._log_audit_event(
                        session, AuditAction.LOGIN_FAILED, user_id=user.id,
                        description=f"Login failed - account status: {user.status.value}",
                        ip_address=request_context.get('ip_address') if request_context else None,
                        success=False
                    )
                    raise AuthenticationError(status_messages.get(user.status, "Account access denied"))

                # Update last login
                user.last_login = datetime.utcnow()

                # Create session
                user_session = UserSession(
                    user_id=user.id,
                    session_duration_hours=self.session_duration_hours,
                    remember_me=remember_me,
                    ip_address=request_context.get('ip_address') if request_context else None,
                    user_agent=request_context.get('user_agent') if request_context else None
                )

                session.add(user_session)

                # Log successful login
                self._log_audit_event(
                    session, AuditAction.LOGIN, user_id=user.id,
                    description="User logged in successfully",
                    ip_address=request_context.get('ip_address') if request_context else None,
                    user_agent=request_context.get('user_agent') if request_context else None
                )

                # Generate JWT token
                token = self._generate_jwt_token(user.id, user_session.session_token)

                return {
                    'success': True,
                    'message': 'Login successful',
                    'token': token,
                    'refresh_token': user_session.refresh_token,
                    'user': user.to_dict(),
                    'expires_at': user_session.expires_at.isoformat()
                }

            except (ValidationError, AuthenticationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Authentication error: {e}")
                raise AuthenticationError("Authentication failed. Please try again.")

    def logout_user(self, session_token: str, logout_all: bool = False,
                   request_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Logout user and revoke session(s)"""
        with db_manager.get_session() as session:
            try:
                # Find the session
                user_session = session.query(UserSession).filter(
                    UserSession.session_token == session_token,
                    UserSession.is_active == True
                ).first()

                if not user_session:
                    raise AuthenticationError("Invalid session")

                user = session.query(User).get(user_session.user_id)

                if logout_all:
                    # Revoke all user sessions
                    session.query(UserSession).filter(
                        UserSession.user_id == user_session.user_id,
                        UserSession.is_active == True
                    ).update({'is_active': False})
                else:
                    # Revoke only this session
                    user_session.revoke()

                # Log logout
                self._log_audit_event(
                    session, AuditAction.LOGOUT, user_id=user.id if user else None,
                    description="User logged out" + (" (all sessions)" if logout_all else ""),
                    ip_address=request_context.get('ip_address') if request_context else None
                )

                return {
                    'success': True,
                    'message': 'Logout successful'
                }

            except AuthenticationError as e:
                raise e
            except Exception as e:
                logger.error(f"Logout error: {e}")
                raise AuthenticationError("Logout failed. Please try again.")

    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """Verify and refresh session if valid"""
        with db_manager.get_session() as session:
            try:
                # Find active session
                user_session = session.query(UserSession).filter(
                    UserSession.session_token == session_token,
                    UserSession.is_active == True
                ).first()

                if not user_session or not user_session.is_valid():
                    raise AuthenticationError("Invalid or expired session")

                # Get user
                user = session.query(User).get(user_session.user_id)
                if not user or not user.is_active():
                    raise AuthenticationError("User account is not active")

                # Refresh session if close to expiry (within 1 hour)
                time_until_expiry = user_session.expires_at - datetime.utcnow()
                if time_until_expiry.total_seconds() < 3600:  # Less than 1 hour
                    user_session.refresh(self.session_duration_hours)

                user_session.last_accessed = datetime.utcnow()

                return {
                    'success': True,
                    'user': user.to_dict(),
                    'session_valid': True,
                    'expires_at': user_session.expires_at.isoformat()
                }

            except AuthenticationError as e:
                raise e
            except Exception as e:
                logger.error(f"Session verification error: {e}")
                raise AuthenticationError("Session verification failed")

    def request_password_reset(self, email: str,
                             request_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Request password reset"""
        with db_manager.get_session() as session:
            try:
                # Find user
                user = session.query(User).filter(User.email == email.lower()).first()

                if not user:
                    # Don't reveal if email exists or not
                    return {
                        'success': True,
                        'message': 'If the email address exists, a password reset link has been sent.'
                    }

                # Create password reset token
                password_reset = PasswordReset(
                    user_id=user.id,
                    ip_address=request_context.get('ip_address') if request_context else None
                )

                session.add(password_reset)

                # Send reset email
                self._send_password_reset_email(user.email, user.username, password_reset.reset_token)

                # Log password reset request
                self._log_audit_event(
                    session, AuditAction.PASSWORD_RESET, user_id=user.id,
                    description="Password reset requested",
                    ip_address=request_context.get('ip_address') if request_context else None
                )

                return {
                    'success': True,
                    'message': 'Password reset link has been sent to your email.'
                }

            except Exception as e:
                logger.error(f"Password reset request error: {e}")
                return {
                    'success': True,
                    'message': 'If the email address exists, a password reset link has been sent.'
                }

    def reset_password(self, reset_token: str, new_password: str,
                      request_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Reset password using reset token"""
        with db_manager.get_session() as session:
            try:
                # Validate new password
                is_valid, password_msg = self._validate_password(new_password)
                if not is_valid:
                    raise ValidationError(password_msg)

                # Find valid reset token
                password_reset = session.query(PasswordReset).filter(
                    PasswordReset.reset_token == reset_token
                ).first()

                if not password_reset or not password_reset.is_valid():
                    raise AuthenticationError("Invalid or expired reset token")

                # Get user and update password
                user = session.query(User).get(password_reset.user_id)
                if not user:
                    raise AuthenticationError("User not found")

                user.set_password(new_password)
                password_reset.use()

                # Revoke all user sessions for security
                session.query(UserSession).filter(
                    UserSession.user_id == user.id,
                    UserSession.is_active == True
                ).update({'is_active': False})

                # Log password change
                self._log_audit_event(
                    session, AuditAction.PASSWORD_CHANGE, user_id=user.id,
                    description="Password reset completed",
                    ip_address=request_context.get('ip_address') if request_context else None
                )

                return {
                    'success': True,
                    'message': 'Password has been reset successfully. Please log in with your new password.'
                }

            except (ValidationError, AuthenticationError) as e:
                raise e
            except Exception as e:
                logger.error(f"Password reset error: {e}")
                raise AuthenticationError("Password reset failed. Please try again.")

    def _generate_jwt_token(self, user_id: int, session_token: str) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'session_token': session_token,
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=self.session_duration_hours)).isoformat()
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def decode_jwt_token(self, token: str) -> Dict[str, Any]:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

    def _email_verification_enabled(self) -> bool:
        """Check if email verification is enabled"""
        return bool(self.smtp_server and self.smtp_username and self.smtp_password)

    def _send_verification_email(self, email: str, username: str):
        """Send email verification (placeholder implementation)"""
        if not self._email_verification_enabled():
            return

        try:
            # This is a basic implementation - you should customize the email template
            subject = "Verify Your AI Stock Trading Account"
            body = f"""
            Hi {username},

            Welcome to AI Stock Trading Platform! Please click the link below to verify your email address:

            [Verification Link - Implement in frontend]

            If you didn't create this account, please ignore this email.

            Best regards,
            AI Stock Trading Team
            """

            self._send_email(email, subject, body)
            logger.info(f"Verification email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")

    def _send_password_reset_email(self, email: str, username: str, reset_token: str):
        """Send password reset email"""
        if not self._email_verification_enabled():
            return

        try:
            subject = "Password Reset - AI Stock Trading"
            body = f"""
            Hi {username},

            You requested a password reset for your AI Stock Trading account. Click the link below to reset your password:

            [Reset Link: /reset-password?token={reset_token} - Implement in frontend]

            This link will expire in 1 hour. If you didn't request this reset, please ignore this email.

            Best regards,
            AI Stock Trading Team
            """

            self._send_email(email, subject, body)
            logger.info(f"Password reset email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")

    def _send_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP"""
        if not self._email_verification_enabled():
            logger.warning("Email sending is not configured")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise

# Global auth service instance
auth_service = AuthService()