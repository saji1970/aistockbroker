import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ProtectedRoute, { AdminRoute, GuestRoute } from './components/Auth/ProtectedRoute';
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import ProfilePage from './components/Auth/ProfilePage';
import AdminDashboard from './components/Admin/AdminDashboard';
import UserManagement from './components/Admin/UserManagement';
import TradingAccessHandler from './components/TradingAccessHandler';

// Lazy load pages
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Analysis = React.lazy(() => import('./pages/Analysis'));
const Portfolio = React.lazy(() => import('./pages/Portfolio'));
const EnhancedPortfolio = React.lazy(() => import('./pages/EnhancedPortfolio'));
const AIAssistant = React.lazy(() => import('./pages/AIAssistant'));
const AIFeatures = React.lazy(() => import('./pages/AIFeatures'));
const Backtest = React.lazy(() => import('./pages/Backtest'));
const FinancialAdvisor = React.lazy(() => import('./pages/FinancialAdvisor'));
const TradingBot = React.lazy(() => import('./pages/TradingBotNew'));

// Agent pages
const AgentDashboard = React.lazy(() => import('./pages/AgentDashboard'));
const CustomerManagement = React.lazy(() => import('./pages/CustomerManagement'));
const TradeSuggestions = React.lazy(() => import('./pages/TradeSuggestions'));

function App() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <TradingAccessHandler>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
        {/* Guest routes (only accessible when not logged in) */}
        <Route
          path="/login"
          element={
            <GuestRoute>
              <LoginForm />
            </GuestRoute>
          }
        />
        <Route
          path="/register"
          element={
            <GuestRoute>
              <RegisterForm />
            </GuestRoute>
          }
        />

        {/* Protected routes (wrapped in Layout for authenticated users) */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Navigate to="/dashboard" replace />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <Analysis />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/portfolio"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <Portfolio />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/enhanced-portfolio"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <EnhancedPortfolio />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-features"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <AIFeatures />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-assistant"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <AIAssistant />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/editor"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <div className="p-8 text-center">Strategy Editor - Coming Soon</div>
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/backtest"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <Backtest />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/financial-advisor"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <FinancialAdvisor />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/trading-bot"
          element={
            <ProtectedRoute requireTrading={true}>
              <Layout>
                <TradingBot />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* User Profile Route */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />

        {/* Admin routes */}
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <Layout>
                <AdminDashboard />
              </Layout>
            </AdminRoute>
          }
        />
                 <Route
                   path="/admin/users"
                   element={
                     <AdminRoute>
                       <Layout>
                         <UserManagement />
                       </Layout>
                     </AdminRoute>
                   }
                 />

                 {/* Agent routes */}
                 <Route
                   path="/agent"
                   element={
                     <ProtectedRoute>
                       <Layout>
                         <AgentDashboard />
                       </Layout>
                     </ProtectedRoute>
                   }
                 />
                 <Route
                   path="/agent/dashboard"
                   element={
                     <ProtectedRoute>
                       <Layout>
                         <AgentDashboard />
                       </Layout>
                     </ProtectedRoute>
                   }
                 />
                 <Route
                   path="/agent/customers"
                   element={
                     <ProtectedRoute>
                       <Layout>
                         <CustomerManagement />
                       </Layout>
                     </ProtectedRoute>
                   }
                 />
                 <Route
                   path="/agent/suggestions"
                   element={
                     <ProtectedRoute>
                       <Layout>
                         <TradeSuggestions />
                       </Layout>
                     </ProtectedRoute>
                   }
                 />

                 {/* Redirect to login if not authenticated */}
                 {!isAuthenticated && <Route path="*" element={<Navigate to="/login" replace />} />}
      </Routes>
    </Suspense>
    </TradingAccessHandler>
  );
}

export default App;