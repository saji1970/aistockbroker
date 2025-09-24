/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TradingBot from '../components/TradingBot/TradingBot';
import { StoreProvider } from '../context/StoreContext';

// Mock the trading bot API
jest.mock('../services/tradingBotAPI', () => ({
  getStatus: jest.fn(() => Promise.resolve({
    status: 'stopped',
    bot_active: false,
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
    status: { status: 'stopped' },
    portfolio: { total_value: 100000 },
    orders: [],
    watchlist: { watchlist: ['AAPL', 'TSLA'] },
    strategies: {},
    performance: { total_return: 0.05 }
  }))
}));

const MockedTradingBot = () => (
  <StoreProvider>
    <TradingBot />
  </StoreProvider>
);

describe('TradingBot Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders trading bot without crashing', async () => {
    render(<MockedTradingBot />);
    
    await waitFor(() => {
      expect(screen.getByText(/Trading Bot/i)).toBeInTheDocument();
    });
  });

  test('displays bot status', async () => {
    render(<MockedTradingBot />);
    
    await waitFor(() => {
      expect(screen.getByText(/Status/i)).toBeInTheDocument();
      expect(screen.getByText(/Stopped/i)).toBeInTheDocument();
    });
  });

  test('handles start bot button click', async () => {
    render(<MockedTradingBot />);
    
    const startButton = screen.getByText(/Start Bot/i);
    fireEvent.click(startButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Starting bot.../i)).toBeInTheDocument();
    });
  });

  test('handles stop bot button click', async () => {
    render(<MockedTradingBot />);
    
    // First start the bot
    const startButton = screen.getByText(/Start Bot/i);
    fireEvent.click(startButton);
    
    await waitFor(() => {
      const stopButton = screen.getByText(/Stop Bot/i);
      fireEvent.click(stopButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Stopping bot.../i)).toBeInTheDocument();
    });
  });

  test('displays bot configuration', async () => {
    render(<MockedTradingBot />);
    
    await waitFor(() => {
      expect(screen.getByText(/Configuration/i)).toBeInTheDocument();
    });
  });

  test('displays performance metrics', async () => {
    render(<MockedTradingBot />);
    
    await waitFor(() => {
      expect(screen.getByText(/Performance/i)).toBeInTheDocument();
      expect(screen.getByText(/Total Return/i)).toBeInTheDocument();
    });
  });

  test('handles configuration changes', async () => {
    render(<MockedTradingBot />);
    
    const configButton = screen.getByText(/Configure/i);
    fireEvent.click(configButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Bot Configuration/i)).toBeInTheDocument();
    });
  });
});
