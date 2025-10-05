/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from '../pages/Dashboard';
import * as stockAPI from '../services/api';

// Mock the API calls
jest.mock('../services/api');

// Mock the store
jest.mock('../store/store', () => ({
  useStore: () => ({
    currentSymbol: 'AAPL',
    currentPeriod: '1y',
    currentMarket: 'US'
  })
}));

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' })
}));

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const TestWrapper = ({ children }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('Prediction Data Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('handles prediction data structure correctly', async () => {
    // Mock the API responses with the correct nested structure
    stockAPI.stockAPI.getStockData.mockResolvedValue({
      summary: {
        current_price: 150.25,
        price_change: 2.15,
        price_change_pct: 1.45
      }
    });

    stockAPI.stockAPI.getStockInfo.mockResolvedValue({
      name: 'Apple Inc.',
      symbol: 'AAPL'
    });

    stockAPI.predictionAPI.getPrediction.mockResolvedValue({
      symbol: 'AAPL',
      prediction: {
        direction: 'bullish',
        confidence: 75.5,
        target_price: 165.50,
        timeframe: '1 week',
        reasoning: 'Strong technical indicators and positive market sentiment',
        stop_loss: 150.00,
        technical_indicators: {
          rsi: 65.2,
          sma_20: 158.75,
          volatility: 0.18,
          price_change_pct: 2.35
        }
      },
      message: 'Demo prediction data'
    });

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    // Wait for the data to load
    await waitFor(() => {
      expect(screen.getByText(/75.5/)).toBeInTheDocument();
    });

    // Check if prediction data is displayed correctly
    expect(screen.getByText('$165.50')).toBeInTheDocument(); // target_price
    expect(screen.getByText('$150.00')).toBeInTheDocument(); // stop_loss
    expect(screen.getByText('65.2')).toBeInTheDocument(); // RSI
    expect(screen.getByText('$158.75')).toBeInTheDocument(); // SMA
    expect(screen.getByText('18.0%')).toBeInTheDocument(); // volatility
    expect(screen.getByText('2.35%')).toBeInTheDocument(); // price_change_pct
  });

  test('handles missing prediction data gracefully', async () => {
    // Mock API responses with missing prediction data
    stockAPI.stockAPI.getStockData.mockResolvedValue({
      summary: {
        current_price: 150.25,
        price_change: 2.15,
        price_change_pct: 1.45
      }
    });

    stockAPI.stockAPI.getStockInfo.mockResolvedValue({
      name: 'Apple Inc.',
      symbol: 'AAPL'
    });

    stockAPI.predictionAPI.getPrediction.mockResolvedValue(null);

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    // Should not crash and should show N/A for missing data
    await waitFor(() => {
      expect(screen.getByText('N/A')).toBeInTheDocument();
    });
  });

  test('handles prediction data with missing nested properties', async () => {
    // Mock API responses with incomplete prediction data
    stockAPI.stockAPI.getStockData.mockResolvedValue({
      summary: {
        current_price: 150.25,
        price_change: 2.15,
        price_change_pct: 1.45
      }
    });

    stockAPI.stockAPI.getStockInfo.mockResolvedValue({
      name: 'Apple Inc.',
      symbol: 'AAPL'
    });

    stockAPI.predictionAPI.getPrediction.mockResolvedValue({
      symbol: 'AAPL',
      prediction: {
        confidence: 75.5
        // Missing other properties
      }
    });

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    // Should handle missing properties gracefully
    await waitFor(() => {
      expect(screen.getByText(/75.5/)).toBeInTheDocument();
    });

    // Missing properties should show as N/A
    expect(screen.getAllByText('N/A')).toHaveLength(5); // target_price, stop_loss, rsi, sma_20, volatility
  });

  test('handles API errors gracefully', async () => {
    // Mock API error
    stockAPI.stockAPI.getStockData.mockRejectedValue(new Error('API Error'));
    stockAPI.stockAPI.getStockInfo.mockRejectedValue(new Error('API Error'));
    stockAPI.predictionAPI.getPrediction.mockRejectedValue(new Error('API Error'));

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    // Should not crash and should handle errors gracefully
    await waitFor(() => {
      // The component should render without crashing
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });

  test('handles confidence calculation correctly', async () => {
    // Mock API responses
    stockAPI.stockAPI.getStockData.mockResolvedValue({
      summary: {
        current_price: 150.25,
        price_change: 2.15,
        price_change_pct: 1.45
      }
    });

    stockAPI.stockAPI.getStockInfo.mockResolvedValue({
      name: 'Apple Inc.',
      symbol: 'AAPL'
    });

    stockAPI.predictionAPI.getPrediction.mockResolvedValue({
      symbol: 'AAPL',
      prediction: {
        confidence: 85.7,
        target_price: 165.50,
        technical_indicators: {
          rsi: 65.2,
          volatility: 0.25
        }
      }
    });

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    // Check if confidence is displayed correctly
    await waitFor(() => {
      expect(screen.getByText(/85.7/)).toBeInTheDocument();
    });

    // Check if volatility percentage is calculated correctly (0.25 * 100 = 25.0%)
    expect(screen.getByText('25.0%')).toBeInTheDocument();
  });

  test('handles different confidence levels in UI', async () => {
    // Test high confidence (>= 80)
    stockAPI.stockAPI.getStockData.mockResolvedValue({
      summary: {
        current_price: 150.25,
        price_change: 2.15,
        price_change_pct: 1.45
      }
    });

    stockAPI.stockAPI.getStockInfo.mockResolvedValue({
      name: 'Apple Inc.',
      symbol: 'AAPL'
    });

    stockAPI.predictionAPI.getPrediction.mockResolvedValue({
      symbol: 'AAPL',
      prediction: {
        confidence: 85.0,
        target_price: 165.50
      }
    });

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/85.0/)).toBeInTheDocument();
    });

    // Test medium confidence (60-80)
    stockAPI.predictionAPI.getPrediction.mockResolvedValue({
      symbol: 'AAPL',
      prediction: {
        confidence: 70.0,
        target_price: 165.50
      }
    });

    // Re-render with new data
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/70.0/)).toBeInTheDocument();
    });

    // Test low confidence (< 60)
    stockAPI.predictionAPI.getPrediction.mockResolvedValue({
      symbol: 'AAPL',
      prediction: {
        confidence: 45.0,
        target_price: 165.50
      }
    });

    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/45.0/)).toBeInTheDocument();
    });
  });
});
