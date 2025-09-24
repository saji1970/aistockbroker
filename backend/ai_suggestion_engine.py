"""
AI Suggestion Engine
Uses Gemini model and auto trader bot to generate trade suggestions for agents
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
import aiohttp
from dataclasses import dataclass
import yfinance as yf
import pandas as pd
import numpy as np

from gemini_predictor import GeminiStockPredictor
from agent_manager import agent_manager, Customer, TradeSuggestion, CustomerTier
from shadow_trading_bot import ShadowTradingBot

logger = logging.getLogger(__name__)

@dataclass
class MarketAnalysis:
    """Market analysis data structure"""
    symbol: str
    current_price: float
    technical_indicators: Dict
    market_sentiment: str
    volatility: float
    trend_direction: str
    support_levels: List[float]
    resistance_levels: List[float]
    confidence_score: float
    analysis_timestamp: datetime

@dataclass
class AISuggestion:
    """AI-generated trade suggestion"""
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    quantity: int
    price: float
    confidence: float
    reasoning: str
    risk_level: str
    expected_return: float
    time_horizon: str
    ai_model: str
    technical_analysis: Dict
    fundamental_analysis: Dict
    market_conditions: Dict

class AISuggestionEngine:
    """AI-powered suggestion engine for agents"""
    
    def __init__(self):
        self.gemini_predictor = GeminiStockPredictor()
        self.market_data_cache = {}
        self.suggestion_history = []
        self.learning_weights = {}
        
        # Initialize learning weights based on agent feedback
        self._initialize_learning_weights()
    
    def _initialize_learning_weights(self):
        """Initialize learning weights for different factors"""
        self.learning_weights = {
            'technical_indicators': 0.3,
            'fundamental_analysis': 0.25,
            'market_sentiment': 0.2,
            'agent_feedback': 0.15,
            'historical_performance': 0.1
        }
    
    async def generate_suggestions_for_customer(self, customer_id: str, 
                                             max_suggestions: int = 5) -> List[AISuggestion]:
        """Generate AI-powered trade suggestions for a specific customer"""
        try:
            # Get customer data
            customer = agent_manager.customers.get(customer_id)
            if not customer:
                raise ValueError("Customer not found")
            
            # Get customer's current portfolio (if available)
            portfolio_data = await self._get_customer_portfolio(customer_id)
            
            # Get market analysis for watchlist
            watchlist = await self._get_customer_watchlist(customer_id)
            market_analyses = await self._analyze_market_conditions(watchlist)
            
            # Generate suggestions using AI
            suggestions = []
            for analysis in market_analyses:
                if len(suggestions) >= max_suggestions:
                    break
                
                suggestion = await self._generate_single_suggestion(
                    customer, analysis, portfolio_data
                )
                
                if suggestion and suggestion.confidence > 0.6:  # Only high-confidence suggestions
                    suggestions.append(suggestion)
            
            # Sort by confidence and expected return
            suggestions.sort(key=lambda x: (x.confidence, x.expected_return), reverse=True)
            
            # Store suggestions in agent manager
            for suggestion in suggestions:
                trade_suggestion = agent_manager.create_trade_suggestion(
                    customer_id=customer_id,
                    symbol=suggestion.symbol,
                    action=suggestion.action,
                    quantity=suggestion.quantity,
                    price=suggestion.price,
                    confidence=suggestion.confidence,
                    reasoning=suggestion.reasoning,
                    ai_model=suggestion.ai_model
                )
                
                # Add additional data to the suggestion
                trade_suggestion.agent_notes = json.dumps({
                    'risk_level': suggestion.risk_level,
                    'expected_return': suggestion.expected_return,
                    'time_horizon': suggestion.time_horizon,
                    'technical_analysis': suggestion.technical_analysis,
                    'fundamental_analysis': suggestion.fundamental_analysis,
                    'market_conditions': suggestion.market_conditions
                })
            
            logger.info(f"Generated {len(suggestions)} suggestions for customer {customer_id}")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions for customer {customer_id}: {e}")
            return []
    
    async def _get_customer_portfolio(self, customer_id: str) -> Dict:
        """Get customer's current portfolio data"""
        # This would integrate with the actual portfolio system
        # For now, return mock data
        return {
            'total_value': 100000,
            'cash': 20000,
            'positions': {},
            'risk_tolerance': 'medium'
        }
    
    async def _get_customer_watchlist(self, customer_id: str) -> List[str]:
        """Get customer's watchlist symbols"""
        # This would get from customer preferences or agent recommendations
        # For now, return default watchlist
        return ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'META', 'NFLX']
    
    async def _analyze_market_conditions(self, symbols: List[str]) -> List[MarketAnalysis]:
        """Analyze market conditions for given symbols"""
        analyses = []
        
        for symbol in symbols:
            try:
                # Get market data
                market_data = await self._get_market_data(symbol)
                
                # Perform technical analysis
                technical_indicators = await self._calculate_technical_indicators(market_data)
                
                # Get market sentiment
                sentiment = await self._analyze_market_sentiment(symbol)
                
                # Calculate volatility
                volatility = self._calculate_volatility(market_data)
                
                # Determine trend direction
                trend = self._determine_trend(market_data)
                
                # Calculate support and resistance levels
                support_levels, resistance_levels = self._calculate_support_resistance(market_data)
                
                # Calculate confidence score
                confidence = self._calculate_confidence_score(
                    technical_indicators, sentiment, volatility, trend
                )
                
                analysis = MarketAnalysis(
                    symbol=symbol,
                    current_price=market_data['current_price'],
                    technical_indicators=technical_indicators,
                    market_sentiment=sentiment,
                    volatility=volatility,
                    trend_direction=trend,
                    support_levels=support_levels,
                    resistance_levels=resistance_levels,
                    confidence_score=confidence,
                    analysis_timestamp=datetime.now()
                )
                
                analyses.append(analysis)
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        return analyses
    
    async def _get_market_data(self, symbol: str) -> Dict:
        """Get market data for a symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d')}"
            if cache_key in self.market_data_cache:
                return self.market_data_cache[cache_key]
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Get current price
            current_price = hist['Close'].iloc[-1]
            
            # Calculate additional metrics
            data = {
                'symbol': symbol,
                'current_price': float(current_price),
                'historical_data': hist,
                'volume': float(hist['Volume'].iloc[-1]),
                'high_52w': float(hist['High'].max()),
                'low_52w': float(hist['Low'].min()),
                'timestamp': datetime.now()
            }
            
            # Cache the data
            self.market_data_cache[cache_key] = data
            return data
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return {}
    
    async def _calculate_technical_indicators(self, market_data: Dict) -> Dict:
        """Calculate technical indicators"""
        if not market_data or 'historical_data' not in market_data:
            return {}
        
        hist = market_data['historical_data']
        close_prices = hist['Close']
        
        # Calculate RSI
        rsi = self._calculate_rsi(close_prices)
        
        # Calculate MACD
        macd_line, signal_line, histogram = self._calculate_macd(close_prices)
        
        # Calculate Moving Averages
        sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
        sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
        sma_200 = close_prices.rolling(window=200).mean().iloc[-1]
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close_prices)
        
        return {
            'rsi': float(rsi) if not pd.isna(rsi) else 50,
            'macd': {
                'macd_line': float(macd_line) if not pd.isna(macd_line) else 0,
                'signal_line': float(signal_line) if not pd.isna(signal_line) else 0,
                'histogram': float(histogram) if not pd.isna(histogram) else 0
            },
            'moving_averages': {
                'sma_20': float(sma_20) if not pd.isna(sma_20) else 0,
                'sma_50': float(sma_50) if not pd.isna(sma_50) else 0,
                'sma_200': float(sma_200) if not pd.isna(sma_200) else 0
            },
            'bollinger_bands': {
                'upper': float(bb_upper) if not pd.isna(bb_upper) else 0,
                'middle': float(bb_middle) if not pd.isna(bb_middle) else 0,
                'lower': float(bb_lower) if not pd.isna(bb_lower) else 0
            }
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper.iloc[-1], sma.iloc[-1], lower.iloc[-1]
    
    async def _analyze_market_sentiment(self, symbol: str) -> str:
        """Analyze market sentiment using Gemini"""
        try:
            # Create sentiment analysis prompt
            prompt = f"""
            Analyze the market sentiment for {symbol} stock. Consider:
            1. Recent news and events
            2. Technical indicators
            3. Market trends
            4. Investor sentiment
            
            Provide a sentiment analysis with one of these classifications:
            - "very_bullish"
            - "bullish" 
            - "neutral"
            - "bearish"
            - "very_bearish"
            
            Also provide a brief reasoning for your classification.
            """
            
            response = await self.gemini_predictor.predict_async(prompt)
            
            # Parse response to extract sentiment
            sentiment = "neutral"  # Default
            if "very_bullish" in response.lower():
                sentiment = "very_bullish"
            elif "bullish" in response.lower():
                sentiment = "bullish"
            elif "bearish" in response.lower():
                sentiment = "bearish"
            elif "very_bearish" in response.lower():
                sentiment = "very_bearish"
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return "neutral"
    
    def _calculate_volatility(self, market_data: Dict) -> float:
        """Calculate price volatility"""
        if 'historical_data' not in market_data:
            return 0.0
        
        hist = market_data['historical_data']
        returns = hist['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized volatility
        return float(volatility)
    
    def _determine_trend(self, market_data: Dict) -> str:
        """Determine trend direction"""
        if 'historical_data' not in market_data:
            return "sideways"
        
        hist = market_data['historical_data']
        close_prices = hist['Close']
        
        # Calculate short and long term trends
        short_trend = close_prices.tail(20).mean() - close_prices.tail(40).mean()
        long_trend = close_prices.tail(50).mean() - close_prices.tail(100).mean()
        
        if short_trend > 0 and long_trend > 0:
            return "strong_uptrend"
        elif short_trend > 0:
            return "uptrend"
        elif short_trend < 0 and long_trend < 0:
            return "strong_downtrend"
        elif short_trend < 0:
            return "downtrend"
        else:
            return "sideways"
    
    def _calculate_support_resistance(self, market_data: Dict) -> Tuple[List[float], List[float]]:
        """Calculate support and resistance levels"""
        if 'historical_data' not in market_data:
            return [], []
        
        hist = market_data['historical_data']
        high_prices = hist['High']
        low_prices = hist['Low']
        
        # Simple support/resistance calculation
        support_levels = low_prices.tail(20).nsmallest(3).tolist()
        resistance_levels = high_prices.tail(20).nlargest(3).tolist()
        
        return support_levels, resistance_levels
    
    def _calculate_confidence_score(self, technical_indicators: Dict, sentiment: str, 
                                  volatility: float, trend: str) -> float:
        """Calculate overall confidence score"""
        score = 0.5  # Base score
        
        # Technical indicators contribution
        if technical_indicators:
            rsi = technical_indicators.get('rsi', 50)
            if 30 <= rsi <= 70:  # Neutral RSI
                score += 0.1
            elif rsi < 30 or rsi > 70:  # Extreme RSI
                score += 0.2
        
        # Sentiment contribution
        sentiment_scores = {
            'very_bullish': 0.2,
            'bullish': 0.1,
            'neutral': 0.0,
            'bearish': -0.1,
            'very_bearish': -0.2
        }
        score += sentiment_scores.get(sentiment, 0.0)
        
        # Volatility contribution (lower volatility = higher confidence)
        if volatility < 0.2:
            score += 0.1
        elif volatility > 0.4:
            score -= 0.1
        
        # Trend contribution
        trend_scores = {
            'strong_uptrend': 0.2,
            'uptrend': 0.1,
            'sideways': 0.0,
            'downtrend': -0.1,
            'strong_downtrend': -0.2
        }
        score += trend_scores.get(trend, 0.0)
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    async def _generate_single_suggestion(self, customer: Customer, 
                                         analysis: MarketAnalysis, 
                                         portfolio_data: Dict) -> Optional[AISuggestion]:
        """Generate a single trade suggestion using AI"""
        try:
            # Create comprehensive analysis prompt for Gemini
            prompt = f"""
            As an expert financial advisor, analyze the following stock and provide a trade recommendation:
            
            Stock: {analysis.symbol}
            Current Price: ${analysis.current_price:.2f}
            Market Sentiment: {analysis.market_sentiment}
            Volatility: {analysis.volatility:.2%}
            Trend: {analysis.trend_direction}
            RSI: {analysis.technical_indicators.get('rsi', 'N/A')}
            
            Customer Profile:
            - Risk Tolerance: {customer.risk_tolerance}
            - Customer Tier: {customer.tier.value}
            - Current Portfolio Value: ${portfolio_data.get('total_value', 0):,.2f}
            
            Technical Analysis:
            {json.dumps(analysis.technical_indicators, indent=2)}
            
            Please provide:
            1. Action: 'buy', 'sell', or 'hold'
            2. Quantity: Number of shares (considering customer's risk tolerance)
            3. Price: Recommended price per share
            4. Confidence: 0.0 to 1.0
            5. Reasoning: Detailed explanation
            6. Risk Level: 'low', 'medium', or 'high'
            7. Expected Return: Expected percentage return
            8. Time Horizon: 'short' (1-3 months), 'medium' (3-12 months), or 'long' (1+ years)
            
            Format your response as JSON with these exact keys.
            """
            
            # Get AI prediction
            response = await self.gemini_predictor.predict_async(prompt)
            
            # Parse JSON response
            try:
                suggestion_data = json.loads(response)
            except json.JSONDecodeError:
                # If not JSON, try to extract key information
                suggestion_data = self._parse_text_response(response)
            
            # Create suggestion object
            suggestion = AISuggestion(
                symbol=analysis.symbol,
                action=suggestion_data.get('action', 'hold'),
                quantity=int(suggestion_data.get('quantity', 0)),
                price=float(suggestion_data.get('price', analysis.current_price)),
                confidence=float(suggestion_data.get('confidence', 0.5)),
                reasoning=suggestion_data.get('reasoning', 'AI analysis'),
                risk_level=suggestion_data.get('risk_level', 'medium'),
                expected_return=float(suggestion_data.get('expected_return', 0.0)),
                time_horizon=suggestion_data.get('time_horizon', 'medium'),
                ai_model='gemini',
                technical_analysis=analysis.technical_indicators,
                fundamental_analysis={},
                market_conditions={
                    'sentiment': analysis.market_sentiment,
                    'volatility': analysis.volatility,
                    'trend': analysis.trend_direction
                }
            )
            
            return suggestion
            
        except Exception as e:
            logger.error(f"Error generating suggestion for {analysis.symbol}: {e}")
            return None
    
    def _parse_text_response(self, response: str) -> Dict:
        """Parse text response to extract suggestion data"""
        # Simple parsing logic - in production, use more sophisticated NLP
        suggestion_data = {
            'action': 'hold',
            'quantity': 0,
            'price': 0.0,
            'confidence': 0.5,
            'reasoning': response,
            'risk_level': 'medium',
            'expected_return': 0.0,
            'time_horizon': 'medium'
        }
        
        # Try to extract action
        if 'buy' in response.lower():
            suggestion_data['action'] = 'buy'
        elif 'sell' in response.lower():
            suggestion_data['action'] = 'sell'
        
        return suggestion_data
    
    def update_learning_weights(self, feedback_data: Dict):
        """Update learning weights based on agent feedback"""
        try:
            # Analyze feedback patterns
            if feedback_data.get('agent_acceptance_rate', 0) > 0.8:
                # Agent accepts most suggestions - increase AI confidence
                self.learning_weights['agent_feedback'] += 0.05
            elif feedback_data.get('agent_acceptance_rate', 0) < 0.3:
                # Agent rejects most suggestions - decrease AI confidence
                self.learning_weights['agent_feedback'] -= 0.05
            
            # Normalize weights
            total_weight = sum(self.learning_weights.values())
            for key in self.learning_weights:
                self.learning_weights[key] /= total_weight
            
            logger.info(f"Updated learning weights: {self.learning_weights}")
            
        except Exception as e:
            logger.error(f"Error updating learning weights: {e}")

# Global instance
ai_suggestion_engine = AISuggestionEngine()
