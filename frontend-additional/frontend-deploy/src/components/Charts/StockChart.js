import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
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
  ReferenceArea,
  ReferenceLine,
} from 'recharts';
import { stockAPI } from '../../services/api';

const StockChart = ({ symbol, period = '1y', interval = '1d', showVolume = true, showIndicators = true }) => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartType, setChartType] = useState('candlestick');
  const [indicators, setIndicators] = useState({
    sma: true,
    ema: true,
    bollinger: false,
    rsi: false,
    macd: false,
  });

  useEffect(() => {
    fetchChartData();
  }, [symbol, period, interval]);

  const fetchChartData = async () => {
    try {
      setLoading(true);
      const response = await stockAPI.getStockData(symbol, period);
      
      if (response && response.data) {
        const formattedData = response.data.map((item, index) => ({
          date: new Date(item.Date || item.date).toLocaleDateString(),
          timestamp: new Date(item.Date || item.date).getTime(),
          open: parseFloat(item.Open),
          high: parseFloat(item.High),
          low: parseFloat(item.Low),
          close: parseFloat(item.Close),
          volume: parseInt(item.Volume) || 0,
          sma20: calculateSMA(response.data, 20, index),
          ema12: calculateEMA(response.data, 12, index),
          bollingerUpper: calculateBollingerBands(response.data, 20, 2, index).upper,
          bollingerLower: calculateBollingerBands(response.data, 20, 2, index).lower,
          rsi: calculateRSI(response.data, 14, index),
          macd: calculateMACD(response.data, index),
        }));
        
        setChartData(formattedData);
      }
    } catch (err) {
      setError('Failed to fetch chart data');
      console.error('Chart data error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Technical Indicators Calculations
  const calculateSMA = (data, period, currentIndex) => {
    if (currentIndex < period - 1) return null;
    const sum = data
      .slice(currentIndex - period + 1, currentIndex + 1)
      .reduce((acc, item) => acc + parseFloat(item.Close), 0);
    return sum / period;
  };

  const calculateEMA = (data, period, currentIndex) => {
    if (currentIndex < period - 1) return null;
    const multiplier = 2 / (period + 1);
    let ema = parseFloat(data[0].Close);
    
    for (let i = 1; i <= currentIndex; i++) {
      ema = (parseFloat(data[i].Close) * multiplier) + (ema * (1 - multiplier));
    }
    return ema;
  };

  const calculateBollingerBands = (data, period, stdDev, currentIndex) => {
    if (currentIndex < period - 1) return { upper: null, lower: null };
    
    const sma = calculateSMA(data, period, currentIndex);
    const prices = data
      .slice(currentIndex - period + 1, currentIndex + 1)
      .map(item => parseFloat(item.Close));
    
    const variance = prices.reduce((acc, price) => acc + Math.pow(price - sma, 2), 0) / period;
    const standardDeviation = Math.sqrt(variance);
    
    return {
      upper: sma + (standardDeviation * stdDev),
      lower: sma - (standardDeviation * stdDev),
    };
  };

  const calculateRSI = (data, period, currentIndex) => {
    if (currentIndex < period) return null;
    
    let gains = 0;
    let losses = 0;
    
    for (let i = currentIndex - period + 1; i <= currentIndex; i++) {
      const change = parseFloat(data[i].Close) - parseFloat(data[i - 1].Close);
      if (change > 0) {
        gains += change;
      } else {
        losses += Math.abs(change);
      }
    }
    
    const avgGain = gains / period;
    const avgLoss = losses / period;
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  };

  const calculateMACD = (data, currentIndex) => {
    if (currentIndex < 26) return null;
    
    const ema12 = calculateEMA(data, 12, currentIndex);
    const ema26 = calculateEMA(data, 26, currentIndex);
    return ema12 - ema26;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          <div className="space-y-1">
            <p>Open: ${data.open?.toFixed(2)}</p>
            <p>High: ${data.high?.toFixed(2)}</p>
            <p>Low: ${data.low?.toFixed(2)}</p>
            <p>Close: ${data.close?.toFixed(2)}</p>
            {data.volume && <p>Volume: {data.volume.toLocaleString()}</p>}
            {data.sma20 && <p>SMA(20): ${data.sma20.toFixed(2)}</p>}
            {data.ema12 && <p>EMA(12): ${data.ema12.toFixed(2)}</p>}
            {data.rsi && <p>RSI: {data.rsi.toFixed(2)}</p>}
          </div>
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
          {symbol} Chart ({period})
        </h3>
        <div className="flex items-center space-x-4">
          {/* Chart Type Selector */}
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded text-sm"
          >
            <option value="candlestick">Candlestick</option>
            <option value="line">Line</option>
            <option value="area">Area</option>
            <option value="bar">Bar</option>
          </select>
          
          {/* Indicator Toggles */}
          <div className="flex items-center space-x-2">
            <label className="flex items-center text-sm">
              <input
                type="checkbox"
                checked={indicators.sma}
                onChange={(e) => setIndicators({ ...indicators, sma: e.target.checked })}
                className="mr-1"
              />
              SMA
            </label>
            <label className="flex items-center text-sm">
              <input
                type="checkbox"
                checked={indicators.ema}
                onChange={(e) => setIndicators({ ...indicators, ema: e.target.checked })}
                className="mr-1"
              />
              EMA
            </label>
            <label className="flex items-center text-sm">
              <input
                type="checkbox"
                checked={indicators.bollinger}
                onChange={(e) => setIndicators({ ...indicators, bollinger: e.target.checked })}
                className="mr-1"
              />
              BB
            </label>
          </div>
        </div>
      </div>

      {/* Main Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={['dataMin - 1', 'dataMax + 1']}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Price Chart */}
          {chartType === 'candlestick' && (
            <>
              {/* Candlestick representation using bars */}
              <Bar dataKey="high" fill="transparent" stroke="none" />
              <Bar dataKey="low" fill="transparent" stroke="none" />
              <Bar dataKey="close" fill="transparent" stroke="none" />
              <Bar dataKey="open" fill="transparent" stroke="none" />
              
              {/* Line chart for close prices */}
              <Line
                type="monotone"
                dataKey="close"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                name="Close"
              />
            </>
          )}

          {chartType === 'line' && (
            <Line
              type="monotone"
              dataKey="close"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              name="Close"
            />
          )}

          {chartType === 'area' && (
            <Area
              type="monotone"
              dataKey="close"
              stroke="#2563eb"
              fill="#2563eb"
              fillOpacity={0.1}
              name="Close"
            />
          )}

          {chartType === 'bar' && (
            <Bar dataKey="close" fill="#2563eb" name="Close" />
          )}

          {/* Technical Indicators */}
          {indicators.sma && (
            <Line
              type="monotone"
              dataKey="sma20"
              stroke="#f59e0b"
              strokeWidth={1}
              dot={false}
              name="SMA(20)"
            />
          )}

          {indicators.ema && (
            <Line
              type="monotone"
              dataKey="ema12"
              stroke="#10b981"
              strokeWidth={1}
              dot={false}
              name="EMA(12)"
            />
          )}

          {indicators.bollinger && (
            <>
              <Line
                type="monotone"
                dataKey="bollingerUpper"
                stroke="#ef4444"
                strokeWidth={1}
                dot={false}
                name="BB Upper"
              />
              <Line
                type="monotone"
                dataKey="bollingerLower"
                stroke="#ef4444"
                strokeWidth={1}
                dot={false}
                name="BB Lower"
              />
            </>
          )}

          {/* Reference Lines */}
          <ReferenceLine y={0} stroke="#d1d5db" />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Volume Chart */}
      {showVolume && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Volume</h4>
          <ResponsiveContainer width="100%" height={100}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" hide />
              <YAxis hide />
              <Tooltip />
              <Bar dataKey="volume" fill="#6b7280" opacity={0.7} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* RSI Chart */}
      {indicators.rsi && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">RSI (14)</h4>
          <ResponsiveContainer width="100%" height={100}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" hide />
              <YAxis domain={[0, 100]} hide />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="rsi"
                stroke="#8b5cf6"
                strokeWidth={1}
                dot={false}
              />
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" />
              <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default StockChart; 