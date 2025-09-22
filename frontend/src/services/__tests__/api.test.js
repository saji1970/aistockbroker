import axios from 'axios';
import { dayTradingAPI, stockAPI, portfolioAPI } from '../api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('API Service Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('dayTradingAPI', () => {
    describe('getDayTradingPrediction', () => {
      test('should make successful API call with correct parameters', async () => {
        const mockResponse = {
          data: {
            symbol: 'AAPL',
            current_price: 150.25,
            sentiment: {
              overall: 'Bullish',
              confidence: 75
            },
            lstm_analysis: {
              trend_direction: 'Strong Bullish',
              prediction_factor: 2.5
            },
            intraday_predictions: {
              open: { min: 148.50, max: 152.00, expected: 150.25 },
              close: { min: 149.00, max: 155.00, expected: 152.50 }
            },
            technical_levels: {
              support: [148.00, 145.50],
              resistance: [152.00, 155.00],
              pivot: 150.25
            }
          }
        };

        mockedAxios.post.mockResolvedValue(mockResponse);

        const result = await dayTradingAPI.getDayTradingPrediction('AAPL', '2024-01-15');

        expect(mockedAxios.post).toHaveBeenCalledWith(
          '/api/day-trading/prediction/AAPL',
          { target_date: '2024-01-15' }
        );
        expect(result).toEqual(mockResponse.data);
      });

      test('should handle API errors with proper error message', async () => {
        const errorResponse = {
          response: {
            data: {
              error: 'Failed to fetch stock data'
            }
          }
        };

        mockedAxios.post.mockRejectedValue(errorResponse);

        await expect(dayTradingAPI.getDayTradingPrediction('INVALID', '2024-01-15'))
          .rejects.toThrow('Failed to fetch stock data');
      });

      test('should handle network errors', async () => {
        const networkError = new Error('Network Error');
        mockedAxios.post.mockRejectedValue(networkError);

        await expect(dayTradingAPI.getDayTradingPrediction('AAPL', '2024-01-15'))
          .rejects.toThrow('Network Error');
      });

      test('should handle missing error response data', async () => {
        const errorResponse = {
          response: {}
        };

        mockedAxios.post.mockRejectedValue(errorResponse);

        await expect(dayTradingAPI.getDayTradingPrediction('AAPL', '2024-01-15'))
          .rejects.toThrow();
      });
    });
  });

  describe('stockAPI', () => {
    describe('getStockData', () => {
      test('should make successful API call for stock data', async () => {
        const mockResponse = {
          data: {
            symbol: 'AAPL',
            prices: [150.25, 151.00, 149.75],
            dates: ['2024-01-12', '2024-01-13', '2024-01-14']
          }
        };

        mockedAxios.get.mockResolvedValue(mockResponse);

        const result = await stockAPI.getStockData('AAPL', '1mo');

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/data/AAPL?period=1mo');
        expect(result).toEqual(mockResponse.data);
      });
    });

    describe('getStockInfo', () => {
      test('should make successful API call for stock info', async () => {
        const mockResponse = {
          data: {
            symbol: 'AAPL',
            name: 'Apple Inc.',
            price: 150.25,
            change: 2.50,
            changePercent: 1.69
          }
        };

        mockedAxios.get.mockResolvedValue(mockResponse);

        const result = await stockAPI.getStockInfo('AAPL', 'US');

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/stock/info/AAPL?market=US');
        expect(result).toEqual(mockResponse.data);
      });
    });
  });

  describe('portfolioAPI', () => {
    describe('buyStock', () => {
      test('should make successful API call to buy stock', async () => {
        const mockResponse = {
          data: {
            success: true,
            message: 'Successfully bought 10 shares of AAPL',
            transaction: {
              symbol: 'AAPL',
              quantity: 10,
              price: 150.25,
              total: 1502.50
            }
          }
        };

        mockedAxios.post.mockResolvedValue(mockResponse);

        const result = await portfolioAPI.buyStock('AAPL', 10, 'US');

        expect(mockedAxios.post).toHaveBeenCalledWith('/api/portfolio/buy', {
          symbol: 'AAPL',
          shares: 10,
          market: 'US'
        });
        expect(result).toEqual(mockResponse.data);
      });
    });

    describe('sellStock', () => {
      test('should make successful API call to sell stock', async () => {
        const mockResponse = {
          data: {
            success: true,
            message: 'Successfully sold 5 shares of AAPL',
            transaction: {
              symbol: 'AAPL',
              quantity: 5,
              price: 150.25,
              total: 751.25
            }
          }
        };

        mockedAxios.post.mockResolvedValue(mockResponse);

        const result = await portfolioAPI.sellStock('AAPL', 5, 'US');

        expect(mockedAxios.post).toHaveBeenCalledWith('/api/portfolio/sell', {
          symbol: 'AAPL',
          shares: 5,
          market: 'US'
        });
        expect(result).toEqual(mockResponse.data);
      });
    });

    describe('getPortfolio', () => {
      test('should make successful API call to get portfolio', async () => {
        const mockResponse = {
          data: {
            total_value: 10000,
            available_cash: 5000,
            assets: [
              {
                symbol: 'AAPL',
                quantity: 10,
                avg_price: 150.25,
                current_price: 155.00,
                total_value: 1550.00
              }
            ]
          }
        };

        mockedAxios.get.mockResolvedValue(mockResponse);

        const result = await portfolioAPI.getPortfolio('US');

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/portfolio?market=US');
        expect(result).toEqual(mockResponse.data);
      });
    });
  });
});
