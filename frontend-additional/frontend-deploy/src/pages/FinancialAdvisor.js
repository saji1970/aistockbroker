import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { toast } from 'react-hot-toast';
import { API_BASE_URL } from '../services/config';
import { 
  UserIcon, 
  CurrencyDollarIcon, 
  ChartBarIcon, 
  ShieldCheckIcon,
  ClockIcon,
  CogIcon,
  DocumentTextIcon,
  CalculatorIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';

const FinancialAdvisor = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [clientProfile, setClientProfile] = useState({
    age: '',
    income: '',
    net_worth: '',
    risk_tolerance: 'moderate',
    goals: [],
    time_horizon: 'long_term',
    liquidity_needs: '',
    existing_investments: {},
    debt_obligations: {}
  });
  const [financialPlan, setFinancialPlan] = useState(null);

  // Financial planning mutation
  const generatePlanMutation = useMutation(
    async (profileData) => {
      const response = await fetch(`${API_BASE_URL}/api/financial-advisor/generate-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return response.json();
    },
    {
      onSuccess: (data) => {
        setFinancialPlan(data);
        toast.success('Financial plan generated successfully!');
        setActiveTab('plan');
      },
      onError: (error) => {
        console.error('Financial planning error:', error);
        toast.error(`Failed to generate financial plan: ${error.message}`);
      }
    }
  );

  const handleProfileChange = (field, value) => {
    setClientProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleGoalToggle = (goal) => {
    setClientProfile(prev => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter(g => g !== goal)
        : [...prev.goals, goal]
    }));
  };

  const handleGeneratePlan = () => {
    if (!clientProfile.age || !clientProfile.income || !clientProfile.net_worth) {
      toast.error('Please fill in all required fields');
      return;
    }

    const profileData = {
      ...clientProfile,
      age: parseInt(clientProfile.age),
      income: parseFloat(clientProfile.income),
      net_worth: parseFloat(clientProfile.net_worth),
      liquidity_needs: parseFloat(clientProfile.liquidity_needs) || 0
    };

    generatePlanMutation.mutate(profileData);
  };

  const investmentGoals = [
    { key: 'retirement', label: 'Retirement Planning', icon: ClockIcon },
    { key: 'education', label: 'Education Funding', icon: DocumentTextIcon },
    { key: 'home_purchase', label: 'Home Purchase', icon: ShieldCheckIcon },
    { key: 'wealth_building', label: 'Wealth Building', icon: ArrowTrendingUpIcon },
    { key: 'income_generation', label: 'Income Generation', icon: CurrencyDollarIcon },
    { key: 'tax_efficiency', label: 'Tax Efficiency', icon: CalculatorIcon }
  ];

  const riskToleranceOptions = [
    { value: 'conservative', label: 'Conservative', description: 'Lower risk, stable returns' },
    { value: 'moderate', label: 'Moderate', description: 'Balanced risk and return' },
    { value: 'aggressive', label: 'Aggressive', description: 'Higher risk, higher potential returns' }
  ];

  const timeHorizonOptions = [
    { value: 'short_term', label: 'Short Term (1-3 years)', description: 'Preserve capital' },
    { value: 'medium_term', label: 'Medium Term (3-10 years)', description: 'Balanced growth' },
    { value: 'long_term', label: 'Long Term (10+ years)', description: 'Maximum growth potential' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Professional Financial Advisor
          </h1>
          <p className="text-lg text-gray-600">
            Get personalized financial planning and investment advice
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('profile')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'profile'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <UserIcon className="w-5 h-5 inline mr-2" />
                Client Profile
              </button>
              <button
                onClick={() => setActiveTab('plan')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'plan'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
                disabled={!financialPlan}
              >
                <ChartBarIcon className="w-5 h-5 inline mr-2" />
                Financial Plan
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm">
          {activeTab === 'profile' && (
            <div className="p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                Create Your Financial Profile
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Age *
                    </label>
                    <input
                      type="number"
                      value={clientProfile.age}
                      onChange={(e) => handleProfileChange('age', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter your age"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Annual Income *
                    </label>
                    <input
                      type="number"
                      value={clientProfile.income}
                      onChange={(e) => handleProfileChange('income', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter annual income"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Net Worth *
                    </label>
                    <input
                      type="number"
                      value={clientProfile.net_worth}
                      onChange={(e) => handleProfileChange('net_worth', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter net worth"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Liquidity Needs
                    </label>
                    <input
                      type="number"
                      value={clientProfile.liquidity_needs}
                      onChange={(e) => handleProfileChange('liquidity_needs', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Amount needed for short-term expenses"
                    />
                  </div>
                </div>

                {/* Investment Preferences */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-900">Investment Preferences</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Risk Tolerance *
                    </label>
                    <select
                      value={clientProfile.risk_tolerance}
                      onChange={(e) => handleProfileChange('risk_tolerance', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {riskToleranceOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} - {option.description}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time Horizon *
                    </label>
                    <select
                      value={clientProfile.time_horizon}
                      onChange={(e) => handleProfileChange('time_horizon', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {timeHorizonOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label} - {option.description}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Investment Goals
                    </label>
                    <div className="space-y-2">
                      {investmentGoals.map(goal => (
                        <label key={goal.key} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={clientProfile.goals.includes(goal.key)}
                            onChange={() => handleGoalToggle(goal.key)}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <span className="ml-2 text-sm text-gray-700">
                            {goal.label}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Generate Plan Button */}
              <div className="mt-8 text-center">
                <button
                  onClick={handleGeneratePlan}
                  disabled={generatePlanMutation.isLoading}
                  className="bg-blue-600 text-white px-8 py-3 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {generatePlanMutation.isLoading ? (
                    <>
                      <CogIcon className="w-5 h-5 inline mr-2 animate-spin" />
                      Generating Plan...
                    </>
                  ) : (
                    <>
                      <ChartBarIcon className="w-5 h-5 inline mr-2" />
                      Generate Financial Plan
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'plan' && financialPlan && (
            <div className="p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                Your Financial Plan
              </h2>

              {/* Plan Summary */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-medium text-blue-900 mb-2">
                  Plan Summary
                </h3>
                <div className="prose prose-sm text-blue-800">
                  <div dangerouslySetInnerHTML={{ __html: financialPlan.advice_summary.replace(/\n/g, '<br/>') }} />
                </div>
              </div>

              {/* Asset Allocation */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Asset Allocation</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(financialPlan.financial_plan.asset_allocation).map(([asset, allocation]) => (
                    <div key={asset} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-gray-900 capitalize">
                          {asset.replace('_', ' ')}
                        </span>
                        <span className="text-lg font-semibold text-blue-600">
                          {(allocation * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${allocation * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Investment Recommendations */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Investment Recommendations</h3>
                <div className="space-y-4">
                  {financialPlan.financial_plan.investment_recommendations.map((rec, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium text-gray-900">{rec.symbol}</h4>
                          <p className="text-sm text-gray-600">{rec.name}</p>
                        </div>
                        <div className="text-right">
                          <span className="text-lg font-semibold text-blue-600">
                            {rec.allocation_percentage.toFixed(1)}%
                          </span>
                          <p className="text-sm text-gray-600">
                            ${rec.investment_amount.toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{rec.rationale}</p>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">
                          Expected Return: {(rec.expected_return * 100).toFixed(1)}%
                        </span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          rec.risk_level === 'conservative' ? 'bg-green-100 text-green-800' :
                          rec.risk_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {rec.risk_level}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risk Assessment */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Assessment</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Portfolio Metrics</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Volatility:</span>
                        <span className="font-medium">
                          {(financialPlan.financial_plan.risk_assessment.portfolio_volatility * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Expected Return:</span>
                        <span className="font-medium">
                          {(financialPlan.financial_plan.risk_assessment.expected_return * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Sharpe Ratio:</span>
                        <span className="font-medium">
                          {financialPlan.financial_plan.risk_assessment.sharpe_ratio.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Risk Alignment</h4>
                    <p className="text-sm text-gray-700">
                      {financialPlan.financial_plan.risk_assessment.risk_alignment}
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Items */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-yellow-900 mb-2">
                  Next Steps
                </h3>
                <ul className="text-sm text-yellow-800 space-y-1">
                  <li>• Review and approve this financial plan</li>
                  <li>• Set up automatic contributions to recommended investments</li>
                  <li>• Schedule quarterly portfolio reviews</li>
                  <li>• Monitor progress and adjust as needed</li>
                  <li>• Consider consulting with a licensed financial advisor</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinancialAdvisor; 