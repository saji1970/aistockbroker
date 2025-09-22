# 🤖 AI Stock Trading System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Platform-orange.svg)](https://cloud.google.com/)

A comprehensive AI-powered stock trading system featuring shadow trading, robo-trading agents, technical analysis, and intelligent portfolio management. Built with Python, React, and Google Cloud Platform.

## 🌟 Features

### 🤖 AI-Powered Trading
- **Gemini Pro Integration**: Advanced AI predictions using Google's Gemini Pro model
- **Shadow Trading**: Paper trading with real market data (no real money involved)
- **Robo Trading Agent**: Automated trading with multiple strategies
- **Technical Analysis**: 50+ technical indicators and signals
- **Portfolio Management**: Intelligent portfolio optimization and risk management

### 📊 Trading Capabilities
- **Multi-Asset Support**: Stocks, Cryptocurrencies, Forex, Commodities, ETFs
- **Real-time Data**: Live market data from multiple sources
- **Risk Management**: Stop-loss, take-profit, position sizing
- **Backtesting**: Historical strategy performance analysis
- **Sensitivity Analysis**: Scenario-based market analysis

### 💬 Natural Language Processing
- **Conversational AI**: Ask questions about stocks in plain English
- **Intent Recognition**: Automatic query classification
- **Sentiment Analysis**: Market sentiment analysis
- **Smart Recommendations**: Personalized investment advice

### 🎯 User Interfaces
- **Web Dashboard**: Modern React-based trading interface
- **Mobile Apps**: Android, iOS, and React Native applications
- **Real-time Monitoring**: Live portfolio tracking and alerts
- **Interactive Charts**: Advanced charting with technical overlays

## 🏗️ Architecture

```
AIStockbroker/
├── backend/                 # Python backend services
│   ├── trading_bots/       # Shadow trading and robo-trading
│   ├── ai_services/        # AI prediction and NLP
│   ├── portfolio/          # Portfolio management
│   └── data/              # Market data fetching
├── frontend/               # React web application
│   ├── src/               # React components and pages
│   └── public/            # Static assets and PWA files
├── mobile/                 # Mobile applications
│   ├── AIStockTradingApp/ # Android app
│   ├── AIStockTradingIOS/ # iOS app
│   └── AIStockTradingMobile/ # React Native app
├── deployment/             # Google Cloud deployment configs
└── config/                # Configuration and documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Platform account
- Google Gemini Pro API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-stock-trading-system.git
   cd ai-stock-trading-system
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   echo "ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here" >> .env
   ```

4. **Run the backend**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Access the application**
   Navigate to `http://localhost:3000`

### Mobile App Setup

1. **Install React Native CLI**
   ```bash
   npm install -g react-native-cli
   ```

2. **Install dependencies**
   ```bash
   cd mobile/AIStockTradingMobile
   npm install
   ```

3. **Run on Android**
   ```bash
   npx react-native run-android
   ```

4. **Run on iOS**
   ```bash
   npx react-native run-ios
   ```

## 📖 Usage Guide

### Shadow Trading Bot
```python
from backend.shadow_trading_bot import ShadowTradingBot

# Initialize bot
bot = ShadowTradingBot(initial_capital=10000)

# Add stocks to watchlist
bot.add_to_watchlist(['AAPL', 'GOOGL', 'MSFT'])

# Start trading
bot.start_trading(interval=300)  # 5 minutes
```

### AI Stock Predictions
```python
from backend.gemini_predictor import GeminiPredictor

# Initialize predictor
predictor = GeminiPredictor()

# Get prediction for a stock
prediction = predictor.predict('AAPL', period='1y')
print(f"Prediction: {prediction['recommendation']}")
print(f"Confidence: {prediction['confidence']}%")
```

### Robo Trading Agent
```python
from backend.robo_trading_agent import RoboTradingAgent, AssetType

# Create trading task
agent = RoboTradingAgent("MyTrader")
task_id = agent.create_trading_task(
    initial_capital=100.0,
    target_amount=110.0,
    asset_type=AssetType.STOCK,
    symbols=['AAPL', 'TSLA'],
    duration_hours=8,
    risk_tolerance="medium"
)

# Start trading
agent.start_task(task_id)
```

## 🎮 Trading Strategies

### 1. Momentum Strategy
- **Logic**: Buy when price momentum is positive, sell when negative
- **Best for**: Trending markets
- **Parameters**: 20-period lookback, 2% momentum threshold

### 2. Mean Reversion Strategy
- **Logic**: Buy below Bollinger Bands, sell above
- **Best for**: Range-bound markets
- **Parameters**: 20-period BB, 2.0 standard deviation

### 3. RSI Strategy
- **Logic**: Buy when RSI < 30, sell when RSI > 70
- **Best for**: Volatile markets
- **Parameters**: 14-period RSI, 30/70 levels

### 4. Machine Learning Strategy
- **Logic**: Random Forest classifier on technical indicators
- **Best for**: Complex market conditions
- **Features**: RSI, MACD, Bollinger Bands, volume, volatility

### 5. Sentiment Strategy
- **Logic**: Buy/sell based on news and social sentiment
- **Best for**: Event-driven trading
- **Parameters**: 60% sentiment threshold

## 📊 Technical Indicators

### Moving Averages
- Simple Moving Average (SMA) - 5, 10, 20, 50, 100, 200 periods
- Exponential Moving Average (EMA) - 5, 10, 20, 50, 100, 200 periods
- Hull Moving Average (HMA) - 20 period
- Weighted Moving Average (WMA) - 20 period

### Momentum Indicators
- Relative Strength Index (RSI) - 14 and 30 periods
- Stochastic Oscillator - %K and %D
- MACD - 12, 26, 9 parameters
- Commodity Channel Index (CCI) - 20 period
- Rate of Change (ROC) - 10 period

### Volatility Indicators
- Bollinger Bands - 20 period, 2 standard deviations
- Average True Range (ATR) - 14 period
- Keltner Channel - 20 period
- Donchian Channel - 20 period

### Volume Indicators
- Volume Weighted Average Price (VWAP)
- On Balance Volume (OBV)
- Accumulation/Distribution Line (ADL)
- Chaikin Money Flow (CMF) - 20 period
- Money Flow Index (MFI) - 14 period

## 🔧 Configuration

### Environment Variables
```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here
MARKETSTACK_API_KEY=your_marketstack_key_here
```

### Trading Bot Configuration
```json
{
  "bot_settings": {
    "initial_capital": 100000.0,
    "trading_interval": 300,
    "max_position_size": 0.1,
    "max_daily_loss": 0.05
  },
  "strategies": {
    "momentum": {
      "enabled": true,
      "parameters": {
        "lookback_period": 20,
        "momentum_threshold": 0.02
      }
    }
  }
}
```

## 🚀 Deployment

### Google Cloud Platform

1. **Set up GCP project**
   ```bash
   gcloud init
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Deploy backend**
   ```bash
   cd deployment
   ./deploy-gcp.sh
   ```

3. **Deploy frontend**
   ```bash
   ./deploy-frontend-only.sh
   ```

4. **Deploy trading bot**
   ```bash
   ./deploy-trading-bot.sh
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
cd deployment
docker-compose up -d
```

## 📱 Mobile Applications

### Android App
- **Location**: `mobile/AIStockTradingApp/`
- **Technology**: React Native
- **Features**: Real-time trading, portfolio management, AI predictions

### iOS App
- **Location**: `mobile/AIStockTradingIOS/`
- **Technology**: React Native
- **Features**: Native iOS experience, push notifications

### React Native App
- **Location**: `mobile/AIStockTradingMobile/`
- **Technology**: React Native with TypeScript
- **Features**: Cross-platform compatibility

## 🔒 Security & Privacy

- **API Key Security**: Store keys in environment variables
- **Data Privacy**: No personal data stored or transmitted
- **Rate Limiting**: Built-in caching to respect API limits
- **Error Handling**: Comprehensive error handling and logging
- **Shadow Trading**: No real money involved in trading simulations

## ⚠️ Disclaimer

**Important**: This system is for educational and research purposes only. The predictions and analysis provided are not financial advice. Always:

- Do your own research before making investment decisions
- Consider consulting with a financial advisor
- Understand that past performance doesn't guarantee future results
- Be aware of the risks involved in stock market investing
- This is shadow trading only - no real money is involved

## 🤝 Contributing

We welcome contributions! Please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
npm install

# Run tests
python -m pytest
npm test

# Run linting
flake8 .
eslint src/
```

## 📚 Documentation

- [API Documentation](config/README.md)
- [Trading Bot Guide](config/TRADING_BOT_README.md)
- [Robo Trading System](config/ROBO_TRADING_SYSTEM.md)
- [Deployment Guide](config/GCP_DEPLOYMENT_GUIDE.md)
- [Test Documentation](config/TEST_DOCUMENTATION.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/yourusername/ai-stock-trading-system/issues) page
2. Ensure your API keys are correctly configured
3. Verify your internet connection
4. Check that all dependencies are installed

## 🔮 Future Enhancements

- [ ] Advanced machine learning models
- [ ] Real-time news sentiment analysis
- [ ] Options trading strategies
- [ ] Cryptocurrency exchange integration
- [ ] Social trading features
- [ ] Advanced backtesting engine
- [ ] Mobile push notifications
- [ ] Multi-language support

## 📊 Performance Metrics

- **Data Accuracy**: Real-time data from multiple sources
- **Prediction Speed**: ~10-30 seconds per stock analysis
- **Technical Indicators**: 50+ indicators calculated in real-time
- **API Efficiency**: Intelligent caching to minimize API calls
- **Mobile Performance**: Optimized for mobile trading

## 🌟 Key Highlights

- ✅ **Complete Trading Ecosystem**: From AI predictions to mobile apps
- ✅ **Shadow Trading**: Risk-free learning and testing
- ✅ **Multi-Platform**: Web, Android, iOS applications
- ✅ **Advanced AI**: Google Gemini Pro integration
- ✅ **Real-time Data**: Live market data and analysis
- ✅ **Cloud Ready**: Google Cloud Platform deployment
- ✅ **Open Source**: MIT licensed for community use

---

**Built with ❤️ using Python, React, and Google Cloud Platform**

**🚀 Ready to revolutionize your trading experience!**
