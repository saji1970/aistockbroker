/**
 * Frontend Security Utilities
 * Comprehensive security measures for client-side protection
 */

import CryptoJS from 'crypto-js';

// Security Constants
const SECURITY_CONFIG = {
  MAX_INPUT_LENGTH: 1000,
  MIN_PASSWORD_LENGTH: 8,
  MAX_LOGIN_ATTEMPTS: 5,
  SESSION_TIMEOUT: 3600000, // 1 hour in milliseconds
  CSRF_TOKEN_LIFETIME: 1800000, // 30 minutes
  RATE_LIMIT_WINDOW: 60000, // 1 minute
  MAX_REQUESTS_PER_WINDOW: 100
};

// Security storage for client-side rate limiting
const rateLimitStorage = new Map();
const loginAttempts = new Map();

/**
 * Sanitize user input to prevent XSS attacks
 */
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') {
    return String(input);
  }

  // Remove potentially dangerous characters
  const dangerousChars = /[<>'"&]/g;
  let sanitized = input.replace(dangerousChars, '');
  
  // Limit length
  sanitized = sanitized.substring(0, SECURITY_CONFIG.MAX_INPUT_LENGTH);
  
  // Trim whitespace
  return sanitized.trim();
};

/**
 * Validate email format
 */
export const validateEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

/**
 * Validate password strength
 */
export const validatePasswordStrength = (password) => {
  const errors = [];
  
  if (password.length < SECURITY_CONFIG.MIN_PASSWORD_LENGTH) {
    errors.push('Password must be at least 8 characters long');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  
  // Check for common passwords
  const commonPasswords = [
    'password', '123456', 'admin', 'qwerty', 'letmein',
    'welcome', 'monkey', 'dragon', 'master', 'hello'
  ];
  
  if (commonPasswords.includes(password.toLowerCase())) {
    errors.push('Password is too common');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
};

/**
 * Validate stock symbol format
 */
export const validateStockSymbol = (symbol) => {
  if (!symbol || typeof symbol !== 'string') {
    return false;
  }
  
  // Allow alphanumeric and some special characters
  const symbolRegex = /^[A-Za-z0-9.\-]+$/;
  return symbolRegex.test(symbol) && symbol.length <= 10;
};

/**
 * Validate numeric input
 */
export const validateNumericInput = (value, min = null, max = null) => {
  const num = parseFloat(value);
  
  if (isNaN(num)) {
    return false;
  }
  
  if (min !== null && num < min) {
    return false;
  }
  
  if (max !== null && num > max) {
    return false;
  }
  
  return true;
};

/**
 * Rate limiting check
 */
export const checkRateLimit = (endpoint) => {
  const now = Date.now();
  const key = `${endpoint}_${getClientIP()}`;
  
  if (!rateLimitStorage.has(key)) {
    rateLimitStorage.set(key, []);
  }
  
  const requests = rateLimitStorage.get(key);
  
  // Remove old requests
  const recentRequests = requests.filter(
    timestamp => now - timestamp < SECURITY_CONFIG.RATE_LIMIT_WINDOW
  );
  
  // Check if limit exceeded
  if (recentRequests.length >= SECURITY_CONFIG.MAX_REQUESTS_PER_WINDOW) {
    return false;
  }
  
  // Add current request
  recentRequests.push(now);
  rateLimitStorage.set(key, recentRequests);
  
  return true;
};

/**
 * Check login attempts
 */
export const checkLoginAttempts = (username) => {
  const key = `login_${username}_${getClientIP()}`;
  const attempts = loginAttempts.get(key) || { count: 0, lastAttempt: 0 };
  
  const now = Date.now();
  
  // Reset if 5 minutes have passed
  if (now - attempts.lastAttempt > 300000) {
    attempts.count = 0;
  }
  
  return attempts.count < SECURITY_CONFIG.MAX_LOGIN_ATTEMPTS;
};

/**
 * Record login attempt
 */
export const recordLoginAttempt = (username, success) => {
  const key = `login_${username}_${getClientIP()}`;
  const attempts = loginAttempts.get(key) || { count: 0, lastAttempt: 0 };
  
  if (success) {
    attempts.count = 0;
  } else {
    attempts.count += 1;
  }
  
  attempts.lastAttempt = Date.now();
  loginAttempts.set(key, attempts);
};

/**
 * Get client IP (mock implementation)
 */
export const getClientIP = () => {
  // In a real application, this would be provided by the server
  // For now, we'll use a mock IP
  return 'client_ip_mock';
};

/**
 * Generate secure random token
 */
export const generateSecureToken = (length = 32) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  return result;
};

/**
 * Hash sensitive data (client-side)
 */
export const hashData = (data, salt = null) => {
  if (!salt) {
    salt = generateSecureToken(16);
  }
  
  const hash = CryptoJS.SHA256(data + salt).toString();
  return { hash, salt };
};

/**
 * Validate CSRF token
 */
export const validateCSRFToken = (token) => {
  if (!token || typeof token !== 'string') {
    return false;
  }
  
  // Basic validation - in production, this would be more comprehensive
  return token.length >= 32;
};

/**
 * Secure localStorage operations
 */
export const secureStorage = {
  setItem: (key, value) => {
    try {
      const encrypted = CryptoJS.AES.encrypt(
        JSON.stringify(value),
        getStorageKey()
      ).toString();
      
      localStorage.setItem(key, encrypted);
      return true;
    } catch (error) {
      console.error('Secure storage set error:', error);
      return false;
    }
  },
  
  getItem: (key) => {
    try {
      const encrypted = localStorage.getItem(key);
      if (!encrypted) {
        return null;
      }
      
      const decrypted = CryptoJS.AES.decrypt(
        encrypted,
        getStorageKey()
      ).toString(CryptoJS.enc.Utf8);
      
      return JSON.parse(decrypted);
    } catch (error) {
      console.error('Secure storage get error:', error);
      return null;
    }
  },
  
  removeItem: (key) => {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Secure storage remove error:', error);
      return false;
    }
  },
  
  clear: () => {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Secure storage clear error:', error);
      return false;
    }
  }
};

/**
 * Get storage encryption key
 */
const getStorageKey = () => {
  // In production, this would be more secure
  // For now, we'll use a combination of factors
  const userAgent = navigator.userAgent;
  const language = navigator.language;
  return CryptoJS.SHA256(userAgent + language).toString().substring(0, 32);
};

/**
 * Content Security Policy validation
 */
export const validateCSP = () => {
  // Check if CSP is properly configured
  const metaTags = document.querySelectorAll('meta[http-equiv="Content-Security-Policy"]');
  
  if (metaTags.length === 0) {
    console.warn('Content Security Policy not found in meta tags');
    return false;
  }
  
  return true;
};

/**
 * Validate secure context
 */
export const validateSecureContext = () => {
  // Check if we're in a secure context (HTTPS)
  if (!window.isSecureContext) {
    console.warn('Application is not running in a secure context');
    return false;
  }
  
  return true;
};

/**
 * Sanitize HTML content
 */
export const sanitizeHTML = (html) => {
  const temp = document.createElement('div');
  temp.textContent = html;
  return temp.innerHTML;
};

/**
 * Validate file upload
 */
export const validateFileUpload = (file, allowedTypes = [], maxSize = 5 * 1024 * 1024) => {
  const errors = [];
  
  // Check file size
  if (file.size > maxSize) {
    errors.push(`File size exceeds ${maxSize / (1024 * 1024)}MB limit`);
  }
  
  // Check file type
  if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
    errors.push(`File type ${file.type} is not allowed`);
  }
  
  // Check for potentially dangerous file types
  const dangerousTypes = [
    'application/x-executable',
    'application/x-sharedlib',
    'application/x-msdownload',
    'application/x-msdos-program'
  ];
  
  if (dangerousTypes.includes(file.type)) {
    errors.push('File type is potentially dangerous');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
};

/**
 * Secure API request wrapper
 */
export const secureApiRequest = async (url, options = {}) => {
  // Check rate limiting
  if (!checkRateLimit(url)) {
    throw new Error('Rate limit exceeded');
  }
  
  // Add security headers
  const secureOptions = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...options.headers
    }
  };
  
  // Add CSRF token if available
  const csrfToken = secureStorage.getItem('csrf_token');
  if (csrfToken) {
    secureOptions.headers['X-CSRF-Token'] = csrfToken;
  }
  
  // Add authorization token if available
  const authToken = secureStorage.getItem('auth_token');
  if (authToken) {
    secureOptions.headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  try {
    const response = await fetch(url, secureOptions);
    
    // Check for security-related headers
    const cspHeader = response.headers.get('Content-Security-Policy');
    if (!cspHeader) {
      console.warn('Content Security Policy header not found in response');
    }
    
    return response;
  } catch (error) {
    console.error('Secure API request error:', error);
    throw error;
  }
};

/**
 * Security event logging
 */
export const logSecurityEvent = (eventType, details) => {
  const event = {
    timestamp: new Date().toISOString(),
    eventType,
    details,
    userAgent: navigator.userAgent,
    url: window.location.href
  };
  
  // In production, this would be sent to a security monitoring system
  console.warn('Security Event:', event);
  
  // Store locally for debugging
  const events = secureStorage.getItem('security_events') || [];
  events.push(event);
  
  // Keep only last 100 events
  if (events.length > 100) {
    events.splice(0, events.length - 100);
  }
  
  secureStorage.setItem('security_events', events);
};

/**
 * Initialize security features
 */
export const initializeSecurity = () => {
  // Validate secure context
  if (!validateSecureContext()) {
    logSecurityEvent('INSECURE_CONTEXT', {
      message: 'Application running in insecure context'
    });
  }
  
  // Validate CSP
  if (!validateCSP()) {
    logSecurityEvent('CSP_MISSING', {
      message: 'Content Security Policy not properly configured'
    });
  }
  
  // Check for development tools
  const devtools = {
    open: false,
    orientation: null
  };
  
  const threshold = 160;
  
  setInterval(() => {
    if (window.outerHeight - window.innerHeight > threshold || 
        window.outerWidth - window.innerWidth > threshold) {
      if (!devtools.open) {
        devtools.open = true;
        logSecurityEvent('DEVTOOLS_OPENED', {
          message: 'Developer tools detected'
        });
      }
    } else {
      devtools.open = false;
    }
  }, 500);
  
  // Monitor for XSS attempts
  const originalEval = window.eval;
  window.eval = function(code) {
    logSecurityEvent('EVAL_ATTEMPT', {
      code: code,
      message: 'Attempted use of eval() function'
    });
    throw new Error('eval() is disabled for security reasons');
  };
  
  // Monitor for suspicious DOM modifications
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check for suspicious attributes
            if (node.onclick || node.onload || node.onerror) {
              logSecurityEvent('SUSPICIOUS_DOM_MODIFICATION', {
                tagName: node.tagName,
                attributes: Array.from(node.attributes).map(attr => ({
                  name: attr.name,
                  value: attr.value
                }))
              });
            }
          }
        });
      }
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
  console.log('Security features initialized');
};

/**
 * Clean up sensitive data
 */
export const cleanupSensitiveData = () => {
  // Clear sensitive data from memory
  rateLimitStorage.clear();
  loginAttempts.clear();
  
  // Clear secure storage
  secureStorage.clear();
  
  // Clear any cached data
  if ('caches' in window) {
    caches.keys().then(names => {
      names.forEach(name => {
        caches.delete(name);
      });
    });
  }
  
  logSecurityEvent('SENSITIVE_DATA_CLEANUP', {
    message: 'Sensitive data cleaned up'
  });
};

export default {
  sanitizeInput,
  validateEmail,
  validatePasswordStrength,
  validateStockSymbol,
  validateNumericInput,
  checkRateLimit,
  checkLoginAttempts,
  recordLoginAttempt,
  generateSecureToken,
  hashData,
  validateCSRFToken,
  secureStorage,
  validateCSP,
  validateSecureContext,
  sanitizeHTML,
  validateFileUpload,
  secureApiRequest,
  logSecurityEvent,
  initializeSecurity,
  cleanupSensitiveData
};
