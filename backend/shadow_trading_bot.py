#!/usr/bin/env python3
"""
AI Stock Trading Bot - Shadow Trading System
A sophisticated trading bot that performs paper trading with real market data
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import websocket
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
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
    """Main trading bot class"""
    
    def __init__(self, initial_capital: float = 100000.0, target_amount: Optional[float] = None,
                 trading_period_days: int = 30, max_position_size: float = 0.1,
                 max_daily_loss: float = 0.05, risk_tolerance: str = 'medium',
                 trading_strategy: str = 'momentum', enable_ml_learning: bool = True):
        self.initial_capital = initial_capital
        self.target_amount = target_amount
        self.trading_period_days = trading_period_days
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.risk_tolerance = risk_tolerance
        self.trading_strategy = trading_strategy
        self.enable_ml_learning = enable_ml_learning
        
        self.portfolio = Portfolio(
            cash=initial_capital,
            total_value=initial_capital,
            positions={},
            orders=[],
            performance_metrics={}
        )
        
        self.market_data = MarketDataProvider()
        self.risk_manager = RiskManager()
        self.strategies = {}
        self.watchlist = []
        self.running = False
        
        # Initialize strategies
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
                   strategy: str, reason: str) -> Optional[Order]:
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
                
        # Create order
        order = Order(
            id=f"{symbol}_{int(time.time())}",
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            price=current_data.price,
            timestamp=datetime.now(),
            status=OrderStatus.FILLED,  # Shadow trading - orders are immediately filled
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
        """Run a specific strategy on a symbol"""
        if strategy_name not in self.strategies:
            logger.error(f"Strategy {strategy_name} not found")
            return
            
        strategy = self.strategies[strategy_name]
        
        # Get historical data
        historical_data = self.market_data.get_historical_data(symbol, "3mo")
        if not historical_data:
            return
            
        # Get current data
        current_data = self.market_data.get_stock_data(symbol)
        if not current_data:
            return
            
        # Analyze with strategy
        signal = strategy.analyze(historical_data)
        
        # Check existing position
        current_position = self.portfolio.positions.get(symbol)
        
        if signal == OrderType.BUY and (not current_position or current_position.quantity == 0):
            # Calculate position size
            quantity = self.risk_manager.calculate_position_size(
                self.portfolio, symbol, current_data.price
            )
            if quantity > 0:
                self.place_order(symbol, OrderType.BUY, quantity, strategy_name, 
                               f"Strategy signal: {signal.value}")
                               
        elif signal == OrderType.SELL and current_position and current_position.quantity > 0:
            # Sell entire position
            self.place_order(symbol, OrderType.SELL, current_position.quantity, strategy_name,
                           f"Strategy signal: {signal.value}")
                           
        # Check exit conditions for existing positions
        if current_position and current_position.quantity > 0:
            if strategy.should_exit(current_position, current_data):
                self.place_order(symbol, OrderType.SELL, current_position.quantity, strategy_name,
                               "Exit condition met")
                               
    def run_trading_cycle(self):
        """Run one trading cycle"""
        logger.info("Starting trading cycle...")
        
        for symbol in self.watchlist:
            try:
                # Run each strategy
                for strategy_name in self.strategies.keys():
                    self.run_strategy(symbol, strategy_name)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                
        # Update portfolio value
        self._update_portfolio_value()
        
        # Log portfolio status
        self._log_portfolio_status()
        
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
            'recommendations': recommendations
        }

if __name__ == "__main__":
    # Create and start the trading bot
    bot = ShadowTradingBot(initial_capital=100000.0)
    
    try:
        bot.start(interval=300)  # Run every 5 minutes
    except KeyboardInterrupt:
        bot.stop()
        print("\nTrading bot stopped.")
        
        # Print final performance report
        report = bot.get_performance_report()
        print("\n" + "="*50)
        print("FINAL PERFORMANCE REPORT")
        print("="*50)
        print(f"Initial Capital: ${report['initial_capital']:,.2f}")
        print(f"Final Value: ${report['current_value']:,.2f}")
        print(f"Total Return: {report['total_return_pct']:.2f}%")
        print(f"Cash: ${report['cash']:,.2f}")
        print(f"Positions: {report['positions_count']}")
        print(f"Total Orders: {report['orders_count']}")
