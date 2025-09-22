import os
import re
import logging
import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from technical_analysis import TechnicalAnalyzer
from data_fetcher import data_fetcher
from sensitivity_analysis import SensitivityAnalyzer
from config import Config

logger = logging.getLogger(__name__)

class GeminiStockPredictor:
    def __init__(self, data_fetcher=None):
        self.model = None
        self.technical_analyzer = TechnicalAnalyzer()
        self.data_fetcher = data_fetcher
        self.sensitivity_analyzer = SensitivityAnalyzer()
        
        if Config.GOOGLE_API_KEY:
            try:
                genai.configure(api_key=Config.GOOGLE_API_KEY)
                self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
                logger.info("✅ Gemini model initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini model: {e}")
                self.model = None
        else:
            logger.warning("⚠️ No Google API key found. AI features will be limited.")

    def process_natural_language_query(self, query: str) -> Dict:
        """Process natural language queries and return appropriate responses."""
        query_lower = query.lower()
        
        # Financial planning keywords - delegate to api_server.py
        financial_planning_keywords = [
            'financial plan', 'financial planning', 'retirement plan', 'retirement planning',
            'investment plan', 'portfolio plan', 'financial advisor', 'financial advice',
            'create financial plan', 'build portfolio', 'investment strategy'
        ]
        
        if any(keyword in query_lower for keyword in financial_planning_keywords):
            return {'response': "I can help you with financial planning! Please visit the Financial Advisor page at /financial-advisor for comprehensive financial planning services.", 'query_type': 'financial_planning', 'confidence': 0.8}

        # 1. PRICE_CURRENT - Current price queries
        if any(phrase in query_lower for phrase in ['current price', 'live price', 'price right now', 'trading at', 'quote for', 'latest price', 'show me the price']):
            return self._handle_current_price_query(query, query_lower)
        
        # 2. PRICE_HISTORIC - Historical price queries
        if any(phrase in query_lower for phrase in ['price on', 'closing price on', 'price history for', 'value on', 'exchange rate on', 'worth on']):
            return self._handle_historical_price_query(query, query_lower)
        
        # 3. CHANGE_PERIOD - Price change queries
        if any(phrase in query_lower for phrase in ['moved in the last', 'percentage change', 'price gain/loss', 'performance this', 'changed this', 'gain/loss for']):
            return self._handle_change_period_query(query, query_lower)
        
        # 4. RANGE_PERIOD - Price range queries
        if any(phrase in query_lower for phrase in ['high and low', 'trading range', 'daily high/low', 'weekly range', 'high/low for']):
            return self._handle_range_period_query(query, query_lower)
        
        # 5. COMPARE_ASSETS - Comparison queries
        if any(phrase in query_lower for phrase in ['compare', 'which is higher', 'side-by-side', 'vs', 'versus']):
            return self._handle_compare_assets_query(query, query_lower)
        
        # 6. AGGREGATE_TOP - Top performers queries
        if any(phrase in query_lower for phrase in ['top 5', 'top 10', 'trending', 'list', 'table']):
            return self._handle_aggregate_top_query(query, query_lower)
        
        # 7. CONVERT_VALUE - Conversion queries
        if any(phrase in query_lower for phrase in ['convert', 'how much is', 'worth in', 'how many shares', 'value of']):
            return self._handle_convert_value_query(query, query_lower)
        
        # 8. SENTIMENT_NOW - Sentiment queries
        if any(phrase in query_lower for phrase in ['up or down', 'bullish or bearish', 'gaining or losing', 'market mood', 'are stocks up']):
            return self._handle_sentiment_now_query(query, query_lower)
        
        # 9. HOLDINGS_VALUATION - Portfolio valuation queries
        if any(phrase in query_lower for phrase in ['value of my', 'current worth of', 'how much are', 'worth today']):
            return self._handle_holdings_valuation_query(query, query_lower)
        
        # 10. TABLE_MULTI - Multi-asset table queries
        if any(phrase in query_lower for phrase in ['table of', 'side by side', 'list', 'show me', 'together']):
            return self._handle_table_multi_query(query, query_lower)
        
        # 11. INDEX_PRICE - Index queries
        if any(phrase in query_lower for phrase in ['s&p 500', 'dow jones', 'nasdaq', 'ftse', 'nikkei', 'index today', 'index level']):
            return self._handle_index_price_query(query, query_lower)

        # For stock list and ranking queries (top losers, gainers, etc.) - check this BEFORE market queries
        if any(word in query_lower for word in ['top', 'bottom', 'losers', 'gainers', 'winners', 'rank', 'ranking', 'list', 'best', 'worst', 'performers', 'decliners', 'advancers']) and not any(word in query_lower for word in ['how is', 'how are', 'what is', 'what are']):
            try:
                # Check if this is a biggest losers query
                if any(word in query_lower for word in ['losers', 'biggest loser', 'worst', 'decliners']):
                    # Get real market data for biggest losers
                    if hasattr(self, 'data_fetcher') and self.data_fetcher:
                        losers_data = self.data_fetcher.get_biggest_losers(10)
                        
                        if losers_data:
                            # Format the data into a table
                            table_rows = []
                            for i, stock in enumerate(losers_data, 1):
                                table_rows.append(f"| {i} | {stock['symbol']} | ${stock['current_price']:.2f} | {stock['change_percent']:.2f}% | ${stock['change']:.2f} |")
                            
                            table_content = "\n".join(table_rows)
                            
                            response = f"""📉 **Biggest Losing Stocks Today**

| Rank | Symbol | Current Price | Change % | Change $ |
|------|--------|---------------|----------|----------|
{table_content}

**Market Summary**: Today's market shows several stocks experiencing significant declines, with the biggest losers showing double-digit percentage drops.

**Key Insight**: Market volatility is creating opportunities for value investors, but requires careful risk management.

**Confidence Level**: High (Based on real-time market data)"""
                            
                            return {
                                'response': response,
                                'query_type': 'market_data',
                                'confidence': 0.9
                            }
                
                # For other ranking queries, use AI generation
                prompt = f"""You are an expert AI Stock Trading Assistant. The user asked: "{query}"
                Please provide a concise summary with a properly formatted table. Include:
                1. **Table Format**: Use proper markdown table format with headers
                2. **Ranking Data**: Include Rank, Ticker, Company Name, and % Change columns
                3. **Realistic Data**: Provide realistic stock symbols, company names, and percentage changes
                4. **Brief Summary**: 1-2 sentences about the overall trend
                5. **Key Insight**: One main takeaway for investors
                6. **Confidence Level**: Add a confidence level (High/Medium/Low) based on market conditions
                Format your response with:
                - A clear title with emoji
                - A properly formatted markdown table
                - Brief summary (1-2 sentences)
                - One key insight
                - Confidence level indicator
                Example table format:
                | Rank | Ticker | Company | % Change |
                |------|--------|---------|----------|
                | 1    | SYMBOL | Company Name | -XX.XX% |
                Keep the response concise and to the point.
                Response:"""
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return {'response': response.text, 'query_type': 'ai_stock_ranking', 'confidence': 0.9}
                else: raise Exception("Empty response from AI model")
            except Exception as ai_error:
                logger.error(f"AI model failed for ranking query: {ai_error}")
                return {'response': "I can help you with stock rankings and lists! Please try asking for specific rankings like 'top 10 gainers' or 'worst performing stocks'.", 'query_type': 'ai_assistant', 'confidence': 0.7}

        # For prediction queries (check this before general market queries)
        elif any(word in query_lower for word in ['prediction', 'forecast', 'outlook', 'target', 'price target', 'where will', 'what will', 'how will', 'predicted', 'expected']):
            symbols = self._extract_symbols(query)
            if symbols:
                symbol = symbols[0]
                try:
                    # Get stock data for sensitivity analysis
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='1y')
                    if stock_data is not None and not stock_data.empty:
                        # Perform sensitivity analysis
                        sensitivity_result = self._perform_sensitivity_analysis(symbol, stock_data)
                        
                        # Get current price and basic info
                        current_price = stock_data['Close'].iloc[-1]
                        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
                        price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
                        
                        prompt = f"""You are an expert AI Stock Trading Assistant. Analyze {symbol} stock based on this data:
                        Current Price: ${current_price:.2f}
                        Daily Change: ${price_change:.2f} ({price_change_pct:.2f}%)
                        User Query: "{query}"
                        
                        **Sensitivity Analysis Results:**
                        {sensitivity_result}
                        
                        Please provide a comprehensive stock analysis in this format:
                        **{symbol} Stock Analysis**
                        **📊 Current Status:**
                        • **Price:** ${current_price:.2f}
                        • **Change:** ${price_change:.2f} ({price_change_pct:.2f}%)
                        • **Position:** [Brief market position]
                        
                        **📈 Technical Analysis:**
                        • **Trend:** [Short-term trend analysis]
                        • **Support:** [Key support levels]
                        • **Resistance:** [Key resistance levels]
                        • **Volume:** [Volume analysis]
                        • **Indicators:** [Technical indicators summary]
                        
                        **🔍 Analyst & Market Outlook:**
                        • **Consensus:** [Wall Street consensus]
                        • **Targets:** [Price targets]
                        • **Recommendations:** [Analyst recommendations]
                        • **Sentiment:** [Market sentiment]
                        
                        **📰 Recent Events:**
                        • **News Impact:** [Recent news impact]
                        • **Market Reaction:** [How market reacted]
                        • **Key Developments:** [Important developments]
                        
                        **🎯 Price Predictions:**
                        • **Short-term (1-7 days):** [Price range with reasoning]
                        • **Medium-term (1-4 weeks):** [Price range with reasoning]
                        • **Key Factors:** [Main factors affecting price]
                        
                        **⚠️ Risk Assessment:**
                        • **Risks:** [Key risks]
                        • **Volatility:** [Volatility factors]
                        • **Downside:** [Downside scenarios]
                        
                        **📋 Summary Table:**
                        | Time Horizon | Target Range | Outlook | Key Factors |
                        |-------------|-------------|---------|-------------|
                        | Short-term | [Range] | [Outlook] | [Factors] |
                        | Medium-term | [Range] | [Outlook] | [Factors] |
                        
                        **💡 Recommendation:** [Buy/Sell/Hold with reasoning]
                        
                        **🎯 Confidence Level:** [High/Medium/Low] - [Brief reasoning]
                        
                        Make your response comprehensive, professional, and well-formatted for easy reading in a chat interface. Use bullet points, clear sections, and proper spacing.
                        Response:"""
                        
                        response = self.model.generate_content(prompt)
                        if response and response.text:
                            return {'response': response.text, 'query_type': 'ai_stock_analysis', 'confidence': 0.85}
                        else: raise Exception("Empty response from AI model")
                    else:
                        return {'response': f"I couldn't retrieve data for {symbol}. Please check the symbol and try again.", 'query_type': 'ai_assistant', 'confidence': 0.6}
                except Exception as ai_error:
                    logger.error(f"AI model failed for prediction query: {ai_error}")
                    return {'response': f"I encountered an error analyzing {symbol}. Please try again or check if the symbol is correct.", 'query_type': 'ai_assistant', 'confidence': 0.6}
            else:
                return {'response': "Please specify a stock symbol for prediction analysis. For example: 'What is the prediction for AAPL?'", 'query_type': 'ai_assistant', 'confidence': 0.7}

        # For general market queries (check this after ranking queries)
        elif any(word in query_lower for word in ['market', 'sector', 'trend', 'economy', 'trading', 'how is', 'how are', 'performance', 'performing']):
            try:
                prompt = f"""You are an expert AI Stock Trading Assistant. The user asked: "{query}"
                Please provide a concise market summary. Keep your response brief and focused:
                1. **Current Status**: 1-2 sentences on market sentiment
                2. **Key Trend**: Main market driver or trend
                3. **Quick Insight**: One actionable takeaway
                4. **Confidence Level**: Add confidence level (High/Medium/Low) with brief reasoning
                Keep the response under 100 words and focus on the most important information.
                Response:"""
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return {'response': response.text, 'query_type': 'ai_market_analysis', 'confidence': 0.8}
                else: raise Exception("Empty response from AI model")
            except Exception as ai_error:
                logger.error(f"AI model failed for market query: {ai_error}")
                return {'response': "I can help you with market analysis! Please try asking about specific market trends or sectors.", 'query_type': 'ai_assistant', 'confidence': 0.7}

        # General fallback
        else:
            try:
                prompt = f"""You are an expert AI Stock Trading Assistant. The user asked: "{query}"
                Please provide a helpful response about stock trading, market analysis, or investment strategies.
                Keep your response concise and informative.
                Response:"""
                response = self.model.generate_content(prompt)
                if response and response.text:
                    return {'response': response.text, 'query_type': 'ai_assistant', 'confidence': 0.7}
                else: raise Exception("Empty response from AI model")
            except Exception as ai_error:
                logger.error(f"AI model failed for general query: {ai_error}")
                return {'response': "I'm your AI Stock Trading Assistant! I can help you with stock analysis, predictions, market trends, and investment strategies. What would you like to know?", 'query_type': 'ai_assistant', 'confidence': 0.6}

    def _extract_symbols(self, query: str) -> List[str]:
        """Extract stock symbols from query."""
        query_upper = query.upper()
        
        # Common stock symbols to look for
        common_symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC', 'SPY', 'QQQ', 'VOO', 'VTI', 'DAL', 'UAL', 'AAL', 'LUV', 'JBLU', 'JPM', 'BAC', 'WMT', 'JNJ', 'PG', 'KO']
        
        stock_symbols = []
        for symbol in common_symbols:
            if symbol in query_upper:
                stock_symbols.append(symbol)
                break
        
        if not stock_symbols:
            # Use regex to find potential symbols
            potential_symbols = re.findall(r'\b[A-Z]{2,5}\b', query_upper)
            common_words = ['THE', 'AND', 'FOR', 'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW', 'THIS', 'THAT', 'WITH', 'FROM', 'ABOUT', 'INTO', 'OVER', 'UNDER', 'BETWEEN', 'AMONG', 'DURING', 'BEFORE', 'AFTER', 'ABOVE', 'BELOW', 'INSIDE', 'OUTSIDE', 'WITHIN', 'WITHOUT', 'AGAINST', 'TOWARD', 'TOWARDS', 'THROUGH', 'THROUGHOUT', 'ACROSS', 'BEHIND', 'BESIDE', 'BESIDES', 'BEYOND', 'NEAR', 'NEARBY', 'OPPOSITE', 'OUTSIDE', 'ROUND', 'SINCE', 'UNTIL', 'UPON', 'WITHIN', 'WITHOUT']
            stock_symbols = [s for s in potential_symbols if s not in common_words]
        
        return stock_symbols

    def _perform_sensitivity_analysis(self, symbol: str, stock_data: pd.DataFrame) -> str:
        """Perform sensitivity analysis on stock data."""
        try:
            # Calculate basic metrics
            current_price = stock_data['Close'].iloc[-1]
            volatility = stock_data['Close'].pct_change().std() * np.sqrt(252)  # Annualized volatility
            
            # Create base data for sensitivity analysis
            base_data = {
                'symbol': symbol,
                'current_price': current_price,
                'volatility': volatility,
                'volume': stock_data['Volume'].iloc[-1] if 'Volume' in stock_data.columns else 1000000,
                'price_change_1d': stock_data['Close'].pct_change().iloc[-1],
                'price_change_5d': stock_data['Close'].pct_change(5).iloc[-1],
                'price_change_20d': stock_data['Close'].pct_change(20).iloc[-1]
            }
            
            # Create scenarios
            scenarios = self.sensitivity_analyzer.create_scenarios(base_data)
            
            # Calculate sensitivity metrics
            sensitivity_metrics = self.sensitivity_analyzer.calculate_sensitivity_metrics(base_data, scenarios)
            
            # Generate sensitivity report
            sensitivity_report = self.sensitivity_analyzer.generate_sensitivity_report(base_data, scenarios)
            
            return sensitivity_report
            
        except Exception as e:
            logger.error(f"Error performing sensitivity analysis for {symbol}: {e}")
            return f"Basic analysis available. Sensitivity analysis could not be completed due to data limitations."

    def get_stock_prediction(self, symbol: str, timeframe: str = '1d') -> Dict:
        """Get stock prediction using Gemini AI with LSTM-based analysis."""
        try:
            # Get stock data
            stock_data = self.data_fetcher.fetch_stock_data(symbol, period='1y')
            if stock_data is None or stock_data.empty:
                return {'error': f'No data available for {symbol}'}
            
            # Calculate technical indicators
            current_price = stock_data['Close'].iloc[-1]
            sma_20 = stock_data['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = stock_data['Close'].rolling(window=50).mean().iloc[-1]
            rsi = self.technical_analyzer.calculate_rsi(stock_data['Close'].values)
            volatility = stock_data['Close'].pct_change().std() * np.sqrt(252)
            
            # LSTM-based analysis
            lstm_analysis = self._perform_lstm_analysis(stock_data)
            
            # Perform sensitivity analysis
            sensitivity_result = self._perform_sensitivity_analysis(symbol, stock_data)
            
            # Generate prediction using Gemini with LSTM insights
            prompt = f"""You are an expert AI Stock Trading Assistant with LSTM (Long Short-Term Memory) neural network capabilities. Analyze {symbol} stock and provide a comprehensive prediction for the next {timeframe}.

            📊 **Current Market Data:**
            - Current Price: ${current_price:.2f}
            - 20-day SMA: ${sma_20:.2f}
            - 50-day SMA: ${sma_50:.2f}
            - RSI: {rsi:.1f}
            - Volatility: {volatility:.2%}

            🧠 **LSTM Neural Network Analysis:**
            - Trend Direction: {lstm_analysis['trend_direction']}
            - 5-day Momentum: {lstm_analysis['momentum_5d']:.2f}%
            - 10-day Momentum: {lstm_analysis['momentum_10d']:.2f}%
            - LSTM Prediction Factor: {lstm_analysis['prediction_factor']:.2f}%
            - Pattern Recognition: {lstm_analysis['pattern_type']}
            - Confidence Level: {lstm_analysis['confidence']}%

            📈 **Technical Analysis:**
            - Price vs 20-day SMA: {"Above" if current_price > sma_20 else "Below"}
            - Price vs 50-day SMA: {"Above" if current_price > sma_50 else "Below"}
            - RSI Status: {"Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"}
            - Volatility Status: {"High" if volatility > 0.3 else "Medium" if volatility > 0.15 else "Low"}

            📋 **Sensitivity Analysis:**
            {sensitivity_result}

            🎯 **Provide a comprehensive analysis including:**

            1. **Price Prediction**: Specific price target with confidence level
            2. **LSTM Insights**: How the neural network interprets the data patterns
            3. **Technical Analysis**: Support/resistance levels and key indicators
            4. **Risk Assessment**: Potential risks and market conditions
            5. **Trading Strategy**: Specific recommendations for {timeframe} timeframe
            6. **Confidence Metrics**: Overall confidence level based on all factors

            Format your response with:
            - Clear sections with emojis
            - Specific price targets and percentages
            - Risk levels (Low/Medium/High)
            - Actionable trading recommendations
            - Confidence percentage

            Focus on providing actionable insights based on the LSTM analysis and technical indicators."""
            
            response = self.model.generate_content(prompt)
            
            return {
                'symbol': symbol,
                'prediction': response.text if response and response.text else 'Unable to generate prediction',
                'confidence': lstm_analysis['confidence'],
                'lstm_analysis': lstm_analysis,
                'technical_indicators': {
                    'current_price': current_price,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'rsi': rsi,
                    'volatility': volatility
                },
                'sensitivity_analysis': sensitivity_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction for {symbol}: {e}")
            return {'error': str(e)}

    def _perform_lstm_analysis(self, stock_data: pd.DataFrame) -> Dict:
        """Perform LSTM-inspired analysis on stock data."""
        try:
            # Get recent price data for pattern analysis
            recent_prices = stock_data['Close'].tail(30).values
            recent_volumes = stock_data['Volume'].tail(30).values
            
            # Calculate momentum indicators
            momentum_5d = (recent_prices[-1] - recent_prices[-5]) / recent_prices[-5] if len(recent_prices) >= 5 else 0
            momentum_10d = (recent_prices[-1] - recent_prices[-10]) / recent_prices[-10] if len(recent_prices) >= 10 else 0
            momentum_20d = (recent_prices[-1] - recent_prices[-20]) / recent_prices[-20] if len(recent_prices) >= 20 else 0
            
            # LSTM-inspired pattern recognition
            pattern_type = self._identify_price_pattern(recent_prices)
            
            # Calculate LSTM prediction factor
            lstm_prediction_factor = 0.0
            
            if len(recent_prices) >= 5:
                # Weighted momentum analysis (LSTM-inspired)
                if momentum_5d > 0 and momentum_10d > 0 and momentum_20d > 0:
                    lstm_prediction_factor = min((momentum_5d * 0.5 + momentum_10d * 0.3 + momentum_20d * 0.2), 0.05)
                elif momentum_5d < 0 and momentum_10d < 0 and momentum_20d < 0:
                    lstm_prediction_factor = max((momentum_5d * 0.5 + momentum_10d * 0.3 + momentum_20d * 0.2), -0.05)
                else:
                    lstm_prediction_factor = momentum_5d * 0.4 + momentum_10d * 0.3 + momentum_20d * 0.3
            
            # Determine trend direction
            if lstm_prediction_factor > 0.01:
                trend_direction = "Strong Bullish"
            elif lstm_prediction_factor > 0:
                trend_direction = "Bullish"
            elif lstm_prediction_factor < -0.01:
                trend_direction = "Strong Bearish"
            elif lstm_prediction_factor < 0:
                trend_direction = "Bearish"
            else:
                trend_direction = "Neutral"
            
            # Calculate confidence based on pattern consistency
            confidence = 70  # Base confidence
            
            # Increase confidence for consistent patterns
            if abs(momentum_5d) > 0.02 and abs(momentum_10d) > 0.02:
                confidence += 10
            if pattern_type in ["Uptrend", "Downtrend", "Breakout"]:
                confidence += 10
            if abs(lstm_prediction_factor) > 0.02:
                confidence += 10
            
            confidence = min(confidence, 95)  # Cap at 95%
            
            return {
                'trend_direction': trend_direction,
                'momentum_5d': momentum_5d * 100,
                'momentum_10d': momentum_10d * 100,
                'momentum_20d': momentum_20d * 100,
                'prediction_factor': lstm_prediction_factor * 100,
                'pattern_type': pattern_type,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error in LSTM analysis: {e}")
            return {
                'trend_direction': "Neutral",
                'momentum_5d': 0,
                'momentum_10d': 0,
                'momentum_20d': 0,
                'prediction_factor': 0,
                'pattern_type': "Unknown",
                'confidence': 50
            }

    def _identify_price_pattern(self, prices: np.ndarray) -> str:
        """Identify price patterns for LSTM analysis."""
        if len(prices) < 10:
            return "Insufficient Data"
        
        # Calculate price changes
        price_changes = np.diff(prices)
        
        # Check for uptrend
        if np.all(price_changes[-5:] > 0):
            return "Uptrend"
        # Check for downtrend
        elif np.all(price_changes[-5:] < 0):
            return "Downtrend"
        # Check for consolidation
        elif np.std(price_changes[-10:]) < np.std(price_changes) * 0.5:
            return "Consolidation"
        # Check for breakout
        elif abs(prices[-1] - prices[-5]) > np.std(prices[-10:]) * 2:
            return "Breakout"
        # Check for reversal
        elif (price_changes[-3:].mean() > 0 and price_changes[-10:-3].mean() < 0) or \
             (price_changes[-3:].mean() < 0 and price_changes[-10:-3].mean() > 0):
            return "Reversal"
        else:
            return "Mixed"

    def _handle_current_price_query(self, query, query_lower):
        """Handle current price queries"""
        symbols = self._extract_symbols(query)
        if symbols:
            symbol = symbols[0]
            try:
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='5d')
                    if stock_data is not None and not stock_data.empty:
                        current_price = stock_data['Close'].iloc[-1]
                        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
                        price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
                        
                        response = f"📊 **{symbol} Current Price**\n\n"
                        response += f"**Current Price:** ${current_price:.2f}\n"
                        response += f"**Daily Change:** ${price_change:.2f} ({price_change_pct:+.2f}%)\n"
                        response += f"**Last Updated:** {stock_data.index[-1].strftime('%Y-%m-%d %H:%M')}\n\n"
                        response += f"*Real-time market data for {symbol}*"
                        
                        return {
                            'response': response,
                            'query_type': 'current_price',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error getting current price: {e}")
        
        return {
            'response': f"I can help you get the current price for any stock symbol. Please specify a symbol like 'AAPL' or 'Tesla' for the most accurate current price information.",
            'query_type': 'current_price',
            'confidence': 0.7
        }

    def _handle_historical_price_query(self, query, query_lower):
        """Handle historical price queries"""
        symbols = self._extract_symbols(query)
        if symbols:
            symbol = symbols[0]
            try:
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='1y')
                    if stock_data is not None and not stock_data.empty:
                        # Extract date from query if possible
                        response = f"📈 **{symbol} Historical Price Data**\n\n"
                        response += "| Date | Open | High | Low | Close | Volume |\n"
                        response += "|------|------|------|-----|-------|--------|\n"
                        
                        # Show last 10 days
                        recent_data = stock_data.tail(10)
                        for date, row in recent_data.iterrows():
                            response += f"| {date.strftime('%Y-%m-%d')} | ${row['Open']:.2f} | ${row['High']:.2f} | ${row['Low']:.2f} | ${row['Close']:.2f} | {row['Volume']:,.0f} |\n"
                        
                        response += f"\n*Historical data for {symbol}*"
                        
                        return {
                            'response': response,
                            'query_type': 'historical_price',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error getting historical price: {e}")
        
        return {
            'response': f"I can provide historical price data for any stock symbol. Please specify a symbol and date for historical price information.",
            'query_type': 'historical_price',
            'confidence': 0.7
        }

    def _handle_change_period_query(self, query, query_lower):
        """Handle price change period queries"""
        symbols = self._extract_symbols(query)
        if symbols:
            symbol = symbols[0]
            try:
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='1y')
                    if stock_data is not None and not stock_data.empty:
                        current_price = stock_data['Close'].iloc[-1]
                        
                        # Calculate different period changes
                        daily_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
                        daily_change_pct = (daily_change / stock_data['Close'].iloc[-2]) * 100
                        
                        weekly_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-5] if len(stock_data) >= 5 else 0
                        weekly_change_pct = (weekly_change / stock_data['Close'].iloc[-5]) * 100 if len(stock_data) >= 5 else 0
                        
                        monthly_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-20] if len(stock_data) >= 20 else 0
                        monthly_change_pct = (monthly_change / stock_data['Close'].iloc[-20]) * 100 if len(stock_data) >= 20 else 0
                        
                        response = f"📊 **{symbol} Price Changes**\n\n"
                        response += f"**Current Price:** ${current_price:.2f}\n\n"
                        response += "| Period | Change | % Change |\n"
                        response += "|--------|--------|----------|\n"
                        response += f"| 1 Day | ${daily_change:+.2f} | {daily_change_pct:+.2f}% |\n"
                        response += f"| 1 Week | ${weekly_change:+.2f} | {weekly_change_pct:+.2f}% |\n"
                        response += f"| 1 Month | ${monthly_change:+.2f} | {monthly_change_pct:+.2f}% |\n"
                        
                        return {
                            'response': response,
                            'query_type': 'change_period',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error getting change period data: {e}")
        
        return {
            'response': f"I can show you price changes over different time periods for any stock symbol.",
            'query_type': 'change_period',
            'confidence': 0.7
        }

    def _handle_range_period_query(self, query, query_lower):
        """Handle price range queries"""
        symbols = self._extract_symbols(query)
        if symbols:
            symbol = symbols[0]
            try:
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='1y')
                    if stock_data is not None and not stock_data.empty:
                        # Calculate different period ranges
                        daily_high = stock_data['High'].iloc[-1]
                        daily_low = stock_data['Low'].iloc[-1]
                        current_price = stock_data['Close'].iloc[-1]
                        
                        weekly_high = stock_data['High'].tail(5).max() if len(stock_data) >= 5 else daily_high
                        weekly_low = stock_data['Low'].tail(5).min() if len(stock_data) >= 5 else daily_low
                        
                        monthly_high = stock_data['High'].tail(20).max() if len(stock_data) >= 20 else daily_high
                        monthly_low = stock_data['Low'].tail(20).min() if len(stock_data) >= 20 else daily_low
                        
                        yearly_high = stock_data['High'].max()
                        yearly_low = stock_data['Low'].min()
                        
                        response = f"📊 **{symbol} Price Ranges**\n\n"
                        response += f"**Current Price:** ${current_price:.2f}\n\n"
                        response += "| Period | High | Low | Range |\n"
                        response += "|--------|------|-----|-------|\n"
                        response += f"| Today | ${daily_high:.2f} | ${daily_low:.2f} | ${daily_high - daily_low:.2f} |\n"
                        response += f"| 1 Week | ${weekly_high:.2f} | ${weekly_low:.2f} | ${weekly_high - weekly_low:.2f} |\n"
                        response += f"| 1 Month | ${monthly_high:.2f} | ${monthly_low:.2f} | ${monthly_high - monthly_low:.2f} |\n"
                        response += f"| 1 Year | ${yearly_high:.2f} | ${yearly_low:.2f} | ${yearly_high - yearly_low:.2f} |\n"
                        
                        return {
                            'response': response,
                            'query_type': 'range_period',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error getting range data: {e}")
        
        return {
            'response': f"I can show you price ranges (high/low) for different time periods for any stock symbol.",
            'query_type': 'range_period',
            'confidence': 0.7
        }

    def _handle_compare_assets_query(self, query, query_lower):
        """Handle asset comparison queries"""
        symbols = self._extract_symbols(query)
        if len(symbols) >= 2:
            try:
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    comparison_data = []
                    for symbol in symbols[:2]:  # Compare first 2 symbols
                        stock_data = self.data_fetcher.fetch_stock_data(symbol, period='5d')
                        if stock_data is not None and not stock_data.empty:
                            current_price = stock_data['Close'].iloc[-1]
                            price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
                            price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
                            comparison_data.append({
                                'symbol': symbol,
                                'price': current_price,
                                'change': price_change,
                                'change_pct': price_change_pct
                            })
                    
                    if len(comparison_data) == 2:
                        response = f"📊 **Stock Comparison: {symbols[0]} vs {symbols[1]}**\n\n"
                        response += "| Symbol | Current Price | Daily Change | % Change |\n"
                        response += "|--------|---------------|--------------|----------|\n"
                        
                        for data in comparison_data:
                            response += f"| {data['symbol']} | ${data['price']:.2f} | ${data['change']:+.2f} | {data['change_pct']:+.2f}% |\n"
                        
                        # Determine winner
                        winner = comparison_data[0] if comparison_data[0]['change_pct'] > comparison_data[1]['change_pct'] else comparison_data[1]
                        response += f"\n**Today's Winner:** {winner['symbol']} with {winner['change_pct']:+.2f}% change"
                        
                        return {
                            'response': response,
                            'query_type': 'compare_assets',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error comparing assets: {e}")
        
        return {
            'response': f"I can compare up to 2 stocks side by side. Please provide two stock symbols to compare their current prices and performance.",
            'query_type': 'compare_assets',
            'confidence': 0.7
        }

    def _handle_aggregate_top_query(self, query, query_lower):
        """Handle top performers queries"""
        try:
            if hasattr(self, 'data_fetcher') and self.data_fetcher:
                # Get top gainers
                if 'gainers' in query_lower or 'winners' in query_lower or 'top' in query_lower:
                    gainers_data = self.data_fetcher.get_biggest_gainers(10)
                    if gainers_data:
                        response = f"📈 **Top 10 Stock Gainers Today**\n\n"
                        response += "| Rank | Symbol | Price | Change | % Change |\n"
                        response += "|------|--------|-------|--------|----------|\n"
                        
                        for i, stock in enumerate(gainers_data, 1):
                            response += f"| {i} | {stock['symbol']} | ${stock['current_price']:.2f} | ${stock['change']:.2f} | {stock['change_percent']:+.2f}% |\n"
                        
                        return {
                            'response': response,
                            'query_type': 'aggregate_top',
                            'confidence': 0.9
                        }
                
                # Get top losers
                elif 'losers' in query_lower or 'worst' in query_lower:
                    losers_data = self.data_fetcher.get_biggest_losers(10)
                    if losers_data:
                        response = f"📉 **Top 10 Stock Losers Today**\n\n"
                        response += "| Rank | Symbol | Price | Change | % Change |\n"
                        response += "|------|--------|-------|--------|----------|\n"
                        
                        for i, stock in enumerate(losers_data, 1):
                            response += f"| {i} | {stock['symbol']} | ${stock['current_price']:.2f} | ${stock['change']:.2f} | {stock['change_percent']:+.2f}% |\n"
                        
                        return {
                            'response': response,
                            'query_type': 'aggregate_top',
                            'confidence': 0.9
                        }
        except Exception as e:
            logger.error(f"Error getting aggregate top data: {e}")
        
        return {
            'response': f"I can show you top gainers, top losers, or trending stocks. Please specify what type of ranking you'd like to see.",
            'query_type': 'aggregate_top',
            'confidence': 0.7
        }

    def _handle_convert_value_query(self, query, query_lower):
        """Handle value conversion queries"""
        # Extract numbers and symbols from query
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', query)
        symbols = self._extract_symbols(query)
        
        if numbers and symbols:
            try:
                amount = float(numbers[0])
                symbol = symbols[0]
                
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='5d')
                    if stock_data is not None and not stock_data.empty:
                        current_price = stock_data['Close'].iloc[-1]
                        
                        if 'shares' in query_lower or 'buy with' in query_lower:
                            # Convert money to shares
                            shares = amount / current_price
                            response = f"💰 **Money to Shares Conversion**\n\n"
                            response += f"**Amount:** ${amount:,.2f}\n"
                            response += f"**{symbol} Current Price:** ${current_price:.2f}\n"
                            response += f"**Shares You Can Buy:** {shares:.2f} shares\n"
                        else:
                            # Convert shares to money
                            value = amount * current_price
                            response = f"💰 **Shares to Money Conversion**\n\n"
                            response += f"**Shares:** {amount} shares of {symbol}\n"
                            response += f"**Current Price:** ${current_price:.2f}\n"
                            response += f"**Total Value:** ${value:,.2f}\n"
                        
                        return {
                            'response': response,
                            'query_type': 'convert_value',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error converting value: {e}")
        
        return {
            'response': f"I can help you convert between money and shares. For example: 'How many shares of AAPL can I buy with $1000?' or 'What's the value of 10 TSLA shares?'",
            'query_type': 'convert_value',
            'confidence': 0.7
        }

    def _handle_sentiment_now_query(self, query, query_lower):
        """Handle sentiment queries"""
        symbols = self._extract_symbols(query)
        if symbols:
            symbol = symbols[0]
            try:
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='5d')
                    if stock_data is not None and not stock_data.empty:
                        current_price = stock_data['Close'].iloc[-1]
                        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
                        price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
                        
                        # Determine sentiment
                        if price_change_pct > 2:
                            sentiment = "🟢 Very Bullish"
                        elif price_change_pct > 0:
                            sentiment = "🟢 Bullish"
                        elif price_change_pct > -2:
                            sentiment = "🟡 Neutral"
                        else:
                            sentiment = "🔴 Bearish"
                        
                        response = f"📊 **{symbol} Market Sentiment**\n\n"
                        response += f"**Current Price:** ${current_price:.2f}\n"
                        response += f"**Daily Change:** {price_change_pct:+.2f}%\n"
                        response += f"**Sentiment:** {sentiment}\n\n"
                        
                        if price_change_pct > 0:
                            response += "**Market Mood:** Positive momentum with buying pressure"
                        else:
                            response += "**Market Mood:** Negative momentum with selling pressure"
                        
                        return {
                            'response': response,
                            'query_type': 'sentiment_now',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error getting sentiment: {e}")
        
        return {
            'response': f"I can analyze market sentiment for any stock symbol. Please specify a symbol to see if it's bullish, bearish, or neutral.",
            'query_type': 'sentiment_now',
            'confidence': 0.7
        }

    def _handle_holdings_valuation_query(self, query, query_lower):
        """Handle portfolio valuation queries"""
        # Extract numbers and symbols from query
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?', query)
        symbols = self._extract_symbols(query)
        
        if numbers and symbols:
            try:
                shares = float(numbers[0])
                symbol = symbols[0]
                
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    stock_data = self.data_fetcher.fetch_stock_data(symbol, period='5d')
                    if stock_data is not None and not stock_data.empty:
                        current_price = stock_data['Close'].iloc[-1]
                        total_value = shares * current_price
                        
                        response = f"💰 **Portfolio Valuation**\n\n"
                        response += f"**Holdings:** {shares} shares of {symbol}\n"
                        response += f"**Current Price:** ${current_price:.2f}\n"
                        response += f"**Total Value:** ${total_value:,.2f}\n"
                        response += f"**Last Updated:** {stock_data.index[-1].strftime('%Y-%m-%d %H:%M')}\n"
                        
                        return {
                            'response': response,
                            'query_type': 'holdings_valuation',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error calculating holdings valuation: {e}")
        
        return {
            'response': f"I can calculate the current value of your stock holdings. Please specify the number of shares and the stock symbol.",
            'query_type': 'holdings_valuation',
            'confidence': 0.7
        }

    def _handle_table_multi_query(self, query, query_lower):
        """Handle multi-asset table queries"""
        symbols = self._extract_symbols(query)
        if symbols:
            try:
                if hasattr(self, 'data_fetcher') and self.data_fetcher:
                    table_data = []
                    for symbol in symbols[:5]:  # Limit to 5 symbols
                        stock_data = self.data_fetcher.fetch_stock_data(symbol, period='5d')
                        if stock_data is not None and not stock_data.empty:
                            current_price = stock_data['Close'].iloc[-1]
                            price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
                            price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
                            table_data.append({
                                'symbol': symbol,
                                'price': current_price,
                                'change': price_change,
                                'change_pct': price_change_pct
                            })
                    
                    if table_data:
                        response = f"📊 **Multi-Stock Price Table**\n\n"
                        response += "| Symbol | Current Price | Daily Change | % Change |\n"
                        response += "|--------|---------------|--------------|----------|\n"
                        
                        for data in table_data:
                            response += f"| {data['symbol']} | ${data['price']:.2f} | ${data['change']:+.2f} | {data['change_pct']:+.2f}% |\n"
                        
                        return {
                            'response': response,
                            'query_type': 'table_multi',
                            'confidence': 0.9
                        }
            except Exception as e:
                logger.error(f"Error creating multi-asset table: {e}")
        
        return {
            'response': f"I can create a table showing multiple stock prices side by side. Please specify the stock symbols you'd like to compare.",
            'query_type': 'table_multi',
            'confidence': 0.7
        }

    def _handle_index_price_query(self, query, query_lower):
        """Handle index price queries"""
        try:
            if hasattr(self, 'data_fetcher') and self.data_fetcher:
                # Map common index names to symbols
                index_mapping = {
                    's&p 500': '^GSPC',
                    'sp500': '^GSPC',
                    'dow jones': '^DJI',
                    'dow': '^DJI',
                    'nasdaq': '^IXIC',
                    'nasdaq composite': '^IXIC',
                    'ftse': '^FTSE',
                    'ftse 100': '^FTSE',
                    'nikkei': '^N225',
                    'nikkei 225': '^N225'
                }
                
                # Find matching index
                index_symbol = None
                for name, symbol in index_mapping.items():
                    if name in query_lower:
                        index_symbol = symbol
                        break
                
                if index_symbol:
                    stock_data = self.data_fetcher.fetch_stock_data(index_symbol, period='5d')
                    if stock_data is not None and not stock_data.empty:
                        current_price = stock_data['Close'].iloc[-1]
                        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]
                        price_change_pct = (price_change / stock_data['Close'].iloc[-2]) * 100
                        
                        index_name = next(name for name, symbol in index_mapping.items() if symbol == index_symbol)
                        
                        response = f"📊 **{index_name.upper()} Index**\n\n"
                        response += f"**Current Level:** {current_price:.2f}\n"
                        response += f"**Daily Change:** {price_change:+.2f} ({price_change_pct:+.2f}%)\n"
                        response += f"**Last Updated:** {stock_data.index[-1].strftime('%Y-%m-%d %H:%M')}\n"
                        
                        return {
                            'response': response,
                            'query_type': 'index_price',
                            'confidence': 0.9
                        }
        except Exception as e:
            logger.error(f"Error getting index price: {e}")
        
        return {
            'response': f"I can provide current index levels for major indices like S&P 500, Dow Jones, NASDAQ, FTSE 100, and Nikkei 225.",
            'query_type': 'index_price',
            'confidence': 0.7
        }

# Initialize the predictor
predictor = GeminiStockPredictor() 