/**
 * Trading Access Hook
 * Provides trading access functionality and error handling
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  getTradingAccessToken, 
  setTradingAccessToken, 
  clearTradingAccessToken,
  hasTradingAccess,
  handleTradingAccessError 
} from '../utils/tradingAuth';

export const useTradingAccess = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [hasAccess, setHasAccess] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Check trading access on mount
  useEffect(() => {
    const checkAccess = async () => {
      setIsLoading(true);
      try {
        const token = await getTradingAccessToken();
        setHasAccess(!!token);
        setError(null);
      } catch (err) {
        setError(err);
        setHasAccess(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAccess();
  }, []);

  // Handle trading access errors
  const handleError = useCallback((error) => {
    if (handleTradingAccessError(error, navigate)) {
      setHasAccess(false);
      setError(error);
      return true; // Error was handled
    }
    return false; // Error was not handled
  }, [navigate]);

  // Request trading access
  const requestAccess = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = await getTradingAccessToken();
      if (token) {
        setTradingAccessToken(token);
        setHasAccess(true);
        return token;
      } else {
        throw new Error('Unable to obtain trading access token');
      }
    } catch (err) {
      setError(err);
      setHasAccess(false);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Clear trading access
  const clearAccess = useCallback(() => {
    clearTradingAccessToken();
    setHasAccess(false);
    setError(null);
  }, []);

  // Enhanced API request with trading access
  const apiRequest = useCallback(async (requestFn) => {
    try {
      // Ensure we have trading access
      if (!hasAccess) {
        await requestAccess();
      }
      
      return await requestFn();
    } catch (error) {
      if (handleError(error)) {
        throw error;
      }
      throw error;
    }
  }, [hasAccess, requestAccess, handleError]);

  return {
    isLoading,
    hasAccess,
    error,
    requestAccess,
    clearAccess,
    handleError,
    apiRequest
  };
};

export default useTradingAccess;
