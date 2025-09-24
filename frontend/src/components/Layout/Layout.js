import React, { useEffect, useState } from 'react';
import Header from './Header';
import { useStore } from '../../store/store';

const Layout = ({ children }) => {
  const { sidebarOpen } = useStore();
  const [mounted, setMounted] = useState(false);

  // Handle body scroll when mobile menu is open
  useEffect(() => {
    if (sidebarOpen) {
      document.body.classList.add('mobile-nav-open');
    } else {
      document.body.classList.remove('mobile-nav-open');
    }

    return () => {
      document.body.classList.remove('mobile-nav-open');
    };
  }, [sidebarOpen]);

  // Handle mount state for animations
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30 bg-mesh">
      {/* Background decorative elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-400/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary-400/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-3/4 left-3/4 w-64 h-64 bg-purple-400/5 rounded-full blur-2xl animate-float" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Header */}
      <Header />

      {/* Main content */}
      <main className="relative flex-1 z-10">
        <div className={`container-modern py-6 sm:py-8 lg:py-10 ${mounted ? 'animate-fade-in-up' : 'opacity-0'}`}>
          <div className="relative">
            {/* Content background with glass effect */}
            <div className="absolute inset-0 bg-white/30 backdrop-blur-sm rounded-3xl -mx-2 -my-2"></div>

            {/* Actual content */}
            <div className="relative z-10">
              {children}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 mt-20">
        <div className="container-modern">
          <div className="glass-card text-center">
            <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-600 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-sm">AI</span>
                </div>
                <span className="text-gradient font-bold">AI Stock Trading</span>
              </div>

              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                  <span>System Online</span>
                </div>
                <div>v1.0.5</div>
                <div>© 2024 AI Trading System</div>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout; 