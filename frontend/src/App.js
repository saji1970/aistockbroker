import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import LoadingSpinner from './components/UI/LoadingSpinner';

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

function App() {
  return (
    <Layout>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/enhanced-portfolio" element={<EnhancedPortfolio />} />
          <Route path="/ai-features" element={<AIFeatures />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />
          <Route path="/editor" element={<div className="p-8 text-center">Strategy Editor - Coming Soon</div>} />
          <Route path="/backtest" element={<Backtest />} />
          <Route path="/financial-advisor" element={<FinancialAdvisor />} />
          <Route path="/trading-bot" element={<TradingBot />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}

export default App;