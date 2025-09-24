/**
 * @jest-environment jsdom
 */

import { 
  handleTradingAccessError, 
  getTradingAccessToken, 
  setTradingAccessToken,
  clearTradingAccessToken,
  hasTradingAccess,
  TradingAuthError 
} from '../tradingAuth';

// Mock fetch
global.fetch = jest.fn();

describe('Trading Auth Utilities', () => {
  beforeEach(() => {
    localStorage.clear();
    fetch.mockClear();
  });

  test('handleTradingAccessError handles trading access denied', () => {
    const mockNavigate = jest.fn();
    const error = {
      response: {
        data: {
          error: 'Trading Access Denied',
          message: 'You need proper credentials'
        }
      }
    };

    const result = handleTradingAccessError(error, mockNavigate);

    expect(result).toBe(true);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('trading_access_token')).toBeNull();
  });

  test('handleTradingAccessError handles 401 errors', () => {
    const mockNavigate = jest.fn();
    const error = {
      response: {
        status: 401
      }
    };

    const result = handleTradingAccessError(error, mockNavigate);

    expect(result).toBe(true);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  test('handleTradingAccessError handles 403 errors', () => {
    const mockNavigate = jest.fn();
    const error = {
      response: {
        status: 403
      }
    };

    const result = handleTradingAccessError(error, mockNavigate);

    expect(result).toBe(true);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  test('handleTradingAccessError does not handle other errors', () => {
    const mockNavigate = jest.fn();
    const error = {
      response: {
        status: 500,
        data: { error: 'Server Error' }
      }
    };

    const result = handleTradingAccessError(error, mockNavigate);

    expect(result).toBe(false);
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('getTradingAccessToken returns token from localStorage', async () => {
    localStorage.setItem('trading_access_token', 'test_token');
    
    const token = await getTradingAccessToken();
    
    expect(token).toBe('test_token');
  });

  test('getTradingAccessToken fetches from API when not in localStorage', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_tokens: {
          trader: 'api_token_123'
        }
      })
    });

    const token = await getTradingAccessToken();

    expect(token).toBe('api_token_123');
    expect(localStorage.getItem('trading_access_token')).toBe('api_token_123');
  });

  test('setTradingAccessToken stores token', () => {
    setTradingAccessToken('test_token');
    
    expect(localStorage.getItem('trading_access_token')).toBe('test_token');
  });

  test('clearTradingAccessToken removes token', () => {
    localStorage.setItem('trading_access_token', 'test_token');
    clearTradingAccessToken();
    
    expect(localStorage.getItem('trading_access_token')).toBeNull();
  });

  test('hasTradingAccess returns true when token exists', () => {
    localStorage.setItem('trading_access_token', 'test_token');
    
    expect(hasTradingAccess()).toBe(true);
  });

  test('hasTradingAccess returns false when no token', () => {
    expect(hasTradingAccess()).toBe(false);
  });

  test('TradingAuthError creates error with correct properties', () => {
    const error = new TradingAuthError('Test message', 403, 'TEST_CODE');
    
    expect(error.message).toBe('Test message');
    expect(error.status).toBe(403);
    expect(error.code).toBe('TEST_CODE');
    expect(error.name).toBe('TradingAuthError');
  });
});
