import React from 'react';
import { useQuery } from 'react-query';
import { 
  ChartBarIcon, 
  ArrowUpIcon, 
  ArrowDownIcon, 
  CurrencyDollarIcon,
  EyeIcon,
  ClockIcon,
  CpuChipIcon,
  BoltIcon
} from '@heroicons/react/24/outline';
import { stockAPI, predictionAPI } from '../services/api';
import { useStore } from '../store/store';
import MetricCard from '../components/Dashboard/MetricCard';
import QuickActions from '../components/Dashboard/QuickActions';
import RecentActivity from '../components/Dashboard/RecentActivity';
import StockSearch from '../components/Dashboard/StockSearch';
import MarketSelector from '../components/Dashboard/MarketSelector';
import InvestmentSettings from '../components/Investment/InvestmentSettings';
import TradingBotWidget from '../components/Dashboard/TradingBotWidget';
import StockChart from '../components/Charts/StockChart';
import SensitivityChart from '../components/Charts/SensitivityChart';
import DayTradingPrediction from '../components/Trading/DayTradingPrediction';
import CurrencySwap from '../components/Trading/CurrencySwap';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Dashboard = () => {
  const { currentSymbol, currentPeriod, currentMarket } = useStore();

  const { data: stockData, isLoading: stockLoading } = useQuery(
    ['stock-data', currentSymbol, currentPeriod, currentMarket],
    () => stockAPI.getStockData(currentSymbol, currentPeriod, currentMarket),
    { enabled: !!currentSymbol }
  );

  const { data: stockInfo, isLoading: infoLoading } = useQuery(
    ['stock-info', currentSymbol, currentMarket],
    () => stockAPI.getStockInfo(currentSymbol, currentMarket),
    { enabled: !!currentSymbol }
  );

  const { data: prediction, isLoading: predictionLoading } = useQuery(
    ['prediction', currentSymbol, currentMarket],
    () => predictionAPI.getPrediction(currentSymbol),
    { enabled: !!currentSymbol }
  );

  if (stockLoading || infoLoading || predictionLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const latestPrice = stockData?.summary?.current_price || 0;
  const priceChange = stockData?.summary?.price_change || 0;
  const priceChangePercent = stockData?.summary?.price_change_pct || 0;
  const confidence = prediction?.prediction?.confidence || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
              <ChartBarIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Trading Dashboard</h1>
              <p className="text-sm text-gray-500">AI-powered market analysis and insights</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-sm text-gray-500">
              {currentSymbol ? (
                <span className="flex items-center space-x-1">
                  <BoltIcon className="w-3 h-3" />
                  <span>{currentSymbol} • {currentPeriod}</span>
                </span>
              ) : (
                <span>Select a stock to begin</span>
              )}
            </div>
            <a
              href="/download.html"
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <span>📱</span>
              <span>Mobile App</span>
            </a>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Stock Search</h3>
              <StockSearch />
            </div>
            
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Market Selection</h3>
              <MarketSelector />
            </div>
            
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Trading Bot</h3>
              <TradingBotWidget />
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Key Metrics */}
            {currentSymbol && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <CurrencyDollarIcon className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-gray-600">Current Price</span>
                  </div>
                  <div className="text-xl font-bold text-gray-900">${latestPrice.toFixed(2)}</div>
                  <div className={`text-sm flex items-center mt-1 ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {priceChange >= 0 ? <ArrowUpIcon className="w-3 h-3 mr-1" /> : <ArrowDownIcon className="w-3 h-3 mr-1" />}
                    {priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
                  </div>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <ArrowUpIcon className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-gray-600">Market Cap</span>
                  </div>
                  <div className="text-xl font-bold text-gray-900">
                    {stockInfo?.market_cap ? `$${(stockInfo.market_cap / 1e9).toFixed(1)}B` : 'N/A'}
                  </div>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <ChartBarIcon className="w-4 h-4 text-purple-600" />
                    <span className="text-sm font-medium text-gray-600">Volume</span>
                  </div>
                  <div className="text-xl font-bold text-gray-900">
                    {stockInfo?.volume ? `${(stockInfo.volume / 1e6).toFixed(1)}M` : 'N/A'}
                  </div>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <CpuChipIcon className="w-4 h-4 text-indigo-600" />
                    <span className="text-sm font-medium text-gray-600">AI Confidence</span>
                  </div>
                  <div className="text-xl font-bold text-gray-900">{confidence}%</div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${confidence}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            )}

            {/* Stock Chart */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-4">
                <ChartBarIcon className="w-4 h-4 text-gray-600" />
                <h3 className="text-sm font-medium text-gray-900">Price Chart</h3>
              </div>
              {currentSymbol ? (
                <StockChart 
                  symbol={currentSymbol} 
                  period={currentPeriod} 
                  showVolume={true} 
                  showIndicators={true} 
                />
              ) : (
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500 text-sm">Select a stock to view performance data</p>
                </div>
              )}
            </div>

          {/* Currency Swap Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            <CurrencySwap />
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">Market Overview</h3>
              <div className="space-y-3 sm:space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs sm:text-sm text-gray-600">Current Market:</span>
                  <span className="text-xs sm:text-sm font-medium">{stockAPI.getMarketInfo(currentMarket).name}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs sm:text-sm text-gray-600">Currency:</span>
                  <span className="text-xs sm:text-sm font-medium">{stockAPI.getMarketInfo(currentMarket).currency}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs sm:text-sm text-gray-600">Exchanges:</span>
                  <span className="text-xs sm:text-sm font-medium">{stockAPI.getMarketInfo(currentMarket).exchanges.join(', ')}</span>
                </div>
              </div>
            </div>
          </div>

          {/* AI Prediction with Confidence */}
          {currentSymbol && prediction && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Prediction & Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Prediction</h4>
                  <p className="text-gray-700 mb-4">
                    {typeof prediction.prediction === 'string' 
                      ? prediction.prediction 
                      : JSON.stringify(prediction.prediction, null, 2)}
                  </p>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Sentiment:</span>
                      <span className={`px-2 py-1 rounded text-sm font-medium ${
                        prediction.sentiment === 'Bullish' ? 'bg-green-100 text-green-800' :
                        prediction.sentiment === 'Bearish' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {prediction.sentiment}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Confidence:</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              confidence >= 80 ? 'bg-green-500' :
                              confidence >= 60 ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`}
                            style={{ width: `${confidence}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{confidence}%</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Target Price:</span>
                      <span className="text-sm font-medium">${prediction?.prediction?.target_price?.toFixed(2) || 'N/A'}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Stop Loss:</span>
                      <span className="text-sm font-medium">${prediction?.prediction?.stop_loss?.toFixed(2) || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Technical Indicators</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">RSI:</span>
                      <span className="text-sm font-medium">{prediction?.prediction?.technical_indicators?.rsi?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">SMA (20):</span>
                      <span className="text-sm font-medium">${prediction?.prediction?.technical_indicators?.sma_20?.toFixed(2) || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Volatility:</span>
                      <span className="text-sm font-medium">{(prediction?.prediction?.technical_indicators?.volatility * 100)?.toFixed(1) || 'N/A'}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Price Change:</span>
                      <span className={`text-sm font-medium ${
                        (prediction?.prediction?.technical_indicators?.price_change_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {(prediction?.prediction?.technical_indicators?.price_change_pct || 0).toFixed(2)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Day Trading Prediction */}
          {currentSymbol && (
            <DayTradingPrediction symbol={currentSymbol} />
          )}

          {/* Sensitivity Analysis */}
          {currentSymbol && (
            <SensitivityChart symbol={currentSymbol} />
          )}

          {/* Mobile App Download Section */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <div className="flex-1 mb-4 md:mb-0 md:mr-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">📱 Get the Mobile App</h3>
                <p className="text-gray-600 mb-4">
                  Take your AI-powered trading with you! Download our mobile app for real-time stock data, 
                  AI predictions, and portfolio management on the go.
                </p>
                <div className="flex flex-wrap gap-2 text-sm text-gray-500">
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Real-time data
                  </span>
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    AI predictions
                  </span>
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Portfolio management
                  </span>
                  <span className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                    Multi-market support
                  </span>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <a
                  href="/download.html"
                  className="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-medium rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  <span className="mr-2">📥</span>
                  Download APK
                </a>
                <a
                  href="/download.html"
                  className="inline-flex items-center justify-center px-6 py-3 bg-white text-blue-600 font-medium rounded-lg border border-blue-200 hover:bg-blue-50 transition-all duration-200"
                >
                  Learn More
                </a>
              </div>
            </div>
          </div>

          {/* Quick Actions and Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <QuickActions />
            <RecentActivity />
          </div>
        </div>
      </div>

      {/* AI Insights */}
      {prediction && currentSymbol && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights for {currentSymbol}</h3>
          <div className="prose prose-sm max-w-none">
            <p>
              {typeof prediction.prediction === 'string' 
                ? prediction.prediction 
                : JSON.stringify(prediction.prediction, null, 2)}
            </p>
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Confidence Analysis</h4>
              <p className="text-blue-800">
                Our AI model has analyzed {currentSymbol} with {confidence}% confidence. 
                {confidence >= 80 ? ' This is a high-confidence prediction based on strong technical and fundamental indicators.' :
                 confidence >= 60 ? ' This is a moderate-confidence prediction with some uncertainty factors.' :
                 ' This prediction has lower confidence due to market volatility or limited data.'}
              </p>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default Dashboard; 