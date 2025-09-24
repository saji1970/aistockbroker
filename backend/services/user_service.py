#!/usr/bin/env python3
"""
User Management Service for AI Stock Trading Platform
Handles user profiles, CRUD operations, and admin functionality
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models import User, AuditLog, UserRole, UserStatus, AuditAction
from database import db_manager

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        pass

    def _log_audit_event(self, session: Session, action: AuditAction, user_id: Optional[int] = None,
                        admin_user_id: Optional[int] = None, success: bool = True,
                        description: str = None, metadata: Dict[str, Any] = None, **kwargs):
        """Log audit event"""
        try:
            audit_log = AuditLog(
                action=action,
                user_id=admin_user_id or user_id,  # Who performed the action
                success=success,
                description=description,
                extra_data=str(metadata) if metadata else None,
                **kwargs
            )
            session.add(audit_log)
            session.flush()
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with db_manager.get_session() as session:
            try:
                user = session.query(User).get(user_id)
                if user:
                    return user.to_dict()
                return None
            except Exception as e:
                logger.error(f"Error getting user by ID {user_id}: {e}")
                return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        with db_manager.get_session() as session:
            try:
                user = session.query(User).filter(User.email == email.lower()).first()
                if user:
                    return user.to_dict()
                return None
            except Exception as e:
                logger.error(f"Error getting user by email {email}: {e}")
                return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with db_manager.get_session() as session:
            try:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    return user.to_dict()
                return None
            except Exception as e:
                logger.error(f"Error getting user by username {username}: {e}")
                return None

    def update_user_profile(self, user_id: int, update_data: Dict[str, Any],
                          admin_user_id: Optional[int] = None) -> Dict[str, Any]:
        """Update user profile"""
        with db_manager.get_session() as session:
            try:
                user = session.query(User).get(user_id)
                if not user:
                    return {'success': False, 'message': 'User not found'}

                # Fields that can be updated
                updatable_fields = [
                    'first_name', 'last_name', 'trading_experience',
                    'risk_tolerance', 'investment_goals', 'preferred_sectors',
                    'initial_capital'
                ]

                # Admin can update additional fields
                if admin_user_id:
                    admin = session.query(User).get(admin_user_id)
                    if admin and admin.is_admin():
                        updatable_fields.extend(['email', 'username', 'role', 'status'])

                # Track changes for audit
                changes = {}
                for field, value in update_data.items():
                    if field in updatable_fields and hasattr(user, field):
                        old_value = getattr(user, field)
                        if old_value != value:
                            changes[field] = {'old': old_value, 'new': value}
                            setattr(user, field, value)

                if not changes:
                    return {'success': True, 'message': 'No changes made', 'user': user.to_dict()}

                user.updated_at = datetime.utcnow()

                # Log the update
                self._log_audit_event(
                    session, AuditAction.PROFILE_UPDATE,
                    user_id=user_id, admin_user_id=admin_user_id,
                    description=f"Profile updated: {list(changes.keys())}",
                    metadata={'changes': changes}
                )

                return {
                    'success': True,
                    'message': 'Profile updated successfully',
                    'user': user.to_dict(),
                    'changes': changes
                }

            except Exception as e:
                logger.error(f"Error updating user profile: {e}")
                return {'success': False, 'message': 'Failed to update profile'}

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        with db_manager.get_session() as session:
            try:
                user = session.query(User).get(user_id)
                if not user:
                    return {'success': False, 'message': 'User not found'}

                # Verify current password
                if not user.check_password(current_password):
                    self._log_audit_event(
                        session, AuditAction.PASSWORD_CHANGE, user_id=user_id,
                        success=False, description="Failed password change - incorrect current password"
                    )
                    return {'success': False, 'message': 'Current password is incorrect'}

                # Validate new password (reuse validation from auth_service)
                from services.auth_service import auth_service
                is_valid, password_msg = auth_service._validate_password(new_password)
                if not is_valid:
                    return {'success': False, 'message': password_msg}

                # Update password
                user.set_password(new_password)
                user.updated_at = datetime.utcnow()

                # Revoke all sessions except current one for security
                from models import UserSession
                session.query(UserSession).filter(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True
                ).update({'is_active': False})

                # Log password change
                self._log_audit_event(
                    session, AuditAction.PASSWORD_CHANGE, user_id=user_id,
                    description="Password changed successfully"
                )

                return {'success': True, 'message': 'Password changed successfully'}

            except Exception as e:
                logger.error(f"Error changing password: {e}")
                return {'success': False, 'message': 'Failed to change password'}

    def get_users_list(self, admin_user_id: int, page: int = 1, per_page: int = 20,
                      search: str = None, role_filter: str = None,
                      status_filter: str = None) -> Dict[str, Any]:
        """Get paginated list of users (admin only)"""
        with db_manager.get_session() as session:
            try:
                # Verify admin privileges
                admin = session.query(User).get(admin_user_id)
                if not admin or not admin.is_admin():
                    return {'success': False, 'message': 'Admin privileges required'}

                # Build query
                query = session.query(User)

                # Apply filters
                if search:
                    search_filter = or_(
                        User.email.ilike(f'%{search}%'),
                        User.username.ilike(f'%{search}%'),
                        User.first_name.ilike(f'%{search}%'),
                        User.last_name.ilike(f'%{search}%')
                    )
                    query = query.filter(search_filter)

                if role_filter:
                    try:
                        role = UserRole(role_filter)
                        query = query.filter(User.role == role)
                    except ValueError:
                        pass  # Invalid role, ignore filter

                if status_filter:
                    try:
                        status = UserStatus(status_filter)
                        query = query.filter(User.status == status)
                    except ValueError:
                        pass  # Invalid status, ignore filter

                # Get total count
                total_count = query.count()

                # Apply pagination
                offset = (page - 1) * per_page
                users = query.offset(offset).limit(per_page).all()

                # Convert to dict
                users_data = [user.to_dict() for user in users]

                return {
                    'success': True,
                    'users': users_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total_count,
                        'total_pages': (total_count + per_page - 1) // per_page
                    }
                }

            except Exception as e:
                logger.error(f"Error getting users list: {e}")
                return {'success': False, 'message': 'Failed to get users list'}

    def update_user_role(self, admin_user_id: int, target_user_id: int, new_role: str) -> Dict[str, Any]:
        """Update user role (admin only)"""
        with db_manager.get_session() as session:
            try:
                # Verify admin privileges
                admin = session.query(User).get(admin_user_id)
                if not admin or not admin.is_admin():
                    return {'success': False, 'message': 'Admin privileges required'}

                # Get target user
                user = session.query(User).get(target_user_id)
                if not user:
                    return {'success': False, 'message': 'User not found'}

                # Validate new role
                try:
                    role = UserRole(new_role)
                except ValueError:
                    return {'success': False, 'message': 'Invalid role'}

                # Prevent self-demotion
                if admin_user_id == target_user_id and role != UserRole.ADMIN:
                    return {'success': False, 'message': 'Cannot change your own admin role'}

                old_role = user.role
                user.role = role
                user.updated_at = datetime.utcnow()

                # Log role change
                self._log_audit_event(
                    session, AuditAction.ROLE_CHANGE,
                    user_id=target_user_id, admin_user_id=admin_user_id,
                    description=f"Role changed from {old_role.value} to {role.value}",
                    metadata={'old_role': old_role.value, 'new_role': role.value}
                )

                return {
                    'success': True,
                    'message': 'User role updated successfully',
                    'user': user.to_dict()
                }

            except Exception as e:
                logger.error(f"Error updating user role: {e}")
                return {'success': False, 'message': 'Failed to update user role'}

    def update_user_status(self, admin_user_id: int, target_user_id: int, new_status: str) -> Dict[str, Any]:
        """Update user status (admin only)"""
        with db_manager.get_session() as session:
            try:
                # Verify admin privileges
                admin = session.query(User).get(admin_user_id)
                if not admin or not admin.is_admin():
                    return {'success': False, 'message': 'Admin privileges required'}

                # Get target user
                user = session.query(User).get(target_user_id)
                if not user:
                    return {'success': False, 'message': 'User not found'}

                # Validate new status
                try:
                    status = UserStatus(new_status)
                except ValueError:
                    return {'success': False, 'message': 'Invalid status'}

                # Prevent self-suspension
                if admin_user_id == target_user_id and status == UserStatus.SUSPENDED:
                    return {'success': False, 'message': 'Cannot suspend your own account'}

                old_status = user.status
                user.status = status
                user.updated_at = datetime.utcnow()

                # Revoke sessions if suspended
                if status == UserStatus.SUSPENDED:
                    from models import UserSession
                    session.query(UserSession).filter(
                        UserSession.user_id == target_user_id,
                        UserSession.is_active == True
                    ).update({'is_active': False})

                # Log status change
                action = AuditAction.ACCOUNT_SUSPEND if status == UserStatus.SUSPENDED else AuditAction.ACCOUNT_ACTIVATE
                self._log_audit_event(
                    session, action,
                    user_id=target_user_id, admin_user_id=admin_user_id,
                    description=f"Status changed from {old_status.value} to {status.value}",
                    metadata={'old_status': old_status.value, 'new_status': status.value}
                )

                return {
                    'success': True,
                    'message': 'User status updated successfully',
                    'user': user.to_dict()
                }

            except Exception as e:
                logger.error(f"Error updating user status: {e}")
                return {'success': False, 'message': 'Failed to update user status'}

    def delete_user(self, admin_user_id: int, target_user_id: int) -> Dict[str, Any]:
        """Delete user (admin only)"""
        with db_manager.get_session() as session:
            try:
                # Verify admin privileges
                admin = session.query(User).get(admin_user_id)
                if not admin or not admin.is_admin():
                    return {'success': False, 'message': 'Admin privileges required'}

                # Get target user
                user = session.query(User).get(target_user_id)
                if not user:
                    return {'success': False, 'message': 'User not found'}

                # Prevent self-deletion
                if admin_user_id == target_user_id:
                    return {'success': False, 'message': 'Cannot delete your own account'}

                username = user.username
                email = user.email

                # Delete user (cascades will handle related records)
                session.delete(user)

                # Log deletion
                self._log_audit_event(
                    session, AuditAction.ACCOUNT_SUSPEND,  # Using SUSPEND as closest action
                    admin_user_id=admin_user_id,
                    description=f"User account deleted: {username} ({email})",
                    metadata={'deleted_user_id': target_user_id, 'username': username, 'email': email}
                )

                return {
                    'success': True,
                    'message': 'User deleted successfully'
                }

            except Exception as e:
                logger.error(f"Error deleting user: {e}")
                return {'success': False, 'message': 'Failed to delete user'}

    def get_user_audit_logs(self, admin_user_id: int, target_user_id: int,
                           page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """Get user audit logs (admin only)"""
        with db_manager.get_session() as session:
            try:
                # Verify admin privileges
                admin = session.query(User).get(admin_user_id)
                if not admin or not admin.is_admin():
                    return {'success': False, 'message': 'Admin privileges required'}

                # Get logs for user
                query = session.query(AuditLog).filter(AuditLog.user_id == target_user_id)
                query = query.order_by(AuditLog.created_at.desc())

                # Get total count
                total_count = query.count()

                # Apply pagination
                offset = (page - 1) * per_page
                logs = query.offset(offset).limit(per_page).all()

                # Convert to dict
                logs_data = [log.to_dict() for log in logs]

                return {
                    'success': True,
                    'logs': logs_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total_count,
                        'total_pages': (total_count + per_page - 1) // per_page
                    }
                }

            except Exception as e:
                logger.error(f"Error getting user audit logs: {e}")
                return {'success': False, 'message': 'Failed to get audit logs'}

    def get_dashboard_stats(self, admin_user_id: int) -> Dict[str, Any]:
        """Get dashboard statistics (admin only)"""
        with db_manager.get_session() as session:
            try:
                # Verify admin privileges
                admin = session.query(User).get(admin_user_id)
                if not admin or not admin.is_admin():
                    return {'success': False, 'message': 'Admin privileges required'}

                # Get user counts by status
                status_counts = {}
                for status in UserStatus:
                    count = session.query(User).filter(User.status == status).count()
                    status_counts[status.value] = count

                # Get user counts by role
                role_counts = {}
                for role in UserRole:
                    count = session.query(User).filter(User.role == role).count()
                    role_counts[role.value] = count

                # Get total users
                total_users = session.query(User).count()

                # Get recent registrations (last 30 days)
                from datetime import timedelta
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                recent_registrations = session.query(User).filter(
                    User.created_at >= thirty_days_ago
                ).count()

                # Get recent login activity
                recent_logins = session.query(AuditLog).filter(
                    and_(
                        AuditLog.action == AuditAction.LOGIN,
                        AuditLog.created_at >= thirty_days_ago
                    )
                ).count()

                return {
                    'success': True,
                    'stats': {
                        'total_users': total_users,
                        'status_breakdown': status_counts,
                        'role_breakdown': role_counts,
                        'recent_registrations': recent_registrations,
                        'recent_logins': recent_logins
                    }
                }

            except Exception as e:
                logger.error(f"Error getting dashboard stats: {e}")
                return {'success': False, 'message': 'Failed to get dashboard statistics'}

# Global user service instance
user_service = UserService()