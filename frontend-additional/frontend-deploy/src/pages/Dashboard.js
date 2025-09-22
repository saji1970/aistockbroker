import React from 'react';
import { useQuery } from 'react-query';
import { stockAPI, predictionAPI } from '../services/api';
import { useStore } from '../store/store';
import MetricCard from '../components/Dashboard/MetricCard';
import QuickActions from '../components/Dashboard/QuickActions';
import RecentActivity from '../components/Dashboard/RecentActivity';
import StockSearch from '../components/Dashboard/StockSearch';
import MarketSelector from '../components/Dashboard/MarketSelector';
import InvestmentSettings from '../components/Investment/InvestmentSettings';
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
  const confidence = prediction?.confidence || 0;

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm sm:text-base text-gray-600">Welcome to your AI-powered trading platform</p>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
          <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-2 text-xs sm:text-sm text-gray-500">
            <span>Current Symbol: {currentSymbol || 'Select a stock'}</span>
            <span className="hidden sm:inline">•</span>
            <span>Period: {currentPeriod || '1Y'}</span>
          </div>
          <a
            href="/download.html"
            className="inline-flex items-center px-3 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white text-xs sm:text-sm font-medium rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-sm hover:shadow-md"
          >
            📱 Download Mobile App
          </a>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Stock Search and Controls */}
        <div className="lg:col-span-1 space-y-4 sm:space-y-6">
          <StockSearch />
          <MarketSelector />
          <InvestmentSettings />
        </div>

        {/* Main Dashboard Content */}
        <div className="lg:col-span-3 space-y-4 sm:space-y-6">
          {/* Key Metrics - Only show if stock is selected */}
          {currentSymbol && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
              <MetricCard
                title="Current Price"
                value={`$${latestPrice.toFixed(2)}`}
                change={priceChange.toFixed(2)}
                changePercent={priceChangePercent.toFixed(2)}
                type="price"
              />
              <MetricCard
                title="Market Cap"
                value={stockInfo?.market_cap ? `$${(stockInfo.market_cap / 1e9).toFixed(1)}B` : 'N/A'}
              />
              <MetricCard
                title="Volume"
                value={stockInfo?.volume ? `${(stockInfo.volume / 1e6).toFixed(1)}M` : 'N/A'}
              />
              <MetricCard
                title="AI Confidence"
                value={`${confidence}%`}
                type="confidence"
                confidence={confidence}
              />
            </div>
          )}

          {/* Stock Chart */}
          {currentSymbol ? (
            <StockChart 
              symbol={currentSymbol} 
              period={currentPeriod} 
              showVolume={true} 
              showIndicators={true} 
            />
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">Stock Performance</h3>
              <div className="h-48 sm:h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                <p className="text-gray-500 text-sm sm:text-base">Select a stock to view performance data</p>
              </div>
            </div>
          )}

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
                  <p className="text-gray-700 mb-4">{prediction.prediction}</p>
                  
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
                      <span className="text-sm font-medium">${prediction.target_price?.toFixed(2) || 'N/A'}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Stop Loss:</span>
                      <span className="text-sm font-medium">${prediction.stop_loss?.toFixed(2) || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Technical Indicators</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">RSI:</span>
                      <span className="text-sm font-medium">{prediction.technical_indicators?.rsi?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">SMA (20):</span>
                      <span className="text-sm font-medium">${prediction.technical_indicators?.sma_20?.toFixed(2) || 'N/A'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Volatility:</span>
                      <span className="text-sm font-medium">{(prediction.technical_indicators?.volatility * 100)?.toFixed(1) || 'N/A'}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Price Change:</span>
                      <span className={`text-sm font-medium ${
                        (prediction.technical_indicators?.price_change_pct || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {(prediction.technical_indicators?.price_change_pct || 0).toFixed(2)}%
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
            <p>{prediction.prediction}</p>
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
  );
};

export default Dashboard; 