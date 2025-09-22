import React from 'react';
import { useStore } from '../../store/store';
import { format } from 'date-fns';

const RecentActivity = () => {
  const { portfolio } = useStore();

  // Safely get recent signals with proper null checking
  const recentSignals = React.useMemo(() => {
    if (!portfolio || !portfolio.signalsHistory || !Array.isArray(portfolio.signalsHistory)) {
      return [];
    }
    return portfolio.signalsHistory.slice(-5).reverse();
  }, [portfolio]);

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
      
      {recentSignals.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-sm text-gray-500">No recent activity</p>
        </div>
      ) : (
        <div className="space-y-3">
          {recentSignals.map((signal, index) => {
            // Safely handle signal data
            if (!signal || typeof signal !== 'object') {
              return null;
            }
            
            return (
              <div key={index} className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50">
                <div className={`w-2 h-2 rounded-full ${
                  signal.signal_type === 'BUY' ? 'bg-green-500' : 
                  signal.signal_type === 'SELL' ? 'bg-red-500' : 'bg-yellow-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {signal.signal_type || 'UNKNOWN'} {signal.symbol || 'N/A'}
                  </p>
                  <p className="text-xs text-gray-500">
                    ${(signal.price || 0).toFixed(2)} • {(signal.confidence || 0).toFixed(1)}% confidence
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {signal.timestamp ? format(new Date(signal.timestamp), 'MMM d, h:mm a') : 'N/A'}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RecentActivity; 