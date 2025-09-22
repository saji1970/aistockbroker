import React, { useState } from 'react';
import { useTradingBot } from '../hooks/useTradingBot';
import TradingBotChart from '../components/Charts/TradingBotChart';
import BotConfiguration from '../components/Trading/BotConfiguration';
import TradingMonitor from '../components/Trading/TradingMonitor';
import {
  CogIcon,
  EyeIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const TradingBotNew = () => {
  const [activeView, setActiveView] = useState('config');
  const [botConfig, setBotConfig] = useState(() => {
    // Load saved configuration from localStorage
    const savedConfig = localStorage.getItem('tradingBotConfig');
    return savedConfig ? JSON.parse(savedConfig) : null;
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
    restartBot,
    addToWatchlist: addToWatchlistAPI,
    removeFromWatchlist: removeFromWatchlistAPI,
    clearError
  } = useTradingBot();

  const handleStartBot = async (config) => {
    try {
      setBotConfig(config);
      // Save configuration to localStorage
      localStorage.setItem('tradingBotConfig', JSON.stringify(config));
      await startBot(config);
    } catch (error) {
      // Handle "bot already running" error gracefully
      if (error.message && error.message.includes('already running')) {
        // Bot is already running, ask user if they want to restart
        const shouldRestart = window.confirm(
          'The trading bot is already running. Would you like to restart it with the new configuration?'
        );
        
        if (shouldRestart) {
                 try {
                   console.log('Restarting bot with new configuration...');
                   await restartBot(config);
                   setBotConfig(config);
                   // Save configuration to localStorage
                   localStorage.setItem('tradingBotConfig', JSON.stringify(config));
                   console.log('Bot restarted successfully with new configuration');
            // Show success message
            alert('Bot restarted successfully with new configuration!');
          } catch (restartError) {
            console.error('Failed to restart bot:', restartError);
            alert(`Failed to restart bot: ${restartError.message}`);
            throw restartError;
          }
        } else {
          // User chose not to restart, just update the config
          setBotConfig(config);
          console.log('Bot is already running with existing configuration');
          alert('Bot is already running with existing configuration.');
        }
      } else {
        // Re-throw other errors
        throw error;
      }
    }
  };

  const handleStopBot = async () => {
    try {
      await stopBot();
      // Clear saved configuration when bot is stopped
      localStorage.removeItem('tradingBotConfig');
      setBotConfig(null);
    } catch (error) {
      console.error('Error stopping bot:', error);
    }
  };

  const views = [
    { id: 'config', label: 'Configuration', icon: CogIcon },
    { id: 'monitor', label: 'Monitor', icon: EyeIcon },
    { id: 'chart', label: 'Performance', icon: ChartBarIcon }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Trading Bot</h1>
          <p className="mt-2 text-gray-600">
            Configure and monitor your AI-powered trading bot with advanced machine learning capabilities.
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
              <button
                onClick={clearError}
                className="ml-auto text-red-400 hover:text-red-600"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {views.map((view) => {
              const Icon = view.icon;
              return (
                <button
                  key={view.id}
                  onClick={() => setActiveView(view.id)}
                  className={`flex items-center px-1 py-2 text-sm font-medium border-b-2 ${
                    activeView === view.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {view.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading...</span>
          </div>
        )}

        {/* Content */}
        {!loading && (
          <div className="space-y-6">
            {activeView === 'config' && (
              <BotConfiguration
                onStartBot={handleStartBot}
                onStopBot={handleStopBot}
                isRunning={botStatus === 'running' || botStatus === 'started'}
                currentConfig={botConfig}
              />
            )}

            {activeView === 'monitor' && (
              <TradingMonitor
                botData={portfolio}
                performance={performance}
                orders={orders}
                mlInsights={null} // Will be implemented later
              />
            )}

            {activeView === 'chart' && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Performance</h3>
                {portfolioHistory && portfolioHistory.length > 0 ? (
                  <TradingBotChart
                    data={portfolioHistory}
                    title="Portfolio Value Over Time"
                  />
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <ChartBarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p>No performance data available yet.</p>
                    <p className="text-sm">Start the bot to begin tracking performance.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Bot Status Summary */}
        {botStatus && (
          <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Bot Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  botStatus.status === 'running' || botStatus.status === 'started'
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    botStatus.status === 'running' || botStatus.status === 'started' ? 'bg-green-500' : 'bg-gray-400'
                  }`}></div>
                  {botStatus.status === 'running' || botStatus.status === 'started' ? 'Running' : 'Stopped'}
                </div>
                <p className="text-sm text-gray-500 mt-1">Bot Status</p>
              </div>
              
              <div className="text-center">
                <p className="text-lg font-semibold text-gray-900">
                  {watchlist?.length || 0}
                </p>
                <p className="text-sm text-gray-500">Watchlist Items</p>
              </div>
              
              <div className="text-center">
                <p className="text-lg font-semibold text-gray-900">
                  {orders?.length || 0}
                </p>
                <p className="text-sm text-gray-500">Total Trades</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradingBotNew;
