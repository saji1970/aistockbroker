#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Stock Trading Bot
Tests all functionality including day trading, learning, sentiment analysis, and API endpoints
"""

import unittest
import json
import time
import requests
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_api import (
    RealTradingBot, DayTradingMomentumStrategy, DayTradingRSIStrategy,
    SentimentAnalyzer, LearningSystem, TradingSession, MarketEvent,
    OrderType, OrderStatus, StockData, Order, Position, Portfolio
)

class TestTradingBotCore(unittest.TestCase):
    """Test core trading bot functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bot = RealTradingBot()
        self.test_symbol = "AAPL"
        self.test_config = {
            'symbol': self.test_symbol,
            'initial_capital': 10000,
            'strategy': 'momentum',
            'max_position_size': 0.1,
            'max_daily_loss': 0.05,
            'risk_tolerance': 'medium'
        }
    
    def test_bot_initialization(self):
        """Test bot initialization"""
        self.assertIsNotNone(self.bot.portfolio)
        self.assertIsNotNone(self.bot.sentiment_analyzer)
        self.assertIsNotNone(self.bot.learning_system)
        self.assertFalse(self.bot.is_running)
        self.assertEqual(self.bot.portfolio.cash, 100000.0)
    
    def test_strategy_adding(self):
        """Test adding trading strategies"""
        momentum_strategy = DayTradingMomentumStrategy({
            'lookback_period': 5,
            'momentum_threshold': 0.01
        })
        
        self.bot.add_strategy('test_momentum', momentum_strategy)
        self.assertIn('test_momentum', self.bot.strategies)
        self.assertEqual(self.bot.strategies['test_momentum'].name, 'DayTradingMomentum')
    
    def test_session_creation(self):
        """Test trading session creation"""
        self.bot._start_new_session()
        self.assertIsNotNone(self.bot.current_session)
        self.assertEqual(self.bot.current_session.date, datetime.now().strftime('%Y-%m-%d'))
        self.assertEqual(self.bot.current_session.initial_capital, self.bot.portfolio.cash)

class TestDayTradingStrategies(unittest.TestCase):
    """Test day trading strategies"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.momentum_strategy = DayTradingMomentumStrategy({
            'lookback_period': 5,
            'momentum_threshold': 0.01,
            'profit_target': 0.02,
            'stop_loss': 0.01,
            'entry_times': [9, 10, 11, 13, 14],
            'exit_time': 15
        })
        
        self.rsi_strategy = DayTradingRSIStrategy({
            'lookback_period': 14,
            'oversold_threshold': 25,
            'overbought_threshold': 75,
            'profit_target': 0.015,
            'stop_loss': 0.008,
            'entry_times': [9, 10, 11, 13, 14],
            'exit_time': 15
        })
        
        # Create mock stock data
        self.mock_data = [
            StockData(
                symbol="AAPL",
                price=100.0,
                open=99.0,
                high=101.0,
                low=98.0,
                close=100.0,
                volume=1000000,
                change_percent=1.0,
                timestamp=datetime.now()
            ) for _ in range(20)
        ]
    
    def test_momentum_strategy_analysis(self):
        """Test momentum strategy analysis"""
        # Test with insufficient data
        result = self.momentum_strategy.analyze(self.mock_data[:3])
        self.assertEqual(result, OrderType.HOLD)
        
        # Test with sufficient data
        result = self.momentum_strategy.analyze(self.mock_data)
        self.assertIn(result, [OrderType.BUY, OrderType.SELL, OrderType.HOLD])
    
    def test_rsi_strategy_analysis(self):
        """Test RSI strategy analysis"""
        # Test with insufficient data
        result = self.rsi_strategy.analyze(self.mock_data[:10])
        self.assertEqual(result, OrderType.HOLD)
        
        # Test with sufficient data
        result = self.rsi_strategy.analyze(self.mock_data)
        self.assertIn(result, [OrderType.BUY, OrderType.SELL, OrderType.HOLD])
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        prices = [100, 101, 102, 101, 100, 99, 98, 99, 100, 101]
        rsi = self.rsi_strategy.calculate_rsi(prices)
        self.assertIsInstance(rsi, float)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
    
    def test_position_exit_logic(self):
        """Test position exit logic"""
        position = Position(
            symbol="AAPL",
            quantity=100,
            avg_price=100.0,
            current_price=102.0,
            unrealized_pnl=200.0,
            realized_pnl=0.0,
            market_value=10200.0
        )
        
        current_data = StockData(
            symbol="AAPL",
            price=102.0,
            open=100.0,
            high=103.0,
            low=99.0,
            close=102.0,
            volume=1000000,
            change_percent=2.0,
            timestamp=datetime.now()
        )
        
        # Test profit target exit
        should_exit = self.momentum_strategy.should_exit(position, current_data)
        self.assertTrue(should_exit)  # 2% profit should trigger exit

class TestSentimentAnalyzer(unittest.TestCase):
    """Test sentiment analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = SentimentAnalyzer()
    
    def test_positive_sentiment(self):
        """Test positive sentiment analysis"""
        text = "Apple reports strong earnings and bullish growth prospects"
        result = self.analyzer.analyze_sentiment(text)
        
        self.assertEqual(result['sentiment'], 'positive')
        self.assertGreater(result['score'], 0)
        self.assertGreater(result['positive_words'], 0)
    
    def test_negative_sentiment(self):
        """Test negative sentiment analysis"""
        text = "Market crash and bearish outlook with declining performance"
        result = self.analyzer.analyze_sentiment(text)
        
        self.assertEqual(result['sentiment'], 'negative')
        self.assertGreater(result['score'], 0)
        self.assertGreater(result['negative_words'], 0)
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment analysis"""
        text = "The company reported quarterly results"
        result = self.analyzer.analyze_sentiment(text)
        
        self.assertEqual(result['sentiment'], 'neutral')
        self.assertEqual(result['score'], 0.0)
    
    def test_market_events(self):
        """Test market event generation"""
        events = self.analyzer.get_market_events("AAPL")
        self.assertIsInstance(events, list)
        
        if events:
            event = events[0]
            self.assertIsInstance(event, MarketEvent)
            self.assertIsNotNone(event.description)
            self.assertIsNotNone(event.sentiment)

class TestLearningSystem(unittest.TestCase):
    """Test machine learning system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.learning_system = LearningSystem()
        
        # Create mock stock data
        self.mock_data = [
            StockData(
                symbol="AAPL",
                price=100.0 + i,
                open=99.0 + i,
                high=101.0 + i,
                low=98.0 + i,
                close=100.0 + i,
                volume=1000000 + i * 10000,
                change_percent=1.0 + i * 0.1,
                timestamp=datetime.now() - timedelta(minutes=i)
            ) for i in range(10)
        ]
    
    def test_feature_extraction(self):
        """Test feature extraction"""
        features = self.learning_system.extract_features(self.mock_data, 0.5)
        
        self.assertIsInstance(features, dict)
        self.assertIn('momentum', features)
        self.assertIn('rsi', features)
        self.assertIn('volume_ratio', features)
        self.assertIn('sentiment_score', features)
        self.assertIn('market_hour', features)
        self.assertIn('day_of_week', features)
    
    def test_training_sample_addition(self):
        """Test adding training samples"""
        features = self.learning_system.extract_features(self.mock_data, 0.5)
        
        initial_count = len(self.learning_system.training_data)
        self.learning_system.add_training_sample(features, 'profitable', 100.0)
        
        self.assertEqual(len(self.learning_system.training_data), initial_count + 1)
        self.assertEqual(self.learning_system.training_data[-1]['outcome'], 'profitable')
        self.assertEqual(self.learning_system.training_data[-1]['pnl'], 100.0)
    
    def test_model_training(self):
        """Test model training"""
        # Add enough training samples
        for i in range(60):
            features = {
                'momentum': i * 0.01,
                'rsi': 50 + i,
                'volume_ratio': 1.0 + i * 0.1,
                'price_change_1d': i * 0.01,
                'price_change_5d': i * 0.02,
                'volatility': 0.1 + i * 0.01,
                'sentiment_score': 0.5,
                'market_hour': 10,
                'day_of_week': 1
            }
            outcome = 'profitable' if i % 2 == 0 else 'loss'
            self.learning_system.add_training_sample(features, outcome, i * 10)
        
        # Train the model
        result = self.learning_system.train_model()
        self.assertTrue(result)
        self.assertTrue(self.learning_system.is_trained)

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "https://ai-stock-trading-simple-720013332324.us-central1.run.app"
        self.headers = {"Content-Type": "application/json"}
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{self.base_url}/api/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
    
    def test_start_bot_endpoint(self):
        """Test start bot endpoint"""
        config = {
            "symbol": "AAPL",
            "initial_capital": 10000,
            "strategy": "momentum",
            "max_position_size": 0.1,
            "max_daily_loss": 0.05,
            "risk_tolerance": "medium"
        }
        
        response = requests.post(
            f"{self.base_url}/api/start",
            headers=self.headers,
            json=config
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'started')
        self.assertIn('bot_id', data)
        self.assertIn('config', data)
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = requests.get(f"{self.base_url}/api/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('mode', data)
        self.assertIn('last_update', data)
    
    def test_portfolio_endpoint(self):
        """Test portfolio endpoint"""
        response = requests.get(f"{self.base_url}/api/portfolio")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('cash_balance', data)
        self.assertIn('positions', data)
        self.assertIn('total_value', data)
        self.assertIn('timestamp', data)
    
    def test_orders_endpoint(self):
        """Test orders endpoint"""
        response = requests.get(f"{self.base_url}/api/orders")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('orders', data)
        self.assertIn('timestamp', data)
        self.assertIsInstance(data['orders'], list)
    
    def test_learning_insights_endpoint(self):
        """Test learning insights endpoint"""
        response = requests.get(f"{self.base_url}/api/learning/insights")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('current_session', data)
        self.assertIn('model_status', data)
        self.assertIn('recommendations', data)
        self.assertIn('timestamp', data)
    
    def test_learning_sessions_endpoint(self):
        """Test learning sessions endpoint"""
        response = requests.get(f"{self.base_url}/api/learning/sessions")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('sessions', data)
        self.assertIn('total_sessions', data)
        self.assertIn('timestamp', data)
        self.assertIsInstance(data['sessions'], list)
    
    def test_learning_report_endpoint(self):
        """Test learning report endpoint"""
        response = requests.get(f"{self.base_url}/api/learning/report")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('date', data)
        self.assertIn('performance', data)
        self.assertIn('market_analysis', data)
        self.assertIn('learning_insights', data)
        self.assertIn('recommendations', data)

class TestIntegration(unittest.TestCase):
    """Test integration scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "https://ai-stock-trading-simple-720013332324.us-central1.run.app"
    
    def test_full_trading_cycle(self):
        """Test a complete trading cycle"""
        # Start the bot
        config = {
            "symbol": "AAPL",
            "initial_capital": 10000,
            "strategy": "momentum",
            "max_position_size": 0.1,
            "max_daily_loss": 0.05,
            "risk_tolerance": "medium"
        }
        
        start_response = requests.post(
            f"{self.base_url}/api/start",
            headers={"Content-Type": "application/json"},
            json=config
        )
        self.assertEqual(start_response.status_code, 200)
        
        # Wait a moment for the bot to initialize
        time.sleep(5)
        
        # Check status
        status_response = requests.get(f"{self.base_url}/api/status")
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        self.assertEqual(status_data['status'], 'started')
        
        # Check learning insights
        insights_response = requests.get(f"{self.base_url}/api/learning/insights")
        self.assertEqual(insights_response.status_code, 200)
        insights_data = insights_response.json()
        self.assertIn('current_session', insights_data)
        
        # Stop the bot
        stop_response = requests.post(f"{self.base_url}/api/stop")
        self.assertEqual(stop_response.status_code, 200)
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid endpoint
        response = requests.get(f"{self.base_url}/api/invalid")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid start configuration
        invalid_config = {"invalid": "config"}
        response = requests.post(
            f"{self.base_url}/api/start",
            headers={"Content-Type": "application/json"},
            json=invalid_config
        )
        # Should still work with defaults
        self.assertEqual(response.status_code, 200)

class TestPerformance(unittest.TestCase):
    """Test performance and scalability"""
    
    def test_strategy_performance(self):
        """Test strategy performance under various conditions"""
        momentum_strategy = DayTradingMomentumStrategy({
            'lookback_period': 5,
            'momentum_threshold': 0.01
        })
        
        # Test with different market conditions
        test_cases = [
            # Bullish market
            [StockData("AAPL", 100 + i, 99 + i, 101 + i, 98 + i, 100 + i, 1000000, 1.0 + i * 0.1, datetime.now()) for i in range(10)],
            # Bearish market
            [StockData("AAPL", 100 - i, 99 - i, 101 - i, 98 - i, 100 - i, 1000000, -1.0 - i * 0.1, datetime.now()) for i in range(10)],
            # Sideways market
            [StockData("AAPL", 100 + (i % 2) * 0.5, 99, 101, 98, 100 + (i % 2) * 0.5, 1000000, 0.0, datetime.now()) for i in range(10)]
        ]
        
        for test_data in test_cases:
            result = momentum_strategy.analyze(test_data)
            self.assertIn(result, [OrderType.BUY, OrderType.SELL, OrderType.HOLD])
    
    def test_learning_system_performance(self):
        """Test learning system performance"""
        learning_system = LearningSystem()
        
        # Test with large dataset
        for i in range(100):
            features = {
                'momentum': i * 0.01,
                'rsi': 50 + i % 50,
                'volume_ratio': 1.0 + i * 0.01,
                'price_change_1d': i * 0.01,
                'price_change_5d': i * 0.02,
                'volatility': 0.1 + i * 0.001,
                'sentiment_score': 0.5,
                'market_hour': i % 24,
                'day_of_week': i % 7
            }
            outcome = 'profitable' if i % 3 == 0 else 'loss' if i % 3 == 1 else 'neutral'
            learning_system.add_training_sample(features, outcome, i * 10)
        
        # Should be able to train with 100 samples
        result = learning_system.train_model()
        self.assertTrue(result)
        self.assertTrue(learning_system.is_trained)

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTradingBotCore,
        TestDayTradingStrategies,
        TestSentimentAnalyzer,
        TestLearningSystem,
        TestAPIEndpoints,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🧪 Running Comprehensive Trading Bot Test Suite")
    print("=" * 60)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed!")
        exit(1)