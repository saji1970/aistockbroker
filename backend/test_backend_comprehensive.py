"""
Comprehensive Backend Unit Tests for AI Stock Trader
Tests all backend functionality including API endpoints, data processing, and business logic
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

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all backend modules
from api_server import app
from data_fetcher import data_fetcher
from technical_analysis import TechnicalAnalyzer
from gemini_predictor import GeminiStockPredictor
from portfolio_manager import PortfolioManager
from enhanced_portfolio_manager import EnhancedPortfolioManager
from enhanced_auto_trader import EnhancedAutoTrader
from shadow_trading_bot import ShadowTradingBot
from agent_manager import AgentManager, AgentRole, CustomerTier
from ai_suggestion_engine import AISuggestionEngine
from financial_advisor import FinancialAdvisor

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
        
        info = data_fetcher.fetch_stock_info(symbol)
        
        assert info is not None
        assert 'currentPrice' in info
        assert 'marketCap' in info
        assert 'sector' in info
    
    def test_get_current_price(self, mock_yfinance):
        """Test getting current stock price"""
        symbol = 'AAPL'
        
        price = data_fetcher.get_current_price(symbol)
        
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
        macd_line, signal_line, histogram = analyzer.calculate_macd(sample_data['Close'])
        
        assert macd_line is not None
        assert signal_line is not None
        assert histogram is not None
        assert not pd.isna(macd_line)
        assert not pd.isna(signal_line)
        assert not pd.isna(histogram)
    
    def test_calculate_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation"""
        analyzer = TechnicalAnalyzer()
        upper, middle, lower = analyzer.calculate_bollinger_bands(sample_data['Close'])
        
        assert upper is not None
        assert middle is not None
        assert lower is not None
        assert upper > middle > lower
        assert not pd.isna(upper)
        assert not pd.isna(middle)
        assert not pd.isna(lower)
    
    def test_calculate_moving_averages(self, sample_data):
        """Test moving averages calculation"""
        analyzer = TechnicalAnalyzer()
        sma_20 = analyzer.calculate_sma(sample_data['Close'], 20)
        ema_20 = analyzer.calculate_ema(sample_data['Close'], 20)
        
        assert sma_20 is not None
        assert ema_20 is not None
        assert not pd.isna(sma_20)
        assert not pd.isna(ema_20)
    
    def test_identify_support_resistance(self, sample_data):
        """Test support and resistance identification"""
        analyzer = TechnicalAnalyzer()
        support, resistance = analyzer.identify_support_resistance(sample_data)
        
        assert support is not None
        assert resistance is not None
        assert len(support) > 0
        assert len(resistance) > 0
        assert all(s < r for s, r in zip(support, resistance))

class TestGeminiStockPredictor:
    """Test cases for gemini_predictor module"""
    
    @pytest.fixture
    def mock_gemini(self):
        """Mock Gemini API for testing"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_response = Mock()
            mock_response.text = "Based on technical analysis, AAPL shows strong bullish signals with RSI at 65 and MACD indicating upward momentum. Recommendation: BUY with target price of $180."
            mock_model.return_value.generate_content.return_value = mock_response
            yield mock_model
    
    def test_initialize_predictor(self, mock_gemini):
        """Test predictor initialization"""
        predictor = GeminiStockPredictor()
        assert predictor is not None
        assert hasattr(predictor, 'model')
    
    def test_predict_stock_movement(self, mock_gemini):
        """Test stock movement prediction"""
        predictor = GeminiStockPredictor()
        symbol = 'AAPL'
        data = pd.DataFrame({
            'Close': [150, 151, 152, 153, 154],
            'Volume': [1000000, 1100000, 1200000, 1300000, 1400000]
        })
        
        prediction = predictor.predict_stock_movement(symbol, data)
        
        assert prediction is not None
        assert 'prediction' in prediction
        assert 'confidence' in prediction
        assert 'reasoning' in prediction
        assert 0 <= prediction['confidence'] <= 1
    
    def test_analyze_sentiment(self, mock_gemini):
        """Test sentiment analysis"""
        predictor = GeminiStockPredictor()
        text = "AAPL stock is performing exceptionally well with strong earnings growth."
        
        sentiment = predictor.analyze_sentiment(text)
        
        assert sentiment is not None
        assert 'sentiment' in sentiment
        assert 'score' in sentiment
        assert sentiment['sentiment'] in ['positive', 'negative', 'neutral']

class TestPortfolioManager:
    """Test cases for portfolio_manager module"""
    
    def test_initialize_portfolio(self):
        """Test portfolio initialization"""
        manager = PortfolioManager(initial_capital=100000)
        
        assert manager.initial_capital == 100000
        assert manager.cash == 100000
        assert len(manager.positions) == 0
        assert manager.total_value == 100000
    
    def test_buy_stock(self):
        """Test buying stock"""
        manager = PortfolioManager(initial_capital=100000)
        
        result = manager.buy_stock('AAPL', 100, 150.0)
        
        assert result['success'] is True
        assert 'AAPL' in manager.positions
        assert manager.positions['AAPL']['quantity'] == 100
        assert manager.cash < 100000
    
    def test_sell_stock(self):
        """Test selling stock"""
        manager = PortfolioManager(initial_capital=100000)
        
        # First buy stock
        manager.buy_stock('AAPL', 100, 150.0)
        initial_cash = manager.cash
        
        # Then sell stock
        result = manager.sell_stock('AAPL', 50, 160.0)
        
        assert result['success'] is True
        assert manager.positions['AAPL']['quantity'] == 50
        assert manager.cash > initial_cash
    
    def test_get_portfolio_summary(self):
        """Test portfolio summary"""
        manager = PortfolioManager(initial_capital=100000)
        manager.buy_stock('AAPL', 100, 150.0)
        
        summary = manager.get_portfolio_summary()
        
        assert 'total_value' in summary
        assert 'cash' in summary
        assert 'positions' in summary
        assert 'total_return' in summary
        assert summary['total_value'] > 0

class TestEnhancedPortfolioManager:
    """Test cases for enhanced_portfolio_manager module"""
    
    def test_initialize_enhanced_portfolio(self):
        """Test enhanced portfolio initialization"""
        manager = EnhancedPortfolioManager(
            portfolio_id="test_portfolio",
            initial_capital=100000
        )
        
        assert manager.portfolio_id == "test_portfolio"
        assert manager.initial_capital == 100000
        assert manager.cash == 100000
        assert len(manager.positions) == 0
    
    def test_add_position(self):
        """Test adding position"""
        manager = EnhancedPortfolioManager(
            portfolio_id="test_portfolio",
            initial_capital=100000
        )
        
        result = manager.add_position('AAPL', 100, 150.0)
        
        assert result['success'] is True
        assert 'AAPL' in manager.positions
        assert manager.positions['AAPL']['quantity'] == 100
    
    def test_update_position(self):
        """Test updating position"""
        manager = EnhancedPortfolioManager(
            portfolio_id="test_portfolio",
            initial_capital=100000
        )
        
        # Add position first
        manager.add_position('AAPL', 100, 150.0)
        
        # Update position
        result = manager.update_position('AAPL', 200, 160.0)
        
        assert result['success'] is True
        assert manager.positions['AAPL']['quantity'] == 200
        assert manager.positions['AAPL']['avg_price'] == 155.0  # Average price
    
    def test_calculate_portfolio_metrics(self):
        """Test portfolio metrics calculation"""
        manager = EnhancedPortfolioManager(
            portfolio_id="test_portfolio",
            initial_capital=100000
        )
        
        manager.add_position('AAPL', 100, 150.0)
        
        metrics = manager.calculate_portfolio_metrics()
        
        assert 'total_value' in metrics
        assert 'total_return' in metrics
        assert 'sharpe_ratio' in metrics
        assert 'max_drawdown' in metrics
        assert metrics['total_value'] > 0

class TestEnhancedAutoTrader:
    """Test cases for enhanced_auto_trader module"""
    
    def test_initialize_auto_trader(self):
        """Test auto trader initialization"""
        trader = EnhancedAutoTrader(
            initial_capital=100000,
            risk_tolerance='medium'
        )
        
        assert trader.initial_capital == 100000
        assert trader.risk_tolerance == 'medium'
        assert trader.is_active is False
    
    def test_configure_trader(self):
        """Test trader configuration"""
        trader = EnhancedAutoTrader(
            initial_capital=100000,
            risk_tolerance='medium'
        )
        
        config = {
            'max_position_size': 0.1,
            'stop_loss': 0.05,
            'take_profit': 0.15
        }
        
        result = trader.configure(config)
        
        assert result['success'] is True
        assert trader.max_position_size == 0.1
        assert trader.stop_loss == 0.05
        assert trader.take_profit == 0.15
    
    def test_start_trading(self):
        """Test starting trading"""
        trader = EnhancedAutoTrader(
            initial_capital=100000,
            risk_tolerance='medium'
        )
        
        result = trader.start_trading()
        
        assert result['success'] is True
        assert trader.is_active is True
    
    def test_stop_trading(self):
        """Test stopping trading"""
        trader = EnhancedAutoTrader(
            initial_capital=100000,
            risk_tolerance='medium'
        )
        
        trader.start_trading()
        result = trader.stop_trading()
        
        assert result['success'] is True
        assert trader.is_active is False

class TestShadowTradingBot:
    """Test cases for shadow_trading_bot module"""
    
    def test_initialize_shadow_bot(self):
        """Test shadow trading bot initialization"""
        bot = ShadowTradingBot(
            initial_capital=100000,
            target_amount=110000,
            trading_strategy='momentum'
        )
        
        assert bot.initial_capital == 100000
        assert bot.target_amount == 110000
        assert bot.trading_strategy == 'momentum'
        assert bot.is_running is False
    
    def test_add_to_watchlist(self):
        """Test adding symbol to watchlist"""
        bot = ShadowTradingBot(
            initial_capital=100000,
            target_amount=110000,
            trading_strategy='momentum'
        )
        
        result = bot.add_to_watchlist('AAPL')
        
        assert result['success'] is True
        assert 'AAPL' in bot.watchlist
    
    def test_start_bot(self):
        """Test starting bot"""
        bot = ShadowTradingBot(
            initial_capital=100000,
            target_amount=110000,
            trading_strategy='momentum'
        )
        
        result = bot.start()
        
        assert result['success'] is True
        assert bot.is_running is True
    
    def test_stop_bot(self):
        """Test stopping bot"""
        bot = ShadowTradingBot(
            initial_capital=100000,
            target_amount=110000,
            trading_strategy='momentum'
        )
        
        bot.start()
        result = bot.stop()
        
        assert result['success'] is True
        assert bot.is_running is False
    
    def test_get_performance_report(self):
        """Test getting performance report"""
        bot = ShadowTradingBot(
            initial_capital=100000,
            target_amount=110000,
            trading_strategy='momentum'
        )
        
        report = bot.get_performance_report()
        
        assert 'total_return' in report
        assert 'orders_count' in report
        assert 'win_rate' in report
        assert 'sharpe_ratio' in report

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
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        authenticated_agent = agent_manager.authenticate_agent("test@example.com", "password123")
        assert authenticated_agent is not None
        assert authenticated_agent.id == agent.id
        
        failed_agent = agent_manager.authenticate_agent("test@example.com", "wrongpassword")
        assert failed_agent is None
    
    def test_create_customer(self, agent_manager):
        """Test customer creation"""
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
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
    
    def test_create_trade_suggestion(self, agent_manager):
        """Test trade suggestion creation"""
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        customer = agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        suggestion = agent_manager.create_trade_suggestion(
            customer_id=customer.id,
            symbol="AAPL",
            action="buy",
            quantity=100,
            price=150.0,
            confidence=0.8,
            reasoning="Strong technical indicators",
            ai_model="gemini"
        )
        
        assert suggestion.symbol == "AAPL"
        assert suggestion.action == "buy"
        assert suggestion.quantity == 100
        assert suggestion.price == 150.0
        assert suggestion.confidence == 0.8
        assert suggestion.id in agent_manager.trade_suggestions
    
    def test_make_agent_decision(self, agent_manager):
        """Test agent decision making"""
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        customer = agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        suggestion = agent_manager.create_trade_suggestion(
            customer_id=customer.id,
            symbol="AAPL",
            action="buy",
            quantity=100,
            price=150.0,
            confidence=0.8,
            reasoning="Strong technical indicators",
            ai_model="gemini"
        )
        
        decision = agent_manager.make_agent_decision(
            suggestion_id=suggestion.id,
            agent_id=agent.id,
            decision="accept",
            reasoning="Good analysis"
        )
        
        assert decision.suggestion_id == suggestion.id
        assert decision.agent_id == agent.id
        assert decision.decision == "accept"
        assert suggestion.status == "accept"
        assert suggestion.id in agent_manager.agent_decisions

class TestAISuggestionEngine:
    """Test cases for ai_suggestion_engine module"""
    
    def test_initialize_engine(self):
        """Test AI suggestion engine initialization"""
        engine = AISuggestionEngine()
        
        assert engine is not None
        assert hasattr(engine, 'learning_weights')
        assert 'technical_indicators' in engine.learning_weights
        assert 'fundamental_analysis' in engine.learning_weights
        assert 'market_sentiment' in engine.learning_weights
    
    def test_calculate_technical_indicators(self):
        """Test technical indicators calculation"""
        engine = AISuggestionEngine()
        
        # Mock market data
        market_data = {
            'symbol': 'AAPL',
            'current_price': 150.0,
            'historical_data': pd.DataFrame({
                'Close': [145, 146, 147, 148, 149, 150],
                'Volume': [1000000, 1100000, 1200000, 1300000, 1400000, 1500000]
            })
        }
        
        indicators = engine._calculate_technical_indicators(market_data)
        
        assert 'rsi' in indicators
        assert 'macd' in indicators
        assert 'moving_averages' in indicators
        assert 'bollinger_bands' in indicators
        assert 0 <= indicators['rsi'] <= 100
    
    def test_calculate_volatility(self):
        """Test volatility calculation"""
        engine = AISuggestionEngine()
        
        market_data = {
            'historical_data': pd.DataFrame({
                'Close': [100, 101, 102, 101, 100, 99, 98, 99, 100, 101]
            })
        }
        
        volatility = engine._calculate_volatility(market_data)
        
        assert volatility is not None
        assert volatility >= 0
        assert isinstance(volatility, float)
    
    def test_determine_trend(self):
        """Test trend determination"""
        engine = AISuggestionEngine()
        
        market_data = {
            'historical_data': pd.DataFrame({
                'Close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
            })
        }
        
        trend = engine._determine_trend(market_data)
        
        assert trend is not None
        assert trend in ['strong_uptrend', 'uptrend', 'sideways', 'downtrend', 'strong_downtrend']
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation"""
        engine = AISuggestionEngine()
        
        technical_indicators = {'rsi': 50}
        sentiment = 'neutral'
        volatility = 0.2
        trend = 'sideways'
        
        confidence = engine._calculate_confidence_score(
            technical_indicators, sentiment, volatility, trend
        )
        
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)
    
    def test_update_learning_weights(self):
        """Test learning weights update"""
        engine = AISuggestionEngine()
        initial_weights = engine.learning_weights.copy()
        
        feedback_data = {
            'agent_acceptance_rate': 0.9
        }
        
        engine.update_learning_weights(feedback_data)
        
        # Weights should be normalized
        total_weight = sum(engine.learning_weights.values())
        assert abs(total_weight - 1.0) < 0.01

class TestFinancialAdvisor:
    """Test cases for financial_advisor module"""
    
    def test_initialize_advisor(self):
        """Test financial advisor initialization"""
        advisor = FinancialAdvisor()
        
        assert advisor is not None
        assert hasattr(advisor, 'risk_profiles')
        assert hasattr(advisor, 'investment_strategies')
    
    def test_analyze_risk_profile(self):
        """Test risk profile analysis"""
        advisor = FinancialAdvisor()
        
        user_data = {
            'age': 30,
            'income': 100000,
            'investment_goals': ['retirement', 'house_purchase'],
            'risk_tolerance': 'medium'
        }
        
        risk_profile = advisor.analyze_risk_profile(user_data)
        
        assert 'risk_level' in risk_profile
        assert 'recommended_allocations' in risk_profile
        assert 'investment_strategy' in risk_profile
        assert risk_profile['risk_level'] in ['low', 'medium', 'high']
    
    def test_generate_investment_advice(self):
        """Test investment advice generation"""
        advisor = FinancialAdvisor()
        
        portfolio_data = {
            'total_value': 100000,
            'positions': {'AAPL': {'value': 50000}, 'TSLA': {'value': 30000}},
            'cash': 20000
        }
        
        advice = advisor.generate_investment_advice(portfolio_data)
        
        assert 'recommendations' in advice
        assert 'risk_assessment' in advice
        assert 'diversification_score' in advice
        assert isinstance(advice['recommendations'], list)

class TestAPIServer:
    """Test cases for API server endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
    
    def test_stock_data_endpoint(self, client):
        """Test stock data endpoint"""
        with patch('data_fetcher.data_fetcher.fetch_stock_data') as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({
                'Close': [150, 151, 152],
                'Volume': [1000000, 1100000, 1200000]
            })
            
            response = client.get('/api/stock/data/AAPL?period=1y&market=US')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'data' in data
            assert 'symbol' in data
            assert data['symbol'] == 'AAPL'
    
    def test_stock_info_endpoint(self, client):
        """Test stock info endpoint"""
        with patch('data_fetcher.data_fetcher.fetch_stock_info') as mock_fetch:
            mock_fetch.return_value = {
                'currentPrice': 150.0,
                'marketCap': 1000000000,
                'sector': 'Technology'
            }
            
            response = client.get('/api/stock/info/AAPL?market=US')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'currentPrice' in data
            assert 'marketCap' in data
            assert 'sector' in data
    
    def test_prediction_endpoint(self, client):
        """Test prediction endpoint"""
        with patch('gemini_predictor.GeminiPredictor.predict_stock_movement') as mock_predict:
            mock_predict.return_value = {
                'prediction': 'buy',
                'confidence': 0.8,
                'reasoning': 'Strong technical indicators'
            }
            
            response = client.get('/api/prediction/AAPL')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'prediction' in data
            assert 'confidence' in data
            assert 'reasoning' in data
    
    def test_portfolio_endpoint(self, client):
        """Test portfolio endpoint"""
        response = client.get('/api/portfolio')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_value' in data
        assert 'cash' in data
        assert 'positions' in data
    
    def test_agent_login_endpoint(self, client):
        """Test agent login endpoint"""
        # Create test agent first
        with patch('agent_manager.agent_manager.authenticate_agent') as mock_auth:
            mock_agent = Mock()
            mock_agent.id = 'test_agent_id'
            mock_agent.name = 'Test Agent'
            mock_agent.email = 'test@example.com'
            mock_agent.role = AgentRole.SENIOR
            mock_auth.return_value = mock_agent
            
            response = client.post('/api/agent/auth/login', json={
                'email': 'test@example.com',
                'password': 'password123'
            })
            
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'success' in data
            assert data['success'] is True
            assert 'agent' in data
    
    def test_agent_suggestions_endpoint(self, client):
        """Test agent suggestions endpoint"""
        with patch('agent_manager.agent_manager.get_pending_suggestions') as mock_suggestions:
            mock_suggestions.return_value = []
            
            response = client.get('/api/agent/suggestions')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'suggestions' in data
            assert 'total' in data

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_trading_workflow(self):
        """Test complete trading workflow"""
        # Initialize components
        portfolio_manager = PortfolioManager(initial_capital=100000)
        auto_trader = EnhancedAutoTrader(initial_capital=100000, risk_tolerance='medium')
        
        # Configure trader
        auto_trader.configure({
            'max_position_size': 0.1,
            'stop_loss': 0.05,
            'take_profit': 0.15
        })
        
        # Start trading
        result = auto_trader.start_trading()
        assert result['success'] is True
        assert auto_trader.is_active is True
        
        # Stop trading
        result = auto_trader.stop_trading()
        assert result['success'] is True
        assert auto_trader.is_active is False
    
    def test_agent_customer_workflow(self):
        """Test complete agent-customer workflow"""
        # Create agent manager
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"agents": [], "customers": [], "trade_suggestions": [], "agent_decisions": [], "learning_data": []}')
            temp_file = f.name
        
        try:
            agent_manager = AgentManager(data_file=temp_file)
            
            # Create agent
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
                agent_id=agent.id
            )
            
            # Create trade suggestion
            suggestion = agent_manager.create_trade_suggestion(
                customer_id=customer.id,
                symbol="AAPL",
                action="buy",
                quantity=100,
                price=150.0,
                confidence=0.8,
                reasoning="Strong technical indicators",
                ai_model="gemini"
            )
            
            # Agent makes decision
            decision = agent_manager.make_agent_decision(
                suggestion_id=suggestion.id,
                agent_id=agent.id,
                decision="accept",
                reasoning="Good analysis"
            )
            
            # Verify workflow
            assert agent.id in agent_manager.agents
            assert customer.id in agent_manager.customers
            assert suggestion.id in agent_manager.trade_suggestions
            assert decision.suggestion_id == suggestion.id
            assert suggestion.status == "accept"
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_ai_learning_workflow(self):
        """Test AI learning workflow"""
        # Initialize AI engine
        ai_engine = AISuggestionEngine()
        
        # Simulate learning data
        learning_data = [
            {
                'timestamp': datetime.now().isoformat(),
                'suggestion_id': 'test1',
                'customer_id': 'customer1',
                'agent_id': 'agent1',
                'agent_decision': {'decision': 'accept'},
                'learning_type': 'agent_decision'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'suggestion_id': 'test2',
                'customer_id': 'customer1',
                'agent_id': 'agent1',
                'agent_decision': {'decision': 'reject'},
                'learning_type': 'agent_decision'
            }
        ]
        
        # Update learning weights
        feedback_data = {
            'agent_acceptance_rate': 0.5
        }
        
        ai_engine.update_learning_weights(feedback_data)
        
        # Verify weights are normalized
        total_weight = sum(ai_engine.learning_weights.values())
        assert abs(total_weight - 1.0) < 0.01

class TestPerformance:
    """Performance tests"""
    
    def test_large_dataset_performance(self):
        """Test performance with large dataset"""
        import time
        
        # Create temporary data file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"agents": [], "customers": [], "trade_suggestions": [], "agent_decisions": [], "learning_data": []}')
            temp_file = f.name
        
        try:
            agent_manager = AgentManager(data_file=temp_file)
            
            # Create multiple agents and customers
            start_time = time.time()
            
            agents = []
            for i in range(100):
                agent = agent_manager.create_agent(
                    name=f"Agent {i}",
                    email=f"agent{i}@example.com",
                    password="password123",
                    role=AgentRole.SENIOR
                )
                agents.append(agent)
            
            customers = []
            for i in range(1000):
                customer = agent_manager.create_customer(
                    name=f"Customer {i}",
                    email=f"customer{i}@example.com",
                    phone=f"123-456-{i:04d}",
                    tier=CustomerTier.BASIC,
                    agent_id=agents[i % 100].id
                )
                customers.append(customer)
            
            end_time = time.time()
            creation_time = end_time - start_time
            
            # Should complete within reasonable time
            assert creation_time < 10.0  # 10 seconds max
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_api_response_times(self):
        """Test API response times"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            import time
            
            # Test health endpoint response time
            start_time = time.time()
            response = client.get('/api/health')
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status_code == 200
            assert response_time < 1.0  # 1 second max

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
