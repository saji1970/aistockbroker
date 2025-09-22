#!/usr/bin/env python3
"""
Unit Tests for Trading Bot Core Functionality
Tests that don't require API calls or external dependencies
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

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
                volume=1000000,
                timestamp=datetime.now(),
                open=99.0,
                high=101.0,
                low=98.0,
                close=100.0,
                change=1.0,
                change_percent=1.0
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
            volume=1000000,
            timestamp=datetime.now(),
            open=100.0,
            high=103.0,
            low=99.0,
            close=102.0,
            change=2.0,
            change_percent=2.0
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
                volume=1000000 + i * 10000,
                timestamp=datetime.now() - timedelta(minutes=i),
                open=99.0 + i,
                high=101.0 + i,
                low=98.0 + i,
                close=100.0 + i,
                change=1.0 + i * 0.1,
                change_percent=1.0 + i * 0.1
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
            [StockData("AAPL", 100 + i, 1000000, datetime.now(), 99 + i, 101 + i, 98 + i, 100 + i, 1.0 + i * 0.1, 1.0 + i * 0.1) for i in range(10)],
            # Bearish market
            [StockData("AAPL", 100 - i, 1000000, datetime.now(), 99 - i, 101 - i, 98 - i, 100 - i, -1.0 - i * 0.1, -1.0 - i * 0.1) for i in range(10)],
            # Sideways market
            [StockData("AAPL", 100 + (i % 2) * 0.5, 1000000, datetime.now(), 99, 101, 98, 100 + (i % 2) * 0.5, 0.0, 0.0) for i in range(10)]
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

if __name__ == '__main__':
    print("🧪 Running Unit Tests for Trading Bot")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTradingBotCore,
        TestDayTradingStrategies,
        TestSentimentAnalyzer,
        TestLearningSystem,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    if result.wasSuccessful():
        print("\n✅ All unit tests passed!")
        exit(0)
    else:
        print("\n❌ Some unit tests failed!")
        exit(1)
