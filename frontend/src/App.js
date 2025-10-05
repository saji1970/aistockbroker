import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ProtectedRoute, { AdminRoute, GuestRoute } from './components/Auth/ProtectedRoute';
import RegisterForm from './components/Auth/RegisterForm';
import ProfilePage from './components/Auth/ProfilePage';
import AdminDashboard from './components/Admin/AdminDashboard';
import UserManagement from './components/Admin/UserManagement';
import AIPromptManager from './components/Admin/AIPromptManager';
import TradingAccessHandler from './components/TradingAccessHandler';
import ScrollToTop from './components/ScrollToTop';

// Lazy load pages
const Homepage = React.lazy(() => import('./pages/Homepage'));
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const CustomerDashboard = React.lazy(() => import('./pages/CustomerDashboard'));
const Portfolio = React.lazy(() => import('./pages/Portfolio'));
const AIAssistant = React.lazy(() => import('./pages/AIAssistant'));
const Backtest = React.lazy(() => import('./pages/Backtest'));
const TradingBot = React.lazy(() => import('./pages/TradingBotNew'));

// Agent pages
const AgentDashboard = React.lazy(() => import('./pages/AgentDashboard'));

// Role-based route component
const RoleBasedRoute = ({ children, requiredRoles }) => {
  const { user, hasAnyRole } = useAuth();
  
  if (!user || !hasAnyRole(requiredRoles)) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

function App() {
  const { isLoading, user, isAdmin } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <TradingAccessHandler>
      <ScrollToTop />
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
        {/* Homepage - accessible to everyone, shows different content based on auth status */}
        <Route
          path="/"
          element={<Homepage />}
        />

        {/* Guest routes (only accessible when not logged in) */}
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
          path="/dashboard"
          element={
            <ProtectedRoute>
              {isAdmin() ? (
                <Layout>
                  <Dashboard />
                </Layout>
              ) : user?.role === 'agent' ? (
                <Layout>
                  <AgentDashboard />
                </Layout>
              ) : (
                <Layout>
                  <CustomerDashboard />
                </Layout>
              )}
            </ProtectedRoute>
          }
        />
        <Route
          path="/portfolio"
          element={
            <ProtectedRoute>
              <RoleBasedRoute requiredRoles={['customer', 'user', 'agent', 'admin']}>
                <Layout>
                  <Portfolio />
                </Layout>
              </RoleBasedRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/ai-assistant"
          element={
            <ProtectedRoute>
              <RoleBasedRoute requiredRoles={['customer', 'user', 'agent', 'admin']}>
                <AIAssistant />
              </RoleBasedRoute>
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
                 <Route
                   path="/admin/ai-prompts"
                   element={
                     <AdminRoute>
                       <Layout>
                         <AIPromptManager />
                       </Layout>
                     </AdminRoute>
                   }
                 />

                 {/* Agent routes */}
                 <Route
                   path="/agent"
                   element={
                     <ProtectedRoute>
                       <RoleBasedRoute requiredRoles={['agent', 'admin']}>
                         <Layout>
                           <AgentDashboard />
                         </Layout>
                       </RoleBasedRoute>
                     </ProtectedRoute>
                   }
                 />
                 <Route
                   path="/agent/dashboard"
                   element={
                     <ProtectedRoute>
                       <RoleBasedRoute requiredRoles={['agent', 'admin']}>
                         <Layout>
                           <AgentDashboard />
                         </Layout>
                       </RoleBasedRoute>
                     </ProtectedRoute>
                   }
                 />

                 {/* Redirect to homepage for unknown routes */}
                 <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
    </TradingAccessHandler>
  );
}

export default App;