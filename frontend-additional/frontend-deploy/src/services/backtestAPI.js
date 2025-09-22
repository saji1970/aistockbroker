import { API_BASE_URL } from './config';

/**
 * Backtest API service for communicating with the backend
 */
class BacktestAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Run a backtest for a given strategy and symbol
   * @param {Object} backtestConfig - Backtest configuration
   * @param {string} backtestConfig.symbol - Stock symbol
   * @param {string} backtestConfig.strategy - Strategy name
   * @param {Object} backtestConfig.parameters - Strategy parameters
   * @param {number} backtestConfig.initial_capital - Initial capital
   * @param {string} backtestConfig.start_date - Start date (YYYY-MM-DD)
   * @param {string} backtestConfig.end_date - End date (YYYY-MM-DD)
   * @returns {Promise<Object>} Backtest results
   */
  async runBacktest(backtestConfig) {
    try {
      const response = await fetch(`${this.baseURL}/api/backtest/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestConfig),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error running backtest:', error);
      throw error;
    }
  }

  /**
   * Get available strategies
   * @returns {Promise<Array>} List of available strategies
   */
  async getStrategies() {
    try {
      const response = await fetch(`${this.baseURL}/api/backtest/strategies`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching strategies:', error);
      throw error;
    }
  }

  /**
   * Get backtest history
   * @returns {Promise<Array>} List of previous backtests
   */
  async getBacktestHistory() {
    try {
      const response = await fetch(`${this.baseURL}/api/backtest/history`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching backtest history:', error);
      throw error;
    }
  }

  /**
   * Save backtest results
   * @param {Object} backtestResult - Backtest result to save
   * @returns {Promise<Object>} Saved backtest result
   */
  async saveBacktestResult(backtestResult) {
    try {
      const response = await fetch(`${this.baseURL}/api/backtest/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestResult),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error saving backtest result:', error);
      throw error;
    }
  }

  /**
   * Compare multiple backtest results
   * @param {Array} backtestIds - Array of backtest IDs to compare
   * @returns {Promise<Object>} Comparison results
   */
  async compareBacktests(backtestIds) {
    try {
      const response = await fetch(`${this.baseURL}/api/backtest/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ backtest_ids: backtestIds }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error comparing backtests:', error);
      throw error;
    }
  }

  /**
   * Optimize strategy parameters
   * @param {Object} optimizationConfig - Optimization configuration
   * @returns {Promise<Object>} Optimization results
   */
  async optimizeStrategy(optimizationConfig) {
    try {
      const response = await fetch(`${this.baseURL}/api/backtest/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(optimizationConfig),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error optimizing strategy:', error);
      throw error;
    }
  }
}

// Create and export a singleton instance
const backtestAPI = new BacktestAPI();
export default backtestAPI; 