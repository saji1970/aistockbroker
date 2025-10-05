/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProtectedRoute from '../components/Auth/ProtectedRoute';
import { AuthProvider } from '../contexts/AuthContext';
import * as authService from '../services/authService';

// Mock the auth service
jest.mock('../services/authService');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/protected' })
}));

// Mock toast
jest.mock('react-hot-toast', () => ({
  error: jest.fn()
}));

const TestComponent = () => <div>Protected Content</div>;

const MockedProtectedRoute = ({ children, requiredRole, requiredStatus, requireTradingAccess }) => (
  <AuthProvider>
    <ProtectedRoute 
      requiredRole={requiredRole}
      requiredStatus={requiredStatus}
      requireTradingAccess={requireTradingAccess}
    >
      {children}
    </ProtectedRoute>
  </AuthProvider>
);

describe('ProtectedRoute Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders children for authenticated active user', () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);

    render(
      <MockedProtectedRoute>
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('does not render children for unauthenticated user', () => {
    authService.getStoredUser.mockReturnValue(null);
    authService.getToken.mockReturnValue(null);

    render(
      <MockedProtectedRoute>
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('does not render children for inactive user', () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      status: 'inactive'
    };

    authService.getStoredUser.mockReturnValue(mockUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(false);

    render(
      <MockedProtectedRoute>
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('checks required role correctly', () => {
    const mockAdminUser = {
      id: '1',
      username: 'admin',
      roles: ['admin'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockAdminUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);

    // Admin user accessing admin route
    render(
      <MockedProtectedRoute requiredRole="admin">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('blocks access for insufficient role', () => {
    const mockCustomerUser = {
      id: '1',
      username: 'customer',
      roles: ['customer'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockCustomerUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);

    // Customer user trying to access admin route
    render(
      <MockedProtectedRoute requiredRole="admin">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('allows access for users with multiple roles', () => {
    const mockMultiRoleUser = {
      id: '1',
      username: 'saji',
      roles: ['admin', 'agent'],
      selectedRole: 'admin',
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockMultiRoleUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);

    render(
      <MockedProtectedRoute requiredRole="admin">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('checks trading access requirement', () => {
    const mockAgentUser = {
      id: '1',
      username: 'agent',
      roles: ['agent'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockAgentUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);
    authService.canAccessTrading.mockReturnValue(true);

    render(
      <MockedProtectedRoute requireTradingAccess={true}>
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('blocks access when trading access required but not available', () => {
    const mockCustomerUser = {
      id: '1',
      username: 'customer',
      roles: ['customer'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockCustomerUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);
    authService.canAccessTrading.mockReturnValue(false);

    render(
      <MockedProtectedRoute requireTradingAccess={true}>
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('checks required status correctly', () => {
    const mockActiveUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockActiveUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);

    render(
      <MockedProtectedRoute requiredStatus="active">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('blocks access for wrong status', () => {
    const mockPendingUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      status: 'pending'
    };

    authService.getStoredUser.mockReturnValue(mockPendingUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(false);

    render(
      <MockedProtectedRoute requiredStatus="active">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('handles missing token gracefully', () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockUser);
    authService.getToken.mockReturnValue(null);

    render(
      <MockedProtectedRoute>
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('handles expired token', () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      roles: ['customer'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockUser);
    authService.getToken.mockReturnValue('expired_token');
    authService.isActive.mockReturnValue(false);

    render(
      <MockedProtectedRoute>
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('handles multiple requirements', () => {
    const mockAdminUser = {
      id: '1',
      username: 'admin',
      roles: ['admin'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockAdminUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);
    authService.canAccessTrading.mockReturnValue(true);

    render(
      <MockedProtectedRoute 
        requiredRole="admin" 
        requiredStatus="active" 
        requireTradingAccess={true}
      >
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('blocks access when any requirement fails', () => {
    const mockCustomerUser = {
      id: '1',
      username: 'customer',
      roles: ['customer'],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockCustomerUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);
    authService.canAccessTrading.mockReturnValue(false);

    render(
      <MockedProtectedRoute 
        requiredRole="admin" 
        requiredStatus="active" 
        requireTradingAccess={true}
      >
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('renders loading state initially', () => {
    // Mock initial loading state
    authService.getStoredUser.mockReturnValue(null);
    authService.getToken.mockReturnValue(null);

    render(
      <MockedProtectedRoute>
        <TestComponent />
      </MockedProtectedRoute>
    );

    // Should not render content while loading
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('handles role switching for multi-role users', () => {
    const mockMultiRoleUser = {
      id: '1',
      username: 'saji',
      roles: ['admin', 'agent'],
      selectedRole: 'agent',
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockMultiRoleUser);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);

    // Should allow access with selected role
    render(
      <MockedProtectedRoute requiredRole="agent">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();

    // Should block access for different role
    render(
      <MockedProtectedRoute requiredRole="customer">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('handles edge case with empty roles array', () => {
    const mockUserWithNoRoles = {
      id: '1',
      username: 'testuser',
      roles: [],
      status: 'active'
    };

    authService.getStoredUser.mockReturnValue(mockUserWithNoRoles);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(true);

    render(
      <MockedProtectedRoute requiredRole="customer">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  test('handles user without status field', () => {
    const mockUserWithoutStatus = {
      id: '1',
      username: 'testuser',
      roles: ['customer']
      // No status field
    };

    authService.getStoredUser.mockReturnValue(mockUserWithoutStatus);
    authService.getToken.mockReturnValue('demo_token_123');
    authService.isActive.mockReturnValue(false);

    render(
      <MockedProtectedRoute requiredStatus="active">
        <TestComponent />
      </MockedProtectedRoute>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
});
