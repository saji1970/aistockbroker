import React from 'react';
import { useTradingBot } from '../../hooks/useTradingBot';
import {
  PlayIcon,
  StopIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const TradingBotWidget = () => {
  const {
    botStatus,
    portfolio,
    performance,
    loading,
    error,
    metrics,
    startBot,
    stopBot,
    clearError,
    formatCurrency,
    formatPercent,
    getStatusColor,
    getStatusIcon
  } = useTradingBot({
    autoUpdate: true,
    updateInterval: 10000
  });

  const toggleBot = async () => {
    try {
      if (botStatus === 'running' || botStatus === 'started') {
        await stopBot();
      } else {
        await startBot();
      }
    } catch (err) {
      // Error is handled by the hook
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">AI Trading Bot</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(botStatus)}`}>
          {getStatusIcon(botStatus)} {botStatus === 'running' || botStatus === 'started' ? 'Running' : botStatus === 'stopped' ? 'Stopped' : 'Not Initialized'}
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-4 w-4 text-red-600 mr-2" />
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Bot Controls */}
      <div className="mb-6">
        <button
          onClick={toggleBot}
          disabled={loading}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            botStatus === 'running' || botStatus === 'started'
              ? 'bg-red-600 text-white hover:bg-red-700'
              : 'bg-green-600 text-white hover:bg-green-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {botStatus === 'running' || botStatus === 'started' ? (
            <>
              <StopIcon className="h-4 w-4" />
              <span>Stop Bot</span>
            </>
          ) : (
            <>
              <PlayIcon className="h-4 w-4" />
              <span>Start Bot</span>
            </>
          )}
        </button>
      </div>

      {/* Performance Metrics */}
      {portfolio && (
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <CurrencyDollarIcon className="h-5 w-5 text-blue-600 mr-1" />
              <span className="text-sm font-medium text-gray-500">Portfolio Value</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {formatCurrency(metrics.totalValue)}
            </p>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <ArrowTrendingUpIcon className="h-5 w-5 text-green-600 mr-1" />
              <span className="text-sm font-medium text-gray-500">Total Return</span>
            </div>
            <p className={`text-lg font-semibold ${
              metrics.totalReturnPercent >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatPercent(metrics.totalReturnPercent)}
            </p>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <CurrencyDollarIcon className="h-5 w-5 text-yellow-600 mr-1" />
              <span className="text-sm font-medium text-gray-500">Cash</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {formatCurrency(metrics.cash)}
            </p>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <ChartBarIcon className="h-5 w-5 text-purple-600 mr-1" />
              <span className="text-sm font-medium text-gray-500">Positions</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {metrics.positionsCount}
            </p>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      {performance && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex justify-between text-sm text-gray-500">
            <span>Orders: {performance.orders_count || 0}</span>
            <span>Initial: {formatCurrency(performance.initial_capital)}</span>
          </div>
        </div>
      )}

      {/* Last Update */}
      {portfolio && (
        <div className="mt-3 flex items-center text-xs text-gray-400">
          <ClockIcon className="h-3 w-3 mr-1" />
          <span>Last update: {new Date().toLocaleTimeString()}</span>
        </div>
      )}
    </div>
  );
};

export default TradingBotWidget;
