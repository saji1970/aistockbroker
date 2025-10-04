import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { EyeIcon, EyeSlashIcon, UserIcon, UserGroupIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';

const LoginForm = ({ onSuccess, redirectTo = null }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    emailOrUsername: '',
    password: '',
    rememberMe: false,
    role: searchParams.get('role') || ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [availableRoles, setAvailableRoles] = useState([]);
  const [showRoleSelection, setShowRoleSelection] = useState(false);
  const [loginResult, setLoginResult] = useState(null);

  const allRoleOptions = [
    { value: 'customer', label: 'Individual Investor', icon: UserIcon, description: 'Access AI predictions and portfolio management' },
    { value: 'user', label: 'Individual Investor', icon: UserIcon, description: 'Access AI predictions and portfolio management' },
    { value: 'agent', label: 'Financial Agent', icon: UserGroupIcon, description: 'Manage multiple clients and provide recommendations' },
    { value: 'admin', label: 'Administrator', icon: ShieldCheckIcon, description: 'Full system access and user management' }
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.emailOrUsername.trim()) {
      newErrors.emailOrUsername = 'Email or username is required';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(
        formData.emailOrUsername,
        formData.password,
        formData.rememberMe
      );

      if (result.success) {
        // Check if user has multiple roles
        const userRoles = result.user?.roles || [result.user?.role];

        if (userRoles.length > 1) {
          // Show role selection if user has multiple roles
          setLoginResult(result);
          setAvailableRoles(userRoles);
          setShowRoleSelection(true);
          setIsLoading(false);
          toast.success('Please select your role to continue');
        } else {
          // Single role - proceed with login
          const selectedRole = userRoles[0];
          completeLogin(result, selectedRole);
        }
      } else {
        setErrors({ general: result.error });
        toast.error(result.error);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = 'An unexpected error occurred. Please try again.';
      setErrors({ general: errorMessage });
      toast.error(errorMessage);
      setIsLoading(false);
    }
  };

  const completeLogin = (result, selectedRole) => {
    toast.success(result.message || 'Login successful!');

    if (onSuccess) {
      onSuccess({ ...result.user, selectedRole });
    } else {
      // Role-based redirection
      let targetRoute = '/dashboard'; // Default fallback

      if (redirectTo) {
        targetRoute = redirectTo;
      } else {
        // Redirect based on selected role
        switch (selectedRole) {
          case 'admin':
            targetRoute = '/admin';
            break;
          case 'agent':
            targetRoute = '/agent/dashboard';
            break;
          case 'customer':
          case 'user':
          default:
            targetRoute = '/dashboard';
            break;
        }
      }

      // Small delay to allow auth state to update before navigation
      setTimeout(() => {
        navigate(targetRoute, { replace: true });
      }, 100);
    }
  };

  const handleRoleSelect = (role) => {
    setFormData(prev => ({ ...prev, role }));
    completeLogin(loginResult, role);
  };

  // If showing role selection
  if (showRoleSelection) {
    const roleOptions = allRoleOptions.filter(opt => availableRoles.includes(opt.value));

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
              Select Your Role
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Choose how you want to access the platform
            </p>
          </div>

          <div className="mt-8 space-y-3">
            {roleOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => handleRoleSelect(option.value)}
                className="relative flex items-center w-full p-4 border rounded-lg cursor-pointer hover:bg-indigo-50 hover:border-indigo-500 transition-all border-gray-300"
              >
                <option.icon className="h-8 w-8 text-indigo-600 mr-4" />
                <div className="text-left flex-1">
                  <div className="text-lg font-medium text-gray-900">
                    {option.label}
                  </div>
                  <div className="text-sm text-gray-500">
                    {option.description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link
              to="/register"
              className="font-medium text-indigo-600 hover:text-indigo-500"
            >
              create a new account
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="emailOrUsername" className="block text-sm font-medium text-gray-700">
                Email or Username
              </label>
              <input
                id="emailOrUsername"
                name="emailOrUsername"
                type="text"
                required
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border rounded-md placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm ${
                  errors.emailOrUsername ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Email or username"
                value={formData.emailOrUsername}
                onChange={handleChange}
                disabled={isLoading}
              />
              {errors.emailOrUsername && (
                <p className="mt-1 text-sm text-red-600">{errors.emailOrUsername}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  className={`appearance-none relative block w-full px-3 py-2 pr-10 border rounded-md placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm ${
                    errors.password ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="rememberMe"
                name="rememberMe"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                checked={formData.rememberMe}
                onChange={handleChange}
                disabled={isLoading}
              />
              <label htmlFor="rememberMe" className="ml-2 block text-sm text-gray-900">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <Link
                to="/forgot-password"
                className="font-medium text-indigo-600 hover:text-indigo-500"
              >
                Forgot your password?
              </Link>
            </div>
          </div>

          {errors.general && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{errors.general}</p>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Signing in...
                </div>
              ) : (
                'Sign in'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginForm;