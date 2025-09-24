import React, { useState, useEffect } from 'react';
import {
  CheckIcon,
  XMarkIcon,
  EyeIcon,
  ClockIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  ChartBarIcon,
  UserIcon
} from '@heroicons/react/24/outline';

const TradeSuggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [filteredSuggestions, setFilteredSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, pending, approved, rejected
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);

  useEffect(() => {
    loadSuggestions();
  }, []);

  useEffect(() => {
    filterSuggestions();
  }, [suggestions, filter]);

  const loadSuggestions = async () => {
    try {
      setLoading(true);
      
      // Mock data - in production, this would fetch from API
      const mockSuggestions = [
        {
          id: 1,
          customerName: 'John Smith',
          customerId: 1,
          symbol: 'AAPL',
          action: 'BUY',
          quantity: 100,
          currentPrice: 175.50,
          targetPrice: 185.00,
          confidence: 0.85,
          expectedReturn: 0.12,
          riskLevel: 'Medium',
          reason: 'Strong earnings growth and technical indicators show bullish momentum',
          timestamp: '2 hours ago',
          status: 'pending',
          aiInsights: {
            technicalScore: 0.82,
            fundamentalScore: 0.78,
            sentimentScore: 0.85,
            marketConditions: 'Bullish'
          }
        },
        {
          id: 2,
          customerName: 'Sarah Johnson',
          customerId: 2,
          symbol: 'TSLA',
          action: 'SELL',
          quantity: 50,
          currentPrice: 245.30,
          targetPrice: 220.00,
          confidence: 0.78,
          expectedReturn: -0.08,
          riskLevel: 'High',
          reason: 'Market volatility and overvaluation concerns based on P/E ratio',
          timestamp: '4 hours ago',
          status: 'pending',
          aiInsights: {
            technicalScore: 0.65,
            fundamentalScore: 0.45,
            sentimentScore: 0.60,
            marketConditions: 'Bearish'
          }
        },
        {
          id: 3,
          customerName: 'Mike Wilson',
          customerId: 3,
          symbol: 'MSFT',
          action: 'BUY',
          quantity: 75,
          currentPrice: 380.25,
          targetPrice: 400.00,
          confidence: 0.92,
          expectedReturn: 0.15,
          riskLevel: 'Low',
          reason: 'Excellent fundamentals and strong cloud growth prospects',
          timestamp: '1 hour ago',
          status: 'approved',
          aiInsights: {
            technicalScore: 0.88,
            fundamentalScore: 0.95,
            sentimentScore: 0.90,
            marketConditions: 'Very Bullish'
          }
        },
        {
          id: 4,
          customerName: 'Emily Davis',
          customerId: 4,
          symbol: 'GOOGL',
          action: 'BUY',
          quantity: 25,
          currentPrice: 142.80,
          targetPrice: 155.00,
          confidence: 0.73,
          expectedReturn: 0.08,
          riskLevel: 'Medium',
          reason: 'AI and cloud computing growth potential',
          timestamp: '6 hours ago',
          status: 'rejected',
          aiInsights: {
            technicalScore: 0.70,
            fundamentalScore: 0.75,
            sentimentScore: 0.68,
            marketConditions: 'Neutral'
          }
        }
      ];

      setSuggestions(mockSuggestions);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterSuggestions = () => {
    let filtered = suggestions;
    
    if (filter !== 'all') {
      filtered = suggestions.filter(s => s.status === filter);
    }
    
    setFilteredSuggestions(filtered);
  };

  const handleApprove = (suggestionId) => {
    setSuggestions(suggestions.map(s => 
      s.id === suggestionId ? { ...s, status: 'approved' } : s
    ));
  };

  const handleReject = (suggestionId) => {
    setSuggestions(suggestions.map(s => 
      s.id === suggestionId ? { ...s, status: 'rejected' } : s
    ));
  };

  const handleViewDetails = (suggestion) => {
    setSelectedSuggestion(suggestion);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionColor = (action) => {
    return action === 'BUY' 
      ? 'bg-green-100 text-green-800' 
      : 'bg-red-100 text-red-800';
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Low':
        return 'bg-green-100 text-green-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'High':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Trade Suggestions</h1>
          <p className="mt-2 text-gray-600">Review and manage AI-generated trading suggestions</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <ClockIcon className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pending</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {suggestions.filter(s => s.status === 'pending').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <CheckIcon className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Approved</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {suggestions.filter(s => s.status === 'approved').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <XMarkIcon className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Rejected</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {suggestions.filter(s => s.status === 'rejected').length}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total</p>
                <p className="text-2xl font-semibold text-gray-900">{suggestions.length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {[
                { key: 'all', label: 'All Suggestions', count: suggestions.length },
                { key: 'pending', label: 'Pending', count: suggestions.filter(s => s.status === 'pending').length },
                { key: 'approved', label: 'Approved', count: suggestions.filter(s => s.status === 'approved').length },
                { key: 'rejected', label: 'Rejected', count: suggestions.filter(s => s.status === 'rejected').length }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setFilter(tab.key)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    filter === tab.key
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label} ({tab.count})
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Suggestions List */}
        <div className="space-y-6">
          {filteredSuggestions.map((suggestion) => (
            <div key={suggestion.id} className="bg-white rounded-lg shadow">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="flex items-center space-x-2">
                        <UserIcon className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-medium text-gray-900">{suggestion.customerName}</span>
                      </div>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(suggestion.status)}`}>
                        {suggestion.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Symbol</p>
                        <p className="text-lg font-semibold text-gray-900">{suggestion.symbol}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Action</p>
                        <span className={`inline-flex px-2 py-1 text-sm font-semibold rounded-full ${getActionColor(suggestion.action)}`}>
                          {suggestion.action}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Quantity</p>
                        <p className="text-lg font-semibold text-gray-900">{suggestion.quantity} shares</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Current Price</p>
                        <p className="text-lg font-semibold text-gray-900">${suggestion.currentPrice}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Target Price</p>
                        <p className="text-lg font-semibold text-gray-900">${suggestion.targetPrice}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Confidence</p>
                        <p className="text-lg font-semibold text-gray-900">{(suggestion.confidence * 100).toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Expected Return</p>
                        <p className={`text-lg font-semibold ${suggestion.expectedReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {(suggestion.expectedReturn * 100).toFixed(1)}%
                        </p>
                      </div>
                    </div>

                    <div className="mb-4">
                      <p className="text-sm text-gray-500">AI Reasoning</p>
                      <p className="text-sm text-gray-900">{suggestion.reason}</p>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center">
                        <ClockIcon className="h-4 w-4 mr-1" />
                        {suggestion.timestamp}
                      </span>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(suggestion.riskLevel)}`}>
                        {suggestion.riskLevel} Risk
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-col space-y-2 ml-6">
                    {suggestion.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleApprove(suggestion.id)}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                        >
                          <CheckIcon className="h-4 w-4 mr-1" />
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(suggestion.id)}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                        >
                          <XMarkIcon className="h-4 w-4 mr-1" />
                          Reject
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => handleViewDetails(suggestion)}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <EyeIcon className="h-4 w-4 mr-1" />
                      Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Suggestion Details Modal */}
        {selectedSuggestion && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Suggestion Details
                </h3>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Customer</p>
                    <p className="text-sm text-gray-900">{selectedSuggestion.customerName}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Symbol</p>
                    <p className="text-sm text-gray-900">{selectedSuggestion.symbol}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">AI Insights</p>
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-gray-600">Technical Score: {(selectedSuggestion.aiInsights.technicalScore * 100).toFixed(1)}%</p>
                      <p className="text-xs text-gray-600">Fundamental Score: {(selectedSuggestion.aiInsights.fundamentalScore * 100).toFixed(1)}%</p>
                      <p className="text-xs text-gray-600">Sentiment Score: {(selectedSuggestion.aiInsights.sentimentScore * 100).toFixed(1)}%</p>
                      <p className="text-xs text-gray-600">Market Conditions: {selectedSuggestion.aiInsights.marketConditions}</p>
                    </div>
                  </div>
                  <div className="flex justify-end pt-4">
                    <button
                      onClick={() => setSelectedSuggestion(null)}
                      className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradeSuggestions;
