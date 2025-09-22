import React, { useEffect } from 'react';
import Header from './Header';
import { useStore } from '../../store/store';

const Layout = ({ children }) => {
  const { sidebarOpen, toggleSidebar } = useStore();

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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header />
      
      {/* Main content */}
      <main className="flex-1">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout; 