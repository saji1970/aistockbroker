import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
  TextInput,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import axios from 'axios';

interface TradeSuggestion {
  id: string;
  customer_id: string;
  symbol: string;
  action: string;
  quantity: number;
  price: number;
  confidence: number;
  reasoning: string;
  ai_model: string;
  created_at: string;
  expires_at: string;
  status: string;
  agent_notes: string;
}

interface Customer {
  id: string;
  name: string;
  email: string;
  tier: string;
}

const TradeSuggestionsScreen: React.FC = () => {
  const [suggestions, setSuggestions] = useState<TradeSuggestion[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<TradeSuggestion | null>(null);
  const [decisionModalVisible, setDecisionModalVisible] = useState(false);
  const [decision, setDecision] = useState('');
  const [reasoning, setReasoning] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [suggestionsResponse, customersResponse] = await Promise.all([
        axios.get('http://localhost:8080/api/agent/suggestions'),
        axios.get('http://localhost:8080/api/agent/customers'),
      ]);

      setSuggestions(suggestionsResponse.data.suggestions);
      setCustomers(customersResponse.data.customers);
    } catch (error) {
      console.error('Error loading data:', error);
      Alert.alert('Error', 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const getCustomerName = (customerId: string) => {
    const customer = customers.find(c => c.id === customerId);
    return customer ? customer.name : 'Unknown Customer';
  };

  const getActionColor = (action: string) => {
    switch (action.toLowerCase()) {
      case 'buy':
        return '#4CAF50';
      case 'sell':
        return '#F44336';
      case 'hold':
        return '#FF9800';
      default:
        return '#666';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return '#FF9800';
      case 'accepted':
        return '#4CAF50';
      case 'rejected':
        return '#F44336';
      case 'expired':
        return '#666';
      default:
        return '#666';
    }
  };

  const handleMakeDecision = (suggestion: TradeSuggestion) => {
    setSelectedSuggestion(suggestion);
    setDecision('');
    setReasoning('');
    setDecisionModalVisible(true);
  };

  const submitDecision = async () => {
    if (!selectedSuggestion || !decision) {
      Alert.alert('Error', 'Please select a decision');
      return;
    }

    try {
      await axios.post(
        `http://localhost:8080/api/agent/suggestions/${selectedSuggestion.id}/decision`,
        {
          decision,
          reasoning,
        }
      );

      Alert.alert('Success', 'Decision recorded successfully');
      setDecisionModalVisible(false);
      loadData(); // Refresh data
    } catch (error) {
      console.error('Error submitting decision:', error);
      Alert.alert('Error', 'Failed to submit decision');
    }
  };

  const generateNewSuggestions = async () => {
    Alert.alert(
      'Generate Suggestions',
      'This will generate new AI suggestions for all your customers. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Generate',
          onPress: async () => {
            try {
              // Generate suggestions for each customer
              for (const customer of customers) {
                await axios.post('http://localhost:8080/api/agent/suggestions/generate', {
                  customer_id: customer.id,
                  max_suggestions: 3,
                });
              }
              Alert.alert('Success', 'New suggestions generated');
              loadData();
            } catch (error) {
              console.error('Error generating suggestions:', error);
              Alert.alert('Error', 'Failed to generate suggestions');
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Loading suggestions...</Text>
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
          <Text style={styles.title}>Trade Suggestions</Text>
          <TouchableOpacity style={styles.generateButton} onPress={generateNewSuggestions}>
            <Text style={styles.generateButtonText}>Generate New</Text>
          </TouchableOpacity>
        </View>

        {/* Suggestions List */}
        {suggestions.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No suggestions available</Text>
            <Text style={styles.emptySubtext}>Generate new suggestions to get started</Text>
          </View>
        ) : (
          suggestions.map((suggestion) => (
            <View key={suggestion.id} style={styles.suggestionCard}>
              <View style={styles.suggestionHeader}>
                <Text style={styles.symbolText}>{suggestion.symbol}</Text>
                <View style={styles.badgeContainer}>
                  <View
                    style={[
                      styles.actionBadge,
                      { backgroundColor: getActionColor(suggestion.action) },
                    ]}
                  >
                    <Text style={styles.actionBadgeText}>
                      {suggestion.action.toUpperCase()}
                    </Text>
                  </View>
                  <View
                    style={[
                      styles.statusBadge,
                      { backgroundColor: getStatusColor(suggestion.status) },
                    ]}
                  >
                    <Text style={styles.statusBadgeText}>
                      {suggestion.status.toUpperCase()}
                    </Text>
                  </View>
                </View>
              </View>

              <Text style={styles.customerText}>
                Customer: {getCustomerName(suggestion.customer_id)}
              </Text>

              <View style={styles.suggestionDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Quantity:</Text>
                  <Text style={styles.detailValue}>{suggestion.quantity}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Price:</Text>
                  <Text style={styles.detailValue}>${suggestion.price.toFixed(2)}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Confidence:</Text>
                  <Text style={styles.detailValue}>
                    {(suggestion.confidence * 100).toFixed(1)}%
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>AI Model:</Text>
                  <Text style={styles.detailValue}>{suggestion.ai_model}</Text>
                </View>
              </View>

              <Text style={styles.reasoningText}>{suggestion.reasoning}</Text>

              <View style={styles.suggestionFooter}>
                <Text style={styles.timestampText}>
                  Created: {new Date(suggestion.created_at).toLocaleString()}
                </Text>
                {suggestion.status === 'pending' && (
                  <TouchableOpacity
                    style={styles.decisionButton}
                    onPress={() => handleMakeDecision(suggestion)}
                  >
                    <Text style={styles.decisionButtonText}>Make Decision</Text>
                  </TouchableOpacity>
                )}
              </View>
            </View>
          ))
        )}
      </ScrollView>

      {/* Decision Modal */}
      <Modal
        visible={decisionModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setDecisionModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Make Decision</Text>
            <Text style={styles.modalSubtitle}>
              {selectedSuggestion?.symbol} - {selectedSuggestion?.action.toUpperCase()}
            </Text>

            <View style={styles.decisionButtons}>
              <TouchableOpacity
                style={[styles.decisionOption, decision === 'accept' && styles.decisionOptionSelected]}
                onPress={() => setDecision('accept')}
              >
                <Text style={[styles.decisionOptionText, decision === 'accept' && styles.decisionOptionTextSelected]}>
                  Accept
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.decisionOption, decision === 'reject' && styles.decisionOptionSelected]}
                onPress={() => setDecision('reject')}
              >
                <Text style={[styles.decisionOptionText, decision === 'reject' && styles.decisionOptionTextSelected]}>
                  Reject
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.decisionOption, decision === 'modify' && styles.decisionOptionSelected]}
                onPress={() => setDecision('modify')}
              >
                <Text style={[styles.decisionOptionText, decision === 'modify' && styles.decisionOptionTextSelected]}>
                  Modify
                </Text>
              </TouchableOpacity>
            </View>

            <TextInput
              style={styles.reasoningInput}
              value={reasoning}
              onChangeText={setReasoning}
              placeholder="Add reasoning for your decision..."
              multiline
              numberOfLines={3}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setDecisionModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.submitButton}
                onPress={submitDecision}
              >
                <Text style={styles.submitButtonText}>Submit</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  generateButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  suggestionCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  suggestionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  symbolText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  badgeContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  actionBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  actionBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  customerText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  suggestionDetails: {
    marginBottom: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  reasoningText: {
    fontSize: 14,
    color: '#333',
    fontStyle: 'italic',
    marginBottom: 12,
  },
  suggestionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  timestampText: {
    fontSize: 12,
    color: '#999',
  },
  decisionButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  decisionButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    width: '90%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  modalSubtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  decisionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  decisionOption: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#ddd',
    alignItems: 'center',
  },
  decisionOptionSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#E3F2FD',
  },
  decisionOptionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  decisionOptionTextSelected: {
    color: '#007AFF',
  },
  reasoningInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    textAlignVertical: 'top',
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    color: '#666',
  },
  submitButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#007AFF',
    alignItems: 'center',
  },
  submitButtonText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '600',
  },
});

export default TradeSuggestionsScreen;
