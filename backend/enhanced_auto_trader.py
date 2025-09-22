#!/usr/bin/env python3
"""
Enhanced Auto Trader - Real Day Trading System
A sophisticated AI-powered automated trading system that monitors markets,
analyzes opportunities, and executes trades to achieve target goals.
"""

import asyncio
import json
import logging
import time
import threading
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
    ANALYZING = "analyzing"
    BUYING = "buying"
    SELLING = "selling"
    TARGET_REACHED = "target_reached"
    STOPPED = "stopped"
    ERROR = "error"
    PAUSED = "paused"

class TradingStrategy(Enum):
    """Trading strategy enumeration."""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    SWING = "swing"
    AI_DRIVEN = "ai_driven"

class MarketCondition(Enum):
    """Market condition enumeration."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    TRENDING = "trending"

@dataclass
class TradingGoal:
    """Trading goal configuration."""
    target_profit_percentage: float = 10.0  # Target profit as percentage
    target_profit_amount: float = 0.0  # Target profit as dollar amount
    max_daily_loss_percentage: float = 5.0  # Max daily loss as percentage
    max_position_size_percentage: float = 20.0  # Max position size as percentage of portfolio
    min_trade_amount: float = 100.0  # Minimum trade amount
    max_trade_amount: float = 5000.0  # Maximum trade amount
    trading_hours_start: str = "09:30"  # Market open time
    trading_hours_end: str = "16:00"  # Market close time
    max_trades_per_day: int = 50  # Maximum trades per day
    stop_loss_percentage: float = 2.0  # Stop loss percentage
    take_profit_percentage: float = 3.0  # Take profit percentage

@dataclass
class TradingSignal:
    """Trading signal data."""
    symbol: str
    signal_type: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 to 1.0
    price: float
    quantity: float
    reasoning: str
    strategy: str
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class TradingSession:
    """Trading session data."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: TradingStatus
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_profit: float
    total_volume: float
    symbols_traded: List[str]
    current_positions: Dict[str, float]

class EnhancedAutoTrader:
    """Enhanced automated trading system."""
    
    def __init__(self, portfolio_manager, ai_predictor=None, data_fetcher=None):
        """
        Initialize the enhanced auto trader.
        
        Args:
            portfolio_manager: Enhanced portfolio manager instance
            ai_predictor: AI predictor for market analysis
            data_fetcher: Data fetcher for real-time market data
        """
        self.portfolio_manager = portfolio_manager
        self.ai_predictor = ai_predictor
        self.data_fetcher = data_fetcher
        
        # Trading configuration
        self.goal = TradingGoal()
        self.strategy = TradingStrategy.AI_DRIVEN
        self.status = TradingStatus.IDLE
        
        # Trading state
        self.current_session: Optional[TradingSession] = None
        self.trading_signals: List[TradingSignal] = []
        self.watchlist: List[str] = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX', 'PLTR', 'BBAI']
        self.active_positions: Dict[str, Dict] = {}
        
        # Performance tracking
        self.daily_stats = {
            'trades_executed': 0,
            'total_profit': 0.0,
            'winning_trades': 0,
            'losing_trades': 0,
            'volume_traded': 0.0,
            'start_balance': 0.0,
            'current_balance': 0.0
        }
        
        # Risk management
        self.risk_metrics = {
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0
        }
        
        # Trading loop control
        self.trading_active = False
        self.trading_thread: Optional[threading.Thread] = None
        self.analysis_interval = 30  # seconds between market analysis
        
        logger.info("Enhanced Auto Trader initialized")

    def configure_trading_goal(self, goal_config: Dict[str, Any]) -> bool:
        """Configure trading goals and parameters."""
        try:
            for key, value in goal_config.items():
                if hasattr(self.goal, key):
                    setattr(self.goal, key, value)
            
            logger.info(f"Trading goal configured: {asdict(self.goal)}")
            return True
        except Exception as e:
            logger.error(f"Error configuring trading goal: {e}")
            return False

    def set_watchlist(self, symbols: List[str]) -> bool:
        """Set the list of symbols to monitor and trade."""
        try:
            self.watchlist = symbols
            logger.info(f"Watchlist updated: {self.watchlist}")
            return True
        except Exception as e:
            logger.error(f"Error setting watchlist: {e}")
            return False

    def start_trading(self) -> bool:
        """Start the automated trading system."""
        try:
            if self.status == TradingStatus.MONITORING:
                logger.warning("Trading already active")
                return False
            
            # Initialize trading session
            self.current_session = TradingSession(
                session_id=f"session_{int(time.time())}",
                start_time=datetime.now(),
                end_time=None,
                status=TradingStatus.MONITORING,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                total_profit=0.0,
                total_volume=0.0,
                symbols_traded=[],
                current_positions={}
            )
            
            # Get initial portfolio balance
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            self.daily_stats['start_balance'] = portfolio_summary['total_value']
            self.daily_stats['current_balance'] = portfolio_summary['total_value']
            
            # Start trading loop
            self.trading_active = True
            self.status = TradingStatus.MONITORING
            self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
            self.trading_thread.start()
            
            logger.info("Automated trading started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting trading: {e}")
            self.status = TradingStatus.ERROR
            return False

    def stop_trading(self) -> bool:
        """Stop the automated trading system."""
        try:
            self.trading_active = False
            self.status = TradingStatus.STOPPED
            
            if self.current_session:
                self.current_session.end_time = datetime.now()
                self.current_session.status = TradingStatus.STOPPED
            
            logger.info("Automated trading stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping trading: {e}")
            return False

    def pause_trading(self) -> bool:
        """Pause the automated trading system."""
        try:
            self.status = TradingStatus.PAUSED
            logger.info("Automated trading paused")
            return True
        except Exception as e:
            logger.error(f"Error pausing trading: {e}")
            return False

    def resume_trading(self) -> bool:
        """Resume the automated trading system."""
        try:
            if self.trading_active:
                self.status = TradingStatus.MONITORING
                logger.info("Automated trading resumed")
                return True
            else:
                logger.warning("Cannot resume - trading not active")
                return False
        except Exception as e:
            logger.error(f"Error resuming trading: {e}")
            return False

    def _trading_loop(self):
        """Main trading loop that runs continuously."""
        logger.info("Trading loop started")
        
        while self.trading_active:
            try:
                if self.status == TradingStatus.MONITORING:
                    # Check if we should be trading (market hours)
                    if self._is_market_hours():
                        # Analyze market and generate signals
                        self._analyze_market()
                        
                        # Execute trades based on signals
                        self._execute_trading_signals()
                        
                        # Update performance metrics
                        self._update_performance_metrics()
                        
                        # Check if target reached
                        if self._is_target_reached():
                            self.status = TradingStatus.TARGET_REACHED
                            logger.info("Trading target reached!")
                            break
                        
                        # Check risk limits
                        if self._is_risk_limit_exceeded():
                            self.status = TradingStatus.STOPPED
                            logger.warning("Risk limits exceeded - stopping trading")
                            break
                
                # Wait before next analysis
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                self.status = TradingStatus.ERROR
                break
        
        logger.info("Trading loop ended")

    def _is_market_hours(self) -> bool:
        """Check if current time is within trading hours."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Simple market hours check (9:30 AM to 4:00 PM EST)
        return self.goal.trading_hours_start <= current_time <= self.goal.trading_hours_end

    def _analyze_market(self):
        """Analyze market conditions and generate trading signals."""
        try:
            logger.info("Analyzing market conditions...")
            
            for symbol in self.watchlist:
                # Get current market data
                current_price = self.portfolio_manager.get_current_price(symbol)
                if not current_price:
                    continue
                
                # Generate trading signal
                signal = self._generate_trading_signal(symbol, current_price)
                if signal and signal.confidence > 0.6:  # Only high-confidence signals
                    self.trading_signals.append(signal)
                    logger.info(f"Generated {signal.signal_type} signal for {symbol} with {signal.confidence:.2f} confidence")
            
        except Exception as e:
            logger.error(f"Error analyzing market: {e}")

    def _generate_trading_signal(self, symbol: str, current_price: float) -> Optional[TradingSignal]:
        """Generate trading signal for a symbol."""
        try:
            # Get AI prediction if available
            ai_prediction = None
            if self.ai_predictor:
                try:
                    prediction_data = self.ai_predictor.get_stock_prediction(symbol)
                    if prediction_data and 'prediction' in prediction_data:
                        ai_prediction = prediction_data['prediction']
                except Exception as e:
                    logger.warning(f"AI prediction failed for {symbol}: {e}")
            
            # Get technical analysis
            technical_signals = self._get_technical_signals(symbol, current_price)
            
            # Combine AI and technical analysis
            signal_type, confidence, reasoning = self._combine_signals(
                symbol, current_price, ai_prediction, technical_signals
            )
            
            if signal_type == "HOLD":
                return None
            
            # Calculate position size
            quantity = self._calculate_position_size(symbol, current_price, signal_type)
            
            # Calculate stop loss and take profit
            stop_loss, take_profit = self._calculate_stop_loss_take_profit(
                current_price, signal_type
            )
            
            return TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                price=current_price,
                quantity=quantity,
                reasoning=reasoning,
                strategy=self.strategy.value,
                timestamp=datetime.now(),
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None

    def _get_technical_signals(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """Get technical analysis signals."""
        try:
            # Get historical data for technical analysis
            if self.data_fetcher:
                data = self.data_fetcher.fetch_stock_data(symbol, period="5d")
                if data is not None and not data.empty:
                    # Simple technical indicators
                    prices = data['Close'].values
                    
                    # Moving averages
                    sma_20 = prices[-20:].mean() if len(prices) >= 20 else prices.mean()
                    sma_50 = prices[-50:].mean() if len(prices) >= 50 else prices.mean()
                    
                    # Price momentum
                    price_change = (current_price - prices[-1]) / prices[-1] if len(prices) > 0 else 0
                    
                    # Volume analysis
                    volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else 1000000
                    avg_volume = data['Volume'].mean() if 'Volume' in data.columns else 1000000
                    volume_ratio = volume / avg_volume if avg_volume > 0 else 1
                    
                    return {
                        'sma_20': sma_20,
                        'sma_50': sma_50,
                        'price_change': price_change,
                        'volume_ratio': volume_ratio,
                        'current_price': current_price
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting technical signals for {symbol}: {e}")
            return {}

    def _combine_signals(self, symbol: str, current_price: float, 
                        ai_prediction: Optional[str], technical_signals: Dict[str, Any]) -> Tuple[str, float, str]:
        """Combine AI and technical signals to generate final trading decision."""
        try:
            buy_score = 0.0
            sell_score = 0.0
            reasoning_parts = []
            
            # AI prediction analysis
            if ai_prediction:
                if "buy" in ai_prediction.lower() or "bullish" in ai_prediction.lower():
                    buy_score += 0.3
                    reasoning_parts.append("AI suggests bullish trend")
                elif "sell" in ai_prediction.lower() or "bearish" in ai_prediction.lower():
                    sell_score += 0.3
                    reasoning_parts.append("AI suggests bearish trend")
            
            # Technical analysis
            if technical_signals:
                sma_20 = technical_signals.get('sma_20', current_price)
                sma_50 = technical_signals.get('sma_50', current_price)
                price_change = technical_signals.get('price_change', 0)
                volume_ratio = technical_signals.get('volume_ratio', 1)
                
                # Moving average signals
                if current_price > sma_20 > sma_50:
                    buy_score += 0.2
                    reasoning_parts.append("Price above moving averages")
                elif current_price < sma_20 < sma_50:
                    sell_score += 0.2
                    reasoning_parts.append("Price below moving averages")
                
                # Momentum signals
                if price_change > 0.02:  # 2% positive change
                    buy_score += 0.2
                    reasoning_parts.append("Strong positive momentum")
                elif price_change < -0.02:  # 2% negative change
                    sell_score += 0.2
                    reasoning_parts.append("Strong negative momentum")
                
                # Volume confirmation
                if volume_ratio > 1.5:
                    buy_score += 0.1
                    reasoning_parts.append("High volume confirmation")
                elif volume_ratio < 0.5:
                    sell_score += 0.1
                    reasoning_parts.append("Low volume - weak signal")
            
            # Random factor for diversification (small impact)
            random_factor = random.uniform(-0.1, 0.1)
            buy_score += random_factor
            sell_score -= random_factor
            
            # Determine final signal
            if buy_score > sell_score and buy_score > 0.6:
                return "BUY", buy_score, "; ".join(reasoning_parts)
            elif sell_score > buy_score and sell_score > 0.6:
                return "SELL", sell_score, "; ".join(reasoning_parts)
            else:
                return "HOLD", max(buy_score, sell_score), "No clear signal"
                
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return "HOLD", 0.0, "Error in signal analysis"

    def _calculate_position_size(self, symbol: str, current_price: float, signal_type: str) -> float:
        """Calculate appropriate position size for a trade."""
        try:
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            available_cash = portfolio_summary['available_cash']
            
            # Calculate position size based on available cash and risk parameters
            max_position_value = available_cash * (self.goal.max_position_size_percentage / 100)
            
            # Ensure within trade amount limits
            position_value = min(max_position_value, self.goal.max_trade_amount)
            position_value = max(position_value, self.goal.min_trade_amount)
            
            # Calculate quantity
            quantity = position_value / current_price
            
            # Round to whole shares
            return math.floor(quantity)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0

    def _calculate_stop_loss_take_profit(self, current_price: float, signal_type: str) -> Tuple[Optional[float], Optional[float]]:
        """Calculate stop loss and take profit levels."""
        try:
            if signal_type == "BUY":
                stop_loss = current_price * (1 - self.goal.stop_loss_percentage / 100)
                take_profit = current_price * (1 + self.goal.take_profit_percentage / 100)
            elif signal_type == "SELL":
                stop_loss = current_price * (1 + self.goal.stop_loss_percentage / 100)
                take_profit = current_price * (1 - self.goal.take_profit_percentage / 100)
            else:
                return None, None
            
            return stop_loss, take_profit
            
        except Exception as e:
            logger.error(f"Error calculating stop loss/take profit: {e}")
            return None, None

    def _execute_trading_signals(self):
        """Execute trading signals."""
        try:
            for signal in self.trading_signals[:]:  # Copy list to avoid modification during iteration
                if self._should_execute_signal(signal):
                    success = self._execute_signal(signal)
                    if success:
                        self.trading_signals.remove(signal)
                        self.daily_stats['trades_executed'] += 1
                        
                        # Update session stats
                        if self.current_session:
                            self.current_session.total_trades += 1
                            if signal.symbol not in self.current_session.symbols_traded:
                                self.current_session.symbols_traded.append(signal.symbol)
            
        except Exception as e:
            logger.error(f"Error executing trading signals: {e}")

    def _should_execute_signal(self, signal: TradingSignal) -> bool:
        """Check if a signal should be executed."""
        try:
            # Check if we've reached daily trade limit
            if self.daily_stats['trades_executed'] >= self.goal.max_trades_per_day:
                return False
            
            # Check if we have enough cash for buy signals
            if signal.signal_type == "BUY":
                portfolio_summary = self.portfolio_manager.get_portfolio_summary()
                required_cash = signal.price * signal.quantity
                if required_cash > portfolio_summary['available_cash']:
                    return False
            
            # Check if we have position for sell signals
            if signal.signal_type == "SELL":
                portfolio_summary = self.portfolio_manager.get_portfolio_summary()
                asset_performance = self.portfolio_manager.get_asset_performance(signal.symbol)
                if not asset_performance or asset_performance['quantity'] < signal.quantity:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking signal execution: {e}")
            return False

    def _execute_signal(self, signal: TradingSignal) -> bool:
        """Execute a trading signal."""
        try:
            logger.info(f"Executing {signal.signal_type} signal for {signal.symbol}")
            
            if signal.signal_type == "BUY":
                result = self.portfolio_manager.buy_shares(
                    signal.symbol, 
                    signal.quantity, 
                    signal.price
                )
            elif signal.signal_type == "SELL":
                result = self.portfolio_manager.sell_shares(
                    signal.symbol, 
                    signal.quantity, 
                    signal.price
                )
            else:
                return False
            
            if result['success']:
                # Update active positions
                if signal.symbol not in self.active_positions:
                    self.active_positions[signal.symbol] = {
                        'quantity': 0,
                        'avg_price': 0,
                        'stop_loss': signal.stop_loss,
                        'take_profit': signal.take_profit
                    }
                
                if signal.signal_type == "BUY":
                    self.active_positions[signal.symbol]['quantity'] += signal.quantity
                    self.active_positions[signal.symbol]['avg_price'] = signal.price
                else:
                    self.active_positions[signal.symbol]['quantity'] -= signal.quantity
                
                # Update volume
                trade_value = signal.price * signal.quantity
                self.daily_stats['volume_traded'] += trade_value
                if self.current_session:
                    self.current_session.total_volume += trade_value
                
                logger.info(f"Successfully executed {signal.signal_type} for {signal.symbol}")
                return True
            else:
                logger.warning(f"Failed to execute {signal.signal_type} for {signal.symbol}: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return False

    def _update_performance_metrics(self):
        """Update performance metrics."""
        try:
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            self.daily_stats['current_balance'] = portfolio_summary['total_value']
            self.daily_stats['total_profit'] = portfolio_summary['total_return']
            
            # Calculate win rate
            if self.daily_stats['trades_executed'] > 0:
                self.risk_metrics['win_rate'] = (
                    self.daily_stats['winning_trades'] / self.daily_stats['trades_executed']
                ) * 100
            
            # Update session stats
            if self.current_session:
                self.current_session.total_profit = self.daily_stats['total_profit']
                self.current_session.winning_trades = self.daily_stats['winning_trades']
                self.current_session.losing_trades = self.daily_stats['losing_trades']
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    def _is_target_reached(self) -> bool:
        """Check if trading target has been reached."""
        try:
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            current_return_percentage = portfolio_summary['total_return_percentage']
            
            # Check percentage target
            if self.goal.target_profit_percentage > 0:
                if current_return_percentage >= self.goal.target_profit_percentage:
                    return True
            
            # Check dollar amount target
            if self.goal.target_profit_amount > 0:
                if portfolio_summary['total_return'] >= self.goal.target_profit_amount:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking target: {e}")
            return False

    def _is_risk_limit_exceeded(self) -> bool:
        """Check if risk limits have been exceeded."""
        try:
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            current_return_percentage = portfolio_summary['total_return_percentage']
            
            # Check daily loss limit
            if current_return_percentage <= -self.goal.max_daily_loss_percentage:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return False

    def get_trading_status(self) -> Dict[str, Any]:
        """Get current trading status and statistics."""
        try:
            portfolio_summary = self.portfolio_manager.get_portfolio_summary()
            
            return {
                'status': self.status.value if self.status else 'idle',
                'strategy': self.strategy.value if self.strategy else 'ai_driven',
                'goal': asdict(self.goal),
                'daily_stats': self.daily_stats,
                'risk_metrics': self.risk_metrics,
                'active_positions': self.active_positions,
                'watchlist': self.watchlist,
                'current_session': asdict(self.current_session) if self.current_session else None,
                'portfolio_summary': {
                    'total_value': portfolio_summary['total_value'],
                    'total_return': portfolio_summary['total_return'],
                    'total_return_percentage': portfolio_summary['total_return_percentage'],
                    'available_cash': portfolio_summary['available_cash']
                },
                'recent_signals': [
                    {
                        'symbol': s.symbol,
                        'type': s.signal_type,
                        'confidence': s.confidence,
                        'price': s.price,
                        'quantity': s.quantity,
                        'reasoning': s.reasoning,
                        'timestamp': s.timestamp.isoformat()
                    }
                    for s in self.trading_signals[-10:]  # Last 10 signals
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting trading status: {e}")
            return {'error': str(e)}

    def get_trading_history(self) -> List[Dict[str, Any]]:
        """Get trading history."""
        try:
            transactions = self.portfolio_manager.get_transaction_history(100)
            return transactions
        except Exception as e:
            logger.error(f"Error getting trading history: {e}")
            return []
