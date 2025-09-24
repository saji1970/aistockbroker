/**
 * Trading Authentication Utilities
 * Handles trading access errors and automatic logout
 */

class TradingAuthError extends Error {
  constructor(message, status, code) {
    super(message);
    this.name = 'TradingAuthError';
    this.status = status;
    this.code = code;
  }
}

/**
 * Handle trading access denied errors
 * Automatically logout and redirect to login page
 */
export const handleTradingAccessError = (error, navigate) => {
  console.error('Trading Access Error:', error);
  
  // Check if it's a trading access denied error
  if (error.response?.data?.error === 'Trading Access Denied' || 
      error.message?.includes('Trading Access Denied') ||
      error.response?.status === 401 ||
      error.response?.status === 403) {
    
    // Show user-friendly message
    const message = error.response?.data?.message || 
                   'Trading access denied. Please login with proper credentials.';
    
    // Show notification
    if (typeof window !== 'undefined' && window.alert) {
      alert(`🔒 ${message}\n\nYou will be redirected to the login page.`);
    } else {
      console.warn(`🔒 ${message}\n\nYou will be redirected to the login page.`);
    }
    
    // Clear local storage (logout)
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('trading_access_token');
    localStorage.removeItem('refreshToken');
    
    // Redirect to login page
    if (navigate) {
      navigate('/login');
    } else {
      window.location.href = '/login';
    }
    
    return true; // Error was handled
  }
  
  return false; // Error was not handled
};

/**
 * Enhanced API request wrapper with trading access error handling
 */
export const apiRequest = async (requestFn, navigate) => {
  try {
    return await requestFn();
  } catch (error) {
    // Handle trading access errors
    if (handleTradingAccessError(error, navigate)) {
      throw new TradingAuthError(
        'Trading access denied. Please login with proper credentials.',
        403,
        'TRADING_ACCESS_DENIED'
      );
    }
    
    // Re-throw other errors
    throw error;
  }
};

/**
 * Get trading access token from storage or API
 */
export const getTradingAccessToken = async () => {
  try {
    // First try to get from local storage
    const storedToken = localStorage.getItem('trading_access_token');
    if (storedToken) {
      return storedToken;
    }
    
    // If not in storage, get from API
    const response = await fetch('/api/trading/access');
    const data = await response.json();
    
    if (data.access_tokens) {
      // Use trader token by default
      const token = data.access_tokens.trader;
      localStorage.setItem('trading_access_token', token);
      return token;
    }
    
    return null;
  } catch (error) {
    console.error('Error getting trading access token:', error);
    return null;
  }
};

/**
 * Set trading access token
 */
export const setTradingAccessToken = (token) => {
  localStorage.setItem('trading_access_token', token);
};

/**
 * Clear trading access token
 */
export const clearTradingAccessToken = () => {
  localStorage.removeItem('trading_access_token');
};

/**
 * Check if user has trading access
 */
export const hasTradingAccess = () => {
  const token = localStorage.getItem('trading_access_token');
  return !!token;
};

/**
 * Enhanced fetch with trading access headers
 */
export const fetchWithTradingAccess = async (url, options = {}) => {
  const token = await getTradingAccessToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['X-Access-Token'] = token;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
    error.response = response;
    throw error;
  }
  
  return response;
};

export { TradingAuthError };

const tradingAuthUtils = {
  handleTradingAccessError,
  apiRequest,
  getTradingAccessToken,
  setTradingAccessToken,
  clearTradingAccessToken,
  hasTradingAccess,
  fetchWithTradingAccess,
  TradingAuthError
};

export default tradingAuthUtils;
