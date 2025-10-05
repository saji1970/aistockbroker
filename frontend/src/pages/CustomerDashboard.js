import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon,
  CpuChipIcon,
  BriefcaseIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  CurrencyDollarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  EyeIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const CustomerDashboard = () => {
  const { user } = useAuth();
  const [portfolioValue, setPortfolioValue] = useState(125000);
  const [dailyChange, setDailyChange] = useState(1250);
  const [changePercent, setChangePercent] = useState(1.01);
  const [topHoldings, setTopHoldings] = useState([]);
  const [recentSuggestions, setRecentSuggestions] = useState([]);

  useEffect(() => {
    // Mock data - in real app, fetch from API
    setTopHoldings([
      { symbol: 'AAPL', name: 'Apple Inc.', shares: 50, value: 7500, change: 2.5, changePercent: 0.33 },
      { symbol: 'MSFT', name: 'Microsoft Corp.', shares: 30, value: 12000, change: -150, changePercent: -1.23 },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', shares: 15, value: 21000, change: 320, changePercent: 1.55 },
      { symbol: 'TSLA', name: 'Tesla Inc.', shares: 25, value: 6000, change: -200, changePercent: -3.23 }
    ]);

    setRecentSuggestions([
      {
        id: 1,
        symbol: 'AAPL',
        action: 'BUY',
        price: 150.25,
        confidence: 85,
        reason: 'Strong earnings report and positive technical indicators',
        timestamp: new Date().toISOString(),
        status: 'pending'
      },
      {
        id: 2,
        symbol: 'TSLA',
        action: 'SELL',
        price: 245.80,
        confidence: 72,
        reason: 'Overbought conditions and resistance level reached',
        timestamp: new Date().toISOString(),
        status: 'pending'
      }
    ]);
  }, []);

  const handleSuggestionAction = (suggestionId, action) => {
    setRecentSuggestions(prev => 
      prev.map(s => 
        s.id === suggestionId 
          ? { ...s, status: action }
          : s
      )
    );
  };

  const quickActions = [
    { name: 'View Portfolio', icon: BriefcaseIcon, href: '/portfolio', color: 'bg-blue-500' },
    { name: 'AI Assistant', icon: CpuChipIcon, href: '/ai-assistant', color: 'bg-purple-500' },
    { name: 'Market Analysis', icon: ChartBarIcon, href: '/dashboard', color: 'bg-green-500' },
    { name: 'Trading Bot', icon: CogIcon, href: '/trading-bot', color: 'bg-orange-500' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Welcome back, {user?.name || 'Customer'}!</h1>
              <p className="text-gray-600">Here's your investment overview</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm text-gray-500">Portfolio Value</div>
                <div className="text-2xl font-bold text-gray-900">
                  ${portfolioValue.toLocaleString()}
                </div>
              </div>
              <div className={`flex items-center ${dailyChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {dailyChange >= 0 ? (
                  <ArrowUpIcon className="h-5 w-5 mr-1" />
                ) : (
                  <ArrowDownIcon className="h-5 w-5 mr-1" />
                )}
                <span className="font-semibold">
                  ${Math.abs(dailyChange).toLocaleString()} ({changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <a
                key={index}
                href={action.href}
                className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${action.color} mb-4`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="font-medium text-gray-900">{action.name}</h3>
              </a>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Holdings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Top Holdings</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {topHoldings.map((holding, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <span className="text-sm font-medium text-gray-900">{holding.symbol}</span>
                      </div>
                      <div className="ml-3">
                        <div className="font-medium text-gray-900">{holding.symbol}</div>
                        <div className="text-sm text-gray-500">{holding.name}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-gray-900">${holding.value.toLocaleString()}</div>
                      <div className={`text-sm ${holding.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {holding.change >= 0 ? '+' : ''}{holding.changePercent.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <a href="/portfolio" className="text-indigo-600 hover:text-indigo-700 font-medium">
                  View Full Portfolio →
                </a>
              </div>
            </div>
          </div>

          {/* AI Suggestions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">AI Trading Suggestions</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {recentSuggestions.map((suggestion, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <span className="font-medium text-gray-900">{suggestion.symbol}</span>
                        <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                          suggestion.action === 'BUY' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {suggestion.action}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-gray-900">${suggestion.price}</div>
                        <div className="text-sm text-gray-500">{suggestion.confidence}% confidence</div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{suggestion.reason}</p>
                    {suggestion.status === 'pending' && (
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleSuggestionAction(suggestion.id, 'approved')}
                          className="flex-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleSuggestionAction(suggestion.id, 'rejected')}
                          className="flex-1 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                    {suggestion.status === 'approved' && (
                      <div className="text-sm text-green-600 font-medium">✓ Approved</div>
                    )}
                    {suggestion.status === 'rejected' && (
                      <div className="text-sm text-red-600 font-medium">✗ Rejected</div>
                    )}
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <a href="/ai-assistant" className="text-indigo-600 hover:text-indigo-700 font-medium">
                  Get More Suggestions →
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Market Overview */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Market Overview</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">+1.2%</div>
                <div className="text-sm text-gray-500">S&P 500</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">+0.8%</div>
                <div className="text-sm text-gray-500">NASDAQ</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">-0.3%</div>
                <div className="text-sm text-gray-500">DOW</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;

