/**
 * @jest-environment jsdom
 */

import { api } from '../services/api';
import { tradingBotAPI } from '../services/tradingBotAPI';
import { huggingfaceAI } from '../services/huggingfaceAI';

// Mock fetch globally
global.fetch = jest.fn();

describe('API Services', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  describe('API Service', () => {
    test('getStockData makes correct API call', async () => {
      const mockData = {
        data: [
          { date: '2023-01-01', close: 150, volume: 1000000 },
          { date: '2023-01-02', close: 151, volume: 1100000 }
        ]
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await api.getStockData('AAPL', '1y', '1d');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/stock/data/AAPL?period=1y&interval=1d&market=US'
      );
      expect(result).toEqual(mockData);
    });

    test('getStockInfo makes correct API call', async () => {
      const mockInfo = {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        currentPrice: 158,
        marketCap: 2500000000000
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockInfo,
      });

      const result = await api.getStockInfo('AAPL');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/stock/info/AAPL?market=US'
      );
      expect(result).toEqual(mockInfo);
    });

    test('getPrediction makes correct API call', async () => {
      const mockPrediction = {
        prediction: 'buy',
        confidence: 0.85,
        reasoning: 'Strong technical indicators'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPrediction,
      });

      const result = await api.getPrediction('AAPL');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/prediction/AAPL'
      );
      expect(result).toEqual(mockPrediction);
    });

    test('getPortfolio makes correct API call', async () => {
      const mockPortfolio = {
        total_value: 100000,
        cash: 20000,
        positions: { AAPL: { quantity: 100, value: 15000 } }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPortfolio,
      });

      const result = await api.getPortfolio();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/portfolio'
      );
      expect(result).toEqual(mockPortfolio);
    });

    test('handles API errors correctly', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(api.getStockData('AAPL')).rejects.toThrow('Network error');
    });
  });

  describe('Trading Bot API Service', () => {
    test('getStatus makes correct API call', async () => {
      const mockStatus = {
        status: 'running',
        bot_active: true,
        last_update: '2023-01-01T00:00:00Z'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatus,
      });

      const result = await tradingBotAPI.getStatus();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/status'
      );
      expect(result).toEqual(mockStatus);
    });

    test('startBot makes correct API call', async () => {
      const mockResponse = {
        success: true,
        message: 'Trading bot started successfully'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const config = { initial_capital: 100000 };
      const result = await tradingBotAPI.startBot(config);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/start',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('stopBot makes correct API call', async () => {
      const mockResponse = {
        success: true,
        message: 'Trading bot stopped successfully'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await tradingBotAPI.stopBot();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/stop',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('getAllBotData makes correct API call', async () => {
      const mockData = {
        status: { status: 'running' },
        portfolio: { total_value: 100000 },
        orders: [],
        watchlist: { watchlist: ['AAPL', 'TSLA'] },
        strategies: {},
        performance: { total_return: 0.05 }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await tradingBotAPI.getAllBotData();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8080/api/status'
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('Hugging Face AI Service', () => {
    test('analyzeStock makes correct API call', async () => {
      const mockAnalysis = {
        analysis: 'AAPL shows strong bullish momentum',
        confidence: 0.85,
        recommendation: 'BUY'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalysis,
      });

      const result = await huggingfaceAI.analyzeStock('AAPL', {});

      expect(fetch).toHaveBeenCalledWith(
        'https://api-inference.huggingface.co/models/gpt2',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer your_huggingface_api_key_here',
            'Content-Type': 'application/json'
          })
        })
      );
      expect(result).toEqual(mockAnalysis);
    });

    test('generateInsights makes correct API call', async () => {
      const mockInsights = {
        insights: 'Market sentiment is positive',
        key_points: ['Strong earnings growth', 'Positive analyst ratings']
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockInsights,
      });

      const result = await huggingfaceAI.generateInsights('market analysis');

      expect(fetch).toHaveBeenCalledWith(
        'https://api-inference.huggingface.co/models/gpt2',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer your_huggingface_api_key_here',
            'Content-Type': 'application/json'
          })
        })
      );
      expect(result).toEqual(mockInsights);
    });

    test('handles API errors correctly', async () => {
      fetch.mockRejectedValueOnce(new Error('API error'));

      await expect(huggingfaceAI.analyzeStock('AAPL', {})).rejects.toThrow('API error');
    });
  });
});
