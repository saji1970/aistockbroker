/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';
import { BrowserRouter } from 'react-router-dom';

// Mock the API calls
jest.mock('../services/api', () => ({
  getStockData: jest.fn(),
  getStockInfo: jest.fn(),
  getPrediction: jest.fn(),
  getPortfolio: jest.fn(),
}));

// Mock the trading bot API
jest.mock('../services/tradingBotAPI', () => ({
  getStatus: jest.fn(),
  startBot: jest.fn(),
  stopBot: jest.fn(),
  getAllBotData: jest.fn(),
}));

// Mock the AI services
jest.mock('../services/huggingfaceAI', () => ({
  analyzeStock: jest.fn(),
  generateInsights: jest.fn(),
}));

const MockedApp = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders main app without crashing', () => {
    render(<MockedApp />);
    expect(screen.getByText(/AI Stock Trading/i)).toBeInTheDocument();
  });

  test('renders navigation menu', () => {
    render(<MockedApp />);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Portfolio/i)).toBeInTheDocument();
    expect(screen.getByText(/Analysis/i)).toBeInTheDocument();
  });

  test('navigates to different pages', async () => {
    render(<MockedApp />);
    
    // Test navigation to Portfolio
    fireEvent.click(screen.getByText(/Portfolio/i));
    await waitFor(() => {
      expect(screen.getByText(/Portfolio Overview/i)).toBeInTheDocument();
    });

    // Test navigation to Analysis
    fireEvent.click(screen.getByText(/Analysis/i));
    await waitFor(() => {
      expect(screen.getByText(/Stock Analysis/i)).toBeInTheDocument();
    });
  });
});
