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
  EyeIcon
} from '@heroicons/react/24/outline';
import { stockAPI, portfolioAPI } from '../services/api';
import { useStore } from '../store/store';
import StockChart from '../components/Charts/StockChart';
import LoadingSpinner from '../components/UI/LoadingSpinner';
import { toast } from 'react-hot-toast';

const EnhancedPortfolio = () => {
  const { 
    currentMarket, 
    investmentSettings
  } = useStore();
  
  const [buySymbol, setBuySymbol] = useState('');
  const [buyShares, setBuyShares] = useState('');
  const [sellSymbol, setSellSymbol] = useState('');
  const [sellShares, setSellShares] = useState('');
  const [cashAmount, setCashAmount] = useState('');
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [showTransactions, setShowTransactions] = useState(false);
  const [transactionFilter, setTransactionFilter] = useState('all');

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
  }[currentMarket] || { currency: '$', name: 'United States' };

  // Fetch portfolio data
  const { data: portfolioData, isLoading: portfolioLoading, refetch: refetchPortfolio } = useQuery(
    ['portfolio', currentMarket],
    () => portfolioAPI.getPortfolio(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
      onError: (error) => {
        console.error('Portfolio fetch error:', error);
        toast.error('Failed to load portfolio data');
      }
    }
  );

  // Fetch portfolio performance
  const { data: performanceData, isLoading: performanceLoading } = useQuery(
    ['portfolio-performance', currentMarket],
    () => portfolioAPI.getPortfolioPerformance(30),
    {
      enabled: !!portfolioData,
      refetchInterval: 60000, // Refresh every minute
    }
  );

  // Fetch transaction history
  const { data: transactionData, isLoading: transactionLoading } = useQuery(
    ['portfolio-transactions', transactionFilter],
    () => portfolioAPI.getTransactionHistory(50, transactionFilter === 'all' ? null : transactionFilter),
    {
      enabled: showTransactions,
      refetchInterval: 30000,
    }
  );

  // Portfolio initialization mutation
  const initializePortfolioMutation = useMutation(
    async (initialCapital) => {
      return portfolioAPI.initializePortfolio(initialCapital);
    },
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        toast.success(`Portfolio initialized with ${marketInfo.currency}${(10000).toLocaleString()}`);
      },
      onError: (error) => {
        toast.error(`Failed to initialize portfolio: ${error.message}`);
      }
    }
  );

  // Refresh portfolio mutation
  const refreshPortfolioMutation = useMutation(
    () => portfolioAPI.refreshPortfolio(),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        toast.success('Portfolio refreshed with latest prices');
      },
      onError: (error) => {
        toast.error(`Failed to refresh portfolio: ${error.message}`);
      }
    }
  );

  // Add cash mutation
  const addCashMutation = useMutation(
    (amount) => portfolioAPI.addCash(amount),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        queryClient.invalidateQueries(['portfolio-transactions']);
        setCashAmount('');
        toast.success(data.message);
      },
      onError: (error) => {
        toast.error(`Failed to add cash: ${error.message}`);
      }
    }
  );

  // Withdraw cash mutation
  const withdrawCashMutation = useMutation(
    (amount) => portfolioAPI.withdrawCash(amount),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        queryClient.invalidateQueries(['portfolio-transactions']);
        setCashAmount('');
        toast.success(data.message);
      },
      onError: (error) => {
        toast.error(`Failed to withdraw cash: ${error.message}`);
      }
    }
  );

  // Buy stock mutation
  const buyStockMutation = useMutation(
    async ({ symbol, shares }) => {
      return portfolioAPI.buyStock(symbol, shares);
    },
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        queryClient.invalidateQueries(['portfolio-transactions']);
        setBuySymbol('');
        setBuyShares('');
        toast.success(data.message);
      },
      onError: (error) => {
        toast.error(`Failed to buy stock: ${error.message}`);
      }
    }
  );

  // Sell stock mutation
  const sellStockMutation = useMutation(
    async ({ symbol, shares }) => {
      return portfolioAPI.sellStock(symbol, shares);
    },
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['portfolio', currentMarket]);
        queryClient.invalidateQueries(['portfolio-transactions']);
        setSellSymbol('');
        setSellShares('');
        toast.success(data.message);
      },
      onError: (error) => {
        toast.error(`Failed to sell stock: ${error.message}`);
      }
    }
  );

  // Handle functions
  const handleInitializePortfolio = () => {
    const initialCapital = 10000; // Default $10,000
    initializePortfolioMutation.mutate(initialCapital);
  };

  const handleRefreshPortfolio = () => {
    refreshPortfolioMutation.mutate();
  };

  const handleAddCash = () => {
    const amount = parseFloat(cashAmount);
    if (amount > 0) {
      addCashMutation.mutate(amount);
    } else {
      toast.error('Please enter a valid amount');
    }
  };

  const handleWithdrawCash = () => {
    const amount = parseFloat(cashAmount);
    if (amount > 0) {
      withdrawCashMutation.mutate(amount);
    } else {
      toast.error('Please enter a valid amount');
    }
  };

  const handleBuyStock = () => {
    const shares = parseInt(buyShares);
    if (buySymbol && shares > 0) {
      buyStockMutation.mutate({ symbol: buySymbol.toUpperCase(), shares });
    } else {
      toast.error('Please enter valid symbol and shares');
    }
  };

  const handleSellStock = () => {
    const shares = parseInt(sellShares);
    if (sellSymbol && shares > 0) {
      sellStockMutation.mutate({ symbol: sellSymbol.toUpperCase(), shares });
    } else {
      toast.error('Please enter valid symbol and shares');
    }
  };

  const formatCurrency = (amount) => {
    if (amount === undefined || amount === null || isNaN(amount)) {
      return `${marketInfo.currency}0.00`;
    }
    return `${marketInfo.currency}${amount.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  const formatPercentage = (value) => {
    if (value === undefined || value === null || isNaN(value)) {
      return <span className="text-gray-600">0.00%</span>;
    }
    const color = value >= 0 ? 'text-green-600' : 'text-red-600';
    const sign = value >= 0 ? '+' : '';
    return <span className={color}>{sign}{value.toFixed(2)}%</span>;
  };

  if (portfolioLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  const isInitialized = portfolioData && portfolioData.total_value > 0;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Enhanced Portfolio</h1>
            <p className="text-gray-600">Market: {marketInfo.name} ({marketInfo.currency})</p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={handleRefreshPortfolio}
              disabled={refreshPortfolioMutation.isLoading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
            >
              <ArrowPathIcon className="w-5 h-5" />
              <span>{refreshPortfolioMutation.isLoading ? 'Refreshing...' : 'Refresh Prices'}</span>
            </button>
          </div>
        </div>

        {!isInitialized ? (
          /* Portfolio Initialization */
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
        ) : (
          <>
            {/* Portfolio Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Value</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(portfolioData.total_value || 0)}
                    </p>
                  </div>
                  <ChartBarIcon className="w-8 h-8 text-blue-600" />
                </div>
                {performanceData && (
                  <p className="text-sm text-gray-600 mt-2">
                    Total Return: {formatPercentage(performanceData.total_return_pct || 0)}
                  </p>
                )}
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Available Cash</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(portfolioData.cash || 0)}
                    </p>
                  </div>
                  <CurrencyDollarIcon className="w-8 h-8 text-green-600" />
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {((portfolioData.cash / portfolioData.total_value) * 100).toFixed(1)}% of portfolio
                </p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Positions Value</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(portfolioData.positions_value || 0)}
                    </p>
                  </div>
                  <ShieldCheckIcon className="w-8 h-8 text-purple-600" />
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {portfolioData.positions?.length || 0} positions
                </p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Unrealized P&L</p>
                    <p className={`text-2xl font-bold ${(portfolioData.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(portfolioData.unrealized_pnl || 0)}
                    </p>
                  </div>
                  {(portfolioData.unrealized_pnl || 0) >= 0 ? 
                    <ArrowUpIcon className="w-8 h-8 text-green-600" /> : 
                    <ArrowDownIcon className="w-8 h-8 text-red-600" />
                  }
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Portfolio Actions */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Actions</h3>
                  
                  {/* Cash Management */}
                  <div className="mb-6">
                    <h4 className="text-md font-medium text-gray-700 mb-3">Cash Management</h4>
                    <div className="space-y-3">
                      <input
                        type="number"
                        placeholder="Amount"
                        value={cashAmount}
                        onChange={(e) => setCashAmount(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={handleAddCash}
                          disabled={!cashAmount || addCashMutation.isLoading}
                          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center justify-center space-x-2"
                        >
                          <BanknotesIcon className="w-4 h-4" />
                          <span>Add Cash</span>
                        </button>
                        <button
                          onClick={handleWithdrawCash}
                          disabled={!cashAmount || withdrawCashMutation.isLoading}
                          className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors flex items-center justify-center space-x-2"
                        >
                          <MinusIcon className="w-4 h-4" />
                          <span>Withdraw</span>
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Buy Stock */}
                  <div className="mb-6">
                    <h4 className="text-md font-medium text-gray-700 mb-3">Buy Stock</h4>
                    <div className="space-y-3">
                      <input
                        type="text"
                        placeholder="Stock Symbol (e.g., AAPL)"
                        value={buySymbol}
                        onChange={(e) => setBuySymbol(e.target.value.toUpperCase())}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <input
                        type="number"
                        placeholder="Number of Shares"
                        value={buyShares}
                        onChange={(e) => setBuyShares(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <button
                        onClick={handleBuyStock}
                        disabled={!buySymbol || !buyShares || buyStockMutation.isLoading}
                        className="w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center justify-center space-x-2"
                      >
                        <PlusIcon className="w-5 h-5" />
                        <span>{buyStockMutation.isLoading ? 'Buying...' : 'Buy Stock'}</span>
                      </button>
                    </div>
                  </div>

                  {/* Sell Stock */}
                  <div>
                    <h4 className="text-md font-medium text-gray-700 mb-3">Sell Stock</h4>
                    <div className="space-y-3">
                      <input
                        type="text"
                        placeholder="Stock Symbol (e.g., AAPL)"
                        value={sellSymbol}
                        onChange={(e) => setSellSymbol(e.target.value.toUpperCase())}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <input
                        type="number"
                        placeholder="Number of Shares"
                        value={sellShares}
                        onChange={(e) => setSellShares(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                      <button
                        onClick={handleSellStock}
                        disabled={!sellSymbol || !sellShares || sellStockMutation.isLoading}
                        className="w-full bg-red-600 text-white px-4 py-3 rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors flex items-center justify-center space-x-2"
                      >
                        <MinusIcon className="w-5 h-5" />
                        <span>{sellStockMutation.isLoading ? 'Selling...' : 'Sell Stock'}</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Transaction History Toggle */}
                <div className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Transaction History</h3>
                    <button
                      onClick={() => setShowTransactions(!showTransactions)}
                      className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                    >
                      <DocumentTextIcon className="w-5 h-5" />
                      <span>{showTransactions ? 'Hide' : 'Show'}</span>
                    </button>
                  </div>
                  
                  {showTransactions && (
                    <div className="space-y-4">
                      <select
                        value={transactionFilter}
                        onChange={(e) => setTransactionFilter(e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="all">All Transactions</option>
                        <option value="buy">Buy Orders</option>
                        <option value="sell">Sell Orders</option>
                        <option value="deposit">Cash Deposits</option>
                        <option value="withdrawal">Cash Withdrawals</option>
                      </select>
                      
                      {transactionLoading ? (
                        <LoadingSpinner />
                      ) : transactionData?.transactions && transactionData.transactions.length > 0 ? (
                        <div className="max-h-80 overflow-y-auto space-y-3">
                          {transactionData.transactions.map((transaction, index) => (
                            <div key={index} className="border border-gray-200 rounded-lg p-3">
                              <div className="flex justify-between items-start">
                                <div>
                                  <p className="font-medium text-sm">
                                    {transaction.type.toUpperCase()} {transaction.symbol === 'CASH' ? 'CASH' : transaction.symbol}
                                  </p>
                                  <p className="text-xs text-gray-600">
                                    {new Date(transaction.timestamp).toLocaleDateString()}
                                  </p>
                                </div>
                                <div className="text-right">
                                  <p className={`font-medium text-sm ${transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {formatCurrency(Math.abs(transaction.amount))}
                                  </p>
                                  {transaction.symbol !== 'CASH' && transaction.quantity > 1 && (
                                    <p className="text-xs text-gray-600">
                                      {transaction.quantity} shares @ {formatCurrency(transaction.price)}
                                    </p>
                                  )}
                                  {transaction.symbol === 'CASH' && (
                                    <p className="text-xs text-gray-600">
                                      Cash {transaction.type.toLowerCase()}
                                    </p>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 text-center py-4">No transactions found</p>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Positions */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-6">Current Positions</h3>
                  
                  {portfolioData.positions && portfolioData.positions.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full">
                        <thead>
                          <tr className="border-b border-gray-200">
                            <th className="text-left py-3 px-4 font-medium text-gray-900">Symbol</th>
                            <th className="text-right py-3 px-4 font-medium text-gray-900">Quantity</th>
                            <th className="text-right py-3 px-4 font-medium text-gray-900">Avg Price</th>
                            <th className="text-right py-3 px-4 font-medium text-gray-900">Current Price</th>
                            <th className="text-right py-3 px-4 font-medium text-gray-900">Market Value</th>
                            <th className="text-right py-3 px-4 font-medium text-gray-900">P&L</th>
                            <th className="text-right py-3 px-4 font-medium text-gray-900">P&L %</th>
                            <th className="text-center py-3 px-4 font-medium text-gray-900">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {portfolioData.positions.map((position, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="py-3 px-4">
                                <span className="font-medium text-blue-600">{position.symbol}</span>
                                <span className="text-xs text-gray-500 block">{position.market}</span>
                              </td>
                              <td className="py-3 px-4 text-right">{position.quantity}</td>
                              <td className="py-3 px-4 text-right">{formatCurrency(position.avg_price)}</td>
                              <td className="py-3 px-4 text-right">{formatCurrency(position.current_price)}</td>
                              <td className="py-3 px-4 text-right font-medium">{formatCurrency(position.market_value)}</td>
                              <td className={`py-3 px-4 text-right font-medium ${(position.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatCurrency(position.unrealized_pnl)}
                              </td>
                              <td className="py-3 px-4 text-right">
                                {formatPercentage(position.unrealized_pnl_pct)}
                              </td>
                              <td className="py-3 px-4 text-center">
                                <button
                                  onClick={() => setSelectedPosition(position)}
                                  className="text-blue-600 hover:text-blue-800"
                                >
                                  <EyeIcon className="w-4 h-4" />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <ChartBarIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">No positions in your portfolio</p>
                      <p className="text-sm text-gray-400 mt-2">Buy your first stock to get started</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Position Details Modal */}
      {selectedPosition && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-90vh overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  {selectedPosition.symbol} Position Details
                </h3>
                <button
                  onClick={() => setSelectedPosition(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">Close</span>
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-600">Current Price</p>
                  <p className="text-lg font-semibold">{formatCurrency(selectedPosition.current_price)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Market Value</p>
                  <p className="text-lg font-semibold">{formatCurrency(selectedPosition.market_value)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Unrealized P&L</p>
                  <p className={`text-lg font-semibold ${(selectedPosition.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(selectedPosition.unrealized_pnl)} ({formatPercentage(selectedPosition.unrealized_pnl_pct)})
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Last Updated</p>
                  <p className="text-lg font-semibold">
                    {selectedPosition.last_updated ? new Date(selectedPosition.last_updated).toLocaleString() : 'N/A'}
                  </p>
                </div>
              </div>
              
              <div className="mb-6">
                <StockChart symbol={selectedPosition.symbol} />
              </div>
              
              <div className="flex space-x-4">
                <button
                  onClick={() => {
                    setBuySymbol(selectedPosition.symbol);
                    setSelectedPosition(null);
                  }}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Buy More
                </button>
                <button
                  onClick={() => {
                    setSellSymbol(selectedPosition.symbol);
                    setSellShares(selectedPosition.quantity.toString());
                    setSelectedPosition(null);
                  }}
                  className="flex-1 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Sell Position
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedPortfolio;
