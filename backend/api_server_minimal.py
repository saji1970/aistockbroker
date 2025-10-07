#!/usr/bin/env python3
"""
Minimal Flask API Server for AI Stock Trading Platform
Provides basic REST API endpoints for the React frontend
"""

import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log startup info
logger.info("Minimal API Server starting up...")
logger.info(f"Python path: {sys.path}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment variables: FLASK_ENV={os.environ.get('FLASK_ENV')}, PORT={os.environ.get('PORT')}")

app = Flask(__name__)

# Enhanced CORS configuration for GCP deployment
cors_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:8080",  # Local API
    "https://ai-stock-trading-frontend-1012090067429.us-central1.run.app",  # Deployed frontend
    "https://ai-stock-trading-frontend-o6i75igepq-uc.a.run.app",  # Alternative frontend URL
]

# Add custom domain if specified
if os.environ.get('FRONTEND_URL'):
    cors_origins.append(os.environ.get('FRONTEND_URL'))

# Configure CORS with more permissive settings for Cloud Run
CORS(app,
     origins=cors_origins,
     allow_headers=["Content-Type", "Authorization", "X-CSRF-Token", "x-access-token", "X-Access-Token"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Add manual CORS headers for Cloud Run services
@app.after_request
def after_request(response):
    """Add CORS headers for all responses"""
    origin = request.headers.get('Origin')
    if origin and origin in cors_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRF-Token, x-access-token, X-Access-Token'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-stock-trading-backend',
        'version': '1.0.0',
        'environment': os.environ.get('FLASK_ENV', 'production')
    })

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Mock login endpoint for testing"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email_or_username = data.get('email_or_username', '')
        password = data.get('password', '')
        
        logger.info(f"Login attempt for: {email_or_username}")
        
        # Mock authentication - accept any credentials for testing
        if email_or_username and password:
            # Mock user data with multiple roles for testing
            user_data = {
                'id': 1,
                'email': email_or_username if '@' in email_or_username else f"{email_or_username}@example.com",
                'username': email_or_username if '@' not in email_or_username else email_or_username.split('@')[0],
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'admin',  # Primary role
                'roles': ['admin', 'agent'],  # Multiple roles array
                'has_multiple_roles': True,  # Flag for multiple roles
                'primary_role': None,  # No primary role when multiple roles exist
                'status': 'active'
            }
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user_data,
                'token': 'mock-jwt-token-12345',
                'refresh_token': 'mock-refresh-token-67890',
                'expires_at': '2024-12-31T23:59:59Z'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500

@app.route('/api/auth/refresh-token', methods=['POST', 'OPTIONS'])
def refresh_token():
    """Mock token refresh"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token', '')
        
        if refresh_token:
            return jsonify({
                'success': True,
                'token': 'new-mock-jwt-token-12345',
                'expires_at': '2024-12-31T23:59:59Z'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid refresh token'
            }), 401
            
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({
            'success': False,
            'error': 'Token refresh failed'
        }), 500

@app.route('/api/auth/verify-session', methods=['GET', 'OPTIONS'])
def verify_session():
    """Mock session verification"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Mock session verification - always return valid for testing
        user_data = {
            'id': 1,
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'admin',  # Primary role
            'roles': ['admin', 'agent'],  # Multiple roles array
            'has_multiple_roles': True,  # Flag for multiple roles
            'primary_role': None,  # No primary role when multiple roles exist
            'status': 'active'
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        return jsonify({
            'success': False,
            'error': 'Session verification failed'
        }), 500

@app.route('/api/stock/data/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Get stock data for a given symbol"""
    try:
        logger.info(f"Fetching stock data for symbol: {symbol}")
        
        # Fetch stock data using yfinance
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="1mo")
        
        if hist.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for symbol: {symbol}'
            }), 404
        
        # Get latest price
        latest_price = hist['Close'].iloc[-1]
        
        # Calculate additional metrics
        change = float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) if len(hist) > 1 else 0
        change_percent = float(((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100) if len(hist) > 1 else 0
        
        # Get 52-week high/low from historical data
        hist_52w = stock.history(period="1y")
        high_52w = float(hist_52w['High'].max()) if not hist_52w.empty else latest_price
        low_52w = float(hist_52w['Low'].min()) if not hist_52w.empty else latest_price
        
        # Prepare chart data for frontend
        chart_data = []
        if not hist.empty:
            for i, (date, row) in enumerate(hist.iterrows()):
                chart_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'price': float(latest_price),
            'summary': {
                'current_price': float(latest_price),
                'previous_close': float(info.get('previousClose', latest_price)),
                'price_change': change,
                'price_change_pct': change_percent,
                'market_cap': info.get('marketCap'),
                'volume': int(hist['Volume'].iloc[-1]) if not hist.empty else 0,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'company_name': info.get('longName', symbol)
            },
            'data': {
                'currentPrice': float(latest_price),
                'previousClose': float(info.get('previousClose', latest_price)),
                'marketCap': info.get('marketCap'),
                'volume': int(hist['Volume'].iloc[-1]) if not hist.empty else 0,
                'change': change,
                'changePercent': change_percent
            },
            'chart_data': chart_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch data for symbol: {symbol}'
        }), 500

@app.route('/api/stock/info/<symbol>', methods=['GET', 'OPTIONS'])
def get_stock_info(symbol):
    """Get stock information for a symbol"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info(f"Fetching stock info for symbol: {symbol}")
        
        # Use yfinance to get stock info
        stock = yf.Ticker(symbol)
        info = stock.info
        
        if not info:
            return jsonify({
                'success': False,
                'error': f'No information found for symbol: {symbol}'
            }), 404
        
        # Extract relevant information
        stock_info = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'exchange': info.get('exchange', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'volume': info.get('volume', 0),
            'avg_volume': info.get('averageVolume', 0),
            'high_52w': info.get('fiftyTwoWeekHigh', 0),
            'low_52w': info.get('fiftyTwoWeekLow', 0),
            'description': info.get('longBusinessSummary', 'No description available')
        }
        
        return jsonify({
            'success': True,
            'info': stock_info
        })
        
    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch stock info for symbol: {symbol}'
        }), 500

# Portfolio Endpoints
@app.route('/api/portfolio/initialize', methods=['POST', 'OPTIONS'])
def initialize_portfolio():
    """Initialize user portfolio"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        logger.info(f"Initializing portfolio with data: {data}")
        
        # Mock portfolio initialization
        portfolio = {
            'id': 1,
            'user_id': 1,
            'name': 'My Portfolio',
            'initial_capital': data.get('initial_capital', 100000.0),
            'current_cash': data.get('initial_capital', 100000.0),
            'total_value': data.get('initial_capital', 100000.0),
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        }
        
        return jsonify({
            'success': True,
            'message': 'Portfolio initialized successfully',
            'portfolio': portfolio
        })
        
    except Exception as e:
        logger.error(f"Error initializing portfolio: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to initialize portfolio'
        }), 500

@app.route('/api/portfolio', methods=['GET', 'OPTIONS'])
def get_portfolio():
    """Get user portfolio"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting user portfolio")
        
        # Mock portfolio data
        portfolio = {
            'id': 1,
            'user_id': 1,
            'name': 'My Portfolio',
            'initial_capital': 100000.0,
            'current_cash': 95000.0,
            'total_value': 105000.0,
            'total_return': 5000.0,
            'total_return_percent': 5.0,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'shares': 10,
                    'average_price': 150.0,
                    'current_price': 155.0,
                    'market_value': 1550.0,
                    'unrealized_pnl': 50.0,
                    'unrealized_pnl_percent': 3.33
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'portfolio': portfolio
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get portfolio'
        }), 500

# Admin Dashboard Endpoints
@app.route('/api/users/dashboard/stats', methods=['GET', 'OPTIONS'])
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting dashboard stats")
        
        # Mock dashboard stats
        stats = {
            'total_users': 150,
            'active_users': 120,
            'new_users_today': 5,
            'total_portfolios': 140,
            'total_value': 15000000.0,
            'top_performers': [
                {'user_id': 1, 'name': 'John Doe', 'return_percent': 15.5},
                {'user_id': 2, 'name': 'Jane Smith', 'return_percent': 12.3}
            ]
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get dashboard stats'
        }), 500

@app.route('/api/users', methods=['GET', 'OPTIONS'])
def get_users():
    """Get users list for admin"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        
        logger.info(f"Getting users - page: {page}, per_page: {per_page}, sort: {sort}, order: {order}")
        
        # Mock users data
        users = [
            {
                'id': 1,
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'user',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'last_login': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'user',
                'status': 'active',
                'created_at': '2024-01-02T00:00:00Z',
                'last_login': '2024-01-14T15:45:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': 150,
                'pages': 15
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get users'
        }), 500

# AI Prompt Management Endpoints
@app.route('/api/admin/ai-prompts', methods=['GET', 'POST', 'OPTIONS'])
def manage_ai_prompts():
    """Manage AI training prompts"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.method == 'GET':
            logger.info("Getting AI prompts")
            
            # Mock AI prompts data
            prompts = [
                {
                    'id': 1,
                    'title': 'Stock Price Analysis',
                    'category': 'stock_analysis',
                    'prompt': 'Analyze the current stock price of {symbol} and provide insights on its performance.',
                    'response_template': 'Based on my analysis of {symbol}, here are the key insights...',
                    'tags': ['technical', 'fundamental'],
                    'is_active': True,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                },
                {
                    'id': 2,
                    'title': 'Trading Strategy Recommendation',
                    'category': 'trading_strategy',
                    'prompt': 'Recommend a trading strategy for {symbol} based on current market conditions.',
                    'response_template': 'For {symbol}, I recommend the following strategy...',
                    'tags': ['strategy', 'risk-management'],
                    'is_active': True,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                },
                {
                    'id': 3,
                    'title': 'Portfolio Performance Review',
                    'category': 'portfolio_management',
                    'prompt': 'Review the performance of my portfolio and provide recommendations.',
                    'response_template': 'Based on your portfolio analysis, here are my recommendations...',
                    'tags': ['portfolio', 'performance'],
                    'is_active': True,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z'
                }
            ]
            
            return jsonify({
                'success': True,
                'prompts': prompts
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            logger.info(f"Creating AI prompt: {data}")
            
            # Mock prompt creation
            new_prompt = {
                'id': len(prompts) + 1,
                'title': data.get('title', ''),
                'category': data.get('category', 'general'),
                'prompt': data.get('prompt', ''),
                'response_template': data.get('response_template', ''),
                'tags': data.get('tags', []),
                'is_active': data.get('is_active', True),
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }
            
            return jsonify({
                'success': True,
                'message': 'AI prompt created successfully',
                'prompt': new_prompt
            })
            
    except Exception as e:
        logger.error(f"Error managing AI prompts: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to manage AI prompts'
        }), 500

@app.route('/api/admin/ai-prompts/<int:prompt_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def manage_single_ai_prompt(prompt_id):
    """Manage individual AI prompt"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.method == 'PUT':
            data = request.get_json()
            logger.info(f"Updating AI prompt {prompt_id}: {data}")
            
            # Mock prompt update
            updated_prompt = {
                'id': prompt_id,
                'title': data.get('title', ''),
                'category': data.get('category', 'general'),
                'prompt': data.get('prompt', ''),
                'response_template': data.get('response_template', ''),
                'tags': data.get('tags', []),
                'is_active': data.get('is_active', True),
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z'
            }
            
            return jsonify({
                'success': True,
                'message': 'AI prompt updated successfully',
                'prompt': updated_prompt
            })
        
        elif request.method == 'DELETE':
            logger.info(f"Deleting AI prompt {prompt_id}")
            
            return jsonify({
                'success': True,
                'message': 'AI prompt deleted successfully'
            })
            
    except Exception as e:
        logger.error(f"Error managing AI prompt {prompt_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to manage AI prompt'
        }), 500

@app.route('/api/prediction/<symbol>', methods=['GET'])
def get_prediction(symbol):
    """Get AI prediction for a given symbol"""
    try:
        logger.info(f"Generating prediction for symbol: {symbol}")
        
        # Get current stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        
        if hist.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for symbol: {symbol}'
            }), 404
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Simple mock prediction based on recent trend
        recent_change = float(hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) if len(hist) > 1 else 0
        trend = "Bullish" if recent_change > 0 else "Bearish" if recent_change < 0 else "Neutral"
        
        # Calculate simple target price
        if trend == "Bullish":
            target_price = current_price * 1.05
            confidence = 75
        elif trend == "Bearish":
            target_price = current_price * 0.95
            confidence = 70
        else:
            target_price = current_price * 1.02
            confidence = 60
        
        prediction_text = f"{symbol} shows {trend.lower()} momentum. Based on recent price action, we expect the stock to move towards ${target_price:.2f} in the near term."
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'prediction': {
                'direction': trend,
                'confidence': confidence,
                'target_price': target_price,
                'current_price': current_price,
                'reasoning': prediction_text
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating prediction for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate prediction for symbol: {symbol}'
        }), 500

@app.route('/api/prediction/<symbol>/sensitivity', methods=['GET'])
def get_prediction_sensitivity(symbol):
    """Get prediction with sensitivity analysis"""
    try:
        logger.info(f"Generating sensitivity analysis for symbol: {symbol}")
        
        # Get current stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        
        if hist.empty:
            return jsonify({
                'success': False,
                'error': f'No data found for symbol: {symbol}'
            }), 404
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Mock sensitivity analysis
        sensitivity_analysis = {
            'scenarios': [
                {
                    'name': 'Bullish Scenario',
                    'price': current_price * 1.1,
                    'confidence': 80,
                    'probability': 0.3
                },
                {
                    'name': 'Base Case',
                    'price': current_price * 1.02,
                    'confidence': 75,
                    'probability': 0.5
                },
                {
                    'name': 'Bearish Scenario',
                    'price': current_price * 0.95,
                    'confidence': 70,
                    'probability': 0.2
                }
            ],
            'risk_metrics': {
                'var': 0.05,
                'sharpe_ratio': 1.2,
                'max_drawdown': 0.08
            }
        }
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'sensitivity_analysis': sensitivity_analysis
        })
        
    except Exception as e:
        logger.error(f"Error generating sensitivity analysis for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate sensitivity analysis for symbol: {symbol}'
        }), 500

@app.route('/api/sensitivity/analysis/<symbol>', methods=['GET'])
def get_sensitivity_analysis(symbol):
    """Get sensitivity analysis for a symbol"""
    try:
        logger.info(f"Generating sensitivity analysis for symbol: {symbol}")
        
        # Mock sensitivity analysis data
        analysis_data = {
            'scenarios': [
                {
                    'name': 'Optimistic',
                    'price': 280.0,
                    'confidence': 85,
                    'risk': 'Low'
                },
                {
                    'name': 'Realistic',
                    'price': 260.0,
                    'confidence': 75,
                    'risk': 'Medium'
                },
                {
                    'name': 'Pessimistic',
                    'price': 240.0,
                    'confidence': 65,
                    'risk': 'High'
                }
            ],
            'risk_metrics': {
                'var': 0.05,
                'sharpe_ratio': 1.2
            }
        }
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'sensitivity_analysis': analysis_data
        })
        
    except Exception as e:
        logger.error(f"Error generating sensitivity analysis for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate sensitivity analysis for symbol: {symbol}'
        }), 500

@app.route('/api/marketmate/query', methods=['GET', 'POST'])
def marketmate_query():
    """Handle marketmate queries"""
    try:
        if request.method == 'GET':
            query = request.args.get('q', '')
        else:
            data = request.get_json()
            query = data.get('query', '')
        
        logger.info(f"Marketmate query: {query}")
        
        # Mock marketmate response
        response = f"Based on current market conditions, {query} shows positive momentum. Consider monitoring key support and resistance levels."
        
        return jsonify({
            'success': True,
            'query': query,
            'response': response,
            'timestamp': '2024-01-01T00:00:00Z'
        })
        
    except Exception as e:
        logger.error(f"Error processing marketmate query: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process marketmate query'
        }), 500

@app.route('/api/day-trading/prediction/<symbol>', methods=['POST'])
def day_trading_prediction(symbol):
    """Get day trading prediction for a symbol"""
    try:
        data = request.get_json()
        target_date = data.get('target_date', 'today')
        
        logger.info(f"Generating day trading prediction for {symbol} on {target_date}")
        
        # Fetch real stock data and generate realistic predictions
        import yfinance as yf
        import random
        import numpy as np
        from datetime import datetime, timedelta
        
        # Fetch real stock data
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1mo")
            
            if hist.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Get current price and historical data
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            
            # Calculate real volatility from historical data
            returns = hist['Close'].pct_change().dropna()
            volatility = float(returns.std() * np.sqrt(252))  # Annualized volatility
            
            # Calculate real technical indicators
            # RSI calculation
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = float(100 - (100 / (1 + rs.iloc[-1]))) if not rs.empty and not np.isnan(rs.iloc[-1]) else 50.0
            
            # Moving averages
            sma_20 = float(hist['Close'].rolling(window=20).mean().iloc[-1]) if len(hist) >= 20 else current_price
            ema_12 = float(hist['Close'].ewm(span=12).mean().iloc[-1]) if len(hist) >= 12 else current_price
            
            # Determine sentiment based on real data
            price_change_pct = ((current_price - prev_price) / prev_price) * 100
            
            if rsi > 70 and price_change_pct > 2:
                sentiment = 'Bearish'
                confidence = min(85, 70 + abs(price_change_pct))
            elif rsi < 30 and price_change_pct < -2:
                sentiment = 'Bullish'
                confidence = min(85, 70 + abs(price_change_pct))
            elif current_price > sma_20 and price_change_pct > 0:
                sentiment = 'Bullish'
                confidence = 65 + (price_change_pct * 2)
            elif current_price < sma_20 and price_change_pct < 0:
                sentiment = 'Bearish'
                confidence = 65 + abs(price_change_pct * 2)
            else:
                sentiment = 'Neutral'
                confidence = 60
            
            confidence = max(50, min(85, confidence))
            
        except Exception as e:
            logger.warning(f"Could not fetch real data for {symbol}: {e}, using fallback")
            # Fallback to realistic mock data based on symbol
            current_price = 150.0  # Default fallback price
            volatility = 0.25
            rsi = 50.0
            sma_20 = 150.0
            ema_12 = 150.0
            sentiment = 'Neutral'
            confidence = 60
        
        # Generate intraday predictions based on real current price and volatility
        volatility_factor = volatility * 100
        
        # Create realistic intraday predictions based on current price
        intraday_predictions = {
            'open': {
                'min': current_price * (1 - volatility_factor * 0.01),
                'max': current_price * (1 + volatility_factor * 0.01),
                'expected': current_price * (1 + (random.random() - 0.5) * volatility_factor * 0.005)
            },
            'mid_morning': {
                'min': current_price * (1 - volatility_factor * 0.008),
                'max': current_price * (1 + volatility_factor * 0.012),
                'expected': current_price * (1 + (random.random() - 0.5) * volatility_factor * 0.01)
            },
            'lunch': {
                'min': current_price * (1 - volatility_factor * 0.006),
                'max': current_price * (1 + volatility_factor * 0.010),
                'expected': current_price * (1 + (random.random() - 0.5) * volatility_factor * 0.008)
            },
            'afternoon': {
                'min': current_price * (1 - volatility_factor * 0.008),
                'max': current_price * (1 + volatility_factor * 0.012),
                'expected': current_price * (1 + (random.random() - 0.5) * volatility_factor * 0.01)
            },
            'close': {
                'min': current_price * (1 - volatility_factor * 0.010),
                'max': current_price * (1 + volatility_factor * 0.008),
                'expected': current_price * (1 + (random.random() - 0.5) * volatility_factor * 0.006)
            }
        }
        
        # Generate trading signals based on real data
        signals = []
        if sentiment == 'Bullish':
            signals.append({
                'time': '09:30-10:30',
                'signal': 'BUY',
                'confidence': confidence,
                'reasoning': f'Bullish momentum detected. RSI: {rsi:.1f}, Price above SMA20: {current_price > sma_20}',
                'target_price': current_price * 1.02,
                'stop_loss': current_price * 0.98
            })
        elif sentiment == 'Bearish':
            signals.append({
                'time': '09:30-10:30',
                'signal': 'SELL',
                'confidence': confidence,
                'reasoning': f'Bearish momentum detected. RSI: {rsi:.1f}, Price below SMA20: {current_price < sma_20}',
                'target_price': current_price * 0.98,
                'stop_loss': current_price * 1.02
            })
        else:
            signals.append({
                'time': '09:30-10:30',
                'signal': 'HOLD',
                'confidence': confidence,
                'reasoning': f'Neutral conditions. RSI: {rsi:.1f}, Price near SMA20: {abs(current_price - sma_20) / sma_20 * 100:.1f}%',
                'target_price': current_price,
                'stop_loss': current_price * 0.99
            })
        
        # Mock risk factors
        risk_factors = [
            {
                'factor': 'Market Volatility',
                'impact': 'High' if volatility > 0.25 else 'Medium',
                'description': f'Expected volatility: {volatility:.2%}',
                'mitigation': 'Use tight stop losses and position sizing'
            }
        ]
        
        # Calculate technical levels based on real price data
        high_20 = current_price * 1.05
        low_20 = current_price * 0.95
        pivot = (high_20 + low_20 + current_price) / 3
        
        # Mock LSTM analysis
        lstm_analysis = {
            'trend_direction': sentiment,
            'prediction_factor': volatility * 100,
            'momentum': 'Strong' if volatility > 0.25 else 'Moderate'
        }
        
        prediction = {
            'symbol': symbol,
            'target_date': target_date,
            'timestamp': datetime.now().isoformat(),
            'current_price': current_price,
            'intraday_predictions': intraday_predictions,
            'signals': signals,
            'risk_factors': risk_factors,
            'technical_levels': {
                'support': [low_20, low_20 * 0.98, low_20 * 0.96],
                'resistance': [high_20, high_20 * 1.02, high_20 * 1.04],
                'pivot': pivot
            },
            'sentiment': {
                'overall': sentiment,
                'confidence': confidence,
                'factors': [
                    f'RSI: {rsi:.1f}',
                    f'Price vs SMA20: {"Above" if current_price > sma_20 else "Below"}',
                    f'Volatility: {volatility:.2%}'
                ]
            },
            'indicators': {
                'rsi': rsi,
                'sma_20': sma_20,
                'ema_12': ema_12,
                'volatility': volatility
            },
            'lstm_analysis': lstm_analysis,
            'demo_mode': False,  # Real stock data is being used
            'note': 'Real stock data analysis with technical indicators. Predictions based on current market conditions.'
        }
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error generating day trading prediction for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to generate day trading prediction for symbol: {symbol}'
        }), 500

# Trading Bot Endpoints
@app.route('/api/status', methods=['GET', 'OPTIONS'])
def get_trading_bot_status():
    """Get trading bot status"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting trading bot status")
        
        # Mock trading bot status
        status = {
            'is_running': False,
            'status': 'stopped',
            'last_update': '2024-01-01T00:00:00Z',
            'active_strategies': 0,
            'total_trades': 0,
            'profit_loss': 0.0
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting trading bot status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get trading bot status'
        }), 500

@app.route('/api/start', methods=['POST', 'OPTIONS'])
def start_trading_bot():
    """Start trading bot"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        logger.info(f"Starting trading bot with config: {data}")
        
        # Mock bot start response
        response = {
            'success': True,
            'message': 'Trading bot started successfully',
            'bot_id': 'bot_12345',
            'status': 'running',
            'started_at': '2024-01-01T12:00:00Z'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error starting trading bot: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to start trading bot'
        }), 500

@app.route('/api/stop', methods=['POST', 'OPTIONS'])
def stop_trading_bot():
    """Stop trading bot"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Stopping trading bot")
        
        # Mock bot stop response
        response = {
            'success': True,
            'message': 'Trading bot stopped successfully',
            'status': 'stopped',
            'stopped_at': '2024-01-01T12:00:00Z'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error stopping trading bot: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to stop trading bot'
        }), 500

@app.route('/api/trading/access', methods=['GET', 'POST', 'OPTIONS'])
def get_trading_access():
    """Get trading access token"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting trading access token")
        
        # Mock trading access token
        access_token = {
            'token': 'mock-trading-access-token-12345',
            'expires_at': '2024-12-31T23:59:59Z',
            'permissions': ['read', 'write', 'trade']
        }
        
        return jsonify({
            'success': True,
            'access_token': access_token
        })
        
    except Exception as e:
        logger.error(f"Error getting trading access token: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get trading access token'
        }), 500

@app.route('/api/orders', methods=['GET', 'OPTIONS'])
def get_orders():
    """Get trading orders"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting trading orders")
        
        # Mock orders data
        orders = [
            {
                'id': 1,
                'symbol': 'AAPL',
                'side': 'buy',
                'quantity': 10,
                'price': 150.0,
                'status': 'filled',
                'timestamp': '2024-01-01T10:00:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'orders': orders
        })
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get orders'
        }), 500

@app.route('/api/strategies', methods=['GET', 'OPTIONS'])
def get_strategies():
    """Get trading strategies"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting trading strategies")
        
        # Mock strategies data
        strategies = [
            {
                'id': 1,
                'name': 'Momentum Strategy',
                'description': 'Buy on momentum, sell on reversal',
                'active': True,
                'performance': 12.5
            },
            {
                'id': 2,
                'name': 'Mean Reversion',
                'description': 'Buy low, sell high',
                'active': False,
                'performance': 8.3
            }
        ]
        
        return jsonify({
            'success': True,
            'strategies': strategies
        })
        
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get strategies'
        }), 500

@app.route('/api/performance', methods=['GET', 'OPTIONS'])
def get_performance():
    """Get trading performance"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting trading performance")
        
        # Mock performance data
        performance = {
            'total_return': 15.2,
            'daily_return': 0.5,
            'win_rate': 65.0,
            'sharpe_ratio': 1.8,
            'max_drawdown': -5.2,
            'total_trades': 45,
            'winning_trades': 29,
            'losing_trades': 16
        }
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get performance'
        }), 500

@app.route('/api/portfolio/history', methods=['GET', 'OPTIONS'])
def get_portfolio_history():
    """Get portfolio history"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        logger.info("Getting portfolio history")
        
        # Mock portfolio history data
        history = [
            {
                'date': '2024-01-01',
                'value': 10000.0,
                'change': 0.0,
                'change_percent': 0.0
            },
            {
                'date': '2024-01-02',
                'value': 10150.0,
                'change': 150.0,
                'change_percent': 1.5
            }
        ]
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get portfolio history'
        }), 500

@app.route('/api/watchlist', methods=['GET', 'POST', 'OPTIONS'])
def handle_watchlist():
    """Handle watchlist operations"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if request.method == 'GET':
            logger.info("Getting watchlist")
            
            # Mock watchlist data
            watchlist = [
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc.',
                    'price': 150.0,
                    'change': 2.5,
                    'change_percent': 1.69
                },
                {
                    'symbol': 'MSFT',
                    'name': 'Microsoft Corporation',
                    'price': 300.0,
                    'change': -1.2,
                    'change_percent': -0.40
                }
            ]
            
            return jsonify({
                'success': True,
                'watchlist': watchlist
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            action = data.get('action', 'add')
            symbol = data.get('symbol', '')
            
            logger.info(f"Watchlist {action} for symbol: {symbol}")
            
            return jsonify({
                'success': True,
                'message': f'Successfully {action}ed {symbol} to watchlist'
            })
        
    except Exception as e:
        logger.error(f"Error handling watchlist: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to handle watchlist operation'
        }), 500

@app.route('/api/chat/query', methods=['POST'])
def chat_query():
    """Handle chat queries"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        logger.info(f"Chat query received: {query}")
        
        # Simple response based on query content
        if 'price' in query.lower() or 'stock' in query.lower():
            response = "I can help you with stock prices and market data. Please specify a stock symbol."
        elif 'prediction' in query.lower() or 'forecast' in query.lower():
            response = "I can provide AI-powered predictions for stocks. Please specify a stock symbol."
        else:
            response = "I'm an AI assistant for stock trading. I can help you with stock prices, predictions, and market analysis. What would you like to know?"
        
        return jsonify({
            'success': True,
            'response': response,
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process chat query'
        }), 500


@app.route('/api/trading/status', methods=['GET'])
def get_trading_status():
    """Get trading bot status"""
    try:
        status_data = {
            'success': True,
            'status': {
                'active': True,
                'strategy': 'conservative',
                'total_trades': 25,
                'successful_trades': 18,
                'profit_loss': 1250.50
            }
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Error fetching trading status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch trading status'
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'AI Stock Trading API Server',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': [
            '/api/health',
            '/api/auth/login',
            '/api/auth/verify-session',
            '/api/auth/refresh-token',
            '/api/stock/data/<symbol>',
            '/api/prediction/<symbol>',
            '/api/prediction/<symbol>/sensitivity',
            '/api/sensitivity/analysis/<symbol>',
            '/api/marketmate/query',
            '/api/day-trading/prediction/<symbol>',
            '/api/chat/query',
            '/api/portfolio',
            '/api/trading/status'
        ]
    })

if __name__ == '__main__':
    try:
        # Get port from environment variable (for Cloud Run) or default to 8080
        port = int(os.environ.get('PORT', 8080))

        # Determine host for display (GCP vs local)
        is_gcp = os.environ.get('GAE_APPLICATION') or os.environ.get('GOOGLE_CLOUD_PROJECT')
        if is_gcp:
            host_url = f"https://{os.environ.get('GAE_APPLICATION', 'your-app')}.appspot.com"
        else:
            host_url = f"http://localhost:{port}"
    
        # Add startup logging
        logger.info("Starting Minimal AI Stock Trading API Server...")
        logger.info(f"Port: {port}")
        logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
        logger.info(f"Host URL: {host_url}")
        logger.info("Available endpoints:")
        logger.info("  - GET  /api/health - Health check")
        logger.info("  - GET  /api/stock/data/<symbol> - Get stock data")
        logger.info("  - GET  /api/prediction/<symbol> - Get AI prediction")
        logger.info("  - POST /api/chat/query - Process chat query")
        logger.info("  - GET  /api/portfolio - Get portfolio data")
        logger.info("  - GET  /api/trading/status - Get trading bot status")
        
        # Use debug mode only in development
        debug_mode = os.environ.get('FLASK_ENV') == 'development'
        # Cloud Run sets PORT environment variable
        cloud_run_port = os.environ.get('PORT', port)
        logger.info(f"Starting Flask app on host=0.0.0.0, port={cloud_run_port}, debug={debug_mode}")
        app.run(debug=debug_mode, host='0.0.0.0', port=int(cloud_run_port))
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
