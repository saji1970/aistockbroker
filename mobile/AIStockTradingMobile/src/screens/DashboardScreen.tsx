import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  ProgressBar,
  useTheme,
  Surface,
  IconButton,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {stockAPI, tradingBotAPI, networkAPI} from '../services/api';
import {showMessage} from 'react-native-flash-message';
import StockChart from '../components/Charts/StockChart';

const {width: screenWidth} = Dimensions.get('window');

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
}

interface BotStatus {
  status: 'running' | 'stopped' | 'error';
  portfolio_value?: number;
  total_trades?: number;
  profit_loss?: number;
}

const DashboardScreen: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null);
  const [networkStatus, setNetworkStatus] = useState<any>(null);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');

  const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA'];

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      const promises = popularStocks.map(async (symbol) => {
        try {
          const data = await stockAPI.getStockData(symbol, '1d');
          if (data && data.data && data.data.length > 0) {
            const latest = data.data[data.data.length - 1];
            const previous = data.data[data.data.length - 2] || latest;
            
            return {
              symbol,
              price: parseFloat(latest.Close || latest.close),
              change: parseFloat(latest.Close || latest.close) - parseFloat(previous.Close || previous.close),
              changePercent: ((parseFloat(latest.Close || latest.close) - parseFloat(previous.Close || previous.close)) / parseFloat(previous.Close || previous.close)) * 100,
              volume: parseInt(latest.Volume || latest.volume),
            };
          }
        } catch (error) {
          console.error(`Error fetching data for ${symbol}:`, error);
        }
        return null;
      });

      const results = await Promise.all(promises);
      setMarketData(results.filter(Boolean) as MarketData[]);
    } catch (error) {
      console.error('Error fetching market data:', error);
      showMessage({
        message: 'Error',
        description: 'Failed to fetch market data',
        type: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchBotStatus = async () => {
    try {
      const status = await tradingBotAPI.getStatus();
      setBotStatus(status);
    } catch (error) {
      console.error('Error fetching bot status:', error);
    }
  };

  const fetchNetworkStatus = async () => {
    try {
      const status = await networkAPI.getNetworkInfo();
      setNetworkStatus(status);
    } catch (error) {
      console.error('Error fetching network status:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([
      fetchMarketData(),
      fetchBotStatus(),
      fetchNetworkStatus(),
    ]);
    setRefreshing(false);
  };

  useEffect(() => {
    onRefresh();
  }, []);

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

  const renderMarketOverview = () => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.cardHeader}>
          <Title>Market Overview</Title>
          <IconButton
            icon="refresh"
            size={20}
            onPress={fetchMarketData}
          />
        </View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {marketData.map((stock) => (
            <TouchableOpacity
              key={stock.symbol}
              onPress={() => setSelectedSymbol(stock.symbol)}
              style={[
                styles.stockCard,
                selectedSymbol === stock.symbol && styles.selectedStock,
              ]}>
              <Text style={styles.stockSymbol}>{stock.symbol}</Text>
              <Text style={styles.stockPrice}>${stock.price.toFixed(2)}</Text>
              <Text
                style={[
                  styles.stockChange,
                  {
                    color: stock.change >= 0 ? '#10b981' : '#ef4444',
                  },
                ]}>
                {stock.change >= 0 ? '+' : ''}
                {stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </Card.Content>
    </Card>
  );

  const renderTradingBotStatus = () => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.cardHeader}>
          <Title>Trading Bot Status</Title>
          <IconButton
            icon="refresh"
            size={20}
            onPress={fetchBotStatus}
          />
        </View>
        
        <View style={styles.botStatusContainer}>
          <View style={styles.botStatusInfo}>
            <Icon
              name={getStatusIcon(botStatus?.status || 'stopped')}
              size={24}
              color={getStatusColor(botStatus?.status || 'stopped')}
            />
            <View style={styles.botStatusText}>
              <Text style={styles.botStatusTitle}>
                {botStatus?.status?.toUpperCase() || 'STOPPED'}
              </Text>
              <Text style={styles.botStatusSubtitle}>
                {botStatus?.status === 'running' ? 'Bot is actively trading' : 'Bot is not running'}
              </Text>
            </View>
          </View>
          
          {botStatus?.portfolio_value && (
            <View style={styles.botMetrics}>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Portfolio Value</Text>
                <Text style={styles.metricValue}>
                  ${botStatus.portfolio_value.toLocaleString()}
                </Text>
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>Total Trades</Text>
                <Text style={styles.metricValue}>
                  {botStatus.total_trades || 0}
                </Text>
              </View>
              <View style={styles.metric}>
                <Text style={styles.metricLabel}>P&L</Text>
                <Text
                  style={[
                    styles.metricValue,
                    {
                      color: (botStatus.profit_loss || 0) >= 0 ? '#10b981' : '#ef4444',
                    },
                  ]}>
                  ${(botStatus.profit_loss || 0).toLocaleString()}
                </Text>
              </View>
            </View>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  const renderNetworkStatus = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title>System Status</Title>
        <View style={styles.networkStatusContainer}>
          <View style={styles.networkItem}>
            <Icon
              name={networkStatus?.api ? 'check-circle' : 'error'}
              size={20}
              color={networkStatus?.api ? '#10b981' : '#ef4444'}
            />
            <Text style={styles.networkLabel}>Main API</Text>
            <Chip
              mode="outlined"
              textStyle={{fontSize: 12}}
              style={[
                styles.networkChip,
                {
                  backgroundColor: networkStatus?.api ? '#dcfce7' : '#fef2f2',
                },
              ]}>
              {networkStatus?.api ? 'Online' : 'Offline'}
            </Chip>
          </View>
          
          <View style={styles.networkItem}>
            <Icon
              name={networkStatus?.tradingBot ? 'check-circle' : 'error'}
              size={20}
              color={networkStatus?.tradingBot ? '#10b981' : '#ef4444'}
            />
            <Text style={styles.networkLabel}>Trading Bot</Text>
            <Chip
              mode="outlined"
              textStyle={{fontSize: 12}}
              style={[
                styles.networkChip,
                {
                  backgroundColor: networkStatus?.tradingBot ? '#dcfce7' : '#fef2f2',
                },
              ]}>
              {networkStatus?.tradingBot ? 'Online' : 'Offline'}
            </Chip>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderQuickActions = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title>Quick Actions</Title>
        <View style={styles.quickActionsContainer}>
          <TouchableOpacity style={styles.quickAction}>
            <Icon name="psychology" size={24} color={theme.colors.primary} />
            <Text style={styles.quickActionText}>Start Bot</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.quickAction}>
            <Icon name="analytics" size={24} color={theme.colors.primary} />
            <Text style={styles.quickActionText}>Analysis</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.quickAction}>
            <Icon name="smart-toy" size={24} color={theme.colors.primary} />
            <Text style={styles.quickActionText}>AI Assistant</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.quickAction}>
            <Icon name="account-balance-wallet" size={24} color={theme.colors.primary} />
            <Text style={styles.quickActionText}>Portfolio</Text>
          </TouchableOpacity>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      {/* Market Overview */}
      {renderMarketOverview()}

      {/* Trading Bot Status */}
      {renderTradingBotStatus()}

      {/* Network Status */}
      {renderNetworkStatus()}

      {/* Stock Chart */}
      <StockChart
        symbol={selectedSymbol}
        period="1mo"
        height={250}
        showVolume={true}
      />

      {/* Quick Actions */}
      {renderQuickActions()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  card: {
    margin: 16,
    elevation: 4,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  stockCard: {
    width: 120,
    padding: 16,
    marginRight: 12,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  selectedStock: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },
  stockSymbol: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  stockPrice: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginTop: 4,
  },
  stockChange: {
    fontSize: 12,
    fontWeight: '500',
    marginTop: 4,
  },
  botStatusContainer: {
    marginTop: 8,
  },
  botStatusInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  botStatusText: {
    marginLeft: 12,
    flex: 1,
  },
  botStatusTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  botStatusSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  botMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
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
  networkStatusContainer: {
    marginTop: 16,
  },
  networkItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  networkLabel: {
    fontSize: 14,
    color: '#1f2937',
    marginLeft: 12,
    flex: 1,
  },
  networkChip: {
    height: 24,
  },
  quickActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  quickAction: {
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    minWidth: 80,
  },
  quickActionText: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default DashboardScreen;