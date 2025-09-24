/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import StockAnalysis from '../components/StockAnalysis/StockAnalysis';
import { StoreProvider } from '../context/StoreContext';

// Mock the API calls
jest.mock('../services/api', () => ({
  getStockData: jest.fn(() => Promise.resolve({
    data: [
      { date: '2023-01-01', open: 150, high: 155, low: 148, close: 152, volume: 1000000 },
      { date: '2023-01-02', open: 152, high: 158, low: 150, close: 156, volume: 1100000 },
      { date: '2023-01-03', open: 156, high: 160, low: 154, close: 158, volume: 1200000 }
    ]
  })),
  getStockInfo: jest.fn(() => Promise.resolve({
    symbol: 'AAPL',
    name: 'Apple Inc.',
    currentPrice: 158,
    marketCap: 2500000000000,
    sector: 'Technology',
    industry: 'Consumer Electronics'
  })),
  getPrediction: jest.fn(() => Promise.resolve({
    prediction: 'buy',
    confidence: 0.85,
    reasoning: 'Strong technical indicators and positive earnings outlook'
  })),
  getTechnicalIndicators: jest.fn(() => Promise.resolve({
    rsi: 65,
    macd: { macd_line: 2.5, signal_line: 2.0, histogram: 0.5 },
    bollinger_bands: { upper: 165, middle: 155, lower: 145 },
    moving_averages: { sma_20: 155, sma_50: 150, sma_200: 140 }
  }))
}));

const MockedStockAnalysis = () => (
  <StoreProvider>
    <StockAnalysis />
  </StoreProvider>
);

describe('StockAnalysis Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders stock analysis without crashing', async () => {
    render(<MockedStockAnalysis />);
    
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
  });

  test('displays stock search input', async () => {
    render(<MockedStockAnalysis />);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Enter stock symbol/i)).toBeInTheDocument();
    });
  });

  test('handles stock symbol input', async () => {
    render(<MockedStockAnalysis />);
    
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    expect(input.value).toBe('AAPL');
  });

  test('handles analyze button click', async () => {
    render(<MockedStockAnalysis />);
    
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Apple Inc./)).toBeInTheDocument();
    });
  });

  test('displays stock information', async () => {
    render(<MockedStockAnalysis />);
    
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Apple Inc./)).toBeInTheDocument();
      expect(screen.getByText(/\$158/)).toBeInTheDocument();
      expect(screen.getByText(/Technology/)).toBeInTheDocument();
    });
  });

  test('displays price chart', async () => {
    render(<MockedStockAnalysis />);
    
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Price Chart/i)).toBeInTheDocument();
    });
  });

  test('displays technical indicators', async () => {
    render(<MockedStockAnalysis />);
    
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Technical Indicators/i)).toBeInTheDocument();
      expect(screen.getByText(/RSI/i)).toBeInTheDocument();
      expect(screen.getByText(/MACD/i)).toBeInTheDocument();
      expect(screen.getByText(/Bollinger Bands/i)).toBeInTheDocument();
    });
  });

  test('displays AI prediction', async () => {
    render(<MockedStockAnalysis />);
    
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    fireEvent.change(input, { target: { value: 'AAPL' } });
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    await waitFor(() => {
      expect(screen.getByText(/AI Prediction/i)).toBeInTheDocument();
      expect(screen.getByText(/BUY/i)).toBeInTheDocument();
      expect(screen.getByText(/85%/)).toBeInTheDocument();
    });
  });

  test('handles time period selection', async () => {
    render(<MockedStockAnalysis />);
    
    const timePeriodSelect = screen.getByText(/1M/i);
    fireEvent.click(timePeriodSelect);
    
    await waitFor(() => {
      expect(screen.getByText(/1M/)).toBeInTheDocument();
    });
  });

  test('handles refresh data', async () => {
    render(<MockedStockAnalysis />);
    
    const refreshButton = screen.getByText(/Refresh/i);
    fireEvent.click(refreshButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
  });
});
