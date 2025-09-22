import React from 'react';
import { GlobeAltIcon } from '@heroicons/react/24/outline';
import { useStore } from '../../store/store';
import { MARKETS } from '../../services/api';

const MarketSelector = () => {
  const { currentMarket, setCurrentMarket } = useStore();

  const handleMarketChange = (market) => {
    setCurrentMarket(market);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 sm:p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-900 flex items-center">
          <GlobeAltIcon className="w-4 h-4 mr-2" />
          Market Selection
        </h3>
        <span className="text-xs text-gray-500">
          {MARKETS[currentMarket]?.currency}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(MARKETS).map(([code, market]) => (
          <button
            key={code}
            onClick={() => handleMarketChange(code)}
            className={`p-2 sm:p-3 text-xs rounded-md border transition-colors ${
              currentMarket === code
                ? 'bg-blue-50 border-blue-200 text-blue-700 font-medium'
                : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <div className="font-medium text-xs sm:text-sm">{market.name}</div>
            <div className="text-gray-500 text-xs">{market.currency}</div>
          </button>
        ))}
      </div>
      
      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-600">
          <div className="font-medium">Current Market:</div>
          <div className="text-sm">{MARKETS[currentMarket]?.name}</div>
          <div className="text-gray-500 text-xs">
            Exchanges: {MARKETS[currentMarket]?.exchanges.join(', ')}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketSelector; 