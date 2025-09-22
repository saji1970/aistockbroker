import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { stockAPI, backtestAPI } from '../services/api';
import EquityCurveChart from '../components/Charts/EquityCurveChart';
import { toast } from 'react-hot-toast';
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
  PlayIcon,
  StopIcon,
  DocumentChartBarIcon,
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

  // Predefined instruments for quick selection
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
      { symbol: 'BND', name: 'Vanguard Total Bond Market ETF', type: 'etf' },
      { symbol: 'IWM', name: 'iShares Russell 2000 ETF', type: 'etf' },
    ],
    crypto: [
      { symbol: 'BTC-USD', name: 'Bitcoin', type: 'crypto' },
      { symbol: 'ETH-USD', name: 'Ethereum', type: 'crypto' },
      { symbol: 'ADA-USD', name: 'Cardano', type: 'crypto' },
      { symbol: 'DOT-USD', name: 'Polkadot', type: 'crypto' },
      { symbol: 'LINK-USD', name: 'Chainlink', type: 'crypto' },
      { symbol: 'UNI-USD', name: 'Uniswap', type: 'crypto' },
    ],
    indices: [
      { symbol: '^GSPC', name: 'S&P 500', type: 'index' },
      { symbol: '^DJI', name: 'Dow Jones Industrial Average', type: 'index' },
      { symbol: '^IXIC', name: 'NASDAQ Composite', type: 'index' },
      { symbol: '^VIX', name: 'CBOE Volatility Index', type: 'index' },
    ]
  };

  const strategies = [
    {
      id: 'sma_crossover',
      name: 'SMA Crossover',
      description: 'Buy when short SMA crosses above long SMA, sell when it crosses below',
      icon: ArrowTrendingUpIcon,
      parameters: [
        { name: 'short_period', label: 'Short SMA Period', type: 'number', default: 20, min: 5, max: 50 },
        { name: 'long_period', label: 'Long SMA Period', type: 'number', default: 50, min: 20, max: 200 }
      ]
    },
    {
      id: 'rsi_strategy',
      name: 'RSI Strategy',
      description: 'Buy when RSI is oversold, sell when overbought',
      icon: ArrowTrendingDownIcon,
      parameters: [
        { name: 'rsi_period', label: 'RSI Period', type: 'number', default: 14, min: 5, max: 30 },
        { name: 'oversold', label: 'Oversold Level', type: 'number', default: 30, min: 10, max: 40 },
        { name: 'overbought', label: 'Overbought Level', type: 'number', default: 70, min: 60, max: 90 }
      ]
    },
    {
      id: 'macd_strategy',
      name: 'MACD Strategy',
      description: 'Buy when MACD crosses above signal line, sell when it crosses below',
      icon: ChartBarIcon,
      parameters: [
        { name: 'fast_period', label: 'Fast EMA Period', type: 'number', default: 12, min: 5, max: 20 },
        { name: 'slow_period', label: 'Slow EMA Period', type: 'number', default: 26, min: 15, max: 50 },
        { name: 'signal_period', label: 'Signal Period', type: 'number', default: 9, min: 5, max: 20 }
      ]
    },
    {
      id: 'bollinger_bands',
      name: 'Bollinger Bands',
      description: 'Buy when price touches lower band, sell when it touches upper band',
      icon: InformationCircleIcon,
      parameters: [
        { name: 'bb_period', label: 'BB Period', type: 'number', default: 20, min: 10, max: 50 },
        { name: 'bb_std', label: 'Standard Deviation', type: 'number', default: 2, min: 1, max: 3, step: 0.1 }
      ]
    },
    {
      id: 'mean_reversion',
      name: 'Mean Reversion',
      description: 'Buy when price is below moving average, sell when above',
      icon: ArrowTrendingUpIcon,
      parameters: [
        { name: 'ma_period', label: 'Moving Average Period', type: 'number', default: 50, min: 20, max: 200 },
        { name: 'deviation', label: 'Deviation Threshold', type: 'number', default: 0.05, min: 0.01, max: 0.2, step: 0.01 }
      ]
    },
    {
      id: 'momentum',
      name: 'Momentum Strategy',
      description: 'Buy when momentum is positive, sell when negative',
      icon: FireIcon,
      parameters: [
        { name: 'momentum_period', label: 'Momentum Period', type: 'number', default: 10, min: 5, max: 30 },
        { name: 'threshold', label: 'Momentum Threshold', type: 'number', default: 0.02, min: 0.01, max: 0.1, step: 0.01 }
      ]
    }
  ];

  const [strategyParams, setStrategyParams] = useState({});

  // Initialize strategy parameters
  React.useEffect(() => {
    const selectedStrategy = strategies.find(s => s.id === strategy);
    if (selectedStrategy) {
      const params = {};
      selectedStrategy.parameters.forEach(param => {
        params[param.name] = param.default;
      });
      setStrategyParams(params);
    }
  }, [strategy]);

  const handleStrategySelect = (strategyId) => {
    setStrategy(strategyId);
  };

  const handleParamChange = (paramName, value) => {
    setStrategyParams(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleInstrumentSelect = (instrument) => {
    setSelectedSymbol(instrument.symbol);
  };

  const runBacktestMutation = useMutation(
    (backtestConfig) => backtestAPI.runBacktest(backtestConfig),
    {
      onSuccess: (data) => {
        setBacktestResults(data);
        setIsRunning(false);
        toast.success('Backtest completed successfully!');
      },
      onError: (error) => {
        setIsRunning(false);
        toast.error('Backtest failed. Please try again.');
        console.error('Backtest error:', error);
      }
    }
  );

  const handleRunBacktest = () => {
    if (!selectedSymbol || !startDate || !endDate || !initialCapital) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsRunning(true);
    const backtestConfig = {
      symbol: selectedSymbol,
      start_date: startDate,
      end_date: endDate,
      initial_capital: parseFloat(initialCapital),
      strategy: strategy,
      parameters: strategyParams
    };

    runBacktestMutation.mutate(backtestConfig);
  };

  const getInstrumentTypeIcon = (type) => {
    switch (type) {
      case 'stock': return BuildingOfficeIcon;
      case 'etf': return DocumentChartBarIcon;
      case 'crypto': return GlobeAltIcon;
      case 'index': return ChartBarIcon;
      default: return InformationCircleIcon;
    }
  };

  const getInstrumentTypeColor = (type) => {
    switch (type) {
      case 'stock': return 'text-blue-600 bg-blue-100';
      case 'etf': return 'text-green-600 bg-green-100';
      case 'crypto': return 'text-orange-600 bg-orange-100';
      case 'index': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Backtest Trading Strategies</h1>
        <p className="text-gray-600">
          Test your trading strategies against historical data to evaluate performance and optimize parameters.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Instrument Selection */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Instrument Selection</h2>
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
                                ? 'bg-primary-100 text-primary-700 border border-primary-300'
                                : 'hover:bg-gray-50 border border-transparent'
                            }`}
                          >
                            <div className="flex items-center space-x-2">
                              <IconComponent className="h-4 w-4" />
                              <span className="font-medium">{instrument.symbol}</span>
                            </div>
                            <div className="text-xs text-gray-500 truncate">{instrument.name}</div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Backtest Configuration */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Backtest Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date Range
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Start Date</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">End Date</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Initial Capital
                </label>
                <input
                  type="number"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(e.target.value)}
                  min="1000"
                  step="1000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </div>

          {/* Strategy Selection */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Trading Strategy</h2>
            <div className="space-y-3">
              {strategies.map((strategyOption) => {
                const IconComponent = strategyOption.icon;
                return (
                  <button
                    key={strategyOption.id}
                    onClick={() => handleStrategySelect(strategyOption.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      strategy === strategyOption.id
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      <IconComponent className="h-4 w-4" />
                      <p className="text-sm font-medium">{strategyOption.name}</p>
                    </div>
                    <p className="text-xs text-gray-500">{strategyOption.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Strategy Parameters */}
          {strategy && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Strategy Parameters</h2>
              <div className="space-y-3">
                {strategies.find(s => s.id === strategy)?.parameters.map((param) => (
                  <div key={param.name}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {param.label}
                    </label>
                    <input
                      type={param.type}
                      value={strategyParams[param.name] || param.default}
                      onChange={(e) => handleParamChange(param.name, parseFloat(e.target.value))}
                      min={param.min}
                      max={param.max}
                      step={param.step || 1}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Run Backtest Button */}
          <div className="card">
            <button
              onClick={handleRunBacktest}
              disabled={isRunning}
              className={`w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
                isRunning
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              {isRunning ? (
                <>
                  <LoadingSpinner size="sm" />
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
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {!backtestResults ? (
            <div className="card">
              <div className="text-center py-12">
                <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Backtest Results</h3>
                <p className="text-gray-500">
                  Configure your strategy and click "Run Backtest" to see results.
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Performance Summary */}
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Total Return</p>
                    <p className={`text-2xl font-bold ${
                      backtestResults.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercentage(backtestResults.total_return)}
                    </p>
                  </div>
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Final Value</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(backtestResults.final_value)}
                    </p>
                  </div>
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Max Drawdown</p>
                    <p className="text-2xl font-bold text-red-600">
                      {formatPercentage(backtestResults.max_drawdown)}
                    </p>
                  </div>
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Sharpe Ratio</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {backtestResults.sharpe_ratio?.toFixed(2) || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Trade Statistics */}
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Trade Statistics</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Total Trades</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {backtestResults.total_trades || 0}
                    </p>
                  </div>
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Win Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {backtestResults.win_rate ? formatPercentage(backtestResults.win_rate) : 'N/A'}
                    </p>
                  </div>
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Avg Win</p>
                    <p className="text-2xl font-bold text-green-600">
                      {backtestResults.avg_win ? formatCurrency(backtestResults.avg_win) : 'N/A'}
                    </p>
                  </div>
                  <div className="metric-card">
                    <p className="text-sm font-medium text-gray-600">Avg Loss</p>
                    <p className="text-2xl font-bold text-red-600">
                      {backtestResults.avg_loss ? formatCurrency(backtestResults.avg_loss) : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Equity Curve Chart */}
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Equity Curve</h2>
                <EquityCurveChart 
                  data={backtestResults.equity_curve} 
                  title={`${selectedSymbol} - ${strategies.find(s => s.id === strategy)?.name}`}
                />
              </div>

              {/* Trade History */}
              {backtestResults.trades && backtestResults.trades.length > 0 && (
                <div className="card">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Trade History</h2>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Date
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Type
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Price
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Quantity
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            P&L
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {backtestResults.trades.slice(0, 10).map((trade, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {new Date(trade.date).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                trade.type === 'buy' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {trade.type.toUpperCase()}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatCurrency(trade.price)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {trade.quantity}
                            </td>
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
  );
};

export default Backtest; 