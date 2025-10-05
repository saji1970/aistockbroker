/**
 * @jest-environment jsdom
 */

import { authService } from '../services/authService';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock fetch for API calls
global.fetch = jest.fn();

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    fetch.mockClear();
  });

  describe('Token Management', () => {
    test('stores and retrieves tokens correctly', () => {
      const token = 'demo_token_123';
      const refreshToken = 'demo_refresh_token_456';

      authService.setToken(token);
      authService.setRefreshToken(refreshToken);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', token);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', refreshToken);

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return token;
        if (key === 'refresh_token') return refreshToken;
        return null;
      });

      expect(authService.getToken()).toBe(token);
      expect(authService.getRefreshToken()).toBe(refreshToken);
    });

    test('clears tokens correctly', () => {
      authService.clearAuthData();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
    });

    test('handles invalid token lengths', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      // Test short tokens
      authService.setToken('short');
      authService.setRefreshToken('tiny');

      authService.clearInvalidTokens();

      expect(consoleSpy).toHaveBeenCalledWith('Token appears to be invalid (too short), clearing auth data');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');

      consoleSpy.mockRestore();
    });

    test('accepts demo tokens with appropriate length', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      // Test demo tokens (should be accepted)
      authService.setToken('demo_token_123');
      authService.setRefreshToken('demo_refresh_token_456');

      authService.clearInvalidTokens();

      expect(consoleSpy).not.toHaveBeenCalled();
      expect(localStorageMock.removeItem).not.toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });

  describe('JWT Token Validation', () => {
    test('validates JWT tokens correctly', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      // Create a valid JWT token (expires in future)
      const futureTime = Math.floor(Date.now() / 1000) + 3600; // 1 hour from now
      const payload = { exp: futureTime, sub: 'testuser' };
      const header = { alg: 'HS256', typ: 'JWT' };
      
      const encodedHeader = btoa(JSON.stringify(header));
      const encodedPayload = btoa(JSON.stringify(payload));
      const validJWT = `${encodedHeader}.${encodedPayload}.signature`;

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return validJWT;
        if (key === 'refresh_token') return 'demo_refresh_token_456';
        return null;
      });

      authService.checkTokenValidity();

      expect(consoleSpy).not.toHaveBeenCalled();
      expect(localStorageMock.removeItem).not.toHaveBeenCalled();

      consoleSpy.mockRestore();
    });

    test('handles expired JWT tokens', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      // Create an expired JWT token
      const pastTime = Math.floor(Date.now() / 1000) - 3600; // 1 hour ago
      const payload = { exp: pastTime, sub: 'testuser' };
      const header = { alg: 'HS256', typ: 'JWT' };
      
      const encodedHeader = btoa(JSON.stringify(header));
      const encodedPayload = btoa(JSON.stringify(payload));
      const expiredJWT = `${encodedHeader}.${encodedPayload}.signature`;

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return expiredJWT;
        if (key === 'refresh_token') return 'demo_refresh_token_456';
        return null;
      });

      authService.checkTokenValidity();

      expect(consoleSpy).toHaveBeenCalledWith('Token is expired or about to expire, clearing auth data');
      expect(localStorageMock.removeItem).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });

    test('handles non-JWT tokens gracefully', () => {
      const consoleSpy = jest.spyOn(console, 'debug').mockImplementation();

      // Test demo tokens (non-JWT)
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return 'demo_token_123';
        if (key === 'refresh_token') return 'demo_refresh_token_456';
        return null;
      });

      authService.checkTokenValidity();

      expect(consoleSpy).toHaveBeenCalledWith('Non-JWT token detected, skipping expiration check');
      expect(localStorageMock.removeItem).not.toHaveBeenCalled();

      consoleSpy.mockRestore();
    });

    test('handles malformed JWT tokens', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      // Test malformed JWT
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return 'malformed.jwt';
        if (key === 'refresh_token') return 'demo_refresh_token_456';
        return null;
      });

      authService.checkTokenValidity();

      expect(consoleSpy).toHaveBeenCalledWith('Invalid token format, clearing auth data');
      expect(localStorageMock.removeItem).toHaveBeenCalled();

      consoleSpy.mockRestore();
    });
  });

  describe('Login Functionality', () => {
    test('handles successful login', async () => {
      const mockResponse = {
        success: true,
        user: {
          id: '1',
          username: 'testuser',
          roles: ['customer'],
          status: 'active'
        },
        token: 'demo_token_123',
        refresh_token: 'demo_refresh_token_456'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.login('testuser', 'password');

      expect(result).toEqual(mockResponse);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'demo_token_123');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'demo_refresh_token_456');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.user));
    });

    test('handles login failure', async () => {
      const mockResponse = {
        success: false,
        message: 'Invalid credentials'
      };

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => mockResponse
      });

      const result = await authService.login('testuser', 'wrongpassword');

      expect(result).toEqual({
        success: false,
        error: 'Invalid credentials'
      });
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });

    test('handles network errors during login', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await authService.login('testuser', 'password');

      expect(result).toEqual({
        success: false,
        error: 'Login failed. Please try again.'
      });
    });

    test('includes remember me parameter in login', async () => {
      const mockResponse = {
        success: true,
        user: { id: '1', username: 'testuser' },
        token: 'demo_token_123',
        refresh_token: 'demo_refresh_token_456'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      await authService.login('testuser', 'password', true);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            email_or_username: 'testuser',
            password: 'password',
            remember_me: true
          })
        })
      );
    });
  });

  describe('Token Refresh', () => {
    test('refreshes token successfully', async () => {
      const mockResponse = {
        success: true,
        token: 'new_demo_token_789',
        refresh_token: 'new_demo_refresh_token_101112'
      };

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'refresh_token') return 'demo_refresh_token_456';
        return null;
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.refreshAuthToken();

      expect(result).toEqual(mockResponse);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'new_demo_token_789');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'new_demo_refresh_token_101112');
    });

    test('handles token refresh failure', async () => {
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'refresh_token') return 'invalid_refresh_token';
        return null;
      });

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ success: false, message: 'Invalid refresh token' })
      });

      const result = await authService.refreshAuthToken();

      expect(result).toEqual({
        success: false,
        error: 'Token refresh failed'
      });
      expect(localStorageMock.removeItem).toHaveBeenCalled();
    });

    test('handles missing refresh token', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = await authService.refreshAuthToken();

      expect(result).toEqual({
        success: false,
        error: 'No refresh token available'
      });
      expect(fetch).not.toHaveBeenCalled();
    });
  });

  describe('Session Verification', () => {
    test('verifies session successfully', async () => {
      const mockUser = {
        id: '1',
        username: 'testuser',
        roles: ['customer'],
        status: 'active'
      };

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return 'demo_token_123';
        return null;
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, user: mockUser })
      });

      const result = await authService.verifySession();

      expect(result).toEqual({ success: true, user: mockUser });
    });

    test('handles session verification failure', async () => {
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return 'invalid_token';
        return null;
      });

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ success: false, message: 'Invalid session' })
      });

      const result = await authService.verifySession();

      expect(result).toEqual({
        success: false,
        error: 'Session verification failed'
      });
    });

    test('handles missing token for session verification', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = await authService.verifySession();

      expect(result).toEqual({
        success: false,
        error: 'No token available'
      });
      expect(fetch).not.toHaveBeenCalled();
    });
  });

  describe('User Status Checking', () => {
    test('returns true for active users', () => {
      const activeUser = {
        id: '1',
        username: 'testuser',
        status: 'active'
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(activeUser));

      expect(authService.isActive()).toBe(true);
    });

    test('returns false for inactive users', () => {
      const inactiveUser = {
        id: '1',
        username: 'testuser',
        status: 'inactive'
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(inactiveUser));

      expect(authService.isActive()).toBe(false);
    });

    test('returns false for users with no status', () => {
      const userWithoutStatus = {
        id: '1',
        username: 'testuser'
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(userWithoutStatus));

      expect(authService.isActive()).toBe(false);
    });

    test('returns false when no user data', () => {
      localStorageMock.getItem.mockReturnValue(null);

      expect(authService.isActive()).toBe(false);
    });
  });

  describe('Error Handling', () => {
    test('handles JSON parsing errors', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });

      const result = await authService.login('testuser', 'password');

      expect(result).toEqual({
        success: false,
        error: 'Login failed. Please try again.'
      });
    });

    test('handles fetch timeouts', async () => {
      fetch.mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      const result = await authService.login('testuser', 'password');

      expect(result).toEqual({
        success: false,
        error: 'Login failed. Please try again.'
      });
    });
  });
});
