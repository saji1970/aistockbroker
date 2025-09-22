import React, { useState, useEffect, useCallback } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useStore } from '../../store/store';
import { stockAPI } from '../../services/api';

const StockSearch = () => {
  const { currentSymbol, setCurrentSymbol, currentPeriod, setCurrentPeriod, currentMarket } = useStore();
  const [searchTerm, setSearchTerm] = useState(currentSymbol || '');
  const [suggestions, setSuggestions] = useState([]);

  // Get market-specific stock symbols
  const getMarketStocks = useCallback(() => {
    const marketSymbols = stockAPI.getMarketSymbols(currentMarket);
    const marketInfo = stockAPI.getMarketInfo(currentMarket);
    
    // Create stock objects with names (you can expand this with real company names)
    return marketSymbols.map(symbol => ({
      symbol: symbol.replace(marketInfo.suffix, ''), // Remove suffix for display
      name: `${symbol.replace(marketInfo.suffix, '')} Inc.`,
      fullSymbol: symbol
    }));
  }, [currentMarket]);

  const periods = [
    { value: '1d', label: '1 Day' },
    { value: '5d', label: '5 Days' },
    { value: '1mo', label: '1 Month' },
    { value: '3mo', label: '3 Months' },
    { value: '6mo', label: '6 Months' },
    { value: '1y', label: '1 Year' },
    { value: '2y', label: '2 Years' },
    { value: '5y', label: '5 Years' },
    { value: '10y', label: '10 Years' },
    { value: 'ytd', label: 'YTD' },
    { value: 'max', label: 'Max' }
  ];

  useEffect(() => {
    if (searchTerm.length >= 1) {
      const marketStocks = getMarketStocks();
      const filtered = marketStocks.filter(stock =>
        stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 8));
    } else {
      setSuggestions([]);
    }
  }, [searchTerm, getMarketStocks]);

  const handleStockSelect = (symbol) => {
    setCurrentSymbol(symbol);
    setSearchTerm(symbol);
    setSuggestions([]);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      setCurrentSymbol(searchTerm.trim().toUpperCase());
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Stock Search</h3>
      
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={`Search for stocks (e.g., ${getMarketStocks().slice(0, 3).map(s => s.symbol).join(', ')})`}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1">
            {suggestions.map((stock) => (
              <button
                key={stock.symbol}
                type="button"
                onClick={() => handleStockSelect(stock.symbol)}
                className="w-full text-left px-4 py-2 hover:bg-gray-50 focus:bg-gray-50 focus:outline-none"
              >
                <div className="font-medium">{stock.symbol}</div>
                <div className="text-sm text-gray-500">{stock.name}</div>
              </button>
            ))}
          </div>
        )}

        {/* Period Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Period
          </label>
          <select
            value={currentPeriod}
            onChange={(e) => setCurrentPeriod(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {periods.map((period) => (
              <option key={period.value} value={period.value}>
                {period.label}
              </option>
            ))}
          </select>
        </div>

        {/* Market Info */}
        <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
          <div className="font-medium">Current Market:</div>
          <div>{stockAPI.getMarketInfo(currentMarket).name}</div>
          <div>Currency: {stockAPI.getMarketInfo(currentMarket).currency}</div>
        </div>
      </form>
    </div>
  );
};

export default StockSearch; 