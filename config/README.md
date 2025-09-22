# 🤖 AI Stock Predictor - Powered by Google Gemini Pro

A comprehensive stock prediction system that leverages Google's Gemini Pro AI model to provide intelligent stock market analysis and predictions. This application combines technical analysis, fundamental data, and AI-powered insights to help users make informed investment decisions.

## 🌟 Features

### 🤖 AI-Powered Predictions
- **Gemini Pro Integration**: Uses Google's advanced Gemini Pro model for intelligent stock analysis
- **Comprehensive Analysis**: Combines technical indicators, fundamental data, and market context
- **Confidence Metrics**: Provides confidence levels for short-term and medium-term predictions
- **Trading Recommendations**: Clear Buy/Sell/Hold recommendations with entry/exit points

### 📊 Technical Analysis
- **50+ Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, and more
- **Interactive Charts**: Real-time candlestick charts with technical overlays
- **Signal Analysis**: Automated signal generation for key indicators
- **Support/Resistance Levels**: Dynamic calculation of key price levels

### 🧠 Sensitivity Analysis
- **Scenario-Based Analysis**: 6 different market scenarios (Bull Market, Bear Market, Interest Rate Shock, etc.)
- **Risk Metrics**: Value at Risk (VaR), Expected Shortfall, and volatility analysis
- **Confidence Intervals**: Statistical confidence intervals for price predictions
- **Factor Impact Analysis**: Detailed breakdown of how different factors affect stock prices
- **Trading Recommendations**: Scenario-specific buy/sell recommendations with position sizing

### 💬 NLP & Conversational AI
- **Natural Language Queries**: Ask questions in plain English about stocks and analysis
- **Intent Recognition**: Automatically classify user queries (price, technical analysis, prediction, etc.)
- **Sentiment Analysis**: Analyze text sentiment for market insights
- **Conversational Interface**: Chat-like interaction with the AI assistant
- **Smart Recommendations**: Personalized investment advice based on user preferences

### 💰 Portfolio Growth & Money Management
- **Portfolio Growth Analysis**: Predict growth for multi-asset portfolios with ETFs and stocks
- **ETF Performance Analysis**: Comprehensive ETF analysis with sector exposure, liquidity metrics, and expense ratio impact
- **Money Growth Strategies**: Conservative, moderate, and aggressive investment strategies
- **Risk-Adjusted Returns**: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Information Ratio calculations
- **Compound Growth Scenarios**: Projected portfolio values over different time horizons (1-10 years)
- **Alternative Strategies**: Dividend-focused, growth-focused, and value-focused approaches
- **Personalized Recommendations**: Strategy recommendations based on risk tolerance and time horizon

### 📈 Data & Analytics
- **Real-time Data**: Live stock data from Yahoo Finance with robust fallback mechanisms
- **Multiple Timeframes**: Analysis from 1 month to 5 years
- **Volume Analysis**: Advanced volume-based indicators
- **Risk Metrics**: Volatility, Sharpe ratio, and drawdown analysis
- **Robust Error Handling**: Graceful handling of API rate limits and data availability issues

### 🎯 User Interface
- **Modern Web App**: Beautiful Streamlit-based interface
- **Interactive Dashboard**: Real-time charts and metrics
- **Batch Analysis**: Analyze multiple stocks simultaneously
- **Export Capabilities**: Download analysis results as CSV

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini Pro API key
- Internet connection for real-time data

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aistocktrading
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**
   ```bash
   # Create a .env file in the project root
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Required: Google Gemini Pro API Key
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Alpha Vantage API Key for additional data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

### Getting a Gemini Pro API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

## 📖 Usage Guide

### Single Stock Analysis
1. **Enter Stock Symbol**: Type a valid stock symbol (e.g., AAPL, GOOGL, MSFT)
2. **Select Time Period**: Choose analysis timeframe (1mo to 5y)
3. **View Technical Analysis**: Interactive charts with indicators
4. **Generate AI Prediction**: Click "Generate AI Prediction" button
5. **Review Results**: Detailed analysis with confidence metrics

### Batch Analysis
1. **Enter Multiple Symbols**: Add stock symbols (one per line)
2. **Run Batch Analysis**: Click "Analyze Multiple Stocks"
3. **Download Results**: Export analysis as CSV file

### Understanding Predictions
- **Short-term (1-7 days)**: Immediate price direction and confidence
- **Medium-term (1-4 weeks)**: Extended outlook with key levels

### Sensitivity Analysis
- **Bull Market Scenario**: Optimistic market conditions with strong growth
- **Bear Market Scenario**: Pessimistic market conditions with economic downturn
- **Interest Rate Shock**: Rapid increase in interest rates
- **Earnings Surprise**: Better than expected earnings performance
- **Sector Rotation**: Money flowing out of current sector
- **Volatility Spike**: Sudden increase in market volatility

### Natural Language Queries
- **Price Queries**: "What's the current price of AAPL?"
- **Technical Analysis**: "Show me the RSI for GOOGL"
- **Predictions**: "Predict the future price of TSLA"
- **Sentiment Analysis**: "What's the market sentiment for MSFT?"
- **Comparisons**: "Compare AAPL vs GOOGL performance"
- **Risk Assessment**: "What are the risks for TSLA?"
- **Risk Assessment**: Potential risks and stop-loss recommendations
- **Trading Recommendations**: Specific entry/exit points

### Portfolio Growth Analysis
- **Multi-Asset Portfolios**: Analyze portfolios with stocks and ETFs
- **Growth Predictions**: Predict portfolio performance over different time horizons
- **Risk Metrics**: Portfolio volatility, VaR, and diversification scores
- **Growth Scenarios**: Conservative, base case, and optimistic projections
- **Individual Asset Analysis**: Detailed predictions for each portfolio component

### ETF Analysis
- **Comprehensive ETF Review**: Sector exposure, liquidity metrics, expense ratios
- **Performance Analysis**: Technical and fundamental ETF analysis
- **Liquidity Assessment**: Trading volume and bid-ask spread analysis
- **Sector Breakdown**: Detailed sector allocation and concentration analysis
- **AI Predictions**: ETF-specific price predictions and recommendations

### Money Growth Strategies
- **Risk-Based Strategies**: Conservative, moderate, and aggressive approaches
- **Alternative Strategies**: Dividend-focused, growth-focused, and value-focused
- **Compound Growth Projections**: Portfolio value projections over 1-10 years
- **Risk-Adjusted Returns**: Sharpe, Sortino, Calmar, and Information ratios
- **Personalized Recommendations**: Strategy advice based on risk tolerance and time horizon

## 🏗️ Architecture

### Core Components

```
aistocktrading/
├── app.py                 # Main Streamlit application
├── gemini_predictor.py    # Gemini Pro AI integration
├── data_fetcher.py        # Stock data retrieval
├── technical_analysis.py  # Technical indicators
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Data Flow
1. **Data Fetching**: Real-time stock data from Yahoo Finance
2. **Technical Analysis**: Calculation of 50+ technical indicators
3. **AI Analysis**: Gemini Pro processes comprehensive data
4. **Prediction Generation**: Structured predictions with confidence metrics
5. **Visualization**: Interactive charts and metrics display

## 📊 Technical Indicators

### Moving Averages
- Simple Moving Average (SMA) - 5, 10, 20, 50, 100, 200 periods
- Exponential Moving Average (EMA) - 5, 10, 20, 50, 100, 200 periods
- Weighted Moving Average (WMA) - 20 period
- Hull Moving Average (HMA) - 20 period

### Momentum Indicators
- Relative Strength Index (RSI) - 14 and 30 periods
- Stochastic Oscillator - %K and %D
- Williams %R - 14 period
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
- Volume Rate of Change (VROC) - 25 period
- Money Flow Index (MFI) - 14 period

### Trend Indicators
- Parabolic SAR
- Average Directional Index (ADX) - 14 period
- Ichimoku Cloud components
- Aroon Indicator - 25 period

## 🔒 Security & Privacy

- **API Key Security**: Store API keys in environment variables
- **Data Privacy**: No personal data is stored or transmitted
- **Rate Limiting**: Built-in caching to respect API limits
- **Error Handling**: Comprehensive error handling and logging

## ⚠️ Disclaimer

**Important**: This tool is for educational and research purposes only. The predictions and analysis provided are not financial advice. Always:

- Do your own research before making investment decisions
- Consider consulting with a financial advisor
- Understand that past performance doesn't guarantee future results
- Be aware of the risks involved in stock market investing

## 🤝 Contributing

We welcome contributions! Please feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when available)
python -m pytest

# Run linting
flake8 .
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Ensure your API key is correctly configured
3. Verify your internet connection
4. Check that all dependencies are installed

## 🔮 Future Enhancements

- [ ] Machine learning model integration
- [ ] Portfolio optimization features
- [ ] Real-time alerts and notifications
- [ ] Advanced backtesting capabilities
- [ ] Social sentiment analysis
- [ ] Options analysis
- [ ] Cryptocurrency support
- [ ] Mobile app version

## 📊 Performance Metrics

- **Data Accuracy**: Real-time data from Yahoo Finance
- **Prediction Speed**: ~10-30 seconds per stock analysis
- **Technical Indicators**: 50+ indicators calculated in real-time
- **API Efficiency**: Intelligent caching to minimize API calls

---

**Built with ❤️ using Google Gemini Pro AI and Streamlit** 