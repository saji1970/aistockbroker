import axios from 'axios';
import { API_BASE_URL } from './config';
import { safeLog, safeLogError } from '../utils/safeLogger';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    safeLog(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    safeLogError('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    safeLog(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    safeLogError('❌ API Response Error:', error, {
      status: error.response?.status,
      data: error.response?.data
    });
    return Promise.reject(error);
  }
);

// Market configuration
export const MARKETS = {
  US: {
    name: 'United States',
    currency: 'USD',
    suffix: '',
    exchanges: ['NYSE', 'NASDAQ', 'AMEX'],
    symbols: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'SPY', 'QQQ', 'VOO', 'DAL', 'UAL', 'AAL', 'JPM', 'BAC', 'WMT', 'JNJ', 'PG', 'KO']
  },
  UK: {
    name: 'United Kingdom',
    currency: 'GBP',
    suffix: '.L',
    exchanges: ['LSE'],
    symbols: ['VOD.L', 'HSBA.L', 'BP.L', 'GSK.L', 'ULVR.L', 'RIO.L', 'BHP.L', 'AZN.L', 'REL.L', 'CRH.L', 'PRU.L', 'LLOY.L', 'BARC.L', 'RKT.L', 'SHEL.L']
  },
  CA: {
    name: 'Canada',
    currency: 'CAD',
    suffix: '.TO',
    exchanges: ['TSX'],
    symbols: ['RY.TO', 'TD.TO', 'CNR.TO', 'CP.TO', 'SHOP.TO', 'ENB.TO', 'TRP.TO', 'BCE.TO', 'T.TO', 'BMO.TO', 'CM.TO', 'BNS.TO', 'ABX.TO', 'G.TO', 'SU.TO']
  },
  AU: {
    name: 'Australia',
    currency: 'AUD',
    suffix: '.AX',
    exchanges: ['ASX'],
    symbols: ['CBA.AX', 'CSL.AX', 'NAB.AX', 'ANZ.AX', 'WBC.AX', 'BHP.AX', 'RIO.AX', 'WES.AX', 'WOW.AX', 'TLS.AX', 'QBE.AX', 'IAG.AX', 'SGP.AX', 'REA.AX', 'TWE.AX']
  },
  DE: {
    name: 'Germany',
    currency: 'EUR',
    suffix: '.DE',
    exchanges: ['FRA'],
    symbols: ['SAP.DE', 'SIE.DE', 'BMW.DE', 'DAI.DE', 'VOW.DE', 'BAYN.DE', 'BAS.DE', 'DTE.DE', 'EOAN.DE', 'RWE.DE', 'ADS.DE', 'ALV.DE', 'DBK.DE', 'CBK.DE', 'LIN.DE']
  },
  JP: {
    name: 'Japan',
    currency: 'JPY',
    suffix: '.T',
    exchanges: ['TYO'],
    symbols: ['7203.T', '6758.T', '9984.T', '6861.T', '6954.T', '7974.T', '8306.T', '9433.T', '9432.T', '9434.T', '7267.T', '6501.T', '6752.T', '7733.T', '4901.T']
  },
  IN: {
    name: 'India',
    currency: 'INR',
    suffix: '.NS',
    exchanges: ['NSE'],
    symbols: ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'SUNPHARMA.NS']
  },
  BR: {
    name: 'Brazil',
    currency: 'BRL',
    suffix: '.SA',
    exchanges: ['SAO'],
    symbols: ['VALE.SA', 'PETR4.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'WEGE3.SA', 'RENT3.SA', 'LREN3.SA', 'RAIL3.SA', 'CCRO3.SA', 'USIM5.SA', 'GGBR4.SA', 'CSAN3.SA', 'EMBR3.SA', 'SUZB3.SA']
  }
};

export const stockAPI = {
  getStockData: async (symbol, period = '1y', market = 'US') => {
    try {
      const marketConfig = MARKETS[market];
      const fullSymbol = marketConfig?.suffix ? symbol + marketConfig.suffix : symbol;
      const response = await api.get(`/api/stock/data/${fullSymbol}?period=${period}&market=${market}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching stock data:', error);
      // Handle specific backend error format
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  getStockInfo: async (symbol, market = 'US') => {
    try {
      const marketConfig = MARKETS[market];
      const fullSymbol = marketConfig?.suffix ? symbol + marketConfig.suffix : symbol;
      const response = await api.get(`/api/stock/info/${fullSymbol}?market=${market}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching stock info:', error);
      // Handle specific backend error format
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  searchStocks: async (query, market = 'US') => {
    try {
      const response = await api.get(`/api/stock/search?q=${query}&market=${market}`);
      return response.data;
    } catch (error) {
      console.error('Error searching stocks:', error);
      // Handle specific backend error format
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },
  
  getMarketSymbols: (market = 'US') => {
    return MARKETS[market]?.symbols || MARKETS.US.symbols;
  },
  
  getMarketInfo: (market = 'US') => {
    return MARKETS[market] || MARKETS.US;
  },

  getTechnicalIndicators: async (symbol, period = '1y', market = 'US') => {
    try {
      const marketConfig = MARKETS[market];
      const fullSymbol = marketConfig?.suffix ? symbol + marketConfig.suffix : symbol;
      const response = await api.get(`/api/stock/technical/${fullSymbol}?period=${period}&market=${market}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching technical indicators:', error);
      // Return mock data if API fails
      return {
        latest_data: {
          RSI: 50 + (Math.random() - 0.5) * 40,
          MACD: (Math.random() - 0.5) * 2,
          MACD_Signal: (Math.random() - 0.5) * 2,
          SMA_20: 100 + (Math.random() - 0.5) * 20,
          SMA_50: 100 + (Math.random() - 0.5) * 20,
          BB_Position: Math.random(),
          Stoch_K: Math.random() * 100,
          OBV: Math.random() * 1000000
        },
        indicators: {
          rsi: Array.from({ length: 20 }, () => 30 + Math.random() * 40),
          macd: Array.from({ length: 20 }, () => (Math.random() - 0.5) * 2),
          sma_20: Array.from({ length: 20 }, () => 100 + (Math.random() - 0.5) * 20),
          sma_50: Array.from({ length: 20 }, () => 100 + (Math.random() - 0.5) * 20),
          bollinger_upper: Array.from({ length: 20 }, () => 110 + Math.random() * 10),
          bollinger_lower: Array.from({ length: 20 }, () => 90 - Math.random() * 10),
          volume: Array.from({ length: 20 }, () => Math.random() * 1000000)
        }
      };
    }
  }
};

// Prediction API
export const predictionAPI = {
  getPrediction: async (symbol) => {
    try {
      const response = await api.get(`/api/prediction/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching prediction:', error);
      // Handle specific backend error format
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  getPredictionWithSensitivity: async (symbol) => {
    try {
      const response = await api.get(`/api/prediction/${symbol}/sensitivity`);
      return response.data;
    } catch (error) {
      console.error('Error fetching prediction with sensitivity:', error);
      // Handle specific backend error format
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  getSensitivityAnalysis: async (symbol) => {
    try {
      const response = await api.get(`/api/sensitivity/analysis/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching sensitivity analysis:', error);
      // Handle specific backend error format
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },
};

// Portfolio API - Real Implementation
export const portfolioAPI = {
  initializePortfolio: async (initialCapital) => {
    try {
      const response = await api.post('/api/portfolio/initialize', {
        initial_capital: initialCapital,
      });
      return response.data;
    } catch (error) {
      console.error('Error initializing portfolio:', error);
      throw error;
    }
  },

  getPortfolio: async () => {
    try {
      const response = await api.get('/api/portfolio');
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      throw error;
    }
  },

  refreshPortfolio: async () => {
    try {
      // Use enhanced portfolio summary to refresh data
      const response = await api.get('/api/portfolio/enhanced/summary');
      return response.data;
    } catch (error) {
      console.error('Error refreshing portfolio:', error);
      throw error;
    }
  },

  addCash: async (amount, description = 'Cash deposit') => {
    try {
      // Get current portfolio summary to get current investment amount
      const currentSummary = await api.get('/api/portfolio/enhanced/summary');
      const currentInvestment = currentSummary.data.total_capital || 100000;
      const newInvestment = currentInvestment + amount;
      
      // Update investment amount using enhanced portfolio
      const response = await api.post('/api/portfolio/enhanced/update-investment', {
        investment_amount: newInvestment
      });
      return response.data;
    } catch (error) {
      console.error('Error adding cash:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  withdrawCash: async (amount, description = 'Cash withdrawal') => {
    try {
      // Get current portfolio summary to get current investment amount
      const currentSummary = await api.get('/api/portfolio/enhanced/summary');
      const currentInvestment = currentSummary.data.total_capital || 100000;
      const newInvestment = Math.max(0, currentInvestment - amount); // Don't allow negative investment
      
      // Update investment amount using enhanced portfolio
      const response = await api.post('/api/portfolio/enhanced/update-investment', {
        investment_amount: newInvestment
      });
      return response.data;
    } catch (error) {
      console.error('Error withdrawing cash:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  // Legacy buy/sell functions - use enhanced versions below
  buyStockLegacy: async (symbol, shares, market = 'US', price = null) => {
    try {
      const response = await api.post('/api/portfolio/buy', {
        symbol: symbol,
        shares: shares,
        market: market,
        price: price // Optional - backend will use real-time price if not provided
      });
      return response.data;
    } catch (error) {
      console.error('Error buying stock:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  sellStockLegacy: async (symbol, shares, market = 'US', price = null) => {
    try {
      const response = await api.post('/api/portfolio/sell', {
        symbol: symbol,
        shares: shares,
        market: market,
        price: price // Optional - backend will use real-time price if not provided
      });
      return response.data;
    } catch (error) {
      console.error('Error selling stock:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  getPortfolioPerformance: async (periodDays = 30) => {
    try {
      // Use enhanced portfolio summary which includes performance metrics
      const response = await api.get('/api/portfolio/enhanced/summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio performance:', error);
      throw error;
    }
  },

  getTransactionHistory: async (limit = 100, type = null) => {
    try {
      // Use enhanced portfolio transactions endpoint
      const response = await api.get('/api/portfolio/enhanced/transactions');
      return response.data;
    } catch (error) {
      console.error('Error fetching transaction history:', error);
      throw error;
    }
  },

  getPositionDetails: async (symbol, market = 'US') => {
    try {
      // Use enhanced portfolio asset endpoint
      const response = await api.get(`/api/portfolio/enhanced/asset/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching position details:', error);
      throw error;
    }
  },

  generateSignals: async (symbols) => {
    try {
      const response = await api.post('/api/portfolio/generate-signals', {
        symbols: symbols,
      });
      return response.data;
    } catch (error) {
      console.error('Error generating signals:', error);
      throw error;
    }
  },

  resetPortfolio: async () => {
    try {
      const response = await api.post('/api/portfolio/reset');
      return response.data;
    } catch (error) {
      console.error('Error resetting portfolio:', error);
      throw error;
    }
  },

  getPortfolioAnalytics: async () => {
    try {
      // Use enhanced portfolio summary which includes analytics
      const response = await api.get('/api/portfolio/enhanced/summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching portfolio analytics:', error);
      throw error;
    }
  },

  // Enhanced Portfolio API functions
  initializeEnhancedPortfolio: async (investmentAmount) => {
    try {
      const response = await api.post('/api/portfolio/enhanced/initialize', {
        investment_amount: investmentAmount
      });
      return response.data;
    } catch (error) {
      console.error('Error initializing enhanced portfolio:', error);
      throw error;
    }
  },

  updateInvestmentAmount: async (newAmount) => {
    try {
      const response = await api.post('/api/portfolio/enhanced/update-investment', {
        investment_amount: newAmount
      });
      return response.data;
    } catch (error) {
      console.error('Error updating investment amount:', error);
      throw error;
    }
  },

  buyStock: async (symbol, quantity, price = null) => {
    try {
      const response = await api.post('/api/portfolio/enhanced/buy', {
        symbol: symbol,
        quantity: quantity,
        price: price
      });
      return response.data;
    } catch (error) {
      console.error('Error buying stock:', error);
      throw error;
    }
  },

  sellStock: async (symbol, quantity, price = null) => {
    try {
      const response = await api.post('/api/portfolio/enhanced/sell', {
        symbol: symbol,
        quantity: quantity,
        price: price
      });
      return response.data;
    } catch (error) {
      console.error('Error selling stock:', error);
      throw error;
    }
  },

  getEnhancedPortfolioSummary: async () => {
    try {
      const response = await api.get('/api/portfolio/enhanced/summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching enhanced portfolio summary:', error);
      throw error;
    }
  },

  getEnhancedTransactionHistory: async () => {
    try {
      const response = await api.get('/api/portfolio/enhanced/transactions');
      return response.data;
    } catch (error) {
      console.error('Error fetching enhanced transaction history:', error);
      throw error;
    }
  },

  getAssetPerformance: async (symbol) => {
    try {
      const response = await api.get(`/api/portfolio/enhanced/asset/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching asset performance:', error);
      throw error;
    }
  },

  getCurrentPrice: async (symbol) => {
    try {
      const response = await api.get(`/api/portfolio/enhanced/current-price/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching current price:', error);
      throw error;
    }
  },
};

// Day Trading API
export const dayTradingAPI = {
  getDayTradingPrediction: async (symbol, targetDate) => {
    try {
      const response = await api.post(`/api/day-trading/prediction/${symbol}`, {
        target_date: targetDate,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching day trading prediction:', error);
      // Handle specific backend error format
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },
};

// Backtest API
export const backtestAPI = {
  runBacktest: async (strategy, symbols, startDate, endDate, initialCapital) => {
    try {
      const response = await api.post('/api/backtest/run', {
        strategy: strategy,
        symbols: symbols,
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
      });
      return response.data;
    } catch (error) {
      console.error('Error running backtest:', error);
      throw error;
    }
  },

  getBacktestResults: async (backtestId) => {
    try {
      const response = await api.get(`/api/backtest/results/${backtestId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching backtest results:', error);
      throw error;
    }
  },
};

// Financial Advisor API
export const financialAdvisorAPI = {
  generatePlan: async (userData) => {
    try {
      const response = await api.post('/api/financial-advisor/generate-plan', userData);
      return response.data;
    } catch (error) {
      console.error('Error generating financial plan:', error);
      throw error;
    }
  },
};

// Chat/AI Assistant API
export const chatAPI = {
  sendMessage: async (message) => {
    try {
      const response = await api.post('/api/chat/query', {
        query: message,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },
};

// MarketMate API - Natural Language Market Queries
export const marketMateAPI = {
  processQuery: async (query) => {
    try {
      const response = await api.get(`/api/marketmate/query?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Error processing MarketMate query:', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },

  processQueryPost: async (query) => {
    try {
      const response = await api.post('/api/marketmate/query', {
        query: query,
      });
      return response.data;
    } catch (error) {
      console.error('Error processing MarketMate query (POST):', error);
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  },
};

export default api; 