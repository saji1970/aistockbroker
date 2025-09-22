import React, { useRef, useEffect, useState } from 'react';

// Try to import Chart.js components, with fallback
let ChartJS, Line;
let chartComponentsLoaded = false;

try {
  const chartJS = require('chart.js');
  const reactChartJS = require('react-chartjs-2');
  
  ChartJS = chartJS.Chart;
  Line = reactChartJS.Line;
  
  // Register Chart.js components
  ChartJS.register(
    chartJS.CategoryScale,
    chartJS.LinearScale,
    chartJS.PointElement,
    chartJS.LineElement,
    chartJS.Title,
    chartJS.Tooltip,
    chartJS.Legend,
    chartJS.Filler
  );
  
  chartComponentsLoaded = true;
} catch (error) {
  console.warn('Chart.js components not available:', error);
  chartComponentsLoaded = false;
}

const EquityCurveChart = ({ data, title = 'Equity Curve' }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (chartRef.current && chartComponentsLoaded) {
      chartRef.current.update();
    }
  }, [data]);

  // Fallback when Chart.js is not available
  if (!chartComponentsLoaded) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-gray-400 text-4xl mb-2">📊</div>
            <p className="text-gray-500 mb-2">Chart visualization not available</p>
            <p className="text-sm text-gray-400">Chart.js components are loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-gray-400 text-4xl mb-2">📈</div>
            <p className="text-gray-500">No equity curve data available</p>
          </div>
        </div>
      </div>
    );
  }

  // Process data for chart
  const labels = data.map(item => {
    const date = new Date(item.date);
    return date.toLocaleDateString();
  });

  const values = data.map(item => item.value);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Portfolio Value',
        data: values,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgb(59, 130, 246)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
          weight: 'bold',
        },
        color: '#374151',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(59, 130, 246, 0.5)',
        borderWidth: 1,
        callbacks: {
          title: function(context) {
            return `Date: ${context[0].label}`;
          },
          label: function(context) {
            const value = context.parsed.y;
            return `Portfolio Value: $${value.toLocaleString('en-US', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`;
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
          color: '#6B7280',
        },
        grid: {
          display: false,
        },
        ticks: {
          color: '#6B7280',
          maxTicksLimit: 10,
        },
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Portfolio Value ($)',
          color: '#6B7280',
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          color: '#6B7280',
          callback: function(value) {
            return '$' + value.toLocaleString('en-US');
          },
        },
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
    elements: {
      point: {
        hoverRadius: 6,
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="h-80">
        <Line ref={chartRef} data={chartData} options={options} />
      </div>
    </div>
  );
};

export default EquityCurveChart; 