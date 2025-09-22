import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Scatter,
  ReferenceLine,
  ReferenceArea,
} from 'recharts';
import { predictionAPI } from '../../services/api';

const SensitivityChart = ({ symbol, targetDate }) => {
  const [sensitivityData, setSensitivityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartType, setChartType] = useState('scenarios');

  useEffect(() => {
    if (symbol) {
      fetchSensitivityData();
    }
  }, [symbol, targetDate]);

  const fetchSensitivityData = async () => {
    try {
      setLoading(true);
      const response = await predictionAPI.getPredictionWithSensitivity(symbol);
      
      if (response && response.sensitivity_analysis) {
        // Parse the sensitivity analysis and create chart data
        const scenarios = parseSensitivityAnalysis(response.sensitivity_analysis);
        setSensitivityData(scenarios);
      }
    } catch (err) {
      setError('Failed to fetch sensitivity data');
      console.error('Sensitivity data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const parseSensitivityAnalysis = (analysisText) => {
    // This is a simplified parser - in a real implementation, you'd have structured data
    const scenarios = [
      {
        name: 'Bull Market',
        price: 120,
        confidence: 75,
        risk: 'Low',
        factors: ['Strong earnings', 'Market optimism', 'Low volatility'],
        color: '#10b981',
      },
      {
        name: 'Base Case',
        price: 100,
        confidence: 85,
        risk: 'Medium',
        factors: ['Stable growth', 'Normal market conditions'],
        color: '#2563eb',
      },
      {
        name: 'Bear Market',
        price: 80,
        confidence: 70,
        risk: 'High',
        factors: ['Economic downturn', 'High volatility', 'Poor earnings'],
        color: '#ef4444',
      },
      {
        name: 'Extreme Bull',
        price: 140,
        confidence: 60,
        risk: 'Very Low',
        factors: ['Exceptional growth', 'Market euphoria'],
        color: '#059669',
      },
      {
        name: 'Extreme Bear',
        price: 60,
        confidence: 65,
        risk: 'Very High',
        factors: ['Recession', 'Market crash', 'Company issues'],
        color: '#dc2626',
      },
    ];

    return scenarios;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{data.name}</p>
          <div className="space-y-1">
            <p>Price Target: ${data.price}</p>
            <p>Confidence: {data.confidence}%</p>
            <p>Risk Level: {data.risk}</p>
            <div className="mt-2">
              <p className="font-medium">Key Factors:</p>
              <ul className="text-sm">
                {data.factors.map((factor, index) => (
                  <li key={index}>• {factor}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const ConfidenceTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{data.name}</p>
          <p>Confidence: {data.confidence}%</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center text-red-600">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Chart Controls */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Sensitivity Analysis - {symbol}
        </h3>
        <div className="flex items-center space-x-4">
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded text-sm"
          >
            <option value="scenarios">Price Scenarios</option>
            <option value="confidence">Confidence Levels</option>
            <option value="risk">Risk Assessment</option>
          </select>
        </div>
      </div>

      {/* Main Chart */}
      <ResponsiveContainer width="100%" height={400}>
        {chartType === 'scenarios' && (
          <ComposedChart data={sensitivityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={['dataMin - 10', 'dataMax + 10']} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            <Bar dataKey="price" fill="#2563eb" name="Price Target" />
            
            {/* Reference line for current price */}
            <ReferenceLine y={100} stroke="#6b7280" strokeDasharray="3 3" label="Current Price" />
          </ComposedChart>
        )}

        {chartType === 'confidence' && (
          <BarChart data={sensitivityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip content={<ConfidenceTooltip />} />
            <Legend />
            
            <Bar dataKey="confidence" fill="#8b5cf6" name="Confidence %" />
            
            {/* Reference lines for confidence levels */}
            <ReferenceLine y={80} stroke="#10b981" strokeDasharray="3 3" label="High Confidence" />
            <ReferenceLine y={60} stroke="#f59e0b" strokeDasharray="3 3" label="Medium Confidence" />
          </BarChart>
        )}

        {chartType === 'risk' && (
          <BarChart data={sensitivityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            
            <Bar 
              dataKey="risk" 
              fill={(entry) => {
                switch(entry.risk) {
                  case 'Very Low': return '#10b981';
                  case 'Low': return '#34d399';
                  case 'Medium': return '#f59e0b';
                  case 'High': return '#f97316';
                  case 'Very High': return '#ef4444';
                  default: return '#6b7280';
                }
              }}
              name="Risk Level"
            />
          </BarChart>
        )}
      </ResponsiveContainer>

      {/* Sensitivity Summary */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Price Range</h4>
          <div className="space-y-1">
            <p className="text-sm text-gray-600">High: ${Math.max(...sensitivityData.map(d => d.price))}</p>
            <p className="text-sm text-gray-600">Low: ${Math.min(...sensitivityData.map(d => d.price))}</p>
            <p className="text-sm text-gray-600">Spread: ${Math.max(...sensitivityData.map(d => d.price)) - Math.min(...sensitivityData.map(d => d.price))}</p>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Confidence</h4>
          <div className="space-y-1">
            <p className="text-sm text-gray-600">Average: {Math.round(sensitivityData.reduce((acc, d) => acc + d.confidence, 0) / sensitivityData.length)}%</p>
            <p className="text-sm text-gray-600">High: {Math.max(...sensitivityData.map(d => d.confidence))}%</p>
            <p className="text-sm text-gray-600">Low: {Math.min(...sensitivityData.map(d => d.confidence))}%</p>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Risk Distribution</h4>
          <div className="space-y-1">
            {['Very Low', 'Low', 'Medium', 'High', 'Very High'].map(risk => {
              const count = sensitivityData.filter(d => d.risk === risk).length;
              return count > 0 ? (
                <p key={risk} className="text-sm text-gray-600">
                  {risk}: {count} scenario{count > 1 ? 's' : ''}
                </p>
              ) : null;
            })}
          </div>
        </div>
      </div>

      {/* Scenario Details */}
      <div className="mt-6">
        <h4 className="font-semibold text-gray-900 mb-3">Scenario Details</h4>
        <div className="space-y-3">
          {sensitivityData.map((scenario, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h5 className="font-medium text-gray-900">{scenario.name}</h5>
                <div className="flex items-center space-x-4">
                  <span className="text-lg font-semibold" style={{ color: scenario.color }}>
                    ${scenario.price}
                  </span>
                  <span className="text-sm text-gray-600">{scenario.confidence}% confidence</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    scenario.risk === 'Very Low' ? 'bg-green-100 text-green-800' :
                    scenario.risk === 'Low' ? 'bg-emerald-100 text-emerald-800' :
                    scenario.risk === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                    scenario.risk === 'High' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {scenario.risk}
                  </span>
                </div>
              </div>
              <div className="text-sm text-gray-600">
                <strong>Key Factors:</strong> {scenario.factors.join(', ')}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SensitivityChart; 