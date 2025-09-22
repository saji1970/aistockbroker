# AI Stock Trading Platform - React Frontend

A modern, responsive React-based frontend for the AI-powered stock trading platform, featuring real-time data visualization, portfolio management, and advanced AI analysis tools.

## 🚀 Features

### 📊 Dashboard
- **Real-time Metrics**: Current price, portfolio value, AI predictions, and available cash
- **Interactive Charts**: Price charts with technical indicators (placeholder for chart implementation)
- **Quick Actions**: Easy access to common portfolio operations
- **Recent Activity**: Latest trading signals and portfolio updates

### 📈 Technical Analysis
- **Multiple Indicators**: Price charts, moving averages, RSI, MACD, Bollinger Bands, volume analysis
- **Interactive Selection**: Choose from 6 different technical indicators
- **Real-time Data**: Live stock data with automatic refresh
- **Analysis Summary**: AI-powered insights and recommendations

### 💼 Portfolio Management
- **Portfolio Initialization**: Set up your investment portfolio with initial capital
- **Capital Management**: Add funds and track available cash
- **Asset Tracking**: Monitor holdings, P&L, and allocation
- **Trading Signals**: AI-generated buy/sell recommendations
- **Performance Metrics**: Total return, volatility, Sharpe ratio, max drawdown

### 🤖 AI Features
- **AI Price Prediction**: Gemini Pro-powered price forecasts with confidence levels
- **Sensitivity Analysis**: Risk assessment and scenario modeling
- **Smart Recommendations**: Personalized trading strategies
- **Portfolio Growth Analysis**: Multi-asset portfolio projections
- **Money Growth Strategies**: Investment strategy generation based on risk tolerance

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Dark/Light Theme**: Toggle between themes (coming soon)
- **Real-time Updates**: Live data refresh and notifications
- **Smooth Animations**: Modern transitions and loading states
- **Accessibility**: WCAG compliant design

## 🛠️ Technology Stack

### Frontend
- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **React Query**: Server state management and caching
- **Tailwind CSS**: Utility-first CSS framework
- **Heroicons**: Beautiful SVG icons
- **Recharts**: Data visualization library (for future chart implementation)
- **Zustand**: Lightweight state management
- **React Hot Toast**: Toast notifications

### Backend Integration
- **Flask API**: RESTful API server
- **CORS**: Cross-origin resource sharing
- **JSON**: Data serialization

## 📦 Installation

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+ with pip
- Google API key for Gemini Pro

### Frontend Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm start
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export GOOGLE_API_KEY=your_api_key_here
   ```

3. **Start API server**:
   ```bash
   python api_server.py
   ```

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Dashboard/      # Dashboard-specific components
│   ├── Layout/         # Layout and navigation
│   └── UI/            # Generic UI components
├── pages/              # Page components
│   ├── Dashboard.js    # Main dashboard
│   ├── Analysis.js     # Technical analysis
│   ├── Portfolio.js    # Portfolio management
│   └── AIFeatures.js   # AI-powered features
├── services/           # API services
│   └── api.js         # API client functions
├── store/              # State management
│   └── store.js       # Zustand store
├── App.js              # Main app component
├── index.js            # App entry point
└── index.css           # Global styles
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_GOOGLE_API_KEY=your_api_key_here
```

### API Configuration
The React app is configured to proxy API requests to `http://localhost:5000` by default. Update the `proxy` field in `package.json` if needed.

## 🎯 Usage

### Getting Started
1. Start the Flask API server: `python api_server.py`
2. Start the React development server: `npm start`
3. Open `http://localhost:3000` in your browser
4. Enter a stock symbol (e.g., AAPL) in the sidebar
5. Explore different analysis tools and features

### Portfolio Management
1. Navigate to the Portfolio page
2. Initialize your portfolio with initial capital
3. Add funds as needed
4. Generate AI trading signals
5. Execute trades based on recommendations
6. Monitor performance and rebalance when needed

### AI Features
1. Go to the AI Features page
2. Select from 5 different AI analysis tools
3. Configure parameters (investment amount, risk tolerance, time horizon)
4. View AI-generated insights and recommendations

## 🔌 API Endpoints

The React frontend communicates with the Flask backend through these endpoints:

### Stock Data
- `GET /api/stock/data` - Get stock price data
- `GET /api/stock/info` - Get stock information
- `GET /api/stock/technical` - Get technical indicators

### AI Predictions
- `GET /api/prediction` - Get AI price prediction
- `GET /api/sensitivity` - Get sensitivity analysis
- `POST /api/recommendations` - Get smart recommendations
- `POST /api/portfolio/growth` - Get portfolio growth analysis
- `GET /api/etf/analysis` - Get ETF analysis
- `POST /api/strategies/money-growth` - Get money growth strategies

### Portfolio Management
- `POST /api/portfolio/initialize` - Initialize portfolio
- `POST /api/portfolio/add-capital` - Add capital
- `POST /api/portfolio/signals` - Generate trading signals
- `POST /api/portfolio/execute` - Execute signal
- `GET /api/portfolio/summary` - Get portfolio summary
- `GET /api/portfolio/performance` - Track performance
- `POST /api/portfolio/rebalance` - Rebalance portfolio
- `POST /api/portfolio/save` - Save portfolio state
- `POST /api/portfolio/load` - Load portfolio state

### Chat/NLP
- `POST /api/chat/query` - Process natural language query
- `POST /api/chat/sentiment` - Analyze sentiment
- `GET /api/chat/insights` - Get conversation insights

## 🎨 Customization

### Styling
The app uses Tailwind CSS for styling. Customize the design by modifying:
- `tailwind.config.js` - Theme configuration
- `src/index.css` - Global styles and component classes

### Components
All components are modular and reusable. Add new features by:
1. Creating new components in `src/components/`
2. Adding new pages in `src/pages/`
3. Updating the routing in `src/App.js`

### State Management
The app uses Zustand for state management. Add new state by modifying `src/store/store.js`.

## 🚀 Deployment

### Production Build
1. Build the React app:
   ```bash
   npm run build
   ```

2. Serve the built files with a static server or integrate with your backend.

### Docker Deployment
Create a `Dockerfile` for containerized deployment:

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔮 Future Enhancements

### Planned Features
- **Real-time Charts**: Integration with Recharts for interactive data visualization
- **WebSocket Support**: Real-time data updates
- **Advanced Filtering**: Enhanced stock screening and filtering
- **Mobile App**: React Native version
- **Social Features**: Portfolio sharing and community features
- **Advanced Analytics**: More sophisticated technical indicators
- **Backtesting**: Historical strategy testing
- **Paper Trading**: Risk-free trading simulation

### Chart Implementation
The current version includes placeholder chart areas. To implement real charts:

1. Install chart library: `npm install recharts`
2. Create chart components in `src/components/Charts/`
3. Replace placeholder divs with actual chart components
4. Pass data from API responses to chart components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation
- Review the console for error messages
- Ensure the backend server is running
- Verify your API keys are correctly set

## 🔗 Links

- [React Documentation](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Query](https://react-query.tanstack.com/)
- [Heroicons](https://heroicons.com/) 