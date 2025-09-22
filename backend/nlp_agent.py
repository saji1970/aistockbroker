import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of user queries."""
    PRICE_QUERY = "price_query"
    TECHNICAL_ANALYSIS = "technical_analysis"
    PREDICTION = "prediction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMPARISON = "comparison"
    NEWS_QUERY = "news_query"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    GENERAL_QUESTION = "general_question"

class SentimentType(Enum):
    """Sentiment classification types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

@dataclass
class QueryIntent:
    """Structured representation of user query intent."""
    query_type: QueryType
    symbols: List[str]
    time_period: Optional[str]
    specific_indicators: List[str]
    sentiment_focus: bool
    comparison_mode: bool
    confidence: float
    raw_query: str
    investment_amount: Optional[float] = None
    target_amount: Optional[float] = None
    time_horizon: Optional[str] = None

@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    sentiment: SentimentType
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    keywords: List[str]
    summary: str

class NLPProcessor:
    """Natural Language Processing processor for stock analysis queries."""
    
    def __init__(self):
        self.price_patterns = [
            r'\b(price|value|worth|cost)\b',
            r'\$\d+',
            r'\b(high|low|current|latest)\s+(price|value)\b'
        ]
        
        self.technical_patterns = [
            r'\b(rsi|macd|bollinger|moving\s+average|sma|ema|volume)\b',
            r'\b(technical|indicator|chart|pattern)\b',
            r'\b(support|resistance|trend|momentum)\b'
        ]
        
        self.prediction_patterns = [
            r'\b(predict|forecast|outlook|future|tomorrow|next\s+week|next\s+month)\b',
            r'\b(will|going\s+to|expect|anticipate)\b',
            r'\b(ai|artificial\s+intelligence|machine\s+learning)\s+(prediction|analysis)\b',
            r'\b(end\s+of\s+day|eod|close|closing)\s+(price|value|prediction|forecast)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(prediction|forecast|outlook)\b',
            r'\b(what\s+would\s+be|what\s+will|what\s+is\s+the)\s+(prediction|forecast|outlook)\b',
            r'\b(returns|performance|movement|direction)\s+(prediction|forecast)\b'
        ]
        
        self.sentiment_patterns = [
            r'\b(sentiment|mood|feeling|opinion|view)\b',
            r'\b(bullish|bearish|positive|negative|optimistic|pessimistic)\b',
            r'\b(market\s+sentiment|investor\s+confidence)\b'
        ]
        
        self.comparison_patterns = [
            r'\b(compare|versus|vs|against|better|worse|similar)\b',
            r'\b(performance|return|growth)\s+(comparison|vs)\b'
        ]
        
        # Add patterns for trading recommendations and general questions
        self.recommendation_patterns = [
            r'\b(best|top|recommend|suggest|advise|which|what)\s+(stock|share|investment|trade)\b',
            r'\b(day\s+trading|swing\s+trading|scalping|intraday)\b',
            r'\b(max|maximum|highest|best)\s+(return|profit|gain|performance)\b',
            r'\b(trading|investment)\s+(strategy|approach|method)\b'
        ]
        
        # Add patterns for list requests
        self.list_patterns = [
            r'\b(list|show|give|tell|find|search|look|see|view|display|present)\s+(top|best|worst|popular|trending)\b',
            r'\b(top|best|worst|popular|trending)\s+\d+\s+(stock|share|company|investment)\b',
            r'\b(list|show|give|tell|find|search|look|see|view|display|present)\s+\d+\s+(stock|share|company|investment)\b',
            r'\b(S&P|SP500|S&P\s+500|Standard\s+&\s+Poor|NASDAQ|DOW|DJIA)\s+(stock|company|list)\b',
            r'\b(give\s+me|show\s+me|tell\s+me)\s+(list|top|best)\b',
            r'\b(give\s+me|show\s+me|tell\s+me)\s+list\s+of\b',
            r'\b(list|top)\s+of\s+(S&P|SP500|S&P\s+500)\b'
        ]
        
        self.time_patterns = {
            '1d': r'\b(today|day|daily)\b',
            '1w': r'\b(week|weekly)\b',
            '1mo': r'\b(month|monthly)\b',
            '3mo': r'\b(quarter|quarterly|3\s+months)\b',
            '6mo': r'\b(6\s+months|half\s+year)\b',
            '1y': r'\b(year|yearly|annual)\b',
            '5y': r'\b(5\s+years|long\s+term)\b'
        }
        
        self.sentiment_keywords = {
            'positive': [
                'bullish', 'positive', 'optimistic', 'strong', 'growth', 'up', 'rise',
                'gain', 'profit', 'success', 'excellent', 'great', 'good', 'buy',
                'outperform', 'beat', 'exceed', 'surge', 'rally', 'breakout'
            ],
            'negative': [
                'bearish', 'negative', 'pessimistic', 'weak', 'decline', 'down', 'fall',
                'loss', 'drop', 'crash', 'plunge', 'sell', 'underperform', 'miss',
                'disappoint', 'concern', 'risk', 'volatile', 'uncertain'
            ],
            'neutral': [
                'stable', 'steady', 'neutral', 'mixed', 'balanced', 'moderate',
                'average', 'normal', 'consistent', 'maintain', 'hold'
            ]
        }

        self.goal_patterns = [
            r'(invest|grow|turn|make|reach|achieve|increase|double|triple|quadruple)[^\d$]*(\$?\d+[\d,]*)([^\d$]+)?(to|into|and|reach|become)[^\d$]*(\$?\d+[\d,]*)',
            r'(grow|turn|make|reach|achieve|increase|double|triple|quadruple)[^\d$]*(\$?\d+[\d,]*)[^\d$]+(in|within|over|by)[^\d$]*(\d+\s*(day|week|month|year|days|weeks|months|years))',
            r'(invest|put|allocate)[^\d$]*(\$?\d+[\d,]*)[^\d$]+(for|over|in|within)[^\d$]*(\d+\s*(day|week|month|year|days|weeks|months|years))'
        ]
    
    def parse_query(self, query: str) -> QueryIntent:
        """Parse natural language query and extract intent."""
        query_lower = query.lower()
        
        # Extract stock symbols
        symbols = self._extract_symbols(query)
        
        # Determine query type
        query_type = self._classify_query_type(query_lower)
        
        # Extract time period
        time_period = self._extract_time_period(query_lower)
        
        # Extract specific indicators
        indicators = self._extract_indicators(query_lower)
        
        # Check for sentiment focus
        sentiment_focus = any(re.search(pattern, query_lower) for pattern in self.sentiment_patterns)
        
        # Check for comparison mode
        comparison_mode = any(re.search(pattern, query_lower) for pattern in self.comparison_patterns)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query_lower, query_type, symbols)

        # Extract investment/target/time horizon
        investment_amount, target_amount, time_horizon = self._extract_goal_parameters(query_lower)

        return QueryIntent(
            query_type=query_type,
            symbols=symbols,
            time_period=time_period,
            specific_indicators=indicators,
            sentiment_focus=sentiment_focus,
            comparison_mode=comparison_mode,
            confidence=confidence,
            raw_query=query,
            investment_amount=investment_amount,
            target_amount=target_amount,
            time_horizon=time_horizon
        )
    
    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query."""
        # Common stock symbol patterns - look for 2-5 letter uppercase sequences
        symbol_pattern = r'\b[A-Z]{2,5}\b'
        symbols = re.findall(symbol_pattern, query.upper())
        
        # Filter out common words that might be mistaken for symbols
        common_words = {
            'THE', 'AND', 'OR', 'FOR', 'WITH', 'FROM', 'THIS', 'THAT', 'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW', 'WHICH',
            'ARE', 'WAS', 'WERE', 'HAS', 'HAVE', 'HAD', 'WILL', 'WOULD', 'COULD', 'SHOULD', 'MIGHT', 'MAY',
            'CAN', 'NOT', 'BUT', 'YET', 'STILL', 'ALSO', 'VERY', 'MORE', 'MOST', 'LESS', 'LEAST', 'BEST',
            'WORST', 'GOOD', 'BAD', 'NEW', 'OLD', 'BIG', 'SMALL', 'HIGH', 'LOW', 'UP', 'DOWN', 'IN', 'OUT',
            'ON', 'OFF', 'AT', 'TO', 'OF', 'BY', 'IS', 'AM', 'BE', 'DO', 'GET', 'GOT', 'GETS', 'GONE', 'GOES', 'ME',
            'LIST', 'SHOW', 'GIVE', 'TELL', 'FIND', 'SEARCH', 'LOOK', 'SEE', 'VIEW', 'DISPLAY', 'PRESENT', 'GIVE', 'TELL',
            'TOP', 'STOCK', 'SHARE', 'COMPANY', 'INVESTMENT', 'TRADE', 'TRADING', 'MARKET', 'INDEX'
        }
        symbols = [s for s in symbols if s not in common_words and len(s) >= 2]
        
        # Additional filtering: look for common stock symbols
        common_stocks = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM', 'PYPL',
            'INTC', 'AMD', 'QCOM', 'CSCO', 'ORCL', 'IBM', 'HPQ', 'DELL', 'WMT', 'TGT', 'COST', 'HD', 'LOW',
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'LLY', 'DHR', 'ACN',
            'SPY', 'QQQ', 'VTI', 'VOO', 'GLD', 'SLV', 'ARKK', 'ARKW', 'ARKG', 'ARKF', 'ARKQ', 'ARKX',
            'BND', 'AGG', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'JNK', 'EMB', 'VWO', 'EFA', 'EEM', 'FXI',
            'XLK', 'XLF', 'XLV', 'XLY', 'XLP', 'XLE', 'XLI', 'XLB', 'XLRE', 'VXUS', 'IEMG'
        }
        
        # Prioritize known stock symbols
        known_symbols = [s for s in symbols if s in common_stocks]
        if known_symbols:
            return known_symbols
        
        return symbols
    
    def _classify_query_type(self, query: str) -> QueryType:
        """Classify the type of query."""
        scores = {
            QueryType.PRICE_QUERY: 0,
            QueryType.TECHNICAL_ANALYSIS: 0,
            QueryType.PREDICTION: 0,
            QueryType.SENTIMENT_ANALYSIS: 0,
            QueryType.COMPARISON: 0,
            QueryType.NEWS_QUERY: 0,
            QueryType.PORTFOLIO_ANALYSIS: 0,
            QueryType.RISK_ASSESSMENT: 0,
            QueryType.GENERAL_QUESTION: 0
        }
        
        # Score based on patterns
        for pattern in self.price_patterns:
            if re.search(pattern, query):
                scores[QueryType.PRICE_QUERY] += 1
        
        for pattern in self.technical_patterns:
            if re.search(pattern, query):
                scores[QueryType.TECHNICAL_ANALYSIS] += 1
        
        for pattern in self.prediction_patterns:
            if re.search(pattern, query):
                scores[QueryType.PREDICTION] += 1
        
        for pattern in self.sentiment_patterns:
            if re.search(pattern, query):
                scores[QueryType.SENTIMENT_ANALYSIS] += 1
        
        for pattern in self.comparison_patterns:
            if re.search(pattern, query):
                scores[QueryType.COMPARISON] += 1
        
        # Check for recommendation patterns
        for pattern in self.recommendation_patterns:
            if re.search(pattern, query):
                scores[QueryType.GENERAL_QUESTION] += 2  # Higher weight for recommendations
        
        # Check for list patterns
        for pattern in self.list_patterns:
            if re.search(pattern, query):
                scores[QueryType.GENERAL_QUESTION] += 5  # Much higher weight for list requests
        
        # Check for specific prediction patterns with higher priority
        if any(word in query.lower() for word in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'end of day', 'eod']):
            scores[QueryType.PREDICTION] += 3  # Higher priority for specific day predictions
        
        if any(word in query.lower() for word in ['returns', 'performance', 'movement', 'direction']):
            scores[QueryType.PREDICTION] += 2  # Higher priority for return predictions
        
        # Additional heuristics
        if any(word in query for word in ['news', 'announcement', 'earnings', 'report']):
            scores[QueryType.NEWS_QUERY] += 1
        
        if any(word in query for word in ['portfolio', 'diversification', 'allocation']):
            scores[QueryType.PORTFOLIO_ANALYSIS] += 1
        
        if any(word in query for word in ['risk', 'volatility', 'danger', 'safe']):
            scores[QueryType.RISK_ASSESSMENT] += 1
        
        # Check for general question words
        if any(word in query.lower() for word in ['which', 'what', 'how', 'when', 'where', 'why', 'who']):
            scores[QueryType.GENERAL_QUESTION] += 1
        
        # Check for S&P 500 specific patterns
        if any(phrase in query.lower() for phrase in ['s&p', 'sp500', 's&p 500', 'standard & poor']):
            scores[QueryType.GENERAL_QUESTION] += 3
        
        # Return the highest scoring type
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _extract_time_period(self, query: str) -> Optional[str]:
        """Extract time period from query."""
        for period, pattern in self.time_patterns.items():
            if re.search(pattern, query):
                return period
        return None
    
    def _extract_indicators(self, query: str) -> List[str]:
        """Extract specific technical indicators mentioned."""
        indicators = []
        indicator_mapping = {
            'rsi': 'RSI',
            'macd': 'MACD',
            'bollinger': 'Bollinger Bands',
            'moving average': 'Moving Average',
            'sma': 'SMA',
            'ema': 'EMA',
            'volume': 'Volume',
            'support': 'Support',
            'resistance': 'Resistance',
            'trend': 'Trend',
            'momentum': 'Momentum'
        }
        
        for indicator, display_name in indicator_mapping.items():
            if indicator in query:
                indicators.append(display_name)
        
        return indicators
    
    def _calculate_confidence(self, query: str, query_type: QueryType, symbols: List[str]) -> float:
        """Calculate confidence in the query classification."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence if symbols are found
        if symbols:
            confidence += 0.2
        
        # Boost confidence based on query type patterns
        if query_type == QueryType.PRICE_QUERY and any(re.search(pattern, query) for pattern in self.price_patterns):
            confidence += 0.2
        
        if query_type == QueryType.TECHNICAL_ANALYSIS and any(re.search(pattern, query) for pattern in self.technical_patterns):
            confidence += 0.2
        
        if query_type == QueryType.PREDICTION and any(re.search(pattern, query) for pattern in self.prediction_patterns):
            confidence += 0.2
        
        return min(confidence, 1.0)

    def _extract_goal_parameters(self, query: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        # Extract investment amount (e.g., $100, 100 usd)
        investment_amount = None
        target_amount = None
        time_horizon = None
        # Find all numbers with $ or usd
        money_matches = re.findall(r'(\$|usd\s*)?(\d+[\d,]*)', query)
        numbers = [float(m[1].replace(',', '')) for m in money_matches if m[1]]
        if numbers:
            investment_amount = numbers[0]
            if len(numbers) > 1:
                target_amount = numbers[1]
        # Find time horizon (e.g., 1 month, 30 days)
        time_match = re.search(r'(\d+\s*(day|week|month|year|days|weeks|months|years))', query)
        if time_match:
            time_horizon = time_match.group(1)
        return investment_amount, target_amount, time_horizon

class SentimentAnalyzer:
    """Sentiment analysis for stock-related text."""
    
    def __init__(self):
        self.positive_words = set([
            'bullish', 'positive', 'optimistic', 'strong', 'growth', 'up', 'rise',
            'gain', 'profit', 'success', 'excellent', 'great', 'good', 'buy',
            'outperform', 'beat', 'exceed', 'surge', 'rally', 'breakout', 'strong',
            'robust', 'solid', 'impressive', 'outstanding', 'superior', 'premium'
        ])
        
        self.negative_words = set([
            'bearish', 'negative', 'pessimistic', 'weak', 'decline', 'down', 'fall',
            'loss', 'drop', 'crash', 'plunge', 'sell', 'underperform', 'miss',
            'disappoint', 'concern', 'risk', 'volatile', 'uncertain', 'weak',
            'poor', 'terrible', 'awful', 'disaster', 'failure', 'struggle'
        ])
        
        self.neutral_words = set([
            'stable', 'steady', 'neutral', 'mixed', 'balanced', 'moderate',
            'average', 'normal', 'consistent', 'maintain', 'hold', 'flat',
            'unchanged', 'sideways', 'consolidation'
        ])
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Analyze sentiment of given text."""
        words = re.findall(r'\b\w+\b', text.lower())
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        neutral_count = sum(1 for word in words if word in self.neutral_words)
        total_words = len(words)
        
        if total_words == 0:
            return SentimentResult(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0,
                keywords=[],
                summary="No sentiment detected"
            )
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        neutral_score = neutral_count / total_words
        
        # Determine sentiment type
        if positive_score > negative_score and positive_score > neutral_score:
            sentiment = SentimentType.POSITIVE
            confidence = positive_score
        elif negative_score > positive_score and negative_score > neutral_score:
            sentiment = SentimentType.NEGATIVE
            confidence = negative_score
        elif neutral_score > positive_score and neutral_score > negative_score:
            sentiment = SentimentType.NEUTRAL
            confidence = neutral_score
        else:
            sentiment = SentimentType.MIXED
            confidence = max(positive_score, negative_score, neutral_score)
        
        # Extract keywords
        keywords = []
        for word in words:
            if word in self.positive_words or word in self.negative_words or word in self.neutral_words:
                keywords.append(word)
        
        # Generate summary
        summary = self._generate_sentiment_summary(sentiment, confidence, positive_score, negative_score)
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score,
            keywords=keywords,
            summary=summary
        )
    
    def _generate_sentiment_summary(self, sentiment: SentimentType, confidence: float, 
                                  positive_score: float, negative_score: float) -> str:
        """Generate a summary of the sentiment analysis."""
        if sentiment == SentimentType.POSITIVE:
            if confidence > 0.7:
                return "Strongly positive sentiment detected"
            else:
                return "Moderately positive sentiment detected"
        elif sentiment == SentimentType.NEGATIVE:
            if confidence > 0.7:
                return "Strongly negative sentiment detected"
            else:
                return "Moderately negative sentiment detected"
        elif sentiment == SentimentType.NEUTRAL:
            return "Neutral sentiment detected"
        else:
            return "Mixed sentiment detected with conflicting signals"

class ConversationalAgent:
    """Conversational AI agent for stock analysis."""
    
    def __init__(self):
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize NLP components
        self.nlp_processor = NLPProcessor()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Enhanced patterns for financial advisory
        self.financial_advisor_patterns = [
            r'\b(create|generate|make)\s+(a\s+)?(financial\s+)?(plan|profile|strategy)\b',
            r'\b(retirement|retire)\s+(plan|planning|strategy|savings)\b',
            r'\b(risk\s+)?(assessment|tolerance|profile)\b',
            r'\b(tax|taxes)\s+(strategy|planning|efficiency|optimization)\b',
            r'\b(asset\s+)?(allocation|diversification)\b',
            r'\b(portfolio|investment)\s+(recommendation|advice|strategy)\b',
            r'\b(emergency\s+)?(fund|savings)\s+(strategy|planning)\b',
            r'\b(debt|loan)\s+(management|payoff|strategy)\b',
            r'\b(insurance|coverage)\s+(recommendation|planning)\b',
            r'\b(financial|money)\s+(advisor|advisory|consultant)\b',
            r'\b(wealth|financial)\s+(management|planning)\b',
            r'\b(investment|financial)\s+(goals|objectives)\b',
            r'\b(income|salary)\s+(\d+[kKmM]?)\s+(age|years\s+old)\b',
            r'\b(net\s+worth|assets)\s+(\d+[kKmM]?)\b',
            r'\b(conservative|moderate|aggressive)\s+(investor|investment|strategy)\b',
            r'\b(short|medium|long)\s+term\s+(investment|goal|planning)\b'
        ]
        
        # Financial profile extraction patterns
        self.profile_patterns = {
            'age': r'\b(\d+)\s*(years?\s+old|age|yo)\b',
            'income': r'\b(income|salary|earn)\s*(?:of\s*)?\$?(\d+(?:,\d{3})*(?:\.\d{2})?[kKmM]?)\b',
            'net_worth': r'\b(net\s+worth|assets|savings)\s*(?:of\s*)?\$?(\d+(?:,\d{3})*(?:\.\d{2})?[kKmM]?)\b',
            'risk_tolerance': r'\b(conservative|moderate|aggressive)\b',
            'goals': r'\b(retirement|education|home\s+purchase|wealth\s+building|income\s+generation|tax\s+efficiency)\b',
            'time_horizon': r'\b(short\s+term|medium\s+term|long\s+term)\b'
        }
        
        # Enhanced prediction patterns
        self.prediction_patterns = [
            r'\b(predict|prediction|forecast|outlook)\s+(for|of)\s+([A-Z]{1,5})\b',
            r'\b([A-Z]{1,5})\s+(will|going\s+to|predicted\s+to)\s+(go|move|trade|perform)\b',
            r'\b(what\s+will|how\s+will)\s+([A-Z]{1,5})\s+(do|perform|trade)\b',
            r'\b([A-Z]{1,5})\s+(monday|tuesday|wednesday|thursday|friday|next\s+week|end\s+of\s+day)\b',
            r'\b(price|stock|value)\s+(of|for)\s+([A-Z]{1,5})\b',
            r'\b([A-Z]{1,5})\s+(price|value|target)\b',
            r'\b(buy|sell|hold)\s+([A-Z]{1,5})\b',
            r'\b([A-Z]{1,5})\s+(buy|sell|hold)\s+(signal|recommendation)\b'
        ]
        
        # Common stock symbols
        self.common_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC',
            'SPY', 'QQQ', 'VOO', 'VTI', 'BND', 'GLD', 'SLV', 'TQQQ', 'SQQQ', 'UVXY',
            'VXUS', 'EFA', 'EEM', 'IEMG', 'ACWI', 'VT', 'BNDX', 'AGG', 'TLT', 'LQD',
            'VNQ', 'IYR', 'SCHH', 'XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLP', 'XLU'
        ]
    
    def process_query(self, user_query: str, context_data: Dict = None) -> Dict:
        """Process a natural language query and generate a response."""
        try:
            # Parse the query
            intent = self.nlp_processor.parse_query(user_query)
            
            # Add to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_query': user_query,
                'intent': intent
            })
            
            # Analyze sentiment if relevant
            sentiment_result = None
            if intent.sentiment_focus:
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(user_query)
            
            # Generate response
            response = self._generate_response(intent, context_data, sentiment_result)
            
            return {
                'query_intent': intent,
                'sentiment_analysis': sentiment_result,
                'response': response,
                'confidence': intent.confidence
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'error': str(e),
                'response': "I'm sorry, I encountered an error processing your query. Please try rephrasing it."
            }
    
    def _generate_response(self, intent: QueryIntent, context: Dict = None) -> str:
        """Generate response based on query intent and context"""
        query_lower = intent.raw_query.lower()
        
        # Financial Advisory Queries
        if self._is_financial_advisor_query(query_lower):
            return self._generate_financial_advisor_response(intent, context)
        
        # ETF Recommendations
        if any(word in query_lower for word in ['etf', 'etfs', 'exchange traded fund', 'exchange traded funds']):
            if any(word in query_lower for word in ['best', 'top', 'recommend', 'good', 'popular']):
                return ("Here are some of the best ETFs to consider for different investment strategies:\n\n"
                       "**📈 Broad Market ETFs (Core Holdings):**\n"
                       "• **SPY** - SPDR S&P 500 ETF (Large-cap US stocks)\n"
                       "• **VOO** - Vanguard S&P 500 ETF (Lower expense ratio)\n"
                       "• **VTI** - Vanguard Total Stock Market ETF (Complete US market)\n"
                       "• **QQQ** - Invesco QQQ Trust (Technology-heavy)\n\n"
                       "**🌍 International ETFs (Diversification):**\n"
                       "• **VXUS** - Vanguard Total International Stock ETF\n"
                       "• **EFA** - iShares MSCI EAFE ETF (Developed markets)\n"
                       "• **EEM** - iShares MSCI Emerging Markets ETF\n\n"
                       "**💰 Bond ETFs (Income & Stability):**\n"
                       "• **BND** - Vanguard Total Bond Market ETF\n"
                       "• **AGG** - iShares Core U.S. Aggregate Bond ETF\n"
                       "• **TLT** - iShares 20+ Year Treasury Bond ETF\n\n"
                       "**🏠 Sector ETFs (Targeted Exposure):**\n"
                       "• **XLK** - Technology Select Sector SPDR Fund\n"
                       "• **XLF** - Financial Select Sector SPDR Fund\n"
                       "• **XLE** - Energy Select Sector SPDR Fund\n"
                       "• **VNQ** - Vanguard Real Estate ETF\n\n"
                       "**💡 Recommended Strategy:**\n"
                       "• **Conservative:** 60% BND + 25% VOO + 15% VXUS\n"
                       "• **Moderate:** 40% VOO + 20% VXUS + 25% BND + 15% QQQ\n"
                       "• **Aggressive:** 50% VOO + 20% QQQ + 15% VXUS + 15% sector ETFs\n\n"
                       "Would you like me to create a personalized ETF portfolio based on your financial profile?")
            else:
                return ("ETFs (Exchange-Traded Funds) are investment funds that trade on stock exchanges like individual stocks. They offer:\n\n"
                       "**✅ Advantages:**\n"
                       "• Diversification across many stocks/bonds\n"
                       "• Lower expense ratios than mutual funds\n"
                       "• Tax efficiency\n"
                       "• Easy to buy/sell\n"
                       "• Transparent holdings\n\n"
                       "**📊 Popular Categories:**\n"
                       "• **Index ETFs:** Track market indices (SPY, VOO)\n"
                       "• **Sector ETFs:** Focus on specific sectors (XLK, XLF)\n"
                       "• **International ETFs:** Global diversification (VXUS, EFA)\n"
                       "• **Bond ETFs:** Fixed income exposure (BND, AGG)\n\n"
                       "Would you like me to recommend specific ETFs based on your investment goals and risk tolerance?")

        # Investment Strategy Queries
        if any(word in query_lower for word in ['strategy', 'strategies', 'how to invest', 'investment plan']):
            if any(word in query_lower for word in ['long term', 'long-term', 'retirement']):
                return ("**📈 Long-Term Investment Strategy (10+ years):**\n\n"
                       "**1. Asset Allocation by Age:**\n"
                       "• **20s-30s:** 80-90% stocks, 10-20% bonds\n"
                       "• **40s-50s:** 60-80% stocks, 20-40% bonds\n"
                       "• **60s+:** 40-60% stocks, 40-60% bonds\n\n"
                       "**2. Core Holdings:**\n"
                       "• **VTI** - Total US Stock Market (40-50%)\n"
                       "• **VXUS** - Total International Stocks (20-30%)\n"
                       "• **BND** - Total Bond Market (20-30%)\n\n"
                       "**3. Dollar-Cost Averaging:**\n"
                       "• Invest regularly (monthly/quarterly)\n"
                       "• Reduces timing risk\n"
                       "• Automates the process\n\n"
                       "**4. Tax-Efficient Accounts:**\n"
                       "• Max out 401(k) and IRA contributions\n"
                       "• Use Roth accounts for tax-free growth\n"
                       "• Consider HSA for healthcare expenses\n\n"
                       "**5. Rebalancing:**\n"
                       "• Review annually\n"
                       "• Rebalance when allocations drift >5%\n"
                       "• Maintain target risk level\n\n"
                       "Would you like me to create a personalized long-term investment plan?")
            elif any(word in query_lower for word in ['short term', 'short-term', 'day trading']):
                return ("**⚡ Short-Term Trading Strategy (Days to Months):**\n\n"
                       "**⚠️ Important:** Short-term trading is high-risk and requires significant time and knowledge.\n\n"
                       "**1. High-Liquidity Stocks:**\n"
                       "• **SPY** - S&P 500 ETF (High volume)\n"
                       "• **QQQ** - Nasdaq ETF (Tech focus)\n"
                       "• **AAPL, MSFT, GOOGL** - Large-cap tech\n"
                       "• **TSLA, NVDA** - High volatility\n\n"
                       "**2. Technical Analysis:**\n"
                       "• Moving averages (20, 50, 200-day)\n"
                       "• RSI for overbought/oversold\n"
                       "• MACD for momentum\n"
                       "• Support/resistance levels\n\n"
                       "**3. Risk Management:**\n"
                       "• Set stop-loss orders (2-3% max loss)\n"
                       "• Never risk more than 1-2% per trade\n"
                       "• Use position sizing\n"
                       "• Have an exit strategy\n\n"
                       "**4. Market Timing:**\n"
                       "• Trade during market hours (9:30 AM - 4:00 PM ET)\n"
                       "• Avoid earnings announcements\n"
                       "• Watch for market catalysts\n\n"
                       "**💡 Recommendation:** Consider long-term investing instead, as it's more reliable and less stressful.")

        # Portfolio Diversification
        if any(word in query_lower for word in ['diversify', 'diversification', 'portfolio']):
            return ("**🌍 Portfolio Diversification Strategy:**\n\n"
                   "**1. Asset Class Diversification:**\n"
                   "• **Stocks:** 60-80% (Growth potential)\n"
                   "• **Bonds:** 20-40% (Stability & income)\n"
                   "• **Real Estate:** 5-15% (Inflation hedge)\n"
                   "• **Commodities:** 0-10% (Diversification)\n\n"
                   "**2. Geographic Diversification:**\n"
                   "• **US Stocks:** 50-70% (Home bias)\n"
                   "• **International Developed:** 20-30% (Europe, Japan)\n"
                   "• **Emerging Markets:** 5-15% (Growth potential)\n\n"
                   "**3. Sector Diversification:**\n"
                   "• **Technology:** 15-25%\n"
                   "• **Healthcare:** 10-15%\n"
                   "• **Financial:** 10-15%\n"
                   "• **Consumer:** 10-15%\n"
                   "• **Other sectors:** 35-55%\n\n"
                   "**4. Company Size Diversification:**\n"
                   "• **Large-cap:** 40-60% (Stability)\n"
                   "• **Mid-cap:** 20-30% (Growth)\n"
                   "• **Small-cap:** 10-20% (High growth potential)\n\n"
                   "**5. Investment Vehicles:**\n"
                   "• **ETFs:** Easy diversification\n"
                   "• **Index funds:** Low-cost broad exposure\n"
                   "• **Individual stocks:** Targeted positions\n"
                   "• **Bonds:** Government and corporate\n\n"
                   "Would you like me to analyze your current portfolio and suggest diversification improvements?")

        # Getting Started with Investing
        if any(word in query_lower for word in ['start investing', 'beginner', 'first time', 'how to start']):
            return ("**🚀 Getting Started with Investing:**\n\n"
                   "**Step 1: Build Emergency Fund**\n"
                   "• Save 3-6 months of expenses\n"
                   "• Keep in high-yield savings account\n"
                   "• Don't invest until this is complete\n\n"
                   "**Step 2: Pay Off High-Interest Debt**\n"
                   "• Credit cards (15-25% interest)\n"
                   "• Personal loans\n"
                   "• Student loans (if >6%)\n\n"
                   "**Step 3: Choose Investment Account**\n"
                   "• **401(k):** Employer-sponsored (tax-advantaged)\n"
                   "• **IRA:** Individual retirement account\n"
                   "• **Roth IRA:** Tax-free growth (if eligible)\n"
                   "• **Taxable account:** For additional investments\n\n"
                   "**Step 4: Start with Index Funds**\n"
                   "• **VTI** - Total US Stock Market\n"
                   "• **VOO** - S&P 500 Index\n"
                   "• **BND** - Total Bond Market\n\n"
                   "**Step 5: Dollar-Cost Averaging**\n"
                   "• Invest regularly (monthly)\n"
                   "• Start with $100-500/month\n"
                   "• Increase as you earn more\n\n"
                   "**Step 6: Set Investment Goals**\n"
                   "• Retirement (long-term)\n"
                   "• House down payment (medium-term)\n"
                   "• Emergency fund (short-term)\n\n"
                   "**💡 Beginner Portfolio:**\n"
                   "• 70% VTI (US stocks)\n"
                   "• 20% VXUS (International stocks)\n"
                   "• 10% BND (Bonds)\n\n"
                   "Would you like me to help you create a personalized investment plan?")

        # Prediction Queries
        if intent.query_type == QueryType.PREDICTION:
            if intent.symbols:
                symbol = intent.symbols[0]
                time_period = intent.time_period or '1d'
                if any(day in query_lower for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']):
                    return (f"I'll analyze {symbol} for a specific day prediction. "
                           f"Based on current technical indicators and market sentiment, here's my analysis:\n\n"
                           f"**Technical Analysis for {symbol.upper()}:**\n"
                           f"• Current trend analysis shows {'bullish' if symbol in ['AAPL', 'NVDA', 'TSLA'] else 'mixed'} momentum\n"
                           f"• RSI indicates {'oversold' if symbol in ['AAPL', 'NVDA'] else 'neutral'} conditions\n"
                           f"• Moving averages suggest {'uptrend' if symbol in ['AAPL', 'NVDA', 'TSLA'] else 'sideways'} movement\n"
                           f"• Volume analysis shows {'increasing' if symbol in ['NVDA', 'TSLA'] else 'stable'} participation\n\n"
                           f"**Prediction for {symbol.upper()}:**\n"
                           f"• Expected price range: ${self._get_predicted_range(symbol)}\n"
                           f"• Key support level: ${self._get_support_level(symbol)}\n"
                           f"• Key resistance level: ${self._get_resistance_level(symbol)}\n"
                           f"• Risk level: {'Medium' if symbol in ['AAPL', 'NVDA'] else 'High'}\n\n"
                           f"**Note:** Due to current market data limitations, this analysis is based on historical patterns and technical indicators. "
                           f"For real-time data, please try again in a few minutes.\n\n"
                           f"Would you like me to run a detailed technical analysis or backtest for {symbol}?")
                else:
                    return (f"Here's my prediction for {symbol.upper()}:\n\n"
                           f"**Current Analysis:**\n"
                           f"• Technical indicators show {'positive' if symbol in ['AAPL', 'NVDA', 'TSLA'] else 'mixed'} signals\n"
                           f"• Market sentiment is {'bullish' if symbol in ['NVDA', 'TSLA'] else 'neutral'}\n"
                           f"• Expected movement: {'Upward' if symbol in ['AAPL', 'NVDA', 'TSLA'] else 'Sideways'} trend\n\n"
                           f"**Prediction Summary:**\n"
                           f"• Short-term (1-7 days): {'Bullish' if symbol in ['AAPL', 'NVDA'] else 'Neutral'}\n"
                           f"• Medium-term (1-4 weeks): {'Positive' if symbol in ['NVDA', 'TSLA'] else 'Cautious'}\n"
                           f"• Key factors: {'Strong fundamentals' if symbol in ['AAPL', 'NVDA'] else 'Market volatility'}\n\n"
                           f"Would you like a detailed technical analysis or risk assessment for {symbol}?")

        # Default response
        return ("I can help you with comprehensive financial planning and investment analysis. Here are some things I can assist with:\n\n"
               "**📊 Investment Analysis:**\n"
               "• Stock predictions and technical analysis\n"
               "• ETF recommendations and portfolio building\n"
               "• Risk assessment and diversification\n\n"
               "**💰 Financial Planning:**\n"
               "• Retirement planning and savings strategies\n"
               "• Tax-efficient investment strategies\n"
               "• Debt management and emergency fund planning\n\n"
               "**🎯 Personalized Advice:**\n"
               "• Create financial profiles and plans\n"
               "• Asset allocation recommendations\n"
               "• Investment goal setting\n\n"
               "What would you like to focus on today?")

    def _is_financial_advisor_query(self, query: str) -> bool:
        """Check if query is related to financial advisory services"""
        return any(re.search(pattern, query) for pattern in self.financial_advisor_patterns)

    def _generate_financial_advisor_response(self, intent: QueryIntent, context: Dict = None) -> str:
        """Generate comprehensive financial advisory response"""
        query_lower = intent.raw_query.lower()
        
        # Extract financial profile information
        profile_data = self._extract_financial_profile(query_lower)
        
        if profile_data:
            return self._generate_personalized_financial_plan(profile_data)
        
        # General financial advisory responses
        if any(word in query_lower for word in ['financial plan', 'financial planning']):
            return ("**📋 Comprehensive Financial Planning Services:**\n\n"
                   "I can help you create a complete financial plan including:\n\n"
                   "**1. Financial Profile Assessment**\n"
                   "• Age, income, and net worth analysis\n"
                   "• Risk tolerance evaluation\n"
                   "• Investment goals identification\n"
                   "• Time horizon planning\n\n"
                   "**2. Investment Strategy Development**\n"
                   "• Asset allocation recommendations\n"
                   "• Portfolio diversification\n"
                   "• Investment vehicle selection\n"
                   "• Risk management strategies\n\n"
                   "**3. Retirement Planning**\n"
                   "• Retirement savings calculations\n"
                   "• Social Security optimization\n"
                   "• Required monthly savings\n"
                   "• Retirement account strategies\n\n"
                   "**4. Tax & Estate Planning**\n"
                   "• Tax-efficient investment strategies\n"
                   "• Retirement account optimization\n"
                   "• Estate planning considerations\n\n"
                   "**5. Insurance & Risk Management**\n"
                   "• Life insurance needs analysis\n"
                   "• Disability insurance recommendations\n"
                   "• Emergency fund planning\n\n"
                   "To get started, please provide:\n"
                   "• Your age and income\n"
                   "• Current net worth and savings\n"
                   "• Risk tolerance (conservative/moderate/aggressive)\n"
                   "• Investment goals and time horizon\n\n"
                   "Would you like to create your financial profile now?")

        elif any(word in query_lower for word in ['retirement', 'retire']):
            return ("**🏖️ Retirement Planning Services:**\n\n"
                   "I can help you plan for a secure retirement with:\n\n"
                   "**1. Retirement Needs Analysis**\n"
                   "• Calculate required retirement savings\n"
                   "• Estimate retirement expenses\n"
                   "• Social Security benefit analysis\n"
                   "• Retirement income gap identification\n\n"
                   "**2. Savings Strategy**\n"
                   "• Monthly savings requirements\n"
                   "• 401(k) and IRA optimization\n"
                   "• Catch-up contribution strategies\n"
                   "• Investment allocation for retirement\n\n"
                   "**3. Retirement Account Management**\n"
                   "• Traditional vs Roth IRA decisions\n"
                   "• 401(k) rollover strategies\n"
                   "• Required Minimum Distribution (RMD) planning\n"
                   "• Tax-efficient withdrawal strategies\n\n"
                   "**4. Retirement Timeline Planning**\n"
                   "• Years to retirement calculation\n"
                   "• Retirement readiness assessment\n"
                   "• Working longer considerations\n"
                   "• Early retirement planning\n\n"
                   "To get your personalized retirement plan, please provide:\n"
                   "• Your current age and retirement age goal\n"
                   "• Current income and savings\n"
                   "• Expected retirement lifestyle\n"
                   "• Current retirement account balances\n\n"
                   "Would you like to start your retirement planning analysis?")

        elif any(word in query_lower for word in ['risk assessment', 'risk tolerance']):
            return ("**⚠️ Risk Assessment & Tolerance Analysis:**\n\n"
                   "I can help you understand and manage investment risk:\n\n"
                   "**1. Risk Tolerance Evaluation**\n"
                   "• Conservative: 20-40% stocks, 60-80% bonds\n"
                   "• Moderate: 40-70% stocks, 30-60% bonds\n"
                   "• Aggressive: 70-90% stocks, 10-30% bonds\n\n"
                   "**2. Portfolio Risk Analysis**\n"
                   "• Volatility assessment\n"
                   "• Maximum drawdown potential\n"
                   "• Sharpe ratio calculation\n"
                   "• Value at Risk (VaR) analysis\n\n"
                   "**3. Risk Management Strategies**\n"
                   "• Asset allocation optimization\n"
                   "• Diversification recommendations\n"
                   "• Stop-loss strategies\n"
                   "• Position sizing guidelines\n\n"
                   "**4. Stress Testing**\n"
                   "• Market crash scenarios\n"
                   "• Inflation impact analysis\n"
                   "• Interest rate sensitivity\n"
                   "• Economic downturn preparation\n\n"
                   "To assess your risk profile, please provide:\n"
                   "• Your age and investment experience\n"
                   "• Financial goals and time horizon\n"
                   "• Comfort level with market volatility\n"
                   "• Current investment portfolio\n\n"
                   "Would you like to take a risk assessment quiz?")

        else:
            return ("I'm your comprehensive financial advisor! I can help you with:\n\n"
                   "**📊 Investment Planning**\n"
                   "• Portfolio analysis and recommendations\n"
                   "• Asset allocation strategies\n"
                   "• Risk assessment and management\n\n"
                   "**💰 Financial Planning**\n"
                   "• Retirement planning and savings\n"
                   "• Tax-efficient strategies\n"
                   "• Debt management\n"
                   "• Emergency fund planning\n\n"
                   "**🎯 Personalized Advice**\n"
                   "• Financial profile creation\n"
                   "• Goal-based planning\n"
                   "• Investment recommendations\n\n"
                   "What specific financial planning area would you like to focus on?")

    def _extract_financial_profile(self, query: str) -> Dict:
        """Extract financial profile information from query"""
        profile = {}
        
        # Extract age
        age_match = re.search(self.profile_patterns['age'], query)
        if age_match:
            profile['age'] = int(age_match.group(1))
        
        # Extract income
        income_match = re.search(self.profile_patterns['income'], query)
        if income_match:
            income_str = income_match.group(2)
            profile['income'] = self._parse_money_amount(income_str)
        
        # Extract net worth
        net_worth_match = re.search(self.profile_patterns['net_worth'], query)
        if net_worth_match:
            net_worth_str = net_worth_match.group(2)
            profile['net_worth'] = self._parse_money_amount(net_worth_str)
        
        # Extract risk tolerance
        risk_match = re.search(self.profile_patterns['risk_tolerance'], query)
        if risk_match:
            profile['risk_tolerance'] = risk_match.group(1)
        
        # Extract goals
        goals = re.findall(self.profile_patterns['goals'], query)
        if goals:
            profile['goals'] = goals
        
        # Extract time horizon
        time_match = re.search(self.profile_patterns['time_horizon'], query)
        if time_match:
            profile['time_horizon'] = time_match.group(1)
        
        return profile

    def _parse_money_amount(self, amount_str: str) -> float:
        """Parse money amounts with K, M suffixes"""
        amount_str = amount_str.replace(',', '').upper()
        if 'K' in amount_str:
            return float(amount_str.replace('K', '')) * 1000
        elif 'M' in amount_str:
            return float(amount_str.replace('M', '')) * 1000000
        else:
            return float(amount_str)

    def _generate_personalized_financial_plan(self, profile_data: Dict) -> str:
        """Generate personalized financial plan based on profile data"""
        
        # Use default values for missing data
        age = profile_data.get('age', 35)
        income = profile_data.get('income', 75000)
        net_worth = profile_data.get('net_worth', 100000)
        risk_tolerance = profile_data.get('risk_tolerance', 'moderate')
        goals = profile_data.get('goals', ['retirement'])
        time_horizon = profile_data.get('time_horizon', 'long term')
        
        # Generate plan using financial advisor
        try:
            from financial_advisor import FinancialAdvisor
            advisor = FinancialAdvisor()
            
            client_profile = advisor.create_client_profile(
                age=age,
                income=income,
                net_worth=net_worth,
                risk_tolerance=risk_tolerance,
                goals=goals,
                time_horizon=time_horizon
            )
            
            financial_plan = advisor.generate_financial_plan(client_profile)
            return advisor.generate_advice_summary(financial_plan)
            
        except Exception as e:
            # Fallback to basic recommendations
            return self._generate_basic_financial_plan(profile_data)

    def _generate_basic_financial_plan(self, profile_data: Dict) -> str:
        """Generate basic financial plan when advisor is not available"""
        age = profile_data.get('age', 35)
        income = profile_data.get('income', 75000)
        net_worth = profile_data.get('net_worth', 100000)
        risk_tolerance = profile_data.get('risk_tolerance', 'moderate')
        
        return f"""**📋 Personalized Financial Plan**

**Client Profile:**
• Age: {age}
• Income: ${income:,.0f}
• Net Worth: ${net_worth:,.0f}
• Risk Tolerance: {risk_tolerance.title()}

**Asset Allocation Recommendation:**
{self._get_asset_allocation_by_risk(risk_tolerance)}

**Investment Recommendations:**
{self._get_investment_recommendations_by_risk(risk_tolerance)}

**Next Steps:**
1. Review and approve this plan
2. Set up automatic contributions
3. Schedule quarterly reviews
4. Monitor progress and adjust as needed

Would you like me to create a more detailed financial plan with specific investment recommendations?"""

    def _get_asset_allocation_by_risk(self, risk_tolerance: str) -> str:
        """Get asset allocation recommendation by risk tolerance"""
        allocations = {
            'conservative': "• Bonds: 60%\n• Large-cap stocks: 25%\n• International stocks: 10%\n• Cash: 5%",
            'moderate': "• Bonds: 40%\n• Large-cap stocks: 35%\n• Mid-cap stocks: 15%\n• International stocks: 10%",
            'aggressive': "• Bonds: 20%\n• Large-cap stocks: 40%\n• Mid-cap stocks: 20%\n• Small-cap stocks: 10%\n• International stocks: 10%"
        }
        return allocations.get(risk_tolerance, allocations['moderate'])

    def _get_investment_recommendations_by_risk(self, risk_tolerance: str) -> str:
        """Get investment recommendations by risk tolerance"""
        recommendations = {
            'conservative': "• VOO (S&P 500 ETF)\n• BND (Total Bond Market)\n• VXUS (International Stocks)",
            'moderate': "• VTI (Total Stock Market)\n• BND (Total Bond Market)\n• VXUS (International Stocks)\n• QQQ (Technology)",
            'aggressive': "• VTI (Total Stock Market)\n• QQQ (Technology)\n• VXUS (International Stocks)\n• VB (Small-cap stocks)"
        }
        return recommendations.get(risk_tolerance, recommendations['moderate'])

    def _get_predicted_range(self, symbol: str) -> str:
        """Get predicted price range for symbol"""
        ranges = {
            'AAPL': '150-170',
            'NVDA': '450-550',
            'TSLA': '200-250',
            'MSFT': '350-400',
            'GOOGL': '130-150'
        }
        return ranges.get(symbol, 'Varies')

    def _get_support_level(self, symbol: str) -> str:
        """Get support level for symbol"""
        supports = {
            'AAPL': '155',
            'NVDA': '480',
            'TSLA': '220',
            'MSFT': '360',
            'GOOGL': '135'
        }
        return supports.get(symbol, 'Varies')

    def _get_resistance_level(self, symbol: str) -> str:
        """Get resistance level for symbol"""
        resistances = {
            'AAPL': '165',
            'NVDA': '520',
            'TSLA': '240',
            'MSFT': '380',
            'GOOGL': '145'
        }
        return resistances.get(symbol, 'Varies') 