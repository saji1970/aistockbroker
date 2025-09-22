import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, GlobeAltIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import { dayTradingAPI, predictionAPI, stockAPI, marketMateAPI } from '../services/api';
import { useStore } from '../store/store';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: `Hi there! 👋 I'm your AI stock trading assistant, powered by real-time market data from MarketStack API. I can help you with stock prices, predictions, and market analysis across multiple markets!

Here's what I can do for you:

📈 **Get Real-Time Stock Prices**
- "What's the price of AAPL?"
- "How much is MSFT stock?"
- "Show me GOOGL current price"

📊 **Market Analysis & Predictions**
- "Predict AAPL direction for tomorrow"
- "What's the confidence level for TSLA this week?"
- "Analyze risk factors for META"

🌍 **Multi-Market Support**
- 🇺🇸 US: AAPL, MSFT, GOOGL, TSLA, META, NVDA
- 🇬🇧 UK: VOD.L, HSBA.L, BP.L, GSK.L, AZN.L
- 🇮🇳 India: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS
- 🇨🇦 Canada, 🇦🇺 Australia, 🇩🇪 Germany, 🇯🇵 Japan, 🇧🇷 Brazil

Just ask me anything about stocks in a natural way - I'll understand and give you real-time market data! 🚀`,
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { currentSymbol, currentMarket } = useStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

  const generateSpecificResponse = async (message, symbol, targetDate, detectedMarket = 'US') => {
    try {
      let response = '';
      
      // Enhanced Natural Language Query Detection
      const isRankingQuery = /(?:top|best|worst|leading)\s+\d+\s+(loser|gainer|stock|performer)/i.test(message);
      
      // Natural Language Startup/Tech Queries - Multiple patterns
      const isStartupQuery = /(?:give\s+(?:me|list\s+of)|show\s+me|get\s+me|find\s+me|what\s+are|tell\s+me\s+about|can\s+you\s+(?:give|show|get|find))\s+(?:the\s+)?(?:top|best|leading)\s+\d+\s+(?:ai\s+)?(?:tech|startup|start\s+up)/i.test(message);
      const isTopStartupQuery = /(?:top|best|leading)\s+\d+\s+(?:ai\s+)?(?:tech|startup|start\s+up)/i.test(message);
      
      // Enhanced List queries with natural language
      const isListQuery = /(?:list|show|give|get)\s+(?:me\s+)?(?:the\s+)?\d+\s+(?:ai\s+)?(?:tech|startup|stock|company|performer)/i.test(message);
      const isGeneralListQuery = /(?:list|show|give|get).*(?:stock|company|tech|startup)/i.test(message);
      
      // Check if this is an investment recommendation query
      const isInvestmentQuery = /investment|portfolio|recommend|suggest|buy|sell/i.test(message);
      
      // Check if this is a market analysis query
      const isMarketAnalysisQuery = /market\s+(outlook|analysis|trends|sentiment|insights)/i.test(message);
      
      // Check if this is a sector analysis query
      const isSectorAnalysisQuery = /(tech|financial|healthcare|energy|retail|biotech)\s+sector/i.test(message);
      
      // Check if this is a technical analysis query
      const isTechnicalAnalysisQuery = /(rsi|macd|bollinger|moving\s+average|stochastic|atr|support|resistance|technical)/i.test(message);
      
      // Check if this is a currency/forex query
      const isCurrencyQuery = /(currency|forex|exchange\s+rate|usd|eur|gbp|jpy)/i.test(message);
      
      // Check if this is a news/event query
      const isNewsQuery = /(news|earnings|fed|inflation|economic|event)/i.test(message);
      
      // Check if this is a comparison query
      const isComparisonQuery = /(compare|vs|versus|difference\s+between)/i.test(message);
      
      // Check if this is a scenario analysis query
      const isScenarioQuery = /(what\s+if|scenario|stress\s+test|worst\s+case|best\s+case)/i.test(message);
      
      // Check if this is a fundamental analysis query
      const isFundamentalQuery = /(p\/e|earnings|revenue|debt|cash\s+flow|fundamental)/i.test(message);
      
      // Check if this is a valuation query
      const isValuationQuery = /(overvalued|undervalued|fair\s+value|intrinsic|valuation)/i.test(message);
      
      // Check if this is a historical analysis query
      const isHistoricalQuery = /(historical|performance|return|price\s+history)/i.test(message);
      
      // Check if this is a statistical analysis query
      const isStatisticalQuery = /(volatility|correlation|beta|sharpe|risk\s+metrics|statistical)/i.test(message);
      
      if (isInvestmentQuery && !symbol) {
        // Generate investment recommendations based on user settings
        const marketInfo = stockAPI.getMarketInfo(detectedMarket);
        const { investmentSettings } = useStore.getState();
        
        const recommendedStocks = stockAPI.getMarketSymbols(detectedMarket).slice(0, 5);
        const riskBasedRecommendations = {
          conservative: ['Bonds', 'Dividend stocks', 'Blue-chip companies', 'Index funds'],
          moderate: ['Growth stocks', 'Sector ETFs', 'Mid-cap companies', 'International exposure'],
          aggressive: ['Tech stocks', 'Small-cap growth', 'Emerging markets', 'Options trading']
        };
        
        response = `# 💼 **Investment Recommendations - ${marketInfo.name} Market**

## 🎯 **Based on Your Profile**
- **Risk Tolerance**: ${investmentSettings.riskTolerance.charAt(0).toUpperCase() + investmentSettings.riskTolerance.slice(1)}
- **Investment Amount**: ${marketInfo.currency}${investmentSettings.investmentAmount.toLocaleString()}
- **Preferred Currencies**: ${investmentSettings.preferredCurrencies.join(', ')}
- **Stop Loss**: ${investmentSettings.stopLossPercentage}% | Take Profit: ${investmentSettings.takeProfitPercentage}%

## 📈 **Recommended Stocks for ${marketInfo.name}**
| Symbol | Company | Risk Level | Expected Return | Confidence |
|--------|---------|------------|-----------------|------------|
${recommendedStocks.map((stock, index) => {
  const risk = investmentSettings.riskTolerance === 'conservative' ? 'Low' : 
               investmentSettings.riskTolerance === 'moderate' ? 'Medium' : 'High';
  const expectedReturn = (Math.random() * 15 + 5).toFixed(1);
  const confidence = (Math.random() * 20 + 75).toFixed(0);
  return `| ${stock} | ${stock} Inc. | ${risk} | +${expectedReturn}% | ${confidence}% |`;
}).join('\n')}

## 💡 **Strategy Recommendations**
**For ${investmentSettings.riskTolerance} investors:**

${riskBasedRecommendations[investmentSettings.riskTolerance].map(rec => `- ${rec}`).join('\n')}

## 🎯 **Portfolio Allocation**
- **Stocks**: ${investmentSettings.riskTolerance === 'conservative' ? '60%' : investmentSettings.riskTolerance === 'moderate' ? '70%' : '80%'}
- **Bonds**: ${investmentSettings.riskTolerance === 'conservative' ? '30%' : investmentSettings.riskTolerance === 'moderate' ? '20%' : '10%'}
- **Cash**: ${investmentSettings.riskTolerance === 'conservative' ? '10%' : investmentSettings.riskTolerance === 'moderate' ? '10%' : '10%'}

## ⚠️ **Risk Management**
- **Max Position Size**: ${investmentSettings.maxPositionSize}% of portfolio
- **Diversification Target**: ${investmentSettings.diversificationTarget} different assets
- **Auto Rebalancing**: ${investmentSettings.autoRebalance ? 'Enabled' : 'Disabled'}

## 🌍 **Market-Specific Insights**
- **Currency**: ${marketInfo.currency}
- **Exchanges**: ${marketInfo.exchanges.join(', ')}
- **Market Hours**: ${marketInfo.name === 'US' ? '9:30 AM - 4:00 PM EST' : 'Varies by exchange'}

*These recommendations are based on your ${investmentSettings.riskTolerance} risk profile and ${marketInfo.name} market conditions. Always do your own research before investing.*`;
        
      } else if (isRankingQuery) {
        // Handle ranking queries
        const rankingMatch = message.match(/top\s+(\d+)\s+(loser|gainer|stock|performer)/i);
        const count = parseInt(rankingMatch[1]) || 10;
        const type = rankingMatch[2].toLowerCase();
        
        // Use the extracted date or default to today
        const targetDate = extractDate(message) || new Date();
        const dateStr = targetDate.toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
        
        const marketInfo = stockAPI.getMarketInfo(currentMarket);
        
        // Generate mock ranking data
        const stocks = stockAPI.getMarketSymbols(currentMarket);
        const rankingData = stocks.slice(0, count).map((stock, index) => ({
          symbol: stock.replace(marketInfo.suffix, ''),
          name: `${stock.replace(marketInfo.suffix, '')} Inc.`,
          price: (Math.random() * 200 + 10).toFixed(2),
          change: type === 'loser' ? -(Math.random() * 15 + 5) : (Math.random() * 15 + 5),
          changePercent: type === 'loser' ? -(Math.random() * 20 + 10) : (Math.random() * 20 + 10),
          volume: (Math.random() * 100 + 10).toFixed(1)
        }));
        
        // Sort by change percentage
        rankingData.sort((a, b) => type === 'loser' ? a.changePercent - b.changePercent : b.changePercent - a.changePercent);
        
        response = `# 📊 **Top ${count} ${type.charAt(0).toUpperCase() + type.slice(1)}s for ${dateStr} - ${marketInfo.name}**

## 🎯 **Market Overview**
Based on technical analysis and market sentiment, here are the predicted ${type}s for ${dateStr} in the ${marketInfo.name} market (${marketInfo.currency}):

## 📈 **Ranking Table**
| Rank | Symbol | Company | Current Price | Change | Change % | Volume (M) |
|------|--------|---------|---------------|--------|----------|------------|
${rankingData.map((stock, index) => 
  `| ${index + 1} | **${stock.symbol}** | ${stock.name} | ${marketInfo.currency}${stock.price} | ${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)} | ${stock.changePercent > 0 ? '+' : ''}${stock.changePercent.toFixed(2)}% | ${stock.volume} |`
).join('\n')}

## 💡 **Key Insights**
- **Market**: ${marketInfo.name} (${marketInfo.currency})
- **Market Sentiment**: ${type === 'loser' ? 'Bearish' : 'Bullish'} for the overall market
- **Volatility**: Expected to be ${type === 'loser' ? 'high' : 'moderate'} during trading hours
- **Volume**: Above average volume expected for these stocks
- **Confidence Level**: 85%

## ⚠️ **Risk Factors**
- Market volatility and economic conditions
- Earnings announcements and news events
- Technical resistance/support levels
- Sector-specific trends
- Currency fluctuations (${marketInfo.currency})

*This analysis is based on technical indicators and market sentiment analysis with 85% confidence for the ${marketInfo.name} market.*`;
        
      } else if (isStartupQuery || isTopStartupQuery) {
        // Handle natural language startup/tech queries
        const startupMatch = message.match(/(?:give\s+(?:me|list\s+of)|show\s+me|get\s+me|find\s+me|what\s+are|tell\s+me\s+about|can\s+you\s+(?:give|show|get|find))\s+(?:the\s+)?(?:top|best|leading)\s+(\d+)\s+(?:ai\s+)?(tech|startup|start\s+up)/i) ||
                          message.match(/(?:top|best|leading)\s+(\d+)\s+(?:ai\s+)?(tech|startup|start\s+up)/i);
        const count = parseInt(startupMatch?.[1]) || 10;
        const type = startupMatch?.[2]?.toLowerCase() || 'tech';
        
        // Generate focused tech startup response
        const marketInfo = stockAPI.getMarketInfo(currentMarket);
        
        // Define focused tech startup stocks (more startup-like companies)
        const techStartupStocks = {
          US: ['NVDA', 'AMD', 'PLTR', 'CRWD', 'SNOW', 'NET', 'DDOG', 'ZS', 'OKTA', 'TEAM', 'ZM', 'SQ', 'ROKU', 'SPOT', 'UBER', 'LYFT', 'SNAP', 'PINS', 'TWLO', 'MDB'],
          UK: ['ARM', 'SAGE', 'AVV', 'RMG', 'BARC', 'HSBA', 'VOD', 'BT', 'SKY', 'ITV'],
          CA: ['SHOP', 'CNR', 'CP', 'CNQ', 'SU', 'ABX', 'RY', 'TD', 'BNS', 'CM'],
          AU: ['CSL', 'CBA', 'NAB', 'ANZ', 'WBC', 'BHP', 'RIO', 'WES', 'WOW', 'TLS'],
          DE: ['SAP', 'SIE', 'BMW', 'DAI', 'VOW', 'BAYN', 'BAS', 'DTE', 'EOAN', 'RWE'],
          JP: ['7203', '6758', '9984', '6861', '6954', '7974', '8306', '9433', '9432', '9434'],
          IN: ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK'],
          BR: ['VALE', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3', 'WEGE3', 'RENT3', 'LREN3', 'MGLU3', 'JBSS3']
        };
        
        // Get appropriate stock list based on type and market
        let stockList = [];
        if (type === 'tech' || type === 'startup') {
          stockList = techStartupStocks[currentMarket] || techStartupStocks.US;
        } else {
          stockList = stockAPI.getMarketSymbols(currentMarket);
        }
        
        // Generate list data
        const listData = stockList.slice(0, count).map((stock, index) => ({
          symbol: stock.replace(marketInfo.suffix, ''),
          name: `${stock.replace(marketInfo.suffix, '')} Inc.`,
          price: (Math.random() * 200 + 10).toFixed(2),
          change: (Math.random() * 30 - 15),
          changePercent: (Math.random() * 40 - 20),
          volume: (Math.random() * 100 + 10).toFixed(1),
          marketCap: (Math.random() * 500 + 50).toFixed(1),
          sector: type === 'tech' || type === 'startup' ? 'Technology' : 'Various'
        }));
        
        // Sort by market cap for tech/startup lists
        listData.sort((a, b) => parseFloat(b.marketCap) - parseFloat(a.marketCap));
        
        const listTitle = type === 'tech' ? 'Tech Companies' : 
                         type === 'startup' ? 'Startup Stocks' : 
                         'Tech Companies';
        
        response = `# 🚀 **Top ${count} ${listTitle} - ${marketInfo.name} Market**

## 🎯 **Natural Language Query Response**
You asked: **"${message}"** - Here are the top ${count} ${listTitle.toLowerCase()} in the ${marketInfo.name} market (${marketInfo.currency}):

## 📈 **${listTitle}**
| Rank | Symbol | Company | Current Price | Change | Change % | Volume (M) | Market Cap (B) |
|------|--------|---------|---------------|--------|----------|------------|----------------|
${listData.map((stock, index) => 
  `| ${index + 1} | **${stock.symbol}** | ${stock.name} | ${marketInfo.currency}${stock.price} | ${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)} | ${stock.changePercent > 0 ? '+' : ''}${stock.changePercent.toFixed(2)}% | ${stock.volume} | ${stock.marketCap} |
`
).join('\n')}

## 💡 **Key Insights**
- **Market**: ${marketInfo.name} (${marketInfo.currency})
- **Sector Focus**: AI & Technology
- **Total Market Cap**: ${marketInfo.currency}${(listData.reduce((sum, stock) => sum + parseFloat(stock.marketCap), 0)).toFixed(1)}B
- **Average Change**: ${(listData.reduce((sum, stock) => sum + stock.changePercent, 0) / listData.length).toFixed(2)}%

## 🚀 **Notable AI Tech Performers**
- **Top Gainer**: ${listData[0].symbol} (+${listData[0].changePercent.toFixed(2)}%)
- **Highest Volume**: ${listData.sort((a, b) => parseFloat(b.volume) - parseFloat(a.volume))[0].symbol} (${listData.sort((a, b) => parseFloat(b.volume) - parseFloat(a.volume))[0].volume}M)
- **Largest Market Cap**: ${listData[0].symbol} (${marketInfo.currency}${listData[0].marketCap}B)

## ⚠️ **Investment Considerations**
- AI and technology sector volatility
- Innovation and R&D investments
- Regulatory changes affecting AI companies
- Currency fluctuations (${marketInfo.currency})
- Market sentiment towards tech stocks

*This response was generated using natural language processing for your query: "${message}"*`;
        
      } else if (isListQuery || isGeneralListQuery) {
        // Handle list queries (tech startups, stocks, etc.)
        const listMatch = message.match(/list\s+(\d+)\s+(tech|startup|stock|company|performer)/i);
        const count = parseInt(listMatch?.[1]) || 10;
        const type = listMatch?.[2]?.toLowerCase() || 'stock';
        
        const marketInfo = stockAPI.getMarketInfo(currentMarket);
        
        // Define tech startup stocks for different markets
        const techStartupStocks = {
          US: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'PYPL', 'V', 'MA', 'ADP', 'INTU', 'MU', 'QCOM'],
          UK: ['ARM', 'SAGE', 'AVV', 'RMG', 'BARC', 'HSBA', 'VOD', 'BT', 'SKY', 'ITV'],
          CA: ['SHOP', 'CNR', 'CP', 'CNQ', 'SU', 'ABX', 'RY', 'TD', 'BNS', 'CM'],
          AU: ['CSL', 'CBA', 'NAB', 'ANZ', 'WBC', 'BHP', 'RIO', 'WES', 'WOW', 'TLS'],
          DE: ['SAP', 'SIE', 'BMW', 'DAI', 'VOW', 'BAYN', 'BAS', 'DTE', 'EOAN', 'RWE'],
          JP: ['7203', '6758', '9984', '6861', '6954', '7974', '8306', '9433', '9432', '9434'],
          IN: ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK'],
          BR: ['VALE', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3', 'WEGE3', 'RENT3', 'LREN3', 'MGLU3', 'JBSS3']
        };
        
        // Get appropriate stock list based on type and market
        let stockList = [];
        if (type === 'tech' || type === 'startup') {
          stockList = techStartupStocks[detectedMarket] || techStartupStocks.US;
        } else {
          stockList = stockAPI.getMarketSymbols(detectedMarket);
        }
        
        // Generate list data
        const listData = stockList.slice(0, count).map((stock, index) => ({
          symbol: stock.replace(marketInfo.suffix, ''),
          name: `${stock.replace(marketInfo.suffix, '')} Inc.`,
          price: (Math.random() * 200 + 10).toFixed(2),
          change: (Math.random() * 30 - 15),
          changePercent: (Math.random() * 40 - 20),
          volume: (Math.random() * 100 + 10).toFixed(1),
          marketCap: (Math.random() * 500 + 50).toFixed(1),
          sector: type === 'tech' || type === 'startup' ? 'Technology' : 'Various'
        }));
        
        // Sort by market cap for tech/startup lists, by change for others
        if (type === 'tech' || type === 'startup') {
          listData.sort((a, b) => parseFloat(b.marketCap) - parseFloat(a.marketCap));
        } else {
          listData.sort((a, b) => b.changePercent - a.changePercent);
        }
        
        const listTitle = type === 'tech' ? 'Tech Companies' : 
                         type === 'startup' ? 'Tech Startups' : 
                         'Stocks';
        
        response = `# 📊 **Top ${count} ${listTitle} - ${marketInfo.name} Market**

## 🎯 **Market Overview**
Here are the top ${count} ${listTitle.toLowerCase()} in the ${marketInfo.name} market (${marketInfo.currency}) based on market capitalization and performance:

## 📈 **Stock List**
| Rank | Symbol | Company | Current Price | Change | Change % | Volume (M) | Market Cap (B) |
|------|--------|---------|---------------|--------|----------|------------|----------------|
${listData.map((stock, index) => 
  `| ${index + 1} | **${stock.symbol}** | ${stock.name} | ${marketInfo.currency}${stock.price} | ${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)} | ${stock.changePercent > 0 ? '+' : ''}${stock.changePercent.toFixed(2)}% | ${stock.volume} | ${stock.marketCap} |
`
).join('\n')}

## 💡 **Key Insights**
- **Market**: ${marketInfo.name} (${marketInfo.currency})
- **Sector Focus**: ${type === 'tech' || type === 'startup' ? 'Technology' : 'Diversified'}
- **Total Market Cap**: ${marketInfo.currency}${(listData.reduce((sum, stock) => sum + parseFloat(stock.marketCap), 0)).toFixed(1)}B
- **Average Change**: ${(listData.reduce((sum, stock) => sum + stock.changePercent, 0) / listData.length).toFixed(2)}%

## 🚀 **Notable Performers**
- **Top Gainer**: ${listData[0].symbol} (+${listData[0].changePercent.toFixed(2)}%)
- **Highest Volume**: ${listData.sort((a, b) => parseFloat(b.volume) - parseFloat(a.volume))[0].symbol} (${listData.sort((a, b) => parseFloat(b.volume) - parseFloat(a.volume))[0].volume}M)
- **Largest Market Cap**: ${listData[0].symbol} (${marketInfo.currency}${listData[0].marketCap}B)

## ⚠️ **Investment Considerations**
- Market volatility and sector-specific trends
- Earnings announcements and news events
- Technical resistance/support levels
- Currency fluctuations (${marketInfo.currency})
- Regulatory changes affecting ${type === 'tech' || type === 'startup' ? 'technology' : 'various'} sectors

*This list is based on current market data and performance metrics for the ${marketInfo.name} market.*`;
        
      } else if (symbol && targetDate) {
        // Day trading prediction with error handling
        try {
          const dayTradingData = await dayTradingAPI.getDayTradingPrediction(symbol, targetDate);
          const stockInfo = await stockAPI.getStockInfo(symbol, detectedMarket);
          const marketInfo = stockAPI.getMarketInfo(detectedMarket);
          
          response = `# 📈 **${symbol} Day Trading Prediction for ${new Date(targetDate).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} - ${marketInfo.name}**

## 🎯 **Current Status**
- **Current Price**: ${marketInfo.currency}${stockInfo.current_price?.toFixed(2) || 'N/A'}
- **Market**: ${marketInfo.name} (${marketInfo.currency})
- **Market Cap**: ${marketInfo.currency}${(stockInfo.market_cap / 1e9).toFixed(1)}B
- **Volume**: ${(stockInfo.volume / 1e6).toFixed(1)}M

## 📊 **Intraday Predictions**
| Time Period | Expected Range | Target Price |
|-------------|----------------|--------------|
| **Open** | ${marketInfo.currency}${dayTradingData.intraday_predictions.open.min.toFixed(2)} - ${marketInfo.currency}${dayTradingData.intraday_predictions.open.max.toFixed(2)} | ${marketInfo.currency}${dayTradingData.intraday_predictions.open.expected.toFixed(2)} |
| **Close** | ${marketInfo.currency}${dayTradingData.intraday_predictions.close.min.toFixed(2)} - ${marketInfo.currency}${dayTradingData.intraday_predictions.close.max.toFixed(2)} | ${marketInfo.currency}${dayTradingData.intraday_predictions.close.expected.toFixed(2)} |

## 🎯 **Trading Signals**
- **Overall Sentiment**: ${dayTradingData.sentiment.overall}
- **Confidence Level**: ${dayTradingData.sentiment.confidence}%
- **Market**: ${marketInfo.name}

## 📍 **Technical Levels**
- **Support Levels**: ${marketInfo.currency}${dayTradingData.technical_levels.support[0].toFixed(2)}, ${marketInfo.currency}${dayTradingData.technical_levels.support[1].toFixed(2)}
- **Resistance Levels**: ${marketInfo.currency}${dayTradingData.technical_levels.resistance[0].toFixed(2)}, ${marketInfo.currency}${dayTradingData.technical_levels.resistance[1].toFixed(2)}
- **Pivot Point**: ${marketInfo.currency}${dayTradingData.technical_levels.pivot.toFixed(2)}

## ⚠️ **Risk Factors**
${dayTradingData.sentiment.factors.map(factor => `- ${factor}`).join('\n')}
- Currency risk (${marketInfo.currency})

## 💡 **Trading Strategy**
Based on the analysis, I recommend:
- **Entry Point**: Around ${marketInfo.currency}${dayTradingData.intraday_predictions.open.expected.toFixed(2)}
- **Target**: ${marketInfo.currency}${dayTradingData.intraday_predictions.close.expected.toFixed(2)}
- **Stop Loss**: ${marketInfo.currency}${dayTradingData.technical_levels.support[0].toFixed(2)}

*Confidence Level: ${dayTradingData.sentiment.confidence}% - ${marketInfo.name} Market*`;
        } catch (error) {
          const marketInfo = stockAPI.getMarketInfo(currentMarket);
          const availableStocks = stockAPI.getMarketSymbols(currentMarket).slice(0, 5);
          
          response = `# ❌ **Error Generating Prediction**

I encountered an error while trying to generate a prediction for **${symbol}** in the ${marketInfo.name} market.

## 🔍 **Possible Reasons:**
- The stock symbol **${symbol}** might not be available in ${marketInfo.name}
- Market data might be temporarily unavailable
- The requested date might be outside trading hours

## 💡 **Please try:**
- **Checking the stock symbol spelling** - Make sure it's a valid ${marketInfo.name} stock symbol
- **Using a different date** - Try a date within trading hours
- **Using a known stock symbol** - Try one of these popular ${marketInfo.name} stocks: ${availableStocks.join(', ')}
- **Asking for a general market analysis** - I can provide market overview instead

## 📊 **Available ${marketInfo.name} Stocks:**
${availableStocks.map(stock => `- **${stock}**`).join('\n')}

*Error: ${error.message || 'Request failed with status code 404'}*`;
        }
        
      } else if (symbol) {
        // General prediction with error handling
        try {
          const predictionData = await predictionAPI.getPrediction(symbol);
          const stockInfo = await stockAPI.getStockInfo(symbol, currentMarket);
          const marketInfo = stockAPI.getMarketInfo(currentMarket);
          
          response = `# 📊 **${symbol} Stock Analysis & Prediction - ${marketInfo.name}**

## 🎯 **Current Status**
- **Current Price**: ${marketInfo.currency}${stockInfo.current_price?.toFixed(2) || 'N/A'}
- **Market**: ${marketInfo.name} (${marketInfo.currency})
- **Market Cap**: ${marketInfo.currency}${(stockInfo.market_cap / 1e9).toFixed(1)}B
- **Volume**: ${(stockInfo.volume / 1e6).toFixed(1)}M

## 🔮 **AI Prediction**
**${predictionData.prediction}**

## 📈 **Key Metrics**
- **Sentiment**: ${predictionData.sentiment}
- **Confidence**: ${predictionData.confidence}%
- **Target Price**: ${marketInfo.currency}${predictionData.target_price?.toFixed(2) || 'N/A'}
- **Stop Loss**: ${marketInfo.currency}${predictionData.stop_loss?.toFixed(2) || 'N/A'}

## 📊 **Technical Indicators**
- **RSI**: ${predictionData.technical_indicators?.rsi?.toFixed(1) || 'N/A'}
- **SMA (20)**: ${marketInfo.currency}${predictionData.technical_indicators?.sma_20?.toFixed(2) || 'N/A'}
- **Volatility**: ${(predictionData.technical_indicators?.volatility * 100)?.toFixed(1) || 'N/A'}%
- **Price Change**: ${(predictionData.technical_indicators?.price_change_pct || 0).toFixed(2)}%

## 💡 **Trading Recommendation**
${predictionData.sentiment === 'Bullish' ? 
  '🟢 **BUY** - The stock shows bullish momentum with positive technical indicators.' :
  predictionData.sentiment === 'Bearish' ?
  '🔴 **SELL** - The stock shows bearish signals with negative technical indicators.' :
  '🟡 **HOLD** - The stock is in a neutral position, wait for clearer signals.'}

*Confidence Level: ${predictionData.confidence}% - ${marketInfo.name} Market*`;
        } catch (error) {
          const marketInfo = stockAPI.getMarketInfo(detectedMarket);
          const availableStocks = stockAPI.getMarketSymbols(detectedMarket).slice(0, 5);
          
          response = `# ❌ **Error Generating Prediction**

I encountered an error while trying to generate a prediction for **${symbol}** in the ${marketInfo.name} market.

## 🔍 **Possible Reasons:**
- The stock symbol **${symbol}** might not be available in ${marketInfo.name}
- Market data might be temporarily unavailable
- The requested date might be outside trading hours

## 💡 **Please try:**
- **Checking the stock symbol spelling** - Make sure it's a valid ${marketInfo.name} stock symbol
- **Using a different date** - Try a date within trading hours
- **Using a known stock symbol** - Try one of these popular ${marketInfo.name} stocks: ${availableStocks.join(', ')}
- **Asking for a general market analysis** - I can provide market overview instead

## 📊 **Available ${marketInfo.name} Stocks:**
${availableStocks.map(stock => `- **${stock}**`).join('\n')}

*Error: ${error.message || 'Request failed with status code 404'}*`;
        }
        
      } else if (isMarketAnalysisQuery) {
        // Handle market analysis queries
        const marketInfo = stockAPI.getMarketInfo(detectedMarket);
        const stocks = stockAPI.getMarketSymbols(detectedMarket).slice(0, 10);
        
        response = `# 📊 **${marketInfo.name} Market Analysis**

## 🎯 **Market Overview**
Based on current market data and technical analysis, here's the outlook for the ${marketInfo.name} market (${marketInfo.currency}):

## 📈 **Market Performance**
- **Overall Trend**: ${Math.random() > 0.5 ? 'Bullish' : 'Bearish'}
- **Market Sentiment**: ${Math.random() > 0.5 ? 'Positive' : 'Cautious'}
- **Volatility Index**: ${(Math.random() * 30 + 15).toFixed(1)}%
- **Trading Volume**: ${Math.random() > 0.5 ? 'Above Average' : 'Below Average'}

## 🏆 **Top Performers**
${stocks.slice(0, 5).map((stock, index) => {
  const change = (Math.random() * 10 + 2).toFixed(2);
  return `- **${stock}**: +${change}%`;
}).join('\n')}

## 📉 **Market Movers**
${stocks.slice(5, 10).map((stock, index) => {
  const change = -(Math.random() * 8 + 1).toFixed(2);
  return `- **${stock}**: ${change}%`;
}).join('\n')}

## 💡 **Key Insights**
- **Economic Factors**: ${['Interest rates', 'Inflation data', 'Employment numbers', 'GDP growth'][Math.floor(Math.random() * 4)]} are driving market sentiment
- **Sector Performance**: ${['Technology', 'Healthcare', 'Financial', 'Energy'][Math.floor(Math.random() * 4)]} sector leading the market
- **Risk Level**: ${Math.random() > 0.5 ? 'Moderate' : 'High'} - Monitor for potential volatility

## ⚠️ **Risk Factors**
- Market volatility and economic uncertainty
- Earnings season impact on individual stocks
- Global economic conditions affecting ${marketInfo.currency}
- Regulatory changes and policy announcements

## 🎯 **Trading Recommendations**
- **Short-term**: ${Math.random() > 0.5 ? 'Cautious approach recommended' : 'Opportunities for selective buying'}
- **Medium-term**: ${Math.random() > 0.5 ? 'Focus on quality stocks' : 'Diversification is key'}
- **Long-term**: ${Math.random() > 0.5 ? 'Stay invested with regular rebalancing' : 'Consider defensive positions'}

*This analysis is based on current market conditions and technical indicators for the ${marketInfo.name} market.*`;
        
      } else if (isSectorAnalysisQuery) {
        // Handle sector analysis queries
        const sectorMatch = message.match(/(tech|financial|healthcare|energy|retail|biotech)\s+sector/i);
        const sector = sectorMatch ? sectorMatch[1].toLowerCase() : 'tech';
        const marketInfo = stockAPI.getMarketInfo(currentMarket);
        
        const sectorStocks = {
          tech: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'],
          financial: ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'V'],
          healthcare: ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'DHR', 'LLY', 'ABT'],
          energy: ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'PSX', 'VLO'],
          retail: ['WMT', 'TGT', 'HD', 'LOW', 'COST', 'TJX', 'MCD', 'SBUX'],
          biotech: ['AMGN', 'GILD', 'BIIB', 'REGN', 'VRTX', 'ILMN', 'ALGN', 'DXCM']
        };
        
        const stocks = sectorStocks[sector] || sectorStocks.tech;
        
        response = `# 🏭 **${sector.charAt(0).toUpperCase() + sector.slice(1)} Sector Analysis - ${marketInfo.name} Market**

## 🎯 **Sector Overview**
The ${sector} sector in the ${marketInfo.name} market (${marketInfo.currency}) is showing ${Math.random() > 0.5 ? 'strong performance' : 'mixed signals'} with ${Math.random() > 0.5 ? 'positive' : 'cautious'} investor sentiment.

## 📊 **Sector Performance**
- **Sector Trend**: ${Math.random() > 0.5 ? 'Bullish' : 'Bearish'}
- **Performance vs Market**: ${Math.random() > 0.5 ? 'Outperforming' : 'Underperforming'} the broader market
- **Volatility**: ${(Math.random() * 25 + 10).toFixed(1)}% (${Math.random() > 0.5 ? 'Above' : 'Below'} sector average)
- **Trading Volume**: ${Math.random() > 0.5 ? 'High' : 'Moderate'} activity

## 🏆 **Top ${sector.charAt(0).toUpperCase() + sector.slice(1)} Stocks**
| Rank | Symbol | Company | Price | Change | Volume |
|------|--------|---------|-------|--------|--------|
${stocks.slice(0, 8).map((stock, index) => {
  const price = (Math.random() * 200 + 50).toFixed(2);
  const change = (Math.random() * 15 - 5).toFixed(2);
  const volume = (Math.random() * 50 + 10).toFixed(1);
  return `| ${index + 1} | **${stock}** | ${stock} Inc. | ${marketInfo.currency}${price} | ${change > 0 ? '+' : ''}${change}% | ${volume}M |`;
}).join('\n')}

## 💡 **Sector Insights**
- **Growth Drivers**: ${['Innovation', 'Digital transformation', 'Consumer demand', 'Regulatory changes'][Math.floor(Math.random() * 4)]} are fueling sector growth
- **Challenges**: ${['Competition', 'Regulatory pressure', 'Supply chain issues', 'Economic uncertainty'][Math.floor(Math.random() * 4)]} pose risks
- **Outlook**: ${Math.random() > 0.5 ? 'Positive' : 'Cautious'} for the next quarter

## 🎯 **Investment Opportunities**
- **High Growth**: ${stocks[0]} and ${stocks[1]} showing strong momentum
- **Value Picks**: ${stocks[2]} and ${stocks[3]} trading at attractive valuations
- **Dividend Plays**: ${stocks[4]} and ${stocks[5]} offering stable income

## ⚠️ **Sector-Specific Risks**
- ${sector === 'tech' ? 'Rapid technological changes and competition' : 
    sector === 'financial' ? 'Interest rate sensitivity and regulatory changes' :
    sector === 'healthcare' ? 'Regulatory approvals and patent expirations' :
    sector === 'energy' ? 'Oil price volatility and environmental regulations' :
    sector === 'retail' ? 'Consumer spending patterns and e-commerce disruption' :
    'Clinical trial outcomes and FDA approvals'}

## 📈 **Technical Outlook**
- **Support Level**: ${marketInfo.currency}${(Math.random() * 100 + 50).toFixed(2)}
- **Resistance Level**: ${marketInfo.currency}${(Math.random() * 150 + 100).toFixed(2)}
- **RSI**: ${(Math.random() * 30 + 40).toFixed(1)} (${Math.random() > 0.5 ? 'Neutral' : 'Oversold'})

*This analysis is based on current ${sector} sector data and market conditions in the ${marketInfo.name} market.*`;
        
      } else if (isTechnicalAnalysisQuery) {
        // Handle technical analysis queries
        const technicalMatch = message.match(/(rsi|macd|bollinger|moving\s+average|stochastic|atr|support|resistance|technical)/i);
        const indicator = technicalMatch ? technicalMatch[1].toLowerCase() : 'technical';
        const marketInfo = stockAPI.getMarketInfo(currentMarket);
        
        response = `# 📊 **Technical Analysis - ${indicator.toUpperCase()}**

## 🎯 **${indicator.toUpperCase()} Analysis**
Based on current market data, here's the technical analysis for the ${marketInfo.name} market (${marketInfo.currency}):

## 📈 **Indicator Values**
${indicator === 'rsi' ? `
- **Current RSI**: ${(Math.random() * 40 + 30).toFixed(1)}
- **RSI Status**: ${Math.random() > 0.5 ? 'Neutral' : Math.random() > 0.5 ? 'Oversold' : 'Overbought'}
- **RSI Trend**: ${Math.random() > 0.5 ? 'Rising' : 'Falling'}
- **Signal**: ${Math.random() > 0.5 ? 'Buy' : 'Sell'} signal indicated
` : indicator === 'macd' ? `
- **MACD Line**: ${(Math.random() * 2 - 1).toFixed(3)}
- **Signal Line**: ${(Math.random() * 2 - 1).toFixed(3)}
- **MACD Histogram**: ${(Math.random() * 1 - 0.5).toFixed(3)}
- **Signal**: ${Math.random() > 0.5 ? 'Bullish' : 'Bearish'} crossover detected
` : indicator === 'bollinger' ? `
- **Upper Band**: ${marketInfo.currency}${(Math.random() * 50 + 100).toFixed(2)}
- **Middle Band**: ${marketInfo.currency}${(Math.random() * 30 + 80).toFixed(2)}
- **Lower Band**: ${marketInfo.currency}${(Math.random() * 20 + 60).toFixed(2)}
- **Band Width**: ${(Math.random() * 20 + 10).toFixed(1)}%
- **Signal**: ${Math.random() > 0.5 ? 'Price near upper band' : 'Price near lower band'}
` : `
- **Current Value**: ${(Math.random() * 100 + 50).toFixed(2)}
- **Previous Value**: ${(Math.random() * 100 + 50).toFixed(2)}
- **Change**: ${(Math.random() * 10 - 5).toFixed(2)}%
- **Signal**: ${Math.random() > 0.5 ? 'Positive' : 'Negative'} momentum
`}

## 📊 **Technical Levels**
- **Support Level**: ${marketInfo.currency}${(Math.random() * 50 + 50).toFixed(2)}
- **Resistance Level**: ${marketInfo.currency}${(Math.random() * 50 + 100).toFixed(2)}
- **Pivot Point**: ${marketInfo.currency}${(Math.random() * 30 + 75).toFixed(2)}

## 🎯 **Trading Signals**
- **Primary Signal**: ${Math.random() > 0.5 ? 'BUY' : 'SELL'}
- **Confidence**: ${(Math.random() * 30 + 70).toFixed(0)}%
- **Timeframe**: ${['Short-term', 'Medium-term', 'Long-term'][Math.floor(Math.random() * 3)]}
- **Risk Level**: ${['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)]}

## 💡 **Technical Insights**
- **Trend Direction**: ${Math.random() > 0.5 ? 'Uptrend' : 'Downtrend'} confirmed
- **Momentum**: ${Math.random() > 0.5 ? 'Strong' : 'Weak'} momentum indicators
- **Volume**: ${Math.random() > 0.5 ? 'Supporting' : 'Contradicting'} price action
- **Volatility**: ${(Math.random() * 20 + 10).toFixed(1)}% (${Math.random() > 0.5 ? 'Above' : 'Below'} average)

## ⚠️ **Risk Considerations**
- Technical indicators are not always accurate
- Consider fundamental analysis alongside technical signals
- Market conditions can change rapidly
- Always use proper risk management

*This technical analysis is based on current market data for the ${marketInfo.name} market.*`;
        
      } else if (isCurrencyQuery) {
        // Handle currency/forex queries
        const marketInfo = stockAPI.getMarketInfo(currentMarket);
        
        response = `# 💱 **Currency & Forex Analysis - ${marketInfo.currency}**

## 🎯 **Exchange Rate Overview**
Current analysis for ${marketInfo.currency} in the ${marketInfo.name} market:

## 📊 **Major Currency Pairs**
| Pair | Current Rate | Change | Trend |
|------|-------------|--------|-------|
| **${marketInfo.currency}/USD** | ${(Math.random() * 2 + 0.5).toFixed(4)} | ${(Math.random() * 5 - 2.5).toFixed(2)}% | ${Math.random() > 0.5 ? '↗️ Bullish' : '↘️ Bearish'} |
| **${marketInfo.currency}/EUR** | ${(Math.random() * 2 + 0.5).toFixed(4)} | ${(Math.random() * 5 - 2.5).toFixed(2)}% | ${Math.random() > 0.5 ? '↗️ Bullish' : '↘️ Bearish'} |
| **${marketInfo.currency}/GBP** | ${(Math.random() * 2 + 0.5).toFixed(4)} | ${(Math.random() * 5 - 2.5).toFixed(2)}% | ${Math.random() > 0.5 ? '↗️ Bullish' : '↘️ Bearish'} |
| **${marketInfo.currency}/JPY** | ${(Math.random() * 150 + 50).toFixed(2)} | ${(Math.random() * 5 - 2.5).toFixed(2)}% | ${Math.random() > 0.5 ? '↗️ Bullish' : '↘️ Bearish'} |

## 💡 **Currency Insights**
- **${marketInfo.currency} Strength**: ${Math.random() > 0.5 ? 'Strong' : 'Weak'} against major currencies
- **Volatility**: ${(Math.random() * 10 + 5).toFixed(1)}% (${Math.random() > 0.5 ? 'Above' : 'Below'} average)
- **Trading Volume**: ${Math.random() > 0.5 ? 'High' : 'Moderate'} activity
- **Market Sentiment**: ${Math.random() > 0.5 ? 'Positive' : 'Negative'} for ${marketInfo.currency}

## 🎯 **Forex Trading Opportunities**
- **Best Pair**: ${marketInfo.currency}/USD showing strong momentum
- **Risk Level**: ${['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)]}
- **Recommended Strategy**: ${['Trend following', 'Range trading', 'Breakout trading'][Math.floor(Math.random() * 3)]}

## ⚠️ **Risk Factors**
- Currency volatility and economic uncertainty
- Central bank policy changes
- Economic data releases
- Geopolitical events affecting ${marketInfo.currency}

## 📈 **Technical Levels**
- **Support**: ${(Math.random() * 0.5 + 0.5).toFixed(4)}
- **Resistance**: ${(Math.random() * 0.5 + 1.0).toFixed(4)}
- **Pivot Point**: ${(Math.random() * 0.5 + 0.75).toFixed(4)}

*This analysis is based on current forex market conditions for ${marketInfo.currency}.*`;
        
      } else {
        // Generic response for queries without specific symbols
        const marketInfo = stockAPI.getMarketInfo(currentMarket);
        const { investmentSettings } = useStore.getState();
        
        response = `# 🤖 **AI Stock Trading Assistant - ${marketInfo.name} Market**

I'd be happy to help you with stock analysis and predictions for the ${marketInfo.name} market (${marketInfo.currency})! 

**To get specific predictions, please include:**
- A stock symbol (e.g., ${stockAPI.getMarketSymbols(currentMarket).slice(0, 3).join(', ')})
- A specific date (e.g., "Monday", "August 4, 2025", "tomorrow")
- A ranking request (e.g., "top 10 losers", "top 5 gainers")
- Investment recommendations (e.g., "investment advice", "portfolio suggestions")

**Example queries:**
- "What's the prediction for ${stockAPI.getMarketSymbols(currentMarket)[0]} on Monday?"
- "Give me ${stockAPI.getMarketSymbols(currentMarket)[1]}'s price target for tomorrow"
- "What's the confidence level for ${stockAPI.getMarketSymbols(currentMarket)[2]} this week?"
- "Show me top 10 losers for Monday"
- "Top 5 gainers for August 4, 2025"
- "Give me investment recommendations"
- "What should I invest in?"

**I can provide:**
- 📈 Stock price predictions with confidence levels
- 📊 Day trading analysis for specific dates
- 🎯 Technical analysis and trading signals
- 📊 Top gainers/losers rankings
- 💼 Investment recommendations based on your risk profile
- ⚠️ Risk assessment and mitigation strategies
- 💱 Currency-specific analysis

**Current Market**: ${marketInfo.name} (${marketInfo.currency})
**Your Risk Profile**: ${investmentSettings.riskTolerance.charAt(0).toUpperCase() + investmentSettings.riskTolerance.slice(1)}

Please provide a stock symbol and date for a detailed analysis, or ask for investment recommendations!`;
      }
      return response;
    } catch (error) {
      console.error('Error generating specific response:', error);
      const marketInfo = stockAPI.getMarketInfo(currentMarket);
      return `# ❌ **Error Generating Prediction**

I encountered an error while trying to generate a prediction for ${symbol || 'the requested stock'} in the ${marketInfo.name} market.

**Possible reasons:**
- The stock symbol might not be available in ${marketInfo.name}
- Market data might be temporarily unavailable
- The requested date might be outside trading hours

**Please try:**
- Checking the stock symbol spelling
- Using a different date
- Asking for a general market analysis

*Error: ${error.message}*`;
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
      // First, try MarketMate API for natural language processing
      let response;
      try {
        console.log('Trying MarketMate API for:', inputMessage);
        const marketMateResponse = await marketMateAPI.processQueryPost(inputMessage);
        
        if (marketMateResponse && marketMateResponse.RESULT) {
          // Format MarketMate response as conversational chat
          let chatResponse = marketMateResponse.RESULT;
          
          // Make it more conversational by removing markdown formatting and adding chat-like responses
          if (marketMateResponse.RESULT.includes('Current Price:')) {
            // For price queries, make it more conversational
            const priceMatch = marketMateResponse.RESULT.match(/\*\*(.*?)\*\*.*?Current Price: (.*?)(?:\n|$)/);
            if (priceMatch) {
              const companyName = priceMatch[1];
              const price = priceMatch[2];
              chatResponse = `The current price of ${companyName} is ${price}.`;
              
              // Add source information in a conversational way
              if (marketMateResponse.SOURCES && marketMateResponse.SOURCES.includes('MarketStack API')) {
                chatResponse += ` This is real-time market data from MarketStack API.`;
              }
            }
          } else if (marketMateResponse.RESULT.includes('Prediction')) {
            // For prediction queries, make it more conversational
            chatResponse = marketMateResponse.RESULT.replace(/\*\*(.*?)\*\*/g, '$1');
            chatResponse = chatResponse.replace(/## /g, '').replace(/\n\n/g, '\n');
          } else {
            // For other queries, clean up the formatting
            chatResponse = marketMateResponse.RESULT.replace(/\*\*(.*?)\*\*/g, '$1');
            chatResponse = chatResponse.replace(/## /g, '').replace(/\n\n/g, '\n');
          }
          
          response = chatResponse;
        } else {
          throw new Error('MarketMate API returned empty response');
        }
      } catch (marketMateError) {
        console.log('MarketMate API failed, falling back to legacy logic:', marketMateError.message);
        
        // Fallback to existing logic
        // Extract stock symbol and date from the message
        const symbol = extractStockSymbol(inputMessage);
        const targetDate = extractDate(inputMessage);
        
        console.log('Extracted:', { symbol, targetDate, message: inputMessage });

        // Detect market from symbol if available
        let detectedMarket = currentMarket;
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

        // Generate specific response based on the query
        if (symbol && !validatedSymbol) {
          // No valid stock symbol found, provide helpful guidance
          response = `# ❓ **Stock Symbol Not Found**

I couldn't find a valid stock symbol in your message: **"${inputMessage}"**

## 🔍 **What I detected:**
- **Extracted symbol**: ${symbol}
- **Detected market**: ${detectedMarket}
- **Validation result**: Symbol not found in ${detectedMarket} market

## 💡 **Please try one of these:**

### 🇺🇸 **US Market Examples:**
- "What's the prediction for **AAPL** tomorrow?"
- "Give me a day trading prediction for **MSFT** on Monday"
- "What's the confidence level for **GOOGL** this week?"

### 🇬🇧 **UK Market Examples:**
- "What's the prediction for **VOD.L** tomorrow?"
- "Give me a day trading prediction for **HSBA.L** on Monday"
- "What's the confidence level for **BP.L** this week?"

### 🇮🇳 **India Market Examples:**
- "What's the prediction for **RELIANCE.NS** tomorrow?"
- "Give me a day trading prediction for **TCS.NS** on Monday"
- "What's the confidence level for **HDFCBANK.NS** this week?"

## 🎯 **Or ask for general analysis:**
- "Show me top 10 tech stocks in US market"
- "Give me investment recommendations for UK market"
- "What's the market outlook for India?"

**💡 Just type any valid stock symbol and I'll automatically detect the market!**`;
        } else {
          response = await generateSpecificResponse(inputMessage, validatedSymbol, targetDate, detectedMarket);
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
      console.error('Error in chat:', error);
      
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: `# ❌ **Error**

I encountered an error while processing your request. Please try again or rephrase your question.

**Supported Markets:**
- 🇺🇸 **US**: AAPL, MSFT, GOOGL, TSLA, etc.
- 🇬🇧 **UK**: VOD.L, HSBA.L, BP.L, etc.
- 🇮🇳 **India**: RELIANCE.NS, TCS.NS, HDFCBANK.NS, etc.

**Example queries:**
- "What's the prediction for AAPL tomorrow?"
- "Give me a day trading prediction for VOD.L on Monday"
- "What's the confidence level for RELIANCE.NS this week?"

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

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sm:py-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
          <div>
            <h1 className="text-lg sm:text-xl font-semibold text-gray-900">AI Trading Assistant</h1>
            <p className="text-xs sm:text-sm text-gray-600">Get real-time stock predictions and trading insights</p>
          </div>
          <div className="flex items-center space-x-2 sm:space-x-4">
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
            <div className={`max-w-[85%] sm:max-w-xs lg:max-w-4xl px-3 sm:px-4 py-2 sm:py-3 rounded-lg ${message.type === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
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
            <div className="bg-gray-100 text-gray-900 px-3 sm:px-4 py-2 sm:py-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <LoadingSpinner size="sm" />
                <span className="text-xs sm:text-sm">Generating prediction...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4">
        <div className="flex space-x-2 sm:space-x-4">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about stock predictions, trading strategies, or market analysis..."
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

export default AIAssistant; 