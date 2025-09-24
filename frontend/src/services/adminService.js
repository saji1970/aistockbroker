/**
 * Admin Service for AI Stock Trading Frontend
 * Handles admin-specific operations and user management
 */

import axios from 'axios';
import { API_BASE_URL } from './config';

const API_BASE = API_BASE_URL + '/api';

class AdminService {
  /**
   * Get list of users with pagination and filters
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Users list result
   */
  async getUsers(params = {}) {
    try {
      const response = await axios.get(`${API_BASE}/users`, { params });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch users'
      };
    }
  }

  /**
   * Get user by ID
   * @param {number} userId - User ID
   * @returns {Promise<Object>} User data result
   */
  async getUserById(userId) {
    try {
      const response = await axios.get(`${API_BASE}/users/${userId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch user'
      };
    }
  }

  /**
   * Update user information
   * @param {number} userId - User ID
   * @param {Object} userData - User data to update
   * @returns {Promise<Object>} Update result
   */
  async updateUser(userId, userData) {
    try {
      const response = await axios.put(`${API_BASE}/users/${userId}`, userData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update user'
      };
    }
  }

  /**
   * Update user role
   * @param {number} userId - User ID
   * @param {string} role - New role
   * @returns {Promise<Object>} Update result
   */
  async updateUserRole(userId, role) {
    try {
      const response = await axios.put(`${API_BASE}/users/${userId}/role`, { role });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update user role'
      };
    }
  }

  /**
   * Update user status
   * @param {number} userId - User ID
   * @param {string} status - New status
   * @returns {Promise<Object>} Update result
   */
  async updateUserStatus(userId, status) {
    try {
      const response = await axios.put(`${API_BASE}/users/${userId}/status`, { status });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update user status'
      };
    }
  }

  /**
   * Delete user
   * @param {number} userId - User ID
   * @returns {Promise<Object>} Delete result
   */
  async deleteUser(userId) {
    try {
      const response = await axios.delete(`${API_BASE}/users/${userId}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to delete user'
      };
    }
  }

  /**
   * Get user audit logs
   * @param {number} userId - User ID
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Audit logs result
   */
  async getUserAuditLogs(userId, params = {}) {
    try {
      const response = await axios.get(`${API_BASE}/users/${userId}/audit-logs`, { params });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch audit logs'
      };
    }
  }

  /**
   * Get admin dashboard statistics
   * @returns {Promise<Object>} Dashboard stats result
   */
  async getDashboardStats() {
    try {
      const response = await axios.get(`${API_BASE}/users/dashboard/stats`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to fetch dashboard statistics'
      };
    }
  }

  /**
   * Search users
   * @param {string} query - Search query
   * @param {Object} filters - Additional filters
   * @returns {Promise<Object>} Search result
   */
  async searchUsers(query, filters = {}) {
    try {
      const params = {
        search: query,
        ...filters,
        per_page: 20 // Limit search results
      };

      const response = await axios.get(`${API_BASE}/users`, { params });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to search users'
      };
    }
  }

  /**
   * Bulk update users status
   * @param {Array} userIds - Array of user IDs
   * @param {string} status - New status
   * @returns {Promise<Object>} Bulk update result
   */
  async bulkUpdateStatus(userIds, status) {
    try {
      const promises = userIds.map(userId => this.updateUserStatus(userId, status));
      const results = await Promise.allSettled(promises);

      const successful = results.filter(result => result.status === 'fulfilled' && result.value.success);
      const failed = results.filter(result => result.status === 'rejected' || !result.value.success);

      return {
        success: true,
        data: {
          successful: successful.length,
          failed: failed.length,
          total: userIds.length
        }
      };
    } catch (error) {
      return {
        success: false,
        error: 'Failed to bulk update users'
      };
    }
  }

  /**
   * Export users data
   * @param {Object} filters - Export filters
   * @returns {Promise<Object>} Export result
   */
  async exportUsers(filters = {}) {
    try {
      // This would typically generate a CSV or Excel file
      // For now, we'll just get all users matching the filters
      const params = {
        ...filters,
        per_page: 1000 // Large number to get all users
      };

      const response = await axios.get(`${API_BASE}/users`, { params });

      if (response.data.success) {
        return {
          success: true,
          data: response.data.users
        };
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to export users'
      };
    }
  }

  /**
   * Get role options
   * @returns {Array} Available roles
   */
  getRoleOptions() {
    return [
      { value: 'admin', label: 'Admin' },
      { value: 'user', label: 'User' },
      { value: 'guest', label: 'Guest' }
    ];
  }

  /**
   * Get status options
   * @returns {Array} Available statuses
   */
  getStatusOptions() {
    return [
      { value: 'active', label: 'Active' },
      { value: 'inactive', label: 'Inactive' },
      { value: 'suspended', label: 'Suspended' },
      { value: 'pending', label: 'Pending' }
    ];
  }

  /**
   * Get experience level options
   * @returns {Array} Available experience levels
   */
  getExperienceOptions() {
    return [
      { value: 'beginner', label: 'Beginner' },
      { value: 'intermediate', label: 'Intermediate' },
      { value: 'advanced', label: 'Advanced' }
    ];
  }

  /**
   * Get risk tolerance options
   * @returns {Array} Available risk tolerance levels
   */
  getRiskToleranceOptions() {
    return [
      { value: 'low', label: 'Low' },
      { value: 'medium', label: 'Medium' },
      { value: 'high', label: 'High' }
    ];
  }

  /**
   * Format user data for display
   * @param {Object} user - User object
   * @returns {Object} Formatted user data
   */
  formatUserForDisplay(user) {
    return {
      ...user,
      full_name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'N/A',
      created_at_formatted: user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A',
      last_login_formatted: user.last_login ? new Date(user.last_login).toLocaleString() : 'Never',
      role_formatted: user.role ? user.role.toUpperCase() : 'N/A',
      status_formatted: user.status ? user.status.toUpperCase() : 'N/A',
      initial_capital_formatted: user.initial_capital ? `$${parseFloat(user.initial_capital).toLocaleString()}` : 'N/A'
    };
  }

  /**
   * Validate user data
   * @param {Object} userData - User data to validate
   * @returns {Object} Validation result
   */
  validateUserData(userData) {
    const errors = {};

    if (userData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userData.email)) {
      errors.email = 'Invalid email format';
    }

    if (userData.username && userData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    }

    if (userData.initial_capital && (isNaN(parseFloat(userData.initial_capital)) || parseFloat(userData.initial_capital) < 0)) {
      errors.initial_capital = 'Initial capital must be a positive number';
    }

    const validRoles = this.getRoleOptions().map(option => option.value);
    if (userData.role && !validRoles.includes(userData.role)) {
      errors.role = 'Invalid role';
    }

    const validStatuses = this.getStatusOptions().map(option => option.value);
    if (userData.status && !validStatuses.includes(userData.status)) {
      errors.status = 'Invalid status';
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }
}

// Create and export singleton instance
export const adminService = new AdminService();
export default adminService;