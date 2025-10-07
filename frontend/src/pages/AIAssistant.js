import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  PaperAirplaneIcon,
  PlusIcon,
  Bars3Icon,
  XMarkIcon,
  TrashIcon,
  CheckIcon,
  XCircleIcon,
  ArrowPathIcon,
  ClipboardDocumentIcon,
  Cog6ToothIcon,
  SunIcon,
  MoonIcon,
  UserIcon,
  SparklesIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowUpIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  BookmarkIcon,
  DocumentArrowDownIcon,
  ChevronDownIcon,
  CommandLineIcon,
  HomeIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { dayTradingAPI, predictionAPI, stockAPI, marketMateAPI } from '../services/api';
import { useStore } from '../store/store';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import ChatMessage from '../components/UI/ChatMessage';
import ChatInput from '../components/UI/ChatInput';
import ExportChat from '../components/UI/ExportChat';

const AIAssistant = () => {
  // Navigation
  const navigate = useNavigate();
  
  // State management
  const { currentMarket } = useStore();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedModel, setSelectedModel] = useState('gemini-1.5-pro');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Auto-resize textarea
  const autoResize = useCallback(() => {
    const textarea = inputRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  }, []);

  useEffect(() => {
    autoResize();
  }, [inputMessage, autoResize]);

  // Load chat history from localStorage
  const loadChatHistory = useCallback(() => {
    try {
      const savedHistory = localStorage.getItem('ai-assistant-chat-history');
      if (savedHistory) {
        const parsedHistory = JSON.parse(savedHistory);
        return parsedHistory.map(chat => ({
          ...chat,
          messages: chat.messages.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          })),
          timestamp: new Date(chat.timestamp)
        }));
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
    return [];
  }, []);

  // Save chat history to localStorage
  const saveChatHistory = useCallback((chats) => {
    try {
      localStorage.setItem('ai-assistant-chat-history', JSON.stringify(chats));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  }, []);

  // Initialize chat history
  useEffect(() => {
    const history = loadChatHistory();
    setChatHistory(history);
    
    if (history.length === 0) {
      createNewChat();
    } else {
      const latestChat = history[history.length - 1];
      setCurrentChatId(latestChat.id);
      setMessages(latestChat.messages || []);
    }
  }, [loadChatHistory]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  // Create new chat
  const createNewChat = useCallback(() => {
    const newChat = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      timestamp: new Date(),
      model: selectedModel,
      temperature,
      maxTokens
    };
    
    const updatedHistory = [...chatHistory, newChat];
    setChatHistory(updatedHistory);
    setCurrentChatId(newChat.id);
    setMessages([]);
    saveChatHistory(updatedHistory);
    setSidebarOpen(false);
    inputRef.current?.focus();
  }, [chatHistory, selectedModel, temperature, maxTokens, saveChatHistory]);

  // Load chat
  const loadChat = useCallback((chatId) => {
    const chat = chatHistory.find(c => c.id === chatId);
    if (chat) {
      setCurrentChatId(chatId);
      setMessages(chat.messages || []);
      setSidebarOpen(false);
      setSelectedModel(chat.model || 'gemini-1.5-pro');
      setTemperature(chat.temperature || 0.7);
      setMaxTokens(chat.maxTokens || 2048);
    }
  }, [chatHistory]);

  // Delete chat
  const deleteChat = useCallback((chatId) => {
    const updatedHistory = chatHistory.filter(c => c.id !== chatId);
    setChatHistory(updatedHistory);
    saveChatHistory(updatedHistory);
    
    if (currentChatId === chatId) {
      if (updatedHistory.length > 0) {
        loadChat(updatedHistory[0].id);
      } else {
        createNewChat();
      }
    }
  }, [chatHistory, currentChatId, createNewChat, loadChat, saveChatHistory]);

  // Update chat title
  const updateChatTitle = useCallback((chatId, title) => {
    const updatedHistory = chatHistory.map(chat => 
      chat.id === chatId ? { ...chat, title } : chat
    );
    setChatHistory(updatedHistory);
    saveChatHistory(updatedHistory);
  }, [chatHistory, saveChatHistory]);

  // Copy message to clipboard
  const copyMessage = useCallback(async (messageId, content) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      toast.success('Message copied to clipboard');
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (error) {
      console.error('Failed to copy message:', error);
      toast.error('Failed to copy message');
    }
  }, []);

  // Regenerate response
  const regenerateResponse = useCallback(async (messageId) => {
    const messageIndex = messages.findIndex(m => m.id === messageId);
    if (messageIndex === -1) return;
    
    const userMessage = messages[messageIndex - 1];
    if (!userMessage) return;
    
    // Remove the assistant message
    const newMessages = messages.slice(0, messageIndex);
    setMessages(newMessages);
    
    // Generate new response
    await handleSendMessage(userMessage.content, newMessages);
  }, [messages]);

  // Stop generation
  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
    setIsTyping(false);
    setStreamingMessage('');
  }, []);

  // Simulate streaming response
  const simulateStreaming = useCallback(async (response, onUpdate) => {
    const words = response.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      if (abortControllerRef.current?.signal.aborted) break;
      
      currentText += (i > 0 ? ' ' : '') + words[i];
      onUpdate(currentText);
      
      // Simulate typing delay
      await new Promise(resolve => setTimeout(resolve, 20 + Math.random() * 30));
    }
    
    return currentText;
  }, []);

  // Handle sending message
  const handleSendMessage = useCallback(async (messageContent = inputMessage, currentMessages = messages) => {
    if (!messageContent.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    const newMessages = [...currentMessages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);
    setStreamingMessage('');

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      let response = '';
      const query = messageContent.toLowerCase();

      // Enhanced API routing based on message content
      if (query.includes('price') || query.includes('stock') || query.includes('market') || query.includes('quote')) {
        const symbol = extractSymbol(messageContent);
        if (symbol) {
          try {
            const stockData = await stockAPI.getStockData(symbol, '1d', currentMarket);
            response = formatStockResponse(stockData, symbol);
          } catch (error) {
            console.error('Stock data error:', error);
            response = `I apologize, but I couldn't fetch stock data for ${symbol} at the moment. This could be due to:

- Invalid stock symbol
- Market is closed
- Temporary service issues

Please try again with a valid stock symbol like AAPL, MSFT, or GOOGL.`;
          }
        } else {
          response = `I can help you get stock prices and market data. Please specify a stock symbol like AAPL, MSFT, or GOOGL.

**Available Commands:**
- "What's the price of AAPL?"
- "Show me MSFT stock data"
- "Get market data for GOOGL"`;
        }
      } else if (query.includes('predict') || query.includes('forecast') || query.includes('prediction')) {
        const symbol = extractSymbol(messageContent);
        if (symbol) {
          try {
            const predictionResponse = await predictionAPI.getPrediction(symbol);
            response = formatPredictionResponse(predictionResponse, symbol);
          } catch (error) {
            console.error('Prediction error:', error);
            response = `I apologize, but I couldn't generate a prediction for ${symbol} at the moment. Please try again with a valid stock symbol.`;
          }
        } else {
          response = `I can provide AI-powered stock predictions. Please specify a stock symbol.

**Example requests:**
- "Predict AAPL direction for tomorrow"
- "What's the forecast for TSLA?"
- "Get prediction for MSFT stock"`;
        }
      } else if (query.includes('day trading') || query.includes('trading strategy') || query.includes('trade')) {
        const symbol = extractSymbol(messageContent);
        if (symbol) {
          try {
            const tradingResponse = await dayTradingAPI.getDayTradingPrediction(symbol, 'today');
            response = formatTradingResponse(tradingResponse, symbol);
          } catch (error) {
            console.error('Trading analysis error:', error);
            response = `I apologize, but I couldn't analyze trading opportunities for ${symbol} at the moment. Please try again with a valid stock symbol.`;
          }
        } else {
          response = `I can analyze day trading opportunities and strategies. Please specify a stock symbol.

**Example requests:**
- "Day trading strategy for MSFT"
- "Trading analysis for AAPL"
- "Get trade signals for TSLA"`;
        }
      } else if (query.includes('portfolio') || query.includes('holdings') || query.includes('investment')) {
        response = `I can help you analyze your portfolio and investment strategies.

**Portfolio Features:**
- Portfolio performance analysis
- Risk assessment
- Diversification recommendations
- Asset allocation suggestions

**Example requests:**
- "Analyze my portfolio performance"
- "What's my portfolio risk level?"
- "Suggest portfolio rebalancing"`;
      } else if (query.includes('market') && (query.includes('analysis') || query.includes('overview') || query.includes('trend'))) {
        response = `I can provide comprehensive market analysis and insights.

**Market Analysis Features:**
- Sector performance analysis
- Market trend identification
- Economic indicators review
- Market sentiment analysis

**Example requests:**
- "Analyze tech sector performance"
- "What are the current market trends?"
- "Get market sentiment analysis"`;
      } else {
        // Use Gemini for general stock analysis when Gemini model is selected
        if (selectedModel === 'gemini-1.5-pro') {
          try {
            const geminiResponse = await fetch('/api/ai/gemini-query', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                query: messageContent,
                temperature: temperature,
                maxTokens: maxTokens,
                market: currentMarket
              })
            });
            
            if (geminiResponse.ok) {
              const geminiData = await geminiResponse.json();
              response = geminiData.response || geminiData.message || generateDefaultResponse(messageContent);
            } else {
              response = generateDefaultResponse(messageContent);
            }
          } catch (error) {
            console.error('Gemini API error:', error);
            response = generateDefaultResponse(messageContent);
          }
        } else {
          // General market mate response for other models
          try {
            const marketResponse = await marketMateAPI.query(messageContent);
            response = marketResponse.message || generateDefaultResponse(messageContent);
          } catch (error) {
            response = generateDefaultResponse(messageContent);
          }
        }
      }

      // Simulate streaming response
      await simulateStreaming(response, (streamedText) => {
        setStreamingMessage(streamedText);
      });

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response,
        timestamp: new Date(),
        model: selectedModel,
        temperature,
        maxTokens
      };

      const updatedMessages = [...newMessages, assistantMessage];
      setMessages(updatedMessages);
      setStreamingMessage('');

      // Update chat history
      const updatedHistory = chatHistory.map(chat => 
        chat.id === currentChatId 
          ? { 
              ...chat, 
              messages: updatedMessages,
              title: chat.title === 'New Chat' ? generateChatTitle(messageContent) : chat.title,
              model: selectedModel,
              temperature,
              maxTokens
            }
          : chat
      );
      setChatHistory(updatedHistory);
      saveChatHistory(updatedHistory);

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
        return;
      }
      
      console.error('Error sending message:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I apologize, but I encountered an error while processing your request. Please try again or rephrase your question.

**Error Details:** ${error.message}

**Troubleshooting Tips:**
- Check your internet connection
- Try rephrasing your question
- Make sure you're using valid stock symbols
- Contact support if the issue persists`,
        timestamp: new Date(),
        isError: true
      };

      const errorMessages = [...newMessages, errorMessage];
      setMessages(errorMessages);

      // Update chat history with error
      const updatedHistory = chatHistory.map(chat => 
        chat.id === currentChatId 
          ? { ...chat, messages: errorMessages }
          : chat
      );
      setChatHistory(updatedHistory);
      saveChatHistory(updatedHistory);
      
      toast.error('Failed to process request');
    } finally {
      setIsLoading(false);
      setIsTyping(false);
      abortControllerRef.current = null;
    }
  }, [inputMessage, messages, currentChatId, chatHistory, selectedModel, temperature, maxTokens, currentMarket, saveChatHistory, simulateStreaming]);

  // Helper functions
  const extractSymbol = (text) => {
    const symbolRegex = /\b[A-Z]{1,5}\b/g;
    const matches = text.match(symbolRegex);
    if (matches) {
      // Enhanced filtering to exclude common words and invalid symbols
      const commonWords = [
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'BY', 'WORD', 'WHAT', 'SOME', 'WE', 'IT', 'IS', 'OR', 'HAVE', 'AS', 'BE', 'IN', 'ON', 'AT', 'TO', 'OF', 'A', 'I',
        // Country/region codes that are not stock symbols
        'US', 'UK', 'CA', 'AU', 'EU', 'JP', 'CN', 'IN', 'BR', 'MX', 'DE', 'FR', 'IT', 'ES', 'NL', 'SE', 'NO', 'DK', 'FI', 'CH', 'AT', 'BE', 'IE', 'PT', 'GR', 'PL', 'CZ', 'HU', 'RO', 'BG', 'HR', 'SI', 'SK', 'LT', 'LV', 'EE', 'CY', 'MT', 'LU',
        // Common abbreviations that are not stock symbols
        'CEO', 'CFO', 'CTO', 'COO', 'VP', 'GM', 'PM', 'HR', 'IT', 'AI', 'ML', 'DL', 'API', 'URL', 'PDF', 'JPG', 'PNG', 'GIF', 'MP3', 'MP4', 'AVI', 'MOV', 'ZIP', 'RAR', 'TXT', 'DOC', 'XLS', 'PPT', 'CSV', 'JSON', 'XML', 'HTML', 'CSS', 'JS', 'PHP', 'SQL', 'DB', 'ID', 'OK', 'NO', 'YES', 'NEW', 'OLD', 'BIG', 'SMALL', 'HIGH', 'LOW', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM', 'FRONT', 'BACK', 'SIDE', 'CENTER', 'MIDDLE', 'START', 'END', 'BEGIN', 'FINISH', 'STOP', 'GO', 'RUN', 'WALK', 'SIT', 'STAND', 'LIE', 'SLEEP', 'WAKE', 'EAT', 'DRINK', 'READ', 'WRITE', 'TALK', 'LISTEN', 'SEE', 'LOOK', 'WATCH', 'HEAR', 'FEEL', 'TOUCH', 'HOLD', 'GRAB', 'PUSH', 'PULL', 'OPEN', 'CLOSE', 'LOCK', 'UNLOCK', 'TURN', 'MOVE', 'STAY', 'COME', 'GO', 'LEAVE', 'ENTER', 'EXIT', 'ARRIVE', 'DEPART', 'RETURN', 'COME', 'BACK', 'AGAIN', 'ONCE', 'TWICE', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'HUNDRED', 'THOUSAND', 'MILLION', 'BILLION', 'TRILLION'
      ];
      
      // Find the first valid symbol that's not in common words
      const validSymbol = matches.find(match => !commonWords.includes(match));
      
      // Additional validation: ensure it looks like a real stock symbol
      if (validSymbol && validSymbol.length >= 2 && validSymbol.length <= 5) {
        // Check if it's likely a real stock symbol (contains at least one letter)
        if (/[A-Z]/.test(validSymbol)) {
          return validSymbol;
        }
      }
    }
    return null;
  };

  const formatStockResponse = (data, symbol) => {
    if (!data || !data.summary) {
      return `I couldn't fetch stock data for ${symbol} at the moment. Please check the symbol and try again.`;
    }

    const summary = data.summary;
    return `## 📊 ${symbol} Stock Information

**Current Price:** $${summary.current_price?.toFixed(2) || 'N/A'}
**Change:** ${summary.price_change >= 0 ? '+' : ''}${summary.price_change?.toFixed(2) || 'N/A'} (${summary.price_change_pct >= 0 ? '+' : ''}${summary.price_change_pct?.toFixed(2) || 'N/A'}%)
**Volume:** ${summary.volume?.toLocaleString() || 'N/A'}
**Market Cap:** ${summary.market_cap ? `$${(summary.market_cap / 1e9).toFixed(1)}B` : 'N/A'}

**52-Week Range:** $${summary.low_52w?.toFixed(2) || 'N/A'} - $${summary.high_52w?.toFixed(2) || 'N/A'}
**PE Ratio:** ${summary.pe_ratio || 'N/A'}
**Dividend Yield:** ${summary.dividend_yield || 'N/A'}

*Data as of ${new Date().toLocaleString()}*`;
  };

  const formatPredictionResponse = (data, symbol) => {
    if (!data || !data.prediction) {
      return `I couldn't generate a prediction for ${symbol} at the moment. Please try again later.`;
    }

    const prediction = data.prediction;
    return `## 🔮 ${symbol} AI Prediction

**Direction:** ${prediction.direction || 'Neutral'} ${prediction.direction === 'Bullish' ? '📈' : prediction.direction === 'Bearish' ? '📉' : '➡️'}
**Confidence:** ${prediction.confidence || 'N/A'}%
**Target Price:** $${prediction.target_price || 'N/A'}
**Timeframe:** ${prediction.timeframe || 'N/A'}

**Technical Analysis:**
${prediction.technical_analysis || 'Analysis based on current market conditions and technical indicators.'}

**Fundamental Analysis:**
${prediction.fundamental_analysis || 'Review of company fundamentals and market conditions.'}

**Risk Assessment:** ${prediction.risk_level || 'Medium'}

⚠️ **Disclaimer:** This prediction is for educational purposes only and not financial advice. Always do your own research before making investment decisions.`;
  };

  const formatTradingResponse = (data, symbol) => {
    if (!data || !data.prediction) {
      return `I couldn't generate day trading analysis for ${symbol} at the moment. Please try again later.`;
    }

    const prediction = data.prediction;
    return `## 🎯 Day Trading Strategy for ${symbol}

**Strategy Type:** ${prediction.strategy || 'Momentum Trading'}
**Entry Point:** $${prediction.entry_price || 'N/A'}
**Stop Loss:** $${prediction.stop_loss || 'N/A'}
**Take Profit:** $${prediction.take_profit || 'N/A'}
**Risk Level:** ${prediction.risk_level || 'Medium'}
**Confidence:** ${prediction.confidence || 'N/A'}%

**Trading Plan:**
1. **Entry:** Wait for price to reach entry point with confirmation
2. **Management:** Use stop loss to limit downside risk
3. **Exit:** Take profit at target or stop loss if hit

**Key Levels to Watch:**
- Entry: $${prediction.entry_price || 'N/A'}
- Stop Loss: $${prediction.stop_loss || 'N/A'}
- Take Profit: $${prediction.take_profit || 'N/A'}

⚠️ **Risk Warning:** Day trading involves significant risk and can result in substantial financial losses. Only trade with money you can afford to lose.`;
  };

  const generateDefaultResponse = (query) => {
    return `I'm your AI Trading Assistant! 🤖 I can help you with various aspects of stock trading and market analysis.

**What I can help you with:**

📈 **Stock Information**
- Current prices and market data
- Historical performance
- Company fundamentals

🔮 **AI Predictions**
- Price direction forecasts
- Technical analysis
- Market sentiment analysis

🎯 **Trading Strategies**
- Day trading opportunities
- Risk management
- Position sizing

📊 **Portfolio Analysis**
- Performance tracking
- Risk assessment
- Diversification advice

**Try asking me:**
- "What's the price of AAPL?"
- "Predict TSLA direction for tomorrow"
- "Day trading strategy for MSFT"
- "Analyze my portfolio risk"

What would you like to know about the stock market?`;
  };

  const generateChatTitle = (message) => {
    const words = message.split(' ').slice(0, 4);
    return words.join(' ') + (message.split(' ').length > 4 ? '...' : '');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const filteredChatHistory = chatHistory.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chat.messages.some(msg => msg.content.toLowerCase().includes(searchQuery.toLowerCase()))
  );


  return (
    <div className={`flex h-screen ${darkMode ? 'bg-gray-900' : 'bg-white'}`}>
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 ${darkMode ? 'bg-gray-800' : 'bg-gray-50'} border-r ${darkMode ? 'border-gray-700' : 'border-gray-200'} overflow-hidden flex flex-col`}>
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Chat History</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className={`p-1 rounded-lg hover:bg-gray-200 ${darkMode ? 'hover:bg-gray-700' : ''}`}
            >
              <XMarkIcon className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          
          <button
            onClick={createNewChat}
            className={`w-full flex items-center space-x-2 px-3 py-2 rounded-lg border transition-colors ${
              darkMode 
                ? 'border-gray-700 hover:bg-gray-700 text-white' 
                : 'border-gray-300 hover:bg-gray-100 text-gray-700'
            }`}
          >
            <PlusIcon className="w-4 h-4" />
            <span>New Chat</span>
          </button>

          <div className="relative mt-4">
            <MagnifyingGlassIcon className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full pl-10 pr-4 py-2 rounded-lg border text-sm ${
                darkMode 
                  ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                  : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
              }`}
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {filteredChatHistory.map((chat) => (
              <div
                key={chat.id}
                className={`p-3 rounded-lg cursor-pointer group transition-colors ${
                  currentChatId === chat.id
                    ? darkMode ? 'bg-gray-700' : 'bg-blue-50'
                    : darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'
                }`}
                onClick={() => loadChat(chat.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <span className={`text-sm font-medium truncate block ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                      {chat.title}
                    </span>
                    <p className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'} mt-1`}>
                      {chat.messages.length} messages • {chat.timestamp.toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteChat(chat.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                  >
                    <TrashIcon className="w-3 h-3 text-red-500" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`flex items-center justify-between p-4 border-b ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex items-center space-x-4">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className={`p-2 rounded-lg hover:bg-gray-100 ${darkMode ? 'hover:bg-gray-700' : ''}`}
              >
                <Bars3Icon className="w-5 h-5 text-gray-500" />
              </button>
            )}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <SparklesIcon className="w-4 h-4 text-white" />
              </div>
              <h1 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                StockBroker AI Assistant
              </h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate('/dashboard')}
              className={`p-2 rounded-lg hover:bg-gray-100 ${darkMode ? 'hover:bg-gray-700' : ''}`}
              title="Go to Main Page"
              aria-label="Go to Main Page"
            >
              <HomeIcon className="w-5 h-5 text-gray-500" />
            </button>
            <button
              onClick={() => setShowExport(true)}
              className={`p-2 rounded-lg hover:bg-gray-100 ${darkMode ? 'hover:bg-gray-700' : ''}`}
              title="Export chat"
              aria-label="Export chat conversation"
            >
              <DocumentArrowDownIcon className="w-5 h-5 text-gray-500" />
            </button>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-lg hover:bg-gray-100 ${darkMode ? 'hover:bg-gray-700' : ''}`}
              title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
              aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              {darkMode ? <SunIcon className="w-5 h-5 text-gray-500" /> : <MoonIcon className="w-5 h-5 text-gray-500" />}
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-2 rounded-lg hover:bg-gray-100 ${darkMode ? 'hover:bg-gray-700' : ''}`}
              title="Settings"
              aria-label="Open settings"
            >
              <Cog6ToothIcon className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className={`p-4 border-b ${darkMode ? 'border-gray-700 bg-gray-800' : 'border-gray-200 bg-gray-50'}`}>
            <div className="max-w-4xl mx-auto">
              <h3 className={`text-sm font-medium mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Model Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className={`block text-xs font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className={`w-full px-3 py-2 rounded-lg border text-sm ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  >
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro (Stock Expert)</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude-3">Claude 3</option>
                  </select>
                </div>
                <div>
                  <label className={`block text-xs font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Temperature: {temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className={`block text-xs font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Max Tokens: {maxTokens}
                  </label>
                  <input
                    type="range"
                    min="512"
                    max="4096"
                    step="512"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full flex items-center justify-center mb-6">
                <SparklesIcon className="w-10 h-10 text-blue-600" />
              </div>
              <h2 className={`text-2xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                Welcome to StockBroker AI Assistant
              </h2>
              <p className={`text-gray-500 mb-8 max-w-2xl ${darkMode ? 'text-gray-400' : ''}`}>
                I'm your intelligent trading companion. I can help you with stock analysis, predictions, 
                trading strategies, portfolio management, and market insights. Ask me anything about the stock market!
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl">
                {[
                  { icon: ChartBarIcon, text: "What's the price of AAPL?", color: "blue" },
                  { icon: ArrowUpIcon, text: "Predict TSLA direction for tomorrow", color: "green" },
                  { icon: CurrencyDollarIcon, text: "Day trading strategy for MSFT", color: "purple" },
                  { icon: DocumentTextIcon, text: "Market analysis for tech stocks", color: "orange" }
                ].map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => setInputMessage(suggestion.text)}
                    className={`p-4 text-left rounded-xl border transition-all hover:scale-105 ${
                      darkMode 
                        ? 'border-gray-700 hover:bg-gray-700 text-gray-300' 
                        : 'border-gray-200 hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 bg-${suggestion.color}-100 rounded-lg flex items-center justify-center`}>
                        <suggestion.icon className={`w-4 h-4 text-${suggestion.color}-600`} />
                      </div>
                      <span className="text-sm font-medium">{suggestion.text}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onCopy={copyMessage}
              onRegenerate={regenerateResponse}
              onPin={() => {}}
              isDarkMode={darkMode}
              showTimestamp={true}
            />
          ))}

          {/* Streaming message */}
          {streamingMessage && (
            <ChatMessage
              message={{
                id: 'streaming',
                type: 'assistant',
                content: streamingMessage,
                timestamp: new Date()
              }}
              isDarkMode={darkMode}
              showTimestamp={false}
            />
          )}

          {/* Loading indicator */}
          {isLoading && !streamingMessage && (
            <div className="flex justify-start">
              <div className="max-w-4xl mr-12">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <SparklesIcon className="w-4 h-4 text-white" />
                  </div>
                  <div className={`p-4 rounded-2xl ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        AI is thinking...
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <ChatInput
          value={inputMessage}
          onChange={setInputMessage}
          onSend={() => handleSendMessage()}
          onStop={stopGeneration}
          isLoading={isLoading}
          isDarkMode={darkMode}
          placeholder="Ask about stock prices, predictions, trading strategies, or market analysis..."
        />
      </div>

      {/* Export Modal */}
      <ExportChat
        messages={messages}
        chatTitle={chatHistory.find(chat => chat.id === currentChatId)?.title || 'New Chat'}
        isOpen={showExport}
        onClose={() => setShowExport(false)}
        isDarkMode={darkMode}
      />
    </div>
  );
};

export default AIAssistant;
