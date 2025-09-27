import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  PlusIcon, 
  MinusIcon, 
  CurrencyDollarIcon, 
  ChartBarIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  ArrowPathIcon,
  BanknotesIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ClockIcon,
  DocumentTextIcon,
  EyeIcon,
  Cog6ToothIcon,
  SparklesIcon,
  MagnifyingGlassIcon
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
  
  const [activeTab, setActiveTab] = useState('overview');
  const [buySymbol, setBuySymbol] = useState('');
  const [buyShares, setBuyShares] = useState('');
  const [sellSymbol, setSellSymbol] = useState('');
  const [sellShares, setSellShares] = useState('');
  const [cashAmount, setCashAmount] = useState('');
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [showTransactions, setShowTransactions] = useState(false);
  const [transactionFilter, setTransactionFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'positions', name: 'Positions', icon: CurrencyDollarIcon },
    { id: 'transactions', name: 'Transactions', icon: DocumentTextIcon },
    { id: 'analysis', name: 'Analysis', icon: SparklesIcon },
    { id: 'settings', name: 'Settings', icon: Cog6ToothIcon }
  ];

  const queryClient = useQueryClient();

  // Market info
  const marketInfo = {
    US: { currency: '$', name: 'United States' },
    UK: { currency: '£', name: 'United Kingdom' },
    Canada: { currency: 'C$', name: 'Canada' },
    Germany: { currency: '€', name: 'Germany' },
    Japan: { currency: '¥', name: 'Japan' },
    Australia: { currency: 'A$', name: 'Australia' },
    France: { currency: '€', name: 'France' },
    India: { currency: '₹', name: 'India' }
  };

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
      ...portfolio,
      positions,
      totalValue: data.totalValue || data.total_value || 0,
      cash: data.cash || 0,
      totalReturn: data.totalReturn || data.total_return || 0,
      totalReturnPercent: data.totalReturnPercent || data.total_return_percent || 0,
      dayChange: data.dayChange || data.day_change || 0,
      dayChangePercent: data.dayChangePercent || data.day_change_percent || 0
    };
  };

  // Fetch portfolio data
  const { data: portfolioData, isLoading: portfolioLoading, refetch: refetchPortfolio } = useQuery(
    'portfolio',
    () => portfolioAPI.getPortfolio(),
    {
      select: transformPortfolioData,
      onSuccess: (data) => {
        if (data) {
          updatePortfolio(data);
        }
      },
      onError: (error) => {
        console.error('Error fetching portfolio:', error);
        toast.error('Failed to load portfolio data');
      }
    }
  );

  // Fetch portfolio performance
  const { data: performanceData, isLoading: performanceLoading } = useQuery(
    'portfolio-performance',
    () => portfolioAPI.getPortfolioPerformance(),
    {
      enabled: !!portfolioData,
      onError: (error) => {
        console.error('Error fetching portfolio performance:', error);
      }
    }
  );

  // Fetch portfolio analytics
  const { data: analyticsData, isLoading: analyticsLoading } = useQuery(
    'portfolio-analytics',
    () => portfolioAPI.getPortfolioAnalytics(),
    {
      enabled: !!portfolioData,
      onError: (error) => {
        console.error('Error fetching portfolio analytics:', error);
      }
    }
  );

  // Buy stock mutation
  const buyMutation = useMutation(
    (data) => portfolioAPI.buyStock(data.symbol, data.shares),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('portfolio');
        queryClient.invalidateQueries('portfolio-performance');
        setBuySymbol('');
        setBuyShares('');
        toast.success('Stock purchased successfully');
      },
      onError: (error) => {
        console.error('Error buying stock:', error);
        toast.error('Failed to purchase stock');
      }
    }
  );

  // Sell stock mutation
  const sellMutation = useMutation(
    (data) => portfolioAPI.sellStock(data.symbol, data.shares),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('portfolio');
        queryClient.invalidateQueries('portfolio-performance');
        setSellSymbol('');
        setSellShares('');
        toast.success('Stock sold successfully');
      },
      onError: (error) => {
        console.error('Error selling stock:', error);
        toast.error('Failed to sell stock');
      }
    }
  );

  // Portfolio initialization mutation
  const initializePortfolioMutation = useMutation(
    async (initialCapital) => {
      return portfolioAPI.initializePortfolio(initialCapital);
    },
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries('portfolio');
        queryClient.invalidateQueries('portfolio-performance');
        toast.success(`Portfolio initialized with ${marketInfo[currentMarket]?.currency || '$'}${(10000).toLocaleString()}`);
      },
      onError: (error) => {
        console.error('Error initializing portfolio:', error);
        toast.error(`Failed to initialize portfolio: ${error.message}`);
      }
    }
  );

  // Refresh portfolio mutation
  const refreshPortfolioMutation = useMutation(
    () => portfolioAPI.refreshPortfolio(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('portfolio');
        queryClient.invalidateQueries('portfolio-performance');
        toast.success('Portfolio refreshed with latest prices');
      },
      onError: (error) => {
        console.error('Error refreshing portfolio:', error);
        toast.error(`Failed to refresh portfolio: ${error.message}`);
      }
    }
  );

  // Add cash mutation
  const addCashMutation = useMutation(
    (amount) => portfolioAPI.addCash(amount),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('portfolio');
        queryClient.invalidateQueries('portfolio-performance');
        setCashAmount('');
        toast.success('Cash added successfully');
      },
      onError: (error) => {
        console.error('Error adding cash:', error);
        toast.error('Failed to add cash');
      }
    }
  );

  // Withdraw cash mutation
  const withdrawCashMutation = useMutation(
    (amount) => portfolioAPI.withdrawCash(amount),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('portfolio');
        queryClient.invalidateQueries('portfolio-performance');
        setCashAmount('');
        toast.success('Cash withdrawn successfully');
      },
      onError: (error) => {
        console.error('Error withdrawing cash:', error);
        toast.error('Failed to withdraw cash');
      }
    }
  );

  const handleBuyStock = (e) => {
    e.preventDefault();
    if (!buySymbol || !buyShares) {
      toast.error('Please enter symbol and shares');
      return;
    }
    buyMutation.mutate({ symbol: buySymbol.toUpperCase(), shares: parseInt(buyShares) });
  };

  const handleSellStock = (e) => {
    e.preventDefault();
    if (!sellSymbol || !sellShares) {
      toast.error('Please enter symbol and shares');
      return;
    }
    sellMutation.mutate({ symbol: sellSymbol.toUpperCase(), shares: parseInt(sellShares) });
  };

  const handleInitializePortfolio = () => {
    const initialCapital = 10000; // Default $10,000
    initializePortfolioMutation.mutate(initialCapital);
  };

  const handleRefreshPortfolio = () => {
    refreshPortfolioMutation.mutate();
  };

  const handleAddCash = (e) => {
    e.preventDefault();
    if (!cashAmount) {
      toast.error('Please enter amount');
      return;
    }
    addCashMutation.mutate(parseFloat(cashAmount));
  };

  const handleWithdrawCash = (e) => {
    e.preventDefault();
    if (!cashAmount) {
      toast.error('Please enter amount');
      return;
    }
    withdrawCashMutation.mutate(parseFloat(cashAmount));
  };

  const filteredPositions = portfolio.positions?.filter(position =>
    position.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    position.name?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  if (portfolioLoading) {
    return <LoadingSpinner />;
  }

  const renderOverview = () => {
    const isInitialized = portfolio.totalValue > 0;
    
    if (!isInitialized) {
      return (
        <div className="space-y-6">
          {/* Portfolio Initialization */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
            <div className="max-w-md mx-auto">
              <h3 className="text-xl font-semibold text-blue-900 mb-4">Initialize Your Portfolio</h3>
              <p className="text-blue-700 mb-6">Start your investment journey with a virtual portfolio</p>
              <button
                onClick={handleInitializePortfolio}
                disabled={initializePortfolioMutation.isLoading}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center space-x-2 mx-auto"
              >
                <PlusIcon className="w-5 h-5" />
                <span>{initializePortfolioMutation.isLoading ? 'Initializing...' : 'Initialize Portfolio'}</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Portfolio Header with Refresh Button */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Portfolio Overview</h2>
            <p className="text-gray-600">Market: {marketInfo[currentMarket]?.name || 'United States'} ({marketInfo[currentMarket]?.currency || '$'})</p>
          </div>
          <button
            onClick={handleRefreshPortfolio}
            disabled={refreshPortfolioMutation.isLoading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
          >
            <ArrowPathIcon className="w-5 h-5" />
            <span>{refreshPortfolioMutation.isLoading ? 'Refreshing...' : 'Refresh Prices'}</span>
          </button>
        </div>

        {/* Portfolio Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Value</p>
              <p className="text-2xl font-semibold text-gray-900">
                {marketInfo[currentMarket]?.currency || '$'}
                {portfolio.totalValue?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowUpIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Return</p>
              <p className="text-2xl font-semibold text-gray-900">
                {marketInfo[currentMarket]?.currency || '$'}
                {portfolio.totalReturn?.toLocaleString() || '0'}
              </p>
              <p className={`text-sm ${portfolio.totalReturnPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {portfolio.totalReturnPercent >= 0 ? '+' : ''}{portfolio.totalReturnPercent?.toFixed(2) || '0'}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Day Change</p>
              <p className="text-2xl font-semibold text-gray-900">
                {marketInfo[currentMarket]?.currency || '$'}
                {portfolio.dayChange?.toLocaleString() || '0'}
              </p>
              <p className={`text-sm ${portfolio.dayChangePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {portfolio.dayChangePercent >= 0 ? '+' : ''}{portfolio.dayChangePercent?.toFixed(2) || '0'}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BanknotesIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Cash</p>
              <p className="text-2xl font-semibold text-gray-900">
                {marketInfo[currentMarket]?.currency || '$'}
                {portfolio.cash?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Performance</h3>
        {performanceData ? (
          <StockChart 
            data={performanceData} 
            height={300}
            showVolume={false}
          />
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-500">
            No performance data available
          </div>
        )}
      </div>

      {/* Recent Positions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Positions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPositions.slice(0, 5).map((position) => (
                <tr key={position.symbol} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{position.symbol}</div>
                    <div className="text-sm text-gray-500">{position.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {position.shares}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {marketInfo[currentMarket]?.currency || '$'}
                    {(position.shares * position.price)?.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm ${position.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {position.change >= 0 ? '+' : ''}{position.change}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    );
  };

  const renderPositions = () => (
    <div className="space-y-6">
      {/* Search */}
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search positions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>

      {/* Trading Forms */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Buy Stock */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Buy Stock</h3>
          <form onSubmit={handleBuyStock} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Symbol</label>
              <input
                type="text"
                value={buySymbol}
                onChange={(e) => setBuySymbol(e.target.value.toUpperCase())}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="e.g., AAPL"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Shares</label>
              <input
                type="number"
                value={buyShares}
                onChange={(e) => setBuyShares(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Number of shares"
              />
            </div>
            <button
              type="submit"
              disabled={buyMutation.isLoading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            >
              {buyMutation.isLoading ? 'Buying...' : 'Buy Stock'}
            </button>
          </form>
        </div>

        {/* Sell Stock */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Sell Stock</h3>
          <form onSubmit={handleSellStock} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Symbol</label>
              <input
                type="text"
                value={sellSymbol}
                onChange={(e) => setSellSymbol(e.target.value.toUpperCase())}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="e.g., AAPL"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Shares</label>
              <input
                type="number"
                value={sellShares}
                onChange={(e) => setSellShares(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Number of shares"
              />
            </div>
            <button
              type="submit"
              disabled={sellMutation.isLoading}
              className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:ring-2 focus:ring-red-500 disabled:opacity-50"
            >
              {sellMutation.isLoading ? 'Selling...' : 'Sell Stock'}
            </button>
          </form>
        </div>
      </div>

      {/* Cash Management */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Cash Management</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Amount</label>
            <input
              type="number"
              step="0.01"
              value={cashAmount}
              onChange={(e) => setCashAmount(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Enter amount"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={handleAddCash}
              disabled={!cashAmount || addCashMutation.isLoading}
              className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-green-500 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              <BanknotesIcon className="h-4 w-4" />
              <span>{addCashMutation.isLoading ? 'Adding...' : 'Add Cash'}</span>
            </button>
            <button
              onClick={handleWithdrawCash}
              disabled={!cashAmount || withdrawCashMutation.isLoading}
              className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:ring-2 focus:ring-red-500 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              <MinusIcon className="h-4 w-4" />
              <span>{withdrawCashMutation.isLoading ? 'Withdrawing...' : 'Withdraw'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">All Positions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPositions.map((position) => (
                <tr key={position.symbol} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{position.symbol}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{position.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {position.shares}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {marketInfo[currentMarket]?.currency || '$'}
                    {position.price?.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {marketInfo[currentMarket]?.currency || '$'}
                    {(position.shares * position.price)?.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`text-sm ${position.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {position.change >= 0 ? '+' : ''}{position.change}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => setSelectedPosition(position)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderTransactions = () => (
    <div className="space-y-6">
      {/* Transaction Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <select
            value={transactionFilter}
            onChange={(e) => setTransactionFilter(e.target.value)}
            className="w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="all">All Transactions</option>
            <option value="buy">Buy Orders</option>
            <option value="sell">Sell Orders</option>
            <option value="cash">Cash Deposits</option>
          </select>
        </div>
      </div>

      {/* Mock Transactions */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Transaction History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {/* Mock transaction data */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">2024-09-25</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                    BUY
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">AAPL</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">10</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$150.00</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$1,500.00</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                    Completed
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderAnalysis = () => (
    <div className="space-y-6">
      {/* Sensitivity Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Sensitivity Analysis</h3>
        <SensitivityChart />
      </div>

      {/* Portfolio Analytics */}
      {analyticsData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Metrics</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Sharpe Ratio</span>
                <span className="text-sm font-medium">{analyticsData.sharpeRatio?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Beta</span>
                <span className="text-sm font-medium">{analyticsData.beta?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Volatility</span>
                <span className="text-sm font-medium">{analyticsData.volatility?.toFixed(2) || 'N/A'}%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Asset Allocation</h3>
            <div className="space-y-4">
              {analyticsData.allocation?.map((item, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">{item.sector}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full" 
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium w-12">{item.percentage.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderSettings = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Default Market</label>
            <select className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
              {Object.entries(marketInfo).map(([key, info]) => (
                <option key={key} value={key}>{info.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Risk Tolerance</label>
            <select className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
              <option>Conservative</option>
              <option>Moderate</option>
              <option>Aggressive</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Rebalancing Frequency</label>
            <select className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500">
              <option>Monthly</option>
              <option>Quarterly</option>
              <option>Annually</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
          <p className="mt-2 text-gray-600">Manage your investments and track performance</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className={`-ml-0.5 mr-2 h-5 w-5 ${
                  activeTab === tab.id ? 'text-indigo-500' : 'text-gray-400 group-hover:text-gray-500'
                }`} />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'positions' && renderPositions()}
        {activeTab === 'transactions' && renderTransactions()}
        {activeTab === 'analysis' && renderAnalysis()}
        {activeTab === 'settings' && renderSettings()}
      </div>
    </div>
  );
};

export default Portfolio;