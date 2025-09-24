import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { UserCircleIcon, CogIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import authService from '../../services/authService';

const ProfilePage = () => {
  const [user, setUser] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setSaving] = useState(false);

  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    trading_experience: '',
    risk_tolerance: '',
    investment_goals: '',
    preferred_sectors: '',
    initial_capital: ''
  });

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    setIsLoading(true);
    try {
      const result = await authService.getCurrentUser();
      if (result.success) {
        setUser(result.user);
        setProfileData({
          first_name: result.user.first_name || '',
          last_name: result.user.last_name || '',
          trading_experience: result.user.trading_experience || '',
          risk_tolerance: result.user.risk_tolerance || '',
          investment_goals: result.user.investment_goals || '',
          preferred_sectors: result.user.preferred_sectors || '',
          initial_capital: result.user.initial_capital || ''
        });
      } else {
        toast.error('Failed to load profile data');
      }
    } catch (error) {
      console.error('Error loading user data:', error);
      toast.error('Failed to load profile data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));

    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));

    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateProfileData = () => {
    const newErrors = {};

    if (profileData.initial_capital && isNaN(parseFloat(profileData.initial_capital))) {
      newErrors.initial_capital = 'Initial capital must be a valid number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validatePasswordData = () => {
    const newErrors = {};

    if (!passwordData.current_password) {
      newErrors.current_password = 'Current password is required';
    }

    if (!passwordData.new_password) {
      newErrors.new_password = 'New password is required';
    } else if (passwordData.new_password.length < 8) {
      newErrors.new_password = 'Password must be at least 8 characters long';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])/.test(passwordData.new_password)) {
      newErrors.new_password = 'Password must contain uppercase, lowercase, digit, and special character';
    }

    if (!passwordData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your new password';
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();

    if (!validateProfileData()) {
      return;
    }

    setSaving(true);

    try {
      const updateData = { ...profileData };
      if (updateData.initial_capital) {
        updateData.initial_capital = parseFloat(updateData.initial_capital);
      }

      const result = await authService.updateProfile(updateData);

      if (result.success) {
        setUser(result.user);
        setIsEditing(false);
        toast.success(result.message || 'Profile updated successfully');
      } else {
        setErrors({ general: result.error });
        toast.error(result.error);
      }
    } catch (error) {
      console.error('Profile update error:', error);
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();

    if (!validatePasswordData()) {
      return;
    }

    setSaving(true);

    try {
      const result = await authService.changePassword(
        passwordData.current_password,
        passwordData.new_password
      );

      if (result.success) {
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
        toast.success(result.message || 'Password changed successfully');
      } else {
        setErrors({ password_general: result.error });
        toast.error(result.error);
      }
    } catch (error) {
      console.error('Password change error:', error);
      toast.error('Failed to change password');
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserCircleIcon },
    { id: 'preferences', name: 'Trading Preferences', icon: CogIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Account Settings</h1>
            <p className="mt-1 text-sm text-gray-600">
              Manage your account information and trading preferences
            </p>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="h-5 w-5 mr-2" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-gray-900">Basic Information</h2>
                  {!isEditing && (
                    <button
                      onClick={() => setIsEditing(true)}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Edit Profile
                    </button>
                  )}
                </div>

                {isEditing ? (
                  <form onSubmit={handleProfileSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          First Name
                        </label>
                        <input
                          type="text"
                          name="first_name"
                          value={profileData.first_name}
                          onChange={handleProfileChange}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Last Name
                        </label>
                        <input
                          type="text"
                          name="last_name"
                          value={profileData.last_name}
                          onChange={handleProfileChange}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Email
                      </label>
                      <input
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 bg-gray-50 text-gray-500 sm:text-sm"
                      />
                      <p className="mt-1 text-sm text-gray-500">
                        Email cannot be changed. Contact support if needed.
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Username
                      </label>
                      <input
                        type="text"
                        value={user?.username || ''}
                        disabled
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 bg-gray-50 text-gray-500 sm:text-sm"
                      />
                      <p className="mt-1 text-sm text-gray-500">
                        Username cannot be changed. Contact support if needed.
                      </p>
                    </div>

                    {errors.general && (
                      <div className="bg-red-50 border border-red-200 rounded-md p-3">
                        <p className="text-sm text-red-600">{errors.general}</p>
                      </div>
                    )}

                    <div className="flex justify-end space-x-3">
                      <button
                        type="button"
                        onClick={() => {
                          setIsEditing(false);
                          setErrors({});
                        }}
                        className="py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={isSaving}
                        className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                      >
                        {isSaving ? 'Saving...' : 'Save Changes'}
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">First Name</dt>
                        <dd className="mt-1 text-sm text-gray-900">{user?.first_name || 'Not provided'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Last Name</dt>
                        <dd className="mt-1 text-sm text-gray-900">{user?.last_name || 'Not provided'}</dd>
                      </div>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Email</dt>
                      <dd className="mt-1 text-sm text-gray-900">{user?.email}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Username</dt>
                      <dd className="mt-1 text-sm text-gray-900">{user?.username}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Role</dt>
                      <dd className="mt-1">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user?.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                        }`}>
                          {user?.role?.toUpperCase()}
                        </span>
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Account Status</dt>
                      <dd className="mt-1">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user?.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {user?.status?.toUpperCase()}
                        </span>
                      </dd>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'preferences' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Trading Preferences</h2>

                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Trading Experience
                    </label>
                    <select
                      name="trading_experience"
                      value={profileData.trading_experience}
                      onChange={handleProfileChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    >
                      <option value="">Select your experience level</option>
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Risk Tolerance
                    </label>
                    <select
                      name="risk_tolerance"
                      value={profileData.risk_tolerance}
                      onChange={handleProfileChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    >
                      <option value="">Select your risk tolerance</option>
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Investment Goals
                    </label>
                    <textarea
                      name="investment_goals"
                      rows={3}
                      value={profileData.investment_goals}
                      onChange={handleProfileChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Describe your investment goals..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Preferred Sectors
                    </label>
                    <input
                      type="text"
                      name="preferred_sectors"
                      value={profileData.preferred_sectors}
                      onChange={handleProfileChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Technology, Healthcare, Finance..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Initial Capital ($)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      name="initial_capital"
                      value={profileData.initial_capital}
                      onChange={handleProfileChange}
                      className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                        errors.initial_capital ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="10000.00"
                    />
                    {errors.initial_capital && (
                      <p className="mt-1 text-sm text-red-600">{errors.initial_capital}</p>
                    )}
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={isSaving}
                      className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                      {isSaving ? 'Saving...' : 'Save Preferences'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h2 className="text-lg font-medium text-gray-900">Change Password</h2>

                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Current Password
                    </label>
                    <input
                      type="password"
                      name="current_password"
                      value={passwordData.current_password}
                      onChange={handlePasswordChange}
                      className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                        errors.current_password ? 'border-red-300' : 'border-gray-300'
                      }`}
                    />
                    {errors.current_password && (
                      <p className="mt-1 text-sm text-red-600">{errors.current_password}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      New Password
                    </label>
                    <input
                      type="password"
                      name="new_password"
                      value={passwordData.new_password}
                      onChange={handlePasswordChange}
                      className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                        errors.new_password ? 'border-red-300' : 'border-gray-300'
                      }`}
                    />
                    {errors.new_password && (
                      <p className="mt-1 text-sm text-red-600">{errors.new_password}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      name="confirm_password"
                      value={passwordData.confirm_password}
                      onChange={handlePasswordChange}
                      className={`mt-1 block w-full border rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                        errors.confirm_password ? 'border-red-300' : 'border-gray-300'
                      }`}
                    />
                    {errors.confirm_password && (
                      <p className="mt-1 text-sm text-red-600">{errors.confirm_password}</p>
                    )}
                  </div>

                  {errors.password_general && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-3">
                      <p className="text-sm text-red-600">{errors.password_general}</p>
                    </div>
                  )}

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={isSaving}
                      className="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                      {isSaving ? 'Changing...' : 'Change Password'}
                    </button>
                  </div>
                </form>

                <div className="pt-6 border-t border-gray-200">
                  <h3 className="text-md font-medium text-gray-900 mb-4">Account Information</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Last login:</span>
                      <span className="text-sm text-gray-900">
                        {user?.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Account created:</span>
                      <span className="text-sm text-gray-900">
                        {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;