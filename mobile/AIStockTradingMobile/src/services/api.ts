import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Configuration
const API_BASE_URL = 'https://ai-stock-trading-api-1024040140027.us-central1.run.app';
const TRADING_BOT_API_URL = 'https://ai-stock-trading-backend-1024040140027.us-central1.run.app';

// Create axios instances
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const tradingBotClient = axios.create({
  baseURL: TRADING_BOT_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Trading Bot API interceptor
tradingBotClient.interceptors.request.use(
  (config) => {
    console.log(`🤖 Trading Bot Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Trading Bot Request Error:', error);
    return Promise.reject(error);
  }
);

tradingBotClient.interceptors.response.use(
  (response) => {
    console.log(`✅ Trading Bot Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ Trading Bot Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Stock Data API
export const stockAPI = {
  // Get stock data
  getStockData: async (symbol: string, period: string = '1y', market: string = 'US') => {
    try {
      const response = await apiClient.get(`/api/stock/data/${symbol}`, {
        params: { period, market }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching stock data:', error);
      throw error;
    }
  },

  // Get stock info
  getStockInfo: async (symbol: string, market: string = 'US') => {
    try {
      const response = await apiClient.get(`/api/stock/info/${symbol}`, {
        params: { market }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching stock info:', error);
      throw error;
    }
  },

  // Get prediction
  getPrediction: async (symbol: string, market: string = 'US') => {
    try {
      const response = await apiClient.get(`/api/prediction/${symbol}`, {
        params: { market }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching prediction:', error);
      throw error;
    }
  },

  // Get sensitivity analysis
  getSensitivityAnalysis: async (symbol: string, market: string = 'US') => {
    try {
      const response = await apiClient.get(`/api/sensitivity/analysis/${symbol}`, {
        params: { market }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching sensitivity analysis:', error);
      throw error;
    }
  },

  // Get prediction with sensitivity
  getPredictionWithSensitivity: async (symbol: string, market: string = 'US') => {
    try {
      const response = await apiClient.get(`/api/prediction/${symbol}/sensitivity`, {
        params: { market }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching prediction with sensitivity:', error);
      throw error;
    }
  },

  // Health check
  getHealth: async () => {
    try {
      const response = await apiClient.get('/api/health');
      return response.data;
    } catch (error) {
      console.error('Error checking API health:', error);
      throw error;
    }
  }
};

// Trading Bot API
export const tradingBotAPI = {
  // Get bot status
  getStatus: async () => {
    try {
      const response = await tradingBotClient.get('/api/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching bot status:', error);
      throw error;
    }
  },

  // Get portfolio
  getPortfolio: async () => {
    try {
      const response = await tradingBotClient.get('/api/portfolio');
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      throw error;
    }
  },

  // Get orders
  getOrders: async () => {
    try {
      const response = await tradingBotClient.get('/api/orders');
      return response.data;
    } catch (error) {
      console.error('Error fetching orders:', error);
      throw error;
    }
  },

  // Get watchlist
  getWatchlist: async () => {
    try {
      const response = await tradingBotClient.get('/api/watchlist');
      return response.data;
    } catch (error) {
      console.error('Error fetching watchlist:', error);
      throw error;
    }
  },

  // Get strategies
  getStrategies: async () => {
    try {
      const response = await tradingBotClient.get('/api/strategies');
      return response.data;
    } catch (error) {
      console.error('Error fetching strategies:', error);
      throw error;
    }
  },

  // Get performance
  getPerformance: async () => {
    try {
      const response = await tradingBotClient.get('/api/performance');
      return response.data;
    } catch (error) {
      console.error('Error fetching performance:', error);
      throw error;
    }
  },

  // Get portfolio history
  getPortfolioHistory: async () => {
    try {
      const response = await tradingBotClient.get('/api/portfolio/history');
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio history:', error);
      throw error;
    }
  },

  // Start bot
  startBot: async (config: any) => {
    try {
      const response = await tradingBotClient.post('/api/start', config);
      return response.data;
    } catch (error) {
      console.error('Error starting bot:', error);
      throw error;
    }
  },

  // Stop bot
  stopBot: async () => {
    try {
      const response = await tradingBotClient.post('/api/stop');
      return response.data;
    } catch (error) {
      console.error('Error stopping bot:', error);
      throw error;
    }
  },

  // Add to watchlist
  addToWatchlist: async (symbol: string) => {
    try {
      const response = await tradingBotClient.post('/api/watchlist', { symbol });
      return response.data;
    } catch (error) {
      console.error('Error adding to watchlist:', error);
      throw error;
    }
  },

  // Remove from watchlist
  removeFromWatchlist: async (symbol: string) => {
    try {
      const response = await tradingBotClient.delete(`/api/watchlist/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error removing from watchlist:', error);
      throw error;
    }
  },

  // Get all bot data
  getAllBotData: async () => {
    try {
      const [status, portfolio, orders, watchlist, strategies, performance, portfolioHistory] = await Promise.all([
        tradingBotAPI.getStatus(),
        tradingBotAPI.getPortfolio(),
        tradingBotAPI.getOrders(),
        tradingBotAPI.getWatchlist(),
        tradingBotAPI.getStrategies(),
        tradingBotAPI.getPerformance(),
        tradingBotAPI.getPortfolioHistory(),
      ]);

      return {
        status,
        portfolio,
        orders,
        watchlist,
        strategies,
        performance,
        portfolioHistory,
      };
    } catch (error) {
      console.error('Error fetching all bot data:', error);
      throw error;
    }
  }
};

// AI Assistant API
export const aiAssistantAPI = {
  // Process natural language query
  processQuery: async (query: string, context?: any) => {
    try {
      const response = await apiClient.post('/api/ai/query', {
        query,
        context
      });
      return response.data;
    } catch (error) {
      console.error('Error processing AI query:', error);
      throw error;
    }
  },

  // Get market insights
  getMarketInsights: async (symbol?: string) => {
    try {
      const response = await apiClient.get('/api/ai/insights', {
        params: symbol ? { symbol } : {}
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching market insights:', error);
      throw error;
    }
  },

  // Get trading recommendations
  getTradingRecommendations: async (symbol: string, riskTolerance: string = 'medium') => {
    try {
      const response = await apiClient.get('/api/ai/recommendations', {
        params: { symbol, risk_tolerance: riskTolerance }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching trading recommendations:', error);
      throw error;
    }
  }
};

// Portfolio API
export const portfolioAPI = {
  // Get portfolio analysis
  getPortfolioAnalysis: async (symbols: string[]) => {
    try {
      const response = await apiClient.post('/api/portfolio/analysis', { symbols });
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio analysis:', error);
      throw error;
    }
  },

  // Get portfolio optimization
  getPortfolioOptimization: async (symbols: string[], riskTolerance: string = 'medium') => {
    try {
      const response = await apiClient.post('/api/portfolio/optimization', {
        symbols,
        risk_tolerance: riskTolerance
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio optimization:', error);
      throw error;
    }
  }
};

// Cache management
export const cacheManager = {
  // Set cache
  setCache: async (key: string, data: any, ttl: number = 300000) => { // 5 minutes default
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
        ttl
      };
      await AsyncStorage.setItem(`cache_${key}`, JSON.stringify(cacheData));
    } catch (error) {
      console.error('Error setting cache:', error);
    }
  },

  // Get cache
  getCache: async (key: string) => {
    try {
      const cached = await AsyncStorage.getItem(`cache_${key}`);
      if (!cached) return null;

      const cacheData = JSON.parse(cached);
      const now = Date.now();

      if (now - cacheData.timestamp > cacheData.ttl) {
        await AsyncStorage.removeItem(`cache_${key}`);
        return null;
      }

      return cacheData.data;
    } catch (error) {
      console.error('Error getting cache:', error);
      return null;
    }
  },

  // Clear cache
  clearCache: async (key?: string) => {
    try {
      if (key) {
        await AsyncStorage.removeItem(`cache_${key}`);
      } else {
        const keys = await AsyncStorage.getAllKeys();
        const cacheKeys = keys.filter(k => k.startsWith('cache_'));
        await AsyncStorage.multiRemove(cacheKeys);
      }
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }
};

// Network status
export const networkAPI = {
  // Check network connectivity
  isConnected: async () => {
    try {
      const response = await apiClient.get('/api/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  },

  // Get network info
  getNetworkInfo: async () => {
    try {
      const [apiHealth, botHealth] = await Promise.all([
        apiClient.get('/api/health').catch(() => ({ status: 0 })),
        tradingBotClient.get('/api/status').catch(() => ({ status: 0 }))
      ]);

      return {
        api: apiHealth.status === 200,
        tradingBot: botHealth.status === 200,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      return {
        api: false,
        tradingBot: false,
        timestamp: new Date().toISOString()
      };
    }
  }
};

export default {
  stockAPI,
  tradingBotAPI,
  aiAssistantAPI,
  portfolioAPI,
  cacheManager,
  networkAPI
};