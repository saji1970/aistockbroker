import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useStore } from '../../store/store';
import {
  HomeIcon,
  ChartBarIcon,
  BriefcaseIcon,
  SparklesIcon,
  CogIcon,
  UserIcon,
} from '@heroicons/react/24/outline';

const Sidebar = ({ navigation }) => {
  const location = useLocation();
  const { currentSymbol, setCurrentSymbol, currentPeriod, setCurrentPeriod } = useStore();

  const getIcon = (iconName) => {
    switch (iconName) {
      case 'HomeIcon':
        return HomeIcon;
      case 'ChartBarIcon':
        return ChartBarIcon;
      case 'BriefcaseIcon':
        return BriefcaseIcon;
      case 'SparklesIcon':
        return SparklesIcon;
      default:
        return HomeIcon;
    }
  };

  const periods = [
    { value: '1d', label: '1 Day' },
    { value: '7d', label: '7 Days' },
    { value: '14d', label: '14 Days' },
    { value: '1mo', label: '1 Month' },
    { value: '3mo', label: '3 Months' },
    { value: '6mo', label: '6 Months' },
    { value: '1y', label: '1 Year' },
    { value: '2y', label: '2 Years' },
  ];

  return (
    <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 border-r border-gray-200">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg flex items-center justify-center">
            <SparklesIcon className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">AI Stock Trading</h1>
            <p className="text-xs text-gray-500">Powered by Gemini Pro</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col">
        <ul role="list" className="flex flex-1 flex-col gap-y-7">
          <li>
            <ul role="list" className="-mx-2 space-y-1">
              {navigation.map((item) => {
                const Icon = getIcon(item.icon);
                const isActive = location.pathname === item.href;
                
                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={`
                        group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors
                        ${isActive
                          ? 'bg-primary-50 text-primary-600'
                          : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                        }
                      `}
                    >
                      <Icon
                        className={`h-6 w-6 shrink-0 ${
                          isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-primary-600'
                        }`}
                      />
                      {item.name}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </li>

          {/* Stock Symbol Input */}
          <li>
            <div className="space-y-3">
              <h3 className="text-xs font-semibold leading-6 text-gray-500 uppercase tracking-wider">
                Stock Symbol
              </h3>
              <input
                type="text"
                value={currentSymbol}
                onChange={(e) => setCurrentSymbol(e.target.value.toUpperCase())}
                className="input-field text-sm"
                placeholder="Enter symbol (e.g., AAPL)"
                maxLength={5}
              />
            </div>
          </li>

          {/* Period Selection */}
          <li>
            <div className="space-y-3">
              <h3 className="text-xs font-semibold leading-6 text-gray-500 uppercase tracking-wider">
                Analysis Period
              </h3>
              <select
                value={currentPeriod}
                onChange={(e) => setCurrentPeriod(e.target.value)}
                className="input-field text-sm"
              >
                {periods.map((period) => (
                  <option key={period.value} value={period.value}>
                    {period.label}
                  </option>
                ))}
              </select>
            </div>
          </li>

          {/* Bottom section */}
          <li className="mt-auto">
            <ul role="list" className="-mx-2 space-y-1">
              <li>
                <Link
                  to="/settings"
                  className="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                >
                  <CogIcon className="h-6 w-6 shrink-0 text-gray-400 group-hover:text-primary-600" />
                  Settings
                </Link>
              </li>
              <li>
                <Link
                  to="/profile"
                  className="group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                >
                  <UserIcon className="h-6 w-6 shrink-0 text-gray-400 group-hover:text-primary-600" />
                  Profile
                </Link>
              </li>
            </ul>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar; 