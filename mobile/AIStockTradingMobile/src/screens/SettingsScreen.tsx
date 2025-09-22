import React, {useState} from 'react';
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
  Switch,
  List,
  Divider,
  Chip,
  Text,
  Dialog,
  Portal,
} from 'react-native-paper';
import {useStore} from '../context/StoreContext';
import {stockAPI} from '../services/api';

const SettingsScreen = () => {
  const {state, dispatch} = useStore();
  const [investmentDialogVisible, setInvestmentDialogVisible] = useState(false);
  const [riskTolerance, setRiskTolerance] = useState(state.investmentSettings.riskTolerance);
  const [investmentAmount, setInvestmentAmount] = useState(state.investmentSettings.investmentAmount.toString());
  const [stopLossPercentage, setStopLossPercentage] = useState(state.investmentSettings.stopLossPercentage.toString());
  const [takeProfitPercentage, setTakeProfitPercentage] = useState(state.investmentSettings.takeProfitPercentage.toString());
  const [maxPositionSize, setMaxPositionSize] = useState(state.investmentSettings.maxPositionSize.toString());
  const [diversificationTarget, setDiversificationTarget] = useState(state.investmentSettings.diversificationTarget.toString());
  const [autoRebalance, setAutoRebalance] = useState(state.investmentSettings.autoRebalance);

  const saveInvestmentSettings = () => {
    try {
      const settings = {
        riskTolerance,
        investmentAmount: parseInt(investmentAmount),
        preferredCurrencies: state.investmentSettings.preferredCurrencies,
        autoRebalance,
        stopLossPercentage: parseInt(stopLossPercentage),
        takeProfitPercentage: parseInt(takeProfitPercentage),
        maxPositionSize: parseInt(maxPositionSize),
        diversificationTarget: parseInt(diversificationTarget),
      };

      dispatch({type: 'UPDATE_INVESTMENT_SETTINGS', payload: settings});
      setInvestmentDialogVisible(false);
      Alert.alert('Success', 'Investment settings updated successfully');
    } catch (error) {
      Alert.alert('Error', 'Please check your input values');
    }
  };

  const resetToDefaults = () => {
    Alert.alert(
      'Reset to Defaults',
      'Are you sure you want to reset all settings to default values?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            dispatch({
              type: 'UPDATE_INVESTMENT_SETTINGS',
              payload: {
                riskTolerance: 'moderate',
                investmentAmount: 10000,
                preferredCurrencies: ['USD'],
                autoRebalance: false,
                stopLossPercentage: 10,
                takeProfitPercentage: 20,
                maxPositionSize: 20,
                diversificationTarget: 10,
              },
            });
            Alert.alert('Success', 'Settings reset to defaults');
          },
        },
      ],
    );
  };

  const marketInfo = stockAPI.getMarketInfo(state.currentMarket);

  return (
    <ScrollView style={styles.container}>
      {/* Current Market */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Current Market</Title>
          <View style={styles.marketInfo}>
            <Text style={styles.label}>Market:</Text>
            <Text style={styles.value}>{marketInfo.name}</Text>
          </View>
          <View style={styles.marketInfo}>
            <Text style={styles.label}>Currency:</Text>
            <Text style={styles.value}>{marketInfo.currency}</Text>
          </View>
          <View style={styles.marketInfo}>
            <Text style={styles.label}>Exchanges:</Text>
            <Text style={styles.value}>{marketInfo.exchanges.join(', ')}</Text>
          </View>
          <View style={styles.chipContainer}>
            {Object.keys(stockAPI.getMarketInfo()).map((market) => (
              <Chip
                key={market}
                selected={state.currentMarket === market}
                onPress={() => dispatch({type: 'SET_CURRENT_MARKET', payload: market})}
                style={styles.chip}>
                {market}
              </Chip>
            ))}
          </View>
        </Card.Content>
      </Card>

      {/* Investment Settings */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Investment Settings</Title>
          <List.Item
            title="Risk Tolerance"
            description={state.investmentSettings.riskTolerance.charAt(0).toUpperCase() + state.investmentSettings.riskTolerance.slice(1)}
            left={(props) => <List.Icon {...props} icon="shield" />}
            onPress={() => setInvestmentDialogVisible(true)}
          />
          <Divider />
          <List.Item
            title="Investment Amount"
            description={`$${state.investmentSettings.investmentAmount.toLocaleString()}`}
            left={(props) => <List.Icon {...props} icon="currency-usd" />}
            onPress={() => setInvestmentDialogVisible(true)}
          />
          <Divider />
          <List.Item
            title="Stop Loss"
            description={`${state.investmentSettings.stopLossPercentage}%`}
            left={(props) => <List.Icon {...props} icon="trending-down" />}
            onPress={() => setInvestmentDialogVisible(true)}
          />
          <Divider />
          <List.Item
            title="Take Profit"
            description={`${state.investmentSettings.takeProfitPercentage}%`}
            left={(props) => <List.Icon {...props} icon="trending-up" />}
            onPress={() => setInvestmentDialogVisible(true)}
          />
          <Divider />
          <List.Item
            title="Max Position Size"
            description={`${state.investmentSettings.maxPositionSize}%`}
            left={(props) => <List.Icon {...props} icon="chart-pie" />}
            onPress={() => setInvestmentDialogVisible(true)}
          />
          <Divider />
          <List.Item
            title="Auto Rebalancing"
            description={state.investmentSettings.autoRebalance ? 'Enabled' : 'Disabled'}
            left={(props) => <List.Icon {...props} icon="refresh" />}
            right={() => (
              <Switch
                value={state.investmentSettings.autoRebalance}
                onValueChange={(value) =>
                  dispatch({
                    type: 'UPDATE_INVESTMENT_SETTINGS',
                    payload: {autoRebalance: value},
                  })
                }
              />
            )}
          />
        </Card.Content>
      </Card>

      {/* App Settings */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>App Settings</Title>
          <List.Item
            title="Default Stock Symbol"
            description={state.currentSymbol}
            left={(props) => <List.Icon {...props} icon="chart-line" />}
          />
          <Divider />
          <List.Item
            title="Default Period"
            description={state.currentPeriod}
            left={(props) => <List.Icon {...props} icon="calendar" />}
          />
          <Divider />
          <List.Item
            title="Notifications"
            description="Price alerts and updates"
            left={(props) => <List.Icon {...props} icon="bell" />}
            right={() => <Switch value={true} onValueChange={() => {}} />}
          />
          <Divider />
          <List.Item
            title="Dark Mode"
            description="Use dark theme"
            left={(props) => <List.Icon {...props} icon="theme-light-dark" />}
            right={() => <Switch value={false} onValueChange={() => {}} />}
          />
        </Card.Content>
      </Card>

      {/* Data & Privacy */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Data & Privacy</Title>
          <List.Item
            title="Export Portfolio Data"
            description="Download your portfolio as CSV"
            left={(props) => <List.Icon {...props} icon="download" />}
            onPress={() => Alert.alert('Info', 'Export feature coming soon')}
          />
          <Divider />
          <List.Item
            title="Clear Cache"
            description="Clear stored data"
            left={(props) => <List.Icon {...props} icon="delete" />}
            onPress={() => Alert.alert('Info', 'Cache cleared')}
          />
          <Divider />
          <List.Item
            title="Privacy Policy"
            description="Read our privacy policy"
            left={(props) => <List.Icon {...props} icon="shield-account" />}
            onPress={() => Alert.alert('Info', 'Privacy policy coming soon')}
          />
        </Card.Content>
      </Card>

      {/* About */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>About</Title>
          <List.Item
            title="Version"
            description="1.0.0"
            left={(props) => <List.Icon {...props} icon="information" />}
          />
          <Divider />
          <List.Item
            title="Terms of Service"
            description="Read our terms of service"
            left={(props) => <List.Icon {...props} icon="file-document" />}
            onPress={() => Alert.alert('Info', 'Terms of service coming soon')}
          />
          <Divider />
          <List.Item
            title="Contact Support"
            description="Get help and support"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            onPress={() => Alert.alert('Info', 'Contact support coming soon')}
          />
        </Card.Content>
      </Card>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <Button
          mode="outlined"
          onPress={() => setInvestmentDialogVisible(true)}
          style={styles.actionButton}>
          Edit Investment Settings
        </Button>
        <Button
          mode="outlined"
          onPress={resetToDefaults}
          style={styles.actionButton}
          buttonColor="#ef4444">
          Reset to Defaults
        </Button>
      </View>

      {/* Investment Settings Dialog */}
      <Portal>
        <Dialog visible={investmentDialogVisible} onDismiss={() => setInvestmentDialogVisible(false)}>
          <Dialog.Title>Investment Settings</Dialog.Title>
          <Dialog.Content>
            <Text style={styles.dialogLabel}>Risk Tolerance</Text>
            <View style={styles.riskContainer}>
              {['conservative', 'moderate', 'aggressive'].map((risk) => (
                <Chip
                  key={risk}
                  selected={riskTolerance === risk}
                  onPress={() => setRiskTolerance(risk as any)}
                  style={styles.riskChip}>
                  {risk.charAt(0).toUpperCase() + risk.slice(1)}
                </Chip>
              ))}
            </View>

            <TextInput
              label="Investment Amount ($)"
              value={investmentAmount}
              onChangeText={setInvestmentAmount}
              style={styles.dialogInput}
              mode="outlined"
              keyboardType="numeric"
            />

            <TextInput
              label="Stop Loss Percentage (%)"
              value={stopLossPercentage}
              onChangeText={setStopLossPercentage}
              style={styles.dialogInput}
              mode="outlined"
              keyboardType="numeric"
            />

            <TextInput
              label="Take Profit Percentage (%)"
              value={takeProfitPercentage}
              onChangeText={setTakeProfitPercentage}
              style={styles.dialogInput}
              mode="outlined"
              keyboardType="numeric"
            />

            <TextInput
              label="Max Position Size (%)"
              value={maxPositionSize}
              onChangeText={setMaxPositionSize}
              style={styles.dialogInput}
              mode="outlined"
              keyboardType="numeric"
            />

            <TextInput
              label="Diversification Target"
              value={diversificationTarget}
              onChangeText={setDiversificationTarget}
              style={styles.dialogInput}
              mode="outlined"
              keyboardType="numeric"
            />

            <View style={styles.switchContainer}>
              <Text>Auto Rebalancing</Text>
              <Switch value={autoRebalance} onValueChange={setAutoRebalance} />
            </View>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setInvestmentDialogVisible(false)}>Cancel</Button>
            <Button onPress={saveInvestmentSettings}>Save</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
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
  marketInfo: {
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
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  actionButtons: {
    marginBottom: 32,
  },
  actionButton: {
    marginBottom: 8,
  },
  dialogLabel: {
    fontWeight: '600',
    marginBottom: 8,
    color: '#1e293b',
  },
  riskContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 8,
  },
  riskChip: {
    marginRight: 8,
  },
  dialogInput: {
    marginBottom: 16,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
});

export default SettingsScreen; 