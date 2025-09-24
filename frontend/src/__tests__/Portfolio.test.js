/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Portfolio from '../components/Portfolio/Portfolio';
import { StoreProvider } from '../context/StoreContext';

// Mock the API calls
jest.mock('../services/api', () => ({
  getPortfolio: jest.fn(() => Promise.resolve({
    total_value: 100000,
    cash: 20000,
    positions: {
      AAPL: { 
        quantity: 100, 
        value: 15000, 
        avg_price: 150,
        current_price: 155,
        unrealized_pnl: 500
      },
      TSLA: { 
        quantity: 50, 
        value: 10000, 
        avg_price: 200,
        current_price: 210,
        unrealized_pnl: 500
      }
    }
  })),
  getPortfolioHistory: jest.fn(() => Promise.resolve({
    history: [
      { date: '2023-01-01', value: 95000 },
      { date: '2023-01-02', value: 98000 },
      { date: '2023-01-03', value: 100000 }
    ]
  }))
}));

const MockedPortfolio = () => (
  <StoreProvider>
    <Portfolio />
  </StoreProvider>
);

describe('Portfolio Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders portfolio without crashing', async () => {
    render(<MockedPortfolio />);
    
    await waitFor(() => {
      expect(screen.getByText(/Portfolio Overview/i)).toBeInTheDocument();
    });
  });

  test('displays portfolio summary', async () => {
    render(<MockedPortfolio />);
    
    await waitFor(() => {
      expect(screen.getByText(/Total Value/i)).toBeInTheDocument();
      expect(screen.getByText(/\$100,000/)).toBeInTheDocument();
      expect(screen.getByText(/Cash/i)).toBeInTheDocument();
      expect(screen.getByText(/\$20,000/)).toBeInTheDocument();
    });
  });

  test('displays positions', async () => {
    render(<MockedPortfolio />);
    
    await waitFor(() => {
      expect(screen.getByText(/AAPL/)).toBeInTheDocument();
      expect(screen.getByText(/TSLA/)).toBeInTheDocument();
      expect(screen.getByText(/100 shares/)).toBeInTheDocument();
      expect(screen.getByText(/50 shares/)).toBeInTheDocument();
    });
  });

  test('displays unrealized P&L', async () => {
    render(<MockedPortfolio />);
    
    await waitFor(() => {
      expect(screen.getByText(/Unrealized P&L/i)).toBeInTheDocument();
      expect(screen.getByText(/\$500/)).toBeInTheDocument();
    });
  });

  test('handles portfolio refresh', async () => {
    render(<MockedPortfolio />);
    
    const refreshButton = screen.getByText(/Refresh/i);
    fireEvent.click(refreshButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Portfolio Overview/i)).toBeInTheDocument();
    });
  });

  test('displays performance chart', async () => {
    render(<MockedPortfolio />);
    
    await waitFor(() => {
      expect(screen.getByText(/Performance Chart/i)).toBeInTheDocument();
    });
  });
});
