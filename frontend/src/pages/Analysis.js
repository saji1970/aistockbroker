import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { stockAPI } from '../services/api';
import { useStore } from '../store/store';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  InformationCircleIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  FireIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import toast from 'react-hot-toast';
import TechnicalChart from '../components/Charts/TechnicalChart';
import MultiIndicatorChart from '../components/Charts/MultiIndicatorChart';
import CandlestickChart from '../components/Charts/CandlestickChart';

const Analysis = () => {
  const { currentMarket } = useStore();
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [selectedPeriod, setSelectedPeriod] = useState('1y');
  const [selectedInterval, setSelectedInterval] = useState('1d');
  const [selectedIndicator, setSelectedIndicator] = useState('price');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [chartViewMode, setChartViewMode] = useState('single'); // 'single' or 'comprehensive'

  // Get market-specific instruments
  const getMarketInstruments = () => {
    const marketSymbols = stockAPI.getMarketSymbols(currentMarket);
    const marketInfo = stockAPI.getMarketInfo(currentMarket);
    
    return {
      stocks: marketSymbols.slice(0, 8).map(symbol => ({
        symbol: symbol.replace(marketInfo.suffix, ''),
        name: `${symbol.replace(marketInfo.suffix, '')} Inc.`,
        type: 'stock'
      })),
      etfs: [
        { symbol: 'SPY', name: 'SPDR S&P 500 ETF', type: 'etf' },
        { symbol: 'QQQ', name: 'Invesco QQQ Trust', type: 'etf' },
        { symbol: 'VTI', name: 'Vanguard Total Stock Market ETF', type: 'etf' },
        { symbol: 'VOO', name: 'Vanguard S&P 500 ETF', type: 'etf' },
      ],
      crypto: [
        { symbol: 'BTC-USD', name: 'Bitcoin', type: 'crypto' },
        { symbol: 'ETH-USD', name: 'Ethereum', type: 'crypto' },
        { symbol: 'ADA-USD', name: 'Cardano', type: 'crypto' },
        { symbol: 'DOT-USD', name: 'Polkadot', type: 'crypto' },
      ],
      indices: [
        { symbol: '^GSPC', name: 'S&P 500', type: 'index' },
        { symbol: '^DJI', name: 'Dow Jones Industrial Average', type: 'index' },
        { symbol: '^IXIC', name: 'NASDAQ Composite', type: 'index' },
        { symbol: '^VIX', name: 'CBOE Volatility Index', type: 'index' },
      ]
    };
  };

  const popularInstruments = getMarketInstruments();

  const timeframes = [
    { value: '1d', label: '1 Day', interval: '1m' },
    { value: '5d', label: '5 Days', interval: '5m' },
    { value: '1mo', label: '1 Month', interval: '1h' },
    { value: '3mo', label: '3 Months', interval: '1d' },
    { value: '6mo', label: '6 Months', interval: '1d' },
    { value: '1y', label: '1 Year', interval: '1d' },
    { value: '2y', label: '2 Years', interval: '1d' },
    { value: '5y', label: '5 Years', interval: '1d' },
    { value: 'max', label: 'Max', interval: '1d' },
  ];

  const indicators = [
    { id: 'price', name: 'Price Chart', description: 'Candlestick and volume', icon: ChartBarIcon },
    { id: 'sma', name: 'Moving Averages', description: 'SMA, EMA, WMA, HMA', icon: ArrowTrendingUpIcon },
    { id: 'rsi', name: 'RSI', description: 'Relative Strength Index', icon: ArrowTrendingDownIcon },
    { id: 'macd', name: 'MACD', description: 'Moving Average Convergence Divergence', icon: ChartBarIcon },
    { id: 'bollinger', name: 'Bollinger Bands', description: 'Price volatility bands', icon: InformationCircleIcon },
    { id: 'volume', name: 'Volume', description: 'Trading volume analysis', icon: ChartBarIcon },
    { id: 'stochastic', name: 'Stochastic', description: 'Stochastic Oscillator', icon: ArrowTrendingUpIcon },
    { id: 'williams', name: 'Williams %R', description: 'Williams %R indicator', icon: ArrowTrendingDownIcon },
    { id: 'cci', name: 'CCI', description: 'Commodity Channel Index', icon: InformationCircleIcon },
    { id: 'roc', name: 'ROC', description: 'Rate of Change', icon: ArrowTrendingUpIcon },
    { id: 'atr', name: 'ATR', description: 'Average True Range', icon: InformationCircleIcon },
    { id: 'obv', name: 'OBV', description: 'On-Balance Volume', icon: ChartBarIcon },
  ];

  // Fetch stock data
  const { data: stockData, isLoading: stockLoading, error: stockError } = useQuery(
    ['stockData', selectedSymbol, selectedPeriod, selectedInterval, currentMarket],
    () => stockAPI.getStockData(selectedSymbol, selectedPeriod, selectedInterval, currentMarket),
    {
      enabled: !!selectedSymbol,
      retry: 2,
      onError: (error) => {
        toast.error(`Failed to fetch data for ${selectedSymbol}`);
      }
    }
  );

  // Fetch technical indicators
  const { data: technicalData, isLoading: technicalLoading, error: technicalError } = useQuery(
    ['technical', selectedSymbol, selectedPeriod, currentMarket],
    () => stockAPI.getTechnicalIndicators(selectedSymbol, selectedPeriod, currentMarket),
    {
      enabled: !!selectedSymbol,
      retry: 2,
      onError: (error) => {
        toast.error(`Failed to fetch technical indicators for ${selectedSymbol}`);
      }
    }
  );

  // Fetch stock info
  const { data: stockInfo, isLoading: infoLoading } = useQuery(
    ['stockInfo', selectedSymbol, currentMarket],
    () => stockAPI.getStockInfo(selectedSymbol, currentMarket),
    {
      enabled: !!selectedSymbol,
      retry: 2,
    }
  );

  // Handle timeframe change
  const handleTimeframeChange = (timeframe) => {
    setSelectedPeriod(timeframe.value);
    setSelectedInterval(timeframe.interval);
  };

  // Handle instrument selection
  const handleInstrumentSelect = (instrument) => {
    setSelectedSymbol(instrument.symbol);
    setShowSearchResults(false);
    setSearchQuery('');
  };

  // Search functionality
  const handleSearch = (query) => {
    setSearchQuery(query);
    setShowSearchResults(query.length > 0);
  };

  const getSearchResults = () => {
    if (!searchQuery) return [];
    
    const query = searchQuery.toUpperCase();
    const results = [];
    
    Object.values(popularInstruments).flat().forEach(instrument => {
      if (instrument.symbol.includes(query) || instrument.name.toUpperCase().includes(query)) {
        results.push(instrument);
      }
    });
    
    return results.slice(0, 10);
  };

  const getInstrumentTypeIcon = (type) => {
    switch (type) {
      case 'stock': return BuildingOfficeIcon;
      case 'etf': return CurrencyDollarIcon;
      case 'crypto': return FireIcon;
      case 'index': return GlobeAltIcon;
      default: return BuildingOfficeIcon;
    }
  };

  const getInstrumentTypeColor = (type) => {
    switch (type) {
      case 'stock': return 'text-blue-600 bg-blue-50';
      case 'etf': return 'text-green-600 bg-green-50';
      case 'crypto': return 'text-orange-600 bg-orange-50';
      case 'index': return 'text-purple-600 bg-purple-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (stockLoading || technicalLoading || infoLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Technical Analysis</h1>
            <p className="mt-1 text-sm text-gray-500">
              Advanced technical indicators and chart analysis for trading instruments
            </p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <GlobeAltIcon className="w-4 h-4" />
            <span>{stockAPI.getMarketInfo(currentMarket).name}</span>
            <span>({stockAPI.getMarketInfo(currentMarket).currency})</span>
          </div>
        </div>
      </div>

      {/* Instrument Selection */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Select Instrument</h2>
          <div className="relative">
            <div className="flex items-center space-x-2">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search symbols..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="input-field w-64"
              />
            </div>
            
            {/* Search Results Dropdown */}
            {showSearchResults && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
                {getSearchResults().map((instrument) => {
                  const IconComponent = getInstrumentTypeIcon(instrument.type);
                  return (
                    <button
                      key={instrument.symbol}
                      onClick={() => handleInstrumentSelect(instrument)}
                      className="w-full p-3 text-left hover:bg-gray-50 flex items-center space-x-3"
                    >
                      <IconComponent className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="font-medium text-gray-900">{instrument.symbol}</p>
                        <p className="text-sm text-gray-500">{instrument.name}</p>
                      </div>
                      <span className={`ml-auto px-2 py-1 text-xs rounded-full ${getInstrumentTypeColor(instrument.type)}`}>
                        {instrument.type.toUpperCase()}
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Popular Instruments */}
        <div className="space-y-4">
          {Object.entries(popularInstruments).map(([category, instruments]) => (
            <div key={category}>
              <h3 className="text-sm font-medium text-gray-700 mb-2 capitalize">{category}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
                {instruments.map((instrument) => {
                  const IconComponent = getInstrumentTypeIcon(instrument.type);
                  const isSelected = selectedSymbol === instrument.symbol;
                  return (
                    <button
                      key={instrument.symbol}
                      onClick={() => handleInstrumentSelect(instrument)}
                      className={`p-2 rounded-lg border text-left transition-colors ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50 text-primary-700'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-2">
                        <IconComponent className="h-4 w-4" />
                        <div>
                          <p className="text-sm font-medium">{instrument.symbol}</p>
                          <p className="text-xs text-gray-500 truncate">{instrument.name}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Timeframe Selection */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Timeframe</h2>
          <div className="flex items-center space-x-2">
            <ClockIcon className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-500">Select time period</span>
          </div>
        </div>

        <div className="grid grid-cols-3 md:grid-cols-9 gap-2">
          {timeframes.map((timeframe) => (
            <button
              key={timeframe.value}
              onClick={() => handleTimeframeChange(timeframe)}
              className={`p-2 rounded-lg border text-center transition-colors ${
                selectedPeriod === timeframe.value
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <p className="text-sm font-medium">{timeframe.label}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Current Instrument Info */}
      {stockInfo && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="metric-card">
            <p className="text-sm font-medium text-gray-600">Current Price</p>
            <p className="text-2xl font-bold text-gray-900">
              ${stockInfo.current_price?.toFixed(2) || 'N/A'}
            </p>
          </div>
          <div className="metric-card">
            <p className="text-sm font-medium text-gray-600">Change</p>
            <p className={`text-2xl font-bold ${
              (stockInfo.price_change || 0) > 0 ? 'text-success-600' : 'text-danger-600'
            }`}>
              {stockInfo.price_change > 0 ? '+' : ''}
              ${stockInfo.price_change?.toFixed(2) || '0.00'}
              ({stockInfo.price_change_percent?.toFixed(2) || '0.00'}%)
            </p>
          </div>
          <div className="metric-card">
            <p className="text-sm font-medium text-gray-600">Volume</p>
            <p className="text-2xl font-bold text-gray-900">
              {stockInfo.volume?.toLocaleString() || 'N/A'}
            </p>
          </div>
          <div className="metric-card">
            <p className="text-sm font-medium text-gray-600">Market Cap</p>
            <p className="text-2xl font-bold text-gray-900">
              ${stockInfo.market_cap?.toLocaleString() || 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Indicator Selection */}
      {chartViewMode === 'single' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Technical Indicators</h2>
            <div className="flex items-center space-x-2">
              <InformationCircleIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-500">Select an indicator to view</span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3">
            {indicators.map((indicator) => {
              const IconComponent = indicator.icon;
              return (
                <button
                  key={indicator.id}
                  onClick={() => setSelectedIndicator(indicator.id)}
                  className={`p-3 rounded-lg border text-left transition-colors ${
                    selectedIndicator === indicator.id
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <IconComponent className="h-4 w-4" />
                    <p className="text-sm font-medium">{indicator.name}</p>
                  </div>
                  <p className="text-xs text-gray-500">{indicator.description}</p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Chart Area */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {chartViewMode === 'comprehensive' ? 'Comprehensive Analysis' : indicators.find(i => i.id === selectedIndicator)?.name} - {selectedSymbol}
          </h2>
          <div className="flex items-center space-x-4">
            {/* View Mode Toggle */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setChartViewMode('single')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  chartViewMode === 'single'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Single Indicator
              </button>
              <button
                onClick={() => setChartViewMode('comprehensive')}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  chartViewMode === 'comprehensive'
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Comprehensive
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-500">{timeframes.find(t => t.value === selectedPeriod)?.label}</span>
            </div>
          </div>
        </div>

        {stockLoading ? (
          <div className="h-96 bg-gray-50 rounded-lg flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : stockError ? (
          <div className="h-96 bg-red-50 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <p className="text-red-500">Failed to load chart data</p>
              <p className="text-sm text-red-400 mt-2">Please try again later</p>
            </div>
          </div>
        ) : chartViewMode === 'comprehensive' ? (
          <MultiIndicatorChart
            data={stockData?.data || []}
            symbol={selectedSymbol}
            period={timeframes.find(t => t.value === selectedPeriod)?.label || selectedPeriod}
          />
        ) : (
          <TechnicalChart
            data={stockData?.data || []}
            indicator={selectedIndicator}
            symbol={selectedSymbol}
            period={timeframes.find(t => t.value === selectedPeriod)?.label || selectedPeriod}
          />
        )}
      </div>

      {/* Technical Analysis Summary */}
      {technicalData && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Analysis Summary</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">RSI Analysis</h3>
              <p className={`text-sm font-medium ${
                technicalData.latest_data?.RSI > 70 ? 'text-danger-600' : 
                technicalData.latest_data?.RSI < 30 ? 'text-success-600' : 'text-gray-600'
              }`}>
                {technicalData.latest_data?.RSI > 70 ? 'Overbought' : 
                 technicalData.latest_data?.RSI < 30 ? 'Oversold' : 'Neutral'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                RSI: {technicalData.latest_data?.RSI?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">MACD Signal</h3>
              <p className={`text-sm font-medium ${
                technicalData.latest_data?.MACD > technicalData.latest_data?.MACD_Signal ? 'text-success-600' : 'text-danger-600'
              }`}>
                {technicalData.latest_data?.MACD > technicalData.latest_data?.MACD_Signal ? 'Bullish' : 'Bearish'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                MACD: {technicalData.latest_data?.MACD?.toFixed(4) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Moving Averages</h3>
              <p className={`text-sm font-medium ${
                technicalData.latest_data?.SMA_20 > technicalData.latest_data?.SMA_50 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {technicalData.latest_data?.SMA_20 > technicalData.latest_data?.SMA_50 ? 'Bullish' : 'Bearish'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                SMA 20: {technicalData.latest_data?.SMA_20?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Bollinger Bands</h3>
              <p className={`text-sm font-medium ${
                technicalData.latest_data?.BB_Position > 0.8 ? 'text-danger-600' :
                technicalData.latest_data?.BB_Position < 0.2 ? 'text-success-600' : 'text-gray-600'
              }`}>
                {technicalData.latest_data?.BB_Position > 0.8 ? 'Upper Band' :
                 technicalData.latest_data?.BB_Position < 0.2 ? 'Lower Band' : 'Middle Range'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Position: {technicalData.latest_data?.BB_Position?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Stochastic</h3>
              <p className={`text-sm font-medium ${
                technicalData.latest_data?.Stoch_K > 80 ? 'text-danger-600' :
                technicalData.latest_data?.Stoch_K < 20 ? 'text-success-600' : 'text-gray-600'
              }`}>
                {technicalData.latest_data?.Stoch_K > 80 ? 'Overbought' :
                 technicalData.latest_data?.Stoch_K < 20 ? 'Oversold' : 'Neutral'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                %K: {technicalData.latest_data?.Stoch_K?.toFixed(2) || 'N/A'}
              </p>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Volume Analysis</h3>
              <p className={`text-sm font-medium ${
                technicalData.latest_data?.OBV > 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {technicalData.latest_data?.OBV > 0 ? 'Accumulation' : 'Distribution'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                OBV: {technicalData.latest_data?.OBV?.toLocaleString() || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {(stockError || technicalError) && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center space-x-2">
            <InformationCircleIcon className="h-5 w-5 text-red-500" />
            <p className="text-red-700">
              {stockError ? `Error loading data for ${selectedSymbol}` : 
               technicalError ? `Error loading technical indicators for ${selectedSymbol}` : ''}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analysis; 