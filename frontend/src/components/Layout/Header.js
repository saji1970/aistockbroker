import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Bars3Icon, XMarkIcon, SparklesIcon, UserIcon, CogIcon, ShieldCheckIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import { useStore } from '../../store/store';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { sidebarOpen, toggleSidebar } = useStore();
  const { user, logout, isAdmin } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    document.addEventListener('scroll', handleScroll, { passive: true });
    return () => document.removeEventListener('scroll', handleScroll);
  }, [scrolled]);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuOpen && !event.target.closest('.user-menu-container')) {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [userMenuOpen]);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊', description: 'Overview & Analytics' },
    { name: 'AI Assistant', href: '/ai-assistant', icon: '🤖', description: 'AI Trading Assistant' },
    { name: 'Portfolio', href: '/portfolio', icon: '💼', description: 'Portfolio Management' },
    { name: 'Enhanced Portfolio', href: '/enhanced-portfolio', icon: '💎', description: 'Advanced Portfolio' },
    { name: 'Analysis', href: '/analysis', icon: '📈', description: 'Market Analysis' },
    { name: 'Trading Bot', href: '/trading-bot', icon: '🚀', description: 'Automated Trading' },
    { name: 'Backtest', href: '/backtest', icon: '🧪', description: 'Strategy Testing' },
    { name: 'AI Features', href: '/ai-features', icon: '⚡', description: 'AI Tools & Features' },
    { name: 'Agent Dashboard', href: '/agent', icon: '👨‍💼', description: 'Agent Management' },
    { name: 'Customers', href: '/agent/customers', icon: '👥', description: 'Customer Management' },
    { name: 'Trade Suggestions', href: '/agent/suggestions', icon: '💡', description: 'AI Trade Suggestions' },
  ];

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Error logging out');
    }
    setUserMenuOpen(false);
  };

  const getUserDisplayName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user?.username || user?.email || 'User';
  };

  const getUserInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    if (user?.username) {
      return user.username[0].toUpperCase();
    }
    return 'U';
  };

  return (
    <header className={`sticky top-0 z-50 transition-all duration-300 ${
      scrolled
        ? 'glass-nav shadow-modern-lg backdrop-blur-xl bg-white/90'
        : 'glass-nav backdrop-blur-md bg-white/80'
    }`}>
      <div className="container-modern">
        <div className="flex justify-between items-center h-16">
          {/* Mobile Menu Button */}
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-xl text-gray-500 hover:text-primary-600 hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all duration-200 hover:scale-105 active:scale-95"
          >
            {sidebarOpen ? (
              <XMarkIcon className="h-6 w-6" />
            ) : (
              <Bars3Icon className="h-6 w-6" />
            )}
          </button>

          {/* Logo and Title */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 via-primary-600 to-secondary-600 rounded-2xl flex items-center justify-center shadow-modern group-hover:shadow-neon transition-all duration-300 group-hover:scale-105">
                <SparklesIcon className="h-5 w-5 text-white" />
              </div>
              <div className="absolute -inset-1 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-2xl opacity-30 group-hover:opacity-60 animate-pulse-glow"></div>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-gradient group-hover:scale-105 transition-transform duration-200">
                AI Stock Trading
              </h1>
              <p className="text-xs text-gray-500 font-medium">
                Powered by Advanced AI
              </p>
            </div>
            <div className="sm:hidden">
              <h1 className="text-lg font-bold text-gradient">AI Trading</h1>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center space-x-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group relative px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 hover:-translate-y-0.5 ${
                    isActive
                      ? 'bg-primary-100 text-primary-700 shadow-sm'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <span className="text-base">{item.icon}</span>
                    <span>{item.name}</span>
                  </div>
                  {/* Tooltip */}
                  <div className="absolute -bottom-10 left-1/2 transform -translate-x-1/2 px-3 py-1 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
                    {item.description}
                    <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-gray-900"></div>
                  </div>
                  {isActive && (
                    <div className="absolute inset-0 rounded-xl bg-primary-500 opacity-10 animate-pulse-glow"></div>
                  )}
                </Link>
              );
            })}

            {/* Download Button */}
            <div className="ml-4 pl-4 border-l border-gray-200">
              <a
                href="/download.html"
                className="btn-success text-sm px-4 py-2 inline-flex items-center space-x-2 group"
              >
                <span className="text-base group-hover:animate-bounce">📱</span>
                <span>Download App</span>
              </a>
            </div>
          </nav>

          {/* Profile/User Section */}
          <div className="hidden lg:flex items-center space-x-3">
            {isAdmin() && (
              <Link
                to="/admin"
                className="flex items-center space-x-2 px-3 py-2 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-700 transition-colors duration-200"
              >
                <ShieldCheckIcon className="h-4 w-4" />
                <span className="text-sm font-medium">Admin</span>
              </Link>
            )}

            <div className="relative user-menu-container">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 px-3 py-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-semibold">{getUserInitials()}</span>
                </div>
                <div className="text-sm">
                  <div className="font-medium text-gray-900">{getUserDisplayName()}</div>
                  <div className="text-gray-500 text-xs">{user?.role?.toUpperCase()}</div>
                </div>
              </button>

              {/* User Dropdown Menu */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                  <div className="py-1">
                    <Link
                      to="/profile"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <UserIcon className="h-4 w-4 mr-3" />
                      Profile Settings
                    </Link>
                    {isAdmin() && (
                      <>
                        <Link
                          to="/admin"
                          onClick={() => setUserMenuOpen(false)}
                          className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <ShieldCheckIcon className="h-4 w-4 mr-3" />
                          Admin Dashboard
                        </Link>
                        <Link
                          to="/admin/users"
                          onClick={() => setUserMenuOpen(false)}
                          className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <CogIcon className="h-4 w-4 mr-3" />
                          User Management
                        </Link>
                      </>
                    )}
                    <hr className="my-1" />
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {sidebarOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden" onClick={toggleSidebar}></div>

          {/* Mobile Menu */}
          <div className="lg:hidden fixed top-16 left-0 right-0 z-50 animate-fade-in-up">
            <div className="glass-card mx-4 my-4 max-h-[calc(100vh-8rem)] overflow-y-auto">
              <div className="p-6 space-y-4">
                {/* User Profile */}
                <div className="flex items-center space-x-3 p-3 rounded-xl bg-gradient-to-r from-primary-50 to-secondary-50 border border-primary-100">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-500 rounded-xl flex items-center justify-center shadow-modern">
                    <span className="text-white font-semibold">{getUserInitials()}</span>
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">{getUserDisplayName()}</div>
                    <div className="text-sm text-gray-600">{user?.role?.toUpperCase()} • {user?.status?.toUpperCase()}</div>
                  </div>
                  <Link
                    to="/profile"
                    onClick={toggleSidebar}
                    className="p-2 text-gray-500 hover:text-primary-600 transition-colors"
                  >
                    <UserIcon className="h-5 w-5" />
                  </Link>
                </div>

                {/* Navigation Links */}
                <div className="space-y-2">
                  {navigation.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        onClick={toggleSidebar}
                        className={`flex items-center space-x-3 p-4 rounded-xl transition-all duration-200 hover:-translate-y-0.5 ${
                          isActive
                            ? 'bg-primary-100 text-primary-700 shadow-sm border-l-4 border-primary-500'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 hover:shadow-sm'
                        }`}
                      >
                        <span className="text-xl">{item.icon}</span>
                        <div>
                          <div className="font-medium">{item.name}</div>
                          <div className="text-xs text-gray-500">{item.description}</div>
                        </div>
                        {isActive && (
                          <div className="ml-auto w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                        )}
                      </Link>
                    );
                  })}

                  {/* Admin Links */}
                  {isAdmin() && (
                    <>
                      <div className="pt-2 border-t border-gray-200">
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                          Admin
                        </div>
                        <Link
                          to="/admin"
                          onClick={toggleSidebar}
                          className="flex items-center space-x-3 p-4 rounded-xl text-purple-600 hover:bg-purple-50 transition-all duration-200"
                        >
                          <ShieldCheckIcon className="h-5 w-5" />
                          <div>
                            <div className="font-medium">Admin Dashboard</div>
                            <div className="text-xs text-gray-500">System overview</div>
                          </div>
                        </Link>
                        <Link
                          to="/admin/users"
                          onClick={toggleSidebar}
                          className="flex items-center space-x-3 p-4 rounded-xl text-purple-600 hover:bg-purple-50 transition-all duration-200"
                        >
                          <CogIcon className="h-5 w-5" />
                          <div>
                            <div className="font-medium">User Management</div>
                            <div className="text-xs text-gray-500">Manage users</div>
                          </div>
                        </Link>
                      </div>
                    </>
                  )}

                  {/* Logout Button */}
                  <div className="pt-2 border-t border-gray-200">
                    <button
                      onClick={handleLogout}
                      className="flex items-center space-x-3 p-4 rounded-xl text-red-600 hover:bg-red-50 transition-all duration-200 w-full"
                    >
                      <ArrowRightOnRectangleIcon className="h-5 w-5" />
                      <div>
                        <div className="font-medium">Sign Out</div>
                        <div className="text-xs text-gray-500">End session</div>
                      </div>
                    </button>
                  </div>
                </div>

                {/* Download Button */}
                <div className="pt-4 border-t border-gray-200">
                  <a
                    href="/download.html"
                    onClick={toggleSidebar}
                    className="btn-success w-full justify-center text-base group"
                  >
                    <span className="text-xl group-hover:animate-bounce mr-2">📱</span>
                    Download Mobile App
                  </a>
                </div>

                {/* Footer Info */}
                <div className="pt-4 border-t border-gray-200 text-center">
                  <p className="text-xs text-gray-500">
                    Powered by Advanced AI Technology
                  </p>
                  <div className="flex justify-center space-x-4 mt-2">
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                      <span className="text-xs text-gray-600">Online</span>
                    </div>
                    <div className="text-xs text-gray-500">v1.0.5</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </header>
  );
};

export default Header; 