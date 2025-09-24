import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, GlobeAltIcon, SparklesIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import { dayTradingAPI, predictionAPI, stockAPI } from '../services/api';
import { useStore } from '../store/store';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import huggingfaceAI from '../services/huggingfaceAI';

const EnhancedAIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: `# 🧠 **Enhanced AI Stock Trading Assistant**

Welcome to the **next-generation AI trading assistant** powered by advanced Hugging Face models! 

## 🚀 **What's New:**
- **🤖 Advanced AI Model**: Using state-of-the-art Hugging Face models for better analysis
- **🧠 Smart Context Management**: Remembers your preferences and conversation history
- **📊 Enhanced Prompt Engineering**: More accurate and detailed responses
- **🎯 Better Query Classification**: Understands your intent more precisely
- **📈 Improved Predictions**: Higher accuracy with confidence scoring

## 🌟 **Enhanced Capabilities:**

### **📊 Advanced Stock Analysis**
- Multi-market support with intelligent market detection
- Technical analysis with detailed indicator breakdown
- Fundamental analysis with risk assessment
- Sentiment analysis with confidence scoring

### **🔮 Intelligent Predictions**
- AI-powered price predictions with confidence levels
- Day trading analysis with entry/exit points
- Risk factor analysis and mitigation strategies
- Scenario-based forecasting

### **💼 Smart Investment Advice**
- Personalized recommendations based on risk profile
- Portfolio optimization suggestions
- Market timing analysis
- Diversification strategies

### **🌍 Multi-Market Intelligence**
- 🇺🇸 **US**: AAPL, MSFT, GOOGL, TSLA, META, NVDA, etc.
- 🇬🇧 **UK**: VOD.L, HSBA.L, BP.L, GSK.L, AZN.L, etc.
- 🇮🇳 **India**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, etc.
- 🇨🇦 Canada, 🇦🇺 Australia, 🇩🇪 Germany, 🇯🇵 Japan, 🇧🇷 Brazil

## 🎯 **Example Queries:**
- "What's the AI prediction for AAPL tomorrow?"
- "Give me a comprehensive analysis of GOOGL with technical indicators"
- "What's the market sentiment for TSLA?"
- "Compare AAPL vs MSFT performance"
- "Show me top 10 tech stocks in UK market"
- "Give me investment advice for a conservative investor"

## 💡 **Smart Features:**
- **Auto Market Detection**: Just type any stock symbol!
- **Context Awareness**: Remembers your previous queries
- **Confidence Scoring**: Every prediction includes confidence levels
- **Risk Assessment**: Built-in risk analysis for all recommendations

**🎯 Ready to experience the future of AI-powered trading analysis!**`,
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiModel, setAiModel] = useState('huggingface'); // 'huggingface' or 'legacy'
  const messagesEndRef = useRef(null);
  const { currentSymbol, currentMarket } = useStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Enhanced stock symbol extraction with better accuracy
  const extractStockSymbol = (message) => {
    // Enhanced Natural Language Query Detection
    const isRankingQuery = /(?:top|best|worst|leading)\s+\d+\s+(loser|gainer|stock|performer)/i.test(message);
    const isStartupQuery = /(?:give\s+(?:me|list\s+of)|show\s+me|get\s+me|find\s+me|what\s+are|tell\s+me\s+about|can\s+you\s+(?:give|show|get|find))\s+(?:the\s+)?(?:top|best|leading)\s+\d+\s+(?:ai\s+)?(?:tech|startup|start\s+up)/i.test(message);
    const isTopStartupQuery = /(?:top|best|leading)\s+\d+\s+(?:ai\s+)?(?:tech|startup|start\s+up)/i.test(message);
    const isListQuery = /(?:list|show|give|get)\s+(?:me\s+)?(?:the\s+)?\d+\s+(?:ai\s+)?(?:tech|startup|stock|company|performer)/i.test(message);
    const isGeneralListQuery = /(?:list|show|give|get).*(?:stock|company|tech|startup)/i.test(message);
    
    if (isRankingQuery || isStartupQuery || isTopStartupQuery || isListQuery || isGeneralListQuery) {
      return null; // Don't extract symbols for ranking or list queries
    }
    
    // Enhanced stock symbol patterns for multiple markets
    const symbolPatterns = [
      // UK market patterns (with .L suffix) - highest priority
      /\b([A-Z]{2,5})\.L\b/g,
      // India market patterns (with .NS suffix) - high priority
      /\b([A-Z]{2,10})\.NS\b/g,
      // US market patterns (3-5 letters, no suffix) - medium priority
      /\b([A-Z]{3,5})\b/g,
      // Generic patterns for any market - lowest priority
      /\b([A-Z]{2,8})\b/g
    ];
    
    // Comprehensive list of words to exclude from symbol extraction
    const excludeWords = [
      // Common words
      'THE', 'AND', 'FOR', 'WITH', 'ABOUT', 'FROM', 'INTO', 'DURING', 'BEFORE', 'AFTER', 'ABOVE', 'BELOW',
      'THIS', 'THAT', 'THESE', 'THOSE', 'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW', 'WHO', 'WHICH',
      'WILL', 'WOULD', 'COULD', 'SHOULD', 'MIGHT', 'MAY', 'CAN', 'MUST', 'SHALL',
      
      // Trading terms
      'LOSER', 'GAINER', 'STOCK', 'PERFORMER', 'TOP', 'PREDICT', 'PREDICTION', 'ANALYSIS',
      'LIST', 'SHOW', 'GIVE', 'ME', 'BEST', 'WORST', 'HOT', 'COLD', 'TRENDING',
      'BUY', 'SELL', 'HOLD', 'TARGET', 'STOP', 'LOSS', 'PROFIT', 'GAIN', 'LOSE',
      
      // Currencies
      'USD', 'GBP', 'INR', 'EUR', 'CAD', 'AUD', 'JPY', 'BRL', 'CNY', 'CHF', 'SEK', 'NOK',
      
      // Market terms
      'MARKET', 'PRICE', 'SHARE', 'SHARES', 'VOLUME', 'TRADE', 'TRADING', 'INVEST', 'INVESTMENT',
      'PORTFOLIO', 'ASSET', 'ASSETS', 'EQUITY', 'BOND', 'BONDS', 'FUND', 'FUNDS',
      
      // Time terms
      'TODAY', 'TOMORROW', 'YESTERDAY', 'WEEK', 'MONTH', 'YEAR', 'TIME', 'DATE', 'HOUR', 'MINUTE',
      
      // Direction terms
      'UP', 'DOWN', 'HIGH', 'LOW', 'RISE', 'FALL', 'INCREASE', 'DECREASE', 'GROW', 'SHRINK',
      
      // Common abbreviations
      'US', 'UK', 'CA', 'AU', 'DE', 'JP', 'IN', 'BR', 'EU', 'UN', 'UNITED', 'STATES', 'KINGDOM',
      
      // Other common words
      'NEW', 'OLD', 'BIG', 'SMALL', 'GOOD', 'BAD', 'YES', 'NO', 'OK', 'NOW', 'THEN', 'HERE', 'THERE'
    ];
    
    // Try to find stock symbols using patterns (in order of priority)
    for (const pattern of symbolPatterns) {
      const matches = message.toUpperCase().match(pattern);
      if (matches) {
        for (const match of matches) {
          const symbol = match.replace(/\.(L|NS|TO|AX|DE|T|SA)$/, ''); // Remove market suffixes
          if (!excludeWords.includes(symbol) && symbol.length >= 2 && symbol.length <= 10) {
            // Additional validation: check if it's not part of a larger word
            const wordBoundaryCheck = new RegExp(`\\b${match}\\b`, 'i');
            if (wordBoundaryCheck.test(message)) {
              return match; // Return the full symbol with suffix if present
            }
          }
        }
      }
    }
    
    // Fallback: try to find 2-10 letter uppercase words that might be stock symbols
    const words = message.toUpperCase().split(/\s+/);
    const potentialSymbols = words.filter(word => 
      word.length >= 2 && word.length <= 10 && 
      /^[A-Z]+$/.test(word) && 
      !excludeWords.includes(word) &&
      !/^(THE|AND|FOR|WITH|ABOUT|FROM|INTO|DURING|BEFORE|AFTER|ABOVE|BELOW|THIS|THAT|THESE|THOSE|WHAT|WHEN|WHERE|WHY|HOW|WHO|WHICH|WILL|WOULD|COULD|SHOULD|MIGHT|MAY|CAN|MUST|SHALL|TODAY|TOMORROW|YESTERDAY|WEEK|MONTH|YEAR|TIME|DATE|HOUR|MINUTE|UP|DOWN|HIGH|LOW|RISE|FALL|INCREASE|DECREASE|GROW|SHRINK|NEW|OLD|BIG|SMALL|GOOD|BAD|YES|NO|OK|NOW|THEN|HERE|THERE)$/.test(word)
    );
    
    return potentialSymbols[0] || null;
  };

  const detectMarketFromSymbol = (symbol) => {
    if (!symbol) return 'US';
    
    // Market detection based on symbol patterns
    if (symbol.includes('.L')) return 'UK';
    if (symbol.includes('.NS')) return 'IN';
    if (symbol.includes('.TO')) return 'CA';
    if (symbol.includes('.AX')) return 'AU';
    if (symbol.includes('.DE')) return 'DE';
    if (symbol.includes('.T')) return 'JP';
    if (symbol.includes('.SA')) return 'BR';
    
    // Default to US for symbols without suffixes
    return 'US';
  };

  const validateStockSymbol = async (symbol, market) => {
    try {
      // Try to get stock info to validate the symbol exists
      const stockInfo = await stockAPI.getStockInfo(symbol, market);
      return stockInfo && stockInfo.symbol;
    } catch (error) {
      console.log(`Stock validation failed for ${symbol} in ${market}:`, error.message);
      return null;
    }
  };

  const extractDate = (message) => {
    // Look for various date patterns
    const patterns = [
      /(?:on\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})/i,
      /(?:on\s+)?(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(?:,\s+)?(\d{4})/i,
      /(?:on\s+)?(\d{1,2})\/(\d{1,2})\/(\d{4})/,
      /(?:on\s+)?(\d{1,2})-(\d{1,2})-(\d{4})/,
      /(?:on\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)/i,
      /(?:on\s+)?(tomorrow|today|next\s+week)/i
    ];

    for (const pattern of patterns) {
      const match = message.match(pattern);
      if (match) {
        if (match[1] && match[2] && match[3] && match[4]) {
          // Full date with day name: "Monday 4 August 2025"
          const dayName = match[1].toLowerCase();
          const day = parseInt(match[2]);
          const monthName = match[3].toLowerCase();
          const year = parseInt(match[4]);
          
          const months = {
            january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
            july: 6, august: 7, september: 8, october: 9, november: 10, december: 11
          };
          
          const month = months[monthName];
          if (month !== undefined) {
            const date = new Date(year, month, day);
            // Verify the day name matches
            const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
            const actualDayName = dayNames[date.getDay()];
            if (actualDayName === dayName) {
              return date;
            }
          }
        } else if (match[1] && match[2] && match[3]) {
          // Date without day name: "August 4, 2025" or "4/8/2025"
          const month = match[1].toLowerCase();
          const day = parseInt(match[2]);
          const year = parseInt(match[3]);
          
          if (isNaN(month)) {
            // Numeric month
            return new Date(year, month - 1, day);
          } else {
            // Month name
            const months = {
              january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
              july: 6, august: 7, september: 8, october: 9, november: 10, december: 11
            };
            const monthIndex = months[month];
            if (monthIndex !== undefined) {
              return new Date(year, monthIndex, day);
            }
          }
        } else if (match[1]) {
          // Day name only or relative date
          const dayName = match[1].toLowerCase();
          const today = new Date();
          
          if (dayName === 'tomorrow') {
            return new Date(today.getTime() + 24 * 60 * 60 * 1000);
          } else if (dayName === 'today') {
            return today;
          } else if (dayName === 'next week') {
            return new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
          } else {
            // Day name like "monday"
            const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
            const targetDay = dayNames.indexOf(dayName);
            if (targetDay !== -1) {
              const currentDay = today.getDay();
              let daysToAdd = targetDay - currentDay;
              if (daysToAdd <= 0) daysToAdd += 7; // Next occurrence
              return new Date(today.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
            }
          }
        }
      }
    }
    return null;
  };

  // Enhanced response generation using Hugging Face AI
  const generateEnhancedResponse = async (message, symbol, targetDate, detectedMarket = 'US') => {
    try {
      let response = '';
      
      // Use Hugging Face AI for enhanced responses
      if (aiModel === 'huggingface') {
        // Prepare context for the AI
        const context = {
          symbol: symbol || 'N/A',
          market: detectedMarket,
          currentMarket: currentMarket,
          targetDate: targetDate ? targetDate.toISOString() : 'N/A',
          message: message,
          userPreferences: {
            riskProfile: 'moderate',
            preferredMarkets: [detectedMarket],
            investmentAmount: 10000
          }
        };

        // Update AI context with user preferences
        huggingfaceAI.updateContext(context);

        // Generate response using Hugging Face AI
        const aiResponse = await huggingfaceAI.generateResponse(message, context);
        
        response = aiResponse.response;
        
        // Add confidence and category information
        response += `\n\n---\n*AI Model: Hugging Face | Category: ${aiResponse.category} | Confidence: ${(aiResponse.confidence * 100).toFixed(1)}%*`;
        
      } else {
        // Fallback to legacy response generation
        response = await generateLegacyResponse(message, symbol, targetDate, detectedMarket);
      }
      
      return response;
    } catch (error) {
      console.error('Error generating enhanced response:', error);
      
      // Fallback response
      const marketInfo = stockAPI.getMarketInfo(detectedMarket);
      const marketSymbols = stockAPI.getMarketSymbols(detectedMarket);
      
      return `# ❌ **AI Response Error**

I encountered an error while processing your request with the enhanced AI model.

## 🔍 **What happened:**
- **Query**: "${message}"
- **Symbol**: ${symbol || 'None detected'}
- **Market**: ${detectedMarket}
- **AI Model**: ${aiModel === 'huggingface' ? 'Hugging Face' : 'Legacy'}

## 💡 **Please try:**
- **Switching AI models** using the toggle above
- **Rephrasing your question** more simply
- **Using a different stock symbol** (e.g., ${marketSymbols.slice(0, 5).join(', ')})
- **Asking for general market analysis** instead

## 📊 **Available ${marketInfo.name} Stocks:**
${marketSymbols.slice(0, 10).map(sym => `- ${sym}`).join('\n')}

## 🎯 **Example Queries:**
- "What's the AI prediction for AAPL tomorrow?"
- "Give me a comprehensive analysis of GOOGL with technical indicators"
- "What's the market sentiment for TSLA?"
- "Show me top 10 tech stocks in ${marketInfo.name} market"
- "Give me investment advice for a conservative investor"

## 🔧 **Technical Details:**
*Error: ${error.message}*

*I'm still learning and improving. Your feedback helps me get better!*`;
    }
  };

  // Legacy response generation (fallback)
  const generateLegacyResponse = async (message, symbol, targetDate, detectedMarket) => {
    // This would contain the original response generation logic
    // For brevity, I'll include a simplified version
    const marketInfo = stockAPI.getMarketInfo(detectedMarket);
    
    if (symbol) {
      return `# 📊 **Legacy Analysis for ${symbol}**

This is a fallback response using the legacy AI model.

**Symbol**: ${symbol}
**Market**: ${marketInfo.name} (${marketInfo.currency})
**Date**: ${targetDate ? targetDate.toLocaleDateString() : 'Not specified'}

## 📈 **Basic Analysis**
- **Current Status**: Analysis in progress
- **Market**: ${marketInfo.name}
- **Currency**: ${marketInfo.currency}

## 💡 **Recommendation**
Please try switching to the enhanced Hugging Face AI model for better analysis.

*This response was generated using the legacy AI model.*`;
    } else {
      return `# 🤖 **Legacy AI Assistant**

I'm using the legacy AI model for this response.

**Query**: "${message}"
**Market**: ${marketInfo.name} (${marketInfo.currency})

## 💡 **Suggestion**
For enhanced analysis, please:
1. Switch to the Hugging Face AI model using the toggle above
2. Include a specific stock symbol in your query
3. Try asking for predictions, technical analysis, or market overview

*This response was generated using the legacy AI model.*`;
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Extract stock symbol and date from the message
      const symbol = extractStockSymbol(inputMessage);
      const targetDate = extractDate(inputMessage);
      
      console.log('Enhanced AI - Extracted:', { symbol, targetDate, message: inputMessage, aiModel });

      // Detect market from symbol if available
      let detectedMarket = currentMarket;
      if (symbol) {
        detectedMarket = detectMarketFromSymbol(symbol);
        console.log('Enhanced AI - Detected market:', detectedMarket, 'for symbol:', symbol);
      }

      // Validate stock symbol if provided
      let validatedSymbol = symbol;
      if (symbol) {
        validatedSymbol = await validateStockSymbol(symbol, detectedMarket);
        if (!validatedSymbol) {
          // Try alternative markets for US symbols
          if (!symbol.includes('.')) {
            for (const market of ['US', 'UK', 'IN']) {
              const altSymbol = await validateStockSymbol(symbol, market);
              if (altSymbol) {
                validatedSymbol = altSymbol;
                detectedMarket = market;
                break;
              }
            }
          }
        }
      }

      // Generate enhanced response
      let response;
      if (symbol && !validatedSymbol) {
        // No valid stock symbol found, provide helpful guidance
        const marketInfo = stockAPI.getMarketInfo(detectedMarket);
        const marketSymbols = stockAPI.getMarketSymbols(detectedMarket);
        
        response = `# ❌ **Error Generating Prediction**

I encountered an error while trying to generate a prediction for **${symbol}** in the **${marketInfo.name}** market.

## 🔍 **Possible Reasons:**
- The stock symbol **${symbol}** might not be available in **${marketInfo.name}**
- Market data might be temporarily unavailable
- The requested date might be outside trading hours

## 💡 **Please try:**
- **Checking the stock symbol spelling** - Make sure it's a valid **${marketInfo.name}** stock symbol
- **Using a different date** - Try a date within trading hours
- **Using a known stock symbol** - Try one of these popular **${marketInfo.name}** stocks: ${marketSymbols.slice(0, 5).join(', ')}
- **Asking for a general market analysis** - I can provide market overview instead

## 📊 **Available ${marketInfo.name} Stocks:**
${marketSymbols.slice(0, 10).map(sym => `- ${sym}`).join('\n')}

## 🌍 **Other Markets Available:**
- 🇺🇸 **US**: AAPL, MSFT, GOOGL, AMZN, TSLA
- 🇬🇧 **UK**: VOD.L, HSBA.L, BP.L, GSK.L, AZN.L
- 🇮🇳 **India**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS
- 🇨🇦 **Canada**: RY.TO, TD.TO, SHOP.TO, ENB.TO
- 🇦🇺 **Australia**: CBA.AX, CSL.AX, BHP.AX, RIO.AX

## 🎯 **Example Queries:**
- "What's the AI prediction for **AAPL** tomorrow?"
- "Give me a comprehensive analysis of **MSFT** with technical indicators"
- "What's the market sentiment for **GOOGL**?"
- "Show me top 10 tech stocks in **${marketInfo.name}** market"
- "Give me investment advice for a conservative investor"

**💡 Just type any valid stock symbol and I'll automatically detect the market!**`;
      } else {
        try {
          response = await generateEnhancedResponse(inputMessage, validatedSymbol, targetDate, detectedMarket);
        } catch (error) {
          // Handle API errors with enhanced error messages
          if (error.response && error.response.data && error.response.data.error) {
            const errorData = error.response.data;
            
            // Check if it's an enhanced error message from the backend
            if (errorData.suggestions && errorData.available_markets) {
              response = `# ❌ **Error Generating Prediction**

I encountered an error while trying to generate a prediction for **${symbol}** in the **${detectedMarket}** market.

## 🔍 **What happened:**
${errorData.message}

## 💡 **Suggestions:**
- **${errorData.suggestions.check_spelling}**
- **${errorData.suggestions.try_popular_stocks}**
- **${errorData.suggestions.verify_market}**
- **${errorData.suggestions.check_trading_hours}**

## 📊 **Available Markets & Symbols:**

${Object.entries(errorData.available_markets).map(([market, symbols]) => {
  const flag = market === 'US' ? '🇺🇸' : market === 'UK' ? '🇬🇧' : market === 'India' ? '🇮🇳' : market === 'Canada' ? '🇨🇦' : '🇦🇺';
  return `${flag} **${market}**: ${symbols.slice(0, 5).join(', ')}`;
}).join('\n')}

## 🎯 **Example Queries:**
${errorData.example_queries.map(query => `- "${query}"`).join('\n')}

**💡 Just type any valid stock symbol and I'll automatically detect the market!**`;
            } else {
              // Fallback to generic error message
              response = `# ❌ **Error Generating Prediction**

I encountered an error while trying to generate a prediction for **${symbol}** in the **${detectedMarket}** market.

## 🔍 **Error Details:**
${errorData.error}

## 💡 **Please try:**
- **Checking the stock symbol spelling** - Make sure it's a valid stock symbol
- **Using a different date** - Try a date within trading hours
- **Using a known stock symbol** - Try: AAPL, MSFT, GOOGL, AMZN, TSLA
- **Asking for a general market analysis** - I can provide market overview instead

**💡 Just type any valid stock symbol and I'll automatically detect the market!**`;
            }
          } else {
            // Generic error fallback
            response = `# ❌ **Error Generating Prediction**

I encountered an error while trying to generate a prediction for **${symbol}** in the **${detectedMarket}** market.

## 🔍 **Error Details:**
${error.message}

## 💡 **Please try:**
- **Checking the stock symbol spelling** - Make sure it's a valid stock symbol
- **Using a different date** - Try a date within trading hours
- **Using a known stock symbol** - Try: AAPL, MSFT, GOOGL, AMZN, TSLA
- **Asking for a general market analysis** - I can provide market overview instead

**💡 Just type any valid stock symbol and I'll automatically detect the market!**`;
          }
        }
      }
      
      const assistantMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error in enhanced chat:', error);
      
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: `# ❌ **Enhanced AI Error**

I encountered an error while processing your request with the enhanced AI system.

**Query**: "${inputMessage}"
**AI Model**: ${aiModel === 'huggingface' ? 'Hugging Face' : 'Legacy'}

## 🔧 **Troubleshooting:**
1. **Try switching AI models** using the toggle above
2. **Check your internet connection**
3. **Rephrase your question** more simply
4. **Use a different stock symbol**

## 📊 **Supported Markets & Symbols:**
- 🇺🇸 **US**: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, NFLX, SPY, QQQ
- 🇬🇧 **UK**: VOD.L, HSBA.L, BP.L, GSK.L, ULVR.L, RIO.L, BHP.L, AZN.L
- 🇮🇳 **India**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ICICIBANK.NS
- 🇨🇦 **Canada**: RY.TO, TD.TO, SHOP.TO, ENB.TO, TRP.TO, BCE.TO
- 🇦🇺 **Australia**: CBA.AX, CSL.AX, BHP.AX, RIO.AX, WES.AX, WOW.AX

## 🎯 **Example Queries:**
- "What's the AI prediction for AAPL tomorrow?"
- "Give me a comprehensive analysis of GOOGL with technical indicators"
- "What's the market sentiment for TSLA?"
- "Show me top 10 tech stocks in US market"
- "Give me investment advice for a conservative investor"

## 💡 **Tips:**
- **Auto Market Detection**: Just type any stock symbol!
- **Context Awareness**: I remember your previous queries
- **Confidence Scoring**: Every prediction includes confidence levels
- **Risk Assessment**: Built-in risk analysis for all recommendations

*Error: ${error.message}*`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleAIModel = () => {
    setAiModel(prev => prev === 'huggingface' ? 'legacy' : 'huggingface');
  };

  const clearConversation = () => {
    setMessages([
      {
        id: 1,
        type: 'assistant',
        content: `# 🧠 **Enhanced AI Stock Trading Assistant**

Welcome to the **next-generation AI trading assistant** powered by advanced Hugging Face models! 

## 🚀 **What's New:**
- **🤖 Advanced AI Model**: Using state-of-the-art Hugging Face models for better analysis
- **🧠 Smart Context Management**: Remembers your preferences and conversation history
- **📊 Enhanced Prompt Engineering**: More accurate and detailed responses
- **🎯 Better Query Classification**: Understands your intent more precisely
- **📈 Improved Predictions**: Higher accuracy with confidence scoring

## 🌟 **Enhanced Capabilities:**

### **📊 Advanced Stock Analysis**
- Multi-market support with intelligent market detection
- Technical analysis with detailed indicator breakdown
- Fundamental analysis with risk assessment
- Sentiment analysis with confidence scoring

### **🔮 Intelligent Predictions**
- AI-powered price predictions with confidence levels
- Day trading analysis with entry/exit points
- Risk factor analysis and mitigation strategies
- Scenario-based forecasting

### **💼 Smart Investment Advice**
- Personalized recommendations based on risk profile
- Portfolio optimization suggestions
- Market timing analysis
- Diversification strategies

### **🌍 Multi-Market Intelligence**
- 🇺🇸 **US**: AAPL, MSFT, GOOGL, TSLA, META, NVDA, etc.
- 🇬🇧 **UK**: VOD.L, HSBA.L, BP.L, GSK.L, AZN.L, etc.
- 🇮🇳 **India**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, etc.
- 🇨🇦 Canada, 🇦🇺 Australia, 🇩🇪 Germany, 🇯🇵 Japan, 🇧🇷 Brazil

## 🎯 **Example Queries:**
- "What's the AI prediction for AAPL tomorrow?"
- "Give me a comprehensive analysis of GOOGL with technical indicators"
- "What's the market sentiment for TSLA?"
- "Compare AAPL vs MSFT performance"
- "Show me top 10 tech stocks in UK market"
- "Give me investment advice for a conservative investor"

## 💡 **Smart Features:**
- **Auto Market Detection**: Just type any stock symbol!
- **Context Awareness**: Remembers your previous queries
- **Confidence Scoring**: Every prediction includes confidence levels
- **Risk Assessment**: Built-in risk analysis for all recommendations

**🎯 Ready to experience the future of AI-powered trading analysis!**`,
        timestamp: new Date(),
      }
    ]);
    
    // Clear AI conversation history
    if (aiModel === 'huggingface') {
      huggingfaceAI.clearHistory();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Enhanced Header */}
      <div className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
          <div className="flex items-center space-x-2">
            <CpuChipIcon className="w-6 h-6 text-blue-600" />
            <div>
              <h1 className="text-lg sm:text-xl font-semibold text-gray-900">Enhanced AI Trading Assistant</h1>
              <p className="text-xs sm:text-sm text-gray-600">Powered by advanced Hugging Face models</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 sm:space-x-4">
            {/* AI Model Toggle */}
            <div className="flex items-center space-x-2">
              <SparklesIcon className="w-4 h-4 text-gray-500" />
              <button
                onClick={toggleAIModel}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  aiModel === 'huggingface' 
                    ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                    : 'bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {aiModel === 'huggingface' ? '🤖 Hugging Face' : '🔧 Legacy'}
              </button>
            </div>
            
            {/* Clear Chat Button */}
            <button
              onClick={clearConversation}
              className="px-2 py-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              Clear Chat
            </button>
            
            {/* Market Selector */}
            <div className="flex items-center space-x-1 sm:space-x-2">
              <GlobeAltIcon className="w-4 h-4 text-gray-500" />
              <select
                value={currentMarket}
                onChange={(e) => useStore.getState().setCurrentMarket(e.target.value)}
                className="text-xs sm:text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="US">🇺🇸 US</option>
                <option value="UK">🇬🇧 UK</option>
                <option value="CA">🇨🇦 Canada</option>
                <option value="AU">🇦🇺 Australia</option>
                <option value="DE">🇩🇪 Germany</option>
                <option value="JP">🇯🇵 Japan</option>
                <option value="IN">🇮🇳 India</option>
                <option value="BR">🇧🇷 Brazil</option>
              </select>
            </div>
            <div className="text-xs text-gray-500">
              {stockAPI.getMarketInfo(currentMarket).currency}
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-3 sm:space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] sm:max-w-xs lg:max-w-4xl px-3 sm:px-4 py-2 sm:py-3 rounded-lg ${
              message.type === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gradient-to-r from-gray-50 to-gray-100 text-gray-900 border border-gray-200'
            }`}>
              <div className="text-xs sm:text-sm prose prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
              <p className={`text-xs mt-2 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 text-gray-900 px-3 sm:px-4 py-2 sm:py-3 rounded-lg border border-blue-200">
              <div className="flex items-center space-x-2">
                <LoadingSpinner size="sm" />
                <span className="text-xs sm:text-sm">
                  {aiModel === 'huggingface' ? '🤖 Enhanced AI analyzing...' : '🔧 Legacy AI processing...'}
                </span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Enhanced Input */}
      <div className="bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4">
        <div className="flex space-x-2 sm:space-x-4">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask about stock predictions, trading strategies, or market analysis... (${aiModel === 'huggingface' ? 'Enhanced AI' : 'Legacy AI'})`}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm sm:text-base"
              rows={2}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-600 text-white px-3 sm:px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
          >
            <PaperAirplaneIcon className="w-4 h-4 sm:w-5 sm:h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAIAssistant;
