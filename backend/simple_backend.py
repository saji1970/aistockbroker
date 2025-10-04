#!/usr/bin/env python3
"""
Simple Backend API for AI Stock Trading Platform
Minimal version with proper CORS support
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS to allow all origins for now
CORS(app, 
     origins="*", 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Stock Trading API',
        'version': '1.0.0',
        'message': 'Service is running successfully'
    })

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Login endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        logger.info(f"Login attempt with data: {data}")

        # Handle both 'username' and 'email_or_username' fields
        username = data.get('username') or data.get('email_or_username', '') if data else ''
        password = data.get('password', '') if data else ''
        requested_role = data.get('role', '') if data else ''

        logger.info(f"Extracted - username: {username}, role: {requested_role}")
        
        # Simple demo authentication with role-based responses
        if username and password:
            # Special case: ranjit user is always agent
            if username.lower() == 'ranjit':
                user_role = 'agent'
            # Use requested role if provided, otherwise assign based on username
            elif requested_role and requested_role in ['admin', 'agent', 'customer']:
                user_role = requested_role
            else:
                # Demo role assignment based on username
                user_role = 'customer'  # Default role
                if username.lower() in ['admin', 'administrator']:
                    user_role = 'admin'
                elif username.lower() in ['agent', 'broker', 'advisor']:
                    user_role = 'agent'
                elif username.lower() in ['user', 'customer', 'client']:
                    user_role = 'customer'
            
            return jsonify({
                'success': True,
                'token': 'demo_token_123',
                'refresh_token': 'demo_refresh_token_456',
                'user': {
                    'id': f'demo_{user_role}',
                    'username': username,
                    'role': user_role,
                    'status': 'active'
                },
                'expires_at': '2025-12-31T23:59:59Z',
                'message': f'Login successful as {user_role}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/verify-session', methods=['GET', 'POST', 'OPTIONS'])
def verify_session():
    """Verify user session"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and 'demo_token' in auth_header:
            # Extract user info from token (in a real app, this would decode the JWT)
            # For demo, we'll extract from the token string if it contains user info
            token = auth_header.replace('Bearer ', '')

            # Try to get user info from stored session or default to customer
            # In demo mode, we'll return success but let the client maintain user state
            return jsonify({
                'success': True,
                'valid': True,
                'message': 'Session verified'
            })
        else:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'No valid authorization token'
            }), 401
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        return jsonify({
            'success': False,
            'valid': False,
            'error': str(e)
        }), 500

@app.route('/api/auth/refresh-token', methods=['POST', 'OPTIONS'])
def refresh_token():
    """Refresh authentication token"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token', '') if data else ''
        
        # Simple demo refresh token validation
        if refresh_token and 'demo_refresh_token' in refresh_token:
            return jsonify({
                'success': True,
                'token': 'demo_token_123',
                'refresh_token': 'demo_refresh_token_456',
                'expires_at': '2025-12-31T23:59:59Z',
                'message': 'Token refreshed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid refresh token'
            }), 401
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/data', methods=['GET'])
def get_stock_data():
    """Get stock data"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        return jsonify({
            'symbol': symbol,
            'price': 150.25,
            'change': 2.15,
            'change_percent': 1.45,
            'volume': 1000000,
            'message': 'Demo data - configure real API for live data'
        })
    except Exception as e:
        logger.error(f"Stock data error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/info/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """Get stock information for validation"""
    try:
        market = request.args.get('market', 'US')
        
        # Simple validation - return basic info for common symbols
        common_symbols = {
            'AAPL': {'name': 'Apple Inc.', 'exchange': 'NASDAQ'},
            'MSFT': {'name': 'Microsoft Corporation', 'exchange': 'NASDAQ'},
            'GOOGL': {'name': 'Alphabet Inc.', 'exchange': 'NASDAQ'},
            'AMZN': {'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ'},
            'TSLA': {'name': 'Tesla Inc.', 'exchange': 'NASDAQ'},
            'META': {'name': 'Meta Platforms Inc.', 'exchange': 'NASDAQ'},
            'NVDA': {'name': 'NVIDIA Corporation', 'exchange': 'NASDAQ'},
            'NFLX': {'name': 'Netflix Inc.', 'exchange': 'NASDAQ'},
            'SPY': {'name': 'SPDR S&P 500 ETF Trust', 'exchange': 'NYSE'},
            'QQQ': {'name': 'Invesco QQQ Trust', 'exchange': 'NASDAQ'},
            'VOO': {'name': 'Vanguard S&P 500 ETF', 'exchange': 'NYSE'},
            'DAL': {'name': 'Delta Air Lines Inc.', 'exchange': 'NYSE'},
            'UAL': {'name': 'United Airlines Holdings Inc.', 'exchange': 'NASDAQ'},
            'AAL': {'name': 'American Airlines Group Inc.', 'exchange': 'NASDAQ'},
            'JPM': {'name': 'JPMorgan Chase & Co.', 'exchange': 'NYSE'},
            'BAC': {'name': 'Bank of America Corporation', 'exchange': 'NYSE'},
            'WMT': {'name': 'Walmart Inc.', 'exchange': 'NYSE'},
            'JNJ': {'name': 'Johnson & Johnson', 'exchange': 'NYSE'},
            'PG': {'name': 'Procter & Gamble Co.', 'exchange': 'NYSE'},
            'KO': {'name': 'The Coca-Cola Company', 'exchange': 'NYSE'}
        }
        
        if symbol in common_symbols:
            return jsonify({
                'symbol': symbol,
                'name': common_symbols[symbol]['name'],
                'exchange': common_symbols[symbol]['exchange'],
                'market': market,
                'valid': True
            })
        else:
            return jsonify({
                'symbol': symbol,
                'valid': False,
                'message': f'Symbol {symbol} not found in {market} market'
            }), 404
            
    except Exception as e:
        logger.error(f"Stock info error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction', methods=['GET'])
def get_prediction():
    """Get AI prediction"""
    try:
        symbol = request.args.get('symbol', 'AAPL')
        return jsonify({
            'symbol': symbol,
            'prediction': 'Bullish trend expected based on technical analysis',
            'confidence': 85,
            'target_price': 155.50,
            'sentiment': 'Bullish',
            'demo_mode': True,
            'message': 'Demo prediction - configure AI service for real predictions'
        })
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/query', methods=['POST', 'OPTIONS'])
def chat_query():
    """Process chat query"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        data = request.get_json()
        query = data.get('query', '') if data else ''

        # Provide more intelligent demo responses based on query keywords
        response = generate_demo_response(query)

        return jsonify({
            'response': response,
            'intent': detect_intent(query),
            'confidence': 0.85,
            'demo_mode': True
        })
    except Exception as e:
        logger.error(f"Chat query error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_demo_response(query):
    """Generate contextual demo responses"""
    query_lower = query.lower()

    if any(word in query_lower for word in ['price', 'cost', 'value', 'worth']):
        return f"Based on current market analysis, I can help you understand pricing trends. For specific stock prices, please check the dashboard or use the search feature."

    elif any(word in query_lower for word in ['buy', 'purchase', 'invest']):
        return f"For investment decisions, I recommend analyzing the stock's fundamentals, technical indicators, and market sentiment. Consider your risk tolerance and investment timeline."

    elif any(word in query_lower for word in ['sell', 'exit', 'profit']):
        return f"When considering selling, evaluate your profit targets, stop-loss levels, and overall portfolio allocation. Market conditions and news events should also factor into your decision."

    elif any(word in query_lower for word in ['portfolio', 'diversification', 'allocation']):
        return f"A well-diversified portfolio typically includes a mix of asset classes, sectors, and geographies. Consider your risk profile and investment goals when rebalancing."

    elif any(word in query_lower for word in ['risk', 'volatile', 'safe']):
        return f"Risk management is crucial in trading. Consider position sizing, stop-losses, and diversification to manage volatility. Higher potential returns often come with higher risks."

    elif any(word in query_lower for word in ['market', 'trend', 'economy']):
        return f"Current market trends show mixed signals. Economic indicators, Federal Reserve policies, and global events continue to influence market direction. Stay informed and maintain a long-term perspective."

    elif any(word in query_lower for word in ['aapl', 'apple']):
        return f"Apple (AAPL) is a large-cap technology stock with strong fundamentals. Consider factors like iPhone sales, services revenue, and new product launches when evaluating."

    elif any(word in query_lower for word in ['tsla', 'tesla']):
        return f"Tesla (TSLA) is known for high volatility and growth potential in the EV market. Monitor production numbers, regulatory changes, and competition in the space."

    else:
        return f"I understand you're asking about: '{query}'. As your AI trading assistant, I can help with stock analysis, market insights, trading strategies, and portfolio management. What specific aspect would you like to explore?"

def detect_intent(query):
    """Detect query intent for demo purposes"""
    query_lower = query.lower()

    if any(word in query_lower for word in ['price', 'cost', 'value']):
        return 'price_inquiry'
    elif any(word in query_lower for word in ['buy', 'purchase']):
        return 'buy_intent'
    elif any(word in query_lower for word in ['sell', 'exit']):
        return 'sell_intent'
    elif any(word in query_lower for word in ['portfolio', 'allocation']):
        return 'portfolio_management'
    elif any(word in query_lower for word in ['risk', 'volatile']):
        return 'risk_assessment'
    elif any(word in query_lower for word in ['market', 'trend']):
        return 'market_analysis'
    else:
        return 'general_inquiry'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Simple AI Stock Trading API Server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
