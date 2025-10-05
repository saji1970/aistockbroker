import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { stockAPI, backtestAPI } from '../services/api';
import EquityCurveChart from '../components/Charts/EquityCurveChart';
import { toast } from 'react-hot-toast';
import {
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  InformationCircleIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  FireIcon,
  PlayIcon,
  StopIcon,
  DocumentChartBarIcon,
  BeakerIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const Backtest = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [initialCapital, setInitialCapital] = useState(10000);
  const [strategy, setStrategy] = useState('sma_crossover');
  const [isRunning, setIsRunning] = useState(false);
  const [backtestResults, setBacktestResults] = useState(null);

  const popularInstruments = {
    stocks: [
      { symbol: 'AAPL', name: 'Apple Inc.', type: 'stock' },
      { symbol: 'MSFT', name: 'Microsoft Corporation', type: 'stock' },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', type: 'stock' },
      { symbol: 'TSLA', name: 'Tesla Inc.', type: 'stock' },
      { symbol: 'NVDA', name: 'NVIDIA Corporation', type: 'stock' },
      { symbol: 'META', name: 'Meta Platforms Inc.', type: 'stock' },
      { symbol: 'AMZN', name: 'Amazon.com Inc.', type: 'stock' },
      { symbol: 'NFLX', name: 'Netflix Inc.', type: 'stock' },
    ],
    etfs: [
      { symbol: 'SPY', name: 'SPDR S&P 500 ETF', type: 'etf' },
      { symbol: 'QQQ', name: 'Invesco QQQ Trust', type: 'etf' },
      { symbol: 'VTI', name: 'Vanguard Total Stock Market ETF', type: 'etf' },
      { symbol: 'VOO', name: 'Vanguard S&P 500 ETF', type: 'etf' },
      { symbol: 'ARKK', name: 'ARK Innovation ETF', type: 'etf' },
      { symbol: 'GLD', name: 'SPDR Gold Trust', type: 'etf' },
    ],
    crypto: [
      { symbol: 'BTCUSD', name: 'Bitcoin / USD', type: 'crypto' },
      { symbol: 'ETHUSD', name: 'Ethereum / USD', type: 'crypto' },
    ],
    indices: [
      { symbol: 'SPX', name: 'S&P 500 Index', type: 'index' },
      { symbol: 'NDX', name: 'NASDAQ 100 Index', type: 'index' },
    ],
  };

  const strategies = [
    { id: 'sma_crossover', name: 'SMA Crossover', description: 'Simple Moving Average Crossover Strategy' },
    { id: 'rsi_divergence', name: 'RSI Divergence', description: 'Relative Strength Index Divergence Strategy' },
    { id: 'macd_signal', name: 'MACD Signal', description: 'Moving Average Convergence Divergence Strategy' },
  ];

  const getInstrumentTypeIcon = (type) => {
    switch (type) {
      case 'stock': return BuildingOfficeIcon;
      case 'etf': return GlobeAltIcon;
      case 'crypto': return CurrencyDollarIcon;
      case 'index': return ChartBarIcon;
      default: return InformationCircleIcon;
    }
  };

  const handleInstrumentSelect = (instrument) => {
    setSelectedSymbol(instrument.symbol);
  };

  const handleStrategySelect = (strategyId) => {
    setStrategy(strategyId);
  };

  const { mutate: runBacktest, isLoading: isBacktesting } = useMutation(
    backtestAPI.runBacktest,
    {
      onMutate: () => {
        setIsRunning(true);
        setBacktestResults(null);
        toast.loading('Running backtest...');
      },
      onSuccess: (data) => {
        toast.dismiss();
        setBacktestResults(data);
        toast.success('Backtest completed successfully!');
      },
      onError: (error) => {
        toast.dismiss();
        console.error('Backtest error:', error);
        toast.error(`Backtest failed: ${error.message}`);
      },
      onSettled: () => {
        setIsRunning(false);
      }
    }
  );

  const handleRunBacktest = () => {
    runBacktest({
      symbol: selectedSymbol,
      startDate,
      endDate,
      initialCapital,
      strategy,
    });
  };

  const formatCurrency = (value) => {
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center justify-center w-10 h-10 bg-orange-600 rounded-lg">
              <BeakerIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Strategy Backtest</h1>
              <p className="text-sm text-gray-500">Test trading strategies with historical data</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Instrument Selection */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-4">
                <BuildingOfficeIcon className="w-4 h-4 text-gray-600" />
                <h2 className="text-sm font-medium text-gray-900">Instrument Selection</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selected Instrument
                  </label>
                  <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                    {(() => {
                      const IconComponent = getInstrumentTypeIcon(
                        popularInstruments.stocks.find(s => s.symbol === selectedSymbol)?.type ||
                        popularInstruments.etfs.find(s => s.symbol === selectedSymbol)?.type ||
                        popularInstruments.crypto.find(s => s.symbol === selectedSymbol)?.type ||
                        popularInstruments.indices.find(s => s.symbol === selectedSymbol)?.type ||
                        'stock'
                      );
                      return <IconComponent className="h-5 w-5 text-gray-400" />;
                    })()}
                    <span className="font-medium">{selectedSymbol}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(popularInstruments).map(([category, instruments]) => (
                    <div key={category} className="space-y-2">
                      <h3 className="text-sm font-medium text-gray-700 capitalize">{category}</h3>
                      <div className="space-y-1">
                        {instruments.slice(0, 4).map((instrument) => {
                          const IconComponent = getInstrumentTypeIcon(instrument.type);
                          return (
                            <button
                              key={instrument.symbol}
                              onClick={() => handleInstrumentSelect(instrument)}
                              className={`w-full text-left p-2 rounded-md text-sm transition-colors ${
                                selectedSymbol === instrument.symbol
                                  ? 'bg-blue-100 text-blue-700 border border-blue-300'
                                  : 'hover:bg-gray-50 border border-transparent'
                              }`}
                            >
                              <div className="flex items-center space-x-2">
                                <IconComponent className="h-4 w-4 text-gray-400" />
                                <span>{instrument.symbol}</span>
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Strategy Selection */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-4">
                <CpuChipIcon className="w-4 h-4 text-gray-600" />
                <h2 className="text-sm font-medium text-gray-900">Strategy Selection</h2>
              </div>
              <div className="space-y-3">
                {strategies.map((strategyOption) => (
                  <button
                    key={strategyOption.id}
                    onClick={() => handleStrategySelect(strategyOption.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      strategy === strategyOption.id
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      <FireIcon className="h-4 w-4 text-gray-500" />
                      <span className="font-medium">{strategyOption.name}</span>
                    </div>
                    <p className="text-xs text-gray-500">{strategyOption.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Backtest Parameters */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-4">
                <ClockIcon className="w-4 h-4 text-gray-600" />
                <h2 className="text-sm font-medium text-gray-900">Backtest Parameters</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label htmlFor="start-date" className="block text-sm font-medium text-gray-700">Start Date</label>
                  <input
                    type="date"
                    id="start-date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label htmlFor="end-date" className="block text-sm font-medium text-gray-700">End Date</label>
                  <input
                    type="date"
                    id="end-date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label htmlFor="initial-capital" className="block text-sm font-medium text-gray-700">Initial Capital</label>
                  <input
                    type="number"
                    id="initial-capital"
                    value={initialCapital}
                    onChange={(e) => setInitialCapital(parseFloat(e.target.value))}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    min="1"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={handleRunBacktest}
              disabled={isBacktesting}
              className="w-full flex items-center justify-center space-x-2 px-4 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isBacktesting ? (
                <>
                  <LoadingSpinner size="sm" color="white" />
                  <span>Running Backtest...</span>
                </>
              ) : (
                <>
                  <PlayIcon className="h-5 w-5" />
                  <span>Run Backtest</span>
                </>
              )}
            </button>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2 space-y-6">
            {isBacktesting && (
              <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-lg text-gray-600">Analyzing historical data...</p>
              </div>
            )}

            {backtestResults && (
              <>
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <div className="flex items-center space-x-2 mb-4">
                    <DocumentChartBarIcon className="w-5 h-5 text-gray-600" />
                    <h2 className="text-lg font-semibold text-gray-900">Backtest Summary</h2>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <p className="text-sm text-blue-800">Total Return</p>
                      <p className="text-xl font-bold text-blue-900">{formatPercentage(backtestResults.total_return)}</p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <p className="text-sm text-green-800">Sharpe Ratio</p>
                      <p className="text-xl font-bold text-green-900">{backtestResults.sharpe_ratio?.toFixed(2) || 'N/A'}</p>
                    </div>
                    <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                      <p className="text-sm text-red-800">Max Drawdown</p>
                      <p className="text-xl font-bold text-red-900">{formatPercentage(backtestResults.max_drawdown)}</p>
                    </div>
                    <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                      <p className="text-sm text-yellow-800">Win Rate</p>
                      <p className="text-xl font-bold text-yellow-900">{formatPercentage(backtestResults.win_rate)}</p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                      <p className="text-sm text-purple-800">Trades Executed</p>
                      <p className="text-xl font-bold text-purple-900">{backtestResults.trades_executed}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <div className="flex items-center space-x-2 mb-4">
                    <ChartBarIcon className="w-5 h-5 text-gray-600" />
                    <h2 className="text-lg font-semibold text-gray-900">Equity Curve</h2>
                  </div>
                  <EquityCurveChart data={backtestResults.equity_curve} height={300} />
                </div>

                {backtestResults.trades && backtestResults.trades.length > 0 && (
                  <div className="bg-white rounded-lg border border-gray-200">
                    <div className="px-6 py-4 border-b border-gray-200">
                      <h3 className="text-lg font-medium text-gray-900">Trade Log</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entry Price</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Exit Price</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P/L</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {backtestResults.trades.map((trade, index) => (
                            <tr key={index}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(trade.date).toLocaleDateString()}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{trade.symbol}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{trade.type}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.shares}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatCurrency(trade.entry_price)}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.exit_price ? formatCurrency(trade.exit_price) : '-'}</td>
                              <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                                trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {trade.pnl ? formatCurrency(trade.pnl) : '-'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Backtest;