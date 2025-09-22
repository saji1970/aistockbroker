import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { predictionAPI, portfolioAPI } from '../services/api';
import { toast } from 'react-hot-toast';
import { 
  SparklesIcon, 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ArrowTrendingUpIcon,
  LightBulbIcon,
  ShieldCheckIcon,
  ClockIcon,
  CalculatorIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/UI/LoadingSpinner';

const AIFeatures = () => {
  const [selectedFeature, setSelectedFeature] = useState('prediction');
  const [initialInvestment, setInitialInvestment] = useState(10000);
  const [riskTolerance, setRiskTolerance] = useState('moderate');
  const [timeHorizon, setTimeHorizon] = useState(5);

  // AI Prediction
  const { data: prediction, isLoading: predictionLoading } = useQuery(
    ['prediction', 'AAPL'],
    () => predictionAPI.getPrediction('AAPL'),
    { enabled: selectedFeature === 'prediction' }
  );

  // Sensitivity Analysis
  const { data: sensitivity, isLoading: sensitivityLoading } = useQuery(
    ['sensitivity', 'AAPL'],
    () => predictionAPI.getSensitivityAnalysis('AAPL'),
    { enabled: selectedFeature === 'sensitivity' }
  );

  // Smart Recommendations
  const recommendationsMutation = useMutation(
    () => predictionAPI.getSmartRecommendations('AAPL'),
    {
      onSuccess: (data) => {
        toast.success('Smart recommendations generated!');
      },
      onError: (error) => {
        toast.error('Failed to generate recommendations');
      }
    }
  );

  // Portfolio Growth
  const portfolioGrowthMutation = useMutation(
    (data) => portfolioAPI.getPortfolioGrowth(data),
    {
      onSuccess: (data) => {
        toast.success('Portfolio growth analysis completed!');
      },
      onError: (error) => {
        toast.error('Failed to analyze portfolio growth');
      }
    }
  );

  // Money Growth Strategies
  const moneyGrowthMutation = useMutation(
    (data) => predictionAPI.getMoneyGrowthStrategies(data),
    {
      onSuccess: (data) => {
        toast.success('Money growth strategies generated!');
      },
      onError: (error) => {
        toast.error('Failed to generate money growth strategies');
      }
    }
  );

  const features = [
    {
      id: 'prediction',
      name: 'AI Prediction',
      description: 'Get AI-powered stock price predictions',
      icon: SparklesIcon,
      color: 'bg-blue-500'
    },
    {
      id: 'sensitivity',
      name: 'Sensitivity Analysis',
      description: 'Analyze how different factors affect stock performance',
      icon: ChartBarIcon,
      color: 'bg-green-500'
    },
    {
      id: 'recommendations',
      name: 'Smart Recommendations',
      description: 'Get AI-generated buy/sell recommendations',
      icon: LightBulbIcon,
      color: 'bg-yellow-500'
    },
    {
      id: 'portfolio-growth',
      name: 'Portfolio Growth',
      description: 'Analyze potential portfolio growth scenarios',
      icon: ArrowTrendingUpIcon,
      color: 'bg-purple-500'
    },
    {
      id: 'money-growth',
      name: 'Money Growth Strategies',
      description: 'Generate investment strategies for wealth building',
      icon: CurrencyDollarIcon,
      color: 'bg-red-500'
    }
  ];

  const handleGenerateRecommendations = () => {
    recommendationsMutation.mutate();
  };

  const handleAnalyzePortfolioGrowth = () => {
    portfolioGrowthMutation.mutate({
      symbols: ['AAPL', 'MSFT', 'GOOGL'],
      initialInvestment,
      timeHorizon
    });
  };

  const handleGenerateMoneyGrowthStrategies = () => {
    moneyGrowthMutation.mutate({
      initialInvestment,
      riskTolerance,
      timeHorizon
    });
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Features</h1>
        <p className="text-gray-600">Leverage AI for advanced stock analysis and predictions</p>
      </div>

      {/* Feature Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((feature) => (
          <button
            key={feature.id}
            onClick={() => setSelectedFeature(feature.id)}
            className={`p-4 rounded-lg border-2 transition-all ${
              selectedFeature === feature.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg ${feature.color} bg-opacity-10`}>
                <feature.icon className={`w-6 h-6 ${feature.color.replace('bg-', 'text-')}`} />
              </div>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900">{feature.name}</h3>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Feature Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {selectedFeature === 'prediction' && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Prediction</h2>
            {predictionLoading ? (
              <LoadingSpinner />
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900">Prediction</h3>
                    <p className="text-2xl font-bold text-blue-600">
                      {prediction?.prediction || 'N/A'}
                    </p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900">Confidence</h3>
                    <p className="text-2xl font-bold text-green-600">
                      {prediction?.confidence ? `${(prediction.confidence * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Analysis</h3>
                  <p className="text-gray-700">{prediction?.analysis || 'No analysis available'}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {selectedFeature === 'sensitivity' && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Sensitivity Analysis</h2>
            {sensitivityLoading ? (
              <LoadingSpinner />
            ) : (
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Scenarios</h3>
                  <div className="space-y-2">
                    {sensitivity?.scenarios?.map((scenario, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-gray-700">{scenario.name}</span>
                        <span className="font-medium text-gray-900">{scenario.impact}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Risk Metrics</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-gray-600">VaR (95%)</span>
                      <p className="font-medium text-gray-900">{sensitivity?.risk_metrics?.var || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Sharpe Ratio</span>
                      <p className="font-medium text-gray-900">{sensitivity?.risk_metrics?.sharpe_ratio || 'N/A'}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {selectedFeature === 'recommendations' && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Smart Recommendations</h2>
            <div className="space-y-4">
              <button
                onClick={handleGenerateRecommendations}
                disabled={recommendationsMutation.isLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {recommendationsMutation.isLoading ? 'Generating...' : 'Generate Recommendations'}
              </button>
              
              {recommendationsMutation.data && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Recommendations</h3>
                  <div className="space-y-2">
                    {recommendationsMutation.data.recommendations?.map((rec, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <ShieldCheckIcon className="w-4 h-4 text-green-500" />
                        <span className="text-gray-700">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {selectedFeature === 'portfolio-growth' && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Growth Analysis</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Initial Investment ($)
                  </label>
                  <input
                    type="number"
                    value={initialInvestment}
                    onChange={(e) => setInitialInvestment(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Time Horizon (Years)
                  </label>
                  <input
                    type="number"
                    value={timeHorizon}
                    onChange={(e) => setTimeHorizon(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    onClick={handleAnalyzePortfolioGrowth}
                    disabled={portfolioGrowthMutation.isLoading}
                    className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                  >
                    {portfolioGrowthMutation.isLoading ? 'Analyzing...' : 'Analyze Growth'}
                  </button>
                </div>
              </div>
              
              {portfolioGrowthMutation.data && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Growth Projection</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-gray-600">Projected Value</span>
                      <p className="text-xl font-bold text-purple-600">
                        ${portfolioGrowthMutation.data.projected_value?.toLocaleString() || 'N/A'}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Total Return</span>
                      <p className="text-xl font-bold text-green-600">
                        {portfolioGrowthMutation.data.total_return?.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {selectedFeature === 'money-growth' && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Money Growth Strategies</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Initial Investment ($)
                  </label>
                  <input
                    type="number"
                    value={initialInvestment}
                    onChange={(e) => setInitialInvestment(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Risk Tolerance
                  </label>
                  <select
                    value={riskTolerance}
                    onChange={(e) => setRiskTolerance(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="conservative">Conservative</option>
                    <option value="moderate">Moderate</option>
                    <option value="aggressive">Aggressive</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Time Horizon (Years)
                  </label>
                  <input
                    type="number"
                    value={timeHorizon}
                    onChange={(e) => setTimeHorizon(Number(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <button
                onClick={handleGenerateMoneyGrowthStrategies}
                disabled={moneyGrowthMutation.isLoading}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {moneyGrowthMutation.isLoading ? 'Generating...' : 'Generate Strategies'}
              </button>
              
              {moneyGrowthMutation.data && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Investment Strategies</h3>
                  <div className="space-y-3">
                    {moneyGrowthMutation.data.strategies?.map((strategy, index) => (
                      <div key={index} className="border-l-4 border-red-500 pl-4">
                        <h4 className="font-medium text-gray-900">{strategy.name}</h4>
                        <p className="text-sm text-gray-600">{strategy.description}</p>
                        <div className="mt-2 flex items-center space-x-4 text-sm">
                          <span className="text-gray-600">Expected Return: {strategy.expected_return}</span>
                          <span className="text-gray-600">Risk Level: {strategy.risk_level}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIFeatures; 