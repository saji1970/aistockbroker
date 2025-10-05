import React, { useState } from 'react';
import { 
  UserIcon, 
  SparklesIcon, 
  ExclamationTriangleIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  ArrowPathIcon,
  BookmarkIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { toast } from 'react-hot-toast';

const ChatMessage = ({ 
  message, 
  onCopy, 
  onRegenerate, 
  onPin,
  isDarkMode = false,
  showTimestamp = true 
}) => {
  const [copied, setCopied] = useState(false);
  const [isPinned, setIsPinned] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      toast.success('Message copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
      if (onCopy) onCopy(message.id);
    } catch (error) {
      toast.error('Failed to copy message');
    }
  };

  const handlePin = () => {
    setIsPinned(!isPinned);
    if (onPin) onPin(message.id, !isPinned);
    toast.success(isPinned ? 'Message unpinned' : 'Message pinned');
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    }
  };

  const getMarketSession = () => {
    const now = new Date();
    const estTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
    const hour = estTime.getHours();
    const minute = estTime.getMinutes();
    const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    
    // Market hours: 9:30 AM - 4:00 PM EST
    if (hour >= 9 && (hour < 16 || (hour === 16 && minute === 0))) {
      return `Market Open – ${timeStr} EST`;
    } else {
      return `Market Closed – ${timeStr} EST`;
    }
  };

  const isUser = message.type === 'user';
  const isError = message.isError;

  // Custom code block renderer for financial data
  const CodeBlock = ({ node, inline, className, children, ...props }) => {
    const match = /language-(\w+)/.exec(className || '');
    const language = match ? match[1] : '';

    if (!inline && language) {
      return (
        <SyntaxHighlighter
          style={isDarkMode ? tomorrow : undefined}
          language={language}
          PreTag="div"
          className="rounded-lg !mt-2 !mb-2"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      );
    }

    return (
      <code className={`px-1.5 py-0.5 rounded text-sm font-mono ${
        isDarkMode ? 'bg-gray-700 text-gray-200' : 'bg-gray-100 text-gray-800'
      }`} {...props}>
        {children}
      </code>
    );
  };

  // Custom table renderer for financial data
  const Table = ({ children }) => (
    <div className="overflow-x-auto my-4">
      <table className={`min-w-full border-collapse border ${
        isDarkMode ? 'border-gray-600' : 'border-gray-300'
      }`}>
        {children}
      </table>
    </div>
  );

  const TableHead = ({ children }) => (
    <thead className={isDarkMode ? 'bg-gray-800' : 'bg-gray-50'}>
      {children}
    </thead>
  );

  const TableRow = ({ children }) => (
    <tr className={`border-b ${isDarkMode ? 'border-gray-600 hover:bg-gray-800' : 'border-gray-200 hover:bg-gray-50'}`}>
      {children}
    </tr>
  );

  const TableCell = ({ children, ...props }) => (
    <td className={`px-3 py-2 text-sm ${isDarkMode ? 'text-gray-200' : 'text-gray-900'}`} {...props}>
      {children}
    </td>
  );

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : ''} max-w-4xl w-full`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser 
              ? 'bg-blue-500' 
              : isError 
                ? 'bg-red-500'
                : 'bg-gradient-to-r from-blue-500 to-purple-600'
          }`}>
            {isUser ? (
              <UserIcon className="w-4 h-4 text-white" />
            ) : isError ? (
              <ExclamationTriangleIcon className="w-4 h-4 text-white" />
            ) : (
              <SparklesIcon className="w-4 h-4 text-white" />
            )}
          </div>
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {/* Header with timestamp and market session */}
          {!isUser && showTimestamp && (
            <div className="flex items-center space-x-2 mb-1">
              <span className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                {formatTimestamp(message.timestamp)}
              </span>
              <span className={`text-xs px-2 py-1 rounded-full ${
                isDarkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-600'
              }`}>
                {getMarketSession()}
              </span>
            </div>
          )}

          {/* Message Bubble */}
          <div className={`inline-block max-w-full px-4 py-3 rounded-2xl shadow-sm ${
            isUser
              ? isDarkMode 
                ? 'bg-blue-600 text-white' 
                : 'bg-blue-500 text-white'
              : isError
                ? isDarkMode 
                  ? 'bg-red-900/20 border border-red-500/20 text-red-400' 
                  : 'bg-red-50 border border-red-200 text-red-800'
                : isDarkMode 
                  ? 'bg-gray-800 text-gray-100' 
                  : 'bg-white text-gray-900 border border-gray-200'
          }`}>
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown
                components={{
                  code: CodeBlock,
                  pre: ({ children }) => children,
                  table: Table,
                  thead: TableHead,
                  tr: TableRow,
                  td: TableCell,
                  th: TableCell
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>

          {/* Message Actions */}
          {!isUser && !isError && (
            <div className={`flex items-center space-x-1 mt-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
              <button
                onClick={handleCopy}
                className={`p-1.5 rounded-lg transition-colors ${
                  isDarkMode 
                    ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200' 
                    : 'hover:bg-gray-100 text-gray-400 hover:text-gray-600'
                }`}
                title="Copy message"
                aria-label="Copy message to clipboard"
              >
                {copied ? (
                  <CheckIcon className="w-3 h-3 text-green-500" />
                ) : (
                  <ClipboardDocumentIcon className="w-3 h-3" />
                )}
              </button>
              
              <button
                onClick={() => onRegenerate && onRegenerate(message.id)}
                className={`p-1.5 rounded-lg transition-colors ${
                  isDarkMode 
                    ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200' 
                    : 'hover:bg-gray-100 text-gray-400 hover:text-gray-600'
                }`}
                title="Regenerate response"
                aria-label="Regenerate AI response"
              >
                <ArrowPathIcon className="w-3 h-3" />
              </button>

              <button
                onClick={handlePin}
                className={`p-1.5 rounded-lg transition-colors ${
                  isPinned 
                    ? 'text-yellow-500' 
                    : isDarkMode 
                      ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200' 
                      : 'hover:bg-gray-100 text-gray-400 hover:text-gray-600'
                }`}
                title={isPinned ? "Unpin message" : "Pin message"}
                aria-label={isPinned ? "Unpin message" : "Pin message for quick reference"}
              >
                <BookmarkIcon className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
