import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

interface Agent {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface DashboardStats {
  total_customers: number;
  total_decisions: number;
  acceptance_rate: number;
  recent_activity: any[];
}

const AgentDashboardScreen: React.FC = () => {
  const navigation = useNavigation();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAgentData();
    loadDashboardData();
  }, []);

  const loadAgentData = async () => {
    try {
      const agentData = await AsyncStorage.getItem('agent_data');
      if (agentData) {
        setAgent(JSON.parse(agentData));
      }
    } catch (error) {
      console.error('Error loading agent data:', error);
    }
  };

  const loadDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:8080/api/agent/dashboard');
      setStats(response.data.stats);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      Alert.alert('Error', 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.removeItem('agent_data');
            await AsyncStorage.removeItem('is_agent_logged_in');
            navigation.navigate('AgentLogin' as never);
          },
        },
      ]
    );
  };

  const navigateToScreen = (screenName: string) => {
    navigation.navigate(screenName as never);
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading dashboard...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.welcomeText}>Welcome back,</Text>
            <Text style={styles.agentName}>{agent?.name}</Text>
            <Text style={styles.roleText}>{agent?.role.toUpperCase()} AGENT</Text>
          </View>
          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats?.total_customers || 0}</Text>
            <Text style={styles.statLabel}>Customers</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats?.total_decisions || 0}</Text>
            <Text style={styles.statLabel}>Decisions</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{stats?.acceptance_rate || 0}%</Text>
            <Text style={styles.statLabel}>Acceptance Rate</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionsGrid}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigateToScreen('CustomerManagement')}
            >
              <Text style={styles.actionButtonText}>Manage Customers</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigateToScreen('TradeSuggestions')}
            >
              <Text style={styles.actionButtonText}>Trade Suggestions</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigateToScreen('PortfolioOverview')}
            >
              <Text style={styles.actionButtonText}>Portfolio Overview</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigateToScreen('LearningInsights')}
            >
              <Text style={styles.actionButtonText}>Learning Insights</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Recent Activity */}
        {stats?.recent_activity && stats.recent_activity.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Activity</Text>
            <View style={styles.activityContainer}>
              {stats.recent_activity.slice(0, 5).map((activity, index) => (
                <View key={index} style={styles.activityItem}>
                  <Text style={styles.activityText}>
                    {activity.agent_decision?.decision || 'Unknown action'}
                  </Text>
                  <Text style={styles.activityTime}>
                    {new Date(activity.timestamp).toLocaleDateString()}
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  welcomeText: {
    fontSize: 16,
    color: '#666',
  },
  agentName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  roleText: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  logoutButton: {
    backgroundColor: '#ff4444',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  activityContainer: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
  },
  activityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  activityText: {
    fontSize: 14,
    color: '#333',
  },
  activityTime: {
    fontSize: 12,
    color: '#666',
  },
});

export default AgentDashboardScreen;
