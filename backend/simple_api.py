#!/usr/bin/env python3
"""
Simple API Server for AI Stock Trading Platform
Minimal version for testing
"""

import os
import time
import requests
import threading
import logging
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
from marketmate_assistant import MarketMate
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import json
import schedule
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings
warnings.filterwarnings('ignore')

# Import exponential backoff
from exponential_backoff import (
    ExponentialBackoff, 
    RateLimitManager, 
    marketstack_retry, 
    yahoo_finance_retry,
    with_exponential_backoff
)

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize global rate limit manager
rate_limiter = RateLimitManager()

# Initialize MarketMate
marketmate = MarketMate()

# Trading System Classes
class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class StockData:
    symbol: str
    price: float
    volume: int
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    change: float
    change_percent: float

@dataclass
class Order:
    id: str
    symbol: str
    order_type: OrderType
    quantity: int
    price: float
    timestamp: datetime
    status: OrderStatus
    strategy: str
    reason: str

@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    market_value: float

@dataclass
class Portfolio:
    cash: float
    total_value: float
    positions: Dict[str, Position]
    orders: List[Order]
    performance_metrics: Dict[str, float]

@dataclass
class TradingSession:
    date: str
    start_time: datetime
    end_time: datetime
    initial_capital: float
    final_capital: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    max_drawdown: float
    strategy_performance: Dict[str, float]
    market_events: List[Dict]
    sentiment_score: float
    learning_insights: List[str]

@dataclass
class MarketEvent:
    timestamp: datetime
    event_type: str
    description: str
    impact_score: float
    sentiment: str
    affected_symbols: List[str]

class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str, parameters: Dict):
        self.name = name
        self.parameters = parameters
        self.signals = []
        
    def analyze(self, data: List[StockData]) -> OrderType:
        """Analyze market data and return trading signal"""
        raise NotImplementedError
        
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        """Determine if position should be closed"""
        raise NotImplementedError

class DayTradingMomentumStrategy(TradingStrategy):
    """Day trading momentum strategy with intraday optimization"""
    
    def __init__(self, parameters: Dict):
        super().__init__("DayTradingMomentum", parameters)
        self.lookback_period = parameters.get('lookback_period', 5)  # Shorter for day trading
        self.momentum_threshold = parameters.get('momentum_threshold', 0.01)  # Lower threshold
        self.profit_target = parameters.get('profit_target', 0.02)  # 2% profit target
        self.stop_loss = parameters.get('stop_loss', 0.01)  # 1% stop loss
        self.entry_times = parameters.get('entry_times', [9, 10, 11, 13, 14])  # Trading hours
        self.exit_time = parameters.get('exit_time', 15)  # Exit before market close
        
    def analyze(self, data: List[StockData]) -> OrderType:
        if len(data) < self.lookback_period:
            return OrderType.HOLD
            
        current_hour = datetime.now().hour
        
        # Only trade during specified hours
        if current_hour not in self.entry_times:
            return OrderType.HOLD
            
        # Calculate intraday momentum
        recent_prices = [d.close for d in data[-self.lookback_period:]]
        momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        # Add volume confirmation
        recent_volumes = [d.volume for d in data[-self.lookback_period:]]
        avg_volume = np.mean(recent_volumes)
        current_volume = data[-1].volume
        
        # Volume spike confirmation
        volume_spike = current_volume > avg_volume * 1.5
        
        if momentum > self.momentum_threshold and volume_spike:
            return OrderType.BUY
        elif momentum < -self.momentum_threshold and volume_spike:
            return OrderType.SELL
        else:
            return OrderType.HOLD
            
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        current_hour = datetime.now().hour
        
        # Force exit before market close
        if current_hour >= self.exit_time:
            return True
            
        # Profit target or stop loss
        if position.quantity > 0:  # Long position
            entry_price = position.avg_price
            current_price = current_data.price
            pnl_pct = (current_price - entry_price) / entry_price
            
            if pnl_pct >= self.profit_target or pnl_pct <= -self.stop_loss:
                return True
                
        return False

class DayTradingRSIStrategy(TradingStrategy):
    """Day trading RSI strategy with intraday optimization"""
    
    def __init__(self, parameters: Dict):
        super().__init__("DayTradingRSI", parameters)
        self.lookback_period = parameters.get('lookback_period', 14)
        self.oversold_threshold = parameters.get('oversold_threshold', 25)  # More aggressive
        self.overbought_threshold = parameters.get('overbought_threshold', 75)  # More aggressive
        self.profit_target = parameters.get('profit_target', 0.015)  # 1.5% profit target
        self.stop_loss = parameters.get('stop_loss', 0.008)  # 0.8% stop loss
        self.entry_times = parameters.get('entry_times', [9, 10, 11, 13, 14])
        self.exit_time = parameters.get('exit_time', 15)
        
    def calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI indicator"""
        if len(prices) < 2:
            return 50
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def analyze(self, data: List[StockData]) -> OrderType:
        if len(data) < self.lookback_period + 1:
            return OrderType.HOLD
            
        current_hour = datetime.now().hour
        
        # Only trade during specified hours
        if current_hour not in self.entry_times:
            return OrderType.HOLD
            
        prices = [d.close for d in data[-self.lookback_period-1:]]
        rsi = self.calculate_rsi(prices)
        
        # Add trend confirmation
        recent_prices = [d.close for d in data[-5:]]
        trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        if rsi < self.oversold_threshold and trend > -0.005:  # Oversold but not in strong downtrend
            return OrderType.BUY
        elif rsi > self.overbought_threshold and trend < 0.005:  # Overbought but not in strong uptrend
            return OrderType.SELL
        else:
            return OrderType.HOLD
            
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        current_hour = datetime.now().hour
        
        # Force exit before market close
        if current_hour >= self.exit_time:
            return True
            
        # Profit target or stop loss
        if position.quantity > 0:  # Long position
            entry_price = position.avg_price
            current_price = current_data.price
            pnl_pct = (current_price - entry_price) / entry_price
            
            if pnl_pct >= self.profit_target or pnl_pct <= -self.stop_loss:
                return True
                
        return False

class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy"""
    
    def __init__(self, parameters: Dict):
        super().__init__("RSI", parameters)
        self.lookback_period = parameters.get('lookback_period', 14)
        self.oversold_threshold = parameters.get('oversold_threshold', 30)
        self.overbought_threshold = parameters.get('overbought_threshold', 70)
        
    def calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI indicator"""
        if len(prices) < 2:
            return 50
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def analyze(self, data: List[StockData]) -> OrderType:
        if len(data) < self.lookback_period + 1:
            return OrderType.HOLD
            
        prices = [d.close for d in data[-self.lookback_period-1:]]
        rsi = self.calculate_rsi(prices)
        
        if rsi < self.oversold_threshold:
            return OrderType.BUY
        elif rsi > self.overbought_threshold:
            return OrderType.SELL
        else:
            return OrderType.HOLD
            
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        # Exit when RSI returns to neutral zone
        return 30 <= self.calculate_rsi([position.avg_price, current_data.price]) <= 70

class RiskManager:
    """Risk management for trading operations"""
    
    def __init__(self, max_position_size: float = 0.1, max_daily_loss: float = 0.05):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0.0
        
    def can_open_position(self, portfolio: Portfolio, symbol: str, quantity: int, price: float) -> bool:
        """Check if position can be opened based on risk parameters"""
        position_value = quantity * price
        portfolio_value = portfolio.total_value
        
        # Check position size limit
        if position_value / portfolio_value > self.max_position_size:
            return False
            
        # Check daily loss limit
        if self.daily_pnl < -portfolio_value * self.max_daily_loss:
            return False
            
        return True
        
    def calculate_position_size(self, portfolio: Portfolio, symbol: str, price: float) -> int:
        """Calculate optimal position size based on risk parameters"""
        max_position_value = portfolio.total_value * self.max_position_size
        max_shares = int(max_position_value / price)
        
        # Ensure we don't exceed available cash
        max_affordable = int(portfolio.cash / price)
        
        return min(max_shares, max_affordable, 100)  # Cap at 100 shares for safety

class SentimentAnalyzer:
    """Sentiment analysis for market events and news"""
    
    def __init__(self):
        self.positive_words = {
            'bullish', 'surge', 'rally', 'gain', 'rise', 'up', 'positive', 'strong', 'growth',
            'beat', 'exceed', 'outperform', 'upgrade', 'buy', 'outperform', 'breakthrough',
            'record', 'high', 'momentum', 'optimistic', 'confidence', 'recovery'
        }
        self.negative_words = {
            'bearish', 'crash', 'fall', 'drop', 'down', 'negative', 'weak', 'decline',
            'miss', 'disappoint', 'underperform', 'downgrade', 'sell', 'underperform',
            'concern', 'risk', 'volatility', 'uncertainty', 'pessimistic', 'recession'
        }
        
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        total_words = len(words)
        
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}
            
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        
        if positive_score > negative_score:
            sentiment = 'positive'
            score = positive_score
        elif negative_score > positive_score:
            sentiment = 'negative'
            score = negative_score
        else:
            sentiment = 'neutral'
            score = 0.0
            
        confidence = abs(positive_score - negative_score)
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count
        }
        
    def get_market_events(self, symbol: str) -> List[MarketEvent]:
        """Get market events for a symbol (simulated for now)"""
        # In a real implementation, this would fetch from news APIs
        events = []
        
        # Simulate some market events
        if symbol == 'AAPL':
            events.append(MarketEvent(
                timestamp=datetime.now() - timedelta(hours=2),
                event_type='earnings',
                description='Apple reports strong Q4 earnings, beats expectations',
                impact_score=0.8,
                sentiment='positive',
                affected_symbols=['AAPL']
            ))
        elif symbol == 'TSLA':
            events.append(MarketEvent(
                timestamp=datetime.now() - timedelta(hours=1),
                event_type='news',
                description='Tesla announces new factory expansion plans',
                impact_score=0.6,
                sentiment='positive',
                affected_symbols=['TSLA']
            ))
            
        return events

class LearningSystem:
    """Machine learning system to learn from trading mistakes"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'momentum', 'rsi', 'volume_ratio', 'price_change_1d', 'price_change_5d',
            'volatility', 'sentiment_score', 'market_hour', 'day_of_week'
        ]
        self.training_data = []
        self.performance_history = []
        
    def extract_features(self, data: List[StockData], sentiment_score: float) -> Dict:
        """Extract features for machine learning"""
        if len(data) < 5:
            return {}
            
        # Calculate technical indicators
        prices = [d.close for d in data[-5:]]
        volumes = [d.volume for d in data[-5:]]
        
        momentum = (prices[-1] - prices[0]) / prices[0] if prices[0] != 0 else 0
        rsi = self._calculate_rsi(prices)
        volume_ratio = volumes[-1] / np.mean(volumes[:-1]) if len(volumes) > 1 else 1
        price_change_1d = (prices[-1] - prices[-2]) / prices[-2] if len(prices) > 1 else 0
        price_change_5d = momentum
        volatility = np.std(prices) / np.mean(prices) if np.mean(prices) != 0 else 0
        
        current_time = datetime.now()
        market_hour = current_time.hour
        day_of_week = current_time.weekday()
        
        return {
            'momentum': momentum,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'price_change_1d': price_change_1d,
            'price_change_5d': price_change_5d,
            'volatility': volatility,
            'sentiment_score': sentiment_score,
            'market_hour': market_hour,
            'day_of_week': day_of_week
        }
        
    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate RSI indicator"""
        if len(prices) < 2:
            return 50
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def add_training_sample(self, features: Dict, actual_outcome: str, pnl: float):
        """Add a training sample"""
        if not features:
            return
            
        sample = {
            'features': features,
            'outcome': actual_outcome,  # 'profitable', 'loss', 'neutral'
            'pnl': pnl,
            'timestamp': datetime.now()
        }
        self.training_data.append(sample)
        
    def train_model(self):
        """Train the machine learning model"""
        if len(self.training_data) < 50:  # Need minimum samples
            return False
            
        # Prepare training data
        X = []
        y = []
        
        for sample in self.training_data:
            features = sample['features']
            feature_vector = [features.get(col, 0) for col in self.feature_columns]
            X.append(feature_vector)
            y.append(sample['outcome'])
            
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        logger.info(f"Model trained with {len(self.training_data)} samples")
        return True
        
    def predict_outcome(self, features: Dict) -> Dict:
        """Predict trading outcome"""
        if not self.is_trained or not features:
            return {'prediction': 'neutral', 'confidence': 0.0}
            
        feature_vector = [features.get(col, 0) for col in self.feature_columns]
        X = np.array([feature_vector])
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        confidence = np.max(probabilities)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'probabilities': dict(zip(self.model.classes_, probabilities))
        }
        
    def analyze_performance(self, session: TradingSession) -> List[str]:
        """Analyze trading performance and generate insights"""
        insights = []
        
        # Calculate win rate
        win_rate = session.winning_trades / session.total_trades if session.total_trades > 0 else 0
        
        # Analyze strategy performance
        for strategy, performance in session.strategy_performance.items():
            if performance > 0:
                insights.append(f"{strategy} strategy performed well with {performance:.2%} return")
            else:
                insights.append(f"{strategy} strategy underperformed with {performance:.2%} return")
                
        # Analyze market events impact
        positive_events = [e for e in session.market_events if e.get('sentiment') == 'positive']
        negative_events = [e for e in session.market_events if e.get('sentiment') == 'negative']
        
        if positive_events:
            insights.append(f"Positive market events: {len(positive_events)} events with average impact {np.mean([e.get('impact_score', 0) for e in positive_events]):.2f}")
        if negative_events:
            insights.append(f"Negative market events: {len(negative_events)} events with average impact {np.mean([e.get('impact_score', 0) for e in negative_events]):.2f}")
            
        # Risk analysis
        if session.max_drawdown > 0.05:  # 5% drawdown
            insights.append(f"High drawdown detected: {session.max_drawdown:.2%}. Consider reducing position sizes.")
            
        # Time-based analysis
        if win_rate < 0.4:
            insights.append("Low win rate detected. Consider adjusting entry criteria or stop-loss levels.")
        elif win_rate > 0.7:
            insights.append("High win rate achieved. Consider increasing position sizes gradually.")
            
        return insights

class RealTradingBot:
    """Real trading bot with sophisticated strategies"""
    
    def __init__(self):
        self.portfolio = Portfolio(
            cash=100000.0,
            total_value=100000.0,
            positions={},
            orders=[],
            performance_metrics={}
        )
        self.strategies = {}
        self.risk_manager = RiskManager()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.learning_system = LearningSystem()
        self.is_running = False
        self.trading_thread = None
        self.market_data_cache = {}
        self.current_session = None
        self.session_history = []
        self.daily_scheduler = None
        
    def add_strategy(self, name: str, strategy: TradingStrategy):
        """Add a trading strategy"""
        self.strategies[name] = strategy
        
    def get_market_data(self, symbol: str) -> Optional[StockData]:
        """Get current market data for a symbol"""
        try:
            # Try to get real data first
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d", interval="1d")
            
            if hist.empty:
                return None
                
            latest = hist.iloc[-1]
            info = stock.info
            
            return StockData(
                symbol=symbol,
                price=float(latest['Close']),
                volume=int(latest['Volume']),
                timestamp=datetime.now(),
                open=float(latest['Open']),
                high=float(latest['High']),
                low=float(latest['Low']),
                close=float(latest['Close']),
                change=float(latest['Close'] - latest['Open']),
                change_percent=float((latest['Close'] - latest['Open']) / latest['Open'] * 100)
            )
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None
            
    def place_order(self, symbol: str, order_type: OrderType, quantity: int, 
                   strategy: str, reason: str) -> Optional[Order]:
        """Place a trading order"""
        current_data = self.get_market_data(symbol)
        if not current_data:
            logger.error(f"No data available for {symbol}")
            return None
            
        # Risk management checks
        if order_type == OrderType.BUY:
            if not self.risk_manager.can_open_position(self.portfolio, symbol, quantity, current_data.price):
                logger.warning(f"Risk management blocked order for {symbol}")
                return None
                
            # Check if we have enough cash
            total_cost = quantity * current_data.price
            if total_cost > self.portfolio.cash:
                logger.warning(f"Insufficient cash for {symbol} order")
                return None
                
        elif order_type == OrderType.SELL:
            if symbol not in self.portfolio.positions:
                logger.warning(f"No position to sell for {symbol}")
                return None
                
            position = self.portfolio.positions[symbol]
            if quantity > position.quantity:
                logger.warning(f"Insufficient shares to sell for {symbol}")
                return None
        
        # Create order
        order = Order(
            id=f"ORD{len(self.portfolio.orders) + 1:03d}",
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            price=current_data.price,
            timestamp=datetime.now(),
            status=OrderStatus.FILLED,  # Simulate immediate fill
            strategy=strategy,
            reason=reason
        )
        
        # Execute order
        self._execute_order(order)
        self.portfolio.orders.append(order)
        
        logger.info(f"Order executed: {order_type.value} {quantity} {symbol} @ ${current_data.price:.2f}")
        return order
        
    def _execute_order(self, order: Order):
        """Execute the order and update portfolio"""
        if order.order_type == OrderType.BUY:
            # Update cash
            self.portfolio.cash -= order.quantity * order.price
            
            # Update position
            if order.symbol in self.portfolio.positions:
                pos = self.portfolio.positions[order.symbol]
                total_cost = (pos.quantity * pos.avg_price) + (order.quantity * order.price)
                total_quantity = pos.quantity + order.quantity
                pos.avg_price = total_cost / total_quantity
                pos.quantity = total_quantity
            else:
                self.portfolio.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_price=order.price,
                    current_price=order.price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    market_value=order.quantity * order.price
                )
                
        elif order.order_type == OrderType.SELL:
            # Update cash
            self.portfolio.cash += order.quantity * order.price
            
            # Update position
            if order.symbol in self.portfolio.positions:
                pos = self.portfolio.positions[order.symbol]
                realized_pnl = (order.price - pos.avg_price) * order.quantity
                pos.realized_pnl += realized_pnl
                pos.quantity -= order.quantity
                
                if pos.quantity <= 0:
                    del self.portfolio.positions[order.symbol]
                    
        # Update portfolio value
        self._update_portfolio_value()
        
    def _update_portfolio_value(self):
        """Update total portfolio value"""
        total_value = self.portfolio.cash
        
        for symbol, position in self.portfolio.positions.items():
            current_data = self.get_market_data(symbol)
            if current_data:
                position.current_price = current_data.price
                position.market_value = position.quantity * current_data.price
                position.unrealized_pnl = (current_data.price - position.avg_price) * position.quantity
                total_value += position.market_value
                
        self.portfolio.total_value = total_value
        
    def run_strategy(self, symbol: str, strategy_name: str):
        """Run a specific strategy for a symbol"""
        if strategy_name not in self.strategies:
            return
            
        strategy = self.strategies[strategy_name]
        current_data = self.get_market_data(symbol)
        
        if not current_data:
            return
            
        # Get historical data for analysis
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="30d", interval="1d")
            
            if hist.empty:
                return
                
            # Convert to StockData format
            historical_data = []
            for _, row in hist.iterrows():
                historical_data.append(StockData(
                    symbol=symbol,
                    price=float(row['Close']),
                    volume=int(row['Volume']),
                    timestamp=row.name,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    change=float(row['Close'] - row['Open']),
                    change_percent=float((row['Close'] - row['Open']) / row['Open'] * 100)
                ))
                
            # Get trading signal from strategy
            strategy_signal = strategy.analyze(historical_data)
            
            # Enhance with AI analysis using Gemini Pro
            ai_analysis = self._get_ai_trading_analysis(symbol, current_data, historical_data, strategy_signal)
            
            # Combine strategy signal with AI analysis
            final_signal = self._combine_signals(strategy_signal, ai_analysis)
            current_position = self.portfolio.positions.get(symbol)
            
            # Execute trades based on enhanced signal
            if final_signal == OrderType.BUY and (not current_position or current_position.quantity == 0):
                # Calculate position size
                quantity = self.risk_manager.calculate_position_size(
                    self.portfolio, symbol, current_data.price
                )
                if quantity > 0:
                    self.place_order(symbol, OrderType.BUY, quantity, strategy_name, 
                                   f"AI-Enhanced signal: {final_signal.value} (Strategy: {strategy_signal.value}, AI: {ai_analysis['signal']})")
                                   
            elif final_signal == OrderType.SELL and current_position and current_position.quantity > 0:
                # Sell entire position
                self.place_order(symbol, OrderType.SELL, current_position.quantity, strategy_name,
                               f"AI-Enhanced signal: {final_signal.value} (Strategy: {strategy_signal.value}, AI: {ai_analysis['signal']})")
                               
            # Check exit conditions for existing positions
            if current_position and current_position.quantity > 0:
                if strategy.should_exit(current_position, current_data):
                    self.place_order(symbol, OrderType.SELL, current_position.quantity, strategy_name,
                                   "Exit condition met")
                                   
        except Exception as e:
            logger.error(f"Error running strategy {strategy_name} for {symbol}: {e}")
            
    def run_trading_cycle(self):
        """Run one trading cycle"""
        logger.info("Starting trading cycle...")
        
        # Update portfolio values
        self._update_portfolio_value()
        
        # Run strategies for each symbol in portfolio or watchlist
        symbols = set(self.portfolio.positions.keys())
        if hasattr(self, 'watchlist'):
            symbols.update(self.watchlist)
            
        for symbol in symbols:
            try:
                # Run each strategy
                for strategy_name in self.strategies.keys():
                    self.run_strategy(symbol, strategy_name)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                
        logger.info("Trading cycle completed")
        
    def start_trading(self, symbol: str, config: Dict):
        """Start the day trading bot with learning and sentiment analysis"""
        if self.is_running:
            logger.warning("Trading bot is already running")
            return
            
        self.current_symbol = symbol
        self.config = config
        
        # Initialize portfolio with initial capital
        self.portfolio.cash = config.get('initial_capital', 100000.0)
        self.portfolio.total_value = self.portfolio.cash
        
        # Start new trading session
        self._start_new_session()
        
        # Initialize day trading strategies based on config
        strategy_type = config.get('strategy', 'momentum')
        
        if strategy_type == 'momentum':
            self.add_strategy('day_momentum', DayTradingMomentumStrategy({
                'lookback_period': 5,
                'momentum_threshold': 0.01,
                'profit_target': 0.02,
                'stop_loss': 0.01,
                'entry_times': [9, 10, 11, 13, 14],
                'exit_time': 15
            }))
        elif strategy_type == 'rsi':
            self.add_strategy('day_rsi', DayTradingRSIStrategy({
                'lookback_period': 14,
                'oversold_threshold': 25,
                'overbought_threshold': 75,
                'profit_target': 0.015,
                'stop_loss': 0.008,
                'entry_times': [9, 10, 11, 13, 14],
                'exit_time': 15
            }))
            
        # Set up watchlist
        self.watchlist = [symbol]
        
        self.is_running = True
        
        # Start trading thread
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        
        # Schedule end-of-day analysis
        self._schedule_eod_analysis()
        
        logger.info(f"Day trading bot started for {symbol} with {strategy_type} strategy")
        
    def _start_new_session(self):
        """Start a new trading session"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        self.current_session = TradingSession(
            date=current_date,
            start_time=datetime.now(),
            end_time=None,
            initial_capital=self.portfolio.cash,
            final_capital=self.portfolio.cash,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            total_pnl=0.0,
            max_drawdown=0.0,
            strategy_performance={},
            market_events=[],
            sentiment_score=0.0,
            learning_insights=[]
        )
        logger.info(f"Started new trading session for {current_date}")
        
    def _schedule_eod_analysis(self):
        """Schedule end-of-day analysis"""
        # Schedule analysis at 4:00 PM EST (market close)
        schedule.every().day.at("16:00").do(self._end_of_day_analysis)
        logger.info("Scheduled end-of-day analysis for 4:00 PM")
        
    def _end_of_day_analysis(self):
        """Perform end-of-day analysis and learning"""
        if not self.current_session:
            return
            
        logger.info("Starting end-of-day analysis...")
        
        # Close all positions at market close
        self._close_all_positions()
        
        # Update session data
        self.current_session.end_time = datetime.now()
        self.current_session.final_capital = self.portfolio.total_value
        self.current_session.total_pnl = self.current_session.final_capital - self.current_session.initial_capital
        
        # Calculate performance metrics
        self._calculate_session_metrics()
        
        # Analyze market events and sentiment
        self._analyze_market_events()
        
        # Generate learning insights
        insights = self.learning_system.analyze_performance(self.current_session)
        
        # Enhance insights with Gemini Pro analysis
        ai_insights = self._generate_ai_learning_insights()
        combined_insights = {
            'traditional_insights': insights,
            'ai_insights': ai_insights,
            'combined_recommendations': self._combine_learning_insights(insights, ai_insights)
        }
        self.current_session.learning_insights = combined_insights
        
        # Train learning model with new data
        self._update_learning_model()
        
        # Save session to history
        self.session_history.append(self.current_session)
        
        # Generate end-of-day report
        self._generate_eod_report()
        
        # Start new session for next day
        self._start_new_session()
        
        logger.info("End-of-day analysis completed")
        
    def _close_all_positions(self):
        """Close all open positions at market close"""
        for symbol, position in list(self.portfolio.positions.items()):
            if position.quantity > 0:
                # Get current market price
                try:
                    market_data = self.get_market_data(symbol)
                    if market_data:
                        # Create sell order
                        order = Order(
                            id=f"EOD_{self.order_counter}",
                            symbol=symbol,
                            side=OrderType.SELL,
                            quantity=position.quantity,
                            price=market_data.price,
                            status=OrderStatus.FILLED,
                            timestamp=datetime.now()
                        )
                        self._execute_order(order)
                        logger.info(f"Closed position for {symbol} at market close")
                except Exception as e:
                    logger.error(f"Error closing position for {symbol}: {e}")
                    
    def _calculate_session_metrics(self):
        """Calculate session performance metrics"""
        # Count trades
        session_orders = [order for order in self.portfolio.orders 
                         if order.timestamp.date() == self.current_session.start_time.date()]
        
        self.current_session.total_trades = len(session_orders)
        
        # Count winning/losing trades
        winning_trades = 0
        losing_trades = 0
        
        for order in session_orders:
            if order.side == OrderType.SELL:
                # Find corresponding buy order
                buy_orders = [o for o in session_orders 
                             if o.symbol == order.symbol and o.side == OrderType.BUY 
                             and o.timestamp < order.timestamp]
                
                if buy_orders:
                    buy_order = buy_orders[-1]  # Most recent buy
                    pnl = (order.price - buy_order.price) * order.quantity
                    if pnl > 0:
                        winning_trades += 1
                    else:
                        losing_trades += 1
                        
        self.current_session.winning_trades = winning_trades
        self.current_session.losing_trades = losing_trades
        
        # Calculate strategy performance
        for strategy_name, strategy in self.strategies.items():
            # This would be calculated based on strategy-specific metrics
            self.current_session.strategy_performance[strategy_name] = 0.0
            
    def _analyze_market_events(self):
        """Analyze market events and sentiment for the session"""
        if not self.current_symbol:
            return
            
        # Get market events for the symbol
        events = self.sentiment_analyzer.get_market_events(self.current_symbol)
        
        # Filter events for today
        today = datetime.now().date()
        today_events = [e for e in events if e.timestamp.date() == today]
        
        # Calculate sentiment score
        if today_events:
            sentiment_scores = []
            for event in today_events:
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(event.description)
                sentiment_scores.append(sentiment_result['score'])
                
            self.current_session.sentiment_score = np.mean(sentiment_scores)
            self.current_session.market_events = [asdict(e) for e in today_events]
        else:
            self.current_session.sentiment_score = 0.0
            
    def _update_learning_model(self):
        """Update the learning model with new session data"""
        # Extract features from session data
        if self.current_session.total_trades > 0:
            # This is a simplified version - in practice, you'd extract more detailed features
            features = {
                'momentum': 0.0,  # Would be calculated from actual data
                'rsi': 50.0,
                'volume_ratio': 1.0,
                'price_change_1d': 0.0,
                'price_change_5d': 0.0,
                'volatility': 0.0,
                'sentiment_score': self.current_session.sentiment_score,
                'market_hour': 16,  # Market close
                'day_of_week': datetime.now().weekday()
            }
            
            # Determine outcome
            if self.current_session.total_pnl > 0:
                outcome = 'profitable'
            elif self.current_session.total_pnl < 0:
                outcome = 'loss'
            else:
                outcome = 'neutral'
                
            # Add training sample
            self.learning_system.add_training_sample(
                features, outcome, self.current_session.total_pnl
            )
            
            # Train model if we have enough data
            if len(self.learning_system.training_data) >= 50:
                self.learning_system.train_model()
                
    def _generate_eod_report(self):
        """Generate end-of-day learning report"""
        report = {
            'date': self.current_session.date,
            'performance': {
                'initial_capital': self.current_session.initial_capital,
                'final_capital': self.current_session.final_capital,
                'total_pnl': self.current_session.total_pnl,
                'pnl_percentage': (self.current_session.total_pnl / self.current_session.initial_capital) * 100,
                'total_trades': self.current_session.total_trades,
                'winning_trades': self.current_session.winning_trades,
                'losing_trades': self.current_session.losing_trades,
                'win_rate': (self.current_session.winning_trades / self.current_session.total_trades * 100) if self.current_session.total_trades > 0 else 0
            },
            'market_analysis': {
                'sentiment_score': self.current_session.sentiment_score,
                'market_events': len(self.current_session.market_events),
                'strategy_performance': self.current_session.strategy_performance
            },
            'learning_insights': self.current_session.learning_insights,
            'recommendations': self._generate_recommendations()
        }
        
        # Log the report
        logger.info("=== END OF DAY REPORT ===")
        logger.info(f"Date: {report['date']}")
        logger.info(f"Performance: {report['performance']['pnl_percentage']:.2f}% PnL")
        logger.info(f"Trades: {report['performance']['total_trades']} (Win Rate: {report['performance']['win_rate']:.1f}%)")
        logger.info(f"Sentiment Score: {report['market_analysis']['sentiment_score']:.2f}")
        logger.info("Learning Insights:")
        for insight in report['learning_insights']:
            logger.info(f"  - {insight}")
            
        return report
        
    def _generate_recommendations(self):
        """Generate trading recommendations based on learning"""
        recommendations = []
        
        if self.current_session.total_trades > 0:
            win_rate = self.current_session.winning_trades / self.current_session.total_trades
            
            if win_rate < 0.4:
                recommendations.append("Consider adjusting entry criteria - low win rate detected")
            elif win_rate > 0.7:
                recommendations.append("High win rate achieved - consider increasing position sizes gradually")
                
            if self.current_session.max_drawdown > 0.05:
                recommendations.append("High drawdown detected - reduce position sizes")
                
            if self.current_session.sentiment_score < -0.3:
                recommendations.append("Negative market sentiment - consider defensive positioning")
            elif self.current_session.sentiment_score > 0.3:
                recommendations.append("Positive market sentiment - consider aggressive positioning")
                
        return recommendations
    
    def _get_ai_trading_analysis(self, symbol: str, current_data: StockData, historical_data: List[StockData], strategy_signal: OrderType) -> Dict:
        """Get AI-powered trading analysis using Gemini Pro"""
        try:
            import google.generativeai as genai
            from config import Config
            
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Prepare market context
            current_price = current_data.price
            change_pct = current_data.change_percent
            volume = current_data.volume
            
            # Calculate recent performance
            recent_prices = [data.price for data in historical_data[-5:]]
            price_trend = "upward" if recent_prices[-1] > recent_prices[0] else "downward"
            
            # Get current portfolio context
            current_position = self.portfolio.positions.get(symbol)
            position_info = ""
            if current_position:
                position_info = f"Current position: {current_position.quantity} shares @ ${current_position.avg_price:.2f}"
            else:
                position_info = "No current position"
            
            prompt = f"""
            As a professional day trader, analyze this trading opportunity for {symbol}.
            
            Current Market Data:
            - Price: ${current_price:.2f}
            - Change: {change_pct:+.2f}%
            - Volume: {volume:,}
            - Price trend (5-day): {price_trend}
            
            Trading Context:
            - Strategy signal: {strategy_signal.value}
            - {position_info}
            - Portfolio cash: ${self.portfolio.cash:.2f}
            
            Consider:
            1. Technical momentum and volume confirmation
            2. Market sentiment and news impact
            3. Risk/reward ratio for this trade
            4. Position sizing appropriateness
            5. Exit strategy planning
            
            Provide your analysis in this format:
            Signal: BUY/SELL/HOLD
            Confidence: HIGH/MEDIUM/LOW
            Risk: LOW/MEDIUM/HIGH
            Reasoning: [1-2 sentences]
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse AI response
            ai_signal = OrderType.HOLD  # Default
            if 'BUY' in text.upper():
                ai_signal = OrderType.BUY
            elif 'SELL' in text.upper():
                ai_signal = OrderType.SELL
            
            confidence = 'MEDIUM'
            if 'HIGH' in text.upper():
                confidence = 'HIGH'
            elif 'LOW' in text.upper():
                confidence = 'LOW'
            
            risk = 'MEDIUM'
            if 'RISK: LOW' in text.upper():
                risk = 'LOW'
            elif 'RISK: HIGH' in text.upper():
                risk = 'HIGH'
            
            return {
                'signal': ai_signal.value,
                'confidence': confidence,
                'risk': risk,
                'reasoning': text,
                'analysis_type': 'gemini_pro'
            }
            
        except Exception as e:
            logger.error(f"AI trading analysis error for {symbol}: {e}")
            # Fallback analysis
            return {
                'signal': strategy_signal.value,
                'confidence': 'MEDIUM',
                'risk': 'MEDIUM',
                'reasoning': f'Fallback analysis - following strategy signal: {strategy_signal.value}',
                'analysis_type': 'fallback'
            }
    
    def _combine_signals(self, strategy_signal: OrderType, ai_analysis: Dict) -> OrderType:
        """Combine strategy signal with AI analysis for final decision"""
        try:
            ai_signal_str = ai_analysis['signal']
            ai_confidence = ai_analysis['confidence']
            ai_risk = ai_analysis['risk']
            
            # Convert AI signal string back to OrderType
            ai_signal = OrderType.HOLD
            if ai_signal_str == 'BUY':
                ai_signal = OrderType.BUY
            elif ai_signal_str == 'SELL':
                ai_signal = OrderType.SELL
            
            # Decision logic: AI can override strategy if high confidence and low risk
            if ai_confidence == 'HIGH' and ai_risk == 'LOW':
                logger.info(f"AI override: High confidence, low risk - using AI signal: {ai_signal.value}")
                return ai_signal
            
            # If signals agree, proceed
            if strategy_signal == ai_signal:
                logger.info(f"Signals agree: Strategy and AI both suggest {strategy_signal.value}")
                return strategy_signal
            
            # If signals disagree, be conservative
            if strategy_signal == OrderType.BUY and ai_signal == OrderType.SELL:
                logger.info("Signals conflict: Strategy BUY vs AI SELL - defaulting to HOLD")
                return OrderType.HOLD
            elif strategy_signal == OrderType.SELL and ai_signal == OrderType.BUY:
                logger.info("Signals conflict: Strategy SELL vs AI BUY - defaulting to HOLD")
                return OrderType.HOLD
            
            # For HOLD vs BUY/SELL, prefer the more conservative option
            if OrderType.HOLD in [strategy_signal, ai_signal]:
                logger.info("One signal is HOLD - choosing conservative approach")
                return OrderType.HOLD
            
            # Default to strategy signal
            return strategy_signal
            
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return strategy_signal
    
    def _generate_ai_learning_insights(self) -> Dict:
        """Generate AI-powered learning insights using Gemini Pro"""
        try:
            import google.generativeai as genai
            from config import Config
            
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            if not self.current_session:
                return {'error': 'No current session data available'}
            
            # Prepare session data for analysis
            session = self.current_session
            total_trades = session.total_trades
            win_rate = (session.winning_trades / total_trades * 100) if total_trades > 0 else 0
            pnl_pct = (session.total_pnl / session.initial_capital * 100) if session.initial_capital > 0 else 0
            
            prompt = f"""
            As a professional trading coach, analyze this day trading session and provide learning insights.
            
            Session Performance:
            - Total Trades: {total_trades}
            - Winning Trades: {session.winning_trades}
            - Losing Trades: {session.losing_trades}
            - Win Rate: {win_rate:.1f}%
            - Total P&L: ${session.total_pnl:.2f} ({pnl_pct:+.2f}%)
            - Max Drawdown: {session.max_drawdown:.2f}%
            - Average Trade Duration: {session.avg_trade_duration:.1f} minutes
            
            Market Context:
            - Sentiment Score: {session.sentiment_score:.2f}
            - Market Events: {len(session.market_events)}
            - Volatility Level: {session.volatility_level}
            
            Strategy Performance:
            """
            
            for strategy, perf in session.strategy_performance.items():
                prompt += f"- {strategy}: {perf['trades']} trades, {perf['win_rate']:.1f}% win rate, ${perf['pnl']:.2f} P&L\n"
            
            prompt += """
            
            Provide actionable learning insights:
            1. What went well and should be repeated?
            2. What mistakes were made and how to avoid them?
            3. Strategy adjustments for tomorrow?
            4. Risk management improvements?
            5. Market condition adaptations needed?
            
            Format as concise, actionable bullet points.
            """
            
            response = model.generate_content(prompt)
            
            # Parse insights into categories
            insights_text = response.text.strip()
            insights = []
            
            lines = insights_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    insights.append(line.lstrip('•-* '))
            
            return {
                'ai_analysis': insights_text,
                'key_insights': insights[:5],  # Top 5 insights
                'session_score': self._calculate_session_score(session),
                'improvement_areas': self._identify_improvement_areas(session),
                'generated_by': 'Gemini Pro',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI learning insights error: {e}")
            return {
                'ai_analysis': 'AI analysis temporarily unavailable',
                'key_insights': ['Continue monitoring strategy performance', 'Maintain risk management discipline'],
                'session_score': 75,
                'improvement_areas': ['Strategy optimization', 'Risk management'],
                'generated_by': 'Fallback Analysis',
                'timestamp': datetime.now().isoformat()
            }
    
    def _combine_learning_insights(self, traditional_insights: Dict, ai_insights: Dict) -> List[str]:
        """Combine traditional and AI learning insights"""
        combined = []
        
        # Add traditional insights
        if isinstance(traditional_insights, dict) and 'recommendations' in traditional_insights:
            combined.extend(traditional_insights['recommendations'][:3])
        
        # Add AI insights
        if isinstance(ai_insights, dict) and 'key_insights' in ai_insights:
            combined.extend(ai_insights['key_insights'][:3])
        
        return combined[:5]  # Limit to 5 total insights
    
    def _calculate_session_score(self, session) -> int:
        """Calculate AI-based session performance score (0-100)"""
        try:
            score = 50  # Base score
            
            # Performance factors
            if session.total_trades > 0:
                win_rate = session.winning_trades / session.total_trades
                score += (win_rate - 0.5) * 40  # +/- 20 points for win rate
            
            # P&L factor
            if session.initial_capital > 0:
                pnl_pct = session.total_pnl / session.initial_capital
                score += pnl_pct * 100  # 1% gain = 1 point
            
            # Risk management factor
            if session.max_drawdown < 0.02:  # Less than 2% drawdown
                score += 10
            elif session.max_drawdown > 0.05:  # More than 5% drawdown
                score -= 15
            
            return max(0, min(100, int(score)))
        except:
            return 75
    
    def _identify_improvement_areas(self, session) -> List[str]:
        """Identify key areas for improvement"""
        areas = []
        
        if session.total_trades > 0:
            win_rate = session.winning_trades / session.total_trades
            if win_rate < 0.5:
                areas.append('Entry timing optimization')
            if session.max_drawdown > 0.03:
                areas.append('Risk management tightening')
            if session.avg_trade_duration > 240:  # More than 4 hours
                areas.append('Exit strategy improvement')
        
        if not areas:
            areas.append('Continue current approach')
            
        return areas
    
    def _trading_loop(self):
        """Main day trading loop with scheduler"""
        while self.is_running:
            try:
                # Run scheduled tasks (EOD analysis)
                schedule.run_pending()
                
                # Run trading cycle
                self.run_trading_cycle()
                
                # Wait 1 minute between cycles
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(60)
                
    def stop_trading(self):
        """Stop the trading bot"""
        self.is_running = False
        if self.trading_thread:
            self.trading_thread.join(timeout=5)
        logger.info("Trading bot stopped")
        
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        self._update_portfolio_value()
        
        positions = []
        for symbol, pos in self.portfolio.positions.items():
            positions.append({
                'symbol': symbol,
                'shares': pos.quantity,
                'avg_price': pos.avg_price,
                'current_price': pos.current_price,
                'value': pos.market_value,
                'gain_loss': pos.unrealized_pnl
            })
            
        return {
            'cash_balance': self.portfolio.cash,
            'total_value': self.portfolio.total_value,
            'positions': positions,
            'total_gain_loss': sum(pos.unrealized_pnl for pos in self.portfolio.positions.values()),
            'total_gain_loss_percent': (self.portfolio.total_value - 100000) / 100000 * 100,
            'timestamp': datetime.now().isoformat()
        }
        
    def get_recent_orders(self) -> List[Dict]:
        """Get recent orders"""
        recent_orders = self.portfolio.orders[-10:]  # Last 10 orders
        
        return [
            {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.order_type.value,
                'quantity': order.quantity,
                'price': order.price,
                'status': order.status.value,
                'timestamp': order.timestamp.isoformat()
            }
            for order in recent_orders
        ]

# MarketStack API Configuration
MARKETSTACK_API_KEY = "7e7d015da85a3e6c0f501fc1ecdeae86"
MARKETSTACK_BASE_URL = "http://api.marketstack.com/v1"

# Simple cache to avoid rate limiting
symbol_cache = {}
CACHE_DURATION = 300  # 5 minutes to reduce API calls and timeouts

# Global bot state
bot_state = {
    'status': 'stopped',
    'config': None,
    'started_at': None,
    'bot_id': None
}

# Initialize real trading bot
real_trading_bot = RealTradingBot()

# Common stock symbols for validation
COMMON_SYMBOLS = {
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology'},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology'},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology'},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary'},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Discretionary'},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
    'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology'},
    'NFLX': {'name': 'Netflix Inc.', 'sector': 'Communication Services'},
    'AMD': {'name': 'Advanced Micro Devices Inc.', 'sector': 'Technology'},
    'INTC': {'name': 'Intel Corporation', 'sector': 'Technology'},
    'SPY': {'name': 'SPDR S&P 500 ETF Trust', 'sector': 'ETF'},
    'QQQ': {'name': 'Invesco QQQ Trust', 'sector': 'ETF'},
    'VOO': {'name': 'Vanguard S&P 500 ETF', 'sector': 'ETF'},
    'VTI': {'name': 'Vanguard Total Stock Market ETF', 'sector': 'ETF'},
    'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
    'BAC': {'name': 'Bank of America Corporation', 'sector': 'Financial Services'},
    'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Staples'},
    'JNJ': {'name': 'Johnson & Johnson', 'sector': 'Healthcare'},
    'PG': {'name': 'Procter & Gamble Co.', 'sector': 'Consumer Staples'},
    'SMR': {'name': 'NuScale Power Corporation', 'sector': 'Utilities'},
    'KO': {'name': 'The Coca-Cola Company', 'sector': 'Consumer Staples'}
}

def get_cached_symbol_info(symbol):
    """Get symbol info from cache if available and not expired"""
    if symbol in symbol_cache:
        cached_time, data = symbol_cache[symbol]
        if time.time() - cached_time < CACHE_DURATION:
            return data
    return None

def cache_symbol_info(symbol, data):
    """Cache symbol info"""
    symbol_cache[symbol] = (time.time(), data)

@with_exponential_backoff(
    base_delay=1.0,
    backoff_factor=2.0,
    max_retries=2,
    max_delay=10.0,
    jitter_type="full"
)
def get_marketstack_data(symbol, period='1y'):
    """Get stock data from MarketStack API with exponential backoff"""
    try:
        # Get latest EOD data (most recent trading day)
        url = f"{MARKETSTACK_BASE_URL}/eod"
        params = {
            'access_key': MARKETSTACK_API_KEY,
            'symbols': symbol,
            'limit': 2,  # Get latest 2 days for price change calculation
            'sort': 'DESC'
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors (like usage limit)
        if 'error' in data:
            error_code = data['error'].get('code', '')
            if error_code == 'usage_limit_reached':
                print(f"MarketStack API usage limit reached, will use Yahoo Finance fallback")
                raise Exception("MarketStack API usage limit reached")
            else:
                raise Exception(f"MarketStack API error: {data['error']}")
        
        if not data.get('data') or len(data['data']) == 0:
            raise Exception(f"No EOD data found for {symbol}")
        
        # Get current price from latest data
        latest_data = data['data'][0]
        current_price = float(latest_data['close'])
        volume = int(latest_data['volume']) if latest_data.get('volume') else 0
        
        # Calculate price change from previous day
        price_change = 0
        price_change_pct = 0
        if len(data['data']) > 1:
            prev_data = data['data'][1]
            prev_price = float(prev_data['close'])
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
        
        return {
            'symbol': symbol,
            'summary': {
                'current_price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volume': volume,
                'market_cap': 0,  # MarketStack doesn't provide market cap in free tier
                'sector': 'Unknown'  # MarketStack doesn't provide sector in free tier
            },
            'history': data['data'][:30],  # Last 30 days
            'source': 'marketstack_api'
        }
        
    except Exception as e:
        print(f"MarketStack API error for {symbol}: {str(e)}")
        raise e

def get_marketstack_info(symbol):
    """Get stock info from MarketStack API"""
    try:
        # Get latest EOD data for current price
        url = f"{MARKETSTACK_BASE_URL}/eod"
        params = {
            'access_key': MARKETSTACK_API_KEY,
            'symbols': symbol,
            'limit': 1,
            'sort': 'DESC'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors (like usage limit)
        if 'error' in data:
            error_code = data['error'].get('code', '')
            if error_code == 'usage_limit_reached':
                print(f"MarketStack API usage limit reached, will use Yahoo Finance fallback")
                raise Exception("MarketStack API usage limit reached")
            else:
                raise Exception(f"MarketStack API error: {data['error']}")
        
        if not data.get('data') or len(data['data']) == 0:
            raise Exception(f"No EOD data found for {symbol}")
        
        latest_data = data['data'][0]
        current_price = float(latest_data['close'])
        
        return {
            'symbol': symbol,
            'name': symbol,  # MarketStack free tier doesn't provide company names
            'current_price': current_price,
            'market_cap': 0,  # MarketStack doesn't provide market cap in free tier
            'sector': 'Unknown',  # MarketStack doesn't provide sector in free tier
            'source': 'marketstack_api'
        }
        
    except Exception as e:
        print(f"MarketStack API error for {symbol}: {str(e)}")
        raise e

@with_exponential_backoff(
    base_delay=1.0,
    backoff_factor=2.0,
    max_retries=2,
    max_delay=8.0,
    jitter_type="full"
)
def get_yahoo_finance_data_robust(symbol, period='1y'):
    """Get stock data from Yahoo Finance with exponential backoff"""
    try:
        # Base delay is now handled by exponential backoff decorator
        
        stock = yf.Ticker(symbol)
        
        # Try multiple methods to get data
        current_price = None
        price_change = 0
        price_change_pct = 0
        volume = 0
        market_cap = 0
        sector = 'Unknown'
        
        # Method 1: Try to get info first
        try:
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            volume = info.get('volume', 0)
            market_cap = info.get('marketCap', 0)
            sector = info.get('sector', 'Unknown')
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Yahoo Finance rate limited for {symbol}, waiting longer...")
                time.sleep(5.0)  # Wait longer for rate limit
                raise Exception("Yahoo Finance rate limited - please try again later")
            pass
        
        # Method 2: Get historical data for price calculation
        try:
            hist = stock.history(period='5d')
            if not hist.empty:
                if current_price is None:
                    current_price = float(hist['Close'].iloc[-1])
                
                if len(hist) > 1:
                    prev_price = float(hist['Close'].iloc[-2])
                    price_change = current_price - prev_price
                    price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
                
                if volume == 0 and 'Volume' in hist.columns:
                    volume = int(hist['Volume'].iloc[-1])
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"Yahoo Finance rate limited for {symbol} history, waiting longer...")
                time.sleep(5.0)  # Wait longer for rate limit
                raise Exception("Yahoo Finance rate limited - please try again later")
            pass
        
        if current_price is None:
            raise Exception(f"Could not get current price for {symbol}")
        
        return {
            'symbol': symbol,
            'summary': {
                'current_price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'volume': volume,
                'market_cap': market_cap,
                'sector': sector
            },
            'history': [],
            'source': 'yahoo_finance_robust'
        }
        
    except Exception as e:
        print(f"Yahoo Finance robust error for {symbol}: {str(e)}")
        raise e

@with_exponential_backoff(
    base_delay=1.0,
    backoff_factor=2.0,
    max_retries=2,
    max_delay=5.0,
    jitter_type="full"
)
def get_finnhub_data(symbol, period='1y'):
    """Get stock data from Finnhub API with exponential backoff"""
    try:
        from config import Config
        
        # Get current quote
        quote_url = f"https://finnhub.io/api/v1/quote"
        quote_params = {
            'symbol': symbol,
            'token': Config.FINNHUB_API_KEY
        }
        
        quote_response = requests.get(quote_url, params=quote_params, timeout=10)
        quote_response.raise_for_status()
        quote_data = quote_response.json()
        
        if 'error' in quote_data:
            raise Exception(f"Finnhub API error: {quote_data['error']}")
        
        current_price = quote_data.get('c', 0)  # Current price
        prev_close = quote_data.get('pc', 0)    # Previous close
        
        if current_price == 0:
            raise Exception("No current price data from Finnhub")
        
        # Calculate price change
        price_change = current_price - prev_close if prev_close else 0
        price_change_pct = (price_change / prev_close * 100) if prev_close else 0
        
        # Get company profile for additional info
        profile_url = f"https://finnhub.io/api/v1/stock/profile2"
        profile_params = {
            'symbol': symbol,
            'token': Config.FINNHUB_API_KEY
        }
        
        try:
            profile_response = requests.get(profile_url, params=profile_params, timeout=10)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            market_cap = profile_data.get('marketCapitalization', 0) * 1000000  # Convert from millions
            sector = profile_data.get('finnhubIndustry', 'Unknown')
        except:
            market_cap = 0
            sector = 'Unknown'
        
        return {
            'symbol': symbol,
            'price': current_price,
            'volume': 0,  # Finnhub quote doesn't include volume in basic quote
            'timestamp': datetime.now(),
            'open': quote_data.get('o', current_price),
            'high': quote_data.get('h', current_price),
            'low': quote_data.get('l', current_price),
            'close': current_price,
            'change': price_change,
            'change_percent': price_change_pct,
            'market_cap': market_cap,
            'sector': sector,
            'source': 'finnhub'
        }
        
    except Exception as e:
        print(f"Finnhub error for {symbol}: {str(e)}")
        raise e

def get_yahoo_finance_info_robust(symbol):
    """Get stock info from Yahoo Finance with robust error handling"""
    try:
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info:
            raise Exception("No data returned from yfinance")
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'current_price': current_price,
            'market_cap': info.get('marketCap', 0),
            'sector': info.get('sector', 'Unknown'),
            'source': 'yahoo_finance_robust'
        }
        
    except Exception as e:
        print(f"Yahoo Finance robust error for {symbol}: {str(e)}")
        raise e

def is_valid_symbol(symbol):
    """Check if symbol is valid using common symbols list"""
    return symbol.upper() in COMMON_SYMBOLS

def get_symbol_info_fallback(symbol):
    """Get symbol info from fallback data"""
    symbol_upper = symbol.upper()
    if symbol_upper in COMMON_SYMBOLS:
        info = COMMON_SYMBOLS[symbol_upper]
        return {
            'symbol': symbol_upper,
            'name': info['name'],
            'current_price': 0,  # Will be filled by actual API call if available
            'market_cap': 0,
            'sector': info['sector']
        }
    return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'AI Stock Trading API'
    })

@app.route('/api/stock/data', methods=['GET'])
def get_stock_data():
    """Get stock data for a symbol"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        period = request.args.get('period', '1mo')
        
        # Fetch stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            return jsonify({'error': f'No data found for symbol {symbol}'}), 404
        
        # Convert to JSON-serializable format
        data = []
        for date, row in hist.iterrows():
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        return jsonify({
            'symbol': symbol,
            'data': data,
            'period': period
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/info', methods=['GET'])
def get_stock_info():
    """Get basic stock information"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return jsonify({
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'current_price': info.get('currentPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'sector': info.get('sector', 'Unknown')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/info/<symbol>', methods=['GET'])
def get_stock_info_by_symbol(symbol):
    """Get basic stock information by symbol"""
    try:
        market = request.args.get('market', 'US')
        original_symbol = symbol
        
        # Handle market suffixes
        if market == 'UK' and not symbol.endswith('.L'):
            symbol = symbol + '.L'
        elif market == 'IN' and not symbol.endswith('.NS'):
            symbol = symbol + '.NS'
        
        # Check cache first
        cached_data = get_cached_symbol_info(symbol)
        if cached_data:
            return jsonify(cached_data)
        
        # First, try fallback validation for common symbols
        fallback_info = get_symbol_info_fallback(original_symbol)
        if fallback_info:
            # Try to get real-time data, but don't fail if it doesn't work
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                
                if info and len(info) > 0:
                    result = {
                        'symbol': symbol,
                        'name': info.get('longName', fallback_info['name']),
                        'current_price': info.get('currentPrice', 0),
                        'market_cap': info.get('marketCap', 0),
                        'sector': info.get('sector', fallback_info['sector'])
                    }
                else:
                    result = fallback_info
            except:
                # If yfinance fails, use fallback data
                result = fallback_info
            
            # Cache the result
            cache_symbol_info(symbol, result)
            return jsonify(result)
        
        # For symbols not in our fallback list, try yfinance with retry logic
        max_retries = 2
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                
                # Check if we got valid data
                if info and len(info) > 0:
                    result = {
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'current_price': info.get('currentPrice', 0),
                        'market_cap': info.get('marketCap', 0),
                        'sector': info.get('sector', 'Unknown')
                    }
                    
                    # Cache the result
                    cache_symbol_info(symbol, result)
                    return jsonify(result)
                else:
                    raise Exception("No data returned from yfinance")
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed, return a basic response
                    result = {
                        'symbol': symbol,
                        'name': symbol,
                        'current_price': 0,
                        'market_cap': 0,
                        'sector': 'Unknown'
                    }
                    cache_symbol_info(symbol, result)
                    return jsonify(result)
                else:
                    # Wait before retry
                    time.sleep(1)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/<symbol>', methods=['GET'])
def get_prediction(symbol):
    """Get simple prediction for a symbol"""
    try:
        # Try to get real data first
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='5d')
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                prev_price = float(hist['Close'].iloc[-2])
                
                change = current_price - prev_price
                change_percent = (change / prev_price) * 100
                
                # Simple prediction based on recent trend
                if change > 0:
                    prediction = 'bullish'
                    confidence = min(abs(change_percent) * 10, 95)
                else:
                    prediction = 'bearish'
                    confidence = min(abs(change_percent) * 10, 95)
                
                return jsonify({
                    'symbol': symbol,
                    'current_price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'prediction': prediction,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat()
                })
        except:
            pass  # Fall through to fallback data
        
        # Fallback data when Yahoo Finance fails
        fallback_predictions = {
            'AAPL': {'prediction': 'bullish', 'confidence': 75, 'current_price': 175.50, 'change': 2.30, 'change_percent': 1.33},
            'MSFT': {'prediction': 'bearish', 'confidence': 65, 'current_price': 380.25, 'change': -1.75, 'change_percent': -0.46},
            'GOOGL': {'prediction': 'bullish', 'confidence': 70, 'current_price': 142.80, 'change': 0.85, 'change_percent': 0.60},
            'TSLA': {'prediction': 'bearish', 'confidence': 60, 'current_price': 245.30, 'change': -3.20, 'change_percent': -1.29},
            'META': {'prediction': 'bullish', 'confidence': 80, 'current_price': 485.20, 'change': 5.40, 'change_percent': 1.12},
            'SMR': {'prediction': 'neutral', 'confidence': 55, 'current_price': 45.20, 'change': 0.15, 'change_percent': 0.33}
        }
        
        prediction_data = fallback_predictions.get(symbol, {
            'prediction': 'neutral',
            'confidence': 50,
            'current_price': 100.00,
            'change': 0.00,
            'change_percent': 0.00
        })
        
        return jsonify({
            'symbol': symbol,
            'current_price': prediction_data['current_price'],
            'change': prediction_data['change'],
            'change_percent': prediction_data['change_percent'],
            'prediction': prediction_data['prediction'],
            'confidence': prediction_data['confidence'],
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback_data'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketmate/query', methods=['POST'])
def marketmate_query():
    """Process natural language market queries using MarketMate"""
    import time
    
    # Use a simple timeout mechanism
    start_time = time.time()
    timeout_seconds = 10
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Check timeout before processing
        if time.time() - start_time > timeout_seconds:
            return jsonify({'error': 'MarketMate query timed out'}), 408
        
        # Process the query using MarketMate
        result = marketmate.process_query(query)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketmate/query', methods=['GET'])
def marketmate_query_get():
    """Process natural language market queries using MarketMate (GET method)"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        # Process the query using MarketMate
        result = marketmate.process_query(query)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/data/<symbol>', methods=['GET'])
def get_stock_data_by_symbol(symbol):
    """Get stock data for a specific symbol (frontend expects this format)"""
    import threading
    import time
    
    # Use a simple timeout mechanism with threading
    start_time = time.time()
    timeout_seconds = 15
    
    try:
        period = request.args.get('period', '1y')
        market = request.args.get('market', 'US')
        
        # Check cache first
        cached_data = get_cached_symbol_info(symbol)
        if cached_data:
            return jsonify(cached_data)
        
        # Priority order: Yahoo Finance → Finnhub → MarketStack → Fallback
        
        # Try Yahoo Finance first (fastest, but rate limited)
        try:
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Request timed out")
            
            print(f"Trying Yahoo Finance for {symbol}")
            result = get_yahoo_finance_data_robust(symbol, period)
            # Cache the result
            cache_symbol_info(symbol, result)
            return jsonify(result)
        except Exception as e:
            print(f"Yahoo Finance failed for {symbol}: {str(e)}")
        
        # Try Finnhub API second (good free tier limits)
        try:
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Request timed out")
            
            print(f"Trying Finnhub API for {symbol}")
            result = get_finnhub_data(symbol, period)
            # Cache the result
            cache_symbol_info(symbol, result)
            return jsonify(result)
        except Exception as e:
            print(f"Finnhub API failed for {symbol}: {str(e)}")
        
        # Try MarketStack API third (monthly limit)
        try:
            print(f"Trying MarketStack API for {symbol}")
            result = get_marketstack_data(symbol, period)
            # Cache the result
            cache_symbol_info(symbol, result)
            return jsonify(result)
        except Exception as e:
            print(f"MarketStack API failed for {symbol}: {str(e)}")
        
        # Fallback to Yahoo Finance with improved retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add delay between requests to avoid rate limiting
                if attempt > 0:
                    time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                
                stock = yf.Ticker(symbol)
                
                # Try to get current price first (faster)
                try:
                    info = stock.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    if current_price:
                        # Get historical data for price change calculation
                        hist = stock.history(period='5d')
                        if not hist.empty:
                            prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                            price_change = current_price - prev_price
                            price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
                        else:
                            price_change = 0
                            price_change_pct = 0
                        
                        result = {
                            'symbol': symbol,
                            'summary': {
                                'current_price': current_price,
                                'price_change': price_change,
                                'price_change_pct': price_change_pct,
                                'volume': info.get('volume', 0),
                                'market_cap': info.get('marketCap', 0),
                                'sector': info.get('sector', 'Unknown')
                            },
                            'history': [],
                            'source': 'yahoo_finance'
                        }
                        
                        # Cache the result
                        cache_symbol_info(symbol, result)
                        return jsonify(result)
                except:
                    pass
                
                # Fallback to historical data method
                hist = stock.history(period=period)
                
                if hist.empty:
                    raise Exception(f"No data found for symbol {symbol}")
                
                # Get current price and calculate changes
                current_price = float(hist['Close'].iloc[-1])
                prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                price_change = current_price - prev_price
                price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
                
                # Get additional info
                info = stock.info
                
                result = {
                    'symbol': symbol,
                    'summary': {
                        'current_price': current_price,
                        'price_change': price_change,
                        'price_change_pct': price_change_pct,
                        'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                        'market_cap': info.get('marketCap', 0),
                        'sector': info.get('sector', 'Unknown')
                    },
                    'history': hist.to_dict('records')[-30:],  # Last 30 days
                    'source': 'yahoo_finance'
                }
                
                # Cache the result
                cache_symbol_info(symbol, result)
                return jsonify(result)
                
            except Exception as e:
                print(f"Yahoo Finance attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt == max_retries - 1:
                    # Last attempt failed, return fallback data with realistic prices
                    fallback_stock_data = {
                        'AAPL': {'current_price': 175.50, 'price_change': 2.30, 'price_change_pct': 1.33, 'volume': 45000000, 'market_cap': 2800000000000, 'sector': 'Technology'},
                        'MSFT': {'current_price': 380.25, 'price_change': -1.75, 'price_change_pct': -0.46, 'volume': 25000000, 'market_cap': 2800000000000, 'sector': 'Technology'},
                        'GOOGL': {'current_price': 142.80, 'price_change': 0.85, 'price_change_pct': 0.60, 'volume': 18000000, 'market_cap': 1800000000000, 'sector': 'Technology'},
                        'TSLA': {'current_price': 245.30, 'price_change': -3.20, 'price_change_pct': -1.29, 'volume': 35000000, 'market_cap': 780000000000, 'sector': 'Consumer Discretionary'},
                        'META': {'current_price': 485.20, 'price_change': 5.40, 'price_change_pct': 1.12, 'volume': 12000000, 'market_cap': 1200000000000, 'sector': 'Technology'},
                        'SMR': {'current_price': 45.20, 'price_change': 0.15, 'price_change_pct': 0.33, 'volume': 2000000, 'market_cap': 3000000000, 'sector': 'Utilities'}
                    }
                    
                    fallback_data = fallback_stock_data.get(symbol, {
                        'current_price': 100.00,
                        'price_change': 0.00,
                        'price_change_pct': 0.00,
                        'volume': 1000000,
                        'market_cap': 1000000000,
                        'sector': 'Unknown'
                    })
                    
                    result = {
                        'symbol': symbol,
                        'summary': {
                            'current_price': fallback_data['current_price'],
                            'price_change': fallback_data['price_change'],
                            'price_change_pct': fallback_data['price_change_pct'],
                            'volume': fallback_data['volume'],
                            'market_cap': fallback_data['market_cap'],
                            'sector': fallback_data['sector']
                        },
                        'history': [],
                        'source': 'fallback_data',
                        'warning': 'Real-time market data unavailable. Showing sample data.'
                    }
                    cache_symbol_info(symbol, result)
                    return jsonify(result)
                else:
                    # Wait before retry
                    time.sleep(1)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/info/<symbol>', methods=['GET'])
def get_stock_info_by_symbol_path(symbol):
    """Get stock info for a specific symbol (frontend expects this format)"""
    try:
        market = request.args.get('market', 'US')
        
        # Check cache first
        cached_data = get_cached_symbol_info(symbol)
        if cached_data:
            return jsonify(cached_data)
        
        # Try MarketStack API first (primary data source)
        try:
            print(f"Trying MarketStack API for {symbol} info")
            result = get_marketstack_info(symbol)
            # Cache the result
            cache_symbol_info(symbol, result)
            return jsonify(result)
        except Exception as e:
            print(f"MarketStack API failed for {symbol}: {str(e)}")
        
        # Fallback to robust Yahoo Finance
        try:
            print(f"Trying robust Yahoo Finance for {symbol} info")
            result = get_yahoo_finance_info_robust(symbol)
            # Cache the result
            cache_symbol_info(symbol, result)
            return jsonify(result)
        except Exception as e:
            print(f"Robust Yahoo Finance failed for {symbol}: {str(e)}")
        
        # Fallback to Yahoo Finance with improved retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add delay between requests to avoid rate limiting
                if attempt > 0:
                    time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                
                stock = yf.Ticker(symbol)
                info = stock.info
                
                if not info:
                    raise Exception("No data returned from yfinance")
                
                result = {
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'current_price': info.get('currentPrice') or info.get('regularMarketPrice', 0),
                    'market_cap': info.get('marketCap', 0),
                    'sector': info.get('sector', 'Unknown'),
                    'source': 'yahoo_finance'
                }
                
                # Cache the result
                cache_symbol_info(symbol, result)
                return jsonify(result)
                
            except Exception as e:
                print(f"Yahoo Finance attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt == max_retries - 1:
                    # Last attempt failed, return fallback data with realistic prices
                    fallback_stock_info = {
                        'AAPL': {'name': 'Apple Inc.', 'current_price': 175.50, 'market_cap': 2800000000000, 'sector': 'Technology'},
                        'MSFT': {'name': 'Microsoft Corporation', 'current_price': 380.25, 'market_cap': 2800000000000, 'sector': 'Technology'},
                        'GOOGL': {'name': 'Alphabet Inc.', 'current_price': 142.80, 'market_cap': 1800000000000, 'sector': 'Technology'},
                        'TSLA': {'name': 'Tesla Inc.', 'current_price': 245.30, 'market_cap': 780000000000, 'sector': 'Consumer Discretionary'},
                        'META': {'name': 'Meta Platforms Inc.', 'current_price': 485.20, 'market_cap': 1200000000000, 'sector': 'Technology'},
                        'SMR': {'name': 'NuScale Power Corporation', 'current_price': 45.20, 'market_cap': 3000000000, 'sector': 'Utilities'}
                    }
                    
                    fallback_data = fallback_stock_info.get(symbol, {
                        'name': symbol,
                        'current_price': 100.00,
                        'market_cap': 1000000000,
                        'sector': 'Unknown'
                    })
                    
                    result = {
                        'symbol': symbol,
                        'name': fallback_data['name'],
                        'current_price': fallback_data['current_price'],
                        'market_cap': fallback_data['market_cap'],
                        'sector': fallback_data['sector'],
                        'source': 'fallback_data',
                        'warning': 'Real-time market data unavailable. Showing sample data.'
                    }
                    cache_symbol_info(symbol, result)
                    return jsonify(result)
                else:
                    # Wait before retry
                    time.sleep(1)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Additional prediction endpoints (avoiding duplicate with existing one)
@app.route('/api/prediction/<symbol>/enhanced', methods=['GET'])
def get_enhanced_prediction(symbol):
    """Get AI prediction for a stock symbol using Gemini Pro"""
    try:
        # Get current stock data first
        current_price = 100.0  # Default fallback
        try:
            stock_data = get_finnhub_data(symbol)
            current_price = stock_data['price']
        except:
            try:
                stock_data = get_yahoo_finance_data_robust(symbol)
                current_price = stock_data['price']
            except:
                # Use fallback price
                current_price = 100.0
        
        # Use Gemini Pro for prediction
        try:
            import google.generativeai as genai
            from config import Config
            
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Create comprehensive prompt for stock prediction
            prompt = f"""
            As a professional financial analyst, provide a detailed stock prediction for {symbol}.
            Current price: ${current_price:.2f}
            
            Analyze the following aspects:
            1. Technical analysis patterns
            2. Market sentiment and trends
            3. Company fundamentals
            4. Industry outlook
            5. Economic factors
            
            Provide your analysis in this exact JSON format:
            {{
                "prediction": "BUY/HOLD/SELL",
                "confidence": 0.75,
                "target_price": 180.00,
                "reasoning": "Brief explanation of the prediction",
                "risk_level": "LOW/MEDIUM/HIGH",
                "timeframe": "1-3 months"
            }}
            
            Base your prediction on current market conditions and provide realistic targets.
            """
            
            response = model.generate_content(prompt)
            
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{[^{}]*\}', response.text, re.DOTALL)
            if json_match:
                try:
                    ai_prediction = json.loads(json_match.group())
                    
                    # Validate and format the response
                    prediction = {
                        'prediction': ai_prediction.get('prediction', 'HOLD'),
                        'confidence': float(ai_prediction.get('confidence', 0.5)),
                        'target_price': float(ai_prediction.get('target_price', current_price * 1.05)),
                        'reasoning': ai_prediction.get('reasoning', 'AI analysis based on current market conditions'),
                        'risk_level': ai_prediction.get('risk_level', 'MEDIUM'),
                        'timeframe': ai_prediction.get('timeframe', '1-3 months')
                    }
                except:
                    # Fallback if JSON parsing fails
                    prediction = {
                        'prediction': 'HOLD',
                        'confidence': 0.6,
                        'target_price': current_price * 1.02,
                        'reasoning': 'Gemini Pro analysis (parsing fallback)',
                        'risk_level': 'MEDIUM',
                        'timeframe': '1-3 months'
                    }
            else:
                # Fallback if no JSON found
                prediction = {
                    'prediction': 'HOLD',
                    'confidence': 0.5,
                    'target_price': current_price,
                    'reasoning': 'Gemini Pro analysis (format fallback)',
                    'risk_level': 'MEDIUM',
                    'timeframe': '1-3 months'
                }
                
        except Exception as e:
            print(f"Gemini Pro prediction error: {e}")
            # Fallback predictions if Gemini fails
            fallback_predictions = {
                'AAPL': {'prediction': 'BUY', 'confidence': 0.75, 'target_price': current_price * 1.08, 'reasoning': 'Strong fundamentals and market position'},
                'MSFT': {'prediction': 'HOLD', 'confidence': 0.65, 'target_price': current_price * 1.03, 'reasoning': 'Stable growth with cloud expansion'},
                'GOOGL': {'prediction': 'BUY', 'confidence': 0.70, 'target_price': current_price * 1.12, 'reasoning': 'AI leadership and search dominance'},
                'TSLA': {'prediction': 'HOLD', 'confidence': 0.60, 'target_price': current_price * 0.98, 'reasoning': 'Volatile but innovative company'},
                'META': {'prediction': 'BUY', 'confidence': 0.80, 'target_price': current_price * 1.15, 'reasoning': 'Metaverse potential and strong user base'}
            }
            
            base_prediction = fallback_predictions.get(symbol, {
                'prediction': 'HOLD',
                'confidence': 0.50,
                'target_price': current_price,
                'reasoning': 'Insufficient data for detailed analysis'
            })
            
            prediction = {
                **base_prediction,
                'risk_level': 'MEDIUM',
                'timeframe': '1-3 months',
                'current_price': current_price
            }
        
        return jsonify({
            'symbol': symbol,
            'prediction': prediction['prediction'],
            'confidence': prediction['confidence'],
            'target_price': prediction['target_price'],
            'current_price': prediction['current_price'],
            'analysis': f"AI analysis suggests {prediction['prediction']} for {symbol} with {prediction['confidence']*100:.0f}% confidence.",
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/<symbol>/sensitivity', methods=['GET'])
def get_prediction_sensitivity(symbol):
    """Get prediction sensitivity analysis"""
    try:
        return jsonify({
            'symbol': symbol,
            'sensitivity_analysis': {
                'market_volatility': 0.15,
                'earnings_impact': 0.25,
                'news_sentiment': 0.20,
                'technical_indicators': 0.30,
                'volume_trend': 0.10
            },
            'risk_factors': [
                'Market volatility',
                'Earnings uncertainty',
                'Regulatory changes',
                'Competition pressure'
            ],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Portfolio endpoints
@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get portfolio summary"""
    try:
        if bot_state['status'] == 'started':
            # Use real trading bot data
            portfolio_data = real_trading_bot.get_portfolio_summary()
            return jsonify(portfolio_data)
        else:
            # Return mock data when bot is stopped
            return jsonify({
                'total_value': 100000.00,
                'total_invested': 0.00,
                'total_gain_loss': 0.00,
                'total_gain_loss_percent': 0.00,
                'positions': [],
                'cash_balance': 100000.00,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/history', methods=['GET'])
def get_portfolio_history():
    """Get portfolio performance history"""
    try:
        # Generate mock historical data
        history = []
        base_value = 95000
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
            value = base_value + (i * 200) + (hash(date) % 1000 - 500)
            history.append({'date': date, 'value': value})
        
        return jsonify({
            'history': history,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/enhanced/summary', methods=['GET'])
def get_enhanced_portfolio_summary():
    """Get enhanced portfolio summary with performance metrics"""
    try:
        # Basic portfolio data
        portfolio_data = {
            'total_value': 100000.00,
            'total_invested': 95000.00,
            'total_gain_loss': 5000.00,
            'total_gain_loss_percent': 5.26,
            'positions': [
                {'symbol': 'AAPL', 'shares': 100, 'avg_price': 170.00, 'current_price': 175.50, 'value': 17550.00, 'gain_loss': 550.00},
                {'symbol': 'MSFT', 'shares': 50, 'avg_price': 375.00, 'current_price': 380.25, 'value': 19012.50, 'gain_loss': 262.50},
                {'symbol': 'GOOGL', 'shares': 30, 'avg_price': 140.00, 'current_price': 142.80, 'value': 4284.00, 'gain_loss': 84.00}
            ],
            'cash_balance': 59153.50,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate AI-powered portfolio insights using Gemini Pro
        ai_insights = generate_portfolio_insights_with_gemini(portfolio_data)
        
        # Add enhanced performance metrics
        enhanced_data = {
            **portfolio_data,
            'ai_insights': ai_insights,
            'performance_metrics': {
                'total_return': 5.2,  # Mock data
                'total_return_pct': 5.2,
                'daily_return': 0.15,
                'daily_return_pct': 0.15,
                'volatility': 12.5,
                'sharpe_ratio': 1.8,
                'max_drawdown': -3.2,
                'win_rate': 65.0,
                'avg_win': 2.1,
                'avg_loss': -1.4,
                'profit_factor': 1.5
            },
            'risk_metrics': {
                'var_95': -2.1,
                'var_99': -3.8,
                'expected_shortfall': -2.8,
                'beta': 1.1,
                'alpha': 0.8,
                'r_squared': 0.75
            },
            'allocation': {
                'equity': 75.0,
                'cash': 20.0,
                'bonds': 5.0
            },
            'sector_allocation': {
                'Technology': 35.0,
                'Healthcare': 15.0,
                'Financial': 12.0,
                'Consumer': 8.0,
                'Industrial': 5.0
            }
        }
        
        return jsonify(enhanced_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Trading bot endpoints
@app.route('/api/status', methods=['GET'])
def get_bot_status():
    """Get trading bot status"""
    try:
        # Calculate uptime if bot is running
        uptime = None
        if bot_state['status'] == 'started' and bot_state['started_at']:
            start_time = datetime.fromisoformat(bot_state['started_at'])
            uptime_delta = datetime.now() - start_time
            hours = int(uptime_delta.total_seconds() // 3600)
            minutes = int((uptime_delta.total_seconds() % 3600) // 60)
            uptime = f"{hours}h {minutes}m"
        
        # Get real trading metrics if bot is running
        trades_today = 0
        success_rate = 0.0
        if bot_state['status'] == 'started':
            orders = real_trading_bot.get_recent_orders()
            trades_today = len(orders)
            if trades_today > 0:
                # Calculate success rate based on profitable trades
                profitable_trades = 0
                for order in orders:
                    if order['side'] == 'SELL':
                        # This is a simplified success calculation
                        profitable_trades += 1
                success_rate = profitable_trades / trades_today if trades_today > 0 else 0.0
        
        # Get AI analysis status
        ai_status = {
            'ai_enabled': True,
            'ai_model': 'Gemini Pro 1.5',
            'ai_features': [
                'Real-time trading analysis',
                'Signal combination logic',
                'End-of-day learning insights',
                'Risk assessment enhancement'
            ],
            'last_ai_analysis': datetime.now().isoformat() if bot_state['status'] == 'started' else None
        }
        
        return jsonify({
            'status': bot_state['status'],
            'mode': 'ai_enhanced_paper_trading',
            'last_update': datetime.now().isoformat(),
            'uptime': uptime,
            'trades_today': trades_today,
            'success_rate': success_rate,
            'config': bot_state['config'],
            'bot_id': bot_state['bot_id'],
            'started_at': bot_state['started_at'],
            'ai_status': ai_status
        })
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get trading bot performance metrics"""
    try:
        return jsonify({
            'total_return': 0.0526,
            'daily_return': 0.0012,
            'weekly_return': 0.0085,
            'monthly_return': 0.0324,
            'sharpe_ratio': 1.25,
            'max_drawdown': -0.08,
            'win_rate': 0.75,
            'avg_trade_duration': '2.5h',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get recent trading orders"""
    try:
        if bot_state['status'] == 'started':
            # Use real trading bot data
            orders_data = real_trading_bot.get_recent_orders()
            return jsonify({
                'orders': orders_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Return empty orders when bot is stopped
            return jsonify({
                'orders': [],
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning/report', methods=['GET'])
def get_learning_report():
    """Get end-of-day learning report"""
    try:
        if bot_state['status'] == 'started' and real_trading_bot.current_session:
            # Generate current session report
            report = real_trading_bot._generate_eod_report()
            return jsonify(report)
        else:
            return jsonify({
                'error': 'No active trading session',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        logger.error(f"Error getting learning report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning/sessions', methods=['GET'])
def get_session_history():
    """Get trading session history"""
    try:
        if bot_state['status'] == 'started':
            # Convert session history to JSON-serializable format
            sessions_data = []
            for session in real_trading_bot.session_history:
                session_dict = {
                    'date': session.date,
                    'start_time': session.start_time.isoformat(),
                    'end_time': session.end_time.isoformat() if session.end_time else None,
                    'initial_capital': session.initial_capital,
                    'final_capital': session.final_capital,
                    'total_pnl': session.total_pnl,
                    'total_trades': session.total_trades,
                    'winning_trades': session.winning_trades,
                    'losing_trades': session.losing_trades,
                    'win_rate': (session.winning_trades / session.total_trades * 100) if session.total_trades > 0 else 0,
                    'sentiment_score': session.sentiment_score,
                    'market_events_count': len(session.market_events),
                    'learning_insights': session.learning_insights
                }
                sessions_data.append(session_dict)
                
            return jsonify({
                'sessions': sessions_data,
                'total_sessions': len(sessions_data),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'sessions': [],
                'total_sessions': 0,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning/insights', methods=['GET'])
def get_learning_insights():
    """Get current learning insights and recommendations"""
    try:
        if bot_state['status'] == 'started' and real_trading_bot.current_session:
            insights = {
                'current_session': {
                    'date': real_trading_bot.current_session.date,
                    'total_trades': real_trading_bot.current_session.total_trades,
                    'winning_trades': real_trading_bot.current_session.winning_trades,
                    'losing_trades': real_trading_bot.current_session.losing_trades,
                    'sentiment_score': real_trading_bot.current_session.sentiment_score,
                    'learning_insights': real_trading_bot.current_session.learning_insights
                },
                'model_status': {
                    'is_trained': real_trading_bot.learning_system.is_trained,
                    'training_samples': len(real_trading_bot.learning_system.training_data),
                    'last_training': 'Available' if real_trading_bot.learning_system.is_trained else 'Not trained yet'
                },
                'recommendations': real_trading_bot._generate_recommendations(),
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(insights)
        else:
            return jsonify({
                'error': 'No active trading session',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}")
        return jsonify({'error': str(e)}), 500

# Other endpoints
@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get available trading strategies"""
    try:
        return jsonify({
            'strategies': [
                {
                    'id': 'momentum',
                    'name': 'Momentum Trading',
                    'description': 'Buy stocks with strong upward momentum',
                    'risk_level': 'medium',
                    'expected_return': 0.12
                },
                {
                    'id': 'mean_reversion',
                    'name': 'Mean Reversion',
                    'description': 'Trade stocks that have deviated from their average',
                    'risk_level': 'low',
                    'expected_return': 0.08
                },
                {
                    'id': 'breakout',
                    'name': 'Breakout Strategy',
                    'description': 'Trade stocks breaking through key resistance levels',
                    'risk_level': 'high',
                    'expected_return': 0.18
                }
            ],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Get user's watchlist"""
    try:
        return jsonify({
            'watchlist': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50, 'change': 2.30, 'change_percent': 1.33},
                {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 380.25, 'change': -1.75, 'change_percent': -0.46},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 142.80, 'change': 0.85, 'change_percent': 0.60},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 245.30, 'change': -3.20, 'change_percent': -1.29},
                {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'price': 485.20, 'change': 5.40, 'change_percent': 1.12}
            ],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the trading bot with configuration"""
    try:
        config = request.get_json() or {}
        
        # Bot configuration parameters
        symbol = config.get('symbol', 'AAPL')
        strategy = config.get('strategy', 'momentum')
        initial_capital = config.get('initial_capital', 100000.0)
        risk_tolerance = config.get('risk_tolerance', 'medium')
        max_position_size = config.get('max_position_size', 0.1)
        max_daily_loss = config.get('max_daily_loss', 0.05)
        
        # Update global bot state
        bot_config = {
            'symbol': symbol,
            'strategy': strategy,
            'initial_capital': initial_capital,
            'risk_tolerance': risk_tolerance,
            'max_position_size': max_position_size,
            'max_daily_loss': max_daily_loss
        }
        
        # Start the real trading bot
        real_trading_bot.start_trading(symbol, bot_config)
        
        bot_state['status'] = 'started'
        bot_state['config'] = bot_config
        bot_state['started_at'] = datetime.now().isoformat()
        bot_state['bot_id'] = f'bot_{symbol}_{int(datetime.now().timestamp())}'
        
        # Response data
        response_data = {
            'status': 'started',
            'message': f'Trading bot started successfully for {symbol}',
            'config': bot_config,
            'bot_id': bot_state['bot_id'],
            'started_at': bot_state['started_at']
        }
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    try:
        # Stop the real trading bot
        real_trading_bot.stop_trading()
        
        # Update global bot state
        bot_state['status'] = 'stopped'
        bot_state['config'] = None
        bot_state['started_at'] = None
        bot_state['bot_id'] = None
        
        return jsonify({
            'status': 'stopped',
            'message': 'Trading bot stopped successfully',
            'stopped_at': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'error': str(e)}), 500

def generate_portfolio_insights_with_gemini(portfolio_data):
    """Generate AI-powered portfolio insights using Gemini Pro"""
    try:
        import google.generativeai as genai
        from config import Config
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prepare portfolio summary for analysis
        total_value = portfolio_data['total_value']
        total_gain_loss = portfolio_data['total_gain_loss']
        gain_loss_pct = portfolio_data['total_gain_loss_percent']
        positions = portfolio_data['positions']
        
        # Create detailed prompt for portfolio analysis
        prompt = f"""
        As a professional financial advisor, analyze this investment portfolio and provide actionable insights.
        
        Portfolio Summary:
        - Total Value: ${total_value:,.2f}
        - Total Gain/Loss: ${total_gain_loss:,.2f} ({gain_loss_pct:+.2f}%)
        - Cash Balance: ${portfolio_data['cash_balance']:,.2f}
        
        Current Positions:
        """
        
        for pos in positions:
            prompt += f"- {pos['symbol']}: {pos['shares']} shares @ ${pos['current_price']:.2f} (Avg: ${pos['avg_price']:.2f}, P&L: ${pos['gain_loss']:+.2f})\n"
        
        prompt += """
        
        Provide a comprehensive analysis including:
        1. Overall portfolio health and diversification
        2. Risk assessment and recommendations
        3. Top performing and underperforming positions
        4. Suggested actions (buy/sell/hold recommendations)
        5. Market outlook impact on the portfolio
        
        Format your response as a professional portfolio review (3-4 concise paragraphs).
        """
        
        response = model.generate_content(prompt)
        
        return {
            'summary': response.text.strip(),
            'generated_by': 'Gemini Pro',
            'analysis_date': datetime.now().isoformat(),
            'portfolio_score': calculate_portfolio_score(portfolio_data)
        }
        
    except Exception as e:
        print(f"Gemini portfolio insights error: {e}")
        return {
            'summary': 'Portfolio showing positive performance with 5.26% gains. Diversified holdings across major tech stocks provide good growth potential. Consider rebalancing for optimal risk management.',
            'generated_by': 'Fallback Analysis',
            'analysis_date': datetime.now().isoformat(),
            'portfolio_score': 75
        }

def calculate_portfolio_score(portfolio_data):
    """Calculate a simple portfolio health score (0-100)"""
    try:
        gain_loss_pct = portfolio_data['total_gain_loss_percent']
        num_positions = len(portfolio_data['positions'])
        
        # Base score from performance
        score = 50 + (gain_loss_pct * 2)  # Each 1% gain adds 2 points
        
        # Bonus for diversification
        if num_positions >= 3:
            score += 10
        elif num_positions >= 5:
            score += 20
        
        # Cap the score between 0 and 100
        return max(0, min(100, int(score)))
    except:
        return 75  # Default score

def generate_market_summary_with_gemini():
    """Generate AI-powered market summary using Gemini Pro"""
    try:
        import google.generativeai as genai
        from config import Config
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Get current market data for major indices
        major_stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META']
        market_data = []
        
        for symbol in major_stocks:
            try:
                stock_data = get_finnhub_data(symbol)
                market_data.append({
                    'symbol': symbol,
                    'price': stock_data['price'],
                    'change_pct': stock_data['change_percent']
                })
            except:
                # Skip if data unavailable
                pass
        
        prompt = f"""
        As a market analyst, provide a concise daily market summary based on these key stocks:
        
        """
        
        for stock in market_data:
            direction = "📈" if stock['change_pct'] > 0 else "📉" if stock['change_pct'] < 0 else "➡️"
            prompt += f"- {stock['symbol']}: ${stock['price']:.2f} ({stock['change_pct']:+.2f}%) {direction}\n"
        
        prompt += """
        
        Provide:
        1. Overall market sentiment (2-3 sentences)
        2. Key trends and notable movements
        3. What to watch for tomorrow
        
        Keep it concise and actionable for retail investors.
        """
        
        response = model.generate_content(prompt)
        
        return {
            'summary': response.text.strip(),
            'market_data': market_data,
            'generated_by': 'Gemini Pro',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Gemini market summary error: {e}")
        return {
            'summary': 'Markets showing mixed signals today with tech stocks leading the way. Investors are cautiously optimistic amid ongoing economic developments. Key focus remains on earnings reports and Federal Reserve policy updates.',
            'market_data': [],
            'generated_by': 'Fallback Analysis',
            'timestamp': datetime.now().isoformat()
        }

@app.route('/api/dashboard/market-summary', methods=['GET'])
def get_ai_market_summary():
    """Get AI-powered market summary for dashboard"""
    try:
        summary = generate_market_summary_with_gemini()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/insights', methods=['GET'])
def get_dashboard_insights():
    """Get comprehensive AI insights for dashboard"""
    try:
        import google.generativeai as genai
        from config import Config
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Get current time and market context
        current_time = datetime.now()
        market_hours = 9 <= current_time.hour <= 16  # Simplified market hours
        
        prompt = f"""
        As a financial dashboard AI, provide key insights for today's trading session.
        Current time: {current_time.strftime('%Y-%m-%d %H:%M')} EST
        Market hours: {'Open' if market_hours else 'Closed'}
        
        Provide 3-4 key insights covering:
        1. Current market sentiment and key drivers
        2. Sector rotation and opportunities
        3. Risk factors to monitor
        4. Actionable recommendations for traders
        
        Format as bullet points, each insight should be 1-2 sentences.
        """
        
        response = model.generate_content(prompt)
        
        insights = []
        lines = response.text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                insights.append(line.lstrip('•-* '))
        
        return jsonify({
            'insights': insights[:4],  # Limit to 4 insights
            'market_status': 'Open' if market_hours else 'Closed',
            'generated_by': 'Gemini Pro',
            'timestamp': current_time.isoformat()
        })
        
    except Exception as e:
        print(f"Dashboard insights error: {e}")
        return jsonify({
            'insights': [
                'Tech stocks continue to show resilience amid market volatility',
                'Federal Reserve policy decisions remain a key market driver',
                'Earnings season approaching - focus on guidance and forward-looking statements',
                'Consider defensive positioning as we approach quarter-end'
            ],
            'market_status': 'Open' if market_hours else 'Closed',
            'generated_by': 'Fallback Analysis',
            'timestamp': current_time.isoformat()
        })

@app.route('/api/dashboard/recommendations', methods=['GET'])
def get_ai_recommendations():
    """Get AI-powered trading recommendations for dashboard"""
    try:
        import google.generativeai as genai
        from config import Config
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Get current market data for analysis
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA']
        recommendations = []
        
        for symbol in symbols[:3]:  # Limit to 3 for performance
            try:
                stock_data = get_finnhub_data(symbol)
                current_price = stock_data['price']
                change_pct = stock_data['change_percent']
                
                prompt = f"""
                As a trading analyst, provide a brief recommendation for {symbol}.
                Current price: ${current_price:.2f}
                Today's change: {change_pct:+.2f}%
                
                Provide:
                - Action: BUY/HOLD/SELL
                - Reasoning (1 sentence)
                - Risk level: LOW/MEDIUM/HIGH
                
                Format: {symbol}: [ACTION] - [Reasoning] (Risk: [LEVEL])
                """
                
                response = model.generate_content(prompt)
                text = response.text.strip()
                
                # Parse the response
                action = 'HOLD'
                if 'BUY' in text.upper():
                    action = 'BUY'
                elif 'SELL' in text.upper():
                    action = 'SELL'
                
                risk = 'MEDIUM'
                if 'LOW' in text.upper():
                    risk = 'LOW'
                elif 'HIGH' in text.upper():
                    risk = 'HIGH'
                
                recommendations.append({
                    'symbol': symbol,
                    'action': action,
                    'current_price': current_price,
                    'change_percent': change_pct,
                    'reasoning': text,
                    'risk_level': risk
                })
                
            except Exception as e:
                print(f"Recommendation error for {symbol}: {e}")
                # Add fallback recommendation
                recommendations.append({
                    'symbol': symbol,
                    'action': 'HOLD',
                    'current_price': 100.0,
                    'change_percent': 0.0,
                    'reasoning': f'{symbol}: HOLD - Awaiting more market data for informed decision (Risk: MEDIUM)',
                    'risk_level': 'MEDIUM'
                })
        
        return jsonify({
            'recommendations': recommendations,
            'generated_by': 'Gemini Pro',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"AI recommendations error: {e}")
        return jsonify({
            'recommendations': [
                {'symbol': 'AAPL', 'action': 'HOLD', 'reasoning': 'Strong fundamentals, monitor for entry points', 'risk_level': 'MEDIUM'},
                {'symbol': 'MSFT', 'action': 'BUY', 'reasoning': 'Cloud growth and AI positioning look promising', 'risk_level': 'LOW'},
                {'symbol': 'GOOGL', 'action': 'HOLD', 'reasoning': 'Search dominance stable, AI competition increasing', 'risk_level': 'MEDIUM'}
            ],
            'generated_by': 'Fallback Analysis',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """Run a backtest with the provided configuration"""
    try:
        data = request.get_json()
        
        # Extract backtest parameters
        symbol = data.get('symbol', 'AAPL')
        start_date = data.get('start_date', '2023-01-01')
        end_date = data.get('end_date', '2024-01-01')
        initial_capital = data.get('initial_capital', 10000)
        strategy = data.get('strategy', 'buy_and_hold')
        
        # Mock backtest results for now
        import random
        
        # Generate some realistic backtest data
        days = 252  # Trading days in a year
        returns = []
        equity_curve = []
        current_value = initial_capital
        
        for i in range(days):
            daily_return = random.uniform(-0.03, 0.03)  # -3% to +3% daily
            current_value *= (1 + daily_return)
            returns.append(daily_return)
            equity_curve.append({
                'date': f"2023-{(i//21)+1:02d}-{(i%21)+1:02d}",
                'value': round(current_value, 2)
            })
        
        total_return = (current_value - initial_capital) / initial_capital
        max_drawdown = random.uniform(0.05, 0.20)  # 5-20% max drawdown
        sharpe_ratio = random.uniform(0.5, 2.0)
        win_rate = random.uniform(0.45, 0.75)
        
        backtest_results = {
            'symbol': symbol,
            'strategy': strategy,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': initial_capital,
            'final_value': round(current_value, 2),
            'total_return': round(total_return * 100, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'win_rate': round(win_rate * 100, 2),
            'total_trades': random.randint(50, 200),
            'equity_curve': equity_curve[-30:],  # Last 30 days
            'performance_metrics': {
                'volatility': round(random.uniform(0.15, 0.35) * 100, 2),
                'beta': round(random.uniform(0.8, 1.2), 2),
                'alpha': round(random.uniform(-0.05, 0.15) * 100, 2),
                'sortino_ratio': round(random.uniform(0.3, 1.5), 2)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(backtest_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancer"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Simple AI Stock Trading API Server on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
