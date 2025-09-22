# 🚀 AI Stock Trading System - Setup Guide

This guide will help you set up the complete AI Stock Trading System on your local machine.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: At least 5GB free space
- **Internet**: Stable internet connection for real-time data

### Software Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Git**: Latest version
- **Google Cloud SDK**: For deployment (optional)

## 🛠️ Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-stock-trading-system.git
cd ai-stock-trading-system

# Verify the structure
ls -la
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2.2 Install Python Dependencies
```bash
# Navigate to backend directory
cd backend

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Verify installation
python -c "import streamlit, pandas, yfinance; print('Dependencies installed successfully!')"
```

#### 2.3 Configure Environment Variables
```bash
# Create .env file in the root directory
cd ..
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
echo "ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here" >> .env
echo "FINNHUB_API_KEY=your_finnhub_key_here" >> .env
echo "MARKETSTACK_API_KEY=your_marketstack_key_here" >> .env
```

### Step 3: Frontend Setup

#### 3.1 Install Node.js Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

#### 3.2 Configure Frontend Environment
```bash
# Create .env file for frontend
echo "REACT_APP_API_URL=http://localhost:5001" > .env
echo "REACT_APP_ENVIRONMENT=development" >> .env
```

### Step 4: Mobile App Setup (Optional)

#### 4.1 Android Development
```bash
# Navigate to mobile app directory
cd ../mobile/AIStockTradingMobile

# Install dependencies
npm install

# Install React Native CLI
npm install -g react-native-cli

# Install Android Studio and SDK
# Follow: https://reactnative.dev/docs/environment-setup
```

#### 4.2 iOS Development (macOS only)
```bash
# Install Xcode from App Store
# Install CocoaPods
sudo gem install cocoapods

# Install iOS dependencies
cd ios && pod install && cd ..
```

## 🔑 API Keys Setup

### Google Gemini Pro API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### Alpha Vantage API Key (Optional)
1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Get a free API key
3. Add to your `.env` file

### Finnhub API Key (Optional)
1. Visit [Finnhub](https://finnhub.io/register)
2. Sign up for a free account
3. Get your API key
4. Add to your `.env` file

## 🚀 Running the Application

### Backend Services

#### 1. Main Streamlit Application
```bash
# Navigate to backend directory
cd backend

# Run the main app
streamlit run app.py

# Access at: http://localhost:8501
```

#### 2. API Server
```bash
# Run the API server
python api_server.py

# Access at: http://localhost:5001
```

#### 3. Trading Bot
```bash
# Run shadow trading bot
python run_trading_bot.py --mode full --capital 10000

# Run robo trading agent
python robo_trading_interface.py
```

### Frontend Application
```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm start

# Access at: http://localhost:3000
```

### Mobile Applications

#### Android
```bash
# Navigate to mobile app directory
cd mobile/AIStockTradingMobile

# Start Metro bundler
npx react-native start

# Run on Android (in another terminal)
npx react-native run-android
```

#### iOS
```bash
# Run on iOS simulator
npx react-native run-ios
```

## 🔧 Configuration

### Trading Bot Configuration
Edit `config/trading_bot_config.json`:

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
    },
    "rsi": {
      "enabled": true,
      "parameters": {
        "period": 14,
        "oversold": 30,
        "overbought": 70
      }
    }
  }
}
```

### Frontend Configuration
Edit `frontend/src/config/api.js`:

```javascript
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5001',
  timeout: 10000,
  endpoints: {
    predictions: '/api/predictions',
    portfolio: '/api/portfolio',
    trading: '/api/trading'
  }
};
```

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_trading_bot.py

# Run with coverage
python -m pytest --cov=backend tests/

# Run integration tests
python -m pytest tests/integration/
```

### Frontend Testing
```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run e2e tests
npm run test:e2e
```

### Mobile Testing
```bash
cd mobile/AIStockTradingMobile

# Run unit tests
npm test

# Run on device
npx react-native run-android --device
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Python Dependencies
```bash
# If you get import errors
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# If TA-Lib installation fails
# Windows: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# macOS: brew install ta-lib
# Ubuntu: sudo apt-get install libta-lib-dev
```

#### 2. Node.js Dependencies
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 3. API Key Issues
```bash
# Verify .env file exists and has correct format
cat .env

# Check if environment variables are loaded
python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"
```

#### 4. Port Conflicts
```bash
# Check if ports are in use
# Windows:
netstat -ano | findstr :8501
netstat -ano | findstr :3000

# macOS/Linux:
lsof -i :8501
lsof -i :3000

# Kill processes if needed
# Windows:
taskkill /PID <PID> /F
# macOS/Linux:
kill -9 <PID>
```

#### 5. Mobile App Issues
```bash
# Clear React Native cache
npx react-native start --reset-cache

# Clean and rebuild
cd android && ./gradlew clean && cd ..
npx react-native run-android
```

## 📊 Performance Optimization

### Backend Optimization
```bash
# Install performance monitoring
pip install psutil memory-profiler

# Monitor memory usage
python -m memory_profiler backend/app.py

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 api_server:app
```

### Frontend Optimization
```bash
# Build optimized production version
npm run build

# Analyze bundle size
npm install -g webpack-bundle-analyzer
npm run build
webpack-bundle-analyzer build/static/js/*.js
```

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique API keys
- Rotate API keys regularly
- Use different keys for development and production

### Network Security
```bash
# Use HTTPS in production
# Configure CORS properly
# Implement rate limiting
# Use authentication for API endpoints
```

## 📚 Additional Resources

### Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [React Documentation](https://reactjs.org/docs/)
- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [Google Cloud Documentation](https://cloud.google.com/docs)

### Community
- [GitHub Issues](https://github.com/yourusername/ai-stock-trading-system/issues)
- [GitHub Discussions](https://github.com/yourusername/ai-stock-trading-system/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/ai-stock-trading)

## ✅ Verification Checklist

After setup, verify that everything works:

- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] API endpoints respond correctly
- [ ] Trading bot can fetch market data
- [ ] AI predictions are generated
- [ ] Mobile app builds successfully
- [ ] All tests pass
- [ ] Environment variables are loaded
- [ ] Database connections work
- [ ] Real-time data updates

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Join our community discussions
5. Check the documentation

---

**🎉 Congratulations! You've successfully set up the AI Stock Trading System!**

Start with the basic Streamlit app and gradually explore the advanced features. Happy trading! 🚀📈
