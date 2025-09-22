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
  Chip,
  ActivityIndicator,
  Text,
  DataTable,
} from 'react-native-paper';
import {LineChart} from 'react-native-chart-kit';
import {Dimensions} from 'react-native';
import {useStore} from '../context/StoreContext';
import {stockAPI} from '../services/api';

const screenWidth = Dimensions.get('window').width;

const AnalysisScreen = () => {
  const {state} = useStore();
  const [stockData, setStockData] = useState<any>(null);
  const [technicalData, setTechnicalData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [searchSymbol, setSearchSymbol] = useState(state.currentSymbol);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [data, technical] = await Promise.all([
        stockAPI.getStockData(state.currentSymbol, state.currentPeriod, state.currentMarket),
        stockAPI.getTechnicalIndicators(state.currentSymbol, state.currentPeriod, state.currentMarket),
      ]);
      setStockData(data);
      setTechnicalData(technical);
    } catch (error) {
      Alert.alert('Error', 'Failed to fetch analysis data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchSymbol.trim()) {
      // Update the current symbol in the store
      // This will trigger a re-fetch of data
    }
  };

  useEffect(() => {
    fetchData();
  }, [state.currentSymbol, state.currentPeriod, state.currentMarket]);

  const chartData = stockData?.formatted_data
    ? {
        labels: stockData.formatted_data
          .slice(-14)
          .map((item: any) => new Date(item.date).toLocaleDateString()),
        datasets: [
          {
            data: stockData.formatted_data
              .slice(-14)
              .map((item: any) => item.close),
            color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`,
            strokeWidth: 2,
          },
        ],
      }
    : null;

  const marketInfo = stockAPI.getMarketInfo(state.currentMarket);

  const getRSIColor = (rsi: number) => {
    if (rsi > 70) return 'red';
    if (rsi < 30) return 'green';
    return 'orange';
  };

  const getRSISignal = (rsi: number) => {
    if (rsi > 70) return 'Overbought';
    if (rsi < 30) return 'Oversold';
    return 'Neutral';
  };

  return (
    <ScrollView style={styles.container}>
      {/* Search Section */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>Technical Analysis</Title>
          <View style={styles.searchContainer}>
            <TextInput
              label="Stock Symbol"
              value={searchSymbol}
              onChangeText={setSearchSymbol}
              style={styles.searchInput}
              mode="outlined"
            />
            <Button mode="contained" onPress={handleSearch} style={styles.searchButton}>
              Analyze
            </Button>
          </View>
          <View style={styles.chipContainer}>
            <Chip
              selected={state.currentPeriod === '1d'}
              onPress={() => {/* Update period */}}
              style={styles.chip}>
              1D
            </Chip>
            <Chip
              selected={state.currentPeriod === '1w'}
              onPress={() => {/* Update period */}}
              style={styles.chip}>
              1W
            </Chip>
            <Chip
              selected={state.currentPeriod === '1m'}
              onPress={() => {/* Update period */}}
              style={styles.chip}>
              1M
            </Chip>
            <Chip
              selected={state.currentPeriod === '1y'}
              onPress={() => {/* Update period */}}
              style={styles.chip}>
              1Y
            </Chip>
          </View>
        </Card.Content>
      </Card>

      {loading ? (
        <Card style={styles.card}>
          <Card.Content>
            <ActivityIndicator size="large" />
            <Text style={styles.loadingText}>Loading analysis data...</Text>
          </Card.Content>
        </Card>
      ) : (
        <>
          {/* Price Chart */}
          {chartData && (
            <Card style={styles.card}>
              <Card.Content>
                <Title>Price Chart - {state.currentSymbol}</Title>
                <LineChart
                  data={chartData}
                  width={screenWidth - 40}
                  height={220}
                  chartConfig={{
                    backgroundColor: '#ffffff',
                    backgroundGradientFrom: '#ffffff',
                    backgroundGradientTo: '#ffffff',
                    decimalPlaces: 2,
                    color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`,
                    labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                    style: {
                      borderRadius: 16,
                    },
                    propsForDots: {
                      r: '4',
                      strokeWidth: '2',
                      stroke: '#2563eb',
                    },
                  }}
                  bezier
                  style={styles.chart}
                />
              </Card.Content>
            </Card>
          )}

          {/* Technical Indicators */}
          {technicalData && (
            <Card style={styles.card}>
              <Card.Content>
                <Title>Technical Indicators</Title>
                <DataTable>
                  <DataTable.Header>
                    <DataTable.Title>Indicator</DataTable.Title>
                    <DataTable.Title numeric>Value</DataTable.Title>
                    <DataTable.Title>Signal</DataTable.Title>
                  </DataTable.Header>

                  <DataTable.Row>
                    <DataTable.Cell>RSI (14)</DataTable.Cell>
                    <DataTable.Cell numeric>{technicalData.rsi?.toFixed(2)}</DataTable.Cell>
                    <DataTable.Cell>
                      <Text style={{color: getRSIColor(technicalData.rsi)}}>
                        {getRSISignal(technicalData.rsi)}
                      </Text>
                    </DataTable.Cell>
                  </DataTable.Row>

                  <DataTable.Row>
                    <DataTable.Cell>MACD</DataTable.Cell>
                    <DataTable.Cell numeric>{technicalData.macd?.macd?.toFixed(3)}</DataTable.Cell>
                    <DataTable.Cell>
                      <Text style={{color: technicalData.macd?.macd > 0 ? 'green' : 'red'}}>
                        {technicalData.macd?.macd > 0 ? 'Bullish' : 'Bearish'}
                      </Text>
                    </DataTable.Cell>
                  </DataTable.Row>

                  <DataTable.Row>
                    <DataTable.Cell>SMA (20)</DataTable.Cell>
                    <DataTable.Cell numeric>${technicalData.sma?.sma_20?.toFixed(2)}</DataTable.Cell>
                    <DataTable.Cell>
                      <Text style={{color: stockData?.summary?.current_price > technicalData.sma?.sma_20 ? 'green' : 'red'}}>
                        {stockData?.summary?.current_price > technicalData.sma?.sma_20 ? 'Above' : 'Below'}
                      </Text>
                    </DataTable.Cell>
                  </DataTable.Row>

                  <DataTable.Row>
                    <DataTable.Cell>SMA (50)</DataTable.Cell>
                    <DataTable.Cell numeric>${technicalData.sma?.sma_50?.toFixed(2)}</DataTable.Cell>
                    <DataTable.Cell>
                      <Text style={{color: stockData?.summary?.current_price > technicalData.sma?.sma_50 ? 'green' : 'red'}}>
                        {stockData?.summary?.current_price > technicalData.sma?.sma_50 ? 'Above' : 'Below'}
                      </Text>
                    </DataTable.Cell>
                  </DataTable.Row>

                  <DataTable.Row>
                    <DataTable.Cell>ATR</DataTable.Cell>
                    <DataTable.Cell numeric>${technicalData.atr?.toFixed(2)}</DataTable.Cell>
                    <DataTable.Cell>
                      <Text style={{color: technicalData.atr > 2 ? 'red' : 'green'}}>
                        {technicalData.atr > 2 ? 'High' : 'Low'}
                      </Text>
                    </DataTable.Cell>
                  </DataTable.Row>
                </DataTable>
              </Card.Content>
            </Card>
          )}

          {/* Bollinger Bands */}
          {technicalData?.bollinger_bands && (
            <Card style={styles.card}>
              <Card.Content>
                <Title>Bollinger Bands</Title>
                <View style={styles.bollingerContainer}>
                  <View style={styles.bollingerRow}>
                    <Text style={styles.label}>Upper Band:</Text>
                    <Text style={styles.value}>${technicalData.bollinger_bands.upper?.toFixed(2)}</Text>
                  </View>
                  <View style={styles.bollingerRow}>
                    <Text style={styles.label}>Middle Band:</Text>
                    <Text style={styles.value}>${technicalData.bollinger_bands.middle?.toFixed(2)}</Text>
                  </View>
                  <View style={styles.bollingerRow}>
                    <Text style={styles.label}>Lower Band:</Text>
                    <Text style={styles.value}>${technicalData.bollinger_bands.lower?.toFixed(2)}</Text>
                  </View>
                  <View style={styles.bollingerRow}>
                    <Text style={styles.label}>Current Price:</Text>
                    <Text style={styles.value}>${stockData?.summary?.current_price?.toFixed(2)}</Text>
                  </View>
                </View>
                <Paragraph style={styles.analysisText}>
                  {stockData?.summary?.current_price > technicalData.bollinger_bands.upper
                    ? 'Price is above the upper Bollinger Band - potential overbought condition.'
                    : stockData?.summary?.current_price < technicalData.bollinger_bands.lower
                    ? 'Price is below the lower Bollinger Band - potential oversold condition.'
                    : 'Price is within the Bollinger Bands - normal trading range.'}
                </Paragraph>
              </Card.Content>
            </Card>
          )}

          {/* Stochastic Oscillator */}
          {technicalData?.stochastic && (
            <Card style={styles.card}>
              <Card.Content>
                <Title>Stochastic Oscillator</Title>
                <View style={styles.stochasticContainer}>
                  <View style={styles.stochasticRow}>
                    <Text style={styles.label}>%K:</Text>
                    <Text style={styles.value}>{technicalData.stochastic.k?.toFixed(2)}</Text>
                  </View>
                  <View style={styles.stochasticRow}>
                    <Text style={styles.label}>%D:</Text>
                    <Text style={styles.value}>{technicalData.stochastic.d?.toFixed(2)}</Text>
                  </View>
                </View>
                <Paragraph style={styles.analysisText}>
                  {technicalData.stochastic.k > 80
                    ? 'Stochastic indicates overbought conditions.'
                    : technicalData.stochastic.k < 20
                    ? 'Stochastic indicates oversold conditions.'
                    : 'Stochastic is in neutral territory.'}
                </Paragraph>
              </Card.Content>
            </Card>
          )}

          {/* Volume Analysis */}
          {stockData && (
            <Card style={styles.card}>
              <Card.Content>
                <Title>Volume Analysis</Title>
                <View style={styles.volumeContainer}>
                  <View style={styles.volumeRow}>
                    <Text style={styles.label}>Current Volume:</Text>
                    <Text style={styles.value}>{(stockData.summary.avg_volume / 1000000).toFixed(1)}M</Text>
                  </View>
                  <View style={styles.volumeRow}>
                    <Text style={styles.label}>Average Volume:</Text>
                    <Text style={styles.value}>{(stockData.summary.avg_volume / 1000000).toFixed(1)}M</Text>
                  </View>
                  <View style={styles.volumeRow}>
                    <Text style={styles.label}>OBV:</Text>
                    <Text style={styles.value}>{(technicalData?.obv / 1000000).toFixed(1)}M</Text>
                  </View>
                </View>
                <Paragraph style={styles.analysisText}>
                  {stockData.summary.avg_volume > stockData.summary.avg_volume * 1.5
                    ? 'Volume is significantly above average - strong price movement likely.'
                    : stockData.summary.avg_volume < stockData.summary.avg_volume * 0.5
                    ? 'Volume is below average - weak price movement expected.'
                    : 'Volume is at normal levels.'}
                </Paragraph>
              </Card.Content>
            </Card>
          )}

          {/* Summary */}
          <Card style={styles.card}>
            <Card.Content>
              <Title>Technical Analysis Summary</Title>
              <Paragraph style={styles.summaryText}>
                Based on the technical indicators, {state.currentSymbol} shows{' '}
                {technicalData?.rsi > 50 && technicalData?.macd?.macd > 0
                  ? 'bullish momentum with positive RSI and MACD signals.'
                  : technicalData?.rsi < 50 && technicalData?.macd?.macd < 0
                  ? 'bearish momentum with negative RSI and MACD signals.'
                  : 'mixed signals with some indicators showing bullish and others bearish.'}
              </Paragraph>
              <Paragraph style={styles.summaryText}>
                The stock is currently trading at ${stockData?.summary?.current_price?.toFixed(2)} with a{' '}
                {stockData?.summary?.price_change_pct > 0 ? 'gain' : 'loss'} of{' '}
                {Math.abs(stockData?.summary?.price_change_pct).toFixed(2)}% today.
              </Paragraph>
            </Card.Content>
          </Card>
        </>
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
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  searchInput: {
    flex: 1,
    marginRight: 8,
  },
  searchButton: {
    marginLeft: 8,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  bollingerContainer: {
    marginBottom: 16,
  },
  bollingerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  stochasticContainer: {
    marginBottom: 16,
  },
  stochasticRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  volumeContainer: {
    marginBottom: 16,
  },
  volumeRow: {
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
  analysisText: {
    color: '#64748b',
    fontStyle: 'italic',
  },
  summaryText: {
    color: '#1e293b',
    lineHeight: 20,
  },
  loadingText: {
    textAlign: 'center',
    marginTop: 8,
    color: '#64748b',
  },
});

export default AnalysisScreen; 