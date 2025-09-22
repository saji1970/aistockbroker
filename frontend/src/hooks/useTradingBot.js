import { useState, useEffect, useCallback, useRef } from 'react';
import tradingBotAPI from '../services/tradingBotAPI';

/**
 * Custom hook for managing trading bot state and operations
 */
export const useTradingBot = (options = {}) => {
  const {
    autoUpdate = true,
    updateInterval = 5000,
    initialConfig = {
      initialCapital: 100000,
      tradingInterval: 300,
      maxPositionSize: 0.1,
      maxDailyLoss: 0.05
    }
  } = options;

  // State
  const [botStatus, setBotStatus] = useState('stopped');
  const [portfolio, setPortfolio] = useState(null);
  const [orders, setOrders] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [strategies, setStrategies] = useState({});
  const [performance, setPerformance] = useState({});
  const [portfolioHistory, setPortfolioHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Refs
  const unsubscribeRef = useRef(null);
  const mountedRef = useRef(true);

  // Fetch all bot data
  const fetchAllData = useCallback(async () => {
    if (!mountedRef.current) return;

    try {
      const data = await tradingBotAPI.getAllBotData();
      
      if (mountedRef.current) {
        console.log('fetchAllData - received data:', data);
        console.log('fetchAllData - setting bot status to:', data.status.status);
        setBotStatus(data.status.status);
        setPortfolio(data.portfolio);
        setOrders(data.orders);
        setWatchlist(data.watchlist.watchlist || []);
        setStrategies(data.strategies);
        setPerformance(data.performance);
        setPortfolioHistory(data.portfolioHistory);
        setLastUpdate(new Date());
        setError(null);
      }
    } catch (err) {
      if (mountedRef.current) {
        console.error('Error fetching bot data:', err);
        setError(err.message);
      }
    }
  }, []);

  // Start bot
  const startBot = useCallback(async (config = {}) => {
    setLoading(true);
    setError(null);

    try {
      const mergedConfig = { ...initialConfig, ...config };
      await tradingBotAPI.startBot(mergedConfig);
      setBotStatus('running');
      
      // Fetch updated data
      await fetchAllData();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [initialConfig, fetchAllData]);

  // Stop bot
  const stopBot = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      await tradingBotAPI.stopBot();
      setBotStatus('stopped');
      
      // Fetch updated data
      await fetchAllData();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchAllData]);

  // Restart bot
  const restartBot = useCallback(async (config = {}) => {
    console.log('restartBot - starting restart process');
    setLoading(true);
    setError(null);

    try {
      const mergedConfig = { ...initialConfig, ...config };
      console.log('restartBot - calling tradingBotAPI.restartBot with config:', mergedConfig);
      await tradingBotAPI.restartBot(mergedConfig);
      console.log('restartBot - API call successful, setting status to running');
      setBotStatus('running');
      
      // Fetch updated data
      console.log('restartBot - fetching updated data');
      await fetchAllData();
      console.log('restartBot - fetchAllData completed');
    } catch (err) {
      console.error('restartBot - error occurred:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
      console.log('restartBot - process completed');
    }
  }, [initialConfig, fetchAllData]);

  // Add to watchlist
  const addToWatchlist = useCallback(async (symbol) => {
    try {
      await tradingBotAPI.addToWatchlist(symbol);
      await fetchAllData();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [fetchAllData]);

  // Remove from watchlist
  const removeFromWatchlist = useCallback(async (symbol) => {
    try {
      await tradingBotAPI.removeFromWatchlist(symbol);
      await fetchAllData();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [fetchAllData]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Start auto-updates
  const startAutoUpdate = useCallback(() => {
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
    }

    unsubscribeRef.current = tradingBotAPI.subscribeToUpdates((data) => {
      if (mountedRef.current) {
        setBotStatus(data.status.status);
        setPortfolio(data.portfolio);
        setOrders(data.orders);
        setWatchlist(data.watchlist.watchlist || []);
        setStrategies(data.strategies);
        setPerformance(data.performance);
        setPortfolioHistory(data.portfolioHistory);
        setLastUpdate(new Date());
        setError(null);
      }
    }, updateInterval);
  }, [updateInterval]);

  // Stop auto-updates
  const stopAutoUpdate = useCallback(() => {
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
      unsubscribeRef.current = null;
    }
  }, []);

  // Initialize
  useEffect(() => {
    mountedRef.current = true;
    fetchAllData();

    return () => {
      mountedRef.current = false;
      stopAutoUpdate();
    };
  }, [fetchAllData, stopAutoUpdate]);

  // Auto-update when bot is running
  useEffect(() => {
    if (autoUpdate && (botStatus === 'running' || botStatus === 'started')) {
      startAutoUpdate();
    } else {
      stopAutoUpdate();
    }

    return () => {
      stopAutoUpdate();
    };
  }, [autoUpdate, botStatus, startAutoUpdate, stopAutoUpdate]);

  // Calculate derived metrics
  const metrics = tradingBotAPI.calculatePortfolioMetrics(portfolio, performance);

  // Formatting helpers
  const formatCurrency = tradingBotAPI.formatCurrency;
  const formatPercent = tradingBotAPI.formatPercent;
  const getStatusColor = tradingBotAPI.getStatusColor;
  const getStatusIcon = tradingBotAPI.getStatusIcon;

  return {
    // State
    botStatus,
    portfolio,
    orders,
    watchlist,
    strategies,
    performance,
    portfolioHistory,
    loading,
    error,
    lastUpdate,
    metrics,

    // Actions
    startBot,
    stopBot,
    restartBot,
    addToWatchlist,
    removeFromWatchlist,
    fetchAllData,
    clearError,
    startAutoUpdate,
    stopAutoUpdate,

    // Helpers
    formatCurrency,
    formatPercent,
    getStatusColor,
    getStatusIcon,

    // Computed
    isRunning: botStatus === 'running' || botStatus === 'started',
    isStopped: botStatus === 'stopped',
    isInitialized: botStatus !== 'not_initialized',
    hasPositions: portfolio && Object.keys(portfolio.positions || {}).length > 0,
    hasOrders: orders && orders.length > 0,
    hasWatchlist: watchlist && watchlist.length > 0
  };
};

export default useTradingBot;
