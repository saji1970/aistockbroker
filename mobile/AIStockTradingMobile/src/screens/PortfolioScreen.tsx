import React, {useState, useEffect} from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  TextInput,
  DataTable,
  Chip,
  ActivityIndicator,
  Text,
  Dialog,
  Portal,
} from 'react-native-paper';
import {useStore} from '../context/StoreContext';
import {stockAPI, portfolioAPI} from '../services/api';

const PortfolioScreen = () => {
  const {state, dispatch} = useStore();
  const [loading, setLoading] = useState(false);
  const [buyDialogVisible, setBuyDialogVisible] = useState(false);
  const [sellDialogVisible, setSellDialogVisible] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState<any>(null);
  const [buySymbol, setBuySymbol] = useState('');
  const [buyShares, setBuyShares] = useState('');
  const [sellShares, setSellShares] = useState('');

  const initializePortfolio = async () => {
    try {
      setLoading(true);
      const response = await portfolioAPI.initializePortfolio(10000);
      dispatch({type: 'UPDATE_PORTFOLIO', payload: response});
      Alert.alert('Success', 'Portfolio initialized with $10,000');
    } catch (error) {
      Alert.alert('Error', 'Failed to initialize portfolio');
    } finally {
      setLoading(false);
    }
  };

  const addCapital = async () => {
    try {
      setLoading(true);
      const response = await portfolioAPI.addCapital(5000);
      dispatch({type: 'UPDATE_PORTFOLIO', payload: response});
      Alert.alert('Success', 'Added $5,000 to portfolio');
    } catch (error) {
      Alert.alert('Error', 'Failed to add capital');
    } finally {
      setLoading(false);
    }
  };

  const buyStock = async () => {
    if (!buySymbol.trim() || !buyShares.trim()) {
      Alert.alert('Error', 'Please enter symbol and shares');
      return;
    }

    try {
      setLoading(true);
      const shares = parseInt(buyShares);
      const stockInfo = await stockAPI.getStockInfo(buySymbol, state.currentMarket);
      const price = stockInfo.current_price;

      const response = await portfolioAPI.buyStock(buySymbol, shares, price);
      dispatch({type: 'UPDATE_PORTFOLIO', payload: response});
      
      setBuyDialogVisible(false);
      setBuySymbol('');
      setBuyShares('');
      Alert.alert('Success', `Bought ${shares} shares of ${buySymbol} at $${price}`);
    } catch (error) {
      Alert.alert('Error', 'Failed to buy stock');
    } finally {
      setLoading(false);
    }
  };

  const sellStock = async () => {
    if (!selectedPosition || !sellShares.trim()) {
      Alert.alert('Error', 'Please select position and enter shares');
      return;
    }

    try {
      setLoading(true);
      const shares = parseInt(sellShares);
      if (shares > selectedPosition.shares) {
        Alert.alert('Error', 'Cannot sell more shares than you own');
        return;
      }

      const stockInfo = await stockAPI.getStockInfo(selectedPosition.symbol, state.currentMarket);
      const price = stockInfo.current_price;

      const response = await portfolioAPI.sellStock(selectedPosition.symbol, shares, price);
      dispatch({type: 'UPDATE_PORTFOLIO', payload: response});
      
      setSellDialogVisible(false);
      setSelectedPosition(null);
      setSellShares('');
      Alert.alert('Success', `Sold ${shares} shares of ${selectedPosition.symbol} at $${price}`);
    } catch (error) {
      Alert.alert('Error', 'Failed to sell stock');
    } finally {
      setLoading(false);
    }
  };

  const resetPortfolio = async () => {
    Alert.alert(
      'Reset Portfolio',
      'Are you sure you want to reset your portfolio? This action cannot be undone.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Reset',
          style: 'destructive',
          onPress: async () => {
            try {
              setLoading(true);
              const response = await portfolioAPI.resetPortfolio();
              dispatch({type: 'UPDATE_PORTFOLIO', payload: response});
              Alert.alert('Success', 'Portfolio reset successfully');
            } catch (error) {
              Alert.alert('Error', 'Failed to reset portfolio');
            } finally {
              setLoading(false);
            }
          },
        },
      ],
    );
  };

  const totalGainLoss = state.portfolio.positions.reduce((sum, pos) => sum + pos.gainLoss, 0);
  const totalGainLossPercentage = state.portfolio.totalValue > 0 
    ? (totalGainLoss / (state.portfolio.totalValue - totalGainLoss)) * 100 
    : 0;

  return (
    <ScrollView style={styles.container}>
      {/* Portfolio Summary */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Portfolio Summary</Title>
          <View style={styles.summaryRow}>
            <Text style={styles.label}>Total Value:</Text>
            <Text style={styles.value}>${state.portfolio.totalValue.toLocaleString()}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.label}>Cash:</Text>
            <Text style={styles.value}>${state.portfolio.cash.toLocaleString()}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.label}>Total Gain/Loss:</Text>
            <Text style={[styles.value, {color: totalGainLoss >= 0 ? 'green' : 'red'}]}>
              {totalGainLoss >= 0 ? '+' : ''}${totalGainLoss.toLocaleString()} ({totalGainLossPercentage.toFixed(2)}%)
            </Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.label}>Last Updated:</Text>
            <Text style={styles.value}>
              {new Date(state.portfolio.lastUpdated).toLocaleString()}
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Portfolio Actions */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Portfolio Actions</Title>
          <View style={styles.actionButtons}>
            <Button
              mode="outlined"
              onPress={() => setBuyDialogVisible(true)}
              style={styles.actionButton}
              disabled={loading}>
              Buy Stock
            </Button>
            <Button
              mode="outlined"
              onPress={addCapital}
              style={styles.actionButton}
              disabled={loading}>
              Add Capital
            </Button>
            <Button
              mode="outlined"
              onPress={initializePortfolio}
              style={styles.actionButton}
              disabled={loading}>
              Initialize
            </Button>
            <Button
              mode="outlined"
              onPress={resetPortfolio}
              style={styles.actionButton}
              disabled={loading}
              buttonColor="#ef4444">
              Reset
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* Positions */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Positions ({state.portfolio.positions.length})</Title>
          {state.portfolio.positions.length === 0 ? (
            <Text style={styles.emptyText}>No positions yet. Buy some stocks to get started!</Text>
          ) : (
            <DataTable>
              <DataTable.Header>
                <DataTable.Title>Symbol</DataTable.Title>
                <DataTable.Title numeric>Shares</DataTable.Title>
                <DataTable.Title numeric>Avg Price</DataTable.Title>
                <DataTable.Title numeric>Current</DataTable.Title>
                <DataTable.Title numeric>G/L</DataTable.Title>
              </DataTable.Header>

              {state.portfolio.positions.map((position, index) => (
                <DataTable.Row
                  key={index}
                  onPress={() => {
                    setSelectedPosition(position);
                    setSellDialogVisible(true);
                  }}>
                  <DataTable.Cell>
                    <Text style={styles.symbolText}>{position.symbol}</Text>
                  </DataTable.Cell>
                  <DataTable.Cell numeric>{position.shares}</DataTable.Cell>
                  <DataTable.Cell numeric>${position.averagePrice.toFixed(2)}</DataTable.Cell>
                  <DataTable.Cell numeric>${position.currentPrice.toFixed(2)}</DataTable.Cell>
                  <DataTable.Cell numeric>
                    <Text style={{color: position.gainLoss >= 0 ? 'green' : 'red'}}>
                      {position.gainLoss >= 0 ? '+' : ''}${position.gainLoss.toFixed(2)}
                    </Text>
                  </DataTable.Cell>
                </DataTable.Row>
              ))}
            </DataTable>
          )}
        </Card.Content>
      </Card>

      {/* Performance */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Performance</Title>
          <View style={styles.performanceRow}>
            <Text style={styles.label}>Total Return:</Text>
            <Text style={[styles.value, {color: state.portfolio.performance.totalReturn >= 0 ? 'green' : 'red'}]}>
              {state.portfolio.performance.totalReturn >= 0 ? '+' : ''}${state.portfolio.performance.totalReturn.toFixed(2)} ({state.portfolio.performance.totalReturnPercentage.toFixed(2)}%)
            </Text>
          </View>
          <View style={styles.performanceRow}>
            <Text style={styles.label}>Daily Return:</Text>
            <Text style={[styles.value, {color: state.portfolio.performance.dailyReturn >= 0 ? 'green' : 'red'}]}>
              {state.portfolio.performance.dailyReturn >= 0 ? '+' : ''}${state.portfolio.performance.dailyReturn.toFixed(2)} ({state.portfolio.performance.dailyReturnPercentage.toFixed(2)}%)
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Buy Dialog */}
      <Portal>
        <Dialog visible={buyDialogVisible} onDismiss={() => setBuyDialogVisible(false)}>
          <Dialog.Title>Buy Stock</Dialog.Title>
          <Dialog.Content>
            <TextInput
              label="Stock Symbol"
              value={buySymbol}
              onChangeText={setBuySymbol}
              style={styles.dialogInput}
              mode="outlined"
            />
            <TextInput
              label="Number of Shares"
              value={buyShares}
              onChangeText={setBuyShares}
              style={styles.dialogInput}
              mode="outlined"
              keyboardType="numeric"
            />
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setBuyDialogVisible(false)}>Cancel</Button>
            <Button onPress={buyStock} disabled={loading}>Buy</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>

      {/* Sell Dialog */}
      <Portal>
        <Dialog visible={sellDialogVisible} onDismiss={() => setSellDialogVisible(false)}>
          <Dialog.Title>Sell {selectedPosition?.symbol}</Dialog.Title>
          <Dialog.Content>
            <Text>Available shares: {selectedPosition?.shares}</Text>
            <TextInput
              label="Number of Shares to Sell"
              value={sellShares}
              onChangeText={setSellShares}
              style={styles.dialogInput}
              mode="outlined"
              keyboardType="numeric"
            />
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setSellDialogVisible(false)}>Cancel</Button>
            <Button onPress={sellStock} disabled={loading}>Sell</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" />
          <Text style={styles.loadingText}>Processing...</Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 2,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  label: {
    fontWeight: '600',
    color: '#64748b',
  },
  value: {
    fontWeight: 'bold',
    color: '#1e293b',
  },
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  actionButton: {
    flex: 1,
    minWidth: '45%',
  },
  symbolText: {
    fontWeight: 'bold',
  },
  emptyText: {
    textAlign: 'center',
    color: '#64748b',
    fontStyle: 'italic',
    marginTop: 16,
  },
  performanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  dialogInput: {
    marginBottom: 16,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#ffffff',
    marginTop: 8,
  },
});

export default PortfolioScreen; 