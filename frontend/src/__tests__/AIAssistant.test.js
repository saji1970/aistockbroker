/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AIAssistant from '../components/AIAssistant/AIAssistant';
import { StoreProvider } from '../context/StoreContext';

// Mock the AI services
jest.mock('../services/huggingfaceAI', () => ({
  analyzeStock: jest.fn(() => Promise.resolve({
    analysis: 'AAPL shows strong bullish momentum with RSI at 65 and MACD indicating upward trend.',
    confidence: 0.85,
    recommendation: 'BUY',
    target_price: 180
  })),
  generateInsights: jest.fn(() => Promise.resolve({
    insights: 'Market sentiment is positive with strong institutional buying.',
    key_points: ['Strong earnings growth', 'Positive analyst ratings', 'Technical breakout']
  }))
}));

// Mock the API calls
jest.mock('../services/api', () => ({
  getStockData: jest.fn(() => Promise.resolve({
    data: [
      { date: '2023-01-01', close: 150, volume: 1000000 },
      { date: '2023-01-02', close: 151, volume: 1100000 }
    ]
  })),
  getPrediction: jest.fn(() => Promise.resolve({
    prediction: 'buy',
    confidence: 0.8,
    reasoning: 'Strong technical indicators'
  }))
}));

const MockedAIAssistant = () => (
  <StoreProvider>
    <AIAssistant />
  </StoreProvider>
);

describe('AIAssistant Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders AI assistant without crashing', async () => {
    render(<MockedAIAssistant />);
    
    await waitFor(() => {
      expect(screen.getByText(/AI Assistant/i)).toBeInTheDocument();
    });
  });

  test('displays chat interface', async () => {
    render(<MockedAIAssistant />);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Ask me anything about stocks/i)).toBeInTheDocument();
    });
  });

  test('handles user input', async () => {
    render(<MockedAIAssistant />);
    
    const input = screen.getByPlaceholderText(/Ask me anything about stocks/i);
    fireEvent.change(input, { target: { value: 'Analyze AAPL stock' } });
    
    expect(input.value).toBe('Analyze AAPL stock');
  });

  test('handles send message', async () => {
    render(<MockedAIAssistant />);
    
    const input = screen.getByPlaceholderText(/Ask me anything about stocks/i);
    fireEvent.change(input, { target: { value: 'Analyze AAPL stock' } });
    
    const sendButton = screen.getByText(/Send/i);
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Analyze AAPL stock/)).toBeInTheDocument();
    });
  });

  test('displays AI response', async () => {
    render(<MockedAIAssistant />);
    
    const input = screen.getByPlaceholderText(/Ask me anything about stocks/i);
    fireEvent.change(input, { target: { value: 'Analyze AAPL stock' } });
    
    const sendButton = screen.getByText(/Send/i);
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/AAPL shows strong bullish momentum/)).toBeInTheDocument();
    });
  });

  test('handles quick actions', async () => {
    render(<MockedAIAssistant />);
    
    const quickAction = screen.getByText(/Market Analysis/i);
    fireEvent.click(quickAction);
    
    await waitFor(() => {
      expect(screen.getByText(/Market sentiment is positive/)).toBeInTheDocument();
    });
  });

  test('displays conversation history', async () => {
    render(<MockedAIAssistant />);
    
    const input = screen.getByPlaceholderText(/Ask me anything about stocks/i);
    fireEvent.change(input, { target: { value: 'What is the market trend?' } });
    
    const sendButton = screen.getByText(/Send/i);
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/What is the market trend?/)).toBeInTheDocument();
    });
  });

  test('handles clear conversation', async () => {
    render(<MockedAIAssistant />);
    
    const clearButton = screen.getByText(/Clear/i);
    fireEvent.click(clearButton);
    
    await waitFor(() => {
      expect(screen.getByText(/AI Assistant/i)).toBeInTheDocument();
    });
  });
});
