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
    this.refreshAttempts = 0;
    this.maxRefreshAttempts = 3;
    this.refreshCooldownMs = 5000; // 5 seconds cooldown between attempts
    this.lastRefreshAttempt = 0;

    // Set up axios interceptor for automatic token inclusion
    this.setupAxiosInterceptors();

    // Check for expired tokens on initialization
    this.checkTokenValidity();
    
    // Clear any invalid tokens that might cause infinite loops
    this.clearInvalidTokens();
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

        // Don't retry refresh-token endpoint to avoid infinite loops
        const isRefreshTokenEndpoint = originalRequest.url && originalRequest.url.includes('/refresh-token');
        
        // Prevent infinite retry loops with a retry counter
        const retryCount = originalRequest._retryCount || 0;
        const maxRetries = 2;
        
        if (error.response?.status === 401 && retryCount < maxRetries && !isRefreshTokenEndpoint) {
          originalRequest._retryCount = retryCount + 1;

          try {
            await this.refreshAuthToken();
            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${this.getToken()}`;
            return axios(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear auth data and redirect
            console.warn('Token refresh failed, clearing auth data');
            this.clearAuthData();
            this.clearRefreshTimer();
            if (window.location.pathname !== '/login') {
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          }
        }

        // If it's a refresh token endpoint that failed, clear auth data
        if (isRefreshTokenEndpoint && error.response?.status === 401) {
          console.warn('Refresh token endpoint failed, clearing auth data');
          this.clearAuthData();
          this.clearRefreshTimer();
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
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
      console.log('🌐 AuthService: Making login request...');
      console.log('📡 AuthService: API endpoint:', `${API_BASE}/auth/login`);
      console.log('📧 AuthService: Email/Username:', emailOrUsername);
      console.log('🔑 AuthService: Password length:', password.length);
      console.log('💾 AuthService: Remember me:', rememberMe);

      const requestData = {
        email_or_username: emailOrUsername,
        password,
        remember_me: rememberMe
      };
      console.log('📤 AuthService: Request data:', { ...requestData, password: '[REDACTED]' });

      const response = await axios.post(`${API_BASE}/auth/login`, requestData);
      
      console.log('📥 AuthService: Response received');
      console.log('📊 AuthService: Response status:', response.status);
      console.log('📋 AuthService: Response data:', response.data);

      if (response.data.success) {
        const { token, refresh_token, user, expires_at } = response.data;

        console.log('🎉 AuthService: Login successful, storing tokens...');
        console.log('🔑 AuthService: Token length:', token ? token.length : 0);
        console.log('🔄 AuthService: Refresh token length:', refresh_token ? refresh_token.length : 0);
        console.log('👤 AuthService: User data:', user);

        // Store authentication data
        this.setToken(token);
        this.setRefreshToken(refresh_token);
        this.setUser(user);

        // Reset refresh attempts on successful login
        this.refreshAttempts = 0;

        // Set up automatic token refresh
        this.scheduleTokenRefresh(expires_at);

        return {
          success: true,
          user,
          message: response.data.message
        };
      } else {
        console.log('❌ AuthService: Login failed - success=false');
        console.log('📝 AuthService: Error message:', response.data.message);
        return {
          success: false,
          error: response.data.message || 'Login failed'
        };
      }
    } catch (error) {
      console.error('💥 AuthService: Login request failed');
      console.error('🔴 AuthService: Error status:', error.response?.status);
      console.error('📝 AuthService: Error data:', error.response?.data);
      console.error('🌐 AuthService: Error message:', error.message);
      
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
      if (response.data.success && response.data.user) {
        // Only set user if we have valid user data
        if (response.data.user && typeof response.data.user === 'object') {
          this.setUser(response.data.user);
          return {
            success: true,
            user: response.data.user
          };
        } else {
          console.warn('getCurrentUser: Invalid user data received from server:', response.data.user);
          return {
            success: false,
            error: 'Invalid user data received'
          };
        }
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
      console.warn('refreshAuthToken: No refresh token available, clearing auth data');
      this.clearAuthData();
      this.clearRefreshTimer();
      throw new Error('No refresh token available');
    }

    // Check if we're in cooldown period
    const now = Date.now();
    if (now - this.lastRefreshAttempt < this.refreshCooldownMs) {
      console.warn('refreshAuthToken: Still in cooldown period, skipping refresh');
      return;
    }

    // Check if we've exceeded max attempts
    if (this.refreshAttempts >= this.maxRefreshAttempts) {
      console.warn('refreshAuthToken: Max refresh attempts exceeded, clearing auth data');
      this.clearAuthData();
      this.clearRefreshTimer();
      throw new Error('Max refresh attempts exceeded');
    }

    this.lastRefreshAttempt = now;
    this.refreshAttempts++;

    try {
      const response = await axios.post(`${API_BASE}/auth/refresh-token`, {
        refresh_token: this.refreshToken
      });

      if (response.data.success) {
        const { token, expires_at, user } = response.data;
        this.setToken(token);
        // Reset refresh attempts on successful refresh
        this.refreshAttempts = 0;
        
        // Only set user if we have valid user data
        if (user && typeof user === 'object') {
          this.setUser(user);
        } else {
          console.warn('refreshAuthToken: Invalid user data received:', user);
          // Don't clear auth data here, just log the warning
          // The token might still be valid even if user data is missing
        }
        this.scheduleTokenRefresh(expires_at);
      } else {
        console.warn('refreshAuthToken: Token refresh failed');
        throw new Error('Token refresh failed');
      }
    } catch (error) {
      console.error('refreshAuthToken error:', error);
      // If refresh token is invalid or expired, clear auth data immediately
      if (error.response?.status === 401) {
        console.warn('Refresh token is invalid or expired, clearing auth data');
        this.clearAuthData();
        this.clearRefreshTimer();
        // Redirect to login page immediately
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        throw new Error('Refresh token expired');
      }
      // For other errors, don't immediately clear auth data
      // The token might still be valid, just the refresh failed
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
        // Only set user if we have valid user data
        if (response.data.user && typeof response.data.user === 'object') {
          this.setUser(response.data.user);
        } else {
          console.warn('verifySession: Invalid user data received:', response.data.user);
        }
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

    // Don't schedule refresh if no refresh token is available
    if (!this.refreshToken) {
      return;
    }

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
        // Only logout if refresh token is expired, not for network errors
        if (error.message === 'Refresh token expired') {
          this.logout();
        }
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
      if (!userData || userData === 'undefined' || userData === 'null') {
        localStorage.removeItem(USER_KEY);
        return null;
      }
      const parsed = JSON.parse(userData);
      if (parsed && typeof parsed === 'object') {
        return parsed;
      } else {
        console.warn('Invalid user data format, clearing storage');
        localStorage.removeItem(USER_KEY);
        return null;
      }
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
    // Enhanced validation for user data
    if (user && typeof user === 'object' && user !== null) {
      // Check for required user properties
      if (user.id || user.user_id || user.email || user.username) {
        this.user = user;
        localStorage.setItem(USER_KEY, JSON.stringify(user));
      } else {
        console.warn('Invalid user data provided to setUser - missing required properties:', user);
        localStorage.removeItem(USER_KEY);
        this.user = null;
      }
    } else {
      console.warn('Invalid user data provided to setUser:', user);
      localStorage.removeItem(USER_KEY);
      this.user = null;
    }
  }

  /**
   * Check token validity on initialization
   */
  checkTokenValidity() {
    if (this.token && this.refreshToken) {
      try {
        // Check if token is expired by parsing JWT payload
        const tokenParts = this.token.split('.');
        if (tokenParts.length === 3) {
          // This is a JWT token, check expiration
          const payload = JSON.parse(atob(tokenParts[1]));
          const currentTime = Math.floor(Date.now() / 1000);
          
          // If token is expired or expires within 5 minutes, clear auth data
          if (payload.exp && payload.exp < currentTime + 300) {
            console.warn('Token is expired or about to expire, clearing auth data');
            this.clearAuthData();
            this.clearRefreshTimer();
          }
        } else {
          // This is not a JWT token (like demo tokens), skip expiration check
          console.debug('Non-JWT token detected, skipping expiration check');
        }
      } catch (error) {
        console.warn('Invalid token format, clearing auth data');
        this.clearAuthData();
        this.clearRefreshTimer();
      }
    }
  }

  /**
   * Clear invalid tokens that might cause infinite loops
   */
  clearInvalidTokens() {
    // Only clear tokens if we have tokens but no user data AND tokens are actually invalid
    // Don't clear demo tokens if they're valid (even if short)
    if ((this.token || this.refreshToken) && !this.user) {
      // Check if tokens are actually invalid (not just demo tokens)
      const isTokenInvalid = this.token && this.token.length < 5; // Very short tokens are invalid
      const isRefreshInvalid = this.refreshToken && this.refreshToken.length < 5;
      
      if (isTokenInvalid || isRefreshInvalid) {
        console.warn('Found invalid tokens without user data, clearing auth data');
        this.clearAuthData();
        this.clearRefreshTimer();
      } else {
        // Tokens exist but no user data - this might be normal for demo tokens
        // Don't clear them, just load user data from localStorage
        this.user = this.getStoredUser();
      }
    }
  }

  /**
   * Clear all authentication data
   */
  clearAuthData() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    this.refreshAttempts = 0;
    this.lastRefreshAttempt = 0;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

// Create and export singleton instance
export const authService = new AuthService();
export default authService;