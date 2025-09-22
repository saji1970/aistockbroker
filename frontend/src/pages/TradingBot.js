import React, { useState } from 'react';
import { useStore } from '../store/store';
import { useTradingBot } from '../hooks/useTradingBot';
import TradingBotChart from '../components/Charts/TradingBotChart';
import BotConfiguration from '../components/Trading/BotConfiguration';
import TradingMonitor from '../components/Trading/TradingMonitor';
import {
  PlayIcon,
  StopIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CogIcon,
  PlusIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

const TradingBot = () => {
  const { currentSymbol } = useStore();
  const [newSymbol, setNewSymbol] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [activeView, setActiveView] = useState('config'); // config, monitor, chart
  const [botConfig, setBotConfig] = useState({
    initialCapital: 100000,
    tradingInterval: 300,
    maxPositionSize: 0.1,
    maxDailyLoss: 0.05
  });

  const {
    botStatus,
    portfolio,
    orders,
    watchlist,
    strategies,
    performance,
    portfolioHistory,
    loading,
    error,
    metrics,
    startBot,
    stopBot,
    addToWatchlist: addToWatchlistAPI,
    removeFromWatchlist: removeFromWatchlistAPI,
    clearError,
    formatCurrency,
    formatPercent,
    getStatusColor,
    getStatusIcon
  } = useTradingBot({
    autoUpdate: true,
    updateInterval: 5000,
    initialConfig: botConfig
  });

  // Add symbol to watchlist
  const addToWatchlist = async () => {
    if (!newSymbol.trim()) return;
    
    try {
      await addToWatchlistAPI(newSymbol);
      setNewSymbol('');
    } catch (err) {
      // Error is handled by the hook
    }
  };

  // Remove symbol from watchlist
  const removeFromWatchlist = async (symbol) => {
    try {
      await removeFromWatchlistAPI(symbol);
    } catch (err) {
      // Error is handled by the hook
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Trading Bot</h1>
            <p className="text-gray-600 mt-1">Shadow trading with real market data</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(botStatus)}`}>
              {botStatus === 'running' || botStatus === 'started' ? '🟢 Running' : botStatus === 'stopped' ? '🔴 Stopped' : '🟡 Not Initialized'}
            </span>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <CogIcon className="h-4 w-4" />
              <span>Settings</span>
            </button>
          </div>
        </div>

        {/* Bot Controls */}
        <div className="mt-6 flex items-center space-x-4">
          <button
            onClick={startBot}
            disabled={loading || botStatus === 'running' || botStatus === 'started'}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <PlayIcon className="h-4 w-4" />
            <span>Start Bot</span>
          </button>
          <button
            onClick={stopBot}
            disabled={loading || botStatus === 'stopped'}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <StopIcon className="h-4 w-4" />
            <span>Stop Bot</span>
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Advanced Settings */}
      {showAdvanced && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Bot Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Initial Capital
              </label>
              <input
                type="number"
                value={botConfig.initialCapital}
                onChange={(e) => setBotConfig({...botConfig, initialCapital: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Trading Interval (seconds)
              </label>
              <input
                type="number"
                value={botConfig.tradingInterval}
                onChange={(e) => setBotConfig({...botConfig, tradingInterval: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Position Size (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={botConfig.maxPositionSize * 100}
                onChange={(e) => setBotConfig({...botConfig, maxPositionSize: parseFloat(e.target.value) / 100})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Daily Loss (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={botConfig.maxDailyLoss * 100}
                onChange={(e) => setBotConfig({...botConfig, maxDailyLoss: parseFloat(e.target.value) / 100})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      )}

      {/* Performance Overview */}
      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Portfolio Value</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatCurrency(metrics.totalValue)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Return</p>
                <p className={`text-2xl font-semibold ${metrics.totalReturnPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercent(metrics.totalReturnPercent)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Cash</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatCurrency(metrics.cash)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Positions</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {metrics.positionsCount}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Watchlist Management */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Watchlist</h3>
        
        {/* Add Symbol */}
        <div className="flex items-center space-x-3 mb-4">
          <input
            type="text"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
            placeholder="Enter symbol (e.g., AAPL)"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            maxLength={5}
          />
          <button
            onClick={addToWatchlist}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Add</span>
          </button>
        </div>

        {/* Watchlist Items */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {watchlist.map((symbol) => (
            <div key={symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium text-gray-900">{symbol}</span>
              <button
                onClick={() => removeFromWatchlist(symbol)}
                className="text-red-600 hover:text-red-800 transition-colors"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>

        {watchlist.length === 0 && (
          <p className="text-gray-500 text-center py-4">No symbols in watchlist</p>
        )}
      </div>

      {/* Portfolio Performance Chart */}
      {portfolioHistory.length > 0 && (
        <TradingBotChart 
          data={portfolioHistory} 
          title="Portfolio Performance Over Time" 
        />
      )}

      {/* Current Positions */}
      {portfolio && portfolio.positions && Object.keys(portfolio.positions).length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Positions</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Market Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    P&L
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(portfolio.positions).map(([symbol, position]) => (
                  <tr key={symbol}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {position.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(position.avg_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(position.current_price)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(position.market_value)}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                      position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatCurrency(position.unrealized_pnl)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Orders */}
      {orders.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Orders</h3>
          <div className="space-y-3">
            {orders.slice(0, 10).map((order) => (
              <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    order.order_type === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {order.order_type}
                  </span>
                  <span className="font-medium text-gray-900">{order.symbol}</span>
                  <span className="text-sm text-gray-500">{order.quantity} shares</span>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">{formatCurrency(order.price)}</div>
                  <div className="text-xs text-gray-500">
                    {new Date(order.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Strategies */}
      {Object.keys(strategies).length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Strategies</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(strategies).map(([name, strategy]) => (
              <div key={name} className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900">{strategy.name}</h4>
                <p className="text-sm text-gray-500 mt-1">Status: Active</p>
                <div className="mt-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Enabled
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingBot;
