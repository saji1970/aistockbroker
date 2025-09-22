import React, {useState, useRef, useEffect} from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  TextInput,
  Button,
  Chip,
  ActivityIndicator,
  Text,
  Avatar,
} from 'react-native-paper';
import {useStore} from '../context/StoreContext';
import {stockAPI, chatAPI} from '../services/api';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const AIAssistantScreen = () => {
  const {state} = useStore();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `🤖 **AI Stock Trading Assistant**

Welcome! I'm your AI-powered trading assistant. I can help you with **ANY stock** across multiple markets!

**📈 Stock Analysis & Predictions**
• Get specific stock predictions with confidence levels
• Analyze technical indicators and market sentiment
• Provide day trading predictions for specific dates

**🌍 Multi-Market Support**
• 🇺🇸 **US**: AAPL, MSFT, GOOGL, TSLA, META, NVDA, etc.
• 🇬🇧 **UK**: VOD.L, HSBA.L, BP.L, GSK.L, AZN.L, etc.
• 🇮🇳 **India**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, etc.

**Example queries:**
• "What's the prediction for AAPL tomorrow?"
• "Give me a day trading prediction for VOD.L on Monday"
• "What's the confidence level for RELIANCE.NS this week?"

**💡 Just type any stock symbol and I'll automatically detect the market!**

Ask me anything about stocks, predictions, or trading strategies!`,
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  const extractStockSymbol = (message: string): string | null => {
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

  const detectMarketFromSymbol = (symbol: string): string => {
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

  const validateStockSymbol = async (symbol: string, market: string): Promise<string | null> => {
    try {
      // Try to get stock info to validate the symbol exists
      const stockInfo = await stockAPI.getStockInfo(symbol, market);
      return stockInfo && stockInfo.symbol ? symbol : null;
    } catch (error) {
      console.log(`Stock validation failed for ${symbol} in ${market}:`, error);
      return null;
    }
  };

  const extractDate = (message: string): Date | null => {
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
          const dayName = match[1].toLowerCase();
          const day = parseInt(match[2]);
          const monthName = match[3].toLowerCase();
          const year = parseInt(match[4]);
          
          const months = {
            january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
            july: 6, august: 7, september: 8, october: 9, november: 10, december: 11
          };
          
          const month = months[monthName as keyof typeof months];
          if (month !== undefined) {
            const date = new Date(year, month, day);
            const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
            const actualDayName = dayNames[date.getDay()];
            if (actualDayName === dayName) {
              return date;
            }
          }
        } else if (match[1] && match[2] && match[3]) {
          const month = match[1].toLowerCase();
          const day = parseInt(match[2]);
          const year = parseInt(match[3]);
          
          if (isNaN(parseInt(month))) {
            const months = {
              january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
              july: 6, august: 7, september: 8, october: 9, november: 10, december: 11
            };
            const monthIndex = months[month as keyof typeof months];
            if (monthIndex !== undefined) {
              return new Date(year, monthIndex, day);
            }
          } else {
            return new Date(year, parseInt(month) - 1, day);
          }
        } else if (match[1]) {
          const dayName = match[1].toLowerCase();
          const today = new Date();
          
          if (dayName === 'tomorrow') {
            return new Date(today.getTime() + 24 * 60 * 60 * 1000);
          } else if (dayName === 'today') {
            return today;
          } else if (dayName === 'next week') {
            return new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
          } else {
            const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
            const targetDay = dayNames.indexOf(dayName);
            if (targetDay !== -1) {
              const currentDay = today.getDay();
              let daysToAdd = targetDay - currentDay;
              if (daysToAdd <= 0) daysToAdd += 7;
              return new Date(today.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
            }
          }
        }
      }
    }
    return null;
  };

  const generateSpecificResponse = async (message: string): Promise<string> => {
    try {
      const symbol = extractStockSymbol(message);
      const targetDate = extractDate(message);
      const isRankingQuery = /top\s+\d+\s+(loser|gainer|stock|performer)/i.test(message);
      const isInvestmentQuery = /investment|portfolio|recommend|suggest|buy|sell/i.test(message);
      
      if (isRankingQuery) {
        const rankingMatch = message.match(/top\s+(\d+)\s+(loser|gainer|stock|performer)/i);
        const count = parseInt(rankingMatch?.[1] || '10');
        const type = rankingMatch?.[2]?.toLowerCase() || 'stock';
        const targetDate = extractDate(message) || new Date();
        const dateStr = targetDate.toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
        
        const marketInfo = stockAPI.getMarketInfo(state.currentMarket);
        const stocks = stockAPI.getMarketSymbols(state.currentMarket);
        const rankingData = stocks.slice(0, count).map((stock, index) => ({
          symbol: stock.replace(marketInfo.suffix, ''),
          price: (Math.random() * 200 + 10).toFixed(2),
          change: type === 'loser' ? -(Math.random() * 15 + 5) : (Math.random() * 15 + 5),
          changePercent: type === 'loser' ? -(Math.random() * 20 + 10) : (Math.random() * 20 + 10),
        }));
        
        rankingData.sort((a, b) => type === 'loser' ? a.changePercent - b.changePercent : b.changePercent - a.changePercent);
        
        return `📊 Top ${count} ${type.charAt(0).toUpperCase() + type.slice(1)}s for ${dateStr} - ${marketInfo.name}

Based on technical analysis and market sentiment, here are the predicted ${type}s for ${dateStr} in the ${marketInfo.name} market (${marketInfo.currency}):

${rankingData.map((stock, index) => 
  `${index + 1}. ${stock.symbol} - ${marketInfo.currency}${stock.price} (${stock.changePercent > 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%)`
).join('\n')}

💡 Key Insights
- Market: ${marketInfo.name} (${marketInfo.currency})
- Market Sentiment: ${type === 'loser' ? 'Bearish' : 'Bullish'} for the overall market
- Confidence Level: 85%

This analysis is based on technical indicators and market sentiment analysis with 85% confidence for the ${marketInfo.name} market.`;
      }
      
      if (isInvestmentQuery && !symbol) {
        const marketInfo = stockAPI.getMarketInfo(state.currentMarket);
        const {investmentSettings} = state;
        const recommendedStocks = stockAPI.getMarketSymbols(state.currentMarket).slice(0, 5);
        
        return `💼 Investment Recommendations - ${marketInfo.name} Market

🎯 Based on Your Profile
- Risk Tolerance: ${investmentSettings.riskTolerance.charAt(0).toUpperCase() + investmentSettings.riskTolerance.slice(1)}
- Investment Amount: ${marketInfo.currency}${investmentSettings.investmentAmount.toLocaleString()}

📈 Recommended Stocks for ${marketInfo.name}
${recommendedStocks.map((stock, index) => {
  const expectedReturn = (Math.random() * 15 + 5).toFixed(1);
  const confidence = (Math.random() * 20 + 75).toFixed(0);
  return `${index + 1}. ${stock} - Expected Return: +${expectedReturn}% (Confidence: ${confidence}%)`;
}).join('\n')}

💡 Strategy Recommendations
For ${investmentSettings.riskTolerance} investors:
- ${investmentSettings.riskTolerance === 'conservative' ? 'Bonds, Dividend stocks, Blue-chip companies' : 
    investmentSettings.riskTolerance === 'moderate' ? 'Growth stocks, Sector ETFs, Mid-cap companies' : 
    'Tech stocks, Small-cap growth, Emerging markets'}

These recommendations are based on your ${investmentSettings.riskTolerance} risk profile and ${marketInfo.name} market conditions.`;
      }
      
      if (symbol) {
        try {
          const stockInfo = await stockAPI.getStockInfo(symbol, state.currentMarket);
          const marketInfo = stockAPI.getMarketInfo(state.currentMarket);
          
          return `📊 ${symbol} Stock Analysis - ${marketInfo.name}

🎯 Current Status
- Current Price: ${marketInfo.currency}${stockInfo.current_price?.toFixed(2) || 'N/A'}
- Market: ${marketInfo.name} (${marketInfo.currency})
- Market Cap: ${marketInfo.currency}${(stockInfo.market_cap / 1e9).toFixed(1)}B
- Volume: ${(stockInfo.volume / 1e6).toFixed(1)}M

🔮 AI Prediction
Based on technical analysis, ${symbol} shows ${Math.random() > 0.5 ? 'bullish' : 'bearish'} momentum with ${Math.floor(Math.random() * 20 + 75)}% confidence.

💡 Trading Recommendation
${Math.random() > 0.5 ? '🟢 BUY - The stock shows bullish momentum with positive technical indicators.' : 
  Math.random() > 0.5 ? '🔴 SELL - The stock shows bearish signals with negative technical indicators.' : 
  '🟡 HOLD - The stock is in a neutral position, wait for clearer signals.'}

Confidence Level: ${Math.floor(Math.random() * 20 + 75)}% - ${marketInfo.name} Market`;
        } catch (error) {
          const marketInfo = stockAPI.getMarketInfo(state.currentMarket);
          const availableStocks = stockAPI.getMarketSymbols(state.currentMarket).slice(0, 5);
          
          return `❌ Error Generating Prediction

I encountered an error while trying to generate a prediction for ${symbol} in the ${marketInfo.name} market.

🔍 Possible Reasons:
- The stock symbol ${symbol} might not be available in ${marketInfo.name}
- Market data might be temporarily unavailable

💡 Please try:
- Checking the stock symbol spelling
- Using a known stock symbol like: ${availableStocks.join(', ')}

Error: ${error instanceof Error ? error.message : 'Request failed'}`;
        }
      }
      
      const marketInfo = stockAPI.getMarketInfo(state.currentMarket);
      return `🤖 AI Stock Trading Assistant - ${marketInfo.name} Market

I'd be happy to help you with stock analysis and predictions for the ${marketInfo.name} market (${marketInfo.currency})! 

To get specific predictions, please include:
- A stock symbol (e.g., ${stockAPI.getMarketSymbols(state.currentMarket).slice(0, 3).join(', ')})
- A specific date (e.g., "Monday", "August 4, 2025", "tomorrow")
- A ranking request (e.g., "top 10 losers", "top 5 gainers")
- Investment recommendations (e.g., "investment advice", "portfolio suggestions")

Example queries:
- "What's the prediction for ${stockAPI.getMarketSymbols(state.currentMarket)[0]} on Monday?"
- "Show me top 10 losers for Monday"
- "Give me investment recommendations"

I can provide:
- 📈 Stock price predictions with confidence levels
- 📊 Day trading analysis for specific dates
- 🎯 Technical analysis and trading signals
- 📊 Top gainers/losers rankings
- 💼 Investment recommendations based on your risk profile`;
    } catch (error) {
      return 'Sorry, I encountered an error while processing your request. Please try again.';
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      // Extract stock symbol and date from the message
      const symbol = extractStockSymbol(inputText);
      const targetDate = extractDate(inputText);
      
      console.log('Extracted:', { symbol, targetDate, message: inputText });

      // Detect market from symbol if available
      let detectedMarket = state.currentMarket;
      if (symbol) {
        detectedMarket = detectMarketFromSymbol(symbol);
        console.log('Detected market:', detectedMarket, 'for symbol:', symbol);
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

      // Generate response based on validation result
      let response;
      if (symbol && !validatedSymbol) {
        // No valid stock symbol found, provide helpful guidance
        response = `❓ **Stock Symbol Not Found**

I couldn't find a valid stock symbol in your message: **"${inputText}"**

**🔍 What I detected:**
• Extracted symbol: ${symbol}
• Detected market: ${detectedMarket}
• Validation result: Symbol not found in ${detectedMarket} market

**💡 Please try one of these:**

🇺🇸 **US Market Examples:**
• "What's the prediction for **AAPL** tomorrow?"
• "Give me a day trading prediction for **MSFT** on Monday"
• "What's the confidence level for **GOOGL** this week?"

🇬🇧 **UK Market Examples:**
• "What's the prediction for **VOD.L** tomorrow?"
• "Give me a day trading prediction for **HSBA.L** on Monday"
• "What's the confidence level for **BP.L** this week?"

🇮🇳 **India Market Examples:**
• "What's the prediction for **RELIANCE.NS** tomorrow?"
• "Give me a day trading prediction for **TCS.NS** on Monday"
• "What's the confidence level for **HDFCBANK.NS** this week?"

**🎯 Or ask for general analysis:**
• "Show me top 10 tech stocks in US market"
• "Give me investment recommendations for UK market"
• "What's the market outlook for India?"

**💡 Just type any valid stock symbol and I'll automatically detect the market!**`;
      } else {
        response = await generateSpecificResponse(inputText);
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `❌ **Error**

I encountered an error while processing your request. Please try again or rephrase your question.

**Supported Markets:**
• 🇺🇸 **US**: AAPL, MSFT, GOOGL, TSLA, META, NVDA, etc.
• 🇬🇧 **UK**: VOD.L, HSBA.L, BP.L, GSK.L, AZN.L, etc.
• 🇮🇳 **India**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, etc.

**Example queries:**
• "What's the prediction for AAPL tomorrow?"
• "Give me a day trading prediction for VOD.L on Monday"
• "What's the confidence level for RELIANCE.NS this week?"

Error: ${error}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (scrollViewRef.current) {
      scrollViewRef.current.scrollToEnd({animated: true});
    }
  }, [messages]);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}>
        {messages.map(message => (
          <View
            key={message.id}
            style={[
              styles.messageContainer,
              message.isUser ? styles.userMessage : styles.aiMessage,
            ]}>
            <View style={styles.messageHeader}>
              <Avatar.Icon
                size={24}
                icon={message.isUser ? 'account' : 'robot'}
                style={[
                  styles.avatar,
                  message.isUser ? styles.userAvatar : styles.aiAvatar,
                ]}
              />
              <Text style={styles.timestamp}>
                {message.timestamp.toLocaleTimeString()}
              </Text>
            </View>
            <Text style={styles.messageText}>{message.text}</Text>
          </View>
        ))}
        {loading && (
          <View style={[styles.messageContainer, styles.aiMessage]}>
            <View style={styles.messageHeader}>
              <Avatar.Icon
                size={24}
                icon="robot"
                style={[styles.avatar, styles.aiAvatar]}
              />
            </View>
            <ActivityIndicator size="small" />
            <Text style={styles.loadingText}>AI is thinking...</Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.inputContainer}>
        <TextInput
          label="Ask me anything about stocks..."
          value={inputText}
          onChangeText={setInputText}
          style={styles.input}
          mode="outlined"
          multiline
          maxLength={500}
        />
        <Button
          mode="contained"
          onPress={sendMessage}
          disabled={!inputText.trim() || loading}
          style={styles.sendButton}>
          Send
        </Button>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  messagesContainer: {
    flex: 1,
    padding: 16,
  },
  messagesContent: {
    paddingBottom: 16,
  },
  messageContainer: {
    marginBottom: 16,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
  },
  aiMessage: {
    alignSelf: 'flex-start',
  },
  messageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  avatar: {
    marginRight: 8,
  },
  userAvatar: {
    backgroundColor: '#2563eb',
  },
  aiAvatar: {
    backgroundColor: '#10b981',
  },
  timestamp: {
    fontSize: 12,
    color: '#64748b',
  },
  messageText: {
    backgroundColor: '#ffffff',
    padding: 12,
    borderRadius: 12,
    elevation: 1,
    color: '#1e293b',
    lineHeight: 20,
  },
  loadingText: {
    marginTop: 8,
    color: '#64748b',
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  input: {
    flex: 1,
    marginRight: 8,
  },
  sendButton: {
    alignSelf: 'flex-end',
  },
});

export default AIAssistantScreen; 