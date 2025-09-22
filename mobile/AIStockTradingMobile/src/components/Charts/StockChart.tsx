import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  useTheme,
} from 'react-native-paper';
import {LineChart, BarChart} from 'react-native-chart-kit';
import {VictoryChart, VictoryLine, VictoryArea, VictoryAxis, VictoryCandlestick} from 'victory-native';
import {stockAPI} from '../../services/api';

const {width: screenWidth} = Dimensions.get('window');

interface StockChartProps {
  symbol: string;
  period?: string;
  height?: number;
  showVolume?: boolean;
  showIndicators?: boolean;
}

interface StockData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const StockChart: React.FC<StockChartProps> = ({
  symbol,
  period = '1mo',
  height = 200,
  showVolume = false,
  showIndicators = false,
}) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState(period);
  const [chartType, setChartType] = useState<'line' | 'candlestick' | 'area'>('line');

  const periods = [
    {label: '1D', value: '1d'},
    {label: '1W', value: '5d'},
    {label: '1M', value: '1mo'},
    {label: '3M', value: '3mo'},
    {label: '6M', value: '6mo'},
    {label: '1Y', value: '1y'},
  ];

  const chartTypes = [
    {label: 'Line', value: 'line'},
    {label: 'Candlestick', value: 'candlestick'},
    {label: 'Area', value: 'area'},
  ];

  const fetchStockData = async () => {
    try {
      setLoading(true);
      const data = await stockAPI.getStockData(symbol, selectedPeriod);
      
      if (data && data.data) {
        const formattedData = data.data.map((item: any) => ({
          timestamp: item.timestamp || item.date,
          open: parseFloat(item.Open || item.open),
          high: parseFloat(item.High || item.high),
          low: parseFloat(item.Low || item.low),
          close: parseFloat(item.Close || item.close),
          volume: parseInt(item.Volume || item.volume),
        }));
        setStockData(formattedData);
      }
    } catch (error) {
      console.error('Error fetching stock data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStockData();
  }, [symbol, selectedPeriod]);

  const formatChartData = () => {
    if (!stockData.length) return {labels: [], datasets: []};

    const labels = stockData.slice(-20).map(item => {
      const date = new Date(item.timestamp);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    });

    const prices = stockData.slice(-20).map(item => item.close);

    return {
      labels,
      datasets: [
        {
          data: prices,
          color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`,
          strokeWidth: 2,
        },
      ],
    };
  };

  const formatVictoryData = () => {
    return stockData.slice(-30).map((item, index) => ({
      x: index,
      y: item.close,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }));
  };

  const formatVolumeData = () => {
    if (!stockData.length) return {labels: [], datasets: []};

    const labels = stockData.slice(-20).map(item => {
      const date = new Date(item.timestamp);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    });

    const volumes = stockData.slice(-20).map(item => item.volume);

    return {
      labels,
      datasets: [
        {
          data: volumes,
          color: (opacity = 1) => `rgba(156, 163, 175, ${opacity})`,
        },
      ],
    };
  };

  const getCurrentPrice = () => {
    if (!stockData.length) return 0;
    return stockData[stockData.length - 1].close;
  };

  const getPriceChange = () => {
    if (!stockData.length) return {change: 0, changePercent: 0};
    const current = stockData[stockData.length - 1].close;
    const previous = stockData[stockData.length - 2]?.close || current;
    const change = current - previous;
    const changePercent = (change / previous) * 100;
    return {change, changePercent};
  };

  const renderLineChart = () => {
    const chartData = formatChartData();
    
    return (
      <LineChart
        data={chartData}
        width={screenWidth - 40}
        height={height}
        chartConfig={{
          backgroundColor: theme.colors.surface,
          backgroundGradientFrom: theme.colors.surface,
          backgroundGradientTo: theme.colors.surface,
          decimalPlaces: 2,
          color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`,
          labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
          style: {
            borderRadius: 16,
          },
          propsForDots: {
            r: '4',
            strokeWidth: '2',
            stroke: theme.colors.primary,
          },
        }}
        bezier
        style={{
          marginVertical: 8,
          borderRadius: 16,
        }}
      />
    );
  };

  const renderVictoryChart = () => {
    const data = formatVictoryData();
    
    if (chartType === 'candlestick') {
      return (
        <VictoryChart
          width={screenWidth - 40}
          height={height}
          padding={{left: 50, top: 20, right: 20, bottom: 40}}
          domainPadding={{x: 10}}>
          <VictoryAxis
            dependentAxis
            tickFormat={(x) => `$${x.toFixed(2)}`}
          />
          <VictoryAxis tickFormat={(x) => x} />
          <VictoryCandlestick
            data={data}
            candleColors={{positive: '#10b981', negative: '#ef4444'}}
          />
        </VictoryChart>
      );
    }

    return (
      <VictoryChart
        width={screenWidth - 40}
        height={height}
        padding={{left: 50, top: 20, right: 20, bottom: 40}}>
        <VictoryAxis
          dependentAxis
          tickFormat={(x) => `$${x.toFixed(2)}`}
        />
        <VictoryAxis tickFormat={(x) => x} />
        {chartType === 'area' ? (
          <VictoryArea
            data={data}
            style={{
              data: {
                fill: theme.colors.primary,
                fillOpacity: 0.3,
              },
            }}
          />
        ) : (
          <VictoryLine
            data={data}
            style={{
              data: {
                stroke: theme.colors.primary,
                strokeWidth: 2,
              },
            }}
          />
        )}
      </VictoryChart>
    );
  };

  const renderVolumeChart = () => {
    if (!showVolume) return null;
    
    const volumeData = formatVolumeData();
    
    return (
      <View style={styles.volumeContainer}>
        <Text style={styles.volumeTitle}>Volume</Text>
        <BarChart
          data={volumeData}
          width={screenWidth - 40}
          height={100}
          chartConfig={{
            backgroundColor: theme.colors.surface,
            backgroundGradientFrom: theme.colors.surface,
            backgroundGradientTo: theme.colors.surface,
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(156, 163, 175, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
            style: {
              borderRadius: 16,
            },
          }}
          style={{
            marginVertical: 8,
            borderRadius: 16,
          }}
        />
      </View>
    );
  };

  const priceChange = getPriceChange();
  const currentPrice = getCurrentPrice();

  return (
    <Card style={styles.container}>
      <Card.Content>
        <View style={styles.header}>
          <View style={styles.priceInfo}>
            <Title style={styles.symbol}>{symbol}</Title>
            <Text style={styles.price}>${currentPrice.toFixed(2)}</Text>
            <View style={styles.changeContainer}>
              <Text
                style={[
                  styles.change,
                  {
                    color: priceChange.change >= 0 ? '#10b981' : '#ef4444',
                  },
                ]}>
                {priceChange.change >= 0 ? '+' : ''}
                {priceChange.change.toFixed(2)} ({priceChange.changePercent.toFixed(2)}%)
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.controls}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {periods.map((period) => (
              <TouchableOpacity
                key={period.value}
                onPress={() => setSelectedPeriod(period.value)}
                style={[
                  styles.periodButton,
                  selectedPeriod === period.value && styles.selectedPeriod,
                ]}>
                <Text
                  style={[
                    styles.periodText,
                    selectedPeriod === period.value && styles.selectedPeriodText,
                  ]}>
                  {period.label}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        <View style={styles.chartControls}>
          {chartTypes.map((type) => (
            <Chip
              key={type.value}
              selected={chartType === type.value}
              onPress={() => setChartType(type.value as any)}
              style={styles.chartTypeChip}>
              {type.label}
            </Chip>
          ))}
        </View>

        <View style={styles.chartContainer}>
          {chartType === 'line' ? renderLineChart() : renderVictoryChart()}
        </View>

        {renderVolumeChart()}
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    margin: 16,
    elevation: 4,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  priceInfo: {
    flex: 1,
  },
  symbol: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  price: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  changeContainer: {
    marginTop: 4,
  },
  change: {
    fontSize: 14,
    fontWeight: '600',
  },
  controls: {
    marginBottom: 16,
  },
  periodButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 8,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
  },
  selectedPeriod: {
    backgroundColor: '#2563eb',
  },
  periodText: {
    fontSize: 14,
    color: '#6b7280',
  },
  selectedPeriodText: {
    color: '#ffffff',
  },
  chartControls: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 8,
  },
  chartTypeChip: {
    marginRight: 8,
  },
  chartContainer: {
    alignItems: 'center',
  },
  volumeContainer: {
    marginTop: 16,
  },
  volumeTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#6b7280',
  },
});

export default StockChart;
