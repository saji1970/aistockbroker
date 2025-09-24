/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import { StoreProvider } from '../context/StoreContext';

// Mock all API services
jest.mock('../services/api', () => ({
  getStockData: jest.fn(() => Promise.resolve({
    data: [
      { date: '2023-01-01', close: 150, volume: 1000000 },
      { date: '2023-01-02', close: 151, volume: 1100000 }
    ]
  })),
  getStockInfo: jest.fn(() => Promise.resolve({
    symbol: 'AAPL',
    name: 'Apple Inc.',
    currentPrice: 158,
    marketCap: 2500000000000
  })),
  getPrediction: jest.fn(() => Promise.resolve({
    prediction: 'buy',
    confidence: 0.85,
    reasoning: 'Strong technical indicators'
  })),
  getPortfolio: jest.fn(() => Promise.resolve({
    total_value: 100000,
    cash: 20000,
    positions: { AAPL: { quantity: 100, value: 15000 } }
  }))
}));

jest.mock('../services/tradingBotAPI', () => ({
  getStatus: jest.fn(() => Promise.resolve({
    status: 'running',
    bot_active: true,
    last_update: '2023-01-01T00:00:00Z'
  })),
  startBot: jest.fn(() => Promise.resolve({
    success: true,
    message: 'Trading bot started successfully'
  })),
  stopBot: jest.fn(() => Promise.resolve({
    success: true,
    message: 'Trading bot stopped successfully'
  })),
  getAllBotData: jest.fn(() => Promise.resolve({
    status: { status: 'running' },
    portfolio: { total_value: 100000 },
    orders: [],
    watchlist: { watchlist: ['AAPL', 'TSLA'] },
    strategies: {},
    performance: { total_return: 0.05 }
  }))
}));

jest.mock('../services/huggingfaceAI', () => ({
  analyzeStock: jest.fn(() => Promise.resolve({
    analysis: 'AAPL shows strong bullish momentum',
    confidence: 0.85,
    recommendation: 'BUY'
  })),
  generateInsights: jest.fn(() => Promise.resolve({
    insights: 'Market sentiment is positive',
    key_points: ['Strong earnings growth', 'Positive analyst ratings']
  }))
}));

const MockedApp = () => (
  <BrowserRouter>
    <StoreProvider>
      <App />
    </StoreProvider>
  </BrowserRouter>
);

describe('Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('complete user workflow - analyze stock and start trading bot', async () => {
    render(<MockedApp />);
    
    // Navigate to stock analysis
    fireEvent.click(screen.getByText(/Analysis/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
    
    // Enter stock symbol
    const symbolInput = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(symbolInput, { target: { value: 'AAPL' } });
    
    // Click analyze
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Apple Inc./)).toBeInTheDocument();
      expect(screen.getByText(/BUY/)).toBeInTheDocument();
    });
    
    // Navigate to trading bot
    fireEvent.click(screen.getByText(/Trading Bot/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Trading Bot/i)).toBeInTheDocument();
    });
    
    // Start trading bot
    const startButton = screen.getByText(/Start Bot/i);
    fireEvent.click(startButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Starting bot.../i)).toBeInTheDocument();
    });
  });

  test('portfolio management workflow', async () => {
    render(<MockedApp />);
    
    // Navigate to portfolio
    fireEvent.click(screen.getByText(/Portfolio/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Portfolio Overview/i)).toBeInTheDocument();
      expect(screen.getByText(/\$100,000/)).toBeInTheDocument();
    });
    
    // Check portfolio positions
    expect(screen.getByText(/AAPL/)).toBeInTheDocument();
    expect(screen.getByText(/100 shares/)).toBeInTheDocument();
    
    // Refresh portfolio
    const refreshButton = screen.getByText(/Refresh/i);
    fireEvent.click(refreshButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Portfolio Overview/i)).toBeInTheDocument();
    });
  });

  test('AI assistant workflow', async () => {
    render(<MockedApp />);
    
    // Navigate to AI assistant
    fireEvent.click(screen.getByText(/AI Assistant/i));
    
    await waitFor(() => {
      expect(screen.getByText(/AI Assistant/i)).toBeInTheDocument();
    });
    
    // Send a message
    const input = screen.getByPlaceholderText(/Ask me anything about stocks/i);
    fireEvent.change(input, { target: { value: 'Analyze AAPL stock' } });
    
    const sendButton = screen.getByText(/Send/i);
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Analyze AAPL stock/)).toBeInTheDocument();
      expect(screen.getByText(/AAPL shows strong bullish momentum/)).toBeInTheDocument();
    });
    
    // Test quick actions
    const quickAction = screen.getByText(/Market Analysis/i);
    fireEvent.click(quickAction);
    
    await waitFor(() => {
      expect(screen.getByText(/Market sentiment is positive/)).toBeInTheDocument();
    });
  });

  test('dashboard data integration', async () => {
    render(<MockedApp />);
    
    // Should be on dashboard by default
    await waitFor(() => {
      expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    });
    
    // Check portfolio summary
    expect(screen.getByText(/Portfolio Value/i)).toBeInTheDocument();
    expect(screen.getByText(/\$100,000/)).toBeInTheDocument();
    
    // Check trading bot status
    expect(screen.getByText(/Trading Bot Status/i)).toBeInTheDocument();
    expect(screen.getByText(/Running/i)).toBeInTheDocument();
    
    // Check watchlist
    expect(screen.getByText(/Watchlist/i)).toBeInTheDocument();
    expect(screen.getByText(/AAPL/)).toBeInTheDocument();
    expect(screen.getByText(/TSLA/)).toBeInTheDocument();
  });

  test('error handling across components', async () => {
    // Mock API errors
    require('../services/api').getStockData.mockRejectedValueOnce(new Error('API Error'));
    require('../services/tradingBotAPI').getStatus.mockRejectedValueOnce(new Error('Bot API Error'));
    
    render(<MockedApp />);
    
    // Navigate to analysis
    fireEvent.click(screen.getByText(/Analysis/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
    
    // Try to analyze a stock
    const symbolInput = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(symbolInput, { target: { value: 'AAPL' } });
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    // Should handle error gracefully
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
  });

  test('navigation between all pages', async () => {
    render(<MockedApp />);
    
    // Test navigation to all pages
    const pages = ['Dashboard', 'Portfolio', 'Analysis', 'Trading Bot', 'AI Assistant'];
    
    for (const page of pages) {
      fireEvent.click(screen.getByText(new RegExp(page, 'i')));
      
      await waitFor(() => {
        expect(screen.getByText(new RegExp(page, 'i'))).toBeInTheDocument();
      });
    }
  });

  test('data persistence across navigation', async () => {
    render(<MockedApp />);
    
    // Navigate to analysis and analyze a stock
    fireEvent.click(screen.getByText(/Analysis/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
    
    const symbolInput = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(symbolInput, { target: { value: 'AAPL' } });
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Apple Inc./)).toBeInTheDocument();
    });
    
    // Navigate away and back
    fireEvent.click(screen.getByText(/Dashboard/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText(/Analysis/i));
    
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
    
    // Data should still be there
    expect(screen.getByText(/Apple Inc./)).toBeInTheDocument();
  });
});
