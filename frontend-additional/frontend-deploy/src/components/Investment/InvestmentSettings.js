import React, { useState } from 'react';
import { Cog6ToothIcon, ShieldCheckIcon, CurrencyDollarIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import { useStore } from '../../store/store';
import { MARKETS } from '../../services/api';

const InvestmentSettings = () => {
  const { investmentSettings, currentMarket, updateInvestmentSettings, setCurrentMarket } = useStore();
  const [isOpen, setIsOpen] = useState(false);

  const riskToleranceOptions = [
    { value: 'conservative', label: 'Conservative', description: 'Low risk, stable returns', color: 'text-green-600' },
    { value: 'moderate', label: 'Moderate', description: 'Balanced risk and return', color: 'text-yellow-600' },
    { value: 'aggressive', label: 'Aggressive', description: 'High risk, high potential returns', color: 'text-red-600' },
  ];

  const currencyOptions = [
    { code: 'USD', name: 'US Dollar', flag: '🇺🇸' },
    { code: 'EUR', name: 'Euro', flag: '🇪🇺' },
    { code: 'GBP', name: 'British Pound', flag: '🇬🇧' },
    { code: 'CAD', name: 'Canadian Dollar', flag: '🇨🇦' },
    { code: 'AUD', name: 'Australian Dollar', flag: '🇦🇺' },
    { code: 'JPY', name: 'Japanese Yen', flag: '🇯🇵' },
    { code: 'INR', name: 'Indian Rupee', flag: '🇮🇳' },
    { code: 'BRL', name: 'Brazilian Real', flag: '🇧🇷' },
  ];

  const handleSettingChange = (key, value) => {
    updateInvestmentSettings({ [key]: value });
  };

  const handleCurrencyToggle = (currency) => {
    const currentCurrencies = investmentSettings.preferredCurrencies;
    const newCurrencies = currentCurrencies.includes(currency)
      ? currentCurrencies.filter(c => c !== currency)
      : [...currentCurrencies, currency];
    
    handleSettingChange('preferredCurrencies', newCurrencies);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div 
        className="p-4 cursor-pointer flex items-center justify-between"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center space-x-3">
          <Cog6ToothIcon className="w-5 h-5 text-gray-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Investment Settings</h3>
            <p className="text-sm text-gray-600">Configure your investment preferences</p>
          </div>
        </div>
        <div className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}>
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Content */}
      {isOpen && (
        <div className="px-4 pb-4 space-y-6">
          {/* Market Selection */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
              <ChartBarIcon className="w-4 h-4 mr-2" />
              Primary Market
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {Object.entries(MARKETS).map(([code, market]) => (
                <button
                  key={code}
                  onClick={() => setCurrentMarket(code)}
                  className={`p-3 text-xs rounded-md border transition-colors ${
                    currentMarket === code
                      ? 'bg-blue-50 border-blue-200 text-blue-700 font-medium'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="font-medium">{market.name}</div>
                  <div className="text-gray-500">{market.currency}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Risk Tolerance */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
              <ShieldCheckIcon className="w-4 h-4 mr-2" />
              Risk Tolerance
            </h4>
            <div className="space-y-2">
              {riskToleranceOptions.map((option) => (
                <label key={option.value} className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="riskTolerance"
                    value={option.value}
                    checked={investmentSettings.riskTolerance === option.value}
                    onChange={(e) => handleSettingChange('riskTolerance', e.target.value)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <div className="flex-1">
                    <div className={`font-medium ${option.color}`}>{option.label}</div>
                    <div className="text-sm text-gray-600">{option.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Investment Amount */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
              <CurrencyDollarIcon className="w-4 h-4 mr-2" />
              Investment Amount
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 mb-1">Total Investment</label>
                <input
                  type="number"
                  value={investmentSettings.investmentAmount}
                  onChange={(e) => handleSettingChange('investmentAmount', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="10000"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">Max Position Size (%)</label>
                <input
                  type="number"
                  value={investmentSettings.maxPositionSize}
                  onChange={(e) => handleSettingChange('maxPositionSize', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="25"
                  min="1"
                  max="100"
                />
              </div>
            </div>
          </div>

          {/* Stop Loss & Take Profit */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Risk Management</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 mb-1">Stop Loss (%)</label>
                <input
                  type="number"
                  value={investmentSettings.stopLossPercentage}
                  onChange={(e) => handleSettingChange('stopLossPercentage', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="10"
                  min="1"
                  max="50"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">Take Profit (%)</label>
                <input
                  type="number"
                  value={investmentSettings.takeProfitPercentage}
                  onChange={(e) => handleSettingChange('takeProfitPercentage', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="20"
                  min="1"
                  max="100"
                />
              </div>
            </div>
          </div>

          {/* Preferred Currencies */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Preferred Currencies</h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {currencyOptions.map((currency) => (
                <label key={currency.code} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={investmentSettings.preferredCurrencies.includes(currency.code)}
                    onChange={() => handleCurrencyToggle(currency.code)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm">
                    {currency.flag} {currency.code}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Diversification */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Diversification</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 mb-1">Target Assets</label>
                <input
                  type="number"
                  value={investmentSettings.diversificationTarget}
                  onChange={(e) => handleSettingChange('diversificationTarget', parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="8"
                  min="1"
                  max="20"
                />
              </div>
              <div className="flex items-center space-x-3">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={investmentSettings.autoRebalance}
                    onChange={(e) => handleSettingChange('autoRebalance', e.target.checked)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Auto Rebalance</span>
                </label>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Current Settings Summary</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <div>Market: {MARKETS[currentMarket]?.name} ({MARKETS[currentMarket]?.currency})</div>
              <div>Risk: {investmentSettings.riskTolerance.charAt(0).toUpperCase() + investmentSettings.riskTolerance.slice(1)}</div>
              <div>Investment: ${investmentSettings.investmentAmount.toLocaleString()}</div>
              <div>Max Position: {investmentSettings.maxPositionSize}%</div>
              <div>Stop Loss: {investmentSettings.stopLossPercentage}% | Take Profit: {investmentSettings.takeProfitPercentage}%</div>
              <div>Currencies: {investmentSettings.preferredCurrencies.join(', ')}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvestmentSettings; 