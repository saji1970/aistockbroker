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
  Scatter,
  ReferenceLine,
  ReferenceArea
} from 'recharts';
import CandlestickChart from './CandlestickChart';
import ChartExport from './ChartExport';

const TechnicalChart = ({ data, indicator, symbol, period }) => {
  if (!data || !data.length) {
    return (
      <div className="h-96 bg-gray-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">No data available for chart</p>
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

  const renderChart = () => {
    switch (indicator) {
      case 'price':
        return <CandlestickChart data={data} symbol={symbol} period={period} />;

      case 'sma':
        return (
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
        );

      case 'rsi':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="RSI" stroke="#8884d8" strokeWidth={2} name="RSI" />
            <ReferenceLine y={70} stroke="#ff0000" strokeDasharray="3 3" name="Overbought" />
            <ReferenceLine y={30} stroke="#00ff00" strokeDasharray="3 3" name="Oversold" />
            <ReferenceLine y={50} stroke="#888888" strokeDasharray="3 3" name="Neutral" />
          </ComposedChart>
        );

      case 'macd':
        return (
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
        );

      case 'bollinger':
        return (
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
        );

      case 'volume':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Volume" fill="#8884d8" name="Volume" />
            <Line type="monotone" dataKey="OBV" stroke="#82ca9d" strokeWidth={2} name="OBV" />
            <Line type="monotone" dataKey="ADL" stroke="#ff7300" strokeWidth={2} name="ADL" />
          </ComposedChart>
        );

      case 'stochastic':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Stoch_K" stroke="#8884d8" strokeWidth={2} name="%K" />
            <Line type="monotone" dataKey="Stoch_D" stroke="#82ca9d" strokeWidth={2} name="%D" />
            <ReferenceLine y={80} stroke="#ff0000" strokeDasharray="3 3" name="Overbought" />
            <ReferenceLine y={20} stroke="#00ff00" strokeDasharray="3 3" name="Oversold" />
          </ComposedChart>
        );

      case 'williams':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={[-100, 0]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Williams_R" stroke="#8884d8" strokeWidth={2} name="Williams %R" />
            <ReferenceLine y={-20} stroke="#ff0000" strokeDasharray="3 3" name="Overbought" />
            <ReferenceLine y={-80} stroke="#00ff00" strokeDasharray="3 3" name="Oversold" />
          </ComposedChart>
        );

      case 'cci':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="CCI" stroke="#8884d8" strokeWidth={2} name="CCI" />
            <ReferenceLine y={100} stroke="#ff0000" strokeDasharray="3 3" name="Overbought" />
            <ReferenceLine y={-100} stroke="#00ff00" strokeDasharray="3 3" name="Oversold" />
            <ReferenceLine y={0} stroke="#888888" strokeDasharray="3 3" name="Neutral" />
          </ComposedChart>
        );

      case 'roc':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="ROC" stroke="#8884d8" strokeWidth={2} name="ROC" />
            <ReferenceLine y={0} stroke="#888888" strokeDasharray="3 3" name="Zero Line" />
          </ComposedChart>
        );

      case 'atr':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="ATR" stroke="#8884d8" strokeWidth={2} name="ATR" />
            <Area dataKey="ATR" fill="#8884d8" fillOpacity={0.3} />
          </ComposedChart>
        );

      case 'obv':
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="OBV" stroke="#8884d8" strokeWidth={2} name="OBV" />
            <Line type="monotone" dataKey="ADL" stroke="#82ca9d" strokeWidth={2} name="ADL" />
            <Line type="monotone" dataKey="CMF" stroke="#ff7300" strokeWidth={2} name="CMF" />
          </ComposedChart>
        );

      default:
        return (
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis domain={['dataMin - 10', 'dataMax + 10']} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Close" stroke="#8884d8" strokeWidth={2} name="Close Price" />
          </ComposedChart>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {symbol} - {indicator.toUpperCase()} Analysis ({period})
        </h3>
        <p className="text-sm text-gray-600">
          {getIndicatorDescription(indicator)}
        </p>
      </div>
      
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 flex items-center justify-between">
        <div className="text-xs text-gray-500">
          <p>Data points: {chartData.length} | Last updated: {new Date().toLocaleString()}</p>
        </div>
        <ChartExport 
          symbol={symbol}
          indicator={indicator}
          period={period}
          data={data}
        />
      </div>
    </div>
  );
};

const getIndicatorDescription = (indicator) => {
  const descriptions = {
    price: 'Price chart showing Open, High, Low, Close prices with volume',
    sma: 'Simple Moving Averages (20, 50) and Exponential Moving Averages (12, 26)',
    rsi: 'Relative Strength Index - Momentum oscillator measuring speed and magnitude of price changes',
    macd: 'Moving Average Convergence Divergence - Trend-following momentum indicator',
    bollinger: 'Bollinger Bands - Volatility indicator showing upper, middle, and lower bands',
    volume: 'Volume analysis with On-Balance Volume (OBV) and Accumulation/Distribution Line (ADL)',
    stochastic: 'Stochastic Oscillator - Momentum indicator comparing closing price to price range',
    williams: 'Williams %R - Momentum indicator measuring overbought/oversold levels',
    cci: 'Commodity Channel Index - Momentum oscillator measuring current price relative to average',
    roc: 'Rate of Change - Momentum oscillator measuring percentage change in price',
    atr: 'Average True Range - Volatility indicator measuring market volatility',
    obv: 'On-Balance Volume - Volume-based indicator measuring buying and selling pressure'
  };
  return descriptions[indicator] || 'Technical analysis chart';
};

export default TechnicalChart; 