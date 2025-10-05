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

describe('User Data Validation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
  });

  describe('setUser method', () => {
    test('stores valid user object', () => {
      const validUser = {
        id: '1',
        username: 'testuser',
        roles: ['customer'],
        status: 'active'
      };

      authService.setUser(validUser);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'user',
        JSON.stringify(validUser)
      );
    });

    test('handles null user gracefully', () => {
      authService.setUser(null);

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });

    test('handles undefined user gracefully', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      authService.setUser(undefined);

      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data provided to setUser:', undefined);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });

    test('handles non-object user data', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      authService.setUser('invalid-user-data');

      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data provided to setUser:', 'invalid-user-data');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });

    test('handles empty object user', () => {
      const emptyUser = {};
      
      authService.setUser(emptyUser);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'user',
        JSON.stringify(emptyUser)
      );
    });
  });

  describe('getStoredUser method', () => {
    test('retrieves valid user data', () => {
      const validUser = {
        id: '1',
        username: 'testuser',
        roles: ['customer'],
        status: 'active'
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(validUser));

      const result = authService.getStoredUser();

      expect(result).toEqual(validUser);
      expect(localStorageMock.getItem).toHaveBeenCalledWith('user');
    });

    test('handles missing user data', () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
    });

    test('handles "undefined" string in localStorage', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      localStorageMock.getItem.mockReturnValue('undefined');

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data format, clearing storage');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      consoleSpy.mockRestore();
    });

    test('handles "null" string in localStorage', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      localStorageMock.getItem.mockReturnValue('null');

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data format, clearing storage');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      consoleSpy.mockRestore();
    });

    test('handles invalid JSON in localStorage', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      localStorageMock.getItem.mockReturnValue('invalid-json');

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Error parsing stored user data:', expect.any(Error));
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      consoleSpy.mockRestore();
    });

    test('handles non-object parsed data', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      localStorageMock.getItem.mockReturnValue('"string-user-data"');

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data format, clearing storage');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      consoleSpy.mockRestore();
    });

    test('handles empty string in localStorage', () => {
      localStorageMock.getItem.mockReturnValue('');

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
    });

    test('handles numeric user data', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      localStorageMock.getItem.mockReturnValue('123');

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data format, clearing storage');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      consoleSpy.mockRestore();
    });

    test('handles boolean user data', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      
      localStorageMock.getItem.mockReturnValue('true');

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data format, clearing storage');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      consoleSpy.mockRestore();
    });
  });

  describe('Integration tests', () => {
    test('setUser and getStoredUser work together', () => {
      const user = {
        id: '1',
        username: 'testuser',
        roles: ['customer'],
        status: 'active'
      };

      // Set user
      authService.setUser(user);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(user));

      // Mock localStorage to return the stored data
      localStorageMock.getItem.mockReturnValue(JSON.stringify(user));

      // Get user
      const retrievedUser = authService.getStoredUser();
      expect(retrievedUser).toEqual(user);
    });

    test('handles corrupted data scenario', () => {
      // Simulate corrupted data in localStorage
      localStorageMock.getItem.mockReturnValue('{"id": "1", "username":}');

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      const result = authService.getStoredUser();

      expect(result).toBeNull();
      expect(consoleSpy).toHaveBeenCalledWith('Error parsing stored user data:', expect.any(Error));
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');

      consoleSpy.mockRestore();
    });

    test('handles multiple invalid data attempts', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      // Try multiple invalid data types
      authService.setUser(undefined);
      authService.setUser(null);
      authService.setUser('string');
      authService.setUser(123);
      authService.setUser(true);

      expect(consoleSpy).toHaveBeenCalledTimes(4); // null is handled differently
      expect(localStorageMock.removeItem).toHaveBeenCalledTimes(5);

      consoleSpy.mockRestore();
    });
  });

  describe('Edge cases', () => {
    test('handles user with nested objects', () => {
      const complexUser = {
        id: '1',
        username: 'testuser',
        roles: ['admin', 'agent'],
        preferences: {
          theme: 'dark',
          notifications: true
        },
        metadata: {
          lastLogin: '2024-01-01',
          loginCount: 5
        }
      };

      authService.setUser(complexUser);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(complexUser));

      localStorageMock.getItem.mockReturnValue(JSON.stringify(complexUser));
      const result = authService.getStoredUser();
      expect(result).toEqual(complexUser);
    });

    test('handles user with circular references', () => {
      const user = { id: '1', name: 'test' };
      user.self = user; // Create circular reference

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      authService.setUser(user);

      // Should handle circular reference gracefully
      expect(consoleSpy).toHaveBeenCalledWith('Invalid user data provided to setUser:', expect.any(Object));
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');

      consoleSpy.mockRestore();
    });

    test('handles very large user objects', () => {
      const largeUser = {
        id: '1',
        username: 'testuser',
        data: new Array(10000).fill('test-data')
      };

      authService.setUser(largeUser);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(largeUser));

      localStorageMock.getItem.mockReturnValue(JSON.stringify(largeUser));
      const result = authService.getStoredUser();
      expect(result).toEqual(largeUser);
    });
  });
});
