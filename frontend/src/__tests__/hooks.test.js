/**
 * @jest-environment jsdom
 */

import { renderHook, act } from '@testing-library/react';
import { useTradingBot } from '../hooks/useTradingBot';
import { usePortfolio } from '../hooks/usePortfolio';
import { useStockData } from '../hooks/useStockData';

// Mock the API services
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

jest.mock('../services/api', () => ({
  getPortfolio: jest.fn(() => Promise.resolve({
    total_value: 100000,
    cash: 20000,
    positions: { AAPL: { quantity: 100, value: 15000 } }
  })),
  getStockData: jest.fn(() => Promise.resolve({
    data: [
      { date: '2023-01-01', close: 150, volume: 1000000 },
      { date: '2023-01-02', close: 151, volume: 1100000 }
    ]
  }))
}));

describe('Custom Hooks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useTradingBot', () => {
    test('initializes with default values', () => {
      const { result } = renderHook(() => useTradingBot());
      
      expect(result.current.botStatus).toBe('stopped');
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    test('fetches bot data on mount', async () => {
      const { result } = renderHook(() => useTradingBot());
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.botStatus).toBe('running');
      expect(result.current.portfolio).toBeDefined();
    });

    test('handles start bot', async () => {
      const { result } = renderHook(() => useTradingBot());
      
      await act(async () => {
        await result.current.startBot({ initial_capital: 100000 });
      });
      
      expect(result.current.botStatus).toBe('running');
    });

    test('handles stop bot', async () => {
      const { result } = renderHook(() => useTradingBot());
      
      await act(async () => {
        await result.current.stopBot();
      });
      
      expect(result.current.botStatus).toBe('stopped');
    });

    test('handles errors correctly', async () => {
      const { result } = renderHook(() => useTradingBot());
      
      // Mock an error
      const mockError = new Error('API Error');
      require('../services/tradingBotAPI').getAllBotData.mockRejectedValueOnce(mockError);
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.error).toBe('API Error');
    });
  });

  describe('usePortfolio', () => {
    test('initializes with default values', () => {
      const { result } = renderHook(() => usePortfolio());
      
      expect(result.current.portfolio).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    test('fetches portfolio data on mount', async () => {
      const { result } = renderHook(() => usePortfolio());
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.portfolio).toBeDefined();
      expect(result.current.portfolio.total_value).toBe(100000);
    });

    test('handles refresh portfolio', async () => {
      const { result } = renderHook(() => usePortfolio());
      
      await act(async () => {
        await result.current.refreshPortfolio();
      });
      
      expect(result.current.portfolio).toBeDefined();
    });

    test('handles errors correctly', async () => {
      const { result } = renderHook(() => usePortfolio());
      
      // Mock an error
      const mockError = new Error('API Error');
      require('../services/api').getPortfolio.mockRejectedValueOnce(mockError);
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.error).toBe('API Error');
    });
  });

  describe('useStockData', () => {
    test('initializes with default values', () => {
      const { result } = renderHook(() => useStockData('AAPL'));
      
      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    test('fetches stock data on mount', async () => {
      const { result } = renderHook(() => useStockData('AAPL'));
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.data).toBeDefined();
      expect(result.current.data.data).toHaveLength(2);
    });

    test('handles symbol change', async () => {
      const { result, rerender } = renderHook(
        ({ symbol }) => useStockData(symbol),
        { initialProps: { symbol: 'AAPL' } }
      );
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.data).toBeDefined();
      
      // Change symbol
      rerender({ symbol: 'TSLA' });
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.data).toBeDefined();
    });

    test('handles errors correctly', async () => {
      const { result } = renderHook(() => useStockData('INVALID'));
      
      // Mock an error
      const mockError = new Error('API Error');
      require('../services/api').getStockData.mockRejectedValueOnce(mockError);
      
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0));
      });
      
      expect(result.current.error).toBe('API Error');
    });
  });
});
