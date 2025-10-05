#!/usr/bin/env python3
"""
Intelligent AI Trading Bot with Market Understanding and Learning
Implements target-based trading with end-of-day learning and analysis
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import yfinance as yf
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingTarget:
    """Defines a trading target for the bot"""
    symbol: str
    target_price: float
    target_return: float  # Percentage return target
    timeframe: str  # 'day', 'week', 'month'
    risk_level: str  # 'low', 'medium', 'high'
    created_at: datetime

@dataclass
class PredictionLearning:
    """Tracks what bot predicted vs actual outcome"""
    symbol: str
    prediction_date: datetime
    predicted_price: float
    predicted_direction: str  # 'up', 'down', 'neutral'
    predicted_factors: List[str]
    actual_price: float
    actual_direction: str
    accuracy_score: float
    missed_factors: List[str]
    learned_insights: str

@dataclass
class TradeDecision:
    """Bot's decision for a trade"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    quantity: int
    confidence: float
    reasoning: str
    expected_return: float
    risk_factors: List[str]
    timestamp: datetime

class IntelligentTradingBot:
    """
    Enhanced trading bot that:
    1. Understands market conditions
    2. Works towards specific targets
    3. Learns from prediction mistakes
    4. Analyzes end-of-day performance
    """

    def __init__(self, initial_capital: float = 100000, learning_file: str = "bot_learning.json"):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.learning_file = learning_file
        self.positions = {}  # symbol -> {quantity, avg_price, entry_date}
        self.targets = {}  # symbol -> TradingTarget
        self.learning_history = []  # List of PredictionLearning
        self.daily_decisions = []  # Today's decisions
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_return': 0.0,
            'prediction_accuracy': 0.0,
            'learned_patterns': []
        }

        # Load previous learning
        self.load_learning()

        logger.info(f"Intelligent Trading Bot initialized with ${initial_capital:,.2f}")

    def set_target(self, symbol: str, target_price: float, target_return: float,
                   timeframe: str = 'day', risk_level: str = 'medium'):
        """Set a trading target for a symbol"""
        target = TradingTarget(
            symbol=symbol,
            target_price=target_price,
            target_return=target_return,
            timeframe=timeframe,
            risk_level=risk_level,
            created_at=datetime.now()
        )
        self.targets[symbol] = target
        logger.info(f"Target set for {symbol}: ${target_price:.2f} ({target_return:+.2f}% return)")
        return target

    def analyze_market_conditions(self, symbol: str) -> Dict:
        """
        Analyze current market conditions for intelligent decision making
        """
        try:
            # Fetch market data
            stock = yf.Ticker(symbol)
            hist = stock.history(period='3mo')

            if hist.empty:
                return {'error': 'No data available'}

            current_price = float(hist['Close'].iloc[-1])

            # Calculate technical indicators
            sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            volatility = hist['Close'].pct_change().std() * np.sqrt(252)  # Annualized

            # Volume analysis
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            # Price momentum
            price_1d_change = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            price_5d_change = ((current_price - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100
            price_20d_change = ((current_price - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21]) * 100

            # Trend detection
            if current_price > sma_20 > sma_50:
                trend = 'strong_uptrend'
            elif current_price > sma_20:
                trend = 'uptrend'
            elif current_price < sma_20 < sma_50:
                trend = 'strong_downtrend'
            elif current_price < sma_20:
                trend = 'downtrend'
            else:
                trend = 'neutral'

            # Market factors that impact price
            factors = []
            if volume_ratio > 1.5:
                factors.append('high_volume')
            if abs(price_1d_change) > 3:
                factors.append('high_volatility')
            if volatility > 0.4:
                factors.append('high_risk')
            if trend in ['strong_uptrend', 'uptrend']:
                factors.append('bullish_momentum')
            elif trend in ['strong_downtrend', 'downtrend']:
                factors.append('bearish_momentum')

            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'volatility': volatility,
                'trend': trend,
                'volume_ratio': volume_ratio,
                'price_1d_change': price_1d_change,
                'price_5d_change': price_5d_change,
                'price_20d_change': price_20d_change,
                'market_factors': factors,
                'timestamp': datetime.now().isoformat()
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing market for {symbol}: {e}")
            return {'error': str(e)}

    def make_trading_decision(self, symbol: str, analysis: Dict) -> TradeDecision:
        """
        Make intelligent trading decision based on market analysis and targets
        """
        if 'error' in analysis:
            return None

        current_price = analysis['current_price']
        target = self.targets.get(symbol)

        # Check if we have a position
        has_position = symbol in self.positions

        # Decision logic based on market understanding
        action = 'HOLD'
        reasoning = []
        confidence = 0.5
        expected_return = 0.0
        risk_factors = []

        if target:
            # Target-based decision making
            price_to_target = ((target.target_price - current_price) / current_price) * 100

            if not has_position:
                # Consider buying
                if analysis['trend'] in ['uptrend', 'strong_uptrend']:
                    reasoning.append(f"Bullish trend detected ({analysis['trend']})")
                    confidence += 0.2

                if 'bullish_momentum' in analysis['market_factors']:
                    reasoning.append("Positive momentum indicators")
                    confidence += 0.1

                if analysis['volume_ratio'] > 1.2:
                    reasoning.append(f"High volume ({analysis['volume_ratio']:.2f}x avg)")
                    confidence += 0.1

                # Check if price is good entry point (below target)
                if price_to_target > 5:  # At least 5% upside to target
                    reasoning.append(f"Good entry point: {price_to_target:.2f}% below target")
                    confidence += 0.15
                    action = 'BUY'
                    expected_return = price_to_target

                # Risk assessment
                if analysis['volatility'] > 0.4:
                    risk_factors.append('High volatility')
                    confidence -= 0.1

                if 'high_risk' in analysis['market_factors']:
                    risk_factors.append('Market showing high risk signals')
                    confidence -= 0.05

            else:
                # Have position - consider selling
                position = self.positions[symbol]
                entry_price = position['avg_price']
                current_return = ((current_price - entry_price) / entry_price) * 100

                # Sell if target reached
                if current_return >= target.target_return * 0.9:  # 90% of target
                    action = 'SELL'
                    reasoning.append(f"Target achieved: {current_return:.2f}% return")
                    confidence = 0.9
                    expected_return = current_return

                # Sell if bearish signals
                elif analysis['trend'] in ['downtrend', 'strong_downtrend']:
                    action = 'SELL'
                    reasoning.append("Bearish trend detected - protecting profits/losses")
                    confidence = 0.7
                    expected_return = current_return
                    risk_factors.append('Bearish market conditions')

                # Stop loss
                elif current_return < -5:  # 5% stop loss
                    action = 'SELL'
                    reasoning.append(f"Stop loss triggered at {current_return:.2f}%")
                    confidence = 0.95
                    expected_return = current_return
                    risk_factors.append('Position in loss')

        # Calculate quantity for buy orders
        quantity = 0
        if action == 'BUY' and confidence >= 0.6:
            # Risk-based position sizing
            position_size_pct = 0.1  # Default 10% of capital
            if target and target.risk_level == 'low':
                position_size_pct = 0.05
            elif target and target.risk_level == 'high':
                position_size_pct = 0.15

            max_investment = self.current_capital * position_size_pct
            quantity = int(max_investment / current_price)
        elif action == 'SELL' and has_position:
            quantity = self.positions[symbol]['quantity']

        decision = TradeDecision(
            symbol=symbol,
            action=action if quantity > 0 else 'HOLD',
            quantity=quantity,
            confidence=min(confidence, 1.0),
            reasoning='; '.join(reasoning) if reasoning else 'Conditions not favorable',
            expected_return=expected_return,
            risk_factors=risk_factors,
            timestamp=datetime.now()
        )

        self.daily_decisions.append(decision)
        return decision

    def execute_trade(self, decision: TradeDecision, current_price: float) -> bool:
        """Execute the trading decision"""
        try:
            if decision.action == 'BUY':
                cost = decision.quantity * current_price
                if cost <= self.current_capital:
                    if decision.symbol not in self.positions:
                        self.positions[decision.symbol] = {
                            'quantity': 0,
                            'avg_price': 0,
                            'entry_date': datetime.now()
                        }

                    pos = self.positions[decision.symbol]
                    total_qty = pos['quantity'] + decision.quantity
                    total_cost = (pos['avg_price'] * pos['quantity']) + cost
                    pos['avg_price'] = total_cost / total_qty if total_qty > 0 else current_price
                    pos['quantity'] = total_qty

                    self.current_capital -= cost
                    self.performance_metrics['total_trades'] += 1

                    logger.info(f"BUY executed: {decision.quantity} {decision.symbol} @ ${current_price:.2f}")
                    return True

            elif decision.action == 'SELL':
                if decision.symbol in self.positions:
                    pos = self.positions[decision.symbol]
                    if pos['quantity'] >= decision.quantity:
                        revenue = decision.quantity * current_price
                        cost_basis = decision.quantity * pos['avg_price']
                        profit = revenue - cost_basis
                        profit_pct = (profit / cost_basis) * 100

                        self.current_capital += revenue
                        pos['quantity'] -= decision.quantity

                        if pos['quantity'] == 0:
                            del self.positions[decision.symbol]

                        self.performance_metrics['total_trades'] += 1
                        if profit > 0:
                            self.performance_metrics['winning_trades'] += 1
                        else:
                            self.performance_metrics['losing_trades'] += 1

                        logger.info(f"SELL executed: {decision.quantity} {decision.symbol} @ ${current_price:.2f} (P&L: {profit_pct:+.2f}%)")
                        return True

            return False

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False

    def end_of_day_learning(self, symbol: str):
        """
        At end of day, compare predictions with actual outcomes and learn
        """
        try:
            # Get today's decisions for this symbol
            today_decisions = [d for d in self.daily_decisions
                             if d.symbol == symbol and d.timestamp.date() == datetime.now().date()]

            if not today_decisions:
                return

            # Fetch actual end-of-day price
            stock = yf.Ticker(symbol)
            hist = stock.history(period='2d')

            if len(hist) < 2:
                return

            predicted_price = today_decisions[0].expected_return
            actual_start = float(hist['Open'].iloc[-1])
            actual_end = float(hist['Close'].iloc[-1])
            actual_change = ((actual_end - actual_start) / actual_start) * 100

            # Determine what we predicted vs what happened
            predicted_direction = 'up' if predicted_price > 0 else 'down' if predicted_price < 0 else 'neutral'
            actual_direction = 'up' if actual_change > 0 else 'down' if actual_change < 0 else 'neutral'

            # Calculate accuracy
            direction_correct = predicted_direction == actual_direction
            magnitude_error = abs(predicted_price - actual_change) if predicted_price != 0 else abs(actual_change)
            accuracy_score = max(0, 100 - magnitude_error) if direction_correct else max(0, 50 - magnitude_error)

            # Analyze what factors we missed
            missed_factors = []
            learned_insights = ""

            # Check what actually impacted the price
            volume_spike = (hist['Volume'].iloc[-1] / hist['Volume'].iloc[-2]) > 1.5
            volatility_high = abs(actual_change) > 3

            if volume_spike and 'high_volume' not in today_decisions[0].risk_factors:
                missed_factors.append('volume_spike')
                learned_insights += f"Missed volume spike ({hist['Volume'].iloc[-1]:,.0f}). "

            if volatility_high and 'high_volatility' not in today_decisions[0].risk_factors:
                missed_factors.append('high_volatility')
                learned_insights += f"Underestimated volatility (actual: {actual_change:.2f}%). "

            if not direction_correct:
                learned_insights += f"Direction prediction was wrong. Need to consider: {', '.join(missed_factors) if missed_factors else 'market sentiment, news events'}. "

            # Store learning
            learning = PredictionLearning(
                symbol=symbol,
                prediction_date=datetime.now(),
                predicted_price=predicted_price,
                predicted_direction=predicted_direction,
                predicted_factors=today_decisions[0].risk_factors,
                actual_price=actual_change,
                actual_direction=actual_direction,
                accuracy_score=accuracy_score,
                missed_factors=missed_factors,
                learned_insights=learned_insights or "Prediction was accurate."
            )

            self.learning_history.append(learning)

            # Update performance metrics
            total_accuracy = sum(l.accuracy_score for l in self.learning_history)
            self.performance_metrics['prediction_accuracy'] = total_accuracy / len(self.learning_history)

            # Extract learned patterns
            if missed_factors:
                pattern = f"Factor '{missed_factors[0]}' often missed - need better detection"
                if pattern not in self.performance_metrics['learned_patterns']:
                    self.performance_metrics['learned_patterns'].append(pattern)

            logger.info(f"EOD Learning for {symbol}: Accuracy={accuracy_score:.1f}% | {learned_insights}")

            # Save learning
            self.save_learning()

        except Exception as e:
            logger.error(f"Error in end-of-day learning: {e}")

    def save_learning(self):
        """Save learning history to file"""
        try:
            data = {
                'learning_history': [asdict(l) for l in self.learning_history[-100:]],  # Keep last 100
                'performance_metrics': self.performance_metrics,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_file, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning: {e}")

    def load_learning(self):
        """Load previous learning"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r') as f:
                    data = json.load(f)
                    self.performance_metrics = data.get('performance_metrics', self.performance_metrics)
                    logger.info(f"Loaded learning data. Prediction accuracy: {self.performance_metrics['prediction_accuracy']:.1f}%")
        except Exception as e:
            logger.error(f"Error loading learning: {e}")

    def get_performance_report(self) -> Dict:
        """Get comprehensive performance report"""
        total_value = self.current_capital
        for symbol, pos in self.positions.items():
            try:
                current_price = yf.Ticker(symbol).history(period='1d')['Close'].iloc[-1]
                total_value += pos['quantity'] * current_price
            except:
                pass

        total_return = ((total_value - self.initial_capital) / self.initial_capital) * 100

        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'total_value': total_value,
            'total_return': total_return,
            'positions_count': len(self.positions),
            'performance_metrics': self.performance_metrics,
            'recent_learning': [asdict(l) for l in self.learning_history[-5:]]
        }

# Global instance
intelligent_bot = None

def get_intelligent_bot(initial_capital: float = 100000):
    """Get or create the intelligent trading bot instance"""
    global intelligent_bot
    if intelligent_bot is None:
        intelligent_bot = IntelligentTradingBot(initial_capital)
    return intelligent_bot
