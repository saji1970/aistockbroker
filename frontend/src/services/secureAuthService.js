/**
 * Secure Authentication Service
 * Enhanced authentication with comprehensive security measures
 */

import { secureApiRequest, secureStorage, logSecurityEvent, validateEmail, validatePasswordStrength } from '../utils/security';
import { API_BASE_URL } from './config';

class SecureAuthService {
  constructor() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    this.refreshTimer = null;
    this.csrfToken = null;
    
    // Initialize security
    this.initializeSecurity();
  }

  /**
   * Initialize security features
   */
  initializeSecurity() {
    // Load tokens from secure storage
    this.loadTokensFromStorage();
    
    // Set up token refresh timer
    this.setupTokenRefresh();
    
    // Validate existing session
    this.validateSession();
  }

  /**
   * Load tokens from secure storage
   */
  loadTokensFromStorage() {
    try {
      const storedToken = secureStorage.getItem('auth_token');
      const storedRefreshToken = secureStorage.getItem('refresh_token');
      const storedUser = secureStorage.getItem('user_data');
      const storedCsrfToken = secureStorage.getItem('csrf_token');

      if (storedToken && this.isTokenValid(storedToken)) {
        this.token = storedToken;
        this.refreshToken = storedRefreshToken;
        this.user = storedUser;
        this.csrfToken = storedCsrfToken;
      } else {
        this.clearAuthData();
      }
    } catch (error) {
      console.error('Error loading tokens from storage:', error);
      this.clearAuthData();
    }
  }

  /**
   * Validate token format and expiration
   */
  isTokenValid(token) {
    if (!token || typeof token !== 'string') {
      return false;
    }

    try {
      // Decode JWT token to check expiration
      const parts = token.split('.');
      if (parts.length !== 3) {
        return false;
      }

      const payload = JSON.parse(atob(parts[1]));
      const currentTime = Math.floor(Date.now() / 1000);

      // Check if token is expired or expires within 5 minutes
      if (payload.exp && payload.exp < currentTime + 300) {
        return false;
      }

      return true;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }

  /**
   * Secure login with comprehensive validation
   */
  async login(emailOrUsername, password, rememberMe = false) {
    try {
      // Input validation
      if (!emailOrUsername || !password) {
        throw new Error('Email/username and password are required');
      }

      // Sanitize inputs
      const sanitizedEmail = emailOrUsername.trim();
      const sanitizedPassword = password;

      // Validate email format if it looks like an email
      if (sanitizedEmail.includes('@') && !validateEmail(sanitizedEmail)) {
        throw new Error('Invalid email format');
      }

      // Check rate limiting
      if (!this.checkLoginRateLimit()) {
        throw new Error('Too many login attempts. Please try again later.');
      }

      // Prepare login data
      const loginData = {
        username: sanitizedEmail,
        password: sanitizedPassword,
        remember_me: rememberMe
      };

      // Make secure API request
      const response = await secureApiRequest(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        body: JSON.stringify(loginData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Login failed');
      }

      const result = await response.json();

      if (result.success) {
        // Store tokens securely
        this.token = result.access_token;
        this.refreshToken = result.refresh_token;
        this.csrfToken = result.csrf_token;
        this.user = result.user;

        // Store in secure storage
        if (rememberMe) {
          secureStorage.setItem('auth_token', this.token);
          secureStorage.setItem('refresh_token', this.refreshToken);
          secureStorage.setItem('user_data', this.user);
          secureStorage.setItem('csrf_token', this.csrfToken);
        }

        // Set up token refresh
        this.setupTokenRefresh();

        // Log successful login
        logSecurityEvent('LOGIN_SUCCESS', {
          user_id: this.user.user_id,
          remember_me: rememberMe
        });

        return result;
      } else {
        throw new Error(result.error || 'Login failed');
      }

    } catch (error) {
      // Log failed login attempt
      logSecurityEvent('LOGIN_FAILURE', {
        email_or_username: emailOrUsername,
        error: error.message
      });

      throw error;
    }
  }

  /**
   * Check login rate limiting
   */
  checkLoginRateLimit() {
    const now = Date.now();
    const attempts = secureStorage.getItem('login_attempts') || [];
    
    // Remove attempts older than 5 minutes
    const recentAttempts = attempts.filter(
      attempt => now - attempt.timestamp < 300000
    );
    
    // Check if limit exceeded
    if (recentAttempts.length >= 5) {
      return false;
    }
    
    return true;
  }

  /**
   * Record login attempt
   */
  recordLoginAttempt(success) {
    const attempts = secureStorage.getItem('login_attempts') || [];
    
    if (!success) {
      attempts.push({
        timestamp: Date.now(),
        success: false
      });
      
      secureStorage.setItem('login_attempts', attempts);
    } else {
      // Clear failed attempts on successful login
      secureStorage.setItem('login_attempts', []);
    }
  }

  /**
   * Refresh access token
   */
  async refreshAccessToken() {
    try {
      if (!this.refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await secureApiRequest(`${API_BASE_URL}/api/auth/refresh-token`, {
        method: 'POST',
        body: JSON.stringify({
          refresh_token: this.refreshToken
        })
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const result = await response.json();
      
      this.token = result.access_token;
      
      // Update stored token
      secureStorage.setItem('auth_token', this.token);
      
      // Set up next refresh
      this.setupTokenRefresh();
      
      return true;

    } catch (error) {
      console.error('Token refresh error:', error);
      
      // Clear auth data if refresh fails
      this.clearAuthData();
      
      logSecurityEvent('TOKEN_REFRESH_FAILURE', {
        error: error.message
      });
      
      return false;
    }
  }

  /**
   * Set up automatic token refresh
   */
  setupTokenRefresh() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
    }

    if (!this.token) {
      return;
    }

    try {
      // Decode token to get expiration time
      const parts = this.token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        const expirationTime = payload.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        const timeUntilExpiry = expirationTime - currentTime;
        
        // Refresh token 5 minutes before expiry
        const refreshTime = timeUntilExpiry - 300000;
        
        if (refreshTime > 0) {
          this.refreshTimer = setTimeout(() => {
            this.refreshAccessToken();
          }, refreshTime);
        }
      }
    } catch (error) {
      console.error('Error setting up token refresh:', error);
    }
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      // Call logout endpoint if token is available
      if (this.token) {
        try {
          await secureApiRequest(`${API_BASE_URL}/api/auth/logout`, {
            method: 'POST'
          });
        } catch (error) {
          console.error('Logout API call failed:', error);
        }
      }

      // Log logout event
      logSecurityEvent('LOGOUT', {
        user_id: this.user?.user_id
      });

    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear all auth data
      this.clearAuthData();
    }
  }

  /**
   * Clear all authentication data
   */
  clearAuthData() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    this.csrfToken = null;
    
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }

    // Clear secure storage
    secureStorage.removeItem('auth_token');
    secureStorage.removeItem('refresh_token');
    secureStorage.removeItem('user_data');
    secureStorage.removeItem('csrf_token');
  }

  /**
   * Verify current session
   */
  async verifySession() {
    try {
      if (!this.token) {
        return { valid: false, user: null };
      }

      const response = await secureApiRequest(`${API_BASE_URL}/api/auth/verify-session`, {
        method: 'GET'
      });

      if (!response.ok) {
        this.clearAuthData();
        return { valid: false, user: null };
      }

      const result = await response.json();
      
      if (result.valid) {
        this.user = result.user;
        secureStorage.setItem('user_data', this.user);
        return { valid: true, user: this.user };
      } else {
        this.clearAuthData();
        return { valid: false, user: null };
      }

    } catch (error) {
      console.error('Session verification error:', error);
      this.clearAuthData();
      return { valid: false, user: null };
    }
  }

  /**
   * Validate session on app start
   */
  async validateSession() {
    try {
      if (!this.token) {
        return false;
      }

      const sessionResult = await this.verifySession();
      return sessionResult.valid;

    } catch (error) {
      console.error('Session validation error:', error);
      return false;
    }
  }

  /**
   * Get current user
   */
  getCurrentUser() {
    return this.user;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!(this.token && this.user);
  }

  /**
   * Check if user has specific role
   */
  hasRole(role) {
    if (!this.user || !this.user.roles) {
      return false;
    }
    
    return this.user.roles.includes(role) || this.user.selectedRole === role;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(roles) {
    if (!this.user || !this.user.roles) {
      return false;
    }
    
    return roles.some(role => 
      this.user.roles.includes(role) || this.user.selectedRole === role
    );
  }

  /**
   * Check if user is admin
   */
  isAdmin() {
    return this.hasRole('admin');
  }

  /**
   * Check if user account is active
   */
  isActive() {
    return this.user && this.user.status === 'active';
  }

  /**
   * Check if user can access trading features
   */
  canAccessTrading() {
    if (!this.isActive()) {
      return false;
    }
    
    return this.hasAnyRole(['admin', 'agent', 'customer', 'user']);
  }

  /**
   * Update selected role for multi-role users
   */
  updateSelectedRole(selectedRole) {
    if (this.user && this.user.roles && this.user.roles.includes(selectedRole)) {
      this.user.selectedRole = selectedRole;
      secureStorage.setItem('user_data', this.user);
      
      logSecurityEvent('ROLE_SWITCH', {
        user_id: this.user.user_id,
        new_role: selectedRole
      });
      
      return true;
    }
    
    return false;
  }

  /**
   * Get CSRF token
   */
  getCSRFToken() {
    return this.csrfToken;
  }

  /**
   * Refresh CSRF token
   */
  async refreshCSRFToken() {
    try {
      if (!this.token) {
        throw new Error('Authentication required');
      }

      const response = await secureApiRequest(`${API_BASE_URL}/api/csrf-token`, {
        method: 'GET'
      });

      if (!response.ok) {
        throw new Error('Failed to refresh CSRF token');
      }

      const result = await response.json();
      this.csrfToken = result.csrf_token;
      secureStorage.setItem('csrf_token', this.csrfToken);
      
      return this.csrfToken;

    } catch (error) {
      console.error('CSRF token refresh error:', error);
      return null;
    }
  }

  /**
   * Register new user
   */
  async register(userData) {
    try {
      // Validate user data
      if (!userData.email || !userData.password || !userData.name) {
        throw new Error('Email, password, and name are required');
      }

      if (!validateEmail(userData.email)) {
        throw new Error('Invalid email format');
      }

      const passwordValidation = validatePasswordStrength(userData.password);
      if (!passwordValidation.valid) {
        throw new Error(`Password validation failed: ${passwordValidation.errors.join(', ')}`);
      }

      // Sanitize user data
      const sanitizedData = {
        email: userData.email.trim(),
        password: userData.password,
        name: userData.name.trim(),
        role: userData.role || 'customer'
      };

      const response = await secureApiRequest(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        body: JSON.stringify(sanitizedData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Registration failed');
      }

      const result = await response.json();

      logSecurityEvent('USER_REGISTRATION', {
        email: sanitizedData.email,
        role: sanitizedData.role
      });

      return result;

    } catch (error) {
      logSecurityEvent('REGISTRATION_FAILURE', {
        email: userData.email,
        error: error.message
      });
      
      throw error;
    }
  }

  /**
   * Change password
   */
  async changePassword(currentPassword, newPassword) {
    try {
      if (!this.token) {
        throw new Error('Authentication required');
      }

      // Validate new password
      const passwordValidation = validatePasswordStrength(newPassword);
      if (!passwordValidation.valid) {
        throw new Error(`Password validation failed: ${passwordValidation.errors.join(', ')}`);
      }

      const response = await secureApiRequest(`${API_BASE_URL}/api/auth/change-password`, {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Password change failed');
      }

      logSecurityEvent('PASSWORD_CHANGE', {
        user_id: this.user.user_id
      });

      return await response.json();

    } catch (error) {
      logSecurityEvent('PASSWORD_CHANGE_FAILURE', {
        user_id: this.user?.user_id,
        error: error.message
      });
      
      throw error;
    }
  }

  /**
   * Get security events
   */
  getSecurityEvents() {
    return secureStorage.getItem('security_events') || [];
  }

  /**
   * Clear security events
   */
  clearSecurityEvents() {
    secureStorage.setItem('security_events', []);
  }
}

// Create singleton instance
const secureAuthService = new SecureAuthService();

export default secureAuthService;
