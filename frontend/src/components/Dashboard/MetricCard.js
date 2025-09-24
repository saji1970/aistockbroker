import React, { useState } from 'react';
import { ArrowUpIcon, ArrowDownIcon, MinusIcon, SparklesIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/solid';

const MetricCard = ({ title, value, change, changePercent, type = 'default', confidence, icon, subtitle }) => {
  const [isHovered, setIsHovered] = useState(false);

  const getChangeIcon = () => {
    if (!change && !changePercent) return null;

    if (type === 'confidence') {
      if (confidence >= 80) return <ArrowUpIcon className="w-4 h-4 text-success-500" />;
      if (confidence >= 60) return <MinusIcon className="w-4 h-4 text-warning-500" />;
      return <ArrowDownIcon className="w-4 h-4 text-danger-500" />;
    }

    const isPositive = (change && change > 0) || (changePercent && changePercent > 0);
    const isNegative = (change && change < 0) || (changePercent && changePercent < 0);

    if (isPositive) return <ArrowTrendingUpIcon className="w-4 h-4 text-success-500" />;
    if (isNegative) return <ArrowDownIcon className="w-4 h-4 text-danger-500" />;
    return <MinusIcon className="w-4 h-4 text-gray-500" />;
  };

  const getChangeColor = () => {
    if (type === 'confidence') {
      if (confidence >= 80) return 'text-success-600';
      if (confidence >= 60) return 'text-warning-600';
      return 'text-danger-600';
    }

    const isPositive = (change && change > 0) || (changePercent && changePercent > 0);
    const isNegative = (change && change < 0) || (changePercent && changePercent < 0);

    if (isPositive) return 'text-success-600';
    if (isNegative) return 'text-danger-600';
    return 'text-gray-600';
  };

  const getConfidenceColor = () => {
    if (confidence >= 80) return 'status-positive';
    if (confidence >= 60) return 'status-neutral bg-warning-50 text-warning-700';
    return 'status-negative';
  };

  const getConfidenceBarColor = () => {
    if (confidence >= 80) return 'bg-gradient-to-r from-success-400 to-success-600';
    if (confidence >= 60) return 'bg-gradient-to-r from-warning-400 to-warning-600';
    return 'bg-gradient-to-r from-danger-400 to-danger-600';
  };

  const getCardStyle = () => {
    if (type === 'primary') return 'metric-card-glow hover:shadow-neon';
    if (type === 'confidence') return 'metric-card';
    return 'metric-card';
  };

  return (
    <div
      className={`${getCardStyle()} animate-fade-in group cursor-pointer`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Background Glow Effect */}
      {type === 'primary' && (
        <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-400 to-secondary-500 rounded-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-300 animate-pulse-glow"></div>
      )}

      <div className="relative">
        {/* Header with Icon */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {icon && (
                <div className={`p-2 rounded-xl ${
                  type === 'primary' ? 'bg-primary-100' :
                  type === 'confidence' ? 'bg-purple-100' :
                  'bg-gray-100'
                }`}>
                  <div className={`w-5 h-5 ${
                    type === 'primary' ? 'text-primary-600' :
                    type === 'confidence' ? 'text-purple-600' :
                    'text-gray-600'
                  }`}>
                    {icon}
                  </div>
                </div>
              )}
              <h3 className="text-sm font-semibold text-gray-700 group-hover:text-gray-900 transition-colors duration-200">
                {title}
              </h3>
              {type === 'primary' && (
                <SparklesIcon className="w-4 h-4 text-primary-500 animate-pulse" />
              )}
            </div>
            {subtitle && (
              <p className="text-xs text-gray-500 mb-2">{subtitle}</p>
            )}
          </div>

          {/* Confidence Badge */}
          {type === 'confidence' && confidence !== undefined && (
            <div className="flex flex-col items-end space-y-2">
              <span className={`px-3 py-1 rounded-xl text-xs font-semibold ${getConfidenceColor()}`}>
                {confidence >= 80 ? 'High Confidence' : confidence >= 60 ? 'Medium' : 'Low'}
              </span>
            </div>
          )}
        </div>

        {/* Main Value */}
        <div className="mb-4">
          <p className={`text-3xl font-bold transition-all duration-200 ${
            type === 'primary' ? 'text-gradient group-hover:scale-105' :
            isHovered ? 'text-gray-900 scale-105' : 'text-gray-800'
          }`}>
            {value}
          </p>
        </div>

        {/* Confidence Progress Bar */}
        {type === 'confidence' && confidence !== undefined && (
          <div className="mb-4">
            <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
              <span>Confidence Level</span>
              <span className="font-semibold">{confidence}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ease-out ${getConfidenceBarColor()}`}
                style={{
                  width: `${confidence}%`,
                  transform: isHovered ? 'scaleY(1.2)' : 'scaleY(1)'
                }}
              ></div>
            </div>
          </div>
        )}

        {/* Change Indicator */}
        {(change || changePercent) && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`p-1.5 rounded-lg ${
                getChangeColor().includes('success') ? 'bg-success-50' :
                getChangeColor().includes('danger') ? 'bg-danger-50' :
                'bg-gray-50'
              }`}>
                {getChangeIcon()}
              </div>
              <span className={`text-sm font-semibold ${getChangeColor()}`}>
                {type === 'confidence' ? (
                  `${confidence}% confidence`
                ) : (
                  <>
                    {change && `${change > 0 ? '+' : ''}${change}`}
                    {changePercent && ` (${changePercent > 0 ? '+' : ''}${changePercent}%)`}
                  </>
                )}
              </span>
            </div>

            {/* Trend Visualization */}
            <div className="flex space-x-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className={`w-1 rounded-full transition-all duration-300 ${
                    getChangeColor().includes('success') ? 'bg-success-400' :
                    getChangeColor().includes('danger') ? 'bg-danger-400' :
                    'bg-gray-300'
                  }`}
                  style={{
                    height: `${8 + Math.random() * 12}px`,
                    animationDelay: `${i * 100}ms`
                  }}
                ></div>
              ))}
            </div>
          </div>
        )}

        {/* Hover Effects */}
        {isHovered && (
          <div className="absolute top-0 right-0 -mr-2 -mt-2">
            <div className="w-3 h-3 bg-primary-500 rounded-full animate-ping"></div>
            <div className="absolute top-0 w-3 h-3 bg-primary-500 rounded-full"></div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard; 