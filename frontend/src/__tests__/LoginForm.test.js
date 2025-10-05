/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginForm from '../components/Auth/LoginForm';
import { AuthProvider } from '../contexts/AuthContext';
import * as authService from '../services/authService';

// Mock the auth service
jest.mock('../services/authService');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/login' })
}));

// Mock toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn()
}));

const MockedLoginForm = () => (
  <AuthProvider>
    <LoginForm />
  </AuthProvider>
);

describe('LoginForm Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear localStorage
    localStorage.clear();
  });

  test('renders login form without crashing', () => {
    render(<MockedLoginForm />);
    expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
  });

  test('displays all form elements', () => {
    render(<MockedLoginForm />);
    
    expect(screen.getByPlaceholderText(/username or email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByRole('checkbox', { name: /remember me/i })).toBeInTheDocument();
  });

  test('handles form input changes', () => {
    render(<MockedLoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/username or email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    
    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('testpass');
  });

  test('handles successful single-role login', async () => {
    const mockLoginResponse = {
      success: true,
      user: {
        id: '1',
        username: 'testuser',
        roles: ['customer'],
        primary_role: 'customer',
        has_multiple_roles: false,
        status: 'active'
      }
    };

    authService.login.mockResolvedValue(mockLoginResponse);

    render(<MockedLoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/username or email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith('testuser', 'testpass', false);
    });
  });

  test('handles successful multi-role login and shows role selection', async () => {
    const mockLoginResponse = {
      success: true,
      user: {
        id: '1',
        username: 'testuser',
        roles: ['admin', 'agent'],
        primary_role: null,
        has_multiple_roles: true,
        status: 'active'
      }
    };

    authService.login.mockResolvedValue(mockLoginResponse);

    render(<MockedLoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/username or email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/select your role/i)).toBeInTheDocument();
    });

    // Check if role options are displayed
    expect(screen.getByText(/admin/i)).toBeInTheDocument();
    expect(screen.getByText(/agent/i)).toBeInTheDocument();
  });

  test('handles login failure', async () => {
    const mockLoginResponse = {
      success: false,
      error: 'Invalid credentials'
    };

    authService.login.mockResolvedValue(mockLoginResponse);

    render(<MockedLoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/username or email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith('testuser', 'wrongpass', false);
    });
  });

  test('handles role selection', async () => {
    const mockLoginResponse = {
      success: true,
      user: {
        id: '1',
        username: 'testuser',
        roles: ['admin', 'agent'],
        primary_role: null,
        has_multiple_roles: true,
        status: 'active'
      }
    };

    authService.login.mockResolvedValue(mockLoginResponse);

    render(<MockedLoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/username or email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/select your role/i)).toBeInTheDocument();
    });

    // Select admin role
    const adminButton = screen.getByText(/admin/i);
    fireEvent.click(adminButton);
    
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalled();
    });
  });

  test('validates required fields', async () => {
    render(<MockedLoginForm />);
    
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(submitButton);
    
    // Form should not submit without required fields
    expect(authService.login).not.toHaveBeenCalled();
  });

  test('handles remember me checkbox', () => {
    render(<MockedLoginForm />);
    
    const rememberCheckbox = screen.getByRole('checkbox', { name: /remember me/i });
    expect(rememberCheckbox.checked).toBe(false);
    
    fireEvent.click(rememberCheckbox);
    expect(rememberCheckbox.checked).toBe(true);
  });

  test('shows loading state during login', async () => {
    const mockLoginResponse = {
      success: true,
      user: {
        id: '1',
        username: 'testuser',
        roles: ['customer'],
        primary_role: 'customer',
        has_multiple_roles: false,
        status: 'active'
      }
    };

    // Mock a delayed response
    authService.login.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve(mockLoginResponse), 100))
    );

    render(<MockedLoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/username or email/i);
    const passwordInput = screen.getByPlaceholderText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'testpass' } });
    fireEvent.click(submitButton);
    
    // Check if button shows loading state
    expect(submitButton).toBeDisabled();
    
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });
});
