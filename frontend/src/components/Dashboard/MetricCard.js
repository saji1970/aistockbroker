import React from 'react';
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from '@heroicons/react/24/solid';

const MetricCard = ({ title, value, change, changePercent, type = 'default', confidence }) => {
  const getChangeIcon = () => {
    if (!change && !changePercent) return null;
    
    if (type === 'confidence') {
      if (confidence >= 80) return <ArrowUpIcon className="w-4 h-4 text-green-500" />;
      if (confidence >= 60) return <MinusIcon className="w-4 h-4 text-yellow-500" />;
      return <ArrowDownIcon className="w-4 h-4 text-red-500" />;
    }
    
    const isPositive = (change && change > 0) || (changePercent && changePercent > 0);
    const isNegative = (change && change < 0) || (changePercent && changePercent < 0);
    
    if (isPositive) return <ArrowUpIcon className="w-4 h-4 text-green-500" />;
    if (isNegative) return <ArrowDownIcon className="w-4 h-4 text-red-500" />;
    return <MinusIcon className="w-4 h-4 text-gray-500" />;
  };

  const getChangeColor = () => {
    if (type === 'confidence') {
      if (confidence >= 80) return 'text-green-600';
      if (confidence >= 60) return 'text-yellow-600';
      return 'text-red-600';
    }
    
    const isPositive = (change && change > 0) || (changePercent && changePercent > 0);
    const isNegative = (change && change < 0) || (changePercent && changePercent < 0);
    
    if (isPositive) return 'text-green-600';
    if (isNegative) return 'text-red-600';
    return 'text-gray-600';
  };

  const getConfidenceColor = () => {
    if (confidence >= 80) return 'bg-green-100 text-green-800';
    if (confidence >= 60) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getConfidenceBarColor = () => {
    if (confidence >= 80) return 'bg-green-500';
    if (confidence >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        {type === 'confidence' && confidence !== undefined && (
          <div className="flex flex-col items-end space-y-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor()}`}>
              {confidence >= 80 ? 'High' : confidence >= 60 ? 'Medium' : 'Low'}
            </span>
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${getConfidenceBarColor()}`}
                style={{ width: `${confidence}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>
      
      {(change || changePercent) && (
        <div className="mt-4 flex items-center space-x-2">
          {getChangeIcon()}
          <span className={`text-sm font-medium ${getChangeColor()}`}>
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
      )}
    </div>
  );
};

export default MetricCard; 