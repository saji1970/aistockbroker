/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import * as authService from '../services/authService';

// Mock the auth service
jest.mock('../services/authService');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' })
}));

// Test component that uses the auth context
const TestComponent = () => {
  const { user, isAuthenticated, isAdmin, canAccessTrading, login, logout } = useAuth();
  
  return (
    <div>
      <div data-testid="user">{user ? user.username : 'No user'}</div>
      <div data-testid="authenticated">{isAuthenticated ? 'true' : 'false'}</div>
      <div data-testid="admin">{isAdmin() ? 'true' : 'false'}</div>
      <div data-testid="trading">{canAccessTrading() ? 'true' : 'false'}</div>
      <button onClick={() => login('testuser', 'password')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('provides initial state correctly', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('user')).toHaveTextContent('No user');
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('admin')).toHaveTextContent('false');
    expect(screen.getByTestId('trading')).toHaveTextContent('false');
  });

  test('handles successful login', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      primary_role: 'customer',
      status: 'active'
    };

    authService.login.mockResolvedValue({
      success: true,
      user: mockUser
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    
    await act(async () => {
      fireEvent.click(loginButton);
    });

    expect(authService.login).toHaveBeenCalledWith('testuser', 'password', false);
  });

  test('handles login failure', async () => {
    authService.login.mockResolvedValue({
      success: false,
      error: 'Invalid credentials'
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    
    await act(async () => {
      fireEvent.click(loginButton);
    });

    expect(authService.login).toHaveBeenCalledWith('testuser', 'password', false);
    // User should remain unauthenticated
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  test('handles logout', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      primary_role: 'customer',
      status: 'active'
    };

    // Mock initial authenticated state
    authService.getStoredUser.mockReturnValue(mockUser);
    authService.getToken.mockReturnValue('mock-token');

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const logoutButton = screen.getByText('Logout');
    
    await act(async () => {
      fireEvent.click(logoutButton);
    });

    expect(authService.clearAuthData).toHaveBeenCalled();
  });

  test('isAdmin returns true for admin users', async () => {
    const mockAdminUser = {
      id: '1',
      username: 'admin',
      roles: ['admin'],
      primary_role: 'admin',
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockAdminUser);
    authService.getToken.mockReturnValue('mock-token');

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('admin')).toHaveTextContent('true');
    });
  });

  test('canAccessTrading returns true for valid roles', async () => {
    const mockAgentUser = {
      id: '1',
      username: 'agent',
      roles: ['agent'],
      primary_role: 'agent',
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockAgentUser);
    authService.getToken.mockReturnValue('mock-token');

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('trading')).toHaveTextContent('true');
    });
  });

  test('handles role selection for multi-role users', async () => {
    const mockMultiRoleUser = {
      id: '1',
      username: 'saji',
      roles: ['admin', 'agent'],
      primary_role: null,
      selectedRole: 'admin',
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockMultiRoleUser);
    authService.getToken.mockReturnValue('mock-token');

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('admin')).toHaveTextContent('true');
      expect(screen.getByTestId('trading')).toHaveTextContent('true');
    });
  });

  test('handles user status checking', async () => {
    const mockInactiveUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      primary_role: 'customer',
      status: 'inactive'
    };

    authService.getStoredUser.mockReturnValue(mockInactiveUser);
    authService.getToken.mockReturnValue('mock-token');

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('trading')).toHaveTextContent('false');
    });
  });

  test('updates selected role for multi-role users', async () => {
    const mockMultiRoleUser = {
      id: '1',
      username: 'saji',
      roles: ['admin', 'agent'],
      primary_role: null,
      selectedRole: 'agent',
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockMultiRoleUser);
    authService.getToken.mockReturnValue('mock-token');

    const TestComponentWithRoleSwitch = () => {
      const { updateSelectedRole, isAdmin, canAccessTrading } = useAuth();
      
      return (
        <div>
          <div data-testid="admin">{isAdmin() ? 'true' : 'false'}</div>
          <div data-testid="trading">{canAccessTrading() ? 'true' : 'false'}</div>
          <button onClick={() => updateSelectedRole('admin')}>Switch to Admin</button>
        </div>
      );
    };

    render(
      <AuthProvider>
        <TestComponentWithRoleSwitch />
      </AuthProvider>
    );

    // Initially should show agent role (trading access but not admin)
    await waitFor(() => {
      expect(screen.getByTestId('admin')).toHaveTextContent('false');
      expect(screen.getByTestId('trading')).toHaveTextContent('true');
    });

    // Switch to admin role
    const switchButton = screen.getByText('Switch to Admin');
    
    await act(async () => {
      fireEvent.click(switchButton);
    });

    // Should now show admin role
    await waitFor(() => {
      expect(screen.getByTestId('admin')).toHaveTextContent('true');
    });

    expect(authService.setUser).toHaveBeenCalled();
  });
});
