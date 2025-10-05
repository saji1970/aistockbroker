import React, { useState, useRef, useEffect } from 'react';
import { 
  PaperAirplaneIcon,
  ChevronDownIcon,
  CommandLineIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  ArrowUpIcon
} from '@heroicons/react/24/outline';

const ChatInput = ({ 
  value, 
  onChange, 
  onSend, 
  isLoading = false,
  onStop,
  isDarkMode = false,
  placeholder = "Ask about stock prices, predictions, or market analysis..."
}) => {
  const [showQuickCommands, setShowQuickCommands] = useState(false);
  const textareaRef = useRef(null);

  const quickCommands = [
    {
      icon: ChartBarIcon,
      label: "Check Portfolio",
      command: "Show me my current portfolio performance and holdings",
      category: "Portfolio"
    },
    {
      icon: CurrencyDollarIcon,
      label: "Get Latest on AAPL",
      command: "What's the current price and analysis for AAPL?",
      category: "Stock Analysis"
    },
    {
      icon: DocumentTextIcon,
      label: "Market Summary",
      command: "Give me today's market summary and key movers",
      category: "Market Overview"
    },
    {
      icon: ArrowUpIcon,
      label: "Top Gainers",
      command: "Show me today's top gaining stocks",
      category: "Market Overview"
    },
    {
      icon: ChartBarIcon,
      label: "Sector Analysis",
      command: "Analyze the technology sector performance",
      category: "Sector Analysis"
    },
    {
      icon: CommandLineIcon,
      label: "Trading Strategy",
      command: "Suggest a day trading strategy for tech stocks",
      category: "Trading"
    }
  ];

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !isLoading) {
        onSend();
      }
    }
  };

  const handleQuickCommand = (command) => {
    onChange(command);
    setShowQuickCommands(false);
    textareaRef.current?.focus();
  };

  const autoResize = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  };

  useEffect(() => {
    autoResize();
  }, [value]);

  const getCurrentMarketStatus = () => {
    const now = new Date();
    const estTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
    const hour = estTime.getHours();
    const minute = estTime.getMinutes();
    
    // Market hours: 9:30 AM - 4:00 PM EST
    if (hour >= 9 && (hour < 16 || (hour === 16 && minute === 0))) {
      return { status: 'open', text: 'Market Open' };
    } else {
      return { status: 'closed', text: 'Market Closed' };
    }
  };

  const marketStatus = getCurrentMarketStatus();

  return (
    <div className={`sticky bottom-0 ${isDarkMode ? 'bg-gray-900' : 'bg-white'} border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'} p-4`}>
      {/* Market Status Bar */}
      <div className={`flex items-center justify-between mb-3 px-2`}>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${marketStatus.status === 'open' ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className={`text-xs font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {marketStatus.text}
          </span>
        </div>
        
        {/* Quick Commands Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowQuickCommands(!showQuickCommands)}
            className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              isDarkMode 
                ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <CommandLineIcon className="w-3 h-3" />
            <span>Quick Commands</span>
            <ChevronDownIcon className={`w-3 h-3 transition-transform ${showQuickCommands ? 'rotate-180' : ''}`} />
          </button>

          {showQuickCommands && (
            <div className={`absolute bottom-full right-0 mb-2 w-80 rounded-lg shadow-lg border z-10 ${
              isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
            }`}>
              <div className="p-3">
                <h3 className={`text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-900'}`}>
                  Quick Commands
                </h3>
                <div className="space-y-2">
                  {quickCommands.map((cmd, index) => {
                    const IconComponent = cmd.icon;
                    return (
                      <button
                        key={index}
                        onClick={() => handleQuickCommand(cmd.command)}
                        className={`w-full text-left p-2 rounded-lg transition-colors ${
                          isDarkMode 
                            ? 'hover:bg-gray-700 text-gray-300' 
                            : 'hover:bg-gray-50 text-gray-700'
                        }`}
                      >
                        <div className="flex items-center space-x-2">
                          <IconComponent className="w-4 h-4 text-blue-500" />
                          <div>
                            <div className="text-sm font-medium">{cmd.label}</div>
                            <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                              {cmd.category}
                            </div>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={isLoading}
          className={`w-full px-4 py-3 pr-20 rounded-2xl border resize-none transition-all ${
            isDarkMode
              ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500'
              : 'bg-gray-50 border-gray-300 text-gray-900 placeholder-gray-500 focus:border-blue-500'
          } focus:ring-2 focus:ring-blue-500/20`}
          style={{ minHeight: '52px', maxHeight: '200px' }}
          rows={1}
        />
        
        {/* Send/Stop Button */}
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
          {isLoading ? (
            <button
              onClick={onStop}
              className="w-8 h-8 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors flex items-center justify-center"
              title="Stop generation"
              aria-label="Stop AI response generation"
            >
              <div className="w-3 h-3 bg-white rounded-sm"></div>
            </button>
          ) : (
            <button
              onClick={() => value.trim() && onSend()}
              disabled={!value.trim()}
              className={`w-8 h-8 rounded-lg transition-colors flex items-center justify-center ${
                value.trim()
                  ? 'bg-blue-500 hover:bg-blue-600 text-white'
                  : isDarkMode 
                    ? 'bg-gray-700 text-gray-500' 
                    : 'bg-gray-200 text-gray-400'
              }`}
              title="Send message (Enter)"
              aria-label="Send message"
            >
              <PaperAirplaneIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      {/* Keyboard Shortcuts Help */}
      <div className={`text-xs mt-2 text-center ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
        Press <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs">Enter</kbd> to send, 
        <kbd className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded text-xs ml-1">Shift+Enter</kbd> for new line
      </div>
    </div>
  );
};

export default ChatInput;
