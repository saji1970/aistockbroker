#!/usr/bin/env python3
"""
Robo Trading Agent - Shadow Trading System
A sophisticated AI-powered trading agent that performs shadow trading with profit targets.
Supports stocks, crypto, and other day trading instruments.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random
import math
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingStatus(Enum):
    """Trading status enumeration."""
    IDLE = "idle"
    MONITORING = "monitoring"
    BUYING = "buying"
    SELLING = "selling"
    TARGET_REACHED = "target_reached"
    STOPPED = "stopped"
    ERROR = "error"

class AssetType(Enum):
    """Asset type enumeration."""
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"
    ETF = "etf"

class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"

@dataclass
class MarketData:
    """Market data structure."""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    bid: float
    ask: float
    high: float
    low: float
    change: float
    change_percent: float

@dataclass
class Order:
    """Order structure."""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    timestamp: datetime
    status: str
    filled_quantity: float = 0.0
    average_price: float = 0.0

@dataclass
class Position:
    """Position structure."""
    symbol: str
    quantity: float
    average_price: float
    current_value: float
    unrealized_pnl: float
    realized_pnl: float
    timestamp: datetime

@dataclass
class TradingTask:
    """Trading task structure."""
    id: str
    initial_capital: float
    target_amount: float
    target_profit_percent: float
    asset_type: AssetType
    symbols: List[str]
    start_time: datetime
    end_time: datetime
    risk_tolerance: str  # low, medium, high
    max_position_size: float
    stop_loss_percent: float
    take_profit_percent: float
    status: TradingStatus
    current_balance: float
    total_pnl: float
    trades_count: int
    success_rate: float

class MarketDataProvider:
    """Mock market data provider for demonstration."""
    
    def __init__(self):
        self.base_prices = {
            'AAPL': 150.0,
            'TSLA': 245.0,
            'MSFT': 380.0,
            'GOOGL': 145.0,
            'NVDA': 485.0,
            'BTC': 45000.0,
            'ETH': 2800.0,
            'SOL': 95.0,
            'ADA': 0.45,
            'DOT': 6.8
        }
        self.volatility = {
            'AAPL': 0.02,
            'TSLA': 0.05,
            'MSFT': 0.015,
            'GOOGL': 0.025,
            'NVDA': 0.04,
            'BTC': 0.03,
            'ETH': 0.035,
            'SOL': 0.06,
            'ADA': 0.08,
            'DOT': 0.045
        }
    
    def get_market_data(self, symbol: str) -> MarketData:
        """Get current market data for a symbol."""
        base_price = self.base_prices.get(symbol, 100.0)
        volatility = self.volatility.get(symbol, 0.02)
        
        # Simulate price movement
        change_percent = random.uniform(-volatility, volatility)
        current_price = base_price * (1 + change_percent)
        
        # Update base price for next iteration
        self.base_prices[symbol] = current_price
        
        bid = current_price * 0.999
        ask = current_price * 1.001
        
        return MarketData(
            symbol=symbol,
            price=current_price,
            volume=random.uniform(1000000, 10000000),
            timestamp=datetime.now(),
            bid=bid,
            ask=ask,
            high=current_price * 1.02,
            low=current_price * 0.98,
            change=current_price - base_price,
            change_percent=change_percent * 100
        )

class TechnicalAnalyzer:
    """Technical analysis component."""
    
    def __init__(self):
        self.price_history = {}
        self.indicators = {}
    
    def add_price_data(self, symbol: str, price: float, timestamp: datetime):
        """Add price data to history."""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': timestamp
        })
        
        # Keep only last 100 data points
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def calculate_rsi(self, symbol: str, period: int = 14) -> Optional[float]:
        """Calculate RSI indicator."""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period + 1:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol][-period-1:]]
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if not gains or not losses:
            return 50.0
        
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_moving_average(self, symbol: str, period: int = 20) -> Optional[float]:
        """Calculate simple moving average."""
        if symbol not in self.price_history or len(self.price_history[symbol]) < period:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol][-period:]]
        return sum(prices) / len(prices)
    
    def get_trading_signals(self, symbol: str) -> Dict[str, Any]:
        """Get trading signals based on technical indicators."""
        rsi = self.calculate_rsi(symbol)
        sma_20 = self.calculate_moving_average(symbol, 20)
        sma_50 = self.calculate_moving_average(symbol, 50)
        
        current_price = self.price_history[symbol][-1]['price'] if symbol in self.price_history else None
        
        signals = {
            'rsi': rsi,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'current_price': current_price,
            'rsi_signal': 'neutral',
            'ma_signal': 'neutral',
            'overall_signal': 'neutral'
        }
        
        if rsi is not None:
            if rsi < 30:
                signals['rsi_signal'] = 'oversold'
            elif rsi > 70:
                signals['rsi_signal'] = 'overbought'
            else:
                signals['rsi_signal'] = 'neutral'
        
        if sma_20 is not None and sma_50 is not None and current_price is not None:
            if current_price > sma_20 > sma_50:
                signals['ma_signal'] = 'bullish'
            elif current_price < sma_20 < sma_50:
                signals['ma_signal'] = 'bearish'
            else:
                signals['ma_signal'] = 'neutral'
        
        # Determine overall signal
        if signals['rsi_signal'] == 'oversold' and signals['ma_signal'] == 'bullish':
            signals['overall_signal'] = 'strong_buy'
        elif signals['rsi_signal'] == 'overbought' and signals['ma_signal'] == 'bearish':
            signals['overall_signal'] = 'strong_sell'
        elif signals['rsi_signal'] == 'oversold' or signals['ma_signal'] == 'bullish':
            signals['overall_signal'] = 'buy'
        elif signals['rsi_signal'] == 'overbought' or signals['ma_signal'] == 'bearish':
            signals['overall_signal'] = 'sell'
        
        return signals

class RoboTradingAgent:
    """Main robo trading agent class."""
    
    def __init__(self, name: str = "RoboTrader"):
        self.name = name
        self.market_data_provider = MarketDataProvider()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # Trading state
        self.tasks: Dict[str, TradingTask] = {}
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.trade_history: List[Dict] = []
        
        # Configuration
        self.max_concurrent_tasks = 5
        self.min_trade_amount = 10.0
        self.max_trade_amount = 1000.0
        self.default_commission = 0.001  # 0.1%
        
        # Performance tracking
        self.total_trades = 0
        self.successful_trades = 0
        self.total_pnl = 0.0
        
        logger.info(f"🤖 {self.name} initialized successfully")
    
    def create_trading_task(self, 
                           initial_capital: float,
                           target_amount: float,
                           asset_type: AssetType,
                           symbols: List[str],
                           duration_hours: int = 8,
                           risk_tolerance: str = "medium") -> str:
        """Create a new trading task."""
        
        if len(self.tasks) >= self.max_concurrent_tasks:
            raise ValueError("Maximum number of concurrent tasks reached")
        
        task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        target_profit_percent = ((target_amount - initial_capital) / initial_capital) * 100
        
        # Calculate position sizing based on risk tolerance
        if risk_tolerance == "low":
            max_position_size = initial_capital * 0.1
            stop_loss_percent = 2.0
            take_profit_percent = 3.0
        elif risk_tolerance == "high":
            max_position_size = initial_capital * 0.5
            stop_loss_percent = 5.0
            take_profit_percent = 8.0
        else:  # medium
            max_position_size = initial_capital * 0.25
            stop_loss_percent = 3.0
            take_profit_percent = 5.0
        
        task = TradingTask(
            id=task_id,
            initial_capital=initial_capital,
            target_amount=target_amount,
            target_profit_percent=target_profit_percent,
            asset_type=asset_type,
            symbols=symbols,
            start_time=start_time,
            end_time=end_time,
            risk_tolerance=risk_tolerance,
            max_position_size=max_position_size,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent,
            status=TradingStatus.IDLE,
            current_balance=initial_capital,
            total_pnl=0.0,
            trades_count=0,
            success_rate=0.0
        )
        
        self.tasks[task_id] = task
        logger.info(f"📋 Created trading task {task_id}: ${initial_capital} → ${target_amount} ({target_profit_percent:.1f}%)")
        
        return task_id
    
    def start_task(self, task_id: str):
        """Start a trading task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TradingStatus.MONITORING
        
        logger.info(f"🚀 Started trading task {task_id}")
        logger.info(f"💰 Target: ${task.initial_capital} → ${task.target_amount}")
        logger.info(f"📊 Symbols: {', '.join(task.symbols)}")
        logger.info(f"⏰ Duration: {task.start_time} to {task.end_time}")
    
    def stop_task(self, task_id: str):
        """Stop a trading task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = TradingStatus.STOPPED
        
        # Close all positions
        for symbol in list(self.positions.keys()):
            if symbol in task.symbols:
                self._close_position(symbol, task_id)
        
        logger.info(f"🛑 Stopped trading task {task_id}")
    
    def get_task_status(self, task_id: str) -> Optional[TradingTask]:
        """Get task status."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[TradingTask]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def execute_trading_cycle(self, task_id: str):
        """Execute one trading cycle for a task."""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        
        if task.status != TradingStatus.MONITORING:
            return
        
        # Check if target reached
        if task.current_balance >= task.target_amount:
            task.status = TradingStatus.TARGET_REACHED
            logger.info(f"🎯 Target reached for task {task_id}: ${task.current_balance:.2f}")
            return
        
        # Check if time expired
        if datetime.now() > task.end_time:
            task.status = TradingStatus.STOPPED
            logger.info(f"⏰ Time expired for task {task_id}")
            return
        
        # Analyze each symbol
        for symbol in task.symbols:
            try:
                self._analyze_and_trade(symbol, task_id)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
    
    def _analyze_and_trade(self, symbol: str, task_id: str):
        """Analyze market data and execute trades."""
        task = self.tasks[task_id]
        
        # Get market data
        market_data = self.market_data_provider.get_market_data(symbol)
        
        # Add to technical analyzer
        self.technical_analyzer.add_price_data(symbol, market_data.price, market_data.timestamp)
        
        # Get technical signals
        signals = self.technical_analyzer.get_trading_signals(symbol)
        
        # Check current position
        current_position = self.positions.get(symbol)
        
        # Decision making logic
        if current_position is None:
            # No position - look for entry
            if signals['overall_signal'] in ['buy', 'strong_buy']:
                self._execute_buy_order(symbol, task_id, market_data, signals)
        else:
            # Have position - check exit conditions
            self._check_exit_conditions(symbol, task_id, market_data, signals)
    
    def _execute_buy_order(self, symbol: str, task_id: str, market_data: MarketData, signals: Dict):
        """Execute a buy order."""
        task = self.tasks[task_id]
        
        # Calculate position size
        available_capital = task.current_balance
        max_position_value = min(task.max_position_size, available_capital * 0.8)
        
        if max_position_value < self.min_trade_amount:
            return
        
        # Calculate quantity
        quantity = max_position_value / market_data.price
        quantity = round(quantity, 6)  # Round to 6 decimal places
        
        if quantity <= 0:
            return
        
        # Create order
        order_id = f"order_{int(time.time())}_{random.randint(1000, 9999)}"
        order = Order(
            id=order_id,
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=quantity,
            price=market_data.price,
            timestamp=datetime.now(),
            status="filled",
            filled_quantity=quantity,
            average_price=market_data.price
        )
        
        # Execute order
        commission = max_position_value * self.default_commission
        total_cost = max_position_value + commission
        
        if total_cost <= task.current_balance:
            # Update task balance
            task.current_balance -= total_cost
            task.trades_count += 1
            
            # Create position
            position = Position(
                symbol=symbol,
                quantity=quantity,
                average_price=market_data.price,
                current_value=quantity * market_data.price,
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                timestamp=datetime.now()
            )
            
            self.positions[symbol] = position
            self.orders[order_id] = order
            
            # Log trade
            trade_log = {
                'task_id': task_id,
                'order_id': order_id,
                'symbol': symbol,
                'side': 'buy',
                'quantity': quantity,
                'price': market_data.price,
                'value': max_position_value,
                'commission': commission,
                'timestamp': datetime.now(),
                'signals': signals
            }
            self.trade_history.append(trade_log)
            
            logger.info(f"📈 BUY {symbol}: {quantity:.6f} @ ${market_data.price:.2f} (${max_position_value:.2f})")
            logger.info(f"💰 Task {task_id} balance: ${task.current_balance:.2f}")
    
    def _check_exit_conditions(self, symbol: str, task_id: str, market_data: MarketData, signals: Dict):
        """Check exit conditions for existing position."""
        task = self.tasks[task_id]
        position = self.positions[symbol]
        
        # Calculate current P&L
        current_value = position.quantity * market_data.price
        unrealized_pnl = current_value - (position.quantity * position.average_price)
        unrealized_pnl_percent = (unrealized_pnl / (position.quantity * position.average_price)) * 100
        
        # Update position
        position.current_value = current_value
        position.unrealized_pnl = unrealized_pnl
        
        # Check exit conditions
        should_exit = False
        exit_reason = ""
        
        # Take profit
        if unrealized_pnl_percent >= task.take_profit_percent:
            should_exit = True
            exit_reason = "take_profit"
        
        # Stop loss
        elif unrealized_pnl_percent <= -task.stop_loss_percent:
            should_exit = True
            exit_reason = "stop_loss"
        
        # Technical signal
        elif signals['overall_signal'] in ['sell', 'strong_sell']:
            should_exit = True
            exit_reason = "technical_signal"
        
        # Target reached
        elif task.current_balance + current_value >= task.target_amount:
            should_exit = True
            exit_reason = "target_reached"
        
        if should_exit:
            self._execute_sell_order(symbol, task_id, market_data, exit_reason)
    
    def _execute_sell_order(self, symbol: str, task_id: str, market_data: MarketData, exit_reason: str):
        """Execute a sell order."""
        task = self.tasks[task_id]
        position = self.positions[symbol]
        
        # Create order
        order_id = f"order_{int(time.time())}_{random.randint(1000, 9999)}"
        order = Order(
            id=order_id,
            symbol=symbol,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=position.quantity,
            price=market_data.price,
            timestamp=datetime.now(),
            status="filled",
            filled_quantity=position.quantity,
            average_price=market_data.price
        )
        
        # Calculate proceeds
        gross_proceeds = position.quantity * market_data.price
        commission = gross_proceeds * self.default_commission
        net_proceeds = gross_proceeds - commission
        
        # Calculate P&L
        realized_pnl = net_proceeds - (position.quantity * position.average_price)
        
        # Update task
        task.current_balance += net_proceeds
        task.total_pnl += realized_pnl
        task.trades_count += 1
        
        # Update success rate
        if realized_pnl > 0:
            self.successful_trades += 1
        self.total_trades += 1
        task.success_rate = (self.successful_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        
        # Remove position
        del self.positions[symbol]
        self.orders[order_id] = order
        
        # Log trade
        trade_log = {
            'task_id': task_id,
            'order_id': order_id,
            'symbol': symbol,
            'side': 'sell',
            'quantity': position.quantity,
            'price': market_data.price,
            'value': gross_proceeds,
            'commission': commission,
            'pnl': realized_pnl,
            'exit_reason': exit_reason,
            'timestamp': datetime.now()
        }
        self.trade_history.append(trade_log)
        
        logger.info(f"📉 SELL {symbol}: {position.quantity:.6f} @ ${market_data.price:.2f} (${gross_proceeds:.2f})")
        logger.info(f"💰 P&L: ${realized_pnl:.2f} | Task balance: ${task.current_balance:.2f}")
        logger.info(f"🎯 Exit reason: {exit_reason}")
    
    def _close_position(self, symbol: str, task_id: str):
        """Close a position at market price."""
        if symbol not in self.positions:
            return
        
        market_data = self.market_data_provider.get_market_data(symbol)
        self._execute_sell_order(symbol, task_id, market_data, "force_close")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        total_initial_capital = sum(task.initial_capital for task in self.tasks.values())
        total_current_balance = sum(task.current_balance for task in self.tasks.values())
        total_pnl = total_current_balance - total_initial_capital
        
        return {
            'total_tasks': len(self.tasks),
            'active_tasks': len([t for t in self.tasks.values() if t.status == TradingStatus.MONITORING]),
            'completed_tasks': len([t for t in self.tasks.values() if t.status in [TradingStatus.TARGET_REACHED, TradingStatus.STOPPED]]),
            'total_initial_capital': total_initial_capital,
            'total_current_balance': total_current_balance,
            'total_pnl': total_pnl,
            'total_return_percent': (total_pnl / total_initial_capital * 100) if total_initial_capital > 0 else 0,
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0,
            'open_positions': len(self.positions),
            'trade_history_count': len(self.trade_history)
        }
    
    def get_detailed_report(self, task_id: str) -> Dict[str, Any]:
        """Get detailed report for a specific task."""
        if task_id not in self.tasks:
            return {}
        
        task = self.tasks[task_id]
        task_trades = [t for t in self.trade_history if t['task_id'] == task_id]
        
        return {
            'task_info': asdict(task),
            'trades': task_trades,
            'current_positions': [asdict(p) for p in self.positions.values() if p.symbol in task.symbols],
            'performance_metrics': {
                'total_trades': len(task_trades),
                'buy_trades': len([t for t in task_trades if t['side'] == 'buy']),
                'sell_trades': len([t for t in task_trades if t['side'] == 'sell']),
                'total_commission': sum(t.get('commission', 0) for t in task_trades),
                'avg_trade_size': sum(t.get('value', 0) for t in task_trades) / len(task_trades) if task_trades else 0
            }
        }

# Example usage and demonstration
async def demonstrate_robo_trading():
    """Demonstrate the robo trading agent capabilities."""
    
    print("🤖 Robo Trading Agent Demonstration")
    print("=" * 50)
    
    # Initialize agent
    agent = RoboTradingAgent("DemoTrader")
    
    # Create trading tasks
    print("\n📋 Creating Trading Tasks:")
    
    # Task 1: Stock trading - $100 to $110
    task1_id = agent.create_trading_task(
        initial_capital=100.0,
        target_amount=110.0,
        asset_type=AssetType.STOCK,
        symbols=['AAPL', 'TSLA', 'MSFT'],
        duration_hours=8,
        risk_tolerance="medium"
    )
    
    # Task 2: Crypto trading - $200 to $220
    task2_id = agent.create_trading_task(
        initial_capital=200.0,
        target_amount=220.0,
        asset_type=AssetType.CRYPTO,
        symbols=['BTC', 'ETH', 'SOL'],
        duration_hours=6,
        risk_tolerance="high"
    )
    
    # Start tasks
    agent.start_task(task1_id)
    agent.start_task(task2_id)
    
    print(f"✅ Created and started 2 trading tasks")
    print(f"📊 Task 1: ${100} → ${110} (Stocks)")
    print(f"📊 Task 2: ${200} → ${220} (Crypto)")
    
    # Simulate trading cycles
    print("\n🔄 Simulating Trading Cycles:")
    
    for cycle in range(20):
        print(f"\n--- Cycle {cycle + 1} ---")
        
        # Execute trading cycles
        agent.execute_trading_cycle(task1_id)
        agent.execute_trading_cycle(task2_id)
        
        # Get task status
        task1 = agent.get_task_status(task1_id)
        task2 = agent.get_task_status(task2_id)
        
        print(f"Task 1: ${task1.current_balance:.2f} / ${task1.target_amount:.2f} ({task1.status.value})")
        print(f"Task 2: ${task2.current_balance:.2f} / ${task2.target_amount:.2f} ({task2.status.value})")
        
        # Check if targets reached
        if task1.status == TradingStatus.TARGET_REACHED and task2.status == TradingStatus.TARGET_REACHED:
            print("🎯 Both targets reached!")
            break
        
        # Simulate time passing
        await asyncio.sleep(0.1)
    
    # Get final performance
    print("\n📊 Final Performance Summary:")
    performance = agent.get_performance_summary()
    
    for key, value in performance.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Get detailed reports
    print(f"\n📋 Detailed Task Reports:")
    report1 = agent.get_detailed_report(task1_id)
    report2 = agent.get_detailed_report(task2_id)
    
    print(f"Task 1 Trades: {len(report1.get('trades', []))}")
    print(f"Task 2 Trades: {len(report2.get('trades', []))}")
    
    print("\n🎉 Robo Trading Agent Demonstration Complete!")

if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_robo_trading())
