#!/usr/bin/env python3
"""
User Management API Routes for AI Stock Trading Platform
"""

from flask import Blueprint, request, jsonify, g
import logging

from middleware import (
    require_auth, require_admin, validate_json, log_api_access,
    security_headers, get_request_context
)
from services.user_service import user_service

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/profile', methods=['GET'])
@log_api_access
@security_headers
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        return jsonify({
            'success': True,
            'user': g.current_user
        }), 200

    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get profile',
            'message': 'An error occurred while fetching profile'
        }), 500

@user_bp.route('/profile', methods=['PUT'])
@log_api_access
@security_headers
@require_auth
@validate_json()
def update_profile():
    """Update user profile"""
    try:
        data = g.json_data
        user_id = g.current_user['id']

        result = user_service.update_user_profile(
            user_id=user_id,
            update_data=data
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update profile',
            'message': 'An error occurred while updating profile'
        }), 500

@user_bp.route('/change-password', methods=['POST'])
@log_api_access
@security_headers
@require_auth
@validate_json(required_fields=['current_password', 'new_password'])
def change_password():
    """Change user password"""
    try:
        data = g.json_data
        user_id = g.current_user['id']

        result = user_service.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Change password error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to change password',
            'message': 'An error occurred while changing password'
        }), 500

# Admin routes
@user_bp.route('', methods=['GET'])
@log_api_access
@security_headers
@require_admin
def list_users():
    """List all users (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Max 100 per page
        search = request.args.get('search')
        role_filter = request.args.get('role')
        status_filter = request.args.get('status')

        admin_user_id = g.current_user['id']

        result = user_service.get_users_list(
            admin_user_id=admin_user_id,
            page=page,
            per_page=per_page,
            search=search,
            role_filter=role_filter,
            status_filter=status_filter
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 403

    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid parameters',
            'message': 'Page and per_page must be valid integers'
        }), 400

    except Exception as e:
        logger.error(f"List users error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list users',
            'message': 'An error occurred while listing users'
        }), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
@log_api_access
@security_headers
@require_admin
def get_user(user_id):
    """Get user by ID (admin only)"""
    try:
        user = user_service.get_user_by_id(user_id)

        if user:
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'message': f'User with ID {user_id} not found'
            }), 404

    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user',
            'message': 'An error occurred while fetching user'
        }), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@log_api_access
@security_headers
@require_admin
@validate_json()
def update_user(user_id):
    """Update user (admin only)"""
    try:
        data = g.json_data
        admin_user_id = g.current_user['id']

        result = user_service.update_user_profile(
            user_id=user_id,
            update_data=data,
            admin_user_id=admin_user_id
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Update user error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update user',
            'message': 'An error occurred while updating user'
        }), 500

@user_bp.route('/<int:user_id>/role', methods=['PUT'])
@log_api_access
@security_headers
@require_admin
@validate_json(required_fields=['role'])
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        data = g.json_data
        admin_user_id = g.current_user['id']

        result = user_service.update_user_role(
            admin_user_id=admin_user_id,
            target_user_id=user_id,
            new_role=data['role']
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Update user role error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update user role',
            'message': 'An error occurred while updating user role'
        }), 500

@user_bp.route('/<int:user_id>/status', methods=['PUT'])
@log_api_access
@security_headers
@require_admin
@validate_json(required_fields=['status'])
def update_user_status(user_id):
    """Update user status (admin only)"""
    try:
        data = g.json_data
        admin_user_id = g.current_user['id']

        result = user_service.update_user_status(
            admin_user_id=admin_user_id,
            target_user_id=user_id,
            new_status=data['status']
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Update user status error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update user status',
            'message': 'An error occurred while updating user status'
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@log_api_access
@security_headers
@require_admin
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        admin_user_id = g.current_user['id']

        result = user_service.delete_user(
            admin_user_id=admin_user_id,
            target_user_id=user_id
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Delete user error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete user',
            'message': 'An error occurred while deleting user'
        }), 500

@user_bp.route('/<int:user_id>/audit-logs', methods=['GET'])
@log_api_access
@security_headers
@require_admin
def get_user_audit_logs(user_id):
    """Get user audit logs (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 per page

        admin_user_id = g.current_user['id']

        result = user_service.get_user_audit_logs(
            admin_user_id=admin_user_id,
            target_user_id=user_id,
            page=page,
            per_page=per_page
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 403

    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid parameters',
            'message': 'Page and per_page must be valid integers'
        }), 400

    except Exception as e:
        logger.error(f"Get user audit logs error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get audit logs',
            'message': 'An error occurred while fetching audit logs'
        }), 500

@user_bp.route('/dashboard/stats', methods=['GET'])
@log_api_access
@security_headers
@require_admin
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        admin_user_id = g.current_user['id']

        result = user_service.get_dashboard_stats(admin_user_id)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 403

    except Exception as e:
        logger.error(f"Get dashboard stats error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get dashboard statistics',
            'message': 'An error occurred while fetching dashboard statistics'
        }), 500