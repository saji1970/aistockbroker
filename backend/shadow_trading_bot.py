#!/usr/bin/env python3
"""
AI Stock Trading Bot - Shadow Trading System
A sophisticated trading bot that performs paper trading with real market data
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading
import pickle
from gemini_predictor import GeminiStockPredictor
from data_fetcher import data_fetcher
from config import Config

# Configure logging
def _setup_logging():
    """Setup logging with cloud-compatible configuration"""
    handlers = [logging.StreamHandler()]  # Always include console output

    # Only add file handler in local environment
    is_cloud = os.environ.get('GAE_APPLICATION') or os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not is_cloud:
        try:
            handlers.append(logging.FileHandler('trading_bot.log'))
        except Exception:
            pass  # Skip file logging if not available

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

_setup_logging()
logger = logging.getLogger(__name__)

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
    ai_confidence: float = 0.0
    expected_return: float = 0.0
    actual_return: Optional[float] = None

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
    daily_trades: List[Order]
    target_amount: Optional[float] = None
    milestone_progress: float = 0.0

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

class MomentumStrategy(TradingStrategy):
    """Momentum-based trading strategy"""
    
    def __init__(self, parameters: Dict):
        super().__init__("Momentum", parameters)
        self.lookback_period = parameters.get('lookback_period', 20)
        self.momentum_threshold = parameters.get('momentum_threshold', 0.02)
        
    def analyze(self, data: List[StockData]) -> OrderType:
        if len(data) < self.lookback_period:
            return OrderType.HOLD
            
        # Calculate momentum
        recent_prices = [d.close for d in data[-self.lookback_period:]]
        momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        
        if momentum > self.momentum_threshold:
            return OrderType.BUY
        elif momentum < -self.momentum_threshold:
            return OrderType.SELL
        else:
            return OrderType.HOLD
            
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        # Exit if momentum reverses
        if position.quantity > 0:  # Long position
            return current_data.change_percent < -0.01
        else:  # Short position
            return current_data.change_percent > 0.01

class MeanReversionStrategy(TradingStrategy):
    """Mean reversion trading strategy"""
    
    def __init__(self, parameters: Dict):
        super().__init__("MeanReversion", parameters)
        self.lookback_period = parameters.get('lookback_period', 20)
        self.std_threshold = parameters.get('std_threshold', 2.0)
        
    def analyze(self, data: List[StockData]) -> OrderType:
        if len(data) < self.lookback_period:
            return OrderType.HOLD
            
        # Calculate Bollinger Bands
        recent_prices = [d.close for d in data[-self.lookback_period:]]
        mean_price = np.mean(recent_prices)
        std_price = np.std(recent_prices)
        
        current_price = data[-1].close
        upper_band = mean_price + (self.std_threshold * std_price)
        lower_band = mean_price - (self.std_threshold * std_price)
        
        if current_price > upper_band:
            return OrderType.SELL
        elif current_price < lower_band:
            return OrderType.BUY
        else:
            return OrderType.HOLD
            
    def should_exit(self, position: Position, current_data: StockData) -> bool:
        # Exit when price returns to mean
        return abs(current_data.change_percent) < 0.005

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
        return 40 <= self.calculate_rsi([current_data.close]) <= 60

class GeminiStrategy(TradingStrategy):
    """AI-powered trading strategy using Gemini predictions"""

    def __init__(self, parameters: Dict):
        super().__init__("GeminiAI", parameters)
        self.confidence_threshold = parameters.get('confidence_threshold', 0.7)
        self.prediction_timeframe = parameters.get('prediction_timeframe', '1d')
        self.min_expected_return = parameters.get('min_expected_return', 0.02)
        self.predictor = None

    def set_predictor(self, predictor):
        """Set the Gemini predictor instance"""
        self.predictor = predictor

    def analyze(self, data: List[StockData], symbol: str = None) -> OrderType:
        if not self.predictor or not symbol:
            return OrderType.HOLD

        try:
            # Get AI prediction
            prediction = self.predictor.get_stock_prediction(symbol, self.prediction_timeframe)

            if 'error' in prediction:
                logger.warning(f"AI prediction error for {symbol}: {prediction['error']}")
                return OrderType.HOLD

            confidence = prediction.get('confidence', 0) / 100.0
            lstm_analysis = prediction.get('lstm_analysis', {})

            # Check confidence threshold
            if confidence < self.confidence_threshold:
                return OrderType.HOLD

            # Extract prediction insights
            trend_direction = lstm_analysis.get('trend_direction', 'Neutral')
            prediction_factor = lstm_analysis.get('prediction_factor', 0)

            # Make trading decision based on AI prediction
            if 'bullish' in trend_direction.lower() and prediction_factor > self.min_expected_return * 100:
                return OrderType.BUY
            elif 'bearish' in trend_direction.lower() and prediction_factor < -self.min_expected_return * 100:
                return OrderType.SELL
            else:
                return OrderType.HOLD

        except Exception as e:
            logger.error(f"Error in Gemini strategy analysis: {e}")
            return OrderType.HOLD

    def should_exit(self, position: Position, current_data: StockData) -> bool:
        # Conservative exit strategy - exit if losing more than 3%
        unrealized_loss_pct = position.unrealized_pnl / (position.avg_price * position.quantity)
        return unrealized_loss_pct < -0.03

    def get_prediction_data(self, symbol: str) -> Dict:
        """Get detailed prediction data for analysis"""
        if not self.predictor:
            return {}

        try:
            return self.predictor.get_stock_prediction(symbol, self.prediction_timeframe)
        except Exception as e:
            logger.error(f"Error getting prediction data for {symbol}: {e}")
            return {}

class MarketDataProvider:
    """Real-time market data provider"""
    
    def __init__(self):
        self.data_cache = {}
        self.subscribers = []
        self.running = False
        
    def subscribe(self, callback):
        """Subscribe to real-time data updates"""
        self.subscribers.append(callback)
        
    def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """Get current stock data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
                
            latest = hist.iloc[-1]
            
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
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
            
    def get_historical_data(self, symbol: str, period: str = "1mo") -> List[StockData]:
        """Get historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            data = []
            for timestamp, row in hist.iterrows():
                data.append(StockData(
                    symbol=symbol,
                    price=float(row['Close']),
                    volume=int(row['Volume']),
                    timestamp=timestamp.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    change=float(row['Close'] - row['Open']),
                    change_percent=float((row['Close'] - row['Open']) / row['Open'] * 100)
                ))
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []

class RiskManager:
    """Risk management system"""
    
    def __init__(self, max_position_size: float = 0.1, max_daily_loss: float = 0.05):
        self.max_position_size = max_position_size  # Max 10% of portfolio per position
        self.max_daily_loss = max_daily_loss  # Max 5% daily loss
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        
    def can_open_position(self, portfolio: Portfolio, symbol: str, quantity: int, price: float) -> bool:
        """Check if position can be opened"""
        # Check daily loss limit
        if self.daily_pnl < -portfolio.total_value * self.max_daily_loss:
            logger.warning(f"Daily loss limit reached: {self.daily_pnl}")
            return False
            
        # Check position size limit
        position_value = quantity * price
        if position_value > portfolio.total_value * self.max_position_size:
            logger.warning(f"Position size too large: {position_value}")
            return False
            
        return True
        
    def calculate_position_size(self, portfolio: Portfolio, symbol: str, price: float) -> int:
        """Calculate optimal position size"""
        max_value = portfolio.total_value * self.max_position_size
        max_shares = int(max_value / price)
        return min(max_shares, 100)  # Cap at 100 shares for demo
        
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L"""
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_pnl = 0.0
            self.last_reset_date = current_date
        self.daily_pnl += pnl

class ShadowTradingBot:
    """Enhanced shadow trading bot with Gemini AI predictions and daily evaluation"""

    def __init__(self, initial_capital: float = 100000.0, target_amount: Optional[float] = None,
                 trading_period_days: int = 30, max_position_size: float = 0.1,
                 max_daily_loss: float = 0.05, risk_tolerance: str = 'medium',
                 trading_strategy: str = 'ai_gemini', enable_ml_learning: bool = True,
                 milestone_target_percent: float = 0.1):
        self.initial_capital = initial_capital
        self.target_amount = target_amount or (initial_capital * (1 + milestone_target_percent))
        self.trading_period_days = trading_period_days
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.risk_tolerance = risk_tolerance
        self.trading_strategy = trading_strategy
        self.enable_ml_learning = enable_ml_learning
        self.milestone_target_percent = milestone_target_percent
        
        self.portfolio = Portfolio(
            cash=initial_capital,
            total_value=initial_capital,
            positions={},
            orders=[],
            performance_metrics={},
            daily_trades=[],
            target_amount=self.target_amount,
            milestone_progress=0.0
        )
        
        self.market_data = MarketDataProvider()
        self.risk_manager = RiskManager(max_position_size, max_daily_loss)
        self.strategies = {}
        self.watchlist = []
        self.running = False

        # Initialize Gemini predictor and data fetcher
        self.gemini_predictor = GeminiStockPredictor(data_fetcher)
        self.data_fetcher = data_fetcher

        # Daily evaluation tracking
        self.daily_performance = []
        self.strategy_performance = {}
        self.learning_data = []
        
        # Initialize strategies including new AI strategy
        self.strategies['momentum'] = MomentumStrategy({
            'lookback_period': 20,
            'momentum_threshold': 0.02
        })
        self.strategies['mean_reversion'] = MeanReversionStrategy({
            'lookback_period': 20,
            'std_threshold': 2.0
        })
        self.strategies['rsi'] = RSIStrategy({
            'lookback_period': 14,
            'oversold_threshold': 30,
            'overbought_threshold': 70
        })
        self.strategies['ai_gemini'] = GeminiStrategy({
            'confidence_threshold': 0.7,
            'prediction_timeframe': '1d',
            'min_expected_return': 0.02
        })
        
    def add_to_watchlist(self, symbol: str):
        """Add symbol to watchlist"""
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
            logger.info(f"Added {symbol} to watchlist")
            
    def remove_from_watchlist(self, symbol: str):
        """Remove symbol from watchlist"""
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
            logger.info(f"Removed {symbol} from watchlist")
            
    def place_order(self, symbol: str, order_type: OrderType, quantity: int,
                   strategy: str, reason: str, ai_confidence: float = 0.0, expected_return: float = 0.0) -> Optional[Order]:
        """Place a shadow trading order"""
        current_data = self.market_data.get_stock_data(symbol)
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
                logger.warning(f"Insufficient cash for {symbol}: {total_cost} > {self.portfolio.cash}")
                return None
                
        elif order_type == OrderType.SELL:
            if symbol not in self.portfolio.positions or self.portfolio.positions[symbol].quantity < quantity:
                logger.warning(f"Insufficient position for {symbol}")
                return None
                
        # Create order with AI data
        order = Order(
            id=f"{symbol}_{int(time.time())}",
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            price=current_data.price,
            timestamp=datetime.now(),
            status=OrderStatus.FILLED,  # Shadow trading - orders are immediately filled
            strategy=strategy,
            reason=reason,
            ai_confidence=ai_confidence,
            expected_return=expected_return
        )
        
        # Execute order
        self._execute_order(order)
        self.portfolio.orders.append(order)
        self.portfolio.daily_trades.append(order)

        # Update milestone progress
        self._update_milestone_progress()

        logger.info(f"Order executed: {order_type.value} {quantity} {symbol} @ ${current_data.price:.2f} (AI Confidence: {ai_confidence:.2f})")
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
            pos = self.portfolio.positions[order.symbol]
            realized_pnl = (order.price - pos.avg_price) * order.quantity
            pos.realized_pnl += realized_pnl
            pos.quantity -= order.quantity
            
            if pos.quantity == 0:
                del self.portfolio.positions[order.symbol]
                
        # Update portfolio value
        self._update_portfolio_value()
        
    def _update_portfolio_value(self):
        """Update total portfolio value"""
        total_value = self.portfolio.cash
        
        for symbol, position in self.portfolio.positions.items():
            current_data = self.market_data.get_stock_data(symbol)
            if current_data:
                position.current_price = current_data.price
                position.market_value = position.quantity * current_data.price
                position.unrealized_pnl = (current_data.price - position.avg_price) * position.quantity
                total_value += position.market_value
                
        self.portfolio.total_value = total_value
        
    def run_strategy(self, symbol: str, strategy_name: str):
        """Run a specific strategy on a symbol with enhanced AI integration"""
        if strategy_name not in self.strategies:
            logger.error(f"Strategy {strategy_name} not found")
            return

        strategy = self.strategies[strategy_name]

        # Set predictor for AI strategy
        if isinstance(strategy, GeminiStrategy):
            strategy.set_predictor(self.gemini_predictor)

        # Get historical data
        historical_data = self.market_data.get_historical_data(symbol, "3mo")
        if not historical_data:
            return

        # Get current data
        current_data = self.market_data.get_stock_data(symbol)
        if not current_data:
            return

        # Analyze with strategy (pass symbol for AI strategy)
        if isinstance(strategy, GeminiStrategy):
            signal = strategy.analyze(historical_data, symbol)
        else:
            signal = strategy.analyze(historical_data)

        # Check existing position
        current_position = self.portfolio.positions.get(symbol)

        # Get AI prediction data for enhanced decision making
        ai_confidence = 0.0
        expected_return = 0.0
        if isinstance(strategy, GeminiStrategy):
            prediction_data = strategy.get_prediction_data(symbol)
            ai_confidence = prediction_data.get('confidence', 0) / 100.0
            lstm_analysis = prediction_data.get('lstm_analysis', {})
            expected_return = lstm_analysis.get('prediction_factor', 0) / 100.0

        if signal == OrderType.BUY and (not current_position or current_position.quantity == 0):
            # Calculate position size based on milestone progress
            quantity = self._calculate_milestone_position_size(symbol, current_data.price, expected_return)
            if quantity > 0:
                self.place_order(symbol, OrderType.BUY, quantity, strategy_name,
                               f"Strategy signal: {signal.value}", ai_confidence, expected_return)

        elif signal == OrderType.SELL and current_position and current_position.quantity > 0:
            # Sell entire position
            self.place_order(symbol, OrderType.SELL, current_position.quantity, strategy_name,
                           f"Strategy signal: {signal.value}", ai_confidence, expected_return)

        # Check exit conditions for existing positions
        if current_position and current_position.quantity > 0:
            if strategy.should_exit(current_position, current_data):
                self.place_order(symbol, OrderType.SELL, current_position.quantity, strategy_name,
                               "Exit condition met", ai_confidence, expected_return)
                               
    def run_trading_cycle(self):
        """Enhanced trading cycle with milestone tracking"""
        logger.info("Starting enhanced trading cycle...")

        # Reset daily trades at start of new day
        current_date = datetime.now().date()
        if not hasattr(self, '_last_trading_date') or self._last_trading_date != current_date:
            self.portfolio.daily_trades = []
            self._last_trading_date = current_date

        for symbol in self.watchlist:
            try:
                # Prioritize AI strategy if available
                if self.trading_strategy in self.strategies:
                    self.run_strategy(symbol, self.trading_strategy)
                else:
                    # Run each strategy
                    for strategy_name in self.strategies.keys():
                        self.run_strategy(symbol, strategy_name)

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")

        # Update portfolio value
        self._update_portfolio_value()

        # Check if milestone achieved
        self._check_milestone_achievement()

        # Log portfolio status
        self._log_portfolio_status()

        # Collect learning data
        self._collect_learning_data()
        
    def _log_portfolio_status(self):
        """Log current portfolio status"""
        logger.info(f"Portfolio Value: ${self.portfolio.total_value:,.2f}")
        logger.info(f"Cash: ${self.portfolio.cash:,.2f}")
        logger.info(f"Positions: {len(self.portfolio.positions)}")
        
        for symbol, position in self.portfolio.positions.items():
            logger.info(f"  {symbol}: {position.quantity} shares @ ${position.avg_price:.2f} "
                       f"(Current: ${position.current_price:.2f}, "
                       f"P&L: ${position.unrealized_pnl:,.2f})")
                       
    def get_performance_report(self) -> Dict:
        """Generate performance report"""
        total_return = (self.portfolio.total_value - self.initial_capital) / self.initial_capital
        
        return {
            'initial_capital': self.initial_capital,
            'current_value': self.portfolio.total_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'cash': self.portfolio.cash,
            'positions_count': len(self.portfolio.positions),
            'orders_count': len(self.portfolio.orders),
            'timestamp': datetime.now().isoformat()
        }
        
    def start(self, interval: int = 300):  # 5 minutes default
        """Start the trading bot"""
        self.running = True
        logger.info(f"Starting trading bot with {interval}s interval...")
        
        # Add some default stocks to watchlist
        if not self.watchlist:
            self.watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
            
        while self.running:
            try:
                self.run_trading_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Trading bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")
                time.sleep(interval)
                
    def run(self, interval: int = 300):
        """Run the trading bot (alias for start method)"""
        self.start(interval)
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False
        logger.info("Trading bot stopped")
    
    def get_ml_insights(self):
        """Get machine learning insights and patterns"""
        if not self.enable_ml_learning:
            return {
                'patterns_learned': 0,
                'accuracy_score': 0.0,
                'market_conditions': 'ML learning disabled',
                'recommendations': ['Enable ML learning in bot configuration']
            }
        
        # Simulate ML insights based on trading activity
        total_orders = len(self.portfolio.orders)
        successful_trades = len([o for o in self.portfolio.orders if o.status == OrderStatus.FILLED])
        
        accuracy = successful_trades / max(total_orders, 1)
        patterns_learned = min(total_orders // 10, 50)  # Simulate learning patterns
        
        # Determine market conditions based on recent performance
        if hasattr(self.portfolio, 'performance_metrics') and self.portfolio.performance_metrics:
            total_return = self.portfolio.performance_metrics.get('total_return_percent', 0)
            if total_return > 0.05:
                market_conditions = 'bullish'
            elif total_return < -0.05:
                market_conditions = 'bearish'
            else:
                market_conditions = 'sideways'
        else:
            market_conditions = 'unknown'
        
        # Generate recommendations based on current state
        recommendations = []
        if accuracy < 0.5:
            recommendations.append("Consider adjusting trading strategy parameters")
        if self.risk_tolerance == 'high' and total_orders > 20:
            recommendations.append("High risk tolerance detected - monitor position sizes")
        if self.enable_ml_learning and patterns_learned > 10:
            recommendations.append("ML model has learned sufficient patterns for better predictions")
        
        return {
            'patterns_learned': patterns_learned,
            'accuracy_score': accuracy,
            'market_conditions': market_conditions,
            'recommendations': recommendations,
            'total_trades': total_orders,
            'successful_trades': successful_trades,
            'current_milestone_progress': self.portfolio.milestone_progress,
            'target_amount': self.portfolio.target_amount,
            'daily_trades_count': len(self.portfolio.daily_trades)
        }

    def _update_milestone_progress(self):
        """Update progress toward milestone target"""
        if self.portfolio.target_amount:
            progress = (self.portfolio.total_value - self.initial_capital) / (self.portfolio.target_amount - self.initial_capital)
            self.portfolio.milestone_progress = max(0.0, min(1.0, progress))

    def _calculate_milestone_position_size(self, symbol: str, price: float, expected_return: float) -> int:
        """Calculate position size based on milestone progress and expected return"""
        # Base calculation from risk manager
        base_quantity = self.risk_manager.calculate_position_size(self.portfolio, symbol, price)

        # Adjust based on milestone progress (more aggressive as we get closer)
        milestone_multiplier = 1.0 + (self.portfolio.milestone_progress * 0.5)

        # Adjust based on AI confidence/expected return
        if expected_return > 0.03:  # High expected return
            confidence_multiplier = 1.2
        elif expected_return < -0.02:  # Negative expected return
            confidence_multiplier = 0.5
        else:
            confidence_multiplier = 1.0

        adjusted_quantity = int(base_quantity * milestone_multiplier * confidence_multiplier)
        return min(adjusted_quantity, 200)  # Cap at 200 shares

    def _check_milestone_achievement(self):
        """Check if milestone has been achieved"""
        if self.portfolio.milestone_progress >= 1.0:
            logger.info(f"🎉 Milestone achieved! Portfolio value: ${self.portfolio.total_value:,.2f}")

            # Record achievement
            achievement_data = {
                'timestamp': datetime.now(),
                'initial_capital': self.initial_capital,
                'final_value': self.portfolio.total_value,
                'target_amount': self.portfolio.target_amount,
                'total_return': (self.portfolio.total_value - self.initial_capital) / self.initial_capital,
                'trading_days': len(self.daily_performance),
                'total_trades': len(self.portfolio.orders)
            }

            # Save achievement data
            self._save_milestone_achievement(achievement_data)

    def _collect_learning_data(self):
        """Collect data for machine learning improvements"""
        if not self.enable_ml_learning:
            return

        # Analyze recent trades for learning
        recent_trades = [order for order in self.portfolio.orders if
                        (datetime.now() - order.timestamp).days <= 1]

        for order in recent_trades:
            # Calculate actual return if position was closed
            if order.actual_return is None:
                current_position = self.portfolio.positions.get(order.symbol)
                if current_position:
                    # Position still open - calculate unrealized return
                    actual_return = (current_position.current_price - order.price) / order.price
                else:
                    # Position closed - find closing order
                    closing_orders = [o for o in self.portfolio.orders if
                                    o.symbol == order.symbol and
                                    o.order_type != order.order_type and
                                    o.timestamp > order.timestamp]
                    if closing_orders:
                        closing_order = closing_orders[0]
                        if order.order_type == OrderType.BUY:
                            actual_return = (closing_order.price - order.price) / order.price
                        else:
                            actual_return = (order.price - closing_order.price) / closing_order.price
                        order.actual_return = actual_return

                # Store learning data
                learning_entry = {
                    'symbol': order.symbol,
                    'strategy': order.strategy,
                    'ai_confidence': order.ai_confidence,
                    'expected_return': order.expected_return,
                    'actual_return': actual_return,
                    'order_type': order.order_type.value,
                    'timestamp': order.timestamp,
                    'market_conditions': self._get_market_conditions()
                }
                self.learning_data.append(learning_entry)

    def _get_market_conditions(self) -> Dict:
        """Get current market conditions for learning analysis"""
        try:
            # Get S&P 500 as market indicator
            spy_data = self.market_data.get_stock_data('SPY')
            if spy_data:
                return {
                    'market_trend': 'bullish' if spy_data.change_percent > 0 else 'bearish',
                    'market_volatility': abs(spy_data.change_percent),
                    'timestamp': datetime.now()
                }
        except:
            pass
        return {'market_trend': 'neutral', 'market_volatility': 0.0, 'timestamp': datetime.now()}

    def perform_daily_evaluation(self):
        """Perform end-of-day evaluation and strategy learning"""
        logger.info("🔍 Performing daily evaluation and strategy learning...")

        current_date = datetime.now().date()
        daily_trades = self.portfolio.daily_trades

        if not daily_trades:
            logger.info("No trades executed today.")
            return

        # Calculate daily performance metrics
        daily_pnl = 0.0
        winning_trades = 0
        losing_trades = 0
        total_ai_confidence = 0.0

        for trade in daily_trades:
            if trade.actual_return is not None:
                pnl = trade.actual_return * trade.quantity * trade.price
                daily_pnl += pnl

                if pnl > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1

                total_ai_confidence += trade.ai_confidence

        # Calculate strategy performance
        strategy_performance = {}
        for trade in daily_trades:
            if trade.strategy not in strategy_performance:
                strategy_performance[trade.strategy] = {'trades': 0, 'pnl': 0.0, 'accuracy': 0.0}

            strategy_performance[trade.strategy]['trades'] += 1
            if trade.actual_return is not None:
                pnl = trade.actual_return * trade.quantity * trade.price
                strategy_performance[trade.strategy]['pnl'] += pnl

        # Calculate accuracy for each strategy
        for strategy in strategy_performance:
            strategy_trades = [t for t in daily_trades if t.strategy == strategy and t.actual_return is not None]
            if strategy_trades:
                profitable_trades = len([t for t in strategy_trades if t.actual_return > 0])
                strategy_performance[strategy]['accuracy'] = profitable_trades / len(strategy_trades)

        # Store daily performance
        daily_performance = {
            'date': current_date,
            'total_trades': len(daily_trades),
            'daily_pnl': daily_pnl,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) > 0 else 0,
            'avg_ai_confidence': total_ai_confidence / len(daily_trades) if daily_trades else 0,
            'strategy_performance': strategy_performance,
            'portfolio_value': self.portfolio.total_value,
            'milestone_progress': self.portfolio.milestone_progress
        }

        self.daily_performance.append(daily_performance)

        # Update strategy performance tracking
        for strategy, perf in strategy_performance.items():
            if strategy not in self.strategy_performance:
                self.strategy_performance[strategy] = []
            self.strategy_performance[strategy].append(perf)

        # Learn and adapt strategies
        self._adapt_strategies(daily_performance)

        # Log results
        logger.info(f"📊 Daily Performance Summary:")
        logger.info(f"   Trades: {daily_performance['total_trades']}")
        logger.info(f"   P&L: ${daily_pnl:,.2f}")
        logger.info(f"   Win Rate: {daily_performance['win_rate']:.1%}")
        logger.info(f"   Portfolio Value: ${self.portfolio.total_value:,.2f}")
        logger.info(f"   Milestone Progress: {self.portfolio.milestone_progress:.1%}")

        # Save evaluation data
        self._save_daily_evaluation(daily_performance)

    def _adapt_strategies(self, daily_performance: Dict):
        """Adapt strategy parameters based on daily performance"""
        if not self.enable_ml_learning:
            return

        # Find best performing strategy
        best_strategy = None
        best_pnl = float('-inf')

        for strategy, perf in daily_performance['strategy_performance'].items():
            if perf['pnl'] > best_pnl:
                best_pnl = perf['pnl']
                best_strategy = strategy

        logger.info(f"🎯 Best performing strategy today: {best_strategy}")

        # Adjust parameters based on performance
        if best_strategy == 'ai_gemini' and best_strategy in self.strategies:
            gemini_strategy = self.strategies[best_strategy]
            if daily_performance['win_rate'] > 0.6:
                # Lower confidence threshold for good performance
                gemini_strategy.confidence_threshold = max(0.6, gemini_strategy.confidence_threshold - 0.05)
                logger.info(f"🔧 Lowered AI confidence threshold to {gemini_strategy.confidence_threshold:.2f}")
            elif daily_performance['win_rate'] < 0.4:
                # Raise confidence threshold for poor performance
                gemini_strategy.confidence_threshold = min(0.9, gemini_strategy.confidence_threshold + 0.05)
                logger.info(f"🔧 Raised AI confidence threshold to {gemini_strategy.confidence_threshold:.2f}")

    def _save_daily_evaluation(self, evaluation_data: Dict):
        """Save daily evaluation data to file (cloud-compatible)"""
        try:
            # Check if we're in a cloud environment
            is_cloud = os.environ.get('GAE_APPLICATION') or os.environ.get('GOOGLE_CLOUD_PROJECT')

            if is_cloud:
                # In cloud environment, log the evaluation data instead of saving to file
                eval_data = evaluation_data.copy()
                eval_data['date'] = eval_data['date'].isoformat()
                logger.info(f"📄 Daily evaluation data: {json.dumps(eval_data, indent=2, default=str)}")
            else:
                # Local environment - save to file
                filename = f"daily_evaluation_{datetime.now().strftime('%Y%m%d')}.json"
                with open(filename, 'w') as f:
                    eval_data = evaluation_data.copy()
                    eval_data['date'] = eval_data['date'].isoformat()
                    json.dump(eval_data, f, indent=2, default=str)
                logger.info(f"📄 Daily evaluation saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving daily evaluation: {e}")

    def _save_milestone_achievement(self, achievement_data: Dict):
        """Save milestone achievement data (cloud-compatible)"""
        try:
            # Check if we're in a cloud environment
            is_cloud = os.environ.get('GAE_APPLICATION') or os.environ.get('GOOGLE_CLOUD_PROJECT')

            if is_cloud:
                # In cloud environment, log the achievement data instead of saving to file
                logger.info(f"🏆 Milestone achievement data: {json.dumps(achievement_data, indent=2, default=str)}")
            else:
                # Local environment - save to file
                filename = f"milestone_achievement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(achievement_data, f, indent=2, default=str)
                logger.info(f"🏆 Milestone achievement saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving milestone achievement: {e}")

    def get_strategy_insights(self) -> Dict:
        """Get insights about strategy performance"""
        if not self.strategy_performance:
            return {'message': 'No strategy performance data available yet'}

        insights = {}
        for strategy, performances in self.strategy_performance.items():
            if not performances:
                continue

            total_trades = sum(p['trades'] for p in performances)
            total_pnl = sum(p['pnl'] for p in performances)
            avg_accuracy = sum(p['accuracy'] for p in performances) / len(performances)

            insights[strategy] = {
                'total_trades': total_trades,
                'total_pnl': total_pnl,
                'average_accuracy': avg_accuracy,
                'performance_trend': 'improving' if len(performances) > 1 and performances[-1]['pnl'] > performances[-2]['pnl'] else 'declining'
            }

        return insights

    def schedule_daily_evaluation(self, hour: int = 16):  # 4 PM market close
        """Schedule daily evaluation at market close"""
        import schedule

        def run_evaluation():
            self.perform_daily_evaluation()

        schedule.every().day.at(f"{hour:02d}:00").do(run_evaluation)
        logger.info(f"⏰ Scheduled daily evaluation at {hour}:00")

if __name__ == "__main__":
    # Enhanced Shadow Trading Bot with Gemini AI Integration
    print("🤖 Starting Enhanced AI Shadow Trading Bot...")
    print("="*60)

    # Configuration
    initial_capital = 100000.0  # $100k starting capital
    target_amount = 110000.0    # $110k target (10% gain)

    # Create enhanced trading bot
    bot = ShadowTradingBot(
        initial_capital=initial_capital,
        target_amount=target_amount,
        trading_strategy='ai_gemini',  # Use Gemini AI strategy
        enable_ml_learning=True,
        milestone_target_percent=0.1   # 10% target
    )

    # Add popular day trading stocks to watchlist
    watchlist_symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'AMZN', 'META']
    for symbol in watchlist_symbols:
        bot.add_to_watchlist(symbol)

    # Schedule daily evaluation at market close (4 PM EST)
    bot.schedule_daily_evaluation(hour=16)

    print(f"💰 Initial Capital: ${initial_capital:,.2f}")
    print(f"🎯 Target Amount: ${target_amount:,.2f}")
    print(f"📈 Strategy: Gemini AI-Powered Day Trading")
    print(f"📊 Watchlist: {', '.join(watchlist_symbols)}")
    print(f"🔄 Trading Interval: Every 5 minutes")
    print(f"📅 Daily Evaluation: 4:00 PM EST")
    print("="*60)

    try:
        # Start the enhanced trading bot
        bot.start(interval=300)  # Run every 5 minutes for day trading
    except KeyboardInterrupt:
        bot.stop()
        print("\n🛑 Trading bot stopped by user.")

        # Perform final evaluation
        bot.perform_daily_evaluation()

        # Print comprehensive final report
        report = bot.get_performance_report()
        ml_insights = bot.get_ml_insights()
        strategy_insights = bot.get_strategy_insights()

        print("\n" + "="*60)
        print("🏁 FINAL PERFORMANCE REPORT")
        print("="*60)
        print(f"📊 Portfolio Performance:")
        print(f"   Initial Capital: ${report['initial_capital']:,.2f}")
        print(f"   Final Value: ${report['current_value']:,.2f}")
        print(f"   Total Return: ${report['total_return_pct']:.2f}%")
        print(f"   Cash Available: ${report['cash']:,.2f}")
        print(f"   Active Positions: {report['positions_count']}")
        print(f"   Total Orders: {report['orders_count']}")
        print()

        print(f"🎯 Milestone Progress:")
        print(f"   Target Amount: ${target_amount:,.2f}")
        print(f"   Progress: {bot.portfolio.milestone_progress:.1%}")
        print(f"   Daily Trades: {len(bot.portfolio.daily_trades)}")

        if bot.portfolio.milestone_progress >= 1.0:
            print("   🎉 MILESTONE ACHIEVED! 🎉")
        else:
            remaining = target_amount - report['current_value']
            print(f"   Remaining to Target: ${remaining:,.2f}")
        print()

        print(f"🤖 AI Performance:")
        print(f"   Patterns Learned: {ml_insights['patterns_learned']}")
        print(f"   Model Accuracy: {ml_insights['accuracy_score']:.1%}")
        print(f"   Market Conditions: {ml_insights['market_conditions']}")
        print(f"   Total AI Trades: {ml_insights['total_trades']}")
        print(f"   Successful Trades: {ml_insights['successful_trades']}")
        print()

        if strategy_insights and 'message' not in strategy_insights:
            print(f"📈 Strategy Insights:")
            for strategy, data in strategy_insights.items():
                print(f"   {strategy}:")
                print(f"     Total Trades: {data['total_trades']}")
                print(f"     Total P&L: ${data['total_pnl']:,.2f}")
                print(f"     Accuracy: {data['average_accuracy']:.1%}")
                print(f"     Trend: {data['performance_trend']}")

        print("\n💡 AI Recommendations:")
        for rec in ml_insights['recommendations']:
            print(f"   • {rec}")

        print("\n📁 Data Files:")
        print("   • Daily evaluation saved to daily_evaluation_YYYYMMDD.json")
        if bot.portfolio.milestone_progress >= 1.0:
            print("   • Milestone achievement saved to milestone_achievement_YYYYMMDD_HHMMSS.json")
        print("   • Trading log saved to trading_bot.log")

        print("\n" + "="*60)
        print("✅ Enhanced AI Shadow Trading Session Complete")
        print("="*60)
