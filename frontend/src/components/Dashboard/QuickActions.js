import React from 'react';
import { Link } from 'react-router-dom';
import {
  PlusIcon,
  ChartBarIcon,
  SparklesIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/outline';

const QuickActions = () => {
  const actions = [
    {
      name: 'Add Capital',
      description: 'Add funds to your portfolio',
      href: '/portfolio',
      icon: PlusIcon,
      color: 'bg-success-500',
    },
    {
      name: 'Generate Signals',
      description: 'Get AI trading signals',
      href: '/portfolio',
      icon: SparklesIcon,
      color: 'bg-primary-500',
    },
    {
      name: 'Technical Analysis',
      description: 'View detailed charts',
      href: '/analysis',
      icon: ChartBarIcon,
      color: 'bg-warning-500',
    },
    {
      name: 'Portfolio Overview',
      description: 'Manage your investments',
      href: '/portfolio',
      icon: BriefcaseIcon,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
      <div className="space-y-3">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.name}
              to={action.href}
              className="flex items-center p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              <div className={`p-2 rounded-lg ${action.color}`}>
                <Icon className="h-5 w-5 text-white" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-gray-900">{action.name}</p>
                <p className="text-xs text-gray-500">{action.description}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActions; 