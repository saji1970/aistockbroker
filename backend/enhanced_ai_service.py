import os
import re
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from config import Config
import asyncio

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Enhanced query types for comprehensive stock market analysis."""
    STOCK_ANALYSIS = "stock_analysis"
    PREDICTION = "prediction"
    TECHNICAL_ANALYSIS = "technical_analysis"
    MARKET_OVERVIEW = "market_overview"
    INVESTMENT_ADVICE = "investment_advice"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMPARISON = "comparison"
    RANKING = "ranking"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    TRADING_STRATEGY = "trading_strategy"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    OPTIONS_ANALYSIS = "options_analysis"
    CRYPTO_ANALYSIS = "crypto_analysis"
    ECONOMIC_ANALYSIS = "economic_analysis"
    GENERAL_QUESTION = "general_question"

@dataclass
class AIResponse:
    """Structured AI response with metadata."""
    content: str
    query_type: QueryType
    confidence: float
    model_used: str
    processing_time: float
    context_used: Dict[str, Any]
    metadata: Dict[str, Any]

class EnhancedHuggingFaceAI:
    """Enhanced AI service using Hugging Face models with better prompt management."""
    
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY', 'your_huggingface_api_key_here')
        self.api_url = "https://api-inference.huggingface.co/models"
        
        # Use a more effective model for financial analysis
        self.model = "gpt2"  # Fallback to gpt2 which is more commonly available
        
        # Check if we can use Hugging Face API
        self.huggingface_available = self._test_huggingface_connection()
        
        # Fallback to Gemini if Hugging Face is not available
        if not self.huggingface_available:
            logger.info("Hugging Face API not available, using Gemini as fallback")
            try:
                import google.generativeai as genai
                if Config.GOOGLE_API_KEY:
                    genai.configure(api_key=Config.GOOGLE_API_KEY)
                    self.gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL)
                    self.gemini_available = True
                else:
                    self.gemini_available = False
            except Exception as e:
                logger.warning(f"Gemini not available: {e}")
                self.gemini_available = False
        
        # Enhanced prompt templates with ChatGPT-like comprehensive capabilities
        self.prompt_templates = {
            QueryType.STOCK_ANALYSIS: {
                "system": """You are an expert AI financial analyst with deep expertise in stock market analysis, similar to ChatGPT and Gemini AI. You provide comprehensive, accurate, and actionable financial insights based on technical indicators, fundamental analysis, market sentiment, and economic data.

Your capabilities include:
- Real-time stock analysis and predictions
- Technical and fundamental analysis
- Market sentiment evaluation
- Risk assessment and management
- Portfolio optimization strategies
- Trading strategy development
- Economic impact analysis
- Options and derivatives analysis
- Cryptocurrency market insights
- Global market analysis

Your responses should be:
- Comprehensive and well-structured with clear sections
- Include specific data points, metrics, and calculations
- Provide actionable insights and recommendations
- Include risk warnings and appropriate disclaimers
- Use professional markdown formatting
- Adapt to user's knowledge level and preferences
- Consider market context and timing
- Include alternative scenarios and what-if analysis""",
                
                "user": """Analyze {symbol} stock in {market} market comprehensively. Current price: {price}. Provide a detailed analysis that covers all aspects of the stock.

Please include:
1. **Executive Summary** - Key insights and recommendations
2. **Current Market Position** - Price action, volume, and market context
3. **Technical Analysis** - Key indicators (RSI, MACD, Bollinger Bands, moving averages)
4. **Fundamental Analysis** - Financial ratios, earnings, growth prospects
5. **Risk Assessment** - Market risks, company-specific risks, volatility analysis
6. **Trading Recommendations** - Entry/exit points, position sizing, stop losses
7. **Investment Thesis** - Long-term outlook and growth potential
8. **Alternative Scenarios** - Bull case, bear case, and base case
9. **Confidence Level** - Your confidence in the analysis (0-100%)
10. **Next Steps** - What to watch for and when to reassess""",
                
                "assistant": "I'll provide a comprehensive analysis of {symbol} in the {market} market, covering technical indicators, fundamental factors, risk assessment, and actionable trading recommendations."
            },
            
            QueryType.PREDICTION: {
                "system": """You are a specialized AI stock prediction model with advanced forecasting capabilities. You analyze historical data, technical indicators, market sentiment, fundamental factors, and economic conditions to provide accurate price predictions with detailed confidence levels and risk assessments.

Your prediction capabilities include:
- Short-term (1-7 days) price predictions
- Medium-term (1-3 months) trend analysis
- Long-term (6-12 months) growth projections
- Volatility forecasting
- Support and resistance level predictions
- Earnings impact analysis
- Market event sensitivity analysis

Your predictions should include:
- Price targets with probability ranges
- Confidence levels with detailed reasoning
- Key factors affecting the prediction
- Risk scenarios and probability weights
- Multiple time horizons
- Entry/exit point recommendations
- Alternative scenarios (bull/bear cases)
- Market condition dependencies""",
                
                "user": """Predict the price movement for {symbol} over {timeframe}. Current price: {price}. Provide a comprehensive prediction analysis.

Please include:
1. **Price Prediction** - Target prices with probability ranges
2. **Confidence Level** - Detailed confidence assessment (0-100%)
3. **Key Drivers** - Factors driving the prediction
4. **Risk Scenarios** - Bull case, bear case, and base case
5. **Technical Levels** - Support and resistance predictions
6. **Entry/Exit Points** - Optimal trading levels
7. **Time Horizon Analysis** - Short, medium, and long-term outlook
8. **Market Conditions** - How market factors affect the prediction
9. **Alternative Scenarios** - What-if analysis for different conditions
10. **Monitoring Points** - Key events to watch for""",
                
                "assistant": "Based on my comprehensive analysis of {symbol}'s technical indicators, fundamental factors, market sentiment, and economic conditions, here's my detailed prediction for the {timeframe} timeframe."
            },
            
            QueryType.TECHNICAL_ANALYSIS: {
                "system": """You are an expert technical analyst. You interpret technical indicators like RSI, MACD, Bollinger Bands, moving averages, and volume patterns to provide actionable trading signals. Always include support/resistance levels and risk management advice.

Your technical analysis should include:
- Key technical indicators and their values
- Support and resistance levels
- Trend analysis
- Volume analysis
- Trading signals
- Risk management levels""",
                
                "user": """Provide technical analysis for {symbol}. Include RSI, MACD, support/resistance levels, and trading signals.

Analyze:
1. RSI, MACD, and other key indicators
2. Support and resistance levels
3. Trend direction and strength
4. Volume patterns
5. Trading signals (Buy/Sell/Hold)
6. Risk management levels""",
                
                "assistant": "Here's my technical analysis for {symbol} based on current market data and technical indicators."
            },
            
            QueryType.MARKET_OVERVIEW: {
                "system": """You are a market analyst providing comprehensive market overviews. You analyze sector performance, market trends, volatility, and macroeconomic factors affecting stock markets. Provide actionable insights and risk assessments.

Your market overview should include:
- Overall market sentiment
- Sector performance analysis
- Key market drivers
- Risk factors
- Investment opportunities
- Market outlook""",
                
                "user": """Provide a market overview for {market} market. Include sector performance, trends, and investment opportunities.

Cover:
1. Overall market sentiment
2. Sector performance highlights
3. Key market drivers
4. Risk factors to watch
5. Investment opportunities
6. Market outlook and trends""",
                
                "assistant": "Here's my analysis of the {market} market based on current conditions and market data."
            },
            
            QueryType.INVESTMENT_ADVICE: {
                "system": """You are a certified financial advisor providing personalized investment recommendations. You consider risk tolerance, investment goals, market conditions, and diversification principles. Always include risk warnings and disclaimer.

Your investment advice should include:
- Risk assessment based on profile
- Diversification recommendations
- Asset allocation suggestions
- Investment timing
- Risk management strategies
- Important disclaimers""",
                
                "user": """Provide investment advice for {riskProfile} investor in {market} market with {amount} investment.

Consider:
1. Risk tolerance and profile
2. Market conditions
3. Diversification strategies
4. Asset allocation
5. Investment timing
6. Risk management""",
                
                "assistant": "Based on your {riskProfile} risk profile and current {market} market conditions, here are my investment recommendations."
            },
            
            QueryType.SENTIMENT_ANALYSIS: {
                "system": """You are a sentiment analysis expert specializing in financial markets. You analyze news, social media, earnings reports, and market data to assess investor sentiment and market mood. Provide sentiment scores and confidence levels.

Your sentiment analysis should include:
- Overall sentiment score
- Sentiment breakdown by factors
- Key sentiment drivers
- Confidence level
- Sentiment trends
- Market implications""",
                
                "user": """Analyze market sentiment for {symbol} or {market} market. Include sentiment score and key factors.

Evaluate:
1. Overall sentiment score (0-100)
2. Sentiment breakdown
3. Key sentiment drivers
4. Confidence level
5. Sentiment trends
6. Market implications""",
                
                "assistant": "Here's my sentiment analysis for {symbol} based on current market data, news, and social media sentiment."
            },
            
            QueryType.RANKING: {
                "system": """You are a financial analyst specializing in stock rankings and lists. You provide comprehensive rankings based on performance, market capitalization, growth potential, and other relevant metrics. Always include detailed information for each stock and investment insights.

Your rankings should include:
- Detailed stock information (price, market cap, sector)
- Performance metrics (YTD return, volatility)
- Investment insights and trends
- Risk considerations
- Market context and analysis
- Important disclaimers""",
                
                "user": """Provide a ranking of top stocks for {market} market. Include detailed information and investment insights.

Include:
1. Top stocks with detailed information
2. Performance metrics and trends
3. Sector analysis and insights
4. Investment recommendations
5. Risk considerations
6. Market context""",
                
                "assistant": "Here's my ranking of top stocks in the {market} market based on current performance and market analysis."
            },
            
            QueryType.PORTFOLIO_ANALYSIS: {
                "system": """You are an expert portfolio analyst with deep expertise in portfolio construction, optimization, and risk management. You provide comprehensive portfolio analysis, optimization recommendations, and performance insights.

Your portfolio analysis capabilities include:
- Portfolio performance evaluation
- Risk-return optimization
- Asset allocation analysis
- Diversification assessment
- Rebalancing recommendations
- Performance attribution analysis
- Risk factor decomposition
- Correlation analysis
- Sector and geographic exposure analysis

Your analysis should include:
- Comprehensive performance metrics
- Risk assessment and management
- Optimization recommendations
- Diversification analysis
- Rebalancing strategies
- Performance attribution
- Forward-looking insights""",
                
                "user": """Analyze the portfolio with symbols {symbols} and investment amount {amount}. Provide comprehensive portfolio analysis and optimization recommendations.

Please include:
1. **Portfolio Overview** - Current allocation and performance
2. **Risk Analysis** - Volatility, beta, and risk metrics
3. **Performance Attribution** - What's driving returns
4. **Diversification Assessment** - Sector, geographic, and style exposure
5. **Optimization Recommendations** - Suggested changes
6. **Rebalancing Strategy** - When and how to rebalance
7. **Risk Management** - Stop losses and position sizing
8. **Performance Projections** - Expected returns and scenarios""",
                
                "assistant": "I'll provide a comprehensive portfolio analysis for your {symbols} portfolio, including performance evaluation, risk assessment, and optimization recommendations."
            },
            
            QueryType.TRADING_STRATEGY: {
                "system": """You are an expert trading strategist with deep knowledge of various trading strategies, risk management, and market dynamics. You develop and analyze trading strategies for different market conditions and timeframes.

Your trading strategy capabilities include:
- Day trading strategies
- Swing trading approaches
- Position trading methods
- Options trading strategies
- Risk management techniques
- Entry and exit strategies
- Position sizing methodologies
- Market timing analysis
- Strategy backtesting and optimization

Your strategies should include:
- Clear entry and exit criteria
- Risk management rules
- Position sizing guidelines
- Performance expectations
- Market condition requirements
- Alternative scenarios
- Monitoring and adjustment protocols""",
                
                "user": """Develop a trading strategy for {symbol} in {market} market. Consider current price {price} and market conditions.

Please include:
1. **Strategy Overview** - Type and approach
2. **Entry Criteria** - When to enter positions
3. **Exit Criteria** - When to exit positions
4. **Risk Management** - Stop losses and position sizing
5. **Position Sizing** - How much to invest
6. **Market Conditions** - When strategy works best
7. **Performance Expectations** - Expected returns and risks
8. **Monitoring Points** - What to watch for
9. **Alternative Scenarios** - Plan B and C
10. **Implementation Steps** - How to execute the strategy""",
                
                "assistant": "I'll develop a comprehensive trading strategy for {symbol} that includes entry/exit criteria, risk management, and performance expectations."
            },
            
            QueryType.FUNDAMENTAL_ANALYSIS: {
                "system": """You are an expert fundamental analyst specializing in company financial analysis, valuation, and investment thesis development. You analyze financial statements, business models, and industry dynamics.

Your fundamental analysis capabilities include:
- Financial statement analysis
- Valuation modeling (DCF, multiples, etc.)
- Business model analysis
- Industry and competitive analysis
- Management quality assessment
- Growth potential evaluation
- Risk factor analysis
- ESG considerations
- Economic moat analysis

Your analysis should include:
- Comprehensive financial metrics
- Valuation assessment
- Business model analysis
- Competitive positioning
- Growth prospects
- Risk factors
- Investment thesis
- Valuation ranges""",
                
                "user": """Provide fundamental analysis for {symbol} in {market} market. Current price: {price}.

Please include:
1. **Business Overview** - Company description and business model
2. **Financial Analysis** - Key metrics and ratios
3. **Valuation Assessment** - Fair value estimates
4. **Growth Prospects** - Revenue and earnings outlook
5. **Competitive Position** - Market position and moats
6. **Risk Factors** - Business and financial risks
7. **Investment Thesis** - Bull and bear cases
8. **Management Quality** - Leadership assessment
9. **Industry Analysis** - Sector trends and dynamics
10. **Recommendation** - Buy, hold, or sell with reasoning""",
                
                "assistant": "I'll provide a comprehensive fundamental analysis of {symbol}, including financial metrics, valuation, and investment thesis."
            },
            
            QueryType.OPTIONS_ANALYSIS: {
                "system": """You are an expert options analyst specializing in options trading strategies, volatility analysis, and risk management. You provide comprehensive options analysis and strategy recommendations.

Your options analysis capabilities include:
- Options pricing and valuation
- Volatility analysis (IV vs HV)
- Options strategies (calls, puts, spreads, etc.)
- Risk management for options
- Greeks analysis (delta, gamma, theta, vega)
- Options flow analysis
- Earnings options strategies
- Calendar and diagonal spreads
- Iron condors and butterflies

Your analysis should include:
- Options pricing analysis
- Volatility assessment
- Strategy recommendations
- Risk-reward analysis
- Greeks breakdown
- Position sizing
- Exit strategies
- Risk management""",
                
                "user": """Analyze options for {symbol} in {market} market. Current price: {price}. Provide options strategies and analysis.

Please include:
1. **Options Overview** - Available options and liquidity
2. **Volatility Analysis** - IV vs HV assessment
3. **Strategy Recommendations** - Best options strategies
4. **Risk-Reward Analysis** - Potential gains and losses
5. **Greeks Analysis** - Delta, gamma, theta, vega
6. **Position Sizing** - How much to invest
7. **Exit Strategies** - When and how to exit
8. **Risk Management** - Stop losses and adjustments
9. **Market Conditions** - When strategies work best
10. **Alternative Strategies** - Plan B options""",
                
                "assistant": "I'll provide comprehensive options analysis for {symbol}, including strategy recommendations, risk assessment, and Greeks analysis."
            },
            
            QueryType.CRYPTO_ANALYSIS: {
                "system": """You are an expert cryptocurrency analyst with deep knowledge of blockchain technology, crypto markets, and digital asset analysis. You provide comprehensive crypto analysis and investment insights.

Your crypto analysis capabilities include:
- Technical analysis for cryptocurrencies
- Fundamental analysis of blockchain projects
- Market sentiment analysis
- DeFi protocol analysis
- NFT market analysis
- Regulatory impact assessment
- Network metrics analysis
- Tokenomics evaluation
- Cross-chain analysis

Your analysis should include:
- Technical and fundamental analysis
- Market sentiment assessment
- Risk factors and volatility
- Investment recommendations
- Regulatory considerations
- Technology assessment
- Network metrics
- Tokenomics analysis""",
                
                "user": """Analyze cryptocurrency {symbol} comprehensively. Current price: {price}. Provide crypto analysis and investment insights.

Please include:
1. **Project Overview** - Technology and use case
2. **Technical Analysis** - Price action and indicators
3. **Fundamental Analysis** - Network metrics and adoption
4. **Market Sentiment** - Community and institutional sentiment
5. **Risk Assessment** - Volatility and regulatory risks
6. **Investment Thesis** - Bull and bear cases
7. **Tokenomics** - Supply, distribution, and utility
8. **Competitive Analysis** - Market position and competitors
9. **Regulatory Environment** - Legal and compliance factors
10. **Recommendation** - Investment advice with risk warnings""",
                
                "assistant": "I'll provide comprehensive cryptocurrency analysis for {symbol}, including technical and fundamental factors, risk assessment, and investment recommendations."
            },
            
            QueryType.ECONOMIC_ANALYSIS: {
                "system": """You are an expert economic analyst specializing in macroeconomic analysis, market impact assessment, and economic trend analysis. You provide insights on how economic factors affect financial markets.

Your economic analysis capabilities include:
- Macroeconomic trend analysis
- Interest rate impact assessment
- Inflation and deflation analysis
- GDP and economic growth analysis
- Employment and labor market analysis
- Central bank policy analysis
- Geopolitical impact assessment
- Sector-specific economic analysis
- Global economic trends

Your analysis should include:
- Economic trend assessment
- Market impact analysis
- Policy implications
- Risk factors
- Investment implications
- Sector-specific effects
- Global context
- Forward-looking insights""",
                
                "user": """Provide economic analysis for {market} market and its impact on investments. Consider current economic conditions.

Please include:
1. **Economic Overview** - Current economic conditions
2. **Key Economic Indicators** - GDP, inflation, employment
3. **Central Bank Policy** - Interest rates and monetary policy
4. **Market Impact** - How economics affect markets
5. **Sector Analysis** - Winners and losers
6. **Risk Factors** - Economic risks to watch
7. **Investment Implications** - Portfolio adjustments
8. **Global Context** - International economic factors
9. **Policy Outlook** - Expected policy changes
10. **Recommendations** - Investment strategies for economic conditions""",
                
                "assistant": "I'll provide comprehensive economic analysis for the {market} market, including economic trends, policy implications, and investment recommendations."
            }
        }
        
        # Enhanced context management
        self.conversation_context = {
            "user_preferences": {},
            "market_context": {},
            "analysis_history": [],
            "risk_profile": "moderate",
            "preferred_markets": ["US"],
            "investment_amount": 10000
        }
        
        # Enhanced query classification patterns for comprehensive NLP
        self.classification_patterns = {
            QueryType.STOCK_ANALYSIS: [
                r'\b(analyze|analysis|overview|summary|evaluate|assess)\b',
                r'\b(price|value|worth|cost)\s+(of|for)\b',
                r'\b(current|latest|present)\s+(price|value)\b',
                r'\b(stock|share)\s+(analysis|overview|evaluation)\b',
                r'\b(what\s+is|tell\s+me\s+about)\s+\w+\s+(stock|company)\b'
            ],
            
            QueryType.PREDICTION: [
                r'\b(predict|forecast|outlook|future|tomorrow|next\s+(week|month|year))\b',
                r'\b(will|going\s+to|expect|anticipate)\s+(price|value|movement)\b',
                r'\b(ai|artificial\s+intelligence|machine\s+learning)\s+(prediction|analysis)\b',
                r'\b(end\s+of\s+day|eod|close|closing)\s+(price|value|prediction)\b',
                r'\b(what\s+will|what\s+would)\s+(happen|be)\b',
                r'\b(price\s+target|target\s+price)\b',
                r'\b(where\s+will|where\s+is\s+going)\s+\w+\s+(go|move)\b'
            ],
            
            QueryType.TECHNICAL_ANALYSIS: [
                r'\b(rsi|macd|bollinger|moving\s+average|sma|ema|volume|stochastic|atr)\b',
                r'\b(technical|indicator|chart|pattern)\b',
                r'\b(support|resistance|trend|momentum|breakout|breakdown)\b',
                r'\b(technical\s+analysis|chart\s+analysis)\b',
                r'\b(technical\s+indicators|chart\s+patterns)\b',
                r'\b(oversold|overbought|divergence|convergence)\b'
            ],
            
            QueryType.MARKET_OVERVIEW: [
                r'\b(market\s+(outlook|analysis|trends|sentiment|insights))\b',
                r'\b(sector|industry)\s+(performance|analysis|outlook)\b',
                r'\b(how\s+is|how\s+are)\s+(market|sector|industry)\b',
                r'\b(market\s+overview|market\s+summary)\b',
                r'\b(market\s+conditions|market\s+trends)\b',
                r'\b(overall\s+market|market\s+performance)\b'
            ],
            
            QueryType.INVESTMENT_ADVICE: [
                r'\b(investment|portfolio|recommend|suggest|advise|buy|sell)\b',
                r'\b(best|top|worst)\s+(stock|investment|opportunity)\b',
                r'\b(what\s+should|where\s+should)\s+(i\s+)?(invest|buy|sell)\b',
                r'\b(investment\s+advice|portfolio\s+recommendations)\b',
                r'\b(should\s+i|do\s+you\s+think)\s+(buy|sell|invest)\b',
                r'\b(investment\s+strategy|portfolio\s+allocation)\b'
            ],
            
            QueryType.SENTIMENT_ANALYSIS: [
                r'\b(sentiment|mood|feeling|opinion|view)\b',
                r'\b(bullish|bearish|positive|negative|optimistic|pessimistic)\b',
                r'\b(market\s+sentiment|investor\s+confidence)\b',
                r'\b(sentiment\s+analysis|market\s+mood)\b',
                r'\b(how\s+do\s+people\s+feel|what\s+is\s+the\s+mood)\b',
                r'\b(investor\s+sentiment|market\s+emotion)\b'
            ],
            
            QueryType.COMPARISON: [
                r'\b(compare|versus|vs|against|better|worse|similar)\b',
                r'\b(performance|return|growth)\s+(comparison|vs)\b',
                r'\b(difference\s+between|which\s+is\s+better)\b',
                r'\b(compare\s+\w+\s+and\s+\w+)\b',
                r'\b(which\s+one|which\s+stock)\s+(is\s+better|performs\s+better)\b'
            ],
            
            QueryType.RANKING: [
                r'\b(top|best|worst|leading)\s+\d+\s+(loser|gainer|stock|performer)\b',
                r'\b(list|show|give)\s+\d+\s+(stock|company|performer)\b',
                r'\b(top|best|worst|leading)\s+\d+\s+stocks?\b',
                r'\b(list|show|give)\s+(me\s+)?(top|best|worst|leading)\s+\d+\s+stocks?\b',
                r'\b(top|best|worst|leading)\s+\d+\s+tech\s+stocks?\b',
                r'\b(top|best|worst|leading)\s+\d+\s+financial\s+stocks?\b',
                r'\b(top|best|worst|leading)\s+\d+\s+startup\s+stocks?\b',
                r'\b(rank|ranking|ranked)\s+(stocks|companies)\b'
            ],
            
            QueryType.PORTFOLIO_ANALYSIS: [
                r'\b(portfolio|diversification|allocation)\b',
                r'\b(portfolio\s+analysis|portfolio\s+review)\b',
                r'\b(how\s+is\s+my\s+portfolio|portfolio\s+performance)\b',
                r'\b(portfolio\s+optimization|rebalancing)\b',
                r'\b(asset\s+allocation|diversification)\b',
                r'\b(portfolio\s+risk|portfolio\s+return)\b'
            ],
            
            QueryType.TRADING_STRATEGY: [
                r'\b(trading\s+strategy|strategy|trading\s+plan)\b',
                r'\b(day\s+trading|swing\s+trading|position\s+trading)\b',
                r'\b(entry|exit|stop\s+loss|take\s+profit)\b',
                r'\b(trading\s+signals|buy\s+signal|sell\s+signal)\b',
                r'\b(position\s+sizing|risk\s+management)\b',
                r'\b(trading\s+approach|trading\s+method)\b'
            ],
            
            QueryType.FUNDAMENTAL_ANALYSIS: [
                r'\b(fundamental|financial|earnings|revenue|profit)\b',
                r'\b(pe\s+ratio|price\s+to\s+earnings|valuation)\b',
                r'\b(balance\s+sheet|income\s+statement|cash\s+flow)\b',
                r'\b(fundamental\s+analysis|financial\s+analysis)\b',
                r'\b(earnings\s+report|quarterly\s+results)\b',
                r'\b(book\s+value|debt|equity|assets)\b'
            ],
            
            QueryType.OPTIONS_ANALYSIS: [
                r'\b(options|calls|puts|strike|expiration)\b',
                r'\b(options\s+strategy|options\s+trading)\b',
                r'\b(implied\s+volatility|iv|greeks)\b',
                r'\b(options\s+chain|options\s+flow)\b',
                r'\b(covered\s+call|put\s+spread|iron\s+condor)\b',
                r'\b(delta|gamma|theta|vega)\b'
            ],
            
            QueryType.CRYPTO_ANALYSIS: [
                r'\b(crypto|cryptocurrency|bitcoin|ethereum|blockchain)\b',
                r'\b(crypto\s+analysis|cryptocurrency\s+analysis)\b',
                r'\b(token|coin|defi|nft)\b',
                r'\b(crypto\s+market|digital\s+assets)\b',
                r'\b(blockchain\s+technology|smart\s+contracts)\b',
                r'\b(crypto\s+trading|crypto\s+investment)\b'
            ],
            
            QueryType.ECONOMIC_ANALYSIS: [
                r'\b(economic|economy|gdp|inflation|interest\s+rates)\b',
                r'\b(fed|federal\s+reserve|central\s+bank)\b',
                r'\b(economic\s+analysis|macroeconomic)\b',
                r'\b(unemployment|employment|jobs)\b',
                r'\b(economic\s+indicators|economic\s+data)\b',
                r'\b(economic\s+impact|market\s+economy)\b'
            ],
            
            QueryType.RISK_ASSESSMENT: [
                r'\b(risk|volatility|beta|standard\s+deviation)\b',
                r'\b(risk\s+assessment|risk\s+analysis)\b',
                r'\b(how\s+risky|risk\s+level|risk\s+profile)\b',
                r'\b(downside\s+risk|upside\s+potential)\b',
                r'\b(risk\s+management|risk\s+mitigation)\b',
                r'\b(risk\s+vs\s+reward|risk\s+adjusted\s+return)\b'
            ]
        }

    def _test_huggingface_connection(self) -> bool:
        """Test if Hugging Face API is available."""
        try:
            response = requests.get(
                f"{self.api_url}/{self.model}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Hugging Face API not available: {e}")
            return False

    def classify_query(self, query: str) -> Tuple[QueryType, float]:
        """Enhanced query classification with confidence scoring."""
        query_lower = query.lower()
        scores = {}
        
        # Calculate scores for each query type
        for query_type, patterns in self.classification_patterns.items():
            scores[query_type] = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    scores[query_type] += 1
        
        # Find the highest scoring type
        if not scores:
            return QueryType.GENERAL_QUESTION, 0.0
        
        max_score = max(scores.values())
        primary_type = max(scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on score strength
        max_possible_score = max(len(patterns) for patterns in self.classification_patterns.values())
        confidence = min(max_score / max_possible_score, 1.0)
        
        return primary_type, confidence

    def create_enhanced_prompt(self, query_type: QueryType, variables: Dict[str, Any]) -> str:
        """Create enhanced prompts with better structure and context."""
        if query_type not in self.prompt_templates:
            # Fallback template
            template = {
                "system": "You are an expert AI financial analyst. Provide helpful and accurate analysis.",
                "user": "Analyze: {query}",
                "assistant": "I'll analyze this for you."
            }
        else:
            template = self.prompt_templates[query_type]
        
        # Merge context with variables
        enhanced_variables = {
            **variables,
            **self.conversation_context
        }
        
        # Replace variables in template
        system_prompt = template["system"]
        user_prompt = template["user"]
        assistant_prompt = template["assistant"]
        
        for key, value in enhanced_variables.items():
            placeholder = f"{{{key}}}"
            system_prompt = system_prompt.replace(placeholder, str(value))
            user_prompt = user_prompt.replace(placeholder, str(value))
            assistant_prompt = assistant_prompt.replace(placeholder, str(value))
        
        # Add conversation history for context
        if self.conversation_context["analysis_history"]:
            recent_history = self.conversation_context["analysis_history"][-3:]  # Last 3 interactions
            history_text = "\n".join([
                f"Previous: {h['query']} -> {h['response'][:100]}..."
                for h in recent_history
            ])
            system_prompt += f"\n\nRecent conversation context:\n{history_text}"
        
        # Create the full prompt
        full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant: {assistant_prompt}"
        
        return full_prompt

    async def generate_response(self, query: str, context: Dict[str, Any] = None) -> AIResponse:
        """Generate enhanced AI response with better prompt management."""
        start_time = datetime.now()
        
        try:
            # Classify the query
            query_type, confidence = self.classify_query(query)
            
            # Update conversation context
            self.conversation_context["analysis_history"].append({
                "query": query,
                "query_type": query_type.value,
                "timestamp": datetime.now().isoformat()
            })
            
            # Prepare context
            if context is None:
                context = {}
            
            enhanced_context = {
                "query": query,
                "market": context.get("market", "US"),
                "symbol": context.get("symbol", "N/A"),
                "price": context.get("price", "N/A"),
                "timeframe": context.get("timeframe", "short-term"),
                "riskProfile": context.get("riskProfile", "moderate"),
                "amount": context.get("amount", 10000),
                **context
            }
            
            # Create enhanced prompt
            prompt = self.create_enhanced_prompt(query_type, enhanced_context)
            
            # Generate response using available AI service
            try:
                if self.huggingface_available:
                    response_text = await self._call_huggingface_api(prompt, query_type)
                    model_used = "Hugging Face GPT-2"
                elif self.gemini_available:
                    response_text = await self._call_gemini_api(prompt, query_type)
                    model_used = "Google Gemini Pro"
                else:
                    response_text = self._generate_mock_response(query_type, enhanced_context)
                    model_used = "Mock AI (Demo Mode)"
            except Exception as e:
                logger.warning(f"AI service failed, using mock response: {e}")
                response_text = self._generate_mock_response(query_type, enhanced_context)
                model_used = "Mock AI (Fallback)"
            
            # Post-process the response
            processed_response = self._post_process_response(response_text, query_type)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update conversation history with response
            self.conversation_context["analysis_history"][-1]["response"] = processed_response
            
            return AIResponse(
                content=processed_response,
                query_type=query_type,
                confidence=confidence,
                model_used=model_used,
                processing_time=processing_time,
                context_used=enhanced_context,
                metadata={
                    "prompt_length": len(prompt),
                    "response_length": len(processed_response),
                    "query_classification": query_type.value
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                content=f"I encountered an error while processing your request: {str(e)}",
                query_type=QueryType.GENERAL_QUESTION,
                confidence=0.0,
                model_used="Error Handler",
                processing_time=processing_time,
                context_used=context or {},
                metadata={"error": str(e)}
            )

    async def _call_huggingface_api(self, prompt: str, query_type: QueryType) -> str:
        """Call Hugging Face API with enhanced error handling and retry logic."""
        if not self.api_key:
            raise ValueError("Hugging Face API key not configured")
        
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.api_url}/{self.model}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_length": 500,
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "do_sample": True,
                            "return_full_text": False
                        }
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                
                # Debug response
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                try:
                    data = response.json()
                    logger.info(f"Response data type: {type(data)}")
                    logger.info(f"Response data: {data}")
                except Exception as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    logger.info(f"Raw response text: {response.text}")
                    raise ValueError(f"Invalid JSON response: {e}")
                
                if data and isinstance(data, list) and len(data) > 0:
                    generated_text = data[0].get("generated_text", "")
                    if generated_text:
                        return generated_text
                    else:
                        # Try alternative response format
                        if isinstance(data[0], str):
                            return data[0]
                        elif isinstance(data[0], dict):
                            # Try different possible keys
                            for key in ["text", "content", "response", "output"]:
                                if key in data[0]:
                                    return data[0][key]
                
                # If we get here, try to return a meaningful response
                if data:
                    return str(data)
                
                raise ValueError("Invalid response format from Hugging Face API")
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retrying (exponential backoff)
                    await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"Failed to generate response after {max_retries} attempts: {last_error}")

    async def _call_gemini_api(self, prompt: str, query_type: QueryType) -> str:
        """Call Gemini API as fallback."""
        try:
            response = self.gemini_model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                raise ValueError("Empty response from Gemini API")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise e

    def _generate_mock_response(self, query_type: QueryType, context: Dict[str, Any]) -> str:
        """Generate mock responses for demonstration purposes."""
        
        symbol = context.get("symbol", "AAPL")
        market = context.get("market", "US")
        price = context.get("price", "150.00")
        
        mock_responses = {
            QueryType.PREDICTION: f"""Based on my analysis of {symbol} in the {market} market, here's my prediction:

**Price Prediction for {symbol}:**
- Current Price: ${price}
- 1-Day Target: ${float(price) * 1.02:.2f} (+2.0%)
- 1-Week Target: ${float(price) * 1.05:.2f} (+5.0%)
- 1-Month Target: ${float(price) * 1.12:.2f} (+12.0%)

**Key Factors:**
- Strong technical momentum
- Positive earnings outlook
- Market sentiment is bullish
- Volume is above average

**Risk Assessment:**
- Market volatility could impact short-term performance
- Economic factors may influence direction
- Technical resistance at ${float(price) * 1.03:.2f}

**Confidence Level: 85%**""",
            
            QueryType.TECHNICAL_ANALYSIS: f"""**Technical Analysis for {symbol} ({market} Market):**

**Key Indicators:**
- RSI: 65 (Neutral to Bullish)
- MACD: Positive momentum
- Moving Averages: Price above 20-day and 50-day MA
- Volume: Above average, supporting price action

**Support & Resistance:**
- Support Level 1: ${float(price) * 0.95:.2f}
- Support Level 2: ${float(price) * 0.90:.2f}
- Resistance Level 1: ${float(price) * 1.05:.2f}
- Resistance Level 2: ${float(price) * 1.10:.2f}

**Trading Signals:**
- Primary Signal: BUY
- Stop Loss: ${float(price) * 0.93:.2f}
- Take Profit: ${float(price) * 1.08:.2f}

**Trend Analysis:**
- Short-term: Bullish
- Medium-term: Bullish
- Long-term: Neutral""",
            
            QueryType.SENTIMENT_ANALYSIS: f"""**Market Sentiment Analysis for {symbol}:**

**Overall Sentiment Score: 75/100 (Bullish)**

**Sentiment Breakdown:**
- News Sentiment: 80/100 (Very Positive)
- Social Media: 70/100 (Positive)
- Analyst Ratings: 75/100 (Positive)
- Institutional Activity: 80/100 (Strong Buying)

**Key Sentiment Drivers:**
- Positive earnings reports
- Strong product launches
- Analyst upgrades
- Institutional buying

**Market Implications:**
- Sentiment supports continued upward movement
- High confidence in positive outlook
- Low risk of sentiment reversal

**Confidence Level: 82%**""",
            
            QueryType.INVESTMENT_ADVICE: f"""**Investment Recommendations for {market} Market:**

**Risk Profile: {context.get('riskProfile', 'Moderate')}**
**Investment Amount: ${context.get('amount', 10000):,}**

**Recommended Portfolio Allocation:**
- Stocks: 60% (${context.get('amount', 10000) * 0.6:,.0f})
- Bonds: 25% (${context.get('amount', 10000) * 0.25:,.0f})
- Cash: 15% (${context.get('amount', 10000) * 0.15:,.0f})

**Top Stock Recommendations:**
1. {symbol} - Strong growth potential
2. Technology sector leaders
3. Dividend-paying blue chips
4. Emerging market opportunities

**Risk Management:**
- Diversify across sectors
- Regular rebalancing
- Dollar-cost averaging
- Emergency fund maintenance

**⚠️ Important Disclaimer:**
This is not financial advice. Always consult with a qualified financial advisor.""",
            
            QueryType.MARKET_OVERVIEW: f"""**{market} Market Overview:**

**Current Market Status:**
- Overall Trend: Bullish
- Market Sentiment: Positive
- Volatility: Moderate
- Volume: Above Average

**Sector Performance:**
- Technology: +3.2% (Leading)
- Healthcare: +1.8% (Strong)
- Financial: +0.9% (Stable)
- Energy: -0.5% (Weak)

**Key Market Drivers:**
- Strong economic data
- Positive earnings season
- Federal Reserve policy
- Global trade relations

**Investment Opportunities:**
- Growth stocks in technology
- Value stocks in financials
- International diversification
- Bond ladder strategies

**Risk Factors:**
- Inflation concerns
- Geopolitical tensions
- Interest rate changes
- Market volatility""",
            
            QueryType.RANKING: f"""**Top 10 Stocks - {market} Market**

Here are the top 10 stocks in the {market} market based on performance, growth potential, and market capitalization:

**🏆 Top 10 Stocks:**

1. **AAPL** - Apple Inc.
   - Current Price: $175.50
   - Market Cap: $2.7T
   - YTD Return: +15.2%
   - Sector: Technology

2. **MSFT** - Microsoft Corporation
   - Current Price: $380.25
   - Market Cap: $2.8T
   - YTD Return: +12.8%
   - Sector: Technology

3. **GOOGL** - Alphabet Inc.
   - Current Price: $145.80
   - Market Cap: $1.8T
   - YTD Return: +18.5%
   - Sector: Technology

4. **AMZN** - Amazon.com Inc.
   - Current Price: $155.90
   - Market Cap: $1.6T
   - YTD Return: +22.1%
   - Sector: Consumer Discretionary

5. **TSLA** - Tesla Inc.
   - Current Price: $245.30
   - Market Cap: $780B
   - YTD Return: +35.7%
   - Sector: Consumer Discretionary

6. **META** - Meta Platforms Inc.
   - Current Price: $320.45
   - Market Cap: $820B
   - YTD Return: +28.9%
   - Sector: Technology

7. **NVDA** - NVIDIA Corporation
   - Current Price: $485.20
   - Market Cap: $1.2T
   - YTD Return: +45.2%
   - Sector: Technology

8. **NFLX** - Netflix Inc.
   - Current Price: $485.75
   - Market Cap: $215B
   - YTD Return: +19.8%
   - Sector: Communication Services

9. **SPY** - SPDR S&P 500 ETF
   - Current Price: $450.30
   - Market Cap: $410B
   - YTD Return: +8.5%
   - Sector: ETF

10. **QQQ** - Invesco QQQ Trust
    - Current Price: $380.90
    - Market Cap: $195B
    - YTD Return: +12.3%
    - Sector: ETF

**📊 Key Metrics:**
- Average YTD Return: +21.1%
- Top Sector: Technology (6 stocks)
- Market Cap Range: $195B - $2.8T
- Volatility: Moderate to High

**💡 Investment Insights:**
- Technology sector dominates the top performers
- Large-cap stocks show strong momentum
- Diversification across sectors recommended
- Consider risk tolerance and investment horizon

**⚠️ Important Disclaimer:**
This ranking is for informational purposes only. Past performance does not guarantee future results. Always conduct your own research and consider consulting with a financial advisor before making investment decisions.""",
            
            QueryType.PORTFOLIO_ANALYSIS: f"""**Portfolio Analysis for {context.get('symbols', 'AAPL,MSFT,GOOGL')} Portfolio:**

**Portfolio Overview:**
- Total Value: ${context.get('amount', 10000):,.0f}
- Number of Positions: {len(context.get('symbols', 'AAPL,MSFT,GOOGL').split(','))}
- Current Allocation: Diversified across sectors
- YTD Performance: +12.5%

**Risk Analysis:**
- Portfolio Beta: 1.15 (Slightly above market)
- Volatility: 18.2% (Moderate)
- Sharpe Ratio: 1.45 (Good risk-adjusted returns)
- Maximum Drawdown: -8.5% (Controlled)

**Performance Attribution:**
- Technology Sector: +45% contribution
- Healthcare Sector: +25% contribution
- Financial Sector: +15% contribution
- Cash & Bonds: +15% contribution

**Diversification Assessment:**
- Sector Exposure: Well-diversified
- Geographic Exposure: 85% US, 15% International
- Market Cap Exposure: 60% Large, 30% Mid, 10% Small
- Style Exposure: 70% Growth, 30% Value

**Optimization Recommendations:**
- Increase international exposure to 20%
- Add emerging market exposure (5%)
- Consider adding defensive sectors
- Rebalance quarterly

**Rebalancing Strategy:**
- Target Allocation: 60% US Stocks, 20% International, 15% Bonds, 5% Cash
- Rebalancing Frequency: Quarterly
- Threshold: 5% deviation from targets
- Method: Systematic rebalancing

**Risk Management:**
- Stop Loss: 15% on individual positions
- Position Sizing: Max 10% per position
- Correlation Monitoring: Monthly
- Stress Testing: Quarterly

**Performance Projections:**
- Expected Return: 8-12% annually
- Risk Level: Moderate
- Volatility: 15-20%
- Downside Protection: 85% of market downside""",
            
            QueryType.TRADING_STRATEGY: f"""**Trading Strategy for {symbol} ({market} Market):**

**Strategy Overview:**
- Type: Swing Trading Strategy
- Timeframe: 1-4 weeks
- Risk Level: Moderate
- Expected Return: 5-15% per trade

**Entry Criteria:**
- Technical breakout above resistance
- Volume confirmation (1.5x average)
- RSI between 30-70 (not overbought/oversold)
- MACD bullish crossover
- Price above 20-day moving average

**Exit Criteria:**
- Take Profit: 10% gain or resistance level
- Stop Loss: 5% loss or support breakdown
- Time-based exit: 4 weeks maximum
- Technical reversal signals

**Risk Management:**
- Position Size: 2-5% of portfolio per trade
- Stop Loss: 5% below entry price
- Trailing Stop: 3% once 5% profit reached
- Maximum Risk: 1% of portfolio per trade

**Position Sizing:**
- Base Position: 2% of portfolio
- Scale-in: Add 1% on pullbacks
- Maximum Position: 5% of portfolio
- Correlation Check: Avoid similar positions

**Market Conditions:**
- Works Best: Trending markets
- Avoid: High volatility periods
- Optimal: Low to moderate volatility
- Market Direction: Bullish or sideways

**Performance Expectations:**
- Win Rate: 60-70%
- Average Win: 8%
- Average Loss: 4%
- Risk-Reward Ratio: 2:1
- Expected Return: 15-25% annually

**Monitoring Points:**
- Daily: Price action and volume
- Weekly: Technical indicators
- Monthly: Strategy performance review
- Quarterly: Strategy optimization

**Alternative Scenarios:**
- Plan B: Reduce position size in high volatility
- Plan C: Switch to defensive positions
- Plan D: Move to cash if trend breaks

**Implementation Steps:**
1. Set up alerts for entry conditions
2. Prepare position sizing calculations
3. Set stop losses and take profits
4. Monitor daily and adjust as needed
5. Review performance weekly
6. Optimize strategy monthly""",
            
            QueryType.FUNDAMENTAL_ANALYSIS: f"""**Fundamental Analysis for {symbol} ({market} Market):**

**Business Overview:**
- Company: {symbol} Corporation
- Sector: Technology
- Industry: Software & Services
- Market Cap: $2.5T
- Business Model: SaaS and cloud services

**Financial Analysis:**
- Revenue: $394.3B (2023)
- Net Income: $96.9B
- P/E Ratio: 25.5
- P/B Ratio: 12.8
- Debt-to-Equity: 0.3
- Current Ratio: 1.8
- ROE: 28.5%
- ROA: 15.2%

**Valuation Assessment:**
- DCF Fair Value: $180.00
- P/E Multiple: $175.00
- EV/EBITDA: $170.00
- Average Fair Value: $175.00
- Current Price: ${price}
- Upside Potential: +16.7%

**Growth Prospects:**
- Revenue Growth: +15% YoY
- Earnings Growth: +18% YoY
- Free Cash Flow Growth: +20% YoY
- Market Share: Expanding in cloud services
- International Expansion: Strong growth

**Competitive Position:**
- Market Leader: #1 in cloud services
- Economic Moats: Network effects, switching costs
- Competitive Advantages: Scale, technology, brand
- Market Share: 35% in cloud computing
- Barriers to Entry: High

**Risk Factors:**
- Regulatory scrutiny
- Competition from major tech companies
- Economic slowdown impact
- Currency fluctuations
- Cybersecurity risks

**Investment Thesis:**
- Bull Case: Continued cloud growth, AI leadership
- Bear Case: Regulatory pressure, competition
- Base Case: Steady growth with market expansion
- Catalysts: AI integration, international growth

**Management Quality:**
- Leadership: Experienced and proven
- Strategy: Clear and executable
- Execution: Strong track record
- Governance: Good corporate governance
- Innovation: High R&D investment

**Industry Analysis:**
- Cloud Computing: 20% annual growth
- AI/ML: Rapid adoption
- Digital Transformation: Accelerating
- Competition: Intensifying
- Regulation: Increasing

**Recommendation: BUY**
- Target Price: $180.00
- Time Horizon: 12-18 months
- Risk Level: Moderate
- Conviction: High""",
            
            QueryType.OPTIONS_ANALYSIS: f"""**Options Analysis for {symbol} ({market} Market):**

**Options Overview:**
- Current Price: ${price}
- Options Available: Calls and Puts
- Expiration Dates: Weekly, Monthly, Quarterly
- Liquidity: High (tight bid-ask spreads)
- Open Interest: Strong across strikes

**Volatility Analysis:**
- Implied Volatility: 25% (Current)
- Historical Volatility: 22% (30-day)
- IV Percentile: 65% (Moderately elevated)
- IV Rank: 70% (Above average)
- Volatility Skew: Normal (puts slightly higher)

**Strategy Recommendations:**
1. **Covered Call Strategy**
   - Sell $160 Call (30 days out)
   - Premium: $3.50
   - Break-even: $156.50
   - Max Profit: $13.50 (if called away)

2. **Bull Put Spread**
   - Sell $150 Put, Buy $145 Put
   - Net Credit: $2.00
   - Max Risk: $3.00
   - Probability of Profit: 65%

3. **Iron Condor**
   - Sell $155 Call, Buy $160 Call
   - Sell $145 Put, Buy $140 Put
   - Net Credit: $1.50
   - Max Risk: $3.50

**Risk-Reward Analysis:**
- Covered Call: Limited upside, income generation
- Bull Put Spread: Defined risk, high probability
- Iron Condor: Income strategy, range-bound
- Long Call: Unlimited upside, limited risk

**Greeks Analysis:**
- Delta: 0.55 (moderate directional exposure)
- Gamma: 0.02 (low gamma risk)
- Theta: -0.05 (time decay)
- Vega: 0.15 (volatility sensitivity)

**Position Sizing:**
- Covered Call: 100 shares + 1 short call
- Bull Put Spread: 5 contracts
- Iron Condor: 3 contracts
- Long Call: 2 contracts

**Exit Strategies:**
- Profit Target: 50% of max profit
- Stop Loss: 2x premium received
- Time-based: 21 days before expiration
- Technical: Break of key levels

**Risk Management:**
- Maximum Risk: 2% of portfolio per trade
- Correlation: Avoid similar positions
- Diversification: Mix of strategies
- Monitoring: Daily position review

**Market Conditions:**
- Best for Covered Calls: Sideways to slightly bullish
- Best for Bull Put Spreads: Bullish outlook
- Best for Iron Condors: Range-bound markets
- Avoid: High volatility periods

**Alternative Strategies:**
- Calendar Spreads: Time decay plays
- Diagonal Spreads: Directional with time decay
- Butterfly Spreads: High probability, low risk
- Straddles: Volatility plays""",
            
            QueryType.CRYPTO_ANALYSIS: f"""**Cryptocurrency Analysis for {symbol}:**

**Project Overview:**
- Token: {symbol}
- Blockchain: Ethereum
- Use Case: Decentralized Finance (DeFi)
- Market Cap: $45.2B
- Circulating Supply: 1.2B tokens

**Technical Analysis:**
- Current Price: ${price}
- 24h Change: +5.2%
- 7d Change: +12.8%
- 30d Change: +25.4%
- RSI: 65 (Neutral to Bullish)
- MACD: Bullish crossover
- Support: $140.00
- Resistance: $160.00

**Fundamental Analysis:**
- Network Value: $2.1B
- Daily Active Users: 450K
- Transaction Volume: $850M daily
- Development Activity: High (GitHub commits)
- Partnerships: Major integrations

**Market Sentiment:**
- Social Media: Bullish (75% positive)
- News Sentiment: Positive
- Institutional Interest: Growing
- Retail Adoption: Increasing
- Developer Activity: Strong

**Risk Assessment:**
- Volatility: Very High (80% annualized)
- Regulatory Risk: Moderate
- Technology Risk: Low
- Competition Risk: High
- Liquidity Risk: Low

**Investment Thesis:**
- Bull Case: Mass adoption, institutional investment
- Bear Case: Regulatory crackdown, competition
- Base Case: Gradual adoption, price appreciation
- Catalysts: ETF approval, institutional adoption

**Tokenomics:**
- Total Supply: 2B tokens
- Circulating: 60%
- Staked: 25%
- Team/Foundation: 10%
- Community: 5%
- Utility: Governance, staking, fees

**Competitive Analysis:**
- Market Position: Top 10 by market cap
- Competitors: Major DeFi protocols
- Competitive Advantages: First-mover, network effects
- Market Share: 15% in DeFi sector
- Innovation: High development pace

**Regulatory Environment:**
- US: Evolving regulations
- EU: MiCA framework
- Asia: Mixed approaches
- Compliance: Working with regulators
- Legal Status: Generally accepted

**Recommendation: BUY**
- Target Price: $180.00 (12 months)
- Risk Level: Very High
- Position Size: 1-3% of portfolio
- Time Horizon: 2-5 years
- **⚠️ High Risk Warning: Cryptocurrencies are highly volatile and speculative investments.**""",
            
            QueryType.ECONOMIC_ANALYSIS: f"""**Economic Analysis for {market} Market:**

**Current Economic Conditions:**
- GDP Growth: +2.1% (Annualized)
- Inflation Rate: 3.2% (Moderate)
- Unemployment Rate: 3.8% (Low)
- Interest Rates: 5.25% (Federal Funds Rate)

**Key Economic Indicators:**
- Consumer Confidence: 108.0 (Strong)
- Manufacturing PMI: 52.5 (Expansion)
- Housing Market: Stable with moderate growth
- Labor Market: Strong job creation

**Central Bank Policy:**
- Federal Reserve: Maintaining restrictive stance
- Inflation targeting: 2% long-term goal
- Policy outlook: Potential rate cuts in 2024

**Market Impact:**
- Strong economy supports corporate earnings
- Moderate inflation allows for stable growth
- Low unemployment supports consumer spending
- Interest rate environment affects growth stocks

**Sector Analysis:**
- Technology: Benefiting from strong economy
- Financial: Mixed impact from interest rates
- Healthcare: Stable growth prospects
- Energy: Volatile due to geopolitical factors

**Risk Factors:**
- Inflation persistence
- Geopolitical tensions
- Supply chain disruptions
- Policy uncertainty

**Investment Implications:**
- Growth stocks favored in strong economy
- Value stocks benefit from higher rates
- International diversification recommended
- Bond ladder strategies for income

**Global Context:**
- US economy leading global growth
- International trade tensions
- Currency fluctuations
- Emerging market opportunities

**Policy Outlook:**
- Gradual policy normalization expected
- Focus on inflation control
- Potential fiscal stimulus measures
- Regulatory environment changes

**Recommendations:**
- Maintain diversified portfolio
- Consider inflation-protected assets
- Monitor policy developments
- Adjust allocation based on economic data""",
            
            QueryType.RISK_ASSESSMENT: f"""**Risk Assessment for {symbol} ({market} Market):**

**Overall Risk Profile:**
- Risk Level: Moderate
- Volatility: 25% (Annualized)
- Beta: 1.15 (vs Market)
- Sharpe Ratio: 1.25
- Maximum Drawdown: -15%

**Market Risk:**
- Systematic Risk: Moderate
- Market Correlation: 0.75
- Sector Risk: Technology sector exposure
- Economic Sensitivity: High to growth
- Interest Rate Sensitivity: Moderate

**Company-Specific Risk:**
- Business Risk: Low (Established company)
- Financial Risk: Low (Strong balance sheet)
- Management Risk: Low (Proven leadership)
- Competitive Risk: Moderate (Strong position)
- Regulatory Risk: Moderate (Tech regulation)

**Volatility Analysis:**
- Historical Volatility: 25%
- Implied Volatility: 28%
- Volatility Regime: Normal
- Volatility Trend: Stable
- Volatility Forecast: 22-30%

**Downside Risk:**
- Value at Risk (95%): -8% (1 month)
- Expected Shortfall: -12% (1 month)
- Worst Case Scenario: -25% (6 months)
- Recovery Time: 6-12 months
- Downside Protection: 85%

**Upside Potential:**
- Bull Case: +40% (12 months)
- Base Case: +20% (12 months)
- Bear Case: -15% (12 months)
- Probability Distribution: Normal
- Expected Return: +15%

**Risk Management:**
- Position Sizing: 3-5% of portfolio
- Stop Loss: 15% below entry
- Diversification: Across sectors
- Correlation: Monitor with portfolio
- Rebalancing: Quarterly

**Risk vs Reward:**
- Risk-Reward Ratio: 1.5:1
- Expected Return: 15%
- Risk-Adjusted Return: 12%
- Information Ratio: 0.8
- Sortino Ratio: 1.5

**Monitoring Points:**
- Daily: Price action and volume
- Weekly: Technical indicators
- Monthly: Fundamental updates
- Quarterly: Earnings reports
- Annually: Strategic review

**Risk Mitigation:**
- Diversification: Across asset classes
- Hedging: Options strategies
- Stop Losses: Automated risk management
- Position Sizing: Risk-based allocation
- Regular Review: Monthly assessment""",
            
            QueryType.STOCK_ANALYSIS: f"""**Comprehensive Analysis of {symbol} ({market} Market):**

**Company Overview:**
- Current Price: ${price}
- Market Cap: $2.5T
- Sector: Technology
- Industry: Software

**Fundamental Analysis:**
- P/E Ratio: 25.5
- Revenue Growth: +15% YoY
- Profit Margin: 25%
- Debt-to-Equity: 0.3

**Technical Analysis:**
- RSI: 65 (Neutral)
- MACD: Bullish crossover
- Support: ${float(price) * 0.95:.2f}
- Resistance: ${float(price) * 1.05:.2f}

**Investment Thesis:**
- Strong market position
- Innovative product pipeline
- Solid financials
- Growth potential

**Risk Assessment:**
- Competition in key markets
- Regulatory challenges
- Market volatility
- Economic cycles

**Recommendation: BUY**
**Target Price: ${float(price) * 1.15:.2f}**
**Confidence: 85%**"""
        }
        
        return mock_responses.get(query_type, f"Analysis for {symbol}: This is a comprehensive analysis based on current market conditions and technical indicators.")

    def _post_process_response(self, response: str, query_type: QueryType) -> str:
        """Post-process AI response with category-specific formatting."""
        # Clean up the response
        cleaned_response = response.strip()
        
        # Remove incomplete sentences at the end
        cleaned_response = re.sub(r'[^.!?]*$', '', cleaned_response)
        
        # Add category-specific formatting
        if query_type == QueryType.PREDICTION:
            return self._format_prediction_response(cleaned_response)
        elif query_type == QueryType.TECHNICAL_ANALYSIS:
            return self._format_technical_response(cleaned_response)
        elif query_type == QueryType.MARKET_OVERVIEW:
            return self._format_market_response(cleaned_response)
        elif query_type == QueryType.INVESTMENT_ADVICE:
            return self._format_investment_response(cleaned_response)
        elif query_type == QueryType.SENTIMENT_ANALYSIS:
            return self._format_sentiment_response(cleaned_response)
        else:
            return self._format_general_response(cleaned_response)

    def _format_prediction_response(self, response: str) -> str:
        """Format prediction responses with enhanced structure."""
        return f"""# 📊 **AI Stock Prediction Analysis**

{response}

## ⚠️ **Risk Disclaimer**
This prediction is based on AI analysis and should not be considered as financial advice. Always do your own research and consult with a financial advisor before making investment decisions.

## 📈 **Key Metrics**
- **Confidence Level**: [AI Confidence Score]
- **Time Horizon**: [Prediction Timeframe]
- **Risk Level**: [Risk Assessment]"""

    def _format_technical_response(self, response: str) -> str:
        """Format technical analysis responses."""
        return f"""# 📈 **Technical Analysis Report**

{response}

## 📊 **Key Technical Levels**
- **Support**: [Calculated support levels]
- **Resistance**: [Calculated resistance levels]
- **Trend**: [Current trend direction]
- **Volume**: [Volume analysis]"""

    def _format_market_response(self, response: str) -> str:
        """Format market overview responses."""
        return f"""# 🌍 **Market Overview Analysis**

{response}

## 📈 **Market Summary**
- **Overall Trend**: [Market trend]
- **Volatility**: [Volatility level]
- **Volume**: [Volume analysis]
- **Sentiment**: [Market sentiment]"""

    def _format_investment_response(self, response: str) -> str:
        """Format investment advice responses."""
        return f"""# 💼 **Investment Recommendations**

{response}

## ⚠️ **Important Disclaimer**
This is not financial advice. Investment decisions should be based on your own research, risk tolerance, and financial goals. Consider consulting with a qualified financial advisor.

## 📋 **Risk Assessment**
- **Risk Level**: [Risk Assessment]
- **Diversification**: [Diversification Recommendations]
- **Timing**: [Investment Timing]"""

    def _format_sentiment_response(self, response: str) -> str:
        """Format sentiment analysis responses."""
        return f"""# 🧠 **Market Sentiment Analysis**

{response}

## 📊 **Sentiment Metrics**
- **Overall Sentiment**: [Sentiment Score]
- **Confidence**: [Confidence Level]
- **Trend**: [Sentiment Trend]
- **Key Drivers**: [Sentiment Drivers]"""

    def _format_general_response(self, response: str) -> str:
        """Format general responses."""
        return f"""# 🤖 **AI Financial Analysis**

{response}

---
*This analysis was generated using advanced AI technology. Please verify information independently.*"""

    def update_context(self, new_context: Dict[str, Any]):
        """Update conversation context with new information."""
        self.conversation_context.update(new_context)

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_context["analysis_history"]

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_context["analysis_history"] = []

# Create singleton instance
enhanced_ai = EnhancedHuggingFaceAI()

# Export for use in other modules
__all__ = ['EnhancedHuggingFaceAI', 'enhanced_ai', 'AIResponse', 'QueryType']
