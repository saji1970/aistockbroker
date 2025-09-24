/**
 * Trading Access Handler Component
 * Handles trading access errors and automatic logout
 */

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { handleTradingAccessError } from '../utils/tradingAuth';

const TradingAccessHandler = ({ children }) => {
  const navigate = useNavigate();

  useEffect(() => {
    // Global error handler for trading access errors
    const handleGlobalError = (event) => {
      if (event.error && event.error.name === 'TradingAuthError') {
        handleTradingAccessError(event.error, navigate);
      }
    };

    // Handle unhandled promise rejections
    const handleUnhandledRejection = (event) => {
      if (event.reason && event.reason.name === 'TradingAuthError') {
        handleTradingAccessError(event.reason, navigate);
      }
    };

    // Add event listeners
    window.addEventListener('error', handleGlobalError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    // Cleanup
    return () => {
      window.removeEventListener('error', handleGlobalError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, [navigate]);

  return children;
};

export default TradingAccessHandler;
