#!/usr/bin/env python3
"""
Advanced AI Trading Bot with Machine Learning and Advanced Strategies
"""

import asyncio
import json
import logging
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

# Import base classes from shadow_trading_bot
from shadow_trading_bot import (
    OrderType, OrderStatus, StockData, Order, Position, Portfolio,
    TradingStrategy, MarketDataProvider, RiskManager, ShadowTradingBot
)

class MLStrategy(TradingStrategy):
    """Machine Learning based trading strategy"""
    
    def __init__(self, parameters: Dict):
        super().__init__("ML_Strategy", parameters)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'rsi', 'macd', 'bollinger_upper', 'bollinger_lower', 'volume_ratio',
            'price_change_1d', 'price_change_5d', 'volatility', 'momentum'
        ]
        self.is_trained = False
        
    def calculate_technical_indicators(self, data: List[StockData]) -> pd.DataFrame:
        """Calculate technical indicators for ML features"""
        if len(data) < 20:
            return pd.DataFrame()
            
        df = pd.DataFrame([{
            'close': d.close,
            'volume': d.volume,
            'high': d.high,
            'low': d.low
        } for d in data])
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        
        # Bollinger Bands
        df['bollinger_middle'] = df['close'].rolling(window=20).mean()
        df['bollinger_std'] = df['close'].rolling(window=20).std()
        df['bollinger_upper'] = df['bollinger_middle'] + (df['bollinger_std'] * 2)
        df['bollinger_lower'] = df['bollinger_middle'] - (df['bollinger_std'] * 2)
        
        # Volume ratio
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Price changes
        df['price_change_1d'] = df['close'].pct_change(1)
        df['price_change_5d'] = df['close'].pct_change(5)
        
        # Volatility
        df['volatility'] = df['close'].rolling(window=20).std()
        
        # Momentum
        df['momentum'] = df['close'] / df['close'].shift(10) - 1
        
        return df
        
    def prepare_features(self, data: List[StockData]) -> np.ndarray:
        """Prepare features for ML model"""
        df = self.calculate_technical_indicators(data)
        if df.empty or len(df) < 20:
            return np.array([])
            
        # Get latest features
        latest_features = df[self.feature_columns].iloc[-1:].fillna(0)
        return latest_features.values
        
    def train_model(self, training_data: Dict[str, List[StockData]]):
        """Train the ML model on historical data"""
        X, y = [], []
        
        for symbol, data in training_data.items():
            if len(data) < 50:
                continue
                
            df = self.calculate_technical_indicators(data)
            if df.empty:
                continue
                
            # Create labels based on future returns
            df['future_return'] = df['close'].shift(-5) / df['close'] - 1
            
            # Create buy/sell/hold signals
            df['signal'] = 0  # Hold
            df.loc[df['future_return'] > 0.02, 'signal'] = 1  # Buy
            df.loc[df['future_return'] < -0.02, 'signal'] = -1  # Sell
            
            # Prepare features and labels
            features = df[self.feature_columns].fillna(0)
            labels = df['signal'].fillna(0)
            
            # Remove rows with NaN labels
            valid_indices = ~labels.isna()
            X.extend(features[valid_indices].values)
            y.extend(labels[valid_indices].values)
            
        if len(X) < 100:
            logging.warning("Insufficient training data for ML model")
            return
            
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Evaluate model
        y_pred = self.model.predict(X_scaled)
        accuracy = accuracy_score(y, y_pred)
        logging.info(f"ML Model trained with accuracy: {accuracy:.3f}")
        
    def analyze(self, data: List[StockData]) -> OrderType:
        """Analyze using ML model"""
        if not self.is_trained or not self.model:
            return OrderType.HOLD
            
        features = self.prepare_features(data)
        if features.size == 0:
            return OrderType.HOLD
            
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        
        if prediction == 1:
            return OrderType.BUY
        elif prediction == -1:
            return OrderType.SELL
        else:
            return OrderType.HOLD
            
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        """ML-based exit strategy"""
        # Simple exit based on position P&L
        pnl_percent = position.unrealized_pnl / (position.quantity * position.avg_price)
        return pnl_percent < -0.05 or pnl_percent > 0.10

class SentimentStrategy(TradingStrategy):
    """Sentiment-based trading strategy using news and social media"""
    
    def __init__(self, parameters: Dict):
        super().__init__("Sentiment", parameters)
        self.sentiment_threshold = parameters.get('sentiment_threshold', 0.6)
        self.news_weight = parameters.get('news_weight', 0.7)
        self.social_weight = parameters.get('social_weight', 0.3)
        
    def get_sentiment_score(self, symbol: str) -> float:
        """Get sentiment score for a symbol (mock implementation)"""
        # In a real implementation, this would fetch from news APIs, social media APIs, etc.
        # For now, we'll use a simple random-based sentiment
        import random
        return random.uniform(0.3, 0.8)
        
    def analyze(self, data: List[StockData]) -> OrderType:
        """Analyze based on sentiment"""
        if len(data) < 5:
            return OrderType.HOLD
            
        symbol = data[-1].symbol
        sentiment_score = self.get_sentiment_score(symbol)
        
        if sentiment_score > self.sentiment_threshold:
            return OrderType.BUY
        elif sentiment_score < (1 - self.sentiment_threshold):
            return OrderType.SELL
        else:
            return OrderType.HOLD
            
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        """Exit based on sentiment reversal"""
        sentiment_score = self.get_sentiment_score(position.symbol)
        return sentiment_score < 0.4  # Exit if sentiment becomes negative

class AdvancedRiskManager(RiskManager):
    """Enhanced risk management with portfolio-level controls"""
    
    def __init__(self, max_position_size: float = 0.1, max_daily_loss: float = 0.05):
        super().__init__(max_position_size, max_daily_loss)
        self.max_correlation = 0.7
        self.max_sector_exposure = 0.3
        self.var_limit = 0.02  # 2% Value at Risk limit
        
    def calculate_portfolio_var(self, portfolio: Portfolio, market_data: MarketDataProvider) -> float:
        """Calculate portfolio Value at Risk"""
        if not portfolio.positions:
            return 0.0
            
        # Simple VaR calculation based on position weights and volatility
        total_var = 0.0
        for symbol, position in portfolio.positions.items():
            # Get recent volatility
            hist_data = market_data.get_historical_data(symbol, "1mo")
            if len(hist_data) > 20:
                returns = [d.change_percent / 100 for d in hist_data[-20:]]
                volatility = np.std(returns)
                weight = position.market_value / portfolio.total_value
                total_var += (weight * volatility * 1.96) ** 2  # 95% confidence
                
        return np.sqrt(total_var)
        
    def can_open_position(self, portfolio: Portfolio, symbol: str, quantity: int, price: float) -> bool:
        """Enhanced position opening checks"""
        # Basic checks
        if not super().can_open_position(portfolio, symbol, quantity, price):
            return False
            
        # Check sector exposure (simplified)
        # In a real implementation, you'd check actual sector classifications
        tech_stocks = ['AAPL', 'GOOGL', 'MSFT', 'META', 'NVDA', 'TSLA']
        if symbol in tech_stocks:
            tech_exposure = sum(
                pos.market_value for sym, pos in portfolio.positions.items() 
                if sym in tech_stocks
            ) / portfolio.total_value
            
            if tech_exposure > self.max_sector_exposure:
                logging.warning(f"Sector exposure limit reached for {symbol}")
                return False
                
        return True

class AdvancedTradingBot(ShadowTradingBot):
    """Enhanced trading bot with ML and advanced strategies"""
    
    def __init__(self, initial_capital: float = 100000.0, config_file: str = "trading_bot_config.json"):
        super().__init__(initial_capital)
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Enhanced components
        self.risk_manager = AdvancedRiskManager(
            max_position_size=self.config['bot_settings']['max_position_size'],
            max_daily_loss=self.config['bot_settings']['max_daily_loss']
        )
        
        # Initialize advanced strategies
        self.strategies['ml'] = MLStrategy(self.config['strategies'].get('ml', {}))
        self.strategies['sentiment'] = SentimentStrategy(self.config['strategies'].get('sentiment', {}))
        
        # Training data for ML
        self.training_data = {}
        self.model_retrain_interval = 7  # Retrain every 7 days
        self.last_model_training = datetime.now()
        
        # Performance tracking
        self.performance_history = []
        self.trade_analysis = []
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"Config file {config_file} not found, using defaults")
            return {
                'bot_settings': {
                    'max_position_size': 0.1,
                    'max_daily_loss': 0.05
                },
                'strategies': {}
            }
            
    def collect_training_data(self):
        """Collect training data for ML strategies"""
        for symbol in self.watchlist:
            try:
                hist_data = self.market_data.get_historical_data(symbol, "6mo")
                if hist_data:
                    self.training_data[symbol] = hist_data
            except Exception as e:
                logging.error(f"Error collecting training data for {symbol}: {e}")
                
    def train_ml_models(self):
        """Train ML models with collected data"""
        if not self.training_data:
            self.collect_training_data()
            
        if self.training_data:
            ml_strategy = self.strategies.get('ml')
            if ml_strategy:
                ml_strategy.train_model(self.training_data)
                self.last_model_training = datetime.now()
                logging.info("ML models trained successfully")
                
    def analyze_market_conditions(self) -> Dict:
        """Analyze overall market conditions"""
        market_conditions = {
            'volatility': 'normal',
            'trend': 'neutral',
            'sentiment': 'neutral'
        }
        
        # Analyze market volatility using SPY as proxy
        spy_data = self.market_data.get_historical_data('SPY', '1mo')
        if spy_data and len(spy_data) > 20:
            returns = [d.change_percent for d in spy_data[-20:]]
            volatility = np.std(returns)
            
            if volatility > 2.0:
                market_conditions['volatility'] = 'high'
            elif volatility < 0.5:
                market_conditions['volatility'] = 'low'
                
        return market_conditions
        
    def run_strategy(self, symbol: str, strategy_name: str):
        """Enhanced strategy execution with market condition awareness"""
        if strategy_name not in self.strategies:
            return
            
        strategy = self.strategies[strategy_name]
        
        # Check if strategy is enabled
        if not self.config['strategies'].get(strategy_name, {}).get('enabled', True):
            return
            
        # Get market conditions
        market_conditions = self.analyze_market_conditions()
        
        # Adjust strategy parameters based on market conditions
        if market_conditions['volatility'] == 'high':
            # Reduce position sizes in high volatility
            original_max_size = self.risk_manager.max_position_size
            self.risk_manager.max_position_size = original_max_size * 0.5
            
        try:
            # Run the strategy
            super().run_strategy(symbol, strategy_name)
        finally:
            # Restore original parameters
            if market_conditions['volatility'] == 'high':
                self.risk_manager.max_position_size = original_max_size
                
    def run_trading_cycle(self):
        """Enhanced trading cycle with ML training and analysis"""
        logging.info("Starting advanced trading cycle...")
        
        # Check if ML models need retraining
        days_since_training = (datetime.now() - self.last_model_training).days
        if days_since_training >= self.model_retrain_interval:
            self.train_ml_models()
            
        # Run standard trading cycle
        super().run_trading_cycle()
        
        # Analyze trades and update performance
        self.analyze_trades()
        
        # Log advanced metrics
        self._log_advanced_metrics()
        
    def analyze_trades(self):
        """Analyze recent trades for performance insights"""
        recent_orders = [order for order in self.portfolio.orders 
                        if order.timestamp > datetime.now() - timedelta(days=1)]
        
        if recent_orders:
            trade_analysis = {
                'timestamp': datetime.now().isoformat(),
                'total_trades': len(recent_orders),
                'buy_trades': len([o for o in recent_orders if o.order_type == OrderType.BUY]),
                'sell_trades': len([o for o in recent_orders if o.order_type == OrderType.SELL]),
                'strategy_performance': {}
            }
            
            # Analyze by strategy
            for strategy_name in self.strategies.keys():
                strategy_orders = [o for o in recent_orders if o.strategy == strategy_name]
                if strategy_orders:
                    trade_analysis['strategy_performance'][strategy_name] = len(strategy_orders)
                    
            self.trade_analysis.append(trade_analysis)
            
    def _log_advanced_metrics(self):
        """Log advanced performance metrics"""
        # Calculate Sharpe ratio (simplified)
        if len(self.performance_history) > 30:
            returns = [p['return'] for p in self.performance_history[-30:]]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            logging.info(f"Sharpe Ratio (30d): {sharpe_ratio:.3f}")
            
        # Log ML model performance
        ml_strategy = self.strategies.get('ml')
        if ml_strategy and ml_strategy.is_trained:
            logging.info("ML Strategy: Model trained and active")
            
        # Log risk metrics
        var = self.risk_manager.calculate_portfolio_var(self.portfolio, self.market_data)
        logging.info(f"Portfolio VaR: {var:.3f}")
        
    def get_advanced_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        base_report = self.get_performance_report()
        
        # Add advanced metrics
        advanced_metrics = {
            'ml_model_trained': self.strategies.get('ml', {}).is_trained if hasattr(self.strategies.get('ml', {}), 'is_trained') else False,
            'strategies_active': len([s for s in self.strategies.values() if hasattr(s, 'is_trained') and s.is_trained]),
            'total_trades_analyzed': len(self.trade_analysis),
            'last_model_training': self.last_model_training.isoformat(),
            'risk_metrics': {
                'portfolio_var': self.risk_manager.calculate_portfolio_var(self.portfolio, self.market_data),
                'max_position_size': self.risk_manager.max_position_size,
                'max_daily_loss': self.risk_manager.max_daily_loss
            }
        }
        
        base_report.update(advanced_metrics)
        return base_report

def main():
    """Main function to run the advanced trading bot"""
    # Initialize the advanced bot
    bot = AdvancedTradingBot(initial_capital=100000.0)
    
    # Add some stocks to watchlist
    bot.watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META']
    
    # Train ML models initially
    bot.train_ml_models()
    
    try:
        # Start the bot
        bot.start(interval=300)  # 5 minutes
    except KeyboardInterrupt:
        bot.stop()
        print("\nAdvanced trading bot stopped.")
        
        # Print comprehensive performance report
        report = bot.get_advanced_performance_report()
        print("\n" + "="*60)
        print("ADVANCED TRADING BOT PERFORMANCE REPORT")
        print("="*60)
        print(f"Initial Capital: ${report['initial_capital']:,.2f}")
        print(f"Final Value: ${report['current_value']:,.2f}")
        print(f"Total Return: {report['total_return_pct']:.2f}%")
        print(f"ML Model Trained: {report['ml_model_trained']}")
        print(f"Active Strategies: {report['strategies_active']}")
        print(f"Total Trades: {report['orders_count']}")
        print(f"Portfolio VaR: {report['risk_metrics']['portfolio_var']:.3f}")

if __name__ == "__main__":
    main()
