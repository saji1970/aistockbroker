#!/usr/bin/env python3
"""
AI Trading Suggestion Service for Agent-Customer System
Generates AI-powered trading suggestions and learns from agent decisions
"""

import os
import sys
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import yfinance as yf

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_manager
from models.agent_models import (
    CustomerPortfolio, PortfolioHolding, TradingSuggestion, AgentDecisionFeedback,
    TradingSuggestionType, SuggestionStatus
)
from gemini_predictor import GeminiStockPredictor
from data_fetcher import data_fetcher
from technical_analysis import TechnicalAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class MarketContext:
    symbol: str
    current_price: float
    volume: int
    market_cap: float
    pe_ratio: float
    sector: str
    beta: float
    analyst_rating: str
    news_sentiment: float
    technical_indicators: Dict

class TradingSuggestionService:
    def __init__(self):
        self.gemini_predictor = GeminiStockPredictor()
        self.technical_analyzer = TechnicalAnalyzer()
        self.learning_weights = {
            'ai_confidence': 0.3,
            'technical_strength': 0.25,
            'agent_feedback_history': 0.2,
            'market_sentiment': 0.15,
            'portfolio_context': 0.1
        }

    async def generate_suggestions_for_portfolio(self, portfolio_id: int) -> List[Dict]:
        """Generate AI trading suggestions for a customer portfolio"""
        with db_manager.get_session() as session:
            try:
                portfolio = session.query(CustomerPortfolio).get(portfolio_id)
                if not portfolio:
                    raise ValueError("Portfolio not found")

                # Get current holdings
                holdings = session.query(PortfolioHolding).filter_by(
                    portfolio_id=portfolio_id
                ).all()

                suggestions = []

                # Generate sell/hold suggestions for existing positions
                for holding in holdings:
                    suggestion = await self._analyze_holding_for_suggestion(
                        session, portfolio, holding
                    )
                    if suggestion:
                        suggestions.append(suggestion)

                # Generate buy suggestions for new positions
                buy_suggestions = await self._generate_buy_suggestions(
                    session, portfolio
                )
                suggestions.extend(buy_suggestions)

                # Store suggestions in database
                for suggestion_data in suggestions:
                    suggestion = TradingSuggestion(
                        portfolio_id=portfolio_id,
                        agent_id=portfolio.agent_id,
                        **suggestion_data
                    )
                    session.add(suggestion)

                logger.info(f"Generated {len(suggestions)} suggestions for portfolio {portfolio_id}")
                return suggestions

            except Exception as e:
                logger.error(f"Error generating suggestions for portfolio {portfolio_id}: {e}")
                raise

    async def _analyze_holding_for_suggestion(
        self, session, portfolio: CustomerPortfolio, holding: PortfolioHolding
    ) -> Optional[Dict]:
        """Analyze existing holding for sell/hold suggestions"""
        try:
            # Get market context
            market_context = await self._get_market_context(holding.symbol)

            # Update current price
            holding.current_price = market_context.current_price
            holding.market_value = holding.quantity * holding.current_price
            holding.unrealized_pnl = (holding.current_price - holding.average_price) * holding.quantity
            holding.unrealized_pnl_percent = (holding.unrealized_pnl / (holding.average_price * holding.quantity)) * 100

            # Get AI prediction
            ai_prediction = await self.gemini_predictor.predict_stock_movement(
                holding.symbol,
                timeframe_days=30
            )

            # Calculate position strength
            position_strength = self._calculate_position_strength(holding, market_context)

            # Check stop loss / take profit conditions
            stop_loss_triggered = (
                holding.stop_loss_price and
                holding.current_price <= holding.stop_loss_price
            )

            take_profit_triggered = (
                holding.take_profit_price and
                holding.current_price >= holding.take_profit_price
            )

            # Determine suggestion
            if stop_loss_triggered:
                suggestion_type = TradingSuggestionType.SELL
                reasoning = f"Stop loss triggered at ${holding.stop_loss_price}"
                confidence = 0.9
            elif take_profit_triggered:
                suggestion_type = TradingSuggestionType.SELL
                reasoning = f"Take profit target reached at ${holding.take_profit_price}"
                confidence = 0.8
            elif ai_prediction['direction'] == 'bearish' and ai_prediction['confidence'] > 0.7:
                suggestion_type = TradingSuggestionType.SELL
                reasoning = f"AI predicts bearish movement: {ai_prediction['reasoning']}"
                confidence = ai_prediction['confidence']
            elif position_strength < 0.3:
                suggestion_type = TradingSuggestionType.SELL
                reasoning = "Weak technical indicators and poor position strength"
                confidence = 0.6
            else:
                suggestion_type = TradingSuggestionType.HOLD
                reasoning = f"Position showing strength, AI confidence: {ai_prediction['confidence']:.2f}"
                confidence = 0.5

            # Apply agent learning adjustments
            adjusted_confidence = await self._apply_agent_learning(
                session, portfolio.agent_id, holding.symbol, confidence
            )

            return {
                'symbol': holding.symbol,
                'suggestion_type': suggestion_type,
                'suggested_quantity': holding.quantity if suggestion_type == TradingSuggestionType.SELL else 0,
                'suggested_price': market_context.current_price,
                'current_price': market_context.current_price,
                'ai_confidence': adjusted_confidence,
                'predicted_return': ai_prediction.get('expected_return', 0),
                'risk_score': self._calculate_risk_score(market_context),
                'reasoning': reasoning,
                'technical_indicators': market_context.technical_indicators,
                'market_sentiment': market_context.analyst_rating,
                'news_sentiment': market_context.news_sentiment,
                'valid_until': datetime.utcnow() + timedelta(hours=24),
                'priority': self._calculate_priority(suggestion_type, confidence)
            }

        except Exception as e:
            logger.error(f"Error analyzing holding {holding.symbol}: {e}")
            return None

    async def _generate_buy_suggestions(
        self, session, portfolio: CustomerPortfolio
    ) -> List[Dict]:
        """Generate buy suggestions for new positions"""
        try:
            # Get potential stocks based on portfolio preferences
            candidate_stocks = await self._get_candidate_stocks(portfolio)

            suggestions = []
            max_suggestions = 5  # Limit to top 5 suggestions

            for symbol in candidate_stocks[:max_suggestions]:
                try:
                    # Get market context
                    market_context = await self._get_market_context(symbol)

                    # Get AI prediction
                    ai_prediction = await self.gemini_predictor.predict_stock_movement(
                        symbol, timeframe_days=30
                    )

                    # Check if it's a good buy opportunity
                    if ai_prediction['direction'] == 'bullish' and ai_prediction['confidence'] > 0.6:
                        # Calculate position size (risk-based)
                        position_size = self._calculate_position_size(
                            portfolio, market_context.current_price
                        )

                        if position_size > 0:
                            # Apply agent learning adjustments
                            adjusted_confidence = await self._apply_agent_learning(
                                session, portfolio.agent_id, symbol, ai_prediction['confidence']
                            )

                            suggestion = {
                                'symbol': symbol,
                                'suggestion_type': TradingSuggestionType.BUY,
                                'suggested_quantity': position_size,
                                'suggested_price': market_context.current_price,
                                'current_price': market_context.current_price,
                                'ai_confidence': adjusted_confidence,
                                'predicted_return': ai_prediction.get('expected_return', 0),
                                'risk_score': self._calculate_risk_score(market_context),
                                'reasoning': f"AI bullish prediction: {ai_prediction['reasoning']}",
                                'technical_indicators': market_context.technical_indicators,
                                'market_sentiment': market_context.analyst_rating,
                                'news_sentiment': market_context.news_sentiment,
                                'valid_until': datetime.utcnow() + timedelta(hours=24),
                                'priority': self._calculate_priority(
                                    TradingSuggestionType.BUY,
                                    adjusted_confidence
                                )
                            }
                            suggestions.append(suggestion)

                except Exception as e:
                    logger.error(f"Error analyzing candidate stock {symbol}: {e}")
                    continue

            return suggestions

        except Exception as e:
            logger.error(f"Error generating buy suggestions: {e}")
            return []

    async def _get_market_context(self, symbol: str) -> MarketContext:
        """Get comprehensive market context for a symbol"""
        try:
            # Get basic market data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="3mo")

            current_price = info.get('currentPrice', hist['Close'].iloc[-1])

            # Get technical indicators
            technical_indicators = self.technical_analyzer.calculate_indicators(hist)

            # Simulate news sentiment (in real implementation, use news API)
            news_sentiment = np.random.uniform(-0.5, 0.5)

            return MarketContext(
                symbol=symbol,
                current_price=current_price,
                volume=info.get('volume', 0),
                market_cap=info.get('marketCap', 0),
                pe_ratio=info.get('trailingPE', 0),
                sector=info.get('sector', 'Unknown'),
                beta=info.get('beta', 1.0),
                analyst_rating=info.get('recommendationKey', 'hold'),
                news_sentiment=news_sentiment,
                technical_indicators=technical_indicators
            )

        except Exception as e:
            logger.error(f"Error getting market context for {symbol}: {e}")
            # Return default context
            return MarketContext(
                symbol=symbol,
                current_price=0,
                volume=0,
                market_cap=0,
                pe_ratio=0,
                sector='Unknown',
                beta=1.0,
                analyst_rating='hold',
                news_sentiment=0,
                technical_indicators={}
            )

    async def _get_candidate_stocks(self, portfolio: CustomerPortfolio) -> List[str]:
        """Get candidate stocks based on portfolio preferences"""
        # This would typically use screeners, sector analysis, etc.
        # For now, return some popular stocks
        candidates = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
            'NVDA', 'META', 'JPM', 'JNJ', 'UNH'
        ]

        # Filter based on portfolio risk level and existing holdings
        with db_manager.get_session() as session:
            existing_symbols = session.query(PortfolioHolding.symbol).filter_by(
                portfolio_id=portfolio.id
            ).all()
            existing_symbols = [s[0] for s in existing_symbols]

        # Remove stocks already held
        candidates = [s for s in candidates if s not in existing_symbols]

        return candidates

    def _calculate_position_strength(self, holding: PortfolioHolding, market_context: MarketContext) -> float:
        """Calculate strength of current position"""
        try:
            strength_factors = []

            # P&L factor
            if holding.unrealized_pnl_percent > 10:
                strength_factors.append(0.8)
            elif holding.unrealized_pnl_percent > 0:
                strength_factors.append(0.6)
            else:
                strength_factors.append(0.3)

            # Technical strength
            tech_indicators = market_context.technical_indicators
            if tech_indicators.get('rsi', 50) > 70:
                strength_factors.append(0.2)  # Overbought
            elif tech_indicators.get('rsi', 50) < 30:
                strength_factors.append(0.8)  # Oversold
            else:
                strength_factors.append(0.5)

            # Volume factor
            if market_context.volume > 0:
                strength_factors.append(0.6)
            else:
                strength_factors.append(0.3)

            return np.mean(strength_factors)

        except Exception:
            return 0.5

    def _calculate_position_size(self, portfolio: CustomerPortfolio, stock_price: float) -> int:
        """Calculate appropriate position size based on portfolio and risk"""
        try:
            # Risk-based position sizing
            available_cash = portfolio.current_cash
            max_position_value = available_cash * portfolio.max_position_size

            if max_position_value < stock_price:
                return 0

            quantity = int(max_position_value / stock_price)
            return quantity

        except Exception:
            return 0

    def _calculate_risk_score(self, market_context: MarketContext) -> float:
        """Calculate risk score for a stock (0-1, higher = riskier)"""
        try:
            risk_factors = []

            # Beta risk
            beta = market_context.beta or 1.0
            if beta > 1.5:
                risk_factors.append(0.8)
            elif beta < 0.5:
                risk_factors.append(0.3)
            else:
                risk_factors.append(0.5)

            # Volatility from technical indicators
            volatility = market_context.technical_indicators.get('volatility', 0.2)
            risk_factors.append(min(volatility * 2, 1.0))

            # Market cap risk (smaller = riskier)
            market_cap = market_context.market_cap or 0
            if market_cap > 100_000_000_000:  # Large cap
                risk_factors.append(0.3)
            elif market_cap > 10_000_000_000:  # Mid cap
                risk_factors.append(0.5)
            else:  # Small cap
                risk_factors.append(0.8)

            return np.mean(risk_factors)

        except Exception:
            return 0.5

    def _calculate_priority(self, suggestion_type: TradingSuggestionType, confidence: float) -> int:
        """Calculate priority (1-10, higher = more urgent)"""
        base_priority = {
            TradingSuggestionType.SELL: 7,
            TradingSuggestionType.BUY: 5,
            TradingSuggestionType.HOLD: 3,
            TradingSuggestionType.STOP_LOSS: 9,
            TradingSuggestionType.TAKE_PROFIT: 8
        }.get(suggestion_type, 5)

        # Adjust based on confidence
        confidence_adjustment = int((confidence - 0.5) * 4)  # -2 to +2

        return max(1, min(10, base_priority + confidence_adjustment))

    async def _apply_agent_learning(
        self, session, agent_id: int, symbol: str, base_confidence: float
    ) -> float:
        """Apply learning from agent's past decisions to adjust confidence"""
        try:
            # Get recent agent feedback for this symbol
            recent_feedback = session.query(AgentDecisionFeedback).join(
                TradingSuggestion
            ).filter(
                TradingSuggestion.symbol == symbol,
                AgentDecisionFeedback.agent_id == agent_id,
                AgentDecisionFeedback.decision_at >= datetime.utcnow() - timedelta(days=90)
            ).limit(10).all()

            if not recent_feedback:
                return base_confidence

            # Calculate agent's accuracy with this symbol
            accurate_decisions = sum(1 for f in recent_feedback if f.ai_accuracy and f.ai_accuracy > 0.6)
            total_decisions = len(recent_feedback)
            accuracy_rate = accurate_decisions / total_decisions if total_decisions > 0 else 0.5

            # Calculate approval rate
            approved_decisions = sum(1 for f in recent_feedback if f.agent_decision == 'approved')
            approval_rate = approved_decisions / total_decisions if total_decisions > 0 else 0.5

            # Adjust confidence based on agent's historical performance
            learning_factor = (accuracy_rate * 0.6) + (approval_rate * 0.4)

            # Apply adjustment (±20% based on learning)
            adjustment = (learning_factor - 0.5) * 0.4
            adjusted_confidence = base_confidence + adjustment

            return max(0.1, min(1.0, adjusted_confidence))

        except Exception as e:
            logger.error(f"Error applying agent learning: {e}")
            return base_confidence

    async def update_suggestion_outcomes(self):
        """Update suggestion outcomes for learning purposes"""
        with db_manager.get_session() as session:
            try:
                # Find suggestions that were executed and have been held for some time
                executed_suggestions = session.query(TradingSuggestion).filter(
                    TradingSuggestion.status == SuggestionStatus.EXECUTED,
                    TradingSuggestion.executed_at <= datetime.utcnow() - timedelta(days=7)
                ).all()

                for suggestion in executed_suggestions:
                    try:
                        # Get current price and calculate actual outcome
                        ticker = yf.Ticker(suggestion.symbol)
                        current_price = ticker.history(period="1d")['Close'].iloc[-1]

                        if suggestion.suggestion_type == TradingSuggestionType.BUY:
                            actual_return = ((current_price - suggestion.suggested_price) /
                                           suggestion.suggested_price) * 100
                        else:  # SELL
                            actual_return = ((suggestion.suggested_price - current_price) /
                                           suggestion.suggested_price) * 100

                        # Update feedback record
                        feedback = session.query(AgentDecisionFeedback).filter_by(
                            suggestion_id=suggestion.id
                        ).first()

                        if feedback:
                            feedback.actual_outcome = "profitable" if actual_return > 0 else "loss"
                            feedback.outcome_value = actual_return
                            feedback.days_to_outcome = (datetime.utcnow() - suggestion.executed_at).days

                            # Calculate AI accuracy
                            predicted_return = suggestion.predicted_return
                            if predicted_return != 0:
                                accuracy = 1 - abs(actual_return - predicted_return) / abs(predicted_return)
                                feedback.ai_accuracy = max(0, min(1, accuracy))

                            feedback.outcome_determined_at = datetime.utcnow()

                    except Exception as e:
                        logger.error(f"Error updating outcome for suggestion {suggestion.id}: {e}")
                        continue

                logger.info(f"Updated outcomes for {len(executed_suggestions)} suggestions")

            except Exception as e:
                logger.error(f"Error updating suggestion outcomes: {e}")

# Global instance
trading_suggestion_service = TradingSuggestionService()