import React from 'react';
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
  ReferenceLine
} from 'recharts';
import ChartExport from './ChartExport';

const MultiIndicatorChart = ({ data, symbol, period }) => {
  if (!data || !data.length) {
    return (
      <div className="h-96 bg-gray-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">No data available for comprehensive analysis</p>
        </div>
      </div>
    );
  }

  // Format data for charts
  const chartData = data.map((item, index) => ({
    ...item,
    date: new Date(item.Date).toLocaleDateString(),
    index
  }));

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {symbol} - Comprehensive Technical Analysis ({period})
        </h3>
        <p className="text-sm text-gray-600">
          Multi-indicator view showing price, volume, RSI, MACD, and Bollinger Bands
        </p>
      </div>
      
      <div className="space-y-6">
        {/* Price and Volume Chart */}
        <div className="h-64">
          <h4 className="text-md font-medium text-gray-800 mb-2">Price & Volume</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" domain={['dataMin - 10', 'dataMax + 10']} />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="Close" stroke="#8884d8" strokeWidth={2} name="Close Price" />
              <Bar yAxisId="right" dataKey="Volume" fill="#8884d8" fillOpacity={0.3} name="Volume" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* RSI Chart */}
        <div className="h-48">
          <h4 className="text-md font-medium text-gray-800 mb-2">RSI (Relative Strength Index)</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="RSI" stroke="#82ca9d" strokeWidth={2} name="RSI" />
              <ReferenceLine y={70} stroke="#ff0000" strokeDasharray="3 3" name="Overbought" />
              <ReferenceLine y={30} stroke="#00ff00" strokeDasharray="3 3" name="Oversold" />
              <ReferenceLine y={50} stroke="#888888" strokeDasharray="3 3" name="Neutral" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* MACD Chart */}
        <div className="h-48">
          <h4 className="text-md font-medium text-gray-800 mb-2">MACD (Moving Average Convergence Divergence)</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="MACD" stroke="#8884d8" strokeWidth={2} name="MACD" />
              <Line type="monotone" dataKey="MACD_Signal" stroke="#82ca9d" strokeWidth={2} name="Signal Line" />
              <Bar dataKey="MACD_Histogram" fill="#ff7300" name="Histogram" />
              <ReferenceLine y={0} stroke="#888888" strokeDasharray="3 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Bollinger Bands Chart */}
        <div className="h-48">
          <h4 className="text-md font-medium text-gray-800 mb-2">Bollinger Bands</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['dataMin - 10', 'dataMax + 10']} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="Close" stroke="#8884d8" strokeWidth={2} name="Close Price" />
              <Line type="monotone" dataKey="BB_Upper" stroke="#ff7300" strokeWidth={1} strokeDasharray="5 5" name="Upper Band" />
              <Line type="monotone" dataKey="BB_Middle" stroke="#82ca9d" strokeWidth={1} name="Middle Band" />
              <Line type="monotone" dataKey="BB_Lower" stroke="#ff7300" strokeWidth={1} strokeDasharray="5 5" name="Lower Band" />
              <Area dataKey="BB_Upper" fill="#ff7300" fillOpacity={0.1} />
              <Area dataKey="BB_Lower" fill="#ff7300" fillOpacity={0.1} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Moving Averages Chart */}
        <div className="h-48">
          <h4 className="text-md font-medium text-gray-800 mb-2">Moving Averages</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['dataMin - 10', 'dataMax + 10']} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="Close" stroke="#8884d8" strokeWidth={2} name="Close Price" />
              <Line type="monotone" dataKey="SMA_20" stroke="#82ca9d" strokeWidth={2} name="SMA 20" />
              <Line type="monotone" dataKey="SMA_50" stroke="#ff7300" strokeWidth={2} name="SMA 50" />
              <Line type="monotone" dataKey="EMA_12" stroke="#ff0000" strokeWidth={2} name="EMA 12" />
              <Line type="monotone" dataKey="EMA_26" stroke="#0000ff" strokeWidth={2} name="EMA 26" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="mt-4 flex items-center justify-between">
        <div className="text-xs text-gray-500">
          <p>Data points: {chartData.length} | Last updated: {new Date().toLocaleString()}</p>
        </div>
        <ChartExport 
          symbol={symbol}
          indicator="comprehensive"
          period={period}
          data={data}
        />
      </div>
    </div>
  );
};

export default MultiIndicatorChart; 