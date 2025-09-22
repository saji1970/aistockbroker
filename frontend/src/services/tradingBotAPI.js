/**
 * Trading Bot API Service
 * Handles all API calls related to the trading bot functionality
 */

import { safeLogError } from '../utils/safeLogger';

import { TRADING_BOT_API_URL } from './config';

const API_BASE_URL = process.env.REACT_APP_TRADING_BOT_URL || TRADING_BOT_API_URL;

class TradingBotAPI {
  /**
   * Get bot status
   */
  async getStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching bot status:', error);
      throw error;
    }
  }

  /**
   * Start the trading bot
   */
  async startBot(config = {}, forceRestart = false) {
    try {
      // Check bot status first
      const statusResponse = await this.getStatus();
      if ((statusResponse.status === 'running' || statusResponse.status === 'started') && !forceRestart) {
        throw new Error('Bot is already running. Use forceRestart=true to restart with new configuration.');
      }

      // If bot is running and we want to restart, stop it first
      if ((statusResponse.status === 'running' || statusResponse.status === 'started') && forceRestart) {
        console.log('Bot is running, stopping it first...');
        try {
          await this.stopBot();
          console.log('Bot stopped successfully');
          // Wait a moment for the bot to stop
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Verify bot is stopped
          const verifyStatus = await this.getStatus();
          if (verifyStatus.status !== 'stopped') {
            throw new Error('Bot failed to stop properly');
          }
          console.log('Bot verified as stopped');
        } catch (stopError) {
          console.error('Error stopping bot:', stopError);
          throw new Error(`Failed to stop bot: ${stopError.message}`);
        }
      }

      // Clean config to remove any non-serializable objects
      const cleanConfig = {
        initial_capital: config.initial_capital || 100000,
        target_amount: config.target_amount || null,
        trading_period_days: config.trading_period_days || 30,
        max_position_size: config.max_position_size || 0.1,
        max_daily_loss: config.max_daily_loss || 0.05,
        risk_tolerance: config.risk_tolerance || 'medium',
        trading_strategy: config.trading_strategy || 'momentum',
        enable_ml_learning: config.enable_ml_learning !== false
      };

      console.log('Starting bot with config:', cleanConfig);
      const response = await fetch(`${API_BASE_URL}/api/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cleanConfig)
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Start bot failed:', errorData);
        throw new Error(errorData.error || 'Failed to start bot');
      }

      const result = await response.json();
      console.log('Bot started successfully:', result);
      return result;
    } catch (error) {
      safeLogError('Error starting bot:', error);
      throw error;
    }
  }

  /**
   * Stop the trading bot
   */
  async stopBot() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stop`, {
        method: 'POST'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to stop bot');
      }

      return await response.json();
    } catch (error) {
      safeLogError('Error stopping bot:', error);
      throw error;
    }
  }

  /**
   * Restart the trading bot with new configuration
   */
  async restartBot(config = {}) {
    try {
      return await this.startBot(config, true);
    } catch (error) {
      safeLogError('Error restarting bot:', error);
      throw error;
    }
  }

  /**
   * Get current portfolio data
   */
  async getPortfolio() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/portfolio`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching portfolio:', error);
      throw error;
    }
  }

  /**
   * Get portfolio history
   */
  async getPortfolioHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/portfolio/history`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching portfolio history:', error);
      throw error;
    }
  }

  /**
   * Get recent orders
   */
  async getOrders() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/orders`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching orders:', error);
      throw error;
    }
  }

  /**
   * Get performance metrics
   */
  async getPerformance() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/performance`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching performance:', error);
      throw error;
    }
  }

  /**
   * Get current watchlist
   */
  async getWatchlist() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/watchlist`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching watchlist:', error);
      throw error;
    }
  }

  /**
   * Add symbol to watchlist
   */
  async addToWatchlist(symbol) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/watchlist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'add',
          symbol: symbol.toUpperCase()
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add symbol');
      }

      return await response.json();
    } catch (error) {
      safeLogError('Error adding to watchlist:', error);
      throw error;
    }
  }

  /**
   * Remove symbol from watchlist
   */
  async removeFromWatchlist(symbol) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/watchlist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'remove',
          symbol: symbol.toUpperCase()
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to remove symbol');
      }

      return await response.json();
    } catch (error) {
      safeLogError('Error removing from watchlist:', error);
      throw error;
    }
  }

  /**
   * Get available strategies
   */
  async getStrategies() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/strategies`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching strategies:', error);
      throw error;
    }
  }

  /**
   * Get comprehensive bot data (all endpoints in one call)
   */
  async getAllBotData() {
    try {
      const [status, portfolio, orders, performance, watchlist, strategies, portfolioHistory] = await Promise.all([
        this.getStatus(),
        this.getPortfolio(),
        this.getOrders(),
        this.getPerformance(),
        this.getWatchlist(),
        this.getStrategies(),
        this.getPortfolioHistory()
      ]);

      return {
        status,
        portfolio,
        orders,
        performance,
        watchlist,
        strategies,
        portfolioHistory
      };
    } catch (error) {
      console.error('Error fetching all bot data:', error);
      throw error;
    }
  }

  /**
   * Subscribe to real-time updates (WebSocket simulation using polling)
   */
  subscribeToUpdates(callback, interval = 5000) {
    const poll = async () => {
      try {
        const data = await this.getAllBotData();
        callback(data);
      } catch (error) {
        console.error('Error in polling update:', error);
      }
    };

    // Initial call
    poll();

    // Set up polling
    const intervalId = setInterval(poll, interval);

    // Return unsubscribe function
    return () => clearInterval(intervalId);
  }

  /**
   * Format currency values
   */
  formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  }

  /**
   * Format percentage values
   */
  formatPercent(value) {
    return `${value >= 0 ? '+' : ''}${(value || 0).toFixed(2)}%`;
  }

  /**
   * Get status color class
   */
  getStatusColor(status) {
    switch (status) {
      case 'running':
      case 'started':
        return 'bg-green-100 text-green-800';
      case 'stopped':
        return 'bg-gray-100 text-gray-800';
      case 'not_initialized':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  /**
   * Get status icon
   */
  getStatusIcon(status) {
    switch (status) {
      case 'running':
      case 'started':
        return '🟢';
      case 'stopped':
        return '🔴';
      default:
        return '🟡';
    }
  }

  /**
   * Calculate portfolio metrics
   */
  calculatePortfolioMetrics(portfolio, performance) {
    if (!portfolio || !performance) {
      return {
        totalValue: 0,
        totalReturn: 0,
        totalReturnPercent: 0,
        cash: 0,
        positionsCount: 0,
        marketValue: 0,
        unrealizedPnL: 0
      };
    }

    const totalValue = portfolio.total_value || 0;
    const cash = portfolio.cash || 0;
    const positions = portfolio.positions || {};
    const positionsCount = Object.keys(positions).length;
    
    const marketValue = Object.values(positions).reduce((sum, pos) => sum + (pos.market_value || 0), 0);
    const unrealizedPnL = Object.values(positions).reduce((sum, pos) => sum + (pos.unrealized_pnl || 0), 0);
    
    const totalReturn = performance.total_return_pct || 0;
    const totalReturnPercent = totalReturn;

    return {
      totalValue,
      totalReturn,
      totalReturnPercent,
      cash,
      positionsCount,
      marketValue,
      unrealizedPnL
    };
  }

  /**
   * Get bot configuration
   */
  async getBotConfig() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/config`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching bot config:', error);
      throw error;
    }
  }

  /**
   * Get ML insights
   */
  async getMLInsights() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/learning/insights`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      safeLogError('Error fetching ML insights:', error);
      throw error;
    }
  }
}

// Create and export a singleton instance
const tradingBotAPI = new TradingBotAPI();
export default tradingBotAPI;
