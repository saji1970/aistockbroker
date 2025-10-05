import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ChartBarIcon,
  CpuChipIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  StarIcon,
  RocketLaunchIcon,
  CurrencyDollarIcon,
  TrendingUpIcon,
  UserIcon
} from '@heroicons/react/24/outline';

const PublicLanding = () => {
  const navigate = useNavigate();

  const features = [
    {
      name: 'AI-Powered Predictions',
      description: 'Get real-time stock predictions using advanced machine learning algorithms.',
      icon: CpuChipIcon,
      color: 'bg-blue-500'
    },
    {
      name: 'Portfolio Management',
      description: 'Track and manage your investments with comprehensive analytics.',
      icon: ChartBarIcon,
      color: 'bg-green-500'
    },
    {
      name: 'Automated Trading',
      description: 'Let AI handle your trading with sophisticated algorithms.',
      icon: RocketLaunchIcon,
      color: 'bg-purple-500'
    },
    {
      name: 'Risk Management',
      description: 'Advanced risk assessment and portfolio optimization tools.',
      icon: ShieldCheckIcon,
      color: 'bg-red-500'
    }
  ];

  const userTypes = [
    {
      title: 'Individual Investor',
      description: 'Access AI predictions, portfolio management, and trading tools',
      icon: UserIcon,
      role: 'customer',
      features: ['AI Stock Predictions', 'Portfolio Analytics', 'Trading Bot', 'Risk Assessment']
    },
    {
      title: 'Financial Agent',
      description: 'Manage multiple clients with advanced agent tools and customer insights',
      icon: UserGroupIcon,
      role: 'agent',
      features: ['Client Management', 'Agent Dashboard', 'Customer Analytics', 'Trade Suggestions']
    },
    {
      title: 'System Administrator',
      description: 'Full system access with admin controls and user management',
      icon: ShieldCheckIcon,
      role: 'admin',
      features: ['User Management', 'System Analytics', 'Admin Controls', 'All Features']
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="ml-3">
                <h1 className="text-2xl font-bold text-gray-900">AI Stock Trading</h1>
                <p className="text-sm text-gray-500">Powered by Advanced AI</p>
              </div>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => navigate('/login')}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Login
              </button>
              <button
                onClick={() => navigate('/register')}
                className="border border-indigo-600 text-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-50 transition-colors"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI-Powered Stock Trading
            <span className="text-indigo-600"> Platform</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Experience the future of trading with our advanced AI system that provides real-time predictions, 
            portfolio management, and automated trading strategies.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/login')}
              className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center"
            >
              Get Started
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="border border-indigo-600 text-indigo-600 px-8 py-3 rounded-lg hover:bg-indigo-50 transition-colors"
            >
              View Demo
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Powerful Features for Every Investor
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our platform provides comprehensive tools for individual investors, financial agents, and administrators.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${feature.color} mb-4`}>
                  <feature.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.name}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* User Types Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Choose Your Role
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Select the type of access that best fits your needs and trading goals.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {userTypes.map((userType, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow">
                <div className="text-center mb-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
                    <userType.icon className="h-8 w-8 text-indigo-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{userType.title}</h3>
                  <p className="text-gray-600">{userType.description}</p>
                </div>

                <div className="space-y-3 mb-8">
                  {userType.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="flex items-center">
                      <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => navigate(`/login?role=${userType.role}`)}
                  className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center"
                >
                  Login as {userType.title}
                  <ArrowRightIcon className="ml-2 h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-white mb-2">95%</div>
              <div className="text-indigo-200">Prediction Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white mb-2">$2.5M+</div>
              <div className="text-indigo-200">Assets Under Management</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white mb-2">24/7</div>
              <div className="text-indigo-200">AI Monitoring</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white mb-2">1000+</div>
              <div className="text-indigo-200">Active Users</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Join thousands of investors who are already using AI to make smarter trading decisions.
          </p>
          <button
            onClick={() => navigate('/register')}
            className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center mx-auto"
          >
            Start Your Journey
            <RocketLaunchIcon className="ml-2 h-5 w-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <ChartBarIcon className="h-8 w-8 text-indigo-400" />
                <span className="ml-2 text-xl font-bold">AI Stock Trading</span>
              </div>
              <p className="text-gray-400">
                Advanced AI-powered trading platform for modern investors.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li>AI Predictions</li>
                <li>Portfolio Management</li>
                <li>Automated Trading</li>
                <li>Risk Assessment</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Account Types</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Individual Investor</li>
                <li>Financial Agent</li>
                <li>Administrator</li>
                <li>Demo Account</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Help Center</li>
                <li>Documentation</li>
                <li>Contact Support</li>
                <li>API Access</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 AI Stock Trading Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PublicLanding;
