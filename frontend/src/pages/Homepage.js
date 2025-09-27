import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  HomeIcon,
  CpuChipIcon,
  UserIcon,
  ArrowRightIcon,
  SparklesIcon,
  ChartBarIcon,
  BriefcaseIcon,
  ShieldCheckIcon,
  BoltIcon,
  BeakerIcon,
  UserGroupIcon,
  LightBulbIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Homepage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, isAdmin, isLoading } = useAuth();
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  // Mock suggestions data for regular users
  const mockSuggestions = [
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
  ];

  useEffect(() => {
    if (isAuthenticated && user?.role === 'USER') {
      setSuggestions(mockSuggestions);
      setShowSuggestions(true);
    }
  }, [isAuthenticated, user]);

  const handleApproveSuggestion = (suggestionId) => {
    setSuggestions(prev => prev.map(s => 
      s.id === suggestionId ? { ...s, status: 'approved' } : s
    ));
    // Here you would typically make an API call to approve the suggestion
  };

  const handleRejectSuggestion = (suggestionId) => {
    setSuggestions(prev => prev.map(s => 
      s.id === suggestionId ? { ...s, status: 'rejected' } : s
    ));
    // Here you would typically make an API call to reject the suggestion
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Role-based navigation
  const getNavigationForRole = () => {
    if (!isAuthenticated) {
      return [
        { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, description: 'Market Overview & Analytics' },
        { name: 'AI Assistant', href: '/ai-assistant', icon: CpuChipIcon, description: 'AI-Powered Trading Assistant' }
      ];
    }

    if (isAdmin()) {
      return [
        { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, description: 'System Overview' },
        { name: 'AI Assistant', href: '/ai-assistant', icon: CpuChipIcon, description: 'AI Trading Assistant' },
        { name: 'Portfolio', href: '/portfolio', icon: BriefcaseIcon, description: 'Portfolio Management' },
        { name: 'Trading Bot', href: '/trading-bot', icon: BoltIcon, description: 'Automated Trading' },
        { name: 'Backtest', href: '/backtest', icon: BeakerIcon, description: 'Strategy Testing' },
        { name: 'Agent Dashboard', href: '/agent', icon: UserIcon, description: 'Agent Management' },
        { name: 'Admin Panel', href: '/admin', icon: ShieldCheckIcon, description: 'System Administration' }
      ];
    }

    if (user?.role === 'AGENT') {
      return [
        { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, description: 'Overview & Analytics' },
        { name: 'AI Assistant', href: '/ai-assistant', icon: CpuChipIcon, description: 'AI Trading Assistant' },
        { name: 'Portfolio', href: '/portfolio', icon: BriefcaseIcon, description: 'Portfolio Management' },
        { name: 'Agent Dashboard', href: '/agent', icon: UserGroupIcon, description: 'Customer & Suggestions Management' }
      ];
    }

    // Regular USER role
    return [
      { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, description: 'Your Investment Overview' },
      { name: 'AI Assistant', href: '/ai-assistant', icon: CpuChipIcon, description: 'AI Trading Assistant' },
      { name: 'Portfolio', href: '/portfolio', icon: BriefcaseIcon, description: 'Manage Your Investments' }
    ];
  };

  const navigation = getNavigationForRole();

  // Public homepage (not logged in)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        {/* Hero Section */}
        <div className="relative overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center">
              <div className="flex justify-center mb-8">
                <div className="relative">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 rounded-3xl flex items-center justify-center shadow-2xl">
                    <SparklesIcon className="h-10 w-10 text-white" />
                  </div>
                  <div className="absolute -inset-2 bg-gradient-to-br from-blue-400 to-purple-500 rounded-3xl opacity-30 animate-pulse"></div>
                </div>
              </div>
              
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                AI-Powered
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"> Stock Trading</span>
              </h1>
              
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Experience the future of trading with our advanced AI technology. Get real-time insights, 
                automated strategies, and intelligent portfolio management.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => navigate('/register')}
                  className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  Get Started Free
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </button>
                <button
                  onClick={() => navigate('/login')}
                  className="inline-flex items-center px-8 py-4 bg-white text-gray-700 font-semibold rounded-xl border-2 border-gray-200 hover:border-blue-300 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                >
                  Sign In
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Choose Our Platform?</h2>
              <p className="text-lg text-gray-600">Cutting-edge AI technology meets professional trading tools</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="text-center p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 hover:shadow-lg transition-shadow">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <CpuChipIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Assistant</h3>
                <p className="text-gray-600">Get personalized trading insights and recommendations powered by advanced machine learning.</p>
              </div>

              <div className="text-center p-6 rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 hover:shadow-lg transition-shadow">
                <div className="w-16 h-16 bg-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <ChartBarIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Real-time Analytics</h3>
                <p className="text-gray-600">Access comprehensive market data and performance analytics in real-time.</p>
              </div>

              <div className="text-center p-6 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 hover:shadow-lg transition-shadow">
                <div className="w-16 h-16 bg-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <BoltIcon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Automated Trading</h3>
                <p className="text-gray-600">Let our AI trading bots execute strategies 24/7 with precision and speed.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Access Section */}
        <div className="py-16 bg-gray-50">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Quick Access</h2>
              <p className="text-lg text-gray-600">Explore our platform features</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {navigation.map((item) => (
                <button
                  key={item.name}
                  onClick={() => navigate(item.href)}
                  className="p-6 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-1 text-left group"
                >
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                      <item.icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900">{item.name}</h3>
                  </div>
                  <p className="text-gray-600 mb-4">{item.description}</p>
                  <div className="flex items-center text-blue-600 font-medium">
                    <span>Explore</span>
                    <ArrowRightIcon className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Authenticated user homepage
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.first_name || user?.username || 'User'}!
          </h1>
          <p className="mt-2 text-gray-600">
            {isAdmin() ? 'Manage your trading platform and users' : 
             user?.role === 'AGENT' ? 'Manage your customers and trading suggestions' :
             'Track your investments and manage your portfolio'}
          </p>
        </div>

        {/* Role-specific Dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Navigation */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Access</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {navigation.map((item) => (
                  <button
                    key={item.name}
                    onClick={() => navigate(item.href)}
                    className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl hover:from-blue-100 hover:to-indigo-100 transition-all duration-200 transform hover:-translate-y-1 text-left group"
                  >
                    <div className="flex items-center mb-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mr-3 group-hover:scale-110 transition-transform">
                        <item.icon className="h-5 w-5 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900">{item.name}</h3>
                    </div>
                    <p className="text-gray-600 text-sm">{item.description}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* User Suggestions Panel (for regular users) */}
          {user?.role === 'USER' && showSuggestions && (
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Trading Suggestions</h3>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                    {suggestions.filter(s => s.status === 'pending').length} New
                  </span>
                </div>
                
                <div className="space-y-4">
                  {suggestions.filter(s => s.status === 'pending').map((suggestion) => (
                    <div key={suggestion.id} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            suggestion.action === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {suggestion.action}
                          </span>
                          <span className="ml-2 font-semibold text-gray-900">{suggestion.symbol}</span>
                        </div>
                        <span className="text-sm text-gray-500">${suggestion.price}</span>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-3">{suggestion.reason}</p>
                      
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center text-xs text-gray-500">
                          <ClockIcon className="h-3 w-3 mr-1" />
                          {new Date(suggestion.timestamp).toLocaleDateString()}
                        </div>
                        <span className="text-xs font-medium text-blue-600">{suggestion.confidence}% confidence</span>
                      </div>
                      
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleApproveSuggestion(suggestion.id)}
                          className="flex-1 flex items-center justify-center px-3 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <CheckCircleIcon className="h-4 w-4 mr-1" />
                          Approve
                        </button>
                        <button
                          onClick={() => handleRejectSuggestion(suggestion.id)}
                          className="flex-1 flex items-center justify-center px-3 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
                        >
                          <XCircleIcon className="h-4 w-4 mr-1" />
                          Reject
                        </button>
                      </div>
                    </div>
                  ))}
                  
                  {suggestions.filter(s => s.status === 'pending').length === 0 && (
                    <p className="text-gray-500 text-sm text-center py-4">No new suggestions at the moment</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Role-specific info panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Status</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Role:</span>
                  <span className="text-sm font-medium text-gray-900">{user?.role}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Status:</span>
                  <span className={`text-sm font-medium ${
                    user?.status === 'ACTIVE' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {user?.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Trading Access:</span>
                  <span className={`text-sm font-medium ${
                    user?.can_access_trading ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {user?.can_access_trading ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
              
              <button
                onClick={() => navigate('/profile')}
                className="w-full mt-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Homepage;
