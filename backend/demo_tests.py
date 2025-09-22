#!/usr/bin/env python3
"""
Demo Script for AI Stock Trading Bot Tests
Demonstrates key functionality and test capabilities
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_api import (
    RealTradingBot, DayTradingMomentumStrategy, DayTradingRSIStrategy,
    SentimentAnalyzer, LearningSystem, StockData, OrderType
)

def demo_trading_bot():
    """Demonstrate trading bot functionality"""
    print("🤖 Trading Bot Demo")
    print("=" * 40)
    
    # Initialize bot
    bot = RealTradingBot()
    print(f"✅ Bot initialized with ${bot.portfolio.cash:,.2f} capital")
    
    # Add strategies
    momentum_strategy = DayTradingMomentumStrategy({
        'lookback_period': 5,
        'momentum_threshold': 0.01,
        'profit_target': 0.02,
        'stop_loss': 0.01
    })
    
    rsi_strategy = DayTradingRSIStrategy({
        'lookback_period': 14,
        'oversold_threshold': 25,
        'overbought_threshold': 75,
        'profit_target': 0.015,
        'stop_loss': 0.008
    })
    
    bot.add_strategy('momentum', momentum_strategy)
    bot.add_strategy('rsi', rsi_strategy)
    print(f"✅ Added {len(bot.strategies)} trading strategies")
    
    # Start session
    bot._start_new_session()
    print(f"✅ Started trading session for {bot.current_session.date}")
    
    return bot

def demo_sentiment_analysis():
    """Demonstrate sentiment analysis"""
    print("\n📊 Sentiment Analysis Demo")
    print("=" * 40)
    
    analyzer = SentimentAnalyzer()
    
    # Test different sentiments
    test_texts = [
        "Apple reports strong earnings and bullish growth prospects",
        "Market crash and bearish outlook with declining performance",
        "The company reported quarterly results"
    ]
    
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"📝 Text: {text[:50]}...")
        print(f"   Sentiment: {result['sentiment']} (Score: {result['score']:.2f})")
        print(f"   Confidence: {result['confidence']:.2f}")
    
    # Test market events
    events = analyzer.get_market_events("AAPL")
    print(f"✅ Generated {len(events)} market events for AAPL")
    
    return analyzer

def demo_learning_system():
    """Demonstrate machine learning system"""
    print("\n🧠 Learning System Demo")
    print("=" * 40)
    
    learning_system = LearningSystem()
    
    # Generate mock data
    mock_data = [
        StockData(
            symbol="AAPL",
            price=100.0 + i,
            volume=1000000 + i * 10000,
            timestamp=datetime.now(),
            open=99.0 + i,
            high=101.0 + i,
            low=98.0 + i,
            close=100.0 + i,
            change=1.0 + i * 0.1,
            change_percent=1.0 + i * 0.1
        ) for i in range(10)
    ]
    
    # Extract features
    features = learning_system.extract_features(mock_data, 0.5)
    print(f"✅ Extracted {len(features)} features from market data")
    print(f"   Features: {list(features.keys())}")
    
    # Add training samples
    for i in range(60):
        sample_features = {
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
        learning_system.add_training_sample(sample_features, outcome, i * 10)
    
    print(f"✅ Added {len(learning_system.training_data)} training samples")
    
    # Train model
    if learning_system.train_model():
        print("✅ Machine learning model trained successfully")
        
        # Test prediction
        test_features = {
            'momentum': 0.05,
            'rsi': 60,
            'volume_ratio': 1.5,
            'price_change_1d': 0.02,
            'price_change_5d': 0.05,
            'volatility': 0.15,
            'sentiment_score': 0.7,
            'market_hour': 10,
            'day_of_week': 1
        }
        
        prediction = learning_system.predict_outcome(test_features)
        print(f"✅ Prediction: {prediction['prediction']} (Confidence: {prediction['confidence']:.2f})")
    else:
        print("❌ Model training failed")
    
    return learning_system

def demo_strategies():
    """Demonstrate trading strategies"""
    print("\n📈 Trading Strategies Demo")
    print("=" * 40)
    
    # Create strategies
    momentum_strategy = DayTradingMomentumStrategy({
        'lookback_period': 5,
        'momentum_threshold': 0.01
    })
    
    rsi_strategy = DayTradingRSIStrategy({
        'lookback_period': 14,
        'oversold_threshold': 25,
        'overbought_threshold': 75
    })
    
    # Generate test data
    mock_data = [
        StockData(
            symbol="AAPL",
            price=100.0 + i * 0.5,
            volume=1000000,
            timestamp=datetime.now(),
            open=99.0 + i * 0.5,
            high=101.0 + i * 0.5,
            low=98.0 + i * 0.5,
            close=100.0 + i * 0.5,
            change=i * 0.5,
            change_percent=i * 0.5
        ) for i in range(20)
    ]
    
    # Test momentum strategy
    momentum_result = momentum_strategy.analyze(mock_data)
    print(f"✅ Momentum Strategy: {momentum_result.value}")
    
    # Test RSI strategy
    rsi_result = rsi_strategy.analyze(mock_data)
    print(f"✅ RSI Strategy: {rsi_result.value}")
    
    # Test RSI calculation
    prices = [100, 101, 102, 101, 100, 99, 98, 99, 100, 101]
    rsi = rsi_strategy.calculate_rsi(prices)
    print(f"✅ RSI Calculation: {rsi:.2f}")
    
    return momentum_strategy, rsi_strategy

def main():
    """Run all demos"""
    print("🚀 AI Stock Trading Bot - Test Demo")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run demos
        bot = demo_trading_bot()
        analyzer = demo_sentiment_analysis()
        learning_system = demo_learning_system()
        momentum_strategy, rsi_strategy = demo_strategies()
        
        print("\n" + "=" * 50)
        print("✅ All demos completed successfully!")
        print("\n📊 Demo Summary:")
        print(f"   • Trading Bot: {len(bot.strategies)} strategies loaded")
        print(f"   • Sentiment Analysis: {len(analyzer.positive_words)} positive words")
        print(f"   • Learning System: {len(learning_system.training_data)} training samples")
        print(f"   • Strategies: Momentum & RSI strategies tested")
        
        print("\n🧪 To run full tests:")
        print("   python3 test_unit_only.py")
        print("   python3 test_trading_bot.py")
        print("   python3 run_tests.py --type all")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
