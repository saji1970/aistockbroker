import React, { useState } from 'react';
import {
  CogIcon,
  CurrencyDollarIcon,
  FlagIcon,
  CalendarIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  CpuChipIcon,
  PlayIcon,
  StopIcon
} from '@heroicons/react/24/outline';

const BotConfiguration = ({ onStartBot, onStopBot, isRunning, currentConfig }) => {
  const [config, setConfig] = useState({
    initial_capital: currentConfig?.initial_capital || 100000,
    target_amount: currentConfig?.target_amount || null,
    trading_period_days: currentConfig?.trading_period_days || 30,
    max_position_size: currentConfig?.max_position_size || 0.1,
    max_daily_loss: currentConfig?.max_daily_loss || 0.05,
    risk_tolerance: currentConfig?.risk_tolerance || 'medium',
    trading_strategy: currentConfig?.trading_strategy || 'momentum',
    enable_ml_learning: currentConfig?.enable_ml_learning !== false
  });

  const [isConfigSaved, setIsConfigSaved] = useState(false);

  const [isExpanded, setIsExpanded] = useState(false);

  const handleInputChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
    setIsConfigSaved(false); // Mark as unsaved when config changes
  };

  const handleSaveConfig = () => {
    localStorage.setItem('tradingBotConfig', JSON.stringify(config));
    setIsConfigSaved(true);
    setTimeout(() => setIsConfigSaved(false), 2000); // Hide message after 2 seconds
  };

  const handleStartBot = () => {
    onStartBot(config);
  };

  const riskToleranceOptions = [
    { value: 'low', label: 'Low Risk', description: 'Conservative approach, lower returns' },
    { value: 'medium', label: 'Medium Risk', description: 'Balanced approach, moderate returns' },
    { value: 'high', label: 'High Risk', description: 'Aggressive approach, higher potential returns' }
  ];

  const strategyOptions = [
    { value: 'momentum', label: 'Momentum Trading', description: 'Follows price trends' },
    { value: 'mean_reversion', label: 'Mean Reversion', description: 'Buys low, sells high' },
    { value: 'ml_enhanced', label: 'ML Enhanced', description: 'AI-powered decision making' },
    { value: 'multi_strategy', label: 'Multi-Strategy', description: 'Combines multiple approaches' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <CogIcon className="h-6 w-6 text-blue-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Trading Bot Configuration</h3>
        </div>
        <div className="flex items-center space-x-3">
          {isConfigSaved && (
            <span className="text-sm text-green-600 flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
              Configuration saved
            </span>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {isExpanded ? 'Collapse' : 'Configure'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="space-y-6">
          {/* Investment Amount */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
              <CurrencyDollarIcon className="h-4 w-4 mr-1" />
              Investment Amount
            </label>
            <input
              type="number"
              value={config.initial_capital}
              onChange={(e) => handleInputChange('initial_capital', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter investment amount"
              min="1000"
              step="1000"
            />
            <p className="text-xs text-gray-500 mt-1">Minimum: $1,000</p>
          </div>

          {/* Target Amount */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
              <FlagIcon className="h-4 w-4 mr-1" />
              Target Amount (Optional)
            </label>
            <input
              type="number"
              value={config.target_amount || ''}
              onChange={(e) => handleInputChange('target_amount', e.target.value ? parseFloat(e.target.value) : null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter target amount (optional)"
              min="1000"
              step="1000"
            />
            <p className="text-xs text-gray-500 mt-1">Leave empty for no target</p>
          </div>

          {/* Trading Period */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
              <CalendarIcon className="h-4 w-4 mr-1" />
              Trading Period (Days)
            </label>
            <select
              value={config.trading_period_days}
              onChange={(e) => handleInputChange('trading_period_days', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>1 Week</option>
              <option value={14}>2 Weeks</option>
              <option value={30}>1 Month</option>
              <option value={60}>2 Months</option>
              <option value={90}>3 Months</option>
              <option value={180}>6 Months</option>
              <option value={365}>1 Year</option>
            </select>
          </div>

          {/* Risk Tolerance */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
              <ShieldCheckIcon className="h-4 w-4 mr-1" />
              Risk Tolerance
            </label>
            <div className="space-y-2">
              {riskToleranceOptions.map((option) => (
                <label key={option.value} className="flex items-start">
                  <input
                    type="radio"
                    name="risk_tolerance"
                    value={option.value}
                    checked={config.risk_tolerance === option.value}
                    onChange={(e) => handleInputChange('risk_tolerance', e.target.value)}
                    className="mt-1 mr-3"
                  />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{option.label}</div>
                    <div className="text-xs text-gray-500">{option.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Trading Strategy */}
          <div>
            <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
              <ChartBarIcon className="h-4 w-4 mr-1" />
              Trading Strategy
            </label>
            <div className="space-y-2">
              {strategyOptions.map((option) => (
                <label key={option.value} className="flex items-start">
                  <input
                    type="radio"
                    name="trading_strategy"
                    value={option.value}
                    checked={config.trading_strategy === option.value}
                    onChange={(e) => handleInputChange('trading_strategy', e.target.value)}
                    className="mt-1 mr-3"
                  />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{option.label}</div>
                    <div className="text-xs text-gray-500">{option.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Advanced Settings</h4>
            
            {/* Max Position Size */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Position Size (% of portfolio)
              </label>
              <input
                type="range"
                min="0.05"
                max="0.5"
                step="0.05"
                value={config.max_position_size}
                onChange={(e) => handleInputChange('max_position_size', parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>5%</span>
                <span className="font-medium">{Math.round(config.max_position_size * 100)}%</span>
                <span>50%</span>
              </div>
            </div>

            {/* Max Daily Loss */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Daily Loss (% of portfolio)
              </label>
              <input
                type="range"
                min="0.01"
                max="0.2"
                step="0.01"
                value={config.max_daily_loss}
                onChange={(e) => handleInputChange('max_daily_loss', parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>1%</span>
                <span className="font-medium">{Math.round(config.max_daily_loss * 100)}%</span>
                <span>20%</span>
              </div>
            </div>

            {/* ML Learning */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="enable_ml_learning"
                checked={config.enable_ml_learning}
                onChange={(e) => handleInputChange('enable_ml_learning', e.target.checked)}
                className="mr-3"
              />
              <label htmlFor="enable_ml_learning" className="flex items-center text-sm text-gray-700">
                <CpuChipIcon className="h-4 w-4 mr-1" />
                Enable AI Learning
              </label>
            </div>
            <p className="text-xs text-gray-500 mt-1 ml-6">
              Bot will learn from market patterns and improve over time
            </p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between mt-6 pt-4 border-t">
        <div className="text-sm text-gray-600">
          {isRunning ? (
            <span className="flex items-center text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Bot is running
            </span>
          ) : (
            <span className="flex items-center text-gray-500">
              <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
              Bot is stopped
            </span>
          )}
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={handleSaveConfig}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <CogIcon className="h-4 w-4 mr-2" />
            Save Config
          </button>
          {isRunning ? (
            <button
              onClick={onStopBot}
              className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <StopIcon className="h-4 w-4 mr-2" />
              Stop Bot
            </button>
          ) : (
            <button
              onClick={handleStartBot}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <PlayIcon className="h-4 w-4 mr-2" />
              Start Bot
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BotConfiguration;
