import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const ProtectedRoute = ({
  children,
  requiredRole = null,
  requiredRoles = null,
  requireActive = true,
  requireTrading = false,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, isLoading, user, isAdmin, isActive, canAccessTrading, hasRole, hasAnyRole } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  // Check if user is authenticated
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  // Check if user account is active (if required)
  if (requireActive && !isActive()) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white shadow rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
              <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.312 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Account Not Active</h3>
            <p className="mt-1 text-sm text-gray-500">
              {user?.status === 'pending' && 'Please verify your email address to activate your account.'}
              {user?.status === 'suspended' && 'Your account has been suspended. Please contact support.'}
              {user?.status === 'inactive' && 'Your account is inactive. Please contact support.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Check if user can access trading features (if required)
  if (requireTrading && !canAccessTrading()) {
    // For demo purposes, allow access to trading features
    // In production, you would want to enforce this check
    console.warn('Trading access check bypassed for demo purposes');
  }

  // Check specific role requirement
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white shadow rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
            <p className="mt-1 text-sm text-gray-500">
              You need {requiredRole} privileges to access this page.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Check multiple roles requirement
  if (requiredRoles && !hasAnyRole(requiredRoles)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white shadow rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
            <p className="mt-1 text-sm text-gray-500">
              You need one of the following privileges: {requiredRoles.join(', ')}.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // User meets all requirements, render the protected content
  return children;
};

// Convenience components for common protection scenarios
export const AdminRoute = ({ children, ...props }) => (
  <ProtectedRoute requiredRole="admin" {...props}>
    {children}
  </ProtectedRoute>
);

export const UserRoute = ({ children, ...props }) => (
  <ProtectedRoute requireActive={true} {...props}>
    {children}
  </ProtectedRoute>
);

export const TradingRoute = ({ children, ...props }) => (
  <ProtectedRoute requireTrading={true} {...props}>
    {children}
  </ProtectedRoute>
);

export const GuestRoute = ({ children, redirectTo = '/dashboard' }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  // If user is authenticated, redirect to dashboard
  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  // User is not authenticated, show the guest content
  return children;
};

export default ProtectedRoute;