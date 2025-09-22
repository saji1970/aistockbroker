import React from 'react';
import { 
  ArrowDownTrayIcon, 
  DocumentArrowDownIcon,
  PhotoIcon 
} from '@heroicons/react/24/outline';

const ChartExport = ({ chartRef, symbol, indicator, period, data }) => {
  const exportAsImage = () => {
    if (chartRef && chartRef.current) {
      // This would require html2canvas or similar library
      // For now, we'll show a placeholder
      alert('Chart export functionality will be implemented with html2canvas library');
    }
  };

  const exportAsCSV = () => {
    if (!data || !data.length) {
      alert('No data available for export');
      return;
    }

    // Convert data to CSV format
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(row => 
      Object.values(row).map(value => 
        typeof value === 'string' ? `"${value}"` : value
      ).join(',')
    );
    
    const csvContent = [headers, ...rows].join('\n');
    
    // Create and download CSV file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${symbol}_${indicator}_${period}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const exportAsJSON = () => {
    if (!data || !data.length) {
      alert('No data available for export');
      return;
    }

    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${symbol}_${indicator}_${period}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
      <span className="text-sm font-medium text-gray-700">Export:</span>
      
      <button
        onClick={exportAsImage}
        className="flex items-center space-x-1 px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        title="Export as PNG image"
      >
        <PhotoIcon className="h-4 w-4" />
        <span>Image</span>
      </button>
      
      <button
        onClick={exportAsCSV}
        className="flex items-center space-x-1 px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        title="Export as CSV file"
      >
        <DocumentArrowDownIcon className="h-4 w-4" />
        <span>CSV</span>
      </button>
      
      <button
        onClick={exportAsJSON}
        className="flex items-center space-x-1 px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        title="Export as JSON file"
      >
        <ArrowDownTrayIcon className="h-4 w-4" />
        <span>JSON</span>
      </button>
    </div>
  );
};

export default ChartExport; 