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

        logger.info(f"Extracted - username: {username}")
        
        # Simple demo authentication with role-based responses
        if username and password:
            # Demo user database with roles and passwords
            user_database = {
                'ranjit': {
                    'roles': ['agent'],
                    'name': 'Ranjit Kumar',
                    'email': 'ranjit@example.com',
                    'password': 'password'
                },
                'admin': {
                    'roles': ['admin'],
                    'name': 'Administrator',
                    'email': 'admin@example.com',
                    'password': 'password'
                },
                'john': {
                    'roles': ['customer'],
                    'name': 'John Smith',
                    'email': 'john@example.com',
                    'password': 'password'
                },
                'sarah': {
                    'roles': ['agent', 'customer'],
                    'name': 'Sarah Wilson',
                    'email': 'sarah@example.com',
                    'password': 'password'
                },
                'mike': {
                    'roles': ['admin', 'agent'],
                    'name': 'Mike Johnson',
                    'email': 'mike@example.com',
                    'password': 'password'
                },
                'saji': {
                    'roles': ['admin', 'agent'],
                    'name': 'Saji Kumar',
                    'email': 'saji@example.com',
                    'password': 'password'
                }
            }
            
            # Get user data from database
            user_data = user_database.get(username.lower())
            if user_data:
                # Check password
                if user_data['password'] != password:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid credentials'
                    }), 401
                
                user_roles = user_data['roles']
                has_multiple_roles = len(user_roles) > 1
                # For users with multiple roles, don't set a primary role
                # Let them choose in the frontend
                primary_role = user_roles[0] if not has_multiple_roles else None
            else:
                # User not found - return 401
                return jsonify({
                    'success': False,
                    'message': 'Invalid credentials'
                }), 401
            
            return jsonify({
                'success': True,
                'token': 'demo_token_123',
                'refresh_token': 'demo_refresh_token_456',
                'user': {
                    'id': f'demo_{username}',
                    'username': username,
                    'name': user_data['name'],
                    'email': user_data['email'],
                    'roles': user_roles,
                    'primary_role': primary_role,
                    'has_multiple_roles': has_multiple_roles,
                    'status': 'active'
                },
                'expires_at': '2025-12-31T23:59:59Z',
                'message': f'Login successful as {user_data["name"]}'
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
@app.route('/api/stock/data/<symbol>', methods=['GET'])
def get_stock_data(symbol=None):
    """Get stock data"""
    try:
        # Get symbol from URL parameter or query parameter
        symbol = symbol or request.args.get('symbol', 'AAPL')
        period = request.args.get('period', '1y')
        market = request.args.get('market', 'US')
        
        return jsonify({
            'symbol': symbol,
            'price': 150.25,
            'change': 2.15,
            'change_percent': 1.45,
            'volume': 1000000,
            'period': period,
            'market': market,
            'data': {
                'prices': [148.10, 149.25, 150.25, 151.50, 150.75],
                'dates': ['2024-09-30', '2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04'],
                'volume': [950000, 1100000, 1000000, 1050000, 980000]
            },
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

@app.route('/api/portfolio', methods=['GET', 'POST', 'OPTIONS'])
def portfolio():
    """Get or create portfolio"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        if request.method == 'GET':
            # Return demo portfolio data
            return jsonify({
                'portfolio': {
                    'id': 'demo_portfolio',
                    'balance': 10000.00,
                    'stocks': [
                        {'symbol': 'AAPL', 'shares': 10, 'avg_price': 150.00},
                        {'symbol': 'MSFT', 'shares': 5, 'avg_price': 300.00}
                    ],
                    'total_value': 15000.00,
                    'daily_change': 250.50,
                    'daily_change_percent': 1.69
                },
                'message': 'Demo portfolio data'
            })
        else:
            # POST - create portfolio
            return jsonify({
                'success': True,
                'portfolio_id': 'demo_portfolio_new',
                'message': 'Portfolio created successfully'
            })
    except Exception as e:
        logger.error(f"Portfolio error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/history', methods=['GET', 'OPTIONS'])
def portfolio_history():
    """Get portfolio history"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Return demo portfolio history
        return jsonify({
            'history': [
                {'date': '2024-09-30', 'value': 14800.00, 'change': -150.00},
                {'date': '2024-09-29', 'value': 14950.00, 'change': 100.00},
                {'date': '2024-09-28', 'value': 14850.00, 'change': -50.00}
            ],
            'message': 'Demo portfolio history'
        })
    except Exception as e:
        logger.error(f"Portfolio history error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/auth', methods=['POST', 'OPTIONS'])
def trading_auth():
    """Trading authentication endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        # Return demo trading auth token
        return jsonify({
            'success': True,
            'access_token': 'demo_trading_token_123',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'message': 'Trading authentication successful'
        })
    except Exception as e:
        logger.error(f"Trading auth error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/bot/status', methods=['GET', 'OPTIONS'])
def trading_bot_status():
    """Get trading bot status"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'status': 'active',
            'bot_id': 'demo_bot',
            'is_running': True,
            'last_update': '2024-09-30T09:15:00Z',
            'message': 'Demo bot status'
        })
    except Exception as e:
        logger.error(f"Trading bot status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/bot/start', methods=['POST', 'OPTIONS'])
def trading_bot_start():
    """Start trading bot"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'success': True,
            'message': 'Trading bot started successfully',
            'bot_id': 'demo_bot'
        })
    except Exception as e:
        logger.error(f"Trading bot start error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trading/bot/stop', methods=['POST', 'OPTIONS'])
def trading_bot_stop():
    """Stop trading bot"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'success': True,
            'message': 'Trading bot stopped successfully',
            'bot_id': 'demo_bot'
        })
    except Exception as e:
        logger.error(f"Trading bot stop error: {e}")
        return jsonify({'error': str(e)}), 500

# Additional trading bot endpoints
@app.route('/api/status', methods=['GET', 'OPTIONS'])
def get_bot_status():
    """Get trading bot status"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'status': 'active',
            'bot_id': 'demo_bot',
            'is_running': True,
            'last_update': '2024-09-30T09:15:00Z',
            'message': 'Demo bot status'
        })
    except Exception as e:
        logger.error(f"Bot status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance', methods=['GET', 'OPTIONS'])
def get_performance():
    """Get trading bot performance"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'performance': {
                'total_return': 15.6,
                'daily_return': 0.8,
                'weekly_return': 3.2,
                'monthly_return': 8.9,
                'sharpe_ratio': 1.8,
                'max_drawdown': -2.1,
                'win_rate': 68.5,
                'total_trades': 145,
                'profitable_trades': 99
            },
            'message': 'Demo performance data'
        })
    except Exception as e:
        logger.error(f"Performance error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['GET', 'OPTIONS'])
def get_orders():
    """Get trading orders"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'orders': [
                {
                    'id': 'order_001',
                    'symbol': 'AAPL',
                    'side': 'buy',
                    'quantity': 10,
                    'price': 150.25,
                    'status': 'filled',
                    'timestamp': '2024-09-30T09:10:00Z'
                },
                {
                    'id': 'order_002',
                    'symbol': 'MSFT',
                    'side': 'sell',
                    'quantity': 5,
                    'price': 305.80,
                    'status': 'pending',
                    'timestamp': '2024-09-30T09:15:00Z'
                }
            ],
            'message': 'Demo orders data'
        })
    except Exception as e:
        logger.error(f"Orders error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['GET', 'OPTIONS'])
def get_watchlist():
    """Get watchlist"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'watchlist': [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.25, 'change': 2.15},
                {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 305.80, 'change': -1.20},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 125.40, 'change': 0.85},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 245.60, 'change': -3.20}
            ],
            'message': 'Demo watchlist data'
        })
    except Exception as e:
        logger.error(f"Watchlist error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies', methods=['GET', 'OPTIONS'])
def get_strategies():
    """Get trading strategies"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'strategies': [
                {
                    'id': 'strategy_001',
                    'name': 'Momentum Trading',
                    'description': 'Buy on upward momentum, sell on downward momentum',
                    'active': True,
                    'performance': 12.5
                },
                {
                    'id': 'strategy_002',
                    'name': 'Mean Reversion',
                    'description': 'Buy oversold stocks, sell overbought stocks',
                    'active': False,
                    'performance': 8.3
                }
            ],
            'message': 'Demo strategies data'
        })
    except Exception as e:
        logger.error(f"Strategies error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/<symbol>', methods=['GET', 'OPTIONS'])
def get_prediction(symbol):
    """Get stock prediction"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'symbol': symbol,
            'prediction': {
                'direction': 'bullish',
                'confidence': 75.5,
                'target_price': 165.50,
                'timeframe': '1 week',
                'reasoning': 'Strong technical indicators and positive market sentiment',
                'stop_loss': 150.00,
                'technical_indicators': {
                    'rsi': 65.2,
                    'sma_20': 158.75,
                    'volatility': 0.18,
                    'price_change_pct': 2.35
                }
            },
            'message': 'Demo prediction data'
        })
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction/<symbol>/sensitivity', methods=['GET', 'OPTIONS'])
def get_prediction_sensitivity(symbol):
    """Get prediction sensitivity analysis"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        return jsonify({
            'symbol': symbol,
            'sensitivity': {
                'market_volatility': 0.65,
                'earnings_impact': 0.80,
                'sector_performance': 0.45,
                'news_sentiment': 0.70
            },
            'message': 'Demo sensitivity data'
        })
    except Exception as e:
        logger.error(f"Sensitivity error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/marketmate/query', methods=['GET', 'OPTIONS'])
def marketmate_query():
    """MarketMate API - Natural Language Market Queries"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        query = request.args.get('q', '')
        logger.info(f"MarketMate query: {query}")
        
        # Simple query processing for demo
        query_lower = query.lower()
        
        # Stock price queries
        if any(word in query_lower for word in ['price', 'cost', 'value', 'how much']):
            # Extract symbol from query
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA', 'AMZN', 'NFLX']
            symbol = None
            for s in symbols:
                if s.lower() in query_lower:
                    symbol = s
                    break
            
            if symbol:
                return jsonify({
                    'query': query,
                    'type': 'stock_price',
                    'symbol': symbol,
                    'price': 150.25,
                    'change': 2.15,
                    'change_percent': 1.45,
                    'message': f"{symbol} is currently trading at $150.25, up 1.45%"
                })
            else:
                return jsonify({
                    'query': query,
                    'type': 'general',
                    'message': 'I can help you with stock price information. Try asking about AAPL, MSFT, GOOGL, TSLA, META, or NVDA.'
                })
        
        # Prediction queries
        elif any(word in query_lower for word in ['predict', 'forecast', 'direction', 'tomorrow', 'next week']):
            return jsonify({
                'query': query,
                'type': 'prediction',
                'message': 'I can provide stock predictions. Please specify a stock symbol for more detailed analysis.',
                'suggestions': [
                    'Predict AAPL direction for tomorrow',
                    'What is the forecast for MSFT next week?',
                    'Analyze TSLA price direction'
                ]
            })
        
        # General market queries
        elif any(word in query_lower for word in ['market', 'overview', 'trend', 'analysis']):
            return jsonify({
                'query': query,
                'type': 'market_analysis',
                'message': 'Market analysis shows mixed signals with technology stocks leading gains.',
                'insights': [
                    'Technology sector up 2.3%',
                    'Healthcare sector down 0.5%',
                    'Overall market sentiment: Bullish'
                ]
            })
        
        # Default response
        else:
            return jsonify({
                'query': query,
                'type': 'general',
                'message': 'I can help you with stock prices, predictions, and market analysis. Try asking about specific stocks or market trends.',
                'examples': [
                    'What is the price of AAPL?',
                    'Predict MSFT direction for tomorrow',
                    'Market overview for today'
                ]
            })
            
    except Exception as e:
        logger.error(f"MarketMate error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Simple AI Stock Trading API Server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
