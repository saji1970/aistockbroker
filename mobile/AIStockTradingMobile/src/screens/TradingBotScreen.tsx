import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Switch,
  TextInput,
  Chip,
  ProgressBar,
  Divider,
  List,
  IconButton,
  Badge,
  Surface,
  useTheme,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {tradingBotAPI} from '../services/api';
import {showMessage} from 'react-native-flash-message';
import {useFocusEffect} from '@react-navigation/native';

const {width: screenWidth} = Dimensions.get('window');

interface BotConfig {
  initial_capital: number;
  target_amount?: number;
  trading_period_days: number;
  max_position_size: number;
  max_daily_loss: number;
  risk_tolerance: 'low' | 'medium' | 'high';
  trading_strategy: 'momentum' | 'mean_reversion' | 'rsi' | 'ml';
  enable_ml_learning: boolean;
}

interface BotStatus {
  status: 'running' | 'stopped' | 'error';
  watchlist: string[];
  last_update: string;
}

interface Portfolio {
  cash: number;
  total_value: number;
  positions: {[key: string]: any};
  orders: any[];
  performance_metrics: {[key: string]: number};
}

const TradingBotScreen: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [orders, setOrders] = useState<any[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [config, setConfig] = useState<BotConfig>({
    initial_capital: 100000,
    target_amount: undefined,
    trading_period_days: 30,
    max_position_size: 0.1,
    max_daily_loss: 0.05,
    risk_tolerance: 'medium',
    trading_strategy: 'momentum',
    enable_ml_learning: true,
  });
  const [isConfigSaved, setIsConfigSaved] = useState(false);

  const fetchBotData = async () => {
    try {
      setLoading(true);
      const data = await tradingBotAPI.getAllBotData();
      
      if (data.status) setBotStatus(data.status);
      if (data.portfolio) setPortfolio(data.portfolio);
      if (data.orders) setOrders(data.orders);
      if (data.watchlist) setWatchlist(data.watchlist.watchlist || []);
    } catch (error) {
      console.error('Error fetching bot data:', error);
      showMessage({
        message: 'Error',
        description: 'Failed to fetch bot data',
        type: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchBotData();
    setRefreshing(false);
  };

  useFocusEffect(
    React.useCallback(() => {
      fetchBotData();
    }, [])
  );

  const handleStartBot = async () => {
    try {
      setLoading(true);
      await tradingBotAPI.startBot(config);
      showMessage({
        message: 'Success',
        description: 'Trading bot started successfully',
        type: 'success',
      });
      await fetchBotData();
    } catch (error) {
      console.error('Error starting bot:', error);
      showMessage({
        message: 'Error',
        description: 'Failed to start trading bot',
        type: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStopBot = async () => {
    Alert.alert(
      'Stop Trading Bot',
      'Are you sure you want to stop the trading bot?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Stop',
          style: 'destructive',
          onPress: async () => {
            try {
              setLoading(true);
              await tradingBotAPI.stopBot();
              showMessage({
                message: 'Success',
                description: 'Trading bot stopped successfully',
                type: 'success',
              });
              await fetchBotData();
            } catch (error) {
              console.error('Error stopping bot:', error);
              showMessage({
                message: 'Error',
                description: 'Failed to stop trading bot',
                type: 'danger',
              });
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return '#10b981';
      case 'stopped':
        return '#ef4444';
      case 'error':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return 'play-circle-filled';
      case 'stopped':
        return 'stop-circle';
      case 'error':
        return 'error';
      default:
        return 'help';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      {/* Bot Status Card */}
      <Card style={styles.statusCard}>
        <Card.Content>
          <View style={styles.statusHeader}>
            <View style={styles.statusInfo}>
              <Icon
                name={getStatusIcon(botStatus?.status || 'stopped')}
                size={24}
                color={getStatusColor(botStatus?.status || 'stopped')}
              />
              <Title style={styles.statusTitle}>
                Bot Status: {botStatus?.status?.toUpperCase() || 'STOPPED'}
              </Title>
            </View>
            <Badge
              style={[
                styles.statusBadge,
                {backgroundColor: getStatusColor(botStatus?.status || 'stopped')},
              ]}>
              {botStatus?.status || 'stopped'}
            </Badge>
          </View>
          
          {portfolio && (
            <View style={styles.portfolioSummary}>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Portfolio Value</Text>
                <Text style={styles.metricValue}>
                  ${portfolio.total_value.toLocaleString()}
                </Text>
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Cash</Text>
                <Text style={styles.metricValue}>
                  ${portfolio.cash.toLocaleString()}
                </Text>
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Positions</Text>
                <Text style={styles.metricValue}>
                  {Object.keys(portfolio.positions).length}
                </Text>
              </View>
            </View>
          )}
        </Card.Content>
      </Card>

      {/* Configuration Card */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Bot Configuration</Title>
          
          <TextInput
            label="Initial Capital ($)"
            value={config.initial_capital.toString()}
            onChangeText={(text) =>
              setConfig({...config, initial_capital: parseFloat(text) || 0})
            }
            keyboardType="numeric"
            mode="outlined"
            style={styles.input}
          />

          <TextInput
            label="Trading Period (days)"
            value={config.trading_period_days.toString()}
            onChangeText={(text) =>
              setConfig({...config, trading_period_days: parseInt(text) || 30})
            }
            keyboardType="numeric"
            mode="outlined"
            style={styles.input}
          />

          <View style={styles.switchContainer}>
            <Text>Enable ML Learning</Text>
            <Switch
              value={config.enable_ml_learning}
              onValueChange={(value) =>
                setConfig({...config, enable_ml_learning: value})
              }
            />
          </View>

          <View style={styles.buttonContainer}>
            <Button
              mode="contained"
              onPress={handleStartBot}
              disabled={loading || botStatus?.status === 'running'}
              style={styles.button}>
              Start Bot
            </Button>
            <Button
              mode="outlined"
              onPress={handleStopBot}
              disabled={loading || botStatus?.status === 'stopped'}
              style={styles.button}>
              Stop Bot
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* Watchlist Card */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Watchlist ({watchlist.length})</Title>
          {watchlist.length === 0 ? (
            <Paragraph>No symbols in watchlist</Paragraph>
          ) : (
            <View style={styles.watchlistContainer}>
              {watchlist.map((symbol) => (
                <Chip
                  key={symbol}
                  mode="outlined"
                  style={styles.watchlistChip}>
                  {symbol}
                </Chip>
              ))}
            </View>
          )}
        </Card.Content>
      </Card>

      {/* Recent Orders Card */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Recent Orders</Title>
          {orders.length === 0 ? (
            <Paragraph>No recent orders</Paragraph>
          ) : (
            orders.slice(0, 5).map((order) => (
              <View key={order.id} style={styles.orderItem}>
                <View style={styles.orderInfo}>
                  <Text style={styles.orderSymbol}>{order.symbol}</Text>
                  <Text style={styles.orderType}>
                    {order.order_type} {order.quantity} @ ${order.price.toFixed(2)}
                  </Text>
                </View>
                <Chip
                  mode="outlined"
                  textStyle={{fontSize: 12}}
                  style={[
                    styles.orderChip,
                    {
                      backgroundColor: order.order_type === 'BUY' ? '#dcfce7' : '#fef2f2',
                    },
                  ]}>
                  {order.order_type}
                </Chip>
              </View>
            ))
          )}
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  statusCard: {
    margin: 16,
    elevation: 4,
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusTitle: {
    marginLeft: 8,
    fontSize: 18,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  portfolioSummary: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  metric: {
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  card: {
    margin: 16,
    elevation: 4,
  },
  input: {
    marginBottom: 16,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  button: {
    flex: 1,
    marginHorizontal: 4,
  },
  watchlistContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  watchlistChip: {
    marginBottom: 8,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  orderInfo: {
    flex: 1,
  },
  orderSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  orderType: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  orderChip: {
    height: 28,
  },
});

export default TradingBotScreen;