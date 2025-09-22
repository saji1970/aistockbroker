# AI Stock Trading Bot - Shadow Trading System

A sophisticated AI-powered trading bot that performs paper trading with real market data. This system includes multiple trading strategies, machine learning capabilities, risk management, and a web dashboard for monitoring.

## 🚀 Features

### Core Features
- **Shadow Trading**: Paper trading with real market data (no real money involved)
- **Multiple Strategies**: Momentum, Mean Reversion, RSI, ML-based, and Sentiment strategies
- **Real-time Data**: Live market data from Yahoo Finance
- **Risk Management**: Position sizing, daily loss limits, portfolio-level controls
- **Web Dashboard**: Real-time monitoring and control interface
- **Performance Tracking**: Comprehensive analytics and reporting

### Advanced Features
- **Machine Learning**: Random Forest classifier for trade predictions
- **Technical Analysis**: RSI, MACD, Bollinger Bands, and more
- **Portfolio Management**: Multi-position tracking with P&L analysis
- **Risk Controls**: VaR calculation, correlation limits, sector exposure
- **Backtesting**: Historical strategy performance analysis

## 📋 Requirements

### Python Dependencies
```bash
pip install -r trading_bot_requirements.txt
```

### Key Libraries
- `yfinance`: Real-time market data
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `scikit-learn`: Machine learning
- `flask`: Web dashboard
- `matplotlib`: Charting and visualization

## 🛠️ Installation

1. **Clone or download the trading bot files**
2. **Install dependencies**:
   ```bash
   pip install -r trading_bot_requirements.txt
   ```
3. **Configure settings** (optional):
   - Edit `trading_bot_config.json` for custom parameters
4. **Run the bot**:
   ```bash
   python run_trading_bot.py
   ```

## 🎮 Usage

### Command Line Options

```bash
python run_trading_bot.py [OPTIONS]

Options:
  --mode {basic,advanced,dashboard,full}  Bot mode to run (default: full)
  --capital FLOAT                         Initial capital (default: 100000)
  --interval INT                          Trading interval in seconds (default: 300)
  --log-level {DEBUG,INFO,WARNING,ERROR}  Logging level (default: INFO)
```

### Running Modes

#### 1. Basic Bot (Command Line Only)
```bash
python run_trading_bot.py --mode basic --capital 50000 --interval 600
```
- Runs basic trading strategies
- Command line interface only
- Good for testing and development

#### 2. Advanced Bot (With ML)
```bash
python run_trading_bot.py --mode advanced --capital 100000
```
- Includes machine learning strategies
- More sophisticated risk management
- Command line interface only

#### 3. Dashboard Only
```bash
python run_trading_bot.py --mode dashboard
```
- Web dashboard at http://localhost:5000
- No trading bot running
- Good for monitoring existing bots

#### 4. Full System (Recommended)
```bash
python run_trading_bot.py --mode full --capital 100000
```
- Advanced bot with ML + Web dashboard
- Best user experience
- Dashboard at http://localhost:5000

## 📊 Trading Strategies

### 1. Momentum Strategy
- **Logic**: Buy when price momentum is positive, sell when negative
- **Parameters**: Lookback period (20), momentum threshold (2%)
- **Best for**: Trending markets

### 2. Mean Reversion Strategy
- **Logic**: Buy when price is below lower Bollinger Band, sell when above upper band
- **Parameters**: Lookback period (20), standard deviation threshold (2.0)
- **Best for**: Range-bound markets

### 3. RSI Strategy
- **Logic**: Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)
- **Parameters**: RSI period (14), oversold (30), overbought (70)
- **Best for**: Volatile markets

### 4. Machine Learning Strategy
- **Logic**: Random Forest classifier trained on technical indicators
- **Features**: RSI, MACD, Bollinger Bands, volume ratio, price changes, volatility
- **Best for**: Complex market conditions

### 5. Sentiment Strategy
- **Logic**: Buy/sell based on news and social media sentiment
- **Parameters**: Sentiment threshold (60%)
- **Best for**: Event-driven trading

## 🎛️ Dashboard Features

### Portfolio Overview
- Real-time portfolio value
- Total return percentage
- Cash balance
- Number of positions

### Charts and Analytics
- Portfolio value over time
- Performance metrics
- Trade history

### Position Management
- Current holdings
- Unrealized P&L
- Position details

### Watchlist Management
- Add/remove stocks
- Real-time monitoring
- Strategy assignment

### Bot Controls
- Start/stop trading
- Strategy configuration
- Risk parameter adjustment

## ⚙️ Configuration

### Bot Settings (`trading_bot_config.json`)
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

### Risk Management
- **Max Position Size**: Maximum percentage of portfolio per position (default: 10%)
- **Max Daily Loss**: Maximum daily loss limit (default: 5%)
- **VaR Limit**: Value at Risk limit (default: 2%)
- **Sector Exposure**: Maximum sector concentration (default: 30%)

## 📈 Performance Monitoring

### Key Metrics
- **Total Return**: Overall portfolio performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Average Trade**: Average profit/loss per trade

### Reports
- Real-time performance updates
- Daily/weekly/monthly summaries
- Strategy-specific analysis
- Risk metrics tracking

## 🔧 Customization

### Adding New Strategies
1. Create a new class inheriting from `TradingStrategy`
2. Implement `analyze()` and `should_exit()` methods
3. Add to bot's strategy dictionary
4. Configure in `trading_bot_config.json`

### Custom Risk Rules
1. Extend `RiskManager` class
2. Override risk calculation methods
3. Add custom position sizing logic
4. Implement sector/correlation limits

### Data Sources
- Currently uses Yahoo Finance (`yfinance`)
- Can be extended to other providers
- Supports real-time and historical data
- Configurable update frequencies

## 🚨 Important Notes

### Shadow Trading Only
- **This is a paper trading system**
- **No real money is involved**
- **All trades are simulated**
- **Use for learning and testing only**

### Risk Disclaimer
- Past performance doesn't guarantee future results
- Market conditions can change rapidly
- Always do your own research
- Consider consulting financial advisors

### Data Limitations
- Yahoo Finance data may have delays
- Free data has limitations
- Consider paid data sources for production use
- Historical data quality varies

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
pip install -r trading_bot_requirements.txt
```

#### 2. Data Connection Issues
- Check internet connection
- Verify Yahoo Finance is accessible
- Try different symbols
- Check firewall settings

#### 3. Dashboard Not Loading
- Ensure port 5000 is available
- Check Flask installation
- Verify template files exist
- Check browser console for errors

#### 4. ML Model Training Fails
- Ensure sufficient historical data
- Check scikit-learn installation
- Verify data quality
- Increase training data period

### Log Files
- `trading_bot.log`: Main bot activity
- Check logs for detailed error information
- Adjust log level for more/less detail

## 📚 API Reference

### Core Classes

#### `ShadowTradingBot`
Main trading bot class with basic functionality.

#### `AdvancedTradingBot`
Enhanced bot with ML and advanced features.

#### `TradingStrategy`
Base class for implementing trading strategies.

#### `RiskManager`
Risk management and position sizing.

#### `MarketDataProvider`
Real-time and historical data access.

### Key Methods

#### Bot Control
- `start(interval)`: Start trading bot
- `stop()`: Stop trading bot
- `add_to_watchlist(symbol)`: Add stock to watchlist
- `remove_from_watchlist(symbol)`: Remove stock from watchlist

#### Strategy Management
- `run_strategy(symbol, strategy_name)`: Run specific strategy
- `analyze(data)`: Analyze market data
- `should_exit(position, data)`: Check exit conditions

#### Portfolio Management
- `place_order(symbol, type, quantity, strategy, reason)`: Place trade
- `get_performance_report()`: Get performance metrics
- `update_portfolio_value()`: Update portfolio calculations

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints
- Write unit tests

### Testing
- Test with different market conditions
- Verify risk management rules
- Check strategy performance
- Validate dashboard functionality

## 📄 License

This project is for educational and research purposes. Use at your own risk.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files
3. Search existing issues
4. Create new issue with details

---

**Happy Trading! 🚀📈**

Remember: This is shadow trading only - no real money involved!
