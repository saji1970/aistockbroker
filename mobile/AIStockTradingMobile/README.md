# 🤖 AI Stock Trading Mobile App

A comprehensive React Native mobile application that provides AI-powered stock trading capabilities, real-time market data, and advanced portfolio management features.

## 🌟 Features

### 🤖 AI Trading Bot
- **Shadow Trading**: Paper trading with real market data
- **Multiple Strategies**: Momentum, Mean Reversion, RSI, and Machine Learning
- **Real-time Monitoring**: Live bot status and performance tracking
- **Risk Management**: Built-in position sizing and loss limits
- **Self-Learning**: ML algorithms that improve over time

### 📊 Real-time Market Data
- **Live Stock Prices**: Real-time price updates from Yahoo Finance
- **Interactive Charts**: Candlestick, Line, and Area charts
- **Technical Indicators**: 50+ technical indicators
- **Volume Analysis**: Trading volume visualization
- **Market Overview**: Top stocks and market trends

### 🧠 AI Assistant
- **Natural Language Queries**: Ask questions in plain English
- **Stock Analysis**: AI-powered stock recommendations
- **Market Insights**: Intelligent market analysis
- **Trading Advice**: Personalized trading recommendations
- **Sentiment Analysis**: Market sentiment tracking

### 💼 Portfolio Management
- **Real-time Tracking**: Live portfolio value updates
- **Performance Analytics**: Detailed performance metrics
- **Risk Assessment**: Portfolio risk analysis
- **Asset Allocation**: Portfolio optimization suggestions
- **Historical Data**: Portfolio performance history

### 📈 Technical Analysis
- **Advanced Charts**: Multiple chart types and timeframes
- **Technical Indicators**: RSI, MACD, Bollinger Bands, etc.
- **Signal Analysis**: Buy/sell signal generation
- **Support/Resistance**: Key price level identification
- **Pattern Recognition**: Chart pattern analysis

### 🔔 Smart Notifications
- **Price Alerts**: Custom price notifications
- **Trading Signals**: Bot trading notifications
- **Market Updates**: Important market news
- **Portfolio Alerts**: Portfolio performance notifications
- **System Status**: API and bot status updates

## 🏗️ Architecture

### Core Components
```
AIStockTradingMobile/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Charts/         # Chart components
│   │   ├── Trading/        # Trading components
│   │   └── UI/            # General UI components
│   ├── screens/           # Main app screens
│   │   ├── DashboardScreen.tsx
│   │   ├── TradingBotScreen.tsx
│   │   ├── AIAssistantScreen.tsx
│   │   ├── PortfolioScreen.tsx
│   │   └── AnalysisScreen.tsx
│   ├── services/          # API services
│   │   └── api.ts        # API client
│   ├── context/          # React context
│   └── utils/           # Utility functions
├── android/              # Android-specific code
├── ios/                 # iOS-specific code
└── package.json         # Dependencies
```

### Technology Stack
- **React Native**: Cross-platform mobile development
- **TypeScript**: Type-safe JavaScript
- **React Native Paper**: Material Design components
- **React Navigation**: Navigation library
- **Victory Native**: Chart library
- **React Native Chart Kit**: Additional chart components
- **Axios**: HTTP client
- **AsyncStorage**: Local storage

## 🚀 Getting Started

### Prerequisites
- Node.js 18 or higher
- npm or yarn
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AIStockTradingMobile
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Install React Native dependencies**
   ```bash
   npx react-native install
   ```

4. **iOS Setup (macOS only)**
   ```bash
   cd ios
   pod install
   cd ..
   ```

### Running the App

#### Android
```bash
# Start Metro bundler
npm start

# Run on Android device/emulator
npm run android
```

#### iOS
```bash
# Start Metro bundler
npm start

# Run on iOS simulator/device
npm run ios
```

## 🔧 Building for Production

### Android APK
```bash
# Build release APK
npm run build:android

# Or use the build script
./build-android.sh
```

### Android App Bundle (AAB)
```bash
# Build AAB for Google Play Store
npm run build:android-bundle
```

### iOS
```bash
# Build iOS app
npm run build:ios
```

## 📱 App Screens

### 1. Dashboard
- Market overview with top stocks
- Trading bot status
- System health indicators
- Quick actions
- Real-time stock charts

### 2. Trading Bot
- Bot configuration and controls
- Real-time bot status
- Portfolio performance
- Recent trades
- Watchlist management

### 3. AI Assistant
- Natural language chat interface
- Stock analysis and recommendations
- Market insights
- Trading advice
- Sentiment analysis

### 4. Portfolio
- Portfolio overview
- Asset allocation
- Performance metrics
- Risk analysis
- Historical performance

### 5. Analysis
- Technical analysis tools
- Chart indicators
- Signal analysis
- Pattern recognition
- Market trends

### 6. Settings
- App preferences
- Notification settings
- API configuration
- Account management
- About information

## 🔌 API Integration

### Main API Server
- **URL**: `https://ai-stock-trading-api-1024040140027.us-central1.run.app`
- **Endpoints**:
  - `/api/stock/data/{symbol}` - Stock data
  - `/api/stock/info/{symbol}` - Stock information
  - `/api/prediction/{symbol}` - AI predictions
  - `/api/sensitivity/analysis/{symbol}` - Sensitivity analysis

### Trading Bot API
- **URL**: `https://ai-stock-trading-backend-1024040140027.us-central1.run.app`
- **Endpoints**:
  - `/api/status` - Bot status
  - `/api/portfolio` - Portfolio data
  - `/api/orders` - Trading orders
  - `/api/start` - Start bot
  - `/api/stop` - Stop bot

## 🎨 UI/UX Features

### Material Design
- Consistent Material Design components
- Smooth animations and transitions
- Responsive layout for all screen sizes
- Dark/Light theme support

### Charts and Visualizations
- Interactive stock charts
- Multiple chart types (Line, Candlestick, Area)
- Technical indicator overlays
- Volume analysis
- Real-time data updates

### User Experience
- Intuitive navigation
- Pull-to-refresh functionality
- Loading states and error handling
- Offline support
- Haptic feedback

## 🔒 Security Features

### Data Protection
- Secure API communication
- Local data encryption
- Biometric authentication support
- Secure storage for sensitive data

### Privacy
- No personal data collection
- Local data storage
- Secure API endpoints
- GDPR compliance

## 📊 Performance

### Optimization
- Lazy loading of components
- Image optimization
- Memory management
- Efficient API calls
- Caching strategies

### Monitoring
- Performance metrics
- Error tracking
- Crash reporting
- User analytics

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### E2E Tests
```bash
npm run test:e2e
```

## 🚀 Deployment

### Google Play Store
1. Build AAB file: `npm run build:android-bundle`
2. Upload to Google Play Console
3. Configure store listing
4. Submit for review

### Apple App Store
1. Build iOS app: `npm run build:ios`
2. Upload to App Store Connect
3. Configure app information
4. Submit for review

### Direct Distribution
1. Build APK file: `npm run build:android`
2. Distribute APK file directly
3. Users enable "Install from Unknown Sources"

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
API_BASE_URL=https://ai-stock-trading-api-1024040140027.us-central1.run.app
TRADING_BOT_API_URL=https://ai-stock-trading-backend-1024040140027.us-central1.run.app
GOOGLE_API_KEY=your_google_api_key_here
```

### App Configuration
- Update `app.json` for app metadata
- Configure `android/app/build.gradle` for Android settings
- Configure `ios/AIStockTradingMobile/Info.plist` for iOS settings

## 📚 Documentation

### API Documentation
- [Main API Documentation](../README.md)
- [Trading Bot API Documentation](../ROBO_TRADING_SYSTEM.md)

### Component Documentation
- [Component Library](./docs/components.md)
- [API Services](./docs/api.md)
- [Navigation](./docs/navigation.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- Check the [FAQ](./docs/faq.md)
- Review [Troubleshooting Guide](./docs/troubleshooting.md)
- Open an [Issue](https://github.com/your-repo/issues)

### Contact
- Email: support@aistocktrading.com
- GitHub: [@your-username](https://github.com/your-username)
- Twitter: [@aistocktrading](https://twitter.com/aistocktrading)

## 🎯 Roadmap

### Upcoming Features
- [ ] Advanced charting tools
- [ ] Social trading features
- [ ] Cryptocurrency support
- [ ] Advanced AI models
- [ ] Voice commands
- [ ] Apple Watch support
- [ ] Widget support

### Version History
- **v1.0.0** - Initial release with core features
- **v1.1.0** - Enhanced AI assistant
- **v1.2.0** - Advanced charting
- **v2.0.0** - Major UI overhaul

---

**Built with ❤️ using React Native and AI technology**