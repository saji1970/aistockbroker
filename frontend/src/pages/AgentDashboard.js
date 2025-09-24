import React, { useState, useEffect } from 'react';
import {
  UserGroupIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  TrendingUpIcon,
  PlusIcon,
  EyeIcon,
  CogIcon,
  BellIcon
} from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';

const AgentDashboard = () => {
  const [customers, setCustomers] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalCustomers: 0,
    activePortfolios: 0,
    totalValue: 0,
    pendingSuggestions: 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    loadAgentData();
  }, []);

  const loadAgentData = async () => {
    try {
      setLoading(true);
      
      // Mock data for now - in production, this would fetch from API
      const mockCustomers = [
        {
          id: 1,
          name: 'John Smith',
          email: 'john@example.com',
          tier: 'Premium',
          portfolioValue: 125000,
          riskTolerance: 'Medium',
          lastActivity: '2 hours ago',
          status: 'Active'
        },
        {
          id: 2,
          name: 'Sarah Johnson',
          email: 'sarah@example.com',
          tier: 'Standard',
          portfolioValue: 75000,
          riskTolerance: 'Low',
          lastActivity: '1 day ago',
          status: 'Active'
        },
        {
          id: 3,
          name: 'Mike Wilson',
          email: 'mike@example.com',
          tier: 'Premium',
          portfolioValue: 200000,
          riskTolerance: 'High',
          lastActivity: '3 hours ago',
          status: 'Active'
        }
      ];

      const mockSuggestions = [
        {
          id: 1,
          customerName: 'John Smith',
          symbol: 'AAPL',
          action: 'BUY',
          confidence: 0.85,
          expectedReturn: 0.12,
          reason: 'Strong earnings growth and technical indicators',
          timestamp: '2 hours ago'
        },
        {
          id: 2,
          customerName: 'Sarah Johnson',
          symbol: 'TSLA',
          action: 'SELL',
          confidence: 0.78,
          expectedReturn: -0.08,
          reason: 'Market volatility and overvaluation concerns',
          timestamp: '4 hours ago'
        }
      ];

      setCustomers(mockCustomers);
      setSuggestions(mockSuggestions);
      setStats({
        totalCustomers: mockCustomers.length,
        activePortfolios: mockCustomers.filter(c => c.status === 'Active').length,
        totalValue: mockCustomers.reduce((sum, c) => sum + c.portfolioValue, 0),
        pendingSuggestions: mockSuggestions.length
      });
    } catch (error) {
      console.error('Error loading agent data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomerClick = (customerId) => {
    navigate(`/agent/customers/${customerId}`);
  };

  const handleSuggestionClick = (suggestionId) => {
    navigate(`/agent/suggestions/${suggestionId}`);
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
          <h1 className="text-3xl font-bold text-gray-900">Agent Dashboard</h1>
          <p className="mt-2 text-gray-600">Manage your customers and trading suggestions</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Customers</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.totalCustomers}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Active Portfolios</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.activePortfolios}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Value</p>
                <p className="text-2xl font-semibold text-gray-900">
                  ${stats.totalValue.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BellIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Pending Suggestions</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.pendingSuggestions}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => navigate('/agent/customers/new')}
                className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Add Customer
              </button>
              <button
                onClick={() => navigate('/agent/suggestions')}
                className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <EyeIcon className="h-5 w-5 mr-2" />
                View Suggestions
              </button>
              <button
                onClick={() => navigate('/agent/settings')}
                className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <CogIcon className="h-5 w-5 mr-2" />
                Settings
              </button>
            </div>
          </div>
        </div>

        {/* Recent Customers */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Customers</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Portfolio Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Activity
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {customers.map((customer) => (
                  <tr
                    key={customer.id}
                    onClick={() => handleCustomerClick(customer.id)}
                    className="hover:bg-gray-50 cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{customer.name}</div>
                        <div className="text-sm text-gray-500">{customer.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        customer.tier === 'Premium' 
                          ? 'bg-purple-100 text-purple-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {customer.tier}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${customer.portfolioValue.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        customer.riskTolerance === 'High' 
                          ? 'bg-red-100 text-red-800' 
                          : customer.riskTolerance === 'Medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {customer.riskTolerance}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                        {customer.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {customer.lastActivity}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Suggestions */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent AI Suggestions</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Expected Return
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {suggestions.map((suggestion) => (
                  <tr
                    key={suggestion.id}
                    onClick={() => handleSuggestionClick(suggestion.id)}
                    className="hover:bg-gray-50 cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {suggestion.customerName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {suggestion.symbol}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        suggestion.action === 'BUY' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {suggestion.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(suggestion.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {(suggestion.expectedReturn * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {suggestion.timestamp}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentDashboard;