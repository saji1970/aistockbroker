"""
Simple Backend Tests
Tests core functionality without requiring full API server
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np

# Set environment variables for testing
os.environ['GOOGLE_API_KEY'] = 'test_key'
os.environ['ALPHA_VANTAGE_API_KEY'] = 'test_key'
os.environ['FINNHUB_API_KEY'] = 'test_key'
os.environ['MARKETSTACK_API_KEY'] = 'test_key'
os.environ['HUGGINGFACE_API_KEY'] = 'test_key'

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules
from data_fetcher import data_fetcher
from technical_analysis import TechnicalAnalyzer
from portfolio_manager import PortfolioManager
from enhanced_portfolio_manager import EnhancedPortfolioManager
from agent_manager import AgentManager, AgentRole, CustomerTier

class TestDataFetcher:
    """Test cases for data_fetcher module"""
    
    @pytest.fixture
    def mock_yfinance(self):
        """Mock yfinance for testing"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_data = pd.DataFrame({
                'Open': [100, 101, 102, 103, 104],
                'High': [105, 106, 107, 108, 109],
                'Low': [95, 96, 97, 98, 99],
                'Close': [102, 103, 104, 105, 106],
                'Volume': [1000000, 1100000, 1200000, 1300000, 1400000]
            }, index=pd.date_range('2023-01-01', periods=5))
            
            mock_ticker.return_value.history.return_value = mock_data
            mock_ticker.return_value.info = {
                'currentPrice': 106.0,
                'marketCap': 1000000000,
                'sector': 'Technology',
                'industry': 'Software'
            }
            yield mock_ticker
    
    def test_fetch_stock_data(self, mock_yfinance):
        """Test fetching stock data"""
        symbol = 'AAPL'
        period = '1y'
        interval = '1d'
        
        data = data_fetcher.fetch_stock_data(symbol, period, interval)
        
        assert data is not None
        assert 'Open' in data.columns
        assert 'Close' in data.columns
        assert 'Volume' in data.columns
        assert len(data) > 0
    
    def test_fetch_stock_info(self, mock_yfinance):
        """Test fetching stock information"""
        symbol = 'AAPL'
        
        info = data_fetcher.get_stock_info(symbol)
        
        assert info is not None
        assert 'currentPrice' in info
        assert 'marketCap' in info
        assert 'sector' in info
    
    def test_get_current_price(self, mock_yfinance):
        """Test getting current stock price"""
        symbol = 'AAPL'
        
        # Get stock info and extract current price
        info = data_fetcher.get_stock_info(symbol)
        price = info.get('currentPrice', 100.0)
        
        assert price is not None
        assert isinstance(price, (int, float))
        assert price > 0

class TestTechnicalAnalyzer:
    """Test cases for technical_analysis module"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample price data for testing"""
        dates = pd.date_range('2023-01-01', periods=100)
        prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
        
        return pd.DataFrame({
            'Open': prices,
            'High': prices + np.random.rand(100) * 2,
            'Low': prices - np.random.rand(100) * 2,
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)
    
    def test_calculate_rsi(self, sample_data):
        """Test RSI calculation"""
        analyzer = TechnicalAnalyzer()
        rsi = analyzer.calculate_rsi(sample_data['Close'])
        
        assert rsi is not None
        assert 0 <= rsi <= 100
        assert not pd.isna(rsi)
    
    def test_calculate_macd(self, sample_data):
        """Test MACD calculation"""
        analyzer = TechnicalAnalyzer()
        # Use the calculate_all_indicators method to get MACD data
        data_with_indicators = analyzer.calculate_all_indicators(sample_data)
        
        # Check if MACD columns exist
        assert 'MACD' in data_with_indicators.columns
        assert 'MACD_Signal' in data_with_indicators.columns
        assert 'MACD_Histogram' in data_with_indicators.columns
        
        # Get the latest values
        macd_line = data_with_indicators['MACD'].iloc[-1]
        signal_line = data_with_indicators['MACD_Signal'].iloc[-1]
        histogram = data_with_indicators['MACD_Histogram'].iloc[-1]
        
        assert macd_line is not None
        assert signal_line is not None
        assert histogram is not None
    
    def test_calculate_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation"""
        analyzer = TechnicalAnalyzer()
        # Use the calculate_all_indicators method to get Bollinger Bands data
        data_with_indicators = analyzer.calculate_all_indicators(sample_data)
        
        # Check if Bollinger Bands columns exist
        assert 'BB_Upper' in data_with_indicators.columns
        assert 'BB_Middle' in data_with_indicators.columns
        assert 'BB_Lower' in data_with_indicators.columns
        
        # Get the latest values
        upper = data_with_indicators['BB_Upper'].iloc[-1]
        middle = data_with_indicators['BB_Middle'].iloc[-1]
        lower = data_with_indicators['BB_Lower'].iloc[-1]
        
        assert upper is not None
        assert middle is not None
        assert lower is not None
        assert upper > middle > lower

class TestPortfolioManager:
    """Test cases for portfolio_manager module"""
    
    def test_initialize_portfolio(self):
        """Test portfolio initialization"""
        manager = PortfolioManager(initial_capital=100000)
        
        assert manager.initial_capital == 100000
        assert manager.portfolio.available_cash == 100000
        assert len(manager.portfolio.assets) == 0
        assert manager.portfolio.total_value == 100000
    
    def test_buy_stock(self):
        """Test buying stock"""
        manager = PortfolioManager(initial_capital=100000)
        
        result = manager.buy_stock('AAPL', 100, 150.0)
        
        assert result is True
        assert 'AAPL' in manager.portfolio.assets
        assert manager.portfolio.assets['AAPL'].quantity == 100
        assert manager.portfolio.available_cash < 100000
    
    def test_sell_stock(self):
        """Test selling stock"""
        manager = PortfolioManager(initial_capital=100000)
        
        # First buy stock
        manager.buy_stock('AAPL', 100, 150.0)
        initial_cash = manager.portfolio.available_cash
        
        # Then sell stock
        result = manager.sell_stock('AAPL', 50, 160.0)
        
        assert result is True
        assert manager.portfolio.assets['AAPL'].quantity == 50
        assert manager.portfolio.available_cash > initial_cash
    
    def test_get_portfolio_summary(self):
        """Test portfolio summary"""
        manager = PortfolioManager(initial_capital=100000)
        manager.buy_stock('AAPL', 100, 150.0)
        
        summary = manager.get_portfolio_summary()
        
        assert 'total_value' in summary
        assert 'available_cash' in summary
        assert 'assets' in summary
        assert 'total_return' in summary
        assert summary['total_value'] > 0

class TestEnhancedPortfolioManager:
    """Test cases for enhanced_portfolio_manager module"""
    
    def test_initialize_enhanced_portfolio(self):
        """Test enhanced portfolio initialization"""
        manager = EnhancedPortfolioManager(
            investment_amount=100000,
            portfolio_name="test_portfolio"
        )
        
        assert manager.portfolio_name == "test_portfolio"
        assert manager.config.investment_amount == 100000
        assert manager.portfolio.available_cash == 100000
        assert len(manager.portfolio.assets) == 0
    
    def test_add_position(self):
        """Test adding position"""
        manager = EnhancedPortfolioManager(
            investment_amount=100000,
            portfolio_name="test_portfolio"
        )
        
        result = manager.buy_shares('AAPL', 100, 150.0)
        
        assert result['success'] is True
        assert 'AAPL' in manager.portfolio.assets
        assert manager.portfolio.assets['AAPL'].quantity == 100
    
    def test_update_position(self):
        """Test updating position"""
        manager = EnhancedPortfolioManager(
            investment_amount=100000,
            portfolio_name="test_portfolio"
        )
        
        # Add position first
        manager.buy_shares('AAPL', 100, 150.0)
        
        # Add more shares (update position)
        result = manager.buy_shares('AAPL', 100, 160.0)
        
        assert result['success'] is True
        assert manager.portfolio.assets['AAPL'].quantity == 200
        assert manager.portfolio.assets['AAPL'].avg_cost == 155.0  # Average price

class TestAgentManager:
    """Test cases for agent_manager module"""
    
    @pytest.fixture
    def temp_data_file(self):
        """Create temporary data file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"agents": [], "customers": [], "trade_suggestions": [], "agent_decisions": [], "learning_data": []}')
            return f.name
    
    @pytest.fixture
    def agent_manager(self, temp_data_file):
        """Create AgentManager instance with temporary data file"""
        return AgentManager(data_file=temp_data_file)
    
    def test_create_agent(self, agent_manager):
        """Test agent creation"""
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        assert agent.name == "Test Agent"
        assert agent.email == "test@example.com"
        assert agent.role == AgentRole.SENIOR
        assert agent.id in agent_manager.agents
    
    def test_authenticate_agent(self, agent_manager):
        """Test agent authentication"""
        # Create agent first
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        # Test successful authentication
        authenticated_agent = agent_manager.authenticate_agent("test@example.com", "password123")
        assert authenticated_agent is not None
        assert authenticated_agent.id == agent.id
        
        # Test failed authentication
        failed_agent = agent_manager.authenticate_agent("test@example.com", "wrongpassword")
        assert failed_agent is None
    
    def test_create_customer(self, agent_manager):
        """Test customer creation"""
        # Create agent first
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        # Create customer
        customer = agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id,
            risk_tolerance="high"
        )
        
        assert customer.name == "Test Customer"
        assert customer.email == "customer@example.com"
        assert customer.tier == CustomerTier.PREMIUM
        assert customer.agent_id == agent.id
        assert customer.id in agent_manager.customers
        assert customer.id in agent.customers

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
