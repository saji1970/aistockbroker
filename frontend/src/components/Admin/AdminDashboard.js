import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  UsersIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import adminService from '../../services/adminService';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentUsers, setRecentUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);

    try {
      // Load dashboard statistics
      const statsResult = await adminService.getDashboardStats();
      if (statsResult.success) {
        setStats(statsResult.data.stats);
      } else {
        toast.error('Failed to load dashboard statistics');
      }

      // Load recent users
      const usersResult = await adminService.getUsers({
        page: 1,
        per_page: 10,
        sort: 'created_at',
        order: 'desc'
      });

      if (usersResult.success) {
        setRecentUsers(usersResult.data.users || []);
      } else {
        toast.error('Failed to load recent users');
      }
    } catch (error) {
      console.error('Dashboard loading error:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'suspended':
        return 'bg-red-100 text-red-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      case 'user':
        return 'bg-blue-100 text-blue-800';
      case 'guest':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const statCards = [
    {
      title: 'Total Users',
      value: stats?.total_users || 0,
      icon: UsersIcon,
      color: 'bg-blue-500',
      change: stats?.recent_registrations ? `+${stats.recent_registrations} this month` : null
    },
    {
      title: 'Active Users',
      value: stats?.status_breakdown?.active || 0,
      icon: UserGroupIcon,
      color: 'bg-green-500',
      percentage: stats?.total_users ? Math.round((stats.status_breakdown?.active / stats.total_users) * 100) : 0
    },
    {
      title: 'Pending Verification',
      value: stats?.status_breakdown?.pending || 0,
      icon: ClockIcon,
      color: 'bg-yellow-500',
      percentage: stats?.total_users ? Math.round((stats.status_breakdown?.pending / stats.total_users) * 100) : 0
    },
    {
      title: 'Suspended Accounts',
      value: stats?.status_breakdown?.suspended || 0,
      icon: ExclamationTriangleIcon,
      color: 'bg-red-500',
      percentage: stats?.total_users ? Math.round((stats.status_breakdown?.suspended / stats.total_users) * 100) : 0
    },
    {
      title: 'Administrators',
      value: stats?.role_breakdown?.admin || 0,
      icon: ShieldCheckIcon,
      color: 'bg-purple-500',
      percentage: stats?.total_users ? Math.round((stats.role_breakdown?.admin / stats.total_users) * 100) : 0
    },
    {
      title: 'Recent Logins',
      value: stats?.recent_logins || 0,
      icon: ChartBarIcon,
      color: 'bg-indigo-500',
      change: 'Last 30 days'
    }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage users and monitor system activity
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
          {statCards.map((stat, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-md ${stat.color}`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-500">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value.toLocaleString()}</p>
                  {stat.change && (
                    <p className="text-xs text-gray-500">{stat.change}</p>
                  )}
                  {stat.percentage !== undefined && (
                    <p className="text-xs text-gray-500">{stat.percentage}% of total</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Quick Actions</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <Link
                  to="/admin/users"
                  className="block w-full text-left px-4 py-3 bg-indigo-50 hover:bg-indigo-100 rounded-lg border border-indigo-200 transition-colors"
                >
                  <div className="flex items-center">
                    <UsersIcon className="h-5 w-5 text-indigo-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Manage Users</p>
                      <p className="text-xs text-gray-500">View, edit, and manage user accounts</p>
                    </div>
                  </div>
                </Link>

                <Link
                  to="/admin/users?status=pending"
                  className="block w-full text-left px-4 py-3 bg-yellow-50 hover:bg-yellow-100 rounded-lg border border-yellow-200 transition-colors"
                >
                  <div className="flex items-center">
                    <ClockIcon className="h-5 w-5 text-yellow-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Pending Verifications</p>
                      <p className="text-xs text-gray-500">
                        {stats?.status_breakdown?.pending || 0} users awaiting verification
                      </p>
                    </div>
                  </div>
                </Link>

                <Link
                  to="/admin/users?status=suspended"
                  className="block w-full text-left px-4 py-3 bg-red-50 hover:bg-red-100 rounded-lg border border-red-200 transition-colors"
                >
                  <div className="flex items-center">
                    <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Suspended Accounts</p>
                      <p className="text-xs text-gray-500">
                        {stats?.status_breakdown?.suspended || 0} suspended accounts
                      </p>
                    </div>
                  </div>
                </Link>

                <button
                  onClick={() => window.location.reload()}
                  className="block w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
                >
                  <div className="flex items-center">
                    <ChartBarIcon className="h-5 w-5 text-gray-600 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Refresh Dashboard</p>
                      <p className="text-xs text-gray-500">Update all statistics and data</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </div>

          {/* Recent Users */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-medium text-gray-900">Recent Users</h2>
                <Link
                  to="/admin/users"
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  View all
                </Link>
              </div>
            </div>
            <div className="p-6">
              {recentUsers.length > 0 ? (
                <div className="space-y-4">
                  {recentUsers.slice(0, 5).map((user) => (
                    <div key={user.id} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                            <span className="text-xs font-medium text-gray-600">
                              {user.first_name?.charAt(0) || user.username?.charAt(0) || 'U'}
                            </span>
                          </div>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm font-medium text-gray-900">
                            {user.first_name && user.last_name
                              ? `${user.first_name} ${user.last_name}`
                              : user.username
                            }
                          </p>
                          <p className="text-xs text-gray-500">{user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRoleColor(user.role)}`}>
                          {user.role?.toUpperCase()}
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(user.status)}`}>
                          {user.status?.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No recent users found</p>
              )}
            </div>
          </div>
        </div>

        {/* User Status Breakdown */}
        {stats && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">User Status Breakdown</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(stats.status_breakdown || {}).map(([status, count]) => (
                  <div key={status} className="text-center">
                    <p className="text-2xl font-bold text-gray-900">{count}</p>
                    <p className={`text-sm font-medium capitalize ${
                      status === 'active' ? 'text-green-600' :
                      status === 'pending' ? 'text-yellow-600' :
                      status === 'suspended' ? 'text-red-600' :
                      'text-gray-600'
                    }`}>
                      {status}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;