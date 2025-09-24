import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import screens
import AgentLoginScreen from './src/screens/AgentLoginScreen';
import AgentDashboardScreen from './src/screens/AgentDashboardScreen';
import TradeSuggestionsScreen from './src/screens/TradeSuggestionsScreen';

const Stack = createStackNavigator();

function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  const [isAgentLoggedIn, setIsAgentLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAgentLoginStatus();
  }, []);

  const checkAgentLoginStatus = async () => {
    try {
      const isLoggedIn = await AsyncStorage.getItem('is_agent_logged_in');
      setIsAgentLoggedIn(isLoggedIn === 'true');
    } catch (error) {
      console.error('Error checking login status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentLogin = () => {
    setIsAgentLoggedIn(true);
  };

  const handleAgentLogout = () => {
    setIsAgentLoggedIn(false);
  };

  const backgroundStyle = {
    backgroundColor: isDarkMode ? '#000000' : '#ffffff',
    flex: 1,
  };

  if (loading) {
    return (
      <SafeAreaView style={backgroundStyle}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (isAgentLoggedIn) {
    return (
      <NavigationContainer>
        <Stack.Navigator initialRouteName="AgentDashboard">
          <Stack.Screen 
            name="AgentDashboard" 
            component={AgentDashboardScreen}
            options={{ title: 'Agent Dashboard' }}
          />
          <Stack.Screen 
            name="TradeSuggestions" 
            component={TradeSuggestionsScreen}
            options={{ title: 'Trade Suggestions' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    );
  }

  return (
    <SafeAreaView style={backgroundStyle}>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={backgroundStyle.backgroundColor}
      />
      <ScrollView
        contentInsetAdjustmentBehavior="automatic"
        style={backgroundStyle}>
        <View style={styles.container}>
          <Text style={styles.title}>AI Stock Trading</Text>
          <Text style={styles.subtitle}>Mobile Application</Text>
          <Text style={styles.description}>
            Welcome to the AI Stock Trading mobile app with agent functionality!
          </Text>
          <Text style={styles.status}>
            App is running successfully ✅
          </Text>
          
          <View style={styles.buttonContainer}>
            <TouchableOpacity 
              style={styles.agentButton}
              onPress={handleAgentLogin}
            >
              <Text style={styles.agentButtonText}>Agent Login</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.featuresButton}
              onPress={() => Alert.alert('Features', 'Agent Management\nCustomer Portfolio\nAI Suggestions\nLearning System')}
            >
              <Text style={styles.featuresButtonText}>View Features</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    marginTop: 100,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 20,
    color: '#64748b',
    marginBottom: 20,
    textAlign: 'center',
  },
  description: {
    fontSize: 16,
    color: '#374151',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 24,
  },
  status: {
    fontSize: 18,
    color: '#059669',
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 30,
  },
  buttonContainer: {
    width: '100%',
    gap: 16,
  },
  agentButton: {
    backgroundColor: '#2563eb',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 8,
    alignItems: 'center',
  },
  agentButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },
  featuresButton: {
    backgroundColor: '#f1f5f9',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  featuresButtonText: {
    color: '#475569',
    fontSize: 16,
    fontWeight: '600',
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
});

export default App;