# Gemini AI Integration Guide

## Overview

The AI Stock Trading Platform now includes Google's Gemini 1.5 Pro model specifically optimized for stock analysis and financial market insights. This integration provides advanced AI capabilities for:

- **Stock Analysis**: Comprehensive technical and fundamental analysis
- **Price Predictions**: AI-powered forecasting with confidence levels
- **Trading Strategies**: Intelligent trading recommendations
- **Market Insights**: Real-time sentiment and trend analysis
- **Portfolio Management**: AI-driven portfolio optimization

## Features

### 🧠 **Gemini 1.5 Pro Stock Expert**
- **Model**: `gemini-1.5-pro` - Google's most advanced language model
- **Optimized Settings**: Configured specifically for financial analysis
- **Temperature**: 0.3 (lower for more focused, consistent responses)
- **Max Tokens**: 4096 (extended context for detailed analysis)
- **Top-P**: 0.9 (balanced creativity and accuracy)
- **Top-K**: 40 (focused vocabulary selection)

### 📊 **Advanced Capabilities**
1. **Natural Language Processing**: Understands complex financial queries
2. **Technical Analysis**: RSI, MACD, Bollinger Bands, moving averages
3. **Fundamental Analysis**: Financial ratios, earnings, growth prospects
4. **Sentiment Analysis**: Market mood and investor confidence
5. **Risk Assessment**: Comprehensive risk evaluation
6. **LSTM-Inspired Analysis**: Pattern recognition and trend prediction

## Setup Instructions

### 1. **API Key Configuration**

Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY=your_actual_google_api_key_here
```

Or set environment variable:
```bash
export GOOGLE_API_KEY=your_actual_google_api_key_here
```

### 2. **Get Google API Key**

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 3. **Install Dependencies**

```bash
pip install google-generativeai
```

### 4. **Start the Backend Server**

```bash
python backend/api_server.py
```

## Usage

### **Frontend Integration**

The AI Assistant automatically uses Gemini when selected:

1. **Open AI Assistant**: Navigate to the AI Assistant page
2. **Select Model**: Choose "Gemini 1.5 Pro (Stock Expert)" from the dropdown
3. **Ask Questions**: Use natural language queries like:
   - "What's the price of AAPL?"
   - "Predict TSLA direction for tomorrow"
   - "Analyze the tech sector performance"
   - "Give me a day trading strategy for MSFT"

### **API Integration**

Use the dedicated Gemini endpoint:

```javascript
const response = await fetch('/api/ai/gemini-query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: "What's the current price of AAPL?",
    temperature: 0.3,
    maxTokens: 2048,
    market: 'US'
  })
});

const data = await response.json();
console.log(data.response);
```

## Query Types Supported

### 📈 **Stock Analysis Queries**
- Current price information
- Historical price data
- Technical indicators analysis
- Fundamental analysis
- Company information

### 🔮 **Prediction Queries**
- Price direction forecasts
- Short-term predictions (1-7 days)
- Medium-term outlook (1-3 months)
- Long-term projections (6-12 months)
- Volatility forecasting

### 🎯 **Trading Strategy Queries**
- Day trading strategies
- Swing trading approaches
- Risk management techniques
- Entry/exit point analysis
- Position sizing recommendations

### 📊 **Market Analysis Queries**
- Sector performance analysis
- Market sentiment evaluation
- Economic trend analysis
- Comparative analysis
- Ranking and listings

### 💼 **Portfolio Management Queries**
- Portfolio performance analysis
- Risk assessment
- Diversification recommendations
- Asset allocation suggestions
- Rebalancing strategies

## Advanced Features

### **LSTM-Inspired Analysis**
The system includes LSTM (Long Short-Term Memory) inspired pattern recognition:
- Trend direction analysis
- Momentum calculations
- Pattern identification
- Confidence scoring
- Multi-timeframe analysis

### **Sensitivity Analysis**
Comprehensive risk evaluation:
- Scenario modeling
- Stress testing
- Risk factor analysis
- Downside protection
- Volatility assessment

### **Real-time Data Integration**
- Live stock prices
- Market data feeds
- News sentiment analysis
- Technical indicators
- Volume analysis

## Configuration Options

### **Model Settings** (`backend/config.py`)
```python
# Model Configuration
GEMINI_MODEL = "gemini-1.5-pro"
MAX_TOKENS = 4096
TEMPERATURE = 0.3  # Lower for focused analysis
TOP_P = 0.9
TOP_K = 40
```

### **Generation Parameters**
- **Temperature**: Controls randomness (0.0-1.0)
- **Top-P**: Nucleus sampling parameter
- **Top-K**: Vocabulary selection limit
- **Max Tokens**: Maximum response length

## Error Handling

### **Fallback Responses**
When Gemini is unavailable, the system provides:
- Helpful guidance on setup
- Demo responses with examples
- Instructions for configuration
- Alternative analysis methods

### **Common Issues**

1. **API Key Not Set**
   ```
   Error: No Google API key found
   Solution: Configure GOOGLE_API_KEY in .env file
   ```

2. **Rate Limiting**
   ```
   Error: API quota exceeded
   Solution: Check your Google AI Studio quota
   ```

3. **Network Issues**
   ```
   Error: Connection timeout
   Solution: Check internet connection and firewall
   ```

## Testing

### **Run Integration Tests**
```bash
python test_gemini_integration.py
```

### **Test Queries**
```bash
# Test API endpoint
curl -X POST http://localhost:5000/api/ai/gemini-query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current price of AAPL?"}'
```

## Performance Optimization

### **Caching**
- Response caching for repeated queries
- Model initialization caching
- Configuration caching

### **Rate Limiting**
- Request throttling
- Batch processing
- Queue management

### **Monitoring**
- API usage tracking
- Performance metrics
- Error logging
- Response time monitoring

## Security Considerations

### **API Key Protection**
- Store keys in environment variables
- Never commit keys to version control
- Use secure key management systems
- Regular key rotation

### **Data Privacy**
- No personal data sent to Google
- Stock symbols only for analysis
- Local processing when possible
- Secure API communication

## Troubleshooting

### **Common Problems**

1. **"Gemini model not initialized"**
   - Check API key configuration
   - Verify internet connection
   - Check Google AI Studio access

2. **"Empty response from AI model"**
   - Check query format
   - Verify model availability
   - Check rate limits

3. **"Failed to generate response"**
   - Check API quota
   - Verify model permissions
   - Check error logs

### **Debug Mode**
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### **Query Optimization**
- Be specific with stock symbols
- Include timeframes when relevant
- Use clear, concise language
- Provide context when needed

### **Response Handling**
- Parse confidence scores
- Validate response format
- Handle errors gracefully
- Cache frequent queries

### **Integration**
- Use appropriate model selection
- Handle fallback scenarios
- Monitor performance
- Update configurations regularly

## Support

For issues or questions:
1. Check the error logs
2. Verify configuration
3. Test with simple queries
4. Check API status
5. Review documentation

## Changelog

### **v1.0.0** - Initial Gemini Integration
- Added Gemini 1.5 Pro support
- Optimized settings for stock analysis
- Integrated with AI Assistant frontend
- Added comprehensive API endpoints
- Implemented fallback responses
- Added testing suite

---

*This integration provides powerful AI capabilities for stock analysis while maintaining security and performance standards.*

