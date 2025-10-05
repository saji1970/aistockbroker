/**
 * @jest-environment jsdom
 */

import { stockAPI, predictionAPI } from '../services/api';

// Mock axios
jest.mock('axios');

import axios from 'axios';
const mockedAxios = axios;

describe('Stock Data API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('stockAPI.getStockData', () => {
    test('fetches stock data successfully', async () => {
      const mockData = {
        symbol: 'AAPL',
        price: 150.25,
        change: 2.15,
        change_percent: 1.45,
        volume: 1000000,
        data: {
          prices: [148.10, 149.25, 150.25],
          dates: ['2024-09-30', '2024-10-01', '2024-10-02'],
          volume: [950000, 1100000, 1000000]
        }
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockData });

      const result = await stockAPI.getStockData('AAPL', '1y', 'US');

      expect(result).toEqual(mockData);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/AAPL?period=1y&market=US');
    });

    test('handles parameterized stock data URL', async () => {
      const mockData = {
        symbol: 'AAPL',
        price: 150.25
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockData });

      const result = await stockAPI.getStockData('AAPL', '1y', 'US');

      expect(result).toEqual(mockData);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/AAPL?period=1y&market=US');
    });

    test('handles market-specific symbols', async () => {
      const mockData = {
        symbol: 'RELIANCE.NS',
        price: 2500.50
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockData });

      const result = await stockAPI.getStockData('RELIANCE', '1y', 'IN');

      expect(result).toEqual(mockData);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/RELIANCE.NS?period=1y&market=IN');
    });

    test('handles API errors', async () => {
      const errorResponse = {
        response: {
          status: 404,
          data: { error: 'Stock not found' }
        }
      };

      mockedAxios.get.mockRejectedValueOnce(errorResponse);

      await expect(stockAPI.getStockData('INVALID', '1y', 'US')).rejects.toThrow('Stock not found');
    });

    test('handles network errors', async () => {
      const networkError = new Error('Network error');
      mockedAxios.get.mockRejectedValueOnce(networkError);

      await expect(stockAPI.getStockData('AAPL', '1y', 'US')).rejects.toThrow('Network error');
    });
  });

  describe('stockAPI.getStockInfo', () => {
    test('fetches stock info successfully', async () => {
      const mockInfo = {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        exchange: 'NASDAQ',
        sector: 'Technology',
        market_cap: 2500000000000
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockInfo });

      const result = await stockAPI.getStockInfo('AAPL', 'US');

      expect(result).toEqual(mockInfo);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/info/AAPL?market=US');
    });

    test('handles API errors for stock info', async () => {
      const errorResponse = {
        response: {
          status: 404,
          data: { error: 'Stock info not found' }
        }
      };

      mockedAxios.get.mockRejectedValueOnce(errorResponse);

      await expect(stockAPI.getStockInfo('INVALID', 'US')).rejects.toThrow('Stock info not found');
    });
  });

  describe('predictionAPI.getPrediction', () => {
    test('fetches prediction data successfully', async () => {
      const mockPrediction = {
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
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockPrediction });

      const result = await predictionAPI.getPrediction('AAPL');

      expect(result).toEqual(mockPrediction);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/prediction/AAPL');
    });

    test('handles prediction API errors', async () => {
      const errorResponse = {
        response: {
          status: 500,
          data: { error: 'Prediction service unavailable' }
        }
      };

      mockedAxios.get.mockRejectedValueOnce(errorResponse);

      await expect(predictionAPI.getPrediction('AAPL')).rejects.toThrow('Prediction service unavailable');
    });

    test('handles network errors for predictions', async () => {
      const networkError = new Error('Network timeout');
      mockedAxios.get.mockRejectedValueOnce(networkError);

      await expect(predictionAPI.getPrediction('AAPL')).rejects.toThrow('Network timeout');
    });
  });

  describe('predictionAPI.getPredictionWithSensitivity', () => {
    test('fetches prediction with sensitivity analysis', async () => {
      const mockSensitivity = {
        symbol: 'AAPL',
        scenarios: [
          {
            scenario: 'Bullish',
            probability: 0.6,
            target_price: 170.00,
            confidence: 80
          },
          {
            scenario: 'Bearish',
            probability: 0.4,
            target_price: 140.00,
            confidence: 70
          }
        ],
        message: 'Sensitivity analysis'
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockSensitivity });

      const result = await predictionAPI.getPredictionWithSensitivity('AAPL');

      expect(result).toEqual(mockSensitivity);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/prediction/AAPL/sensitivity');
    });

    test('handles sensitivity analysis errors', async () => {
      const errorResponse = {
        response: {
          status: 503,
          data: { error: 'Sensitivity analysis service down' }
        }
      };

      mockedAxios.get.mockRejectedValueOnce(errorResponse);

      await expect(predictionAPI.getPredictionWithSensitivity('AAPL')).rejects.toThrow('Sensitivity analysis service down');
    });
  });

  describe('Market Configuration', () => {
    test('handles US market symbols correctly', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      await stockAPI.getStockData('AAPL', '1y', 'US');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/AAPL?period=1y&market=US');
    });

    test('handles UK market symbols with suffix', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      await stockAPI.getStockData('VOD', '1y', 'UK');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/VOD.L?period=1y&market=UK');
    });

    test('handles Japan market symbols with suffix', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      await stockAPI.getStockData('7203', '1y', 'JP');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/7203.T?period=1y&market=JP');
    });

    test('handles Brazil market symbols with suffix', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      await stockAPI.getStockData('VALE', '1y', 'BR');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/VALE.SA?period=1y&market=BR');
    });

    test('handles unknown market gracefully', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      await stockAPI.getStockData('TEST', '1y', 'UNKNOWN');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/TEST?period=1y&market=UNKNOWN');
    });
  });

  describe('Error Handling Edge Cases', () => {
    test('handles malformed API responses', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: null });

      const result = await stockAPI.getStockData('AAPL', '1y', 'US');

      expect(result).toBeNull();
    });

    test('handles empty API responses', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      const result = await stockAPI.getStockData('AAPL', '1y', 'US');

      expect(result).toEqual({});
    });

    test('handles API responses with error field', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: { error: 'Invalid symbol format' }
        }
      };

      mockedAxios.get.mockRejectedValueOnce(errorResponse);

      await expect(stockAPI.getStockInfo('INVALID_SYMBOL', 'US')).rejects.toThrow('Invalid symbol format');
    });

    test('handles API responses without error field', async () => {
      const errorResponse = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      };

      mockedAxios.get.mockRejectedValueOnce(errorResponse);

      await expect(stockAPI.getStockInfo('AAPL', 'US')).rejects.toThrow();
    });
  });

  describe('API Endpoint Validation', () => {
    test('uses correct base URL for all endpoints', async () => {
      mockedAxios.get.mockResolvedValue({ data: {} });

      await stockAPI.getStockData('AAPL', '1y', 'US');
      await stockAPI.getStockInfo('AAPL', 'US');
      await predictionAPI.getPrediction('AAPL');
      await predictionAPI.getPredictionWithSensitivity('AAPL');

      expect(mockedAxios.get).toHaveBeenCalledTimes(4);
      expect(mockedAxios.get).toHaveBeenNthCalledWith(1, '/api/stock/data/AAPL?period=1y&market=US');
      expect(mockedAxios.get).toHaveBeenNthCalledWith(2, '/api/stock/info/AAPL?market=US');
      expect(mockedAxios.get).toHaveBeenNthCalledWith(3, '/api/prediction/AAPL');
      expect(mockedAxios.get).toHaveBeenNthCalledWith(4, '/api/prediction/AAPL/sensitivity');
    });

    test('handles special characters in symbols', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      await stockAPI.getStockData('BRK.B', '1y', 'US');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/BRK.B?period=1y&market=US');
    });

    test('handles URL encoding for special symbols', async () => {
      mockedAxios.get.mockResolvedValueOnce({ data: {} });

      await stockAPI.getStockData('BRK/B', '1y', 'US');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/BRK/B?period=1y&market=US');
    });
  });
});
