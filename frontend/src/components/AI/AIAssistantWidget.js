import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, ChatBubbleLeftRightIcon, XMarkIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import { marketMateAPI } from '../../services/api';
import LoadingSpinner from '../UI/LoadingSpinner';

// Add error boundary for debugging
const AIAssistantWidget = ({ isExpanded = false, onToggle }) => {
  console.log('AIAssistantWidget rendering...');
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: `👋 Hi! I'm your AI trading assistant. I can help you with:

📈 **Stock Analysis**: "What's the price of AAPL?"
🔮 **Predictions**: "Predict TSLA direction for tomorrow"
📊 **Market Insights**: "Show me top 10 tech stocks"
💼 **Investment Advice**: "What should I invest in?"

Just ask me anything about stocks in a natural way!`,
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(isExpanded);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      // Use our backend chat API
      let response;
      try {
        console.log('Sending query to backend chat API:', inputMessage);
        const backendResponse = await api.post('/api/chat/query', {
          query: inputMessage
        });

        if (backendResponse.data && backendResponse.data.response) {
          response = backendResponse.data.response;
        } else {
          throw new Error('Backend chat API returned empty response');
        }
      } catch (chatAPIError) {
        console.log('Backend chat API failed, using fallback response:', chatAPIError.message);

        // Fallback response based on common queries
        const lowerMessage = inputMessage.toLowerCase();

        if (lowerMessage.includes('price') || lowerMessage.includes('stock')) {
          response = `I'd be happy to help you with stock prices! Please provide a specific stock symbol (like AAPL, MSFT, GOOGL) and I'll get you the current price and analysis.`;
        } else if (lowerMessage.includes('predict') || lowerMessage.includes('forecast')) {
          response = `I can provide stock predictions! Please include a stock symbol and timeframe (like "predict AAPL for tomorrow" or "TSLA next week") and I'll give you a detailed analysis.`;
        } else if (lowerMessage.includes('invest') || lowerMessage.includes('recommend')) {
          response = `I can help with investment recommendations! Please let me know your risk tolerance (conservative, moderate, or aggressive) and investment amount, and I'll suggest suitable stocks and strategies.`;
        } else if (lowerMessage.includes('market') || lowerMessage.includes('analysis')) {
          response = `I can provide market analysis! I can show you top performers, market trends, sector analysis, and more. What specific market information are you looking for?`;
        } else {
          response = `I understand you're asking about "${inputMessage}". I can help with:

📈 **Stock Prices**: "What's the price of AAPL?"
🔮 **Predictions**: "Predict TSLA for tomorrow"
📊 **Market Data**: "Show me top 10 tech stocks"
💼 **Investment Advice**: "What should I invest in?"

Please be more specific with a stock symbol or investment question!`;
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
        content: `I encountered an error while processing your request. Please try again or rephrase your question.

**I can help with:**
- Stock prices and analysis
- Market predictions and forecasts
- Investment recommendations
- Portfolio analysis

**Example queries:**
- "What's the price of AAPL?"
- "Predict TSLA for tomorrow"
- "Show me top tech stocks"
- "What should I invest in?"

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

  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (onToggle) onToggle(!isOpen);
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Toggle Button */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
          title="Open AI Assistant"
        >
          <ChatBubbleLeftRightIcon className="h-6 w-6" />
        </button>
      )}

      {/* Chat Widget */}
      {isOpen && (
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 w-80 h-96 flex flex-col">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                <ChatBubbleLeftRightIcon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold text-sm">AI Trading Assistant</h3>
                <p className="text-xs text-blue-100">Ask me anything about stocks</p>
              </div>
            </div>
            <button
              onClick={toggleChat}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] px-3 py-2 rounded-lg text-sm ${
                  message.type === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                  <p className={`text-xs mt-1 ${
                    message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 px-3 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <LoadingSpinner size="sm" />
                    <span className="text-xs">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-2">
              <div className="flex-1">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about stocks..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isLoading}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <PaperAirplaneIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAssistantWidget;
