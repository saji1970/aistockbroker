/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Dashboard from '../components/Dashboard/Dashboard';
import { StoreProvider } from '../context/StoreContext';

// Mock the API calls
jest.mock('../services/api', () => ({
  getStockData: jest.fn(() => Promise.resolve({
    data: [
      { date: '2023-01-01', close: 150, volume: 1000000 },
      { date: '2023-01-02', close: 151, volume: 1100000 }
    ]
  })),
  getPortfolio: jest.fn(() => Promise.resolve({
    total_value: 100000,
    cash: 20000,
    positions: { AAPL: { quantity: 100, value: 15000 } }
  })),
  getPrediction: jest.fn(() => Promise.resolve({
    prediction: 'buy',
    confidence: 0.8,
    reasoning: 'Strong technical indicators'
  }))
}));

// Mock the trading bot API
jest.mock('../services/tradingBotAPI', () => ({
  getStatus: jest.fn(() => Promise.resolve({
    status: 'running',
    bot_active: true,
    last_update: '2023-01-01T00:00:00Z'
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

const MockedDashboard = () => (
  <StoreProvider>
    <Dashboard />
  </StoreProvider>
);

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders dashboard without crashing', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    });
  });

  test('displays portfolio summary', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Portfolio Value/i)).toBeInTheDocument();
      expect(screen.getByText(/\$100,000/)).toBeInTheDocument();
    });
  });

  test('displays trading bot status', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Trading Bot Status/i)).toBeInTheDocument();
      expect(screen.getByText(/Running/i)).toBeInTheDocument();
    });
  });

  test('displays watchlist', async () => {
    render(<MockedDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Watchlist/i)).toBeInTheDocument();
      expect(screen.getByText(/AAPL/)).toBeInTheDocument();
      expect(screen.getByText(/TSLA/)).toBeInTheDocument();
    });
  });

  test('handles refresh button click', async () => {
    render(<MockedDashboard />);
    
    const refreshButton = screen.getByText(/Refresh/i);
    fireEvent.click(refreshButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    });
  });
});
