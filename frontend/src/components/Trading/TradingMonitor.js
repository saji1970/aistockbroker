import React, { useState, useEffect } from 'react';
import {
  EyeIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CpuChipIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

const TradingMonitor = ({ botData, performance, orders, mlInsights }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercent = (percent) => {
    if (percent === undefined || percent === null || isNaN(percent)) {
      return '0.00%';
    }
    return `${percent >= 0 ? '+' : ''}${percent.toFixed(2)}%`;
  };

  const getPerformanceColor = (value) => {
    if (value >= 0) return 'text-green-600';
    return 'text-red-600';
  };

  const getPerformanceBgColor = (value) => {
    if (value >= 0) return 'bg-green-50';
    return 'bg-red-50';
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: EyeIcon },
    { id: 'trades', label: 'Recent Trades', icon: ChartBarIcon },
    { id: 'performance', label: 'Performance', icon: ArrowTrendingUpIcon },
    { id: 'insights', label: 'AI Insights', icon: CpuChipIcon }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Trading Monitor</h3>
          <div className="flex items-center text-sm text-gray-500">
            <ClockIcon className="h-4 w-4 mr-1" />
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 py-3 border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-1 py-2 text-sm font-medium border-b-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Total Value</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(botData?.total_value || 0)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Total Return</p>
                    <p className={`text-lg font-semibold ${getPerformanceColor(performance?.total_return_percent || 0)}`}>
                      {formatPercent(performance?.total_return_percent || 0)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <ChartBarIcon className="h-8 w-8 text-purple-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Active Positions</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {Object.keys(botData?.positions || {}).length}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <CpuChipIcon className="h-8 w-8 text-orange-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">AI Accuracy</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {mlInsights?.accuracy_score ? `${(mlInsights.accuracy_score * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Portfolio Breakdown */}
            <div>
              <h4 className="text-sm font-medium text-gray-900 mb-3">Portfolio Breakdown</h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm text-gray-600">Cash</span>
                  <span className="font-medium">{formatCurrency(botData?.cash || 0)}</span>
                </div>
                {Object.entries(botData?.positions || {}).map(([symbol, position]) => (
                  <div key={symbol} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="text-sm font-medium text-gray-900">{symbol}</span>
                      <span className="text-xs text-gray-500 ml-2">{position?.quantity || 0} shares</span>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatCurrency(position?.value || 0)}</div>
                      <div className={`text-xs ${getPerformanceColor(position?.pnl_percent || 0)}`}>
                        {formatPercent(position?.pnl_percent || 0)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trades' && (
          <div className="space-y-4">
            <h4 className="text-sm font-medium text-gray-900">Recent Trading Activity</h4>
            {orders && orders.length > 0 ? (
              <div className="space-y-3">
                {orders.slice(0, 10).map((order, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        (order?.side?.toLowerCase() === 'buy') ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <div>
                        <div className="font-medium text-gray-900">
                          {order?.side?.toUpperCase() || 'UNKNOWN'} {order?.symbol || 'N/A'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {order?.quantity || 0} shares @ {formatCurrency(order?.price || 0)}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{formatCurrency((order?.quantity || 0) * (order?.price || 0))}</div>
                      <div className="text-sm text-gray-500">
                        {order?.timestamp ? new Date(order.timestamp).toLocaleString() : 'N/A'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <ChartBarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>No trades yet. Bot will start trading based on market conditions.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="space-y-6">
            <h4 className="text-sm font-medium text-gray-900">Performance Metrics</h4>
            
            {/* Performance Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className={`p-4 rounded-lg ${getPerformanceBgColor(performance?.total_return_percent || 0)}`}>
                <div className="flex items-center">
                  <ArrowTrendingUpIcon className="h-6 w-6 text-gray-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Total Return</p>
                    <p className={`text-xl font-semibold ${getPerformanceColor(performance?.total_return_percent || 0)}`}>
                      {formatPercent(performance?.total_return_percent || 0)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <ArrowTrendingDownIcon className="h-6 w-6 text-gray-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Max Drawdown</p>
                    <p className="text-xl font-semibold text-gray-900">
                      {formatPercent(performance?.max_drawdown || 0)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <ChartBarIcon className="h-6 w-6 text-gray-600" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">Sharpe Ratio</p>
                    <p className="text-xl font-semibold text-gray-900">
                      {(performance?.sharpe_ratio || 0).toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Performance Chart Placeholder */}
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <ChartBarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p className="text-gray-500">Performance chart will be displayed here</p>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-6">
            <h4 className="text-sm font-medium text-gray-900">AI Learning Insights</h4>
            
            {mlInsights ? (
              <div className="space-y-4">
                {/* Market Conditions */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <LightBulbIcon className="h-5 w-5 text-blue-600 mr-2" />
                    <h5 className="font-medium text-blue-900">Current Market Conditions</h5>
                  </div>
                  <p className="text-sm text-blue-800">{mlInsights.market_conditions || 'Analyzing market patterns...'}</p>
                </div>

                {/* Learning Progress */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2">Patterns Learned</h5>
                    <p className="text-2xl font-semibold text-gray-900">{mlInsights.patterns_learned || 0}</p>
                    <p className="text-sm text-gray-500">Market patterns identified</p>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2">Prediction Accuracy</h5>
                    <p className="text-2xl font-semibold text-gray-900">
                      {mlInsights.accuracy_score ? `${(mlInsights.accuracy_score * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                    <p className="text-sm text-gray-500">AI prediction accuracy</p>
                  </div>
                </div>

                {/* Recommendations */}
                {mlInsights.recommendations && mlInsights.recommendations.length > 0 && (
                  <div>
                    <h5 className="font-medium text-gray-900 mb-3">AI Recommendations</h5>
                    <div className="space-y-2">
                      {mlInsights.recommendations.map((rec, index) => (
                        <div key={index} className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <p className="text-sm text-green-800">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <CpuChipIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>AI learning is not enabled or no insights available yet.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TradingMonitor;
