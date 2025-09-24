// API Configuration
export const API_BASE_URL = 'http://localhost:8080';
export const TRADING_BOT_API_URL = 'http://localhost:8080';

// API Endpoints
export const API_ENDPOINTS = {
  HEALTH: '/api/health',
  STOCK_DATA: '/api/stock/data',
  STOCK_INFO: '/api/stock/info',
  TECHNICAL_ANALYSIS: '/api/stock/technical',
  PREDICTION: '/api/prediction',
  SENSITIVITY: '/api/sensitivity',
  RECOMMENDATIONS: '/api/recommendations',
  PORTFOLIO_GROWTH: '/api/portfolio/growth',
  ETF_ANALYSIS: '/api/etf/analysis',
  MONEY_GROWTH_STRATEGIES: '/api/strategies/money-growth',
  PORTFOLIO_INITIALIZE: '/api/portfolio/initialize',
  PORTFOLIO_ADD_CAPITAL: '/api/portfolio/add-capital',
  PORTFOLIO_SIGNALS: '/api/portfolio/signals',
  PORTFOLIO_EXECUTE: '/api/portfolio/execute',
  PORTFOLIO_SUMMARY: '/api/portfolio/summary',
  PORTFOLIO_PERFORMANCE: '/api/portfolio/performance',
  PORTFOLIO_REBALANCE: '/api/portfolio/rebalance',
  PORTFOLIO_SAVE: '/api/portfolio/save',
  PORTFOLIO_LOAD: '/api/portfolio/load',
  CHAT_QUERY: '/api/chat/query',
  CHAT_SENTIMENT: '/api/chat/sentiment',
  CHAT_INSIGHTS: '/api/chat/insights',
  BACKTEST_RUN: '/api/backtest/run',
  MARKETMATE_QUERY: '/api/marketmate/query'
};

// Request Configuration
export const REQUEST_CONFIG = {
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
}; 