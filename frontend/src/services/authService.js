/**
 * Authentication Service for AI Stock Trading Frontend
 * Handles user authentication, token management, and session management
 */

import axios from 'axios';
import { API_BASE_URL } from './config';

const API_BASE = API_BASE_URL + '/api';
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user_data';

class AuthService {
  constructor() {
    this.token = localStorage.getItem(TOKEN_KEY);
    this.refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    this.user = this.getStoredUser();
    this.refreshTimer = null;

    // Set up axios interceptor for automatic token inclusion
    this.setupAxiosInterceptors();
  }

  setupAxiosInterceptors() {
    // Request interceptor to add auth token
    axios.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle auth errors and token refresh
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            await this.refreshAuthToken();
            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${this.getToken()}`;
            return axios(originalRequest);
          } catch (refreshError) {
            // Refresh failed, logout user
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise<Object>} Registration result
   */
  async register(userData) {
    try {
      const response = await axios.post(`${API_BASE}/auth/register`, userData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Registration failed'
      };
    }
  }

  /**
   * Login user
   * @param {string} emailOrUsername - Email or username
   * @param {string} password - Password
   * @param {boolean} rememberMe - Remember login
   * @returns {Promise<Object>} Login result
   */
  async login(emailOrUsername, password, rememberMe = false) {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, {
        email_or_username: emailOrUsername,
        password,
        remember_me: rememberMe
      });

      if (response.data.success) {
        const { token, refresh_token, user, expires_at } = response.data;

        // Store authentication data
        this.setToken(token);
        this.setRefreshToken(refresh_token);
        this.setUser(user);

        // Set up automatic token refresh
        this.scheduleTokenRefresh(expires_at);

        return {
          success: true,
          user,
          message: response.data.message
        };
      } else {
        return {
          success: false,
          error: response.data.message || 'Login failed'
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed'
      };
    }
  }

  /**
   * Logout user
   * @param {boolean} logoutAll - Logout from all sessions
   * @returns {Promise<Object>} Logout result
   */
  async logout(logoutAll = false) {
    try {
      if (this.token) {
        await axios.post(`${API_BASE}/auth/logout`, {
          logout_all: logoutAll
        });
      }
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      // Clear local data regardless of API call result
      this.clearAuthData();
      this.clearRefreshTimer();
    }

    return { success: true };
  }

  /**
   * Get current user info
   * @returns {Promise<Object>} User info
   */
  async getCurrentUser() {
    try {
      const response = await axios.get(`${API_BASE}/auth/me`);
      if (response.data.success) {
        this.setUser(response.data.user);
        return {
          success: true,
          user: response.data.user
        };
      }
      return {
        success: false,
        error: 'Failed to get user info'
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to get user info'
      };
    }
  }

  /**
   * Update user profile
   * @param {Object} profileData - Profile update data
   * @returns {Promise<Object>} Update result
   */
  async updateProfile(profileData) {
    try {
      const response = await axios.put(`${API_BASE}/users/profile`, profileData);
      if (response.data.success) {
        this.setUser(response.data.user);
        return {
          success: true,
          user: response.data.user,
          message: response.data.message
        };
      }
      return {
        success: false,
        error: response.data.message || 'Failed to update profile'
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to update profile'
      };
    }
  }

  /**
   * Change password
   * @param {string} currentPassword - Current password
   * @param {string} newPassword - New password
   * @returns {Promise<Object>} Change result
   */
  async changePassword(currentPassword, newPassword) {
    try {
      const response = await axios.post(`${API_BASE}/users/change-password`, {
        current_password: currentPassword,
        new_password: newPassword
      });

      return {
        success: response.data.success,
        message: response.data.message || (response.data.success ? 'Password changed successfully' : 'Failed to change password')
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to change password'
      };
    }
  }

  /**
   * Request password reset
   * @param {string} email - Email address
   * @returns {Promise<Object>} Reset request result
   */
  async requestPasswordReset(email) {
    try {
      const response = await axios.post(`${API_BASE}/auth/forgot-password`, {
        email
      });

      return {
        success: true,
        message: response.data.message || 'Password reset email sent'
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to send reset email'
      };
    }
  }

  /**
   * Reset password with token
   * @param {string} resetToken - Reset token
   * @param {string} newPassword - New password
   * @returns {Promise<Object>} Reset result
   */
  async resetPassword(resetToken, newPassword) {
    try {
      const response = await axios.post(`${API_BASE}/auth/reset-password`, {
        reset_token: resetToken,
        new_password: newPassword
      });

      return {
        success: response.data.success,
        message: response.data.message || (response.data.success ? 'Password reset successfully' : 'Password reset failed')
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Password reset failed'
      };
    }
  }

  /**
   * Refresh authentication token
   * @returns {Promise<void>}
   */
  async refreshAuthToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(`${API_BASE}/auth/refresh-token`, {
        refresh_token: this.refreshToken
      });

      if (response.data.success) {
        const { token, expires_at, user } = response.data;
        this.setToken(token);
        this.setUser(user);
        this.scheduleTokenRefresh(expires_at);
      } else {
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      this.clearAuthData();
      throw error;
    }
  }

  /**
   * Verify session validity
   * @returns {Promise<boolean>} Session validity
   */
  async verifySession() {
    if (!this.token) {
      return false;
    }

    try {
      const response = await axios.post(`${API_BASE}/auth/verify-session`);
      if (response.data.success && response.data.session_valid) {
        this.setUser(response.data.user);
        this.scheduleTokenRefresh(response.data.expires_at);
        return true;
      }
      return false;
    } catch (error) {
      this.clearAuthData();
      return false;
    }
  }

  /**
   * Schedule automatic token refresh
   * @param {string} expiresAt - Token expiration time
   */
  scheduleTokenRefresh(expiresAt) {
    this.clearRefreshTimer();

    const expirationTime = new Date(expiresAt);
    const now = new Date();
    const timeUntilExpiry = expirationTime.getTime() - now.getTime();

    // Refresh token 5 minutes before expiry
    const refreshTime = Math.max(timeUntilExpiry - 5 * 60 * 1000, 60 * 1000);

    this.refreshTimer = setTimeout(async () => {
      try {
        await this.refreshAuthToken();
      } catch (error) {
        console.error('Auto token refresh failed:', error);
        this.logout();
      }
    }, refreshTime);
  }

  /**
   * Clear refresh timer
   */
  clearRefreshTimer() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  /**
   * Check if user is authenticated
   * @returns {boolean} Authentication status
   */
  isAuthenticated() {
    return !!this.token && !!this.user;
  }

  /**
   * Check if user has admin role
   * @returns {boolean} Admin status
   */
  isAdmin() {
    return this.user?.role === 'admin';
  }

  /**
   * Check if user account is active
   * @returns {boolean} Active status
   */
  isActive() {
    return this.user?.status === 'active';
  }

  /**
   * Check if user can access trading features
   * @returns {boolean} Trading access status
   */
  canAccessTrading() {
    return this.isActive() && (this.user?.role === 'user' || this.user?.role === 'admin');
  }

  /**
   * Get stored token
   * @returns {string|null} Auth token
   */
  getToken() {
    return this.token || localStorage.getItem(TOKEN_KEY);
  }

  /**
   * Set auth token
   * @param {string} token - Auth token
   */
  setToken(token) {
    this.token = token;
    localStorage.setItem(TOKEN_KEY, token);
  }

  /**
   * Get refresh token
   * @returns {string|null} Refresh token
   */
  getRefreshToken() {
    return this.refreshToken || localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Set refresh token
   * @param {string} refreshToken - Refresh token
   */
  setRefreshToken(refreshToken) {
    this.refreshToken = refreshToken;
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }

  /**
   * Get stored user data
   * @returns {Object|null} User data
   */
  getStoredUser() {
    try {
      const userData = localStorage.getItem(USER_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error parsing stored user data:', error);
      localStorage.removeItem(USER_KEY);
      return null;
    }
  }

  /**
   * Get current user
   * @returns {Object|null} Current user
   */
  getUser() {
    return this.user;
  }

  /**
   * Set user data
   * @param {Object} user - User data
   */
  setUser(user) {
    this.user = user;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * Clear all authentication data
   */
  clearAuthData() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

// Create and export singleton instance
export const authService = new AuthService();
export default authService;