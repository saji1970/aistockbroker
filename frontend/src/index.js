import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import './index.css';
import App from './App';

// Handle chunk loading errors with cache busting
window.addEventListener('error', (event) => {
  if (event.message && event.message.includes('Loading chunk')) {
    console.warn('Chunk loading error detected, clearing cache and reloading...');
    // Clear all caches
    if ('caches' in window) {
      caches.keys().then(cacheNames => {
        cacheNames.forEach(cacheName => {
          caches.delete(cacheName);
        });
      });
    }
    // Force reload with cache busting
    window.location.reload(true);
  }
});

// Handle unhandled promise rejections for chunk loading
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason && event.reason.message && event.reason.message.includes('Loading chunk')) {
    console.warn('Chunk loading promise rejection detected, clearing cache and reloading...');
    event.preventDefault();
    // Clear all caches
    if ('caches' in window) {
      caches.keys().then(cacheNames => {
        cacheNames.forEach(cacheName => {
          caches.delete(cacheName);
        });
      });
    }
    // Force reload with cache busting
    window.location.reload(true);
  }
});

// Add cache busting for service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(registration => {
      registration.unregister();
    });
  });
  
  // Listen for force reload messages from service worker
  navigator.serviceWorker.addEventListener('message', event => {
    if (event.data && event.data.type === 'FORCE_RELOAD') {
      console.log('Service worker requested force reload - FORCING RELOAD NOW');
      // Clear all caches before reloading
      if ('caches' in window) {
        caches.keys().then(cacheNames => {
          cacheNames.forEach(cacheName => {
            caches.delete(cacheName);
          });
        });
      }
      // Force reload with cache bypass
      window.location.reload(true);
    }
  });
}

// Force cache busting comment - v2

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter 
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
        scrollRestoration="manual"
      >
        <AuthProvider>
          <App />
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);

// Force new build hash - bot status fix - cache bust
console.log('Bot status fix deployed'); 