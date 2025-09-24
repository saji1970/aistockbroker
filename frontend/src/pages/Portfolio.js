import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  PlusIcon, 
  MinusIcon, 
  CurrencyDollarIcon, 
  ChartBarIcon,
  GlobeAltIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';
import { stockAPI, portfolioAPI } from '../services/api';
import { useStore } from '../store/store';
import StockChart from '../components/Charts/StockChart';
import SensitivityChart from '../components/Charts/SensitivityChart';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { toast } from 'react-hot-toast';

const Portfolio = () => {
  const { 
    currentMarket, 
    investmentSettings, 
    portfolio, 
    addPosition, 
    removePosition,
    updatePortfolio 
  } = useStore();
  
  const [buySymbol, setBuySymbol] = useState('');
  const [buyShares, setBuyShares] = useState('');
  const [sellSymbol, setSellSymbol] = useState('');
  const [sellShares, setSellShares] = useState('');
  const [selectedAsset, setSelectedAsset] = useState(null);

  const queryClient = useQueryClient();

  // Transform backend data structure to match frontend expectations
  const transformPortfolioData = (data) => {
    if (!data) return portfolio;

    // Ensure positions is always an array
    let positions = [];
    if (Array.isArray(data.assets)) {
      positions = data.assets;
    } else if (Array.isArray(data.positions)) {
      positions = data.positions;
    } else if (data.assets && typeof data.assets === 'object') {
      // If assets is an object, convert to array
      positions = Object.values(data.assets);
    } else if (data.positions && typeof data.positions === 'object') {
      // If positions is an object, convert to array
      positions = Object.values(data.positions);
    }

    return {
      totalValue: data.total_value || data.totalValue || 0,
      cash: data.available_cash || data.cash || 0,
      positions: positions,
      performance: data.performance || {},
      lastUpdated: data.lastUpdated || new Date().toISOString(),
    };
  };

  // Fetch portfolio data using enhanced API
  const { data: portfolioData, isLoading: portfolioLoading } = useQuery(
    ['portfolio', currentMarket],
    () => portfolioAPI.refreshPortfolio(),
    { enabled: !!currentMarket }
  );

  // Fetch portfolio performance
  const { data: performanceData, isLoading: performanceLoading } = useQuery(
    ['portfolio-performance', currentMarket],
    () => portfolioAPI.getPortfolioPerformance(currentMarket),
    { enabled: !!currentMarket }
  );

  // Fetch portfolio analytics
  const { data: analyticsData, isLoading: analyticsLoading } = useQuery(
    ['portfolio-analytics', currentMarket],
    () => portfolioAPI.getPortfolioAnalytics(currentMarket),
    { enabled: !!currentMarket }
  );

  // Mutations
  const buyStockMutation = useMutation(
    async ({ symbol, shares, market }) => {
      // Use enhanced API - it will fetch real-time price automatically
      return portfolioAPI.buyStock(symbol, shares);
    },
    {
      onSuccess: (data, variables) => {
        const { symbol } = variables;
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        toast.success(data.message || `Successfully bought shares of ${symbol}`);
        setBuySymbol('');
        setBuyShares('');
      },
      onError: (error) => {
        toast.error(`Failed to buy stock: ${error.message}`);
      }
    }
  );

  const sellStockMutation = useMutation(
    async ({ symbol, shares, market }) => {
      // Use enhanced API - it will fetch real-time price automatically
      return portfolioAPI.sellStock(symbol, shares);
    },
    {
      onSuccess: (data, variables) => {
        const { symbol } = variables;
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        toast.success(data.message || `Successfully sold shares of ${symbol}`);
        setSellSymbol('');
        setSellShares('');
      },
      onError: (error) => {
        toast.error(`Failed to sell stock: ${error.message}`);
      }
    }
  );

  const initializePortfolioMutation = useMutation(
    async (initialCapital) => {
      return portfolioAPI.initializePortfolio(initialCapital);
    },
    {
      onSuccess: (data, variables) => {
        const initialCapital = variables;
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        toast.success(`Portfolio initialized with ${marketInfo.currency}${(10000).toLocaleString()}`);
      },
      onError: (error) => {
        toast.error(`Failed to initialize portfolio: ${error.message}`);
      }
    }
  );

  const handleInitializePortfolio = () => {
    const initialCapital = 10000; // Default $10,000
    initializePortfolioMutation.mutate(initialCapital);
  };

  const handleBuyStock = (e) => {
    e.preventDefault();
    if (!buySymbol || !buyShares) {
      toast.error('Please enter symbol and shares');
      return;
    }
    buyStockMutation.mutate({ 
      symbol: buySymbol, 
      shares: parseFloat(buyShares), 
      market: currentMarket 
    });
  };

  const handleSellStock = (e) => {
    e.preventDefault();
    if (!sellSymbol || !sellShares) {
      toast.error('Please enter symbol and shares');
      return;
    }
    sellStockMutation.mutate({ 
      symbol: sellSymbol, 
      shares: parseFloat(sellShares), 
      market: currentMarket 
    });
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (portfolioLoading) return <LoadingSpinner />;

  const currentPortfolio = transformPortfolioData(portfolioData) || portfolio;
  const marketInfo = stockAPI.getMarketInfo(currentMarket);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
          <p className="text-gray-600">Manage your investments across markets</p>
        </div>
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <GlobeAltIcon className="w-4 h-4" />
            <span>{marketInfo.name}</span>
          </div>
          <div className="flex items-center space-x-1">
            <ShieldCheckIcon className="w-4 h-4" />
            <span className="capitalize">{investmentSettings.riskTolerance}</span>
          </div>
        </div>
      </div>

      {/* Initialize Portfolio Button */}
      {(!currentPortfolio.totalValue || currentPortfolio.totalValue === 0) && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900">Initialize Your Portfolio</h3>
              <p className="text-blue-700">Start your investment journey with a virtual portfolio</p>
            </div>
            <button
              onClick={handleInitializePortfolio}
              disabled={initializePortfolioMutation.isLoading}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
            >
              <PlusIcon className="w-5 h-5" />
              <span>{initializePortfolioMutation.isLoading ? 'Initializing...' : 'Initialize Portfolio'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-gray-900">
                {marketInfo.currency}{currentPortfolio.totalValue?.toLocaleString() || '0'}
              </p>
            </div>
            <CurrencyDollarIcon className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Available Cash</p>
              <p className="text-2xl font-bold text-gray-900">
                {marketInfo.currency}{currentPortfolio.cash?.toLocaleString() || '0'}
              </p>
            </div>
            <ChartBarIcon className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Return</p>
              <p className={`text-2xl font-bold ${performanceData?.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {performanceData?.totalReturn?.toFixed(2) || '0'}%
              </p>
            </div>
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 text-sm font-bold">%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Positions</p>
              <p className="text-2xl font-bold text-gray-900">
                {Array.isArray(currentPortfolio.positions) ? currentPortfolio.positions.length : 0}
              </p>
            </div>
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <span className="text-purple-600 text-sm font-bold">#</span>
            </div>
          </div>
        </div>
      </div>

      {/* Trading Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Buy Stock */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <PlusIcon className="w-5 h-5 mr-2 text-green-600" />
            Buy Stock
          </h3>
          <form onSubmit={handleBuyStock} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Symbol</label>
              <input
                type="text"
                value={buySymbol}
                onChange={(e) => setBuySymbol(e.target.value.toUpperCase())}
                placeholder="e.g., AAPL"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Shares</label>
              <input
                type="number"
                value={buyShares}
                onChange={(e) => setBuyShares(e.target.value)}
                placeholder="10"
                min="0.01"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              disabled={buyStockMutation.isLoading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {buyStockMutation.isLoading ? 'Buying...' : 'Buy Stock'}
            </button>
          </form>
        </div>

        {/* Sell Stock */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <MinusIcon className="w-5 h-5 mr-2 text-red-600" />
            Sell Stock
          </h3>
          <form onSubmit={handleSellStock} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Symbol</label>
              <input
                type="text"
                value={sellSymbol}
                onChange={(e) => setSellSymbol(e.target.value.toUpperCase())}
                placeholder="e.g., AAPL"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Shares</label>
              <input
                type="number"
                value={sellShares}
                onChange={(e) => setSellShares(e.target.value)}
                placeholder="10"
                min="0.01"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            <button
              type="submit"
              disabled={sellStockMutation.isLoading}
              className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {sellStockMutation.isLoading ? 'Selling...' : 'Sell Stock'}
            </button>
          </form>
        </div>
      </div>

      {/* Portfolio Assets */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Portfolio Assets</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Return</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {(Array.isArray(currentPortfolio.positions) ? currentPortfolio.positions : []).length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                    <div className="space-y-2">
                      <p className="text-lg font-medium">No positions yet</p>
                      <p className="text-sm">Start by buying your first stock</p>
                    </div>
                  </td>
                </tr>
              ) : (
                (Array.isArray(currentPortfolio.positions) ? currentPortfolio.positions : []).map((position) => (
                  <tr key={position.symbol} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{position.symbol || 'N/A'}</div>
                      <div className="text-sm text-gray-500">{position.name || position.symbol}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {position.quantity || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {marketInfo.currency}{(position.currentPrice || position.current_price || 0).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {marketInfo.currency}{((position.quantity || 0) * (position.currentPrice || position.current_price || 0)).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${(position.return || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {(position.return || 0) >= 0 ? '+' : ''}{(position.return || 0).toFixed(2)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(position.risk || 'medium')}`}>
                        {position.risk || 'medium'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setSelectedAsset(position)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        View
                      </button>
                      <button
                        onClick={() => {
                          setSellSymbol(position.symbol || '');
                          setSellShares((position.quantity || 0).toString());
                        }}
                        className="text-red-600 hover:text-red-900"
                      >
                        Sell
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Charts */}
      {selectedAsset && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <StockChart 
            symbol={selectedAsset.symbol} 
            period="1y" 
            market={currentMarket}
          />
          <SensitivityChart 
            symbol={selectedAsset.symbol}
            market={currentMarket}
          />
        </div>
      )}
    </div>
  );
};

export default Portfolio; 