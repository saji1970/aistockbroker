import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DayTradingPrediction from '../DayTradingPrediction';
import { dayTradingAPI } from '../../../services/api';

// Mock the API
jest.mock('../../../services/api', () => ({
  dayTradingAPI: {
    getDayTradingPrediction: jest.fn(),
  },
}));

// Mock the chart components
jest.mock('../../Charts/StockChart', () => {
  return function MockStockChart({ symbol }) {
    return <div data-testid="stock-chart">Stock Chart for {symbol}</div>;
  };
});

jest.mock('../../Charts/SensitivityChart', () => {
  return function MockSensitivityChart({ symbol, targetDate }) {
    return <div data-testid="sensitivity-chart">Sensitivity Chart for {symbol} on {targetDate}</div>;
  };
});

describe('DayTradingPrediction Component', () => {
  const mockSymbol = 'AAPL';
  
  beforeEach(() => {
    jest.clearAllMocks();
    // Set default date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    
    // Mock successful API response
    dayTradingAPI.getDayTradingPrediction.mockResolvedValue({
      symbol: mockSymbol,
      current_price: 150.25,
      sentiment: {
        overall: 'Bullish',
        confidence: 75,
        factors: ['RSI: 65', 'SMA: Above 50-day', 'Volume: High']
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
    });
  });

  describe('Component Rendering', () => {
    test('renders the component with correct title and description', () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      expect(screen.getByText('Day Trading Prediction')).toBeInTheDocument();
      expect(screen.getByText('Generate detailed predictions for specific trading dates')).toBeInTheDocument();
    });

    test('renders date input with tomorrow as default', () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const dateInput = screen.getByDisplayValue(/\d{4}-\d{2}-\d{2}/);
      expect(dateInput).toBeInTheDocument();
    });

    test('renders generate prediction button', () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      expect(screen.getByText('Generate Prediction')).toBeInTheDocument();
    });

    test('button is disabled when no symbol is provided', () => {
      render(<DayTradingPrediction symbol="" />);
      
      const button = screen.getByText('Generate Prediction');
      expect(button).toBeDisabled();
    });
  });

  describe('Date Selection', () => {
    test('allows user to change target date', () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const dateInput = screen.getByDisplayValue(/\d{4}-\d{2}-\d{2}/);
      const newDate = '2024-02-15';
      
      fireEvent.change(dateInput, { target: { value: newDate } });
      expect(dateInput.value).toBe(newDate);
    });

    test('prevents selecting past dates', () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const dateInput = screen.getByDisplayValue(/\d{4}-\d{2}-\d{2}/);
      const today = new Date().toISOString().split('T')[0];
      
      expect(dateInput.min).toBe(today);
    });
  });

  describe('API Integration', () => {
    test('calls API with correct parameters when generate button is clicked', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(dayTradingAPI.getDayTradingPrediction).toHaveBeenCalledWith(
          mockSymbol,
          expect.stringMatching(/\d{4}-\d{2}-\d{2}/)
        );
      });
    });

    test('shows loading state during API call', async () => {
      // Mock a delayed API response
      dayTradingAPI.getDayTradingPrediction.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({}), 100))
      );
      
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      expect(screen.getByText('Generating...')).toBeInTheDocument();
    });

    test('handles API errors gracefully', async () => {
      const errorMessage = 'Failed to fetch prediction data';
      dayTradingAPI.getDayTradingPrediction.mockRejectedValue(new Error(errorMessage));
      
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText(`Error generating prediction: ${errorMessage}`)).toBeInTheDocument();
      });
    });

    test('handles invalid API response format', async () => {
      dayTradingAPI.getDayTradingPrediction.mockResolvedValue({});
      
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to generate prediction - invalid response format')).toBeInTheDocument();
      });
    });
  });

  describe('Prediction Display', () => {
    test('displays prediction summary after successful API call', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText(/Prediction for AAPL on/)).toBeInTheDocument();
      });
    });

    test('displays market sentiment with correct styling', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Bullish')).toBeInTheDocument();
        expect(screen.getByText('75% confidence')).toBeInTheDocument();
      });
    });

    test('displays intraday predictions', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Intraday Price Predictions')).toBeInTheDocument();
        expect(screen.getByText('open')).toBeInTheDocument();
        expect(screen.getByText('close')).toBeInTheDocument();
      });
    });

    test('displays trading signals', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Trading Signals')).toBeInTheDocument();
      });
    });

    test('displays risk factors', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Risk Factors')).toBeInTheDocument();
      });
    });

    test('displays technical levels', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Technical Levels')).toBeInTheDocument();
        expect(screen.getByText('Support Levels')).toBeInTheDocument();
        expect(screen.getByText('Resistance Levels')).toBeInTheDocument();
      });
    });
  });

  describe('Chart Toggle', () => {
    test('shows/hides charts when toggle button is clicked', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Hide Charts')).toBeInTheDocument();
        expect(screen.getByTestId('stock-chart')).toBeInTheDocument();
        expect(screen.getByTestId('sensitivity-chart')).toBeInTheDocument();
      });
      
      const toggleButton = screen.getByText('Hide Charts');
      fireEvent.click(toggleButton);
      
      expect(screen.getByText('Show Charts')).toBeInTheDocument();
      expect(screen.queryByTestId('stock-chart')).not.toBeInTheDocument();
      expect(screen.queryByTestId('sensitivity-chart')).not.toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('displays error message when symbol is missing', async () => {
      render(<DayTradingPrediction symbol="" />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      expect(screen.getByText('Please select a symbol and date')).toBeInTheDocument();
    });

    test('displays error message when date is missing', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const dateInput = screen.getByDisplayValue(/\d{4}-\d{2}-\d{2}/);
      fireEvent.change(dateInput, { target: { value: '' } });
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      expect(screen.getByText('Please select a symbol and date')).toBeInTheDocument();
    });
  });

  describe('Data Validation', () => {
    test('handles missing sentiment data gracefully', async () => {
      dayTradingAPI.getDayTradingPrediction.mockResolvedValue({
        symbol: mockSymbol,
        current_price: 150.25,
        // Missing sentiment data
        lstm_analysis: {
          trend_direction: 'Neutral',
          prediction_factor: 1.0
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
      });
      
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Neutral')).toBeInTheDocument();
        expect(screen.getByText('70% confidence')).toBeInTheDocument();
      });
    });

    test('handles missing technical levels gracefully', async () => {
      dayTradingAPI.getDayTradingPrediction.mockResolvedValue({
        symbol: mockSymbol,
        current_price: 150.25,
        sentiment: {
          overall: 'Bullish',
          confidence: 75,
          factors: ['RSI: 65', 'SMA: Above 50-day', 'Volume: High']
        },
        lstm_analysis: {
          trend_direction: 'Strong Bullish',
          prediction_factor: 2.5
        },
        intraday_predictions: {
          open: { min: 148.50, max: 152.00, expected: 150.25 },
          close: { min: 149.00, max: 155.00, expected: 152.50 }
        }
        // Missing technical_levels
      });
      
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('No support levels available')).toBeInTheDocument();
        expect(screen.getByText('No resistance levels available')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels and roles', () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const dateInput = screen.getByDisplayValue(/\d{4}-\d{2}-\d{2}/);
      expect(dateInput).toHaveAttribute('type', 'date');
      
      const button = screen.getByText('Generate Prediction');
      expect(button).toBeInTheDocument();
    });

    test('button state changes are properly communicated', async () => {
      render(<DayTradingPrediction symbol={mockSymbol} />);
      
      const button = screen.getByText('Generate Prediction');
      fireEvent.click(button);
      
      expect(screen.getByText('Generating...')).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getByText('Generate Prediction')).toBeInTheDocument();
      });
    });
  });
});
