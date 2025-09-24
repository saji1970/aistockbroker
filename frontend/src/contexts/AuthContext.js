import React, { createContext, useContext, useReducer, useEffect } from 'react';
import authService from '../services/authService';

// Auth context
const AuthContext = createContext();

// Auth actions
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  UPDATE_USER: 'UPDATE_USER',
  SET_LOADING: 'SET_LOADING'
};

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
};

// Auth reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      };

    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: action.payload
      };

    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };

    default:
      return state;
  }
};

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });

      // Check if user is already authenticated
      const isAuthenticated = authService.isAuthenticated();

      if (isAuthenticated) {
        try {
          // Verify session with server
          const isValid = await authService.verifySession();

          if (isValid) {
            const user = authService.getUser();
            dispatch({ type: AUTH_ACTIONS.LOGIN_SUCCESS, payload: user });
          } else {
            // Session is invalid, logout
            await logout();
          }
        } catch (error) {
          // If verification fails, just logout silently
          console.warn('Session verification failed:', error.message);
          await logout();
        }
      } else {
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
    }
  };

  const login = async (emailOrUsername, password, rememberMe = false) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });

      const result = await authService.login(emailOrUsername, password, rememberMe);

      if (result.success) {
        dispatch({ type: AUTH_ACTIONS.LOGIN_SUCCESS, payload: result.user });
        return result;
      } else {
        dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE, payload: result.error });
        return result;
      }
    } catch (error) {
      const errorMessage = 'Login failed. Please try again.';
      dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE, payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });

      const result = await authService.register(userData);

      if (result.success) {
        // Note: Registration doesn't automatically log the user in
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        return result;
      } else {
        dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE, payload: result.error });
        return result;
      }
    } catch (error) {
      const errorMessage = 'Registration failed. Please try again.';
      dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE, payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  const logout = async (logoutAll = false) => {
    try {
      await authService.logout(logoutAll);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  const updateUser = (userData) => {
    dispatch({ type: AUTH_ACTIONS.UPDATE_USER, payload: userData });
  };

  const refreshUser = async () => {
    try {
      const result = await authService.getCurrentUser();
      if (result.success) {
        dispatch({ type: AUTH_ACTIONS.UPDATE_USER, payload: result.user });
        return result;
      }
      return result;
    } catch (error) {
      console.error('Refresh user error:', error);
      return { success: false, error: 'Failed to refresh user data' };
    }
  };

  // Helper functions
  const isAdmin = () => {
    return state.user?.role === 'admin';
  };

  const isActive = () => {
    return state.user?.status === 'active';
  };

  const canAccessTrading = () => {
    return isActive() && (state.user?.role === 'user' || state.user?.role === 'admin');
  };

  const hasRole = (role) => {
    return state.user?.role === role;
  };

  const hasAnyRole = (roles) => {
    return roles.includes(state.user?.role);
  };

  const value = {
    // State
    ...state,

    // Actions
    login,
    register,
    logout,
    updateUser,
    refreshUser,

    // Helper functions
    isAdmin,
    isActive,
    canAccessTrading,
    hasRole,
    hasAnyRole
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};

export default AuthContext;