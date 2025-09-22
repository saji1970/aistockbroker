import React, { useState, useEffect } from 'react';
import { CurrencyDollarIcon, ArrowRightIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import { useStore } from '../../store/store';
import { MARKETS } from '../../services/api';

const CurrencySwap = () => {
  const { currentMarket } = useStore();
  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('EUR');
  const [amount, setAmount] = useState(1000);
  const [exchangeRate, setExchangeRate] = useState(0);
  const [swapHistory, setSwapHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Currency pairs with mock exchange rates
  const currencyPairs = {
    'USD-EUR': 0.85,
    'USD-GBP': 0.73,
    'USD-CAD': 1.25,
    'USD-AUD': 1.35,
    'USD-JPY': 110.5,
    'USD-INR': 74.5,
    'USD-BRL': 5.2,
    'EUR-USD': 1.18,
    'EUR-GBP': 0.86,
    'EUR-CAD': 1.47,
    'EUR-AUD': 1.59,
    'EUR-JPY': 130.0,
    'EUR-INR': 87.6,
    'EUR-BRL': 6.12,
    'GBP-USD': 1.37,
    'GBP-EUR': 1.16,
    'GBP-CAD': 1.71,
    'GBP-AUD': 1.85,
    'GBP-JPY': 151.4,
    'GBP-INR': 101.8,
    'GBP-BRL': 7.12,
    'CAD-USD': 0.80,
    'CAD-EUR': 0.68,
    'CAD-GBP': 0.58,
    'CAD-AUD': 1.08,
    'CAD-JPY': 88.4,
    'CAD-INR': 59.6,
    'CAD-BRL': 4.16,
    'AUD-USD': 0.74,
    'AUD-EUR': 0.63,
    'AUD-GBP': 0.54,
    'AUD-CAD': 0.93,
    'AUD-JPY': 81.9,
    'AUD-INR': 55.2,
    'AUD-BRL': 3.85,
    'JPY-USD': 0.009,
    'JPY-EUR': 0.0077,
    'JPY-GBP': 0.0066,
    'JPY-CAD': 0.0113,
    'JPY-AUD': 0.0122,
    'JPY-INR': 0.674,
    'JPY-BRL': 0.047,
    'INR-USD': 0.0134,
    'INR-EUR': 0.0114,
    'INR-GBP': 0.0098,
    'INR-CAD': 0.0168,
    'INR-AUD': 0.0181,
    'INR-JPY': 1.48,
    'INR-BRL': 0.0698,
    'BRL-USD': 0.192,
    'BRL-EUR': 0.163,
    'BRL-GBP': 0.140,
    'BRL-CAD': 0.240,
    'BRL-AUD': 0.260,
    'BRL-JPY': 21.3,
    'BRL-INR': 14.3
  };

  const currencies = [
    { code: 'USD', name: 'US Dollar', flag: '🇺🇸' },
    { code: 'EUR', name: 'Euro', flag: '🇪🇺' },
    { code: 'GBP', name: 'British Pound', flag: '🇬🇧' },
    { code: 'CAD', name: 'Canadian Dollar', flag: '🇨🇦' },
    { code: 'AUD', name: 'Australian Dollar', flag: '🇦🇺' },
    { code: 'JPY', name: 'Japanese Yen', flag: '🇯🇵' },
    { code: 'INR', name: 'Indian Rupee', flag: '🇮🇳' },
    { code: 'BRL', name: 'Brazilian Real', flag: '🇧🇷' }
  ];

  useEffect(() => {
    // Set default currencies based on current market
    const marketInfo = MARKETS[currentMarket];
    if (marketInfo) {
      setFromCurrency('USD');
      setToCurrency(marketInfo.currency);
    }
  }, [currentMarket]);

  useEffect(() => {
    // Calculate exchange rate
    const pair = `${fromCurrency}-${toCurrency}`;
    const rate = currencyPairs[pair] || 1;
    setExchangeRate(rate);
  }, [fromCurrency, toCurrency]);

  const handleSwap = () => {
    if (amount <= 0) return;

    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const convertedAmount = amount * exchangeRate;
      const swap = {
        id: Date.now(),
        fromCurrency,
        toCurrency,
        amount,
        convertedAmount,
        exchangeRate,
        timestamp: new Date(),
        status: 'completed'
      };

      setSwapHistory(prev => [swap, ...prev.slice(0, 9)]);
      setIsLoading(false);
    }, 1000);
  };

  const getConvertedAmount = () => {
    return (amount * exchangeRate).toFixed(2);
  };

  const getRateChange = () => {
    // Mock rate change (positive or negative)
    return (Math.random() - 0.5) * 0.02; // ±2% change
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 sm:p-6">
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900">Currency Swap</h3>
        <ChartBarIcon className="w-4 h-5 text-gray-400" />
      </div>

      {/* Currency Swap Form */}
      <div className="space-y-3 sm:space-y-4">
        {/* From Currency */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            From Currency
          </label>
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            <select
              value={fromCurrency}
              onChange={(e) => setFromCurrency(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {currencies.map(currency => (
                <option key={currency.code} value={currency.code}>
                  {currency.flag} {currency.code} - {currency.name}
                </option>
              ))}
            </select>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              placeholder="Amount"
            />
          </div>
        </div>

        {/* Swap Arrow */}
        <div className="flex justify-center">
          <div className="bg-gray-100 p-2 rounded-full">
            <ArrowRightIcon className="w-4 h-4 sm:w-5 sm:h-5 text-gray-600 transform rotate-90" />
          </div>
        </div>

        {/* To Currency */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            To Currency
          </label>
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            <select
              value={toCurrency}
              onChange={(e) => setToCurrency(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {currencies.map(currency => (
                <option key={currency.code} value={currency.code}>
                  {currency.flag} {currency.code} - {currency.name}
                </option>
              ))}
            </select>
            <div className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm">
              {getConvertedAmount()} {toCurrency}
            </div>
          </div>
        </div>

        {/* Exchange Rate Info */}
        <div className="bg-blue-50 p-3 sm:p-4 rounded-lg">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
            <div>
              <p className="text-sm font-medium text-blue-900">Exchange Rate</p>
              <p className="text-base sm:text-lg font-bold text-blue-900">
                1 {fromCurrency} = {exchangeRate.toFixed(4)} {toCurrency}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-blue-600">
                {getRateChange() > 0 ? '+' : ''}{getRateChange().toFixed(2)}%
              </p>
              <p className="text-xs text-blue-500">24h change</p>
            </div>
          </div>
        </div>

        {/* Swap Button */}
        <button
          onClick={handleSwap}
          disabled={isLoading || amount <= 0}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2 text-sm sm:text-base"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <CurrencyDollarIcon className="w-4 h-4 sm:w-5 sm:h-5" />
              <span>Execute Swap</span>
            </>
          )}
        </button>
      </div>

      {/* Swap History */}
      {swapHistory.length > 0 && (
        <div className="mt-4 sm:mt-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Recent Swaps</h4>
          <div className="space-y-2">
            {swapHistory.map(swap => (
              <div key={swap.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <div className="text-xs sm:text-sm">
                    <span className="font-medium">{swap.amount} {swap.fromCurrency}</span>
                    <span className="text-gray-500 mx-1 sm:mx-2">→</span>
                    <span className="font-medium">{swap.convertedAmount} {swap.toCurrency}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {swap.timestamp.toLocaleTimeString()}
                  </p>
                  <p className="text-xs text-green-600 font-medium">
                    {swap.status}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CurrencySwap; 