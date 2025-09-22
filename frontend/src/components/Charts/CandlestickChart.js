import React from 'react';
import {
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Bar,
  Line
} from 'recharts';

const CandlestickChart = ({ data, symbol, period }) => {
  if (!data || !data.length) {
    return (
      <div className="h-96 bg-gray-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">No data available for candlestick chart</p>
        </div>
      </div>
    );
  }

  // Format data for candlestick chart
  const chartData = data.map((item, index) => ({
    ...item,
    date: new Date(item.Date).toLocaleDateString(),
    index,
    // Calculate candlestick properties
    bodyHeight: Math.abs(item.Close - item.Open),
    bodyTop: Math.max(item.Open, item.Close),
    bodyBottom: Math.min(item.Open, item.Close),
    isGreen: item.Close >= item.Open,
    // Volume bars
    volumeBar: item.Volume
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          <p className="text-sm">
            <span className="font-medium">Open:</span> ${data.Open?.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="font-medium">High:</span> ${data.High?.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="font-medium">Low:</span> ${data.Low?.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="font-medium">Close:</span> ${data.Close?.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="font-medium">Volume:</span> {data.Volume?.toLocaleString()}
          </p>
          <p className="text-sm">
            <span className="font-medium">Change:</span> 
            <span className={data.isGreen ? 'text-green-600' : 'text-red-600'}>
              {data.isGreen ? '+' : ''}{(data.Close - data.Open).toFixed(2)} 
              ({((data.Close - data.Open) / data.Open * 100).toFixed(2)}%)
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {symbol} - Candlestick Chart ({period})
        </h3>
        <p className="text-sm text-gray-600">
          OHLC (Open, High, Low, Close) candlestick chart with volume
        </p>
      </div>
      
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" domain={['dataMin - 10', 'dataMax + 10']} />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Candlestick bodies using bars */}
            <Bar 
              yAxisId="left"
              dataKey="bodyHeight" 
              fill={(entry) => entry.isGreen ? '#10b981' : '#ef4444'}
              stroke={(entry) => entry.isGreen ? '#059669' : '#dc2626'}
              strokeWidth={1}
              name="Price Range"
            />
            
            {/* High-Low lines */}
            <Bar 
              yAxisId="left"
              dataKey="High" 
              fill="transparent"
              stroke="#6b7280"
              strokeWidth={1}
              name="High-Low"
            />
            
            {/* Volume bars */}
            <Bar 
              yAxisId="right"
              dataKey="volumeBar" 
              fill="#8884d8" 
              fillOpacity={0.3}
              name="Volume"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 text-xs text-gray-500">
        <p>Data points: {chartData.length} | Last updated: {new Date().toLocaleString()}</p>
        <p className="mt-1">
          <span className="inline-block w-3 h-3 bg-green-500 mr-1"></span> Green: Close ≥ Open (Bullish)
          <span className="inline-block w-3 h-3 bg-red-500 mr-1 ml-4"></span> Red: Close &lt; Open (Bearish)
        </p>
      </div>
    </div>
  );
};

export default CandlestickChart; 