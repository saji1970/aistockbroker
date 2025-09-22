#!/usr/bin/env python3
"""
Portfolio Management System
Handles capital allocation, AI analysis, buy/sell signals, performance tracking, and rebalancing.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class AssetType(Enum):
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    ETF = "ETF"

@dataclass
class Asset:
    symbol: str
    name: str
    asset_type: AssetType
    current_price: float
    quantity: float = 0.0
    avg_cost: float = 0.0
    target_allocation: float = 0.0

@dataclass
class Signal:
    symbol: str
    signal_type: SignalType
    confidence: float
    price: float
    timestamp: datetime
    reasoning: str
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

@dataclass
class Portfolio:
    total_capital: float
    available_cash: float
    total_value: float
    assets: Dict[str, Asset]
    performance_history: List[Dict]
    signals_history: List[Signal]
    created_at: datetime
    last_rebalance: Optional[datetime] = None

class PortfolioManager:
    def __init__(self, initial_capital: float, ai_predictor=None):
        """
        Initialize portfolio manager with initial capital.
        
        Args:
            initial_capital: Starting capital in dollars
            ai_predictor: AI predictor instance for analysis
        """
        self.initial_capital = initial_capital
        self.ai_predictor = ai_predictor
        self.portfolio = self._initialize_portfolio()
        self.risk_tolerance = "moderate"  # conservative, moderate, aggressive
        self.rebalance_threshold = 0.05  # 5% deviation triggers rebalancing
        self.max_position_size = 0.20  # Maximum 20% in single asset
        self.min_position_size = 0.02  # Minimum 2% in single asset
        
        # Performance tracking
        self.performance_metrics = {
            'total_return': 0.0,
            'daily_return': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0
        }
        
        logger.info(f"Portfolio Manager initialized with ${initial_capital:,.2f}")

    def _initialize_portfolio(self) -> Portfolio:
        """Initialize a new portfolio."""
        return Portfolio(
            total_capital=self.initial_capital,
            available_cash=self.initial_capital,
            total_value=self.initial_capital,
            assets={},
            performance_history=[],
            signals_history=[],
            created_at=datetime.now(),
            last_rebalance=None
        )

    def add_capital(self, amount: float) -> bool:
        """Add capital to the portfolio."""
        if amount <= 0:
            logger.error("Capital amount must be positive")
            return False
        
        self.portfolio.total_capital += amount
        self.portfolio.available_cash += amount
        self.portfolio.total_value += amount
        
        logger.info(f"Added ${amount:,.2f} to portfolio. New total: ${self.portfolio.total_capital:,.2f}")
        return True

    def analyze_asset_with_ai(self, symbol: str, asset_type: AssetType = AssetType.STOCK) -> Dict:
        """
        Analyze an asset using AI models.
        
        Args:
            symbol: Asset symbol
            asset_type: Type of asset (stock, crypto, etf)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if not self.ai_predictor:
                logger.warning("No AI predictor available, using basic analysis")
                return self._basic_analysis(symbol)
            
            # Get AI analysis
            analysis = {}
            
            # Technical analysis
            tech_analysis = self.ai_predictor.prepare_analysis_data(symbol, "1y")
            if tech_analysis:
                analysis['technical'] = tech_analysis
            
            # AI prediction
            prediction = self.ai_predictor.predict_stock(symbol, "1y")
            if prediction:
                analysis['prediction'] = prediction
            
            # Sensitivity analysis
            sensitivity = self.ai_predictor.perform_sensitivity_analysis(symbol, "1y")
            if sensitivity:
                analysis['sensitivity'] = sensitivity
            
            # Smart recommendations
            recommendations = self.ai_predictor.generate_smart_recommendations(symbol)
            if recommendations:
                analysis['recommendations'] = recommendations
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return self._basic_analysis(symbol)

    def _basic_analysis(self, symbol: str) -> Dict:
        """Basic analysis when AI is not available."""
        return {
            'symbol': symbol,
            'current_price': 100.0,  # Placeholder
            'signal': SignalType.HOLD,
            'confidence': 0.5,
            'reasoning': 'Basic analysis - no AI available'
        }

    def generate_signals(self, watchlist: List[str], asset_types: List[AssetType] = None) -> List[Signal]:
        """
        Generate buy/sell signals for assets in watchlist.
        
        Args:
            watchlist: List of asset symbols to analyze
            asset_types: List of asset types (defaults to all types)
            
        Returns:
            List of trading signals
        """
        if asset_types is None:
            asset_types = [AssetType.STOCK, AssetType.CRYPTO, AssetType.ETF]
        
        signals = []
        
        for symbol in watchlist:
            try:
                # Determine asset type (simplified logic)
                asset_type = self._determine_asset_type(symbol)
                if asset_type not in asset_types:
                    continue
                
                # Analyze asset
                analysis = self.analyze_asset_with_ai(symbol, asset_type)
                
                # Generate signal based on analysis
                signal = self._generate_signal_from_analysis(symbol, analysis, asset_type)
                if signal:
                    signals.append(signal)
                    self.portfolio.signals_history.append(signal)
                
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {str(e)}")
        
        logger.info(f"Generated {len(signals)} signals")
        return signals

    def _determine_asset_type(self, symbol: str) -> AssetType:
        """Determine asset type based on symbol."""
        # Crypto symbols (simplified)
        crypto_symbols = ['BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH', 'XRP', 'SOL', 'AVAX']
        
        if symbol.upper() in crypto_symbols:
            return AssetType.CRYPTO
        elif symbol.upper().endswith('X'):  # Common crypto pattern
            return AssetType.CRYPTO
        elif symbol.upper() in ['SPY', 'QQQ', 'VTI', 'VOO', 'GLD', 'SLV', 'ARKK']:
            return AssetType.ETF
        else:
            return AssetType.STOCK

    def _generate_signal_from_analysis(self, symbol: str, analysis: Dict, asset_type: AssetType) -> Optional[Signal]:
        """Generate trading signal from AI analysis."""
        try:
            # Extract key metrics
            current_price = analysis.get('technical', {}).get('latest_data', {}).get('Close', 100.0)
            prediction = analysis.get('prediction', {})
            technical = analysis.get('technical', {})
            recommendations = analysis.get('recommendations', {})
            
            # Determine signal type and confidence
            signal_type = SignalType.HOLD
            confidence = 0.5
            reasoning = []
            target_price = None
            stop_loss = None
            
            # AI prediction analysis
            if prediction:
                predicted_price = prediction.get('predicted_price', current_price)
                prediction_confidence = prediction.get('confidence', 0.5)
                
                price_change_pct = ((predicted_price - current_price) / current_price) * 100
                
                if price_change_pct > 10 and prediction_confidence > 0.7:
                    signal_type = SignalType.STRONG_BUY
                    confidence = prediction_confidence
                    reasoning.append(f"Strong AI prediction: {price_change_pct:.1f}% upside")
                    target_price = predicted_price
                elif price_change_pct > 5 and prediction_confidence > 0.6:
                    signal_type = SignalType.BUY
                    confidence = prediction_confidence
                    reasoning.append(f"AI prediction: {price_change_pct:.1f}% upside")
                    target_price = predicted_price
                elif price_change_pct < -10 and prediction_confidence > 0.7:
                    signal_type = SignalType.STRONG_SELL
                    confidence = prediction_confidence
                    reasoning.append(f"Strong AI prediction: {abs(price_change_pct):.1f}% downside")
                elif price_change_pct < -5 and prediction_confidence > 0.6:
                    signal_type = SignalType.SELL
                    confidence = prediction_confidence
                    reasoning.append(f"AI prediction: {abs(price_change_pct):.1f}% downside")
            
            # Technical analysis
            if technical:
                latest_data = technical.get('latest_data', {})
                
                # RSI analysis
                rsi = latest_data.get('RSI', 50)
                if rsi < 30:
                    reasoning.append("RSI oversold (< 30)")
                    if signal_type == SignalType.HOLD:
                        signal_type = SignalType.BUY
                        confidence = max(confidence, 0.6)
                elif rsi > 70:
                    reasoning.append("RSI overbought (> 70)")
                    if signal_type == SignalType.HOLD:
                        signal_type = SignalType.SELL
                        confidence = max(confidence, 0.6)
                
                # MACD analysis
                macd = latest_data.get('MACD', 0)
                macd_signal = latest_data.get('MACD_Signal', 0)
                if macd > macd_signal:
                    reasoning.append("MACD bullish")
                    if signal_type == SignalType.HOLD:
                        signal_type = SignalType.BUY
                        confidence = max(confidence, 0.55)
                elif macd < macd_signal:
                    reasoning.append("MACD bearish")
                    if signal_type == SignalType.HOLD:
                        signal_type = SignalType.SELL
                        confidence = max(confidence, 0.55)
            
            # Smart recommendations
            if recommendations:
                risk_assessment = recommendations.get('risk_assessment', {})
                timing_recommendations = recommendations.get('timing_recommendations', {})
                
                if risk_assessment:
                    risk_level = risk_assessment.get('overall_risk', 'medium')
                    if risk_level == 'low' and signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                        confidence = min(confidence + 0.1, 1.0)
                        reasoning.append("Low risk profile")
                    elif risk_level == 'high' and signal_type in [SignalType.SELL, SignalType.STRONG_SELL]:
                        confidence = min(confidence + 0.1, 1.0)
                        reasoning.append("High risk profile")
                
                if timing_recommendations:
                    timing = timing_recommendations.get('recommended_timing', 'neutral')
                    if timing == 'immediate' and signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                        confidence = min(confidence + 0.05, 1.0)
                        reasoning.append("Immediate timing recommended")
            
            # Set stop loss for buy signals
            if signal_type in [SignalType.BUY, SignalType.STRONG_BUY] and target_price:
                stop_loss = current_price * 0.95  # 5% stop loss
            
            return Signal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                price=current_price,
                timestamp=datetime.now(),
                reasoning="; ".join(reasoning) if reasoning else "No clear signal",
                target_price=target_price,
                stop_loss=stop_loss
            )
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            return None

    def execute_signal(self, signal: Signal, quantity: Optional[float] = None) -> bool:
        """
        Execute a trading signal.
        
        Args:
            signal: Trading signal to execute
            quantity: Quantity to trade (None for auto-calculate)
            
        Returns:
            True if executed successfully
        """
        try:
            symbol = signal.symbol
            current_price = signal.price
            
            # Calculate quantity if not provided
            if quantity is None:
                if signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                    # Use available cash based on signal strength
                    allocation_pct = 0.1 if signal.signal_type == SignalType.BUY else 0.15
                    max_amount = self.portfolio.available_cash * allocation_pct
                    quantity = max_amount / current_price
                else:
                    # Sell existing position
                    if symbol in self.portfolio.assets:
                        quantity = self.portfolio.assets[symbol].quantity
                    else:
                        logger.warning(f"No position in {symbol} to sell")
                        return False
            
            # Execute trade
            if signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                return self._buy_asset(symbol, quantity, current_price)
            elif signal.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]:
                return self._sell_asset(symbol, quantity, current_price)
            else:
                logger.info(f"HOLD signal for {symbol} - no action taken")
                return True
                
        except Exception as e:
            logger.error(f"Error executing signal for {signal.symbol}: {str(e)}")
            return False

    def _buy_asset(self, symbol: str, quantity: float, price: float) -> bool:
        """Buy an asset."""
        try:
            total_cost = quantity * price
            
            if total_cost > self.portfolio.available_cash:
                logger.warning(f"Insufficient cash for {symbol} purchase")
                return False
            
            # Update portfolio
            if symbol in self.portfolio.assets:
                asset = self.portfolio.assets[symbol]
                # Update average cost
                total_quantity = asset.quantity + quantity
                total_cost_basis = (asset.quantity * asset.avg_cost) + total_cost
                asset.avg_cost = total_cost_basis / total_quantity
                asset.quantity = total_quantity
            else:
                # Create new asset
                asset = Asset(
                    symbol=symbol,
                    name=symbol,  # Could be enhanced with real names
                    asset_type=self._determine_asset_type(symbol),
                    current_price=price,
                    quantity=quantity,
                    avg_cost=price
                )
                self.portfolio.assets[symbol] = asset
            
            # Update cash and total value
            self.portfolio.available_cash -= total_cost
            self.portfolio.total_value = self._calculate_total_value()
            
            logger.info(f"Bought {quantity:.2f} {symbol} at ${price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error buying {symbol}: {str(e)}")
            return False

    def _sell_asset(self, symbol: str, quantity: float, price: float) -> bool:
        """Sell an asset."""
        try:
            if symbol not in self.portfolio.assets:
                logger.warning(f"No position in {symbol} to sell")
                return False
            
            asset = self.portfolio.assets[symbol]
            
            if quantity > asset.quantity:
                logger.warning(f"Insufficient quantity of {symbol} to sell")
                return False
            
            # Calculate proceeds
            proceeds = quantity * price
            
            # Update portfolio
            asset.quantity -= quantity
            
            if asset.quantity <= 0:
                # Remove asset if fully sold
                del self.portfolio.assets[symbol]
            
            # Update cash and total value
            self.portfolio.available_cash += proceeds
            self.portfolio.total_value = self._calculate_total_value()
            
            logger.info(f"Sold {quantity:.2f} {symbol} at ${price:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error selling {symbol}: {str(e)}")
            return False

    def _calculate_total_value(self) -> float:
        """Calculate total portfolio value."""
        total = self.portfolio.available_cash
        
        for asset in self.portfolio.assets.values():
            total += asset.quantity * asset.current_price
        
        return total

    def update_prices(self, price_updates: Dict[str, float]):
        """Update asset prices and recalculate portfolio value."""
        for symbol, price in price_updates.items():
            if symbol in self.portfolio.assets:
                self.portfolio.assets[symbol].current_price = price
        
        self.portfolio.total_value = self._calculate_total_value()

    def track_performance(self) -> Dict:
        """Track portfolio performance metrics."""
        try:
            current_value = self.portfolio.total_value
            total_return = ((current_value - self.initial_capital) / self.initial_capital) * 100
            
            # Calculate daily return
            if self.portfolio.performance_history:
                yesterday_value = self.portfolio.performance_history[-1]['total_value']
                daily_return = ((current_value - yesterday_value) / yesterday_value) * 100
            else:
                daily_return = 0.0
            
            # Update performance history
            performance_record = {
                'date': datetime.now(),
                'total_value': current_value,
                'total_return': total_return,
                'daily_return': daily_return,
                'available_cash': self.portfolio.available_cash,
                'num_assets': len(self.portfolio.assets)
            }
            
            self.portfolio.performance_history.append(performance_record)
            
            # Calculate additional metrics
            self._calculate_performance_metrics()
            
            return {
                'total_return': total_return,
                'daily_return': daily_return,
                'total_value': current_value,
                'available_cash': self.portfolio.available_cash,
                'num_assets': len(self.portfolio.assets),
                'performance_metrics': self.performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Error tracking performance: {str(e)}")
            return {}

    def _calculate_performance_metrics(self):
        """Calculate advanced performance metrics."""
        try:
            if len(self.portfolio.performance_history) < 2:
                return
            
            # Extract daily returns
            daily_returns = []
            values = []
            
            for record in self.portfolio.performance_history:
                daily_returns.append(record['daily_return'])
                values.append(record['total_value'])
            
            # Calculate metrics
            self.performance_metrics['total_return'] = daily_returns[-1] if daily_returns else 0.0
            self.performance_metrics['daily_return'] = daily_returns[-1] if daily_returns else 0.0
            self.performance_metrics['volatility'] = np.std(daily_returns) if len(daily_returns) > 1 else 0.0
            
            # Sharpe ratio (simplified)
            if self.performance_metrics['volatility'] > 0:
                avg_return = np.mean(daily_returns)
                self.performance_metrics['sharpe_ratio'] = avg_return / self.performance_metrics['volatility']
            
            # Maximum drawdown
            peak = values[0]
            max_dd = 0.0
            for value in values:
                if value > peak:
                    peak = value
                dd = (peak - value) / peak
                max_dd = max(max_dd, dd)
            self.performance_metrics['max_drawdown'] = max_dd * 100
            
            # Win rate (simplified)
            positive_days = sum(1 for r in daily_returns if r > 0)
            self.performance_metrics['win_rate'] = (positive_days / len(daily_returns)) * 100 if daily_returns else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")

    def check_rebalancing_needed(self) -> bool:
        """Check if portfolio rebalancing is needed."""
        try:
            if not self.portfolio.assets:
                return False
            
            total_value = self.portfolio.total_value
            if total_value == 0:
                return False
            
            # Check each asset's allocation
            for symbol, asset in self.portfolio.assets.items():
                current_allocation = (asset.quantity * asset.current_price) / total_value
                target_allocation = asset.target_allocation
                
                if target_allocation > 0:
                    deviation = abs(current_allocation - target_allocation)
                    if deviation > self.rebalance_threshold:
                        logger.info(f"Rebalancing needed: {symbol} deviation {deviation:.2%}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking rebalancing: {str(e)}")
            return False

    def rebalance_portfolio(self, target_allocations: Dict[str, float] = None) -> bool:
        """
        Rebalance portfolio to target allocations.
        
        Args:
            target_allocations: Dict of symbol -> target allocation percentage
            
        Returns:
            True if rebalancing successful
        """
        try:
            if not target_allocations:
                # Use equal weight allocation
                num_assets = len(self.portfolio.assets)
                if num_assets == 0:
                    return True
                
                equal_weight = 1.0 / num_assets
                target_allocations = {symbol: equal_weight for symbol in self.portfolio.assets.keys()}
            
            total_value = self.portfolio.total_value
            if total_value == 0:
                return False
            
            # Calculate target values and required trades
            trades = []
            
            for symbol, target_allocation in target_allocations.items():
                if symbol in self.portfolio.assets:
                    asset = self.portfolio.assets[symbol]
                    current_value = asset.quantity * asset.current_price
                    target_value = total_value * target_allocation
                    
                    # Update target allocation
                    asset.target_allocation = target_allocation
                    
                    # Calculate required trade
                    value_diff = target_value - current_value
                    if abs(value_diff) > (total_value * 0.01):  # 1% minimum trade size
                        quantity_diff = value_diff / asset.current_price
                        trades.append({
                            'symbol': symbol,
                            'quantity': quantity_diff,
                            'action': 'BUY' if quantity_diff > 0 else 'SELL'
                        })
            
            # Execute trades
            for trade in trades:
                if trade['action'] == 'BUY':
                    success = self._buy_asset(trade['symbol'], trade['quantity'], 
                                            self.portfolio.assets[trade['symbol']].current_price)
                else:
                    success = self._sell_asset(trade['symbol'], abs(trade['quantity']), 
                                             self.portfolio.assets[trade['symbol']].current_price)
                
                if not success:
                    logger.warning(f"Failed to execute rebalancing trade for {trade['symbol']}")
            
            self.portfolio.last_rebalance = datetime.now()
            logger.info(f"Portfolio rebalancing completed with {len(trades)} trades")
            return True
            
        except Exception as e:
            logger.error(f"Error rebalancing portfolio: {str(e)}")
            return False

    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary."""
        try:
            total_value = self.portfolio.total_value
            total_return = ((total_value - self.initial_capital) / self.initial_capital) * 100 if self.initial_capital > 0 else 0.0
            
            # Asset breakdown
            assets_summary = []
            for symbol, asset in self.portfolio.assets.items():
                asset_value = asset.quantity * asset.current_price
                allocation = (asset_value / total_value) * 100 if total_value > 0 else 0
                unrealized_pnl = asset_value - (asset.quantity * asset.avg_cost)
                
                assets_summary.append({
                    'symbol': symbol,
                    'name': asset.name,
                    'asset_type': asset.asset_type.value,
                    'quantity': asset.quantity,
                    'current_price': asset.current_price,
                    'avg_cost': asset.avg_cost,
                    'current_value': asset_value,
                    'allocation': allocation,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': (unrealized_pnl / (asset.quantity * asset.avg_cost)) * 100 if asset.quantity * asset.avg_cost > 0 else 0
                })
            
            # Sort by current value
            assets_summary.sort(key=lambda x: x['current_value'], reverse=True)
            
            return {
                'total_capital': self.portfolio.total_capital,
                'total_value': total_value,
                'available_cash': self.portfolio.available_cash,
                'total_return': total_return,
                'num_assets': len(self.portfolio.assets),
                'assets': assets_summary,
                'performance_metrics': self.performance_metrics,
                'created_at': self.portfolio.created_at,
                'last_rebalance': self.portfolio.last_rebalance,
                'total_signals': len(self.portfolio.signals_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            return {}

    def save_portfolio_state(self, filename: str = None):
        """Save portfolio state to file."""
        try:
            if filename is None:
                filename = f"portfolio_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            state = {
                'initial_capital': self.initial_capital,
                'portfolio': {
                    'total_capital': self.portfolio.total_capital,
                    'available_cash': self.portfolio.available_cash,
                    'total_value': self.portfolio.total_value,
                    'created_at': self.portfolio.created_at.isoformat(),
                    'last_rebalance': self.portfolio.last_rebalance.isoformat() if self.portfolio.last_rebalance else None,
                    'assets': {
                        symbol: {
                            'symbol': asset.symbol,
                            'name': asset.name,
                            'asset_type': asset.asset_type.value,
                            'current_price': asset.current_price,
                            'quantity': asset.quantity,
                            'avg_cost': asset.avg_cost,
                            'target_allocation': asset.target_allocation
                        }
                        for symbol, asset in self.portfolio.assets.items()
                    }
                },
                'performance_metrics': self.performance_metrics,
                'risk_tolerance': self.risk_tolerance,
                'rebalance_threshold': self.rebalance_threshold
            }
            
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Portfolio state saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving portfolio state: {str(e)}")

    def load_portfolio_state(self, filename: str):
        """Load portfolio state from file."""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            
            self.initial_capital = state['initial_capital']
            self.risk_tolerance = state.get('risk_tolerance', 'moderate')
            self.rebalance_threshold = state.get('rebalance_threshold', 0.05)
            
            # Reconstruct portfolio
            portfolio_data = state['portfolio']
            self.portfolio.total_capital = portfolio_data['total_capital']
            self.portfolio.available_cash = portfolio_data['available_cash']
            self.portfolio.total_value = portfolio_data['total_value']
            self.portfolio.created_at = datetime.fromisoformat(portfolio_data['created_at'])
            
            if portfolio_data['last_rebalance']:
                self.portfolio.last_rebalance = datetime.fromisoformat(portfolio_data['last_rebalance'])
            
            # Reconstruct assets
            self.portfolio.assets = {}
            for symbol, asset_data in portfolio_data['assets'].items():
                asset = Asset(
                    symbol=asset_data['symbol'],
                    name=asset_data['name'],
                    asset_type=AssetType(asset_data['asset_type']),
                    current_price=asset_data['current_price'],
                    quantity=asset_data['quantity'],
                    avg_cost=asset_data['avg_cost'],
                    target_allocation=asset_data['target_allocation']
                )
                self.portfolio.assets[symbol] = asset
            
            self.performance_metrics = state.get('performance_metrics', self.performance_metrics)
            
            logger.info(f"Portfolio state loaded from {filename}")
            
        except Exception as e:
            logger.error(f"Error loading portfolio state: {str(e)}")

    def get_recent_signals(self, limit: int = 10) -> List[Signal]:
        """Get recent trading signals."""
        return self.portfolio.signals_history[-limit:] if self.portfolio.signals_history else []

    def get_performance_history(self, days: int = 30) -> List[Dict]:
        """Get performance history for the last N days."""
        if not self.portfolio.performance_history:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        return [record for record in self.portfolio.performance_history 
                if record['date'] >= cutoff_date] 