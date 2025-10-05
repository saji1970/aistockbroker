import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ModernIcon, { IconButton, IconGroup } from '../components/UI/ModernIcon';
import toast from 'react-hot-toast';

const Homepage = () => {
  const { user, isAuthenticated, isLoading, login, updateSelectedRole } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Login form state
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [loginData, setLoginData] = useState({
    emailOrUsername: '',
    password: '',
    rememberMe: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginErrors, setLoginErrors] = useState({});
  const [availableRoles, setAvailableRoles] = useState([]);
  const [showRoleSelection, setShowRoleSelection] = useState(false);
  const [loginResult, setLoginResult] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Login functions
  const handleLoginChange = (e) => {
    const { name, value, type, checked } = e.target;
    setLoginData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    if (loginErrors[name]) {
      setLoginErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateLoginForm = () => {
    const newErrors = {};
    if (!loginData.emailOrUsername.trim()) {
      newErrors.emailOrUsername = 'Username is required';
    }
    if (!loginData.password) {
      newErrors.password = 'Password is required';
    }
    setLoginErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!validateLoginForm()) return;

    console.log('🔐 Starting login process...');
    console.log('📧 Email/Username:', loginData.emailOrUsername);
    console.log('🔑 Password length:', loginData.password.length);

    setLoginLoading(true);
    try {
      const result = await login(loginData.emailOrUsername, loginData.password);
      console.log('✅ Login result:', result);
      setLoginResult(result);
      
      if (result.success) {
        console.log('🎉 Login successful, user:', result.user);
        if (result.user.has_multiple_roles && !result.user.primary_role) {
          setAvailableRoles(result.user.roles);
          setShowRoleSelection(true);
        } else {
          toast.success(`Welcome back, ${result.user.name}!`);
          setShowLoginForm(false);
          setLoginData({ emailOrUsername: '', password: '', rememberMe: false });
        }
      } else {
        console.log('❌ Login failed:', result.error || result.message);
        toast.error(result.message || 'Login failed');
      }
    } catch (error) {
      console.error('💥 Login error:', error);
      toast.error('Login failed. Please try again.');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRoleSelection = async (role) => {
    try {
      await updateSelectedRole(role);
      setShowRoleSelection(false);
      setShowLoginForm(false);
      setLoginData({ emailOrUsername: '', password: '', rememberMe: false });
      toast.success(`Welcome as ${role}!`);
    } catch (error) {
      toast.error('Failed to set role');
    }
  };

  const toggleLoginForm = () => {
    setShowLoginForm(!showLoginForm);
    setLoginErrors({});
    setLoginResult(null);
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getNavigationForRole = () => {
    if (!isAuthenticated) {
      return [
        { name: 'Dashboard', href: '/dashboard', icon: 'dashboard', description: 'Market Overview & Analytics', color: 'primary' },
        { name: 'AI Assistant', href: '/ai-assistant', icon: 'ai', description: 'AI-Powered Trading Assistant', color: 'secondary' }
      ];
    }

    if (user?.roles?.includes('admin')) {
      return [
        { name: 'Dashboard', href: '/dashboard', icon: 'dashboard', description: 'System Overview', color: 'primary' },
        { name: 'AI Assistant', href: '/ai-assistant', icon: 'ai', description: 'AI Trading Assistant', color: 'secondary' },
        { name: 'Portfolio', href: '/portfolio', icon: 'portfolio', description: 'Portfolio Management', color: 'success' },
        { name: 'Trading Bot', href: '/trading-bot', icon: 'trading', description: 'Automated Trading', color: 'warning' },
        { name: 'Backtest', href: '/backtest', icon: 'backtest', description: 'Strategy Testing', color: 'danger' },
        { name: 'Admin Panel', href: '/admin', icon: 'admin', description: 'System Administration', color: 'primary' }
      ];
    }

    if (user?.roles?.includes('agent')) {
      return [
        { name: 'Dashboard', href: '/dashboard', icon: 'dashboard', description: 'Overview & Analytics', color: 'primary' },
        { name: 'AI Assistant', href: '/ai-assistant', icon: 'ai', description: 'AI Trading Assistant', color: 'secondary' },
        { name: 'Portfolio', href: '/portfolio', icon: 'portfolio', description: 'Portfolio Management', color: 'success' },
        { name: 'Agent Dashboard', href: '/agent', icon: 'users', description: 'Customer & Suggestions Management', color: 'warning' }
      ];
    }

    // Regular customer/user role
    return [
      { name: 'Dashboard', href: '/dashboard', icon: 'dashboard', description: 'Your Investment Overview', color: 'primary' },
      { name: 'AI Assistant', href: '/ai-assistant', icon: 'ai', description: 'AI Trading Assistant', color: 'secondary' },
      { name: 'Portfolio', href: '/portfolio', icon: 'portfolio', description: 'Manage Your Investments', color: 'success' }
    ];
  };

  const getMarketStatus = () => {
    const hour = currentTime.getHours();
    const day = currentTime.getDay();
    
    // Market is closed on weekends
    if (day === 0 || day === 6) return { status: 'closed', message: 'Market Closed - Weekend' };
    
    // Market hours: 9:30 AM - 4:00 PM EST
    if (hour >= 9 && hour < 16) return { status: 'open', message: 'Market Open' };
    if (hour < 9) return { status: 'pre-market', message: 'Pre-Market' };
    return { status: 'after-hours', message: 'After Hours' };
  };

  const marketStatus = getMarketStatus();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
        <div className="text-center">
          <ModernIcon name="sparkles" size="xl" color="primary" effect="pulse" container />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      {/* Integrated Login Form - Top Left */}
      {!isAuthenticated && showLoginForm && (
        <div className="fixed top-4 left-4 z-50 w-80">
          <div className="card-glass backdrop-blur-lg border border-white/20 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Sign In</h3>
              <button
                onClick={toggleLoginForm}
                className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <ModernIcon name="close" size="sm" color="gray" />
              </button>
            </div>
            
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  name="emailOrUsername"
                  value={loginData.emailOrUsername}
                  onChange={handleLoginChange}
                  className={`input-field ${loginErrors.emailOrUsername ? 'border-red-500' : ''}`}
                  placeholder="Enter username"
                />
                {loginErrors.emailOrUsername && (
                  <p className="text-red-500 text-xs mt-1">{loginErrors.emailOrUsername}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={loginData.password}
                    onChange={handleLoginChange}
                    className={`input-field pr-10 ${loginErrors.password ? 'border-red-500' : ''}`}
                    placeholder="Enter password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <ModernIcon 
                      name={showPassword ? "eye-slash" : "eye"} 
                      size="sm" 
                      color="gray" 
                    />
                  </button>
                </div>
                {loginErrors.password && (
                  <p className="text-red-500 text-xs mt-1">{loginErrors.password}</p>
                )}
              </div>
              
              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="rememberMe"
                    checked={loginData.rememberMe}
                    onChange={handleLoginChange}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-600">Remember me</span>
                </label>
              </div>
              
              <button
                type="submit"
                disabled={loginLoading}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loginLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="loading-spinner mr-2"></div>
                    Signing in...
                  </div>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>
            
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">
                Demo: <span className="font-medium">saji / sajiai123@</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Or: <span className="font-medium">ranjit / ranjitai123@</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Role Selection Modal */}
      {showRoleSelection && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="card-glass backdrop-blur-lg border border-white/20 shadow-2xl max-w-md w-full">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">
              Select Your Role
            </h3>
            <p className="text-gray-600 text-center mb-6">
              You have multiple roles. Please select which role you'd like to use:
            </p>
            <div className="space-y-3">
              {availableRoles.map((role) => (
                <button
                  key={role}
                  onClick={() => handleRoleSelection(role)}
                  className="w-full btn-secondary text-left capitalize"
                >
                  <div className="flex items-center">
                    <ModernIcon 
                      name={role === 'admin' ? 'shield-check' : role === 'agent' ? 'users' : 'user'} 
                      size="md" 
                      color="primary" 
                      className="mr-3" 
                    />
                    {role}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-600/10 via-secondary-600/10 to-success-600/10"></div>
        <div className="relative container-modern section-padding">
          <div className="text-center max-w-4xl mx-auto">
            {/* Welcome Message */}
            <div className="mb-8">
              <h1 className="text-5xl md:text-6xl font-bold text-gradient mb-4">
                {isAuthenticated ? `${getGreeting()}, ${user?.name || 'Trader'}!` : 'AI-Powered Stock Trading'}
              </h1>
              <p className="text-xl text-gray-600 mb-6">
                {isAuthenticated 
                  ? 'Welcome back to your trading dashboard' 
                  : 'Experience the future of trading with our advanced AI technology'
                }
              </p>
            </div>

            {/* Time and Market Status */}
            <div className="flex flex-wrap justify-center items-center gap-6 mb-8">
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-xl px-4 py-2 shadow-modern">
                <ModernIcon name="clock" size="sm" color="primary" />
                <span className="text-sm font-medium text-gray-700">{formatTime(currentTime)}</span>
              </div>
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-xl px-4 py-2 shadow-modern">
                <ModernIcon 
                  name={marketStatus.status === 'open' ? 'success' : 'info'} 
                  size="sm" 
                  color={marketStatus.status === 'open' ? 'success' : 'warning'} 
                />
                <span className="text-sm font-medium text-gray-700">{marketStatus.message}</span>
              </div>
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm rounded-xl px-4 py-2 shadow-modern">
                <ModernIcon name="calendar" size="sm" color="secondary" />
                <span className="text-sm font-medium text-gray-700">{formatDate(currentTime)}</span>
              </div>
            </div>

            {/* CTA Buttons */}
            {!isAuthenticated && (
              <div className="flex flex-wrap justify-center gap-4 mb-12">
                <button onClick={toggleLoginForm} className="btn-primary">
                  Get Started Free
                  <ModernIcon name="send" size="sm" color="white" className="ml-2" />
                </button>
                <button onClick={toggleLoginForm} className="btn-secondary">
                  Sign In
                  <ModernIcon name="user" size="sm" color="primary" className="ml-2" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container-modern section-padding">
        {/* Navigation Cards */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            {isAuthenticated ? 'Your Trading Tools' : 'Why Choose Our Platform?'}
          </h2>
          
          <div className="card-grid">
            {getNavigationForRole().map((item, index) => (
              <Link
                key={item.name}
                to={item.href}
                className="card hover-lift group"
              >
                <div className="text-center">
                  <div className={`icon-container icon-container-lg icon-container-${item.color} mx-auto mb-4`}>
                    <ModernIcon 
                      name={item.icon} 
                      size="xl" 
                      color="white" 
                      effect="float"
                    />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                    {item.name}
                  </h3>
                  <p className="text-gray-600">
                    {item.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Advanced Trading Features
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="icon-container icon-container-md icon-container-primary mx-auto mb-4">
                <ModernIcon name="sparkles" size="lg" color="white" effect="pulse" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-Powered Predictions</h3>
              <p className="text-gray-600">
                Get accurate stock predictions using advanced machine learning algorithms
              </p>
            </div>
            
            <div className="text-center">
              <div className="icon-container icon-container-md icon-container-success mx-auto mb-4">
                <ModernIcon name="portfolio" size="lg" color="white" effect="float" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Portfolio Management</h3>
              <p className="text-gray-600">
                Track and optimize your investments with real-time portfolio analytics
              </p>
            </div>
            
            <div className="text-center">
              <div className="icon-container icon-container-md icon-container-warning mx-auto mb-4">
                <ModernIcon name="trading" size="lg" color="white" effect="rotate" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Automated Trading</h3>
              <p className="text-gray-600">
                Execute trades automatically based on your predefined strategies
              </p>
            </div>
          </div>
        </div>

        {/* Market Overview */}
        {isAuthenticated && (
          <div className="card mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Market Overview</h2>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-success-600">+2.4%</div>
                <div className="text-sm text-gray-600">S&P 500</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-success-600">+1.8%</div>
                <div className="text-sm text-gray-600">NASDAQ</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-danger-600">-0.5%</div>
                <div className="text-sm text-gray-600">DOW</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-success-600">+3.2%</div>
                <div className="text-sm text-gray-600">RUSSELL</div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-gray-600">
          <p>© 2024 AI Stock Trading Platform. All rights reserved.</p>
          <p className="text-sm mt-2">
            Built with modern technology for the future of trading
          </p>
        </div>
      </div>
    </div>
  );
};

export default Homepage;
