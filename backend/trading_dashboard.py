#!/usr/bin/env python3
"""
Trading Bot Dashboard - Web interface for monitoring shadow trading bot
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import threading
import time
import os
from datetime import datetime, timedelta
from shadow_trading_bot import ShadowTradingBot
import logging

app = Flask(__name__)
CORS(app, origins=[
    'https://ai-stock-trading-frontend-1024040140027.us-central1.run.app',
    'https://ai-stock-trading-frontend-ccrwk2lv6q-uc.a.run.app'
])

# Global bot instance
bot = None
bot_thread = None
dashboard_data = {
    'portfolio_history': [],
    'orders_history': [],
    'performance_metrics': {},
    'last_update': None
}

def update_dashboard_data():
    """Update dashboard data from bot"""
    global dashboard_data
    
    if bot:
        # Get current portfolio data
        portfolio_data = {
            'timestamp': datetime.now().isoformat(),
            'total_value': bot.portfolio.total_value,
            'cash': bot.portfolio.cash,
            'positions': {symbol: {
                'quantity': pos.quantity,
                'avg_price': pos.avg_price,
                'current_price': pos.current_price,
                'unrealized_pnl': pos.unrealized_pnl,
                'market_value': pos.market_value
            } for symbol, pos in bot.portfolio.positions.items()}
        }
        
        # Add to history (keep last 100 entries)
        dashboard_data['portfolio_history'].append(portfolio_data)
        if len(dashboard_data['portfolio_history']) > 100:
            dashboard_data['portfolio_history'] = dashboard_data['portfolio_history'][-100:]
            
        # Update orders history
        dashboard_data['orders_history'] = [
            {
                'id': order.id,
                'symbol': order.symbol,
                'order_type': order.order_type.value,
                'quantity': order.quantity,
                'price': order.price,
                'timestamp': order.timestamp.isoformat(),
                'strategy': order.strategy,
                'reason': order.reason
            } for order in bot.portfolio.orders[-50:]  # Last 50 orders
        ]
        
        # Update performance metrics
        dashboard_data['performance_metrics'] = bot.get_performance_report()
        dashboard_data['last_update'] = datetime.now().isoformat()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('trading_dashboard.html')

@app.route('/api/portfolio')
def get_portfolio():
    """Get current portfolio data"""
    if not bot:
        return jsonify({
            'cash': 100000,
            'positions': {},
            'timestamp': datetime.now().isoformat(),
            'total_value': 100000
        })
        
    update_dashboard_data()
    return jsonify(dashboard_data['portfolio_history'][-1] if dashboard_data['portfolio_history'] else {})

@app.route('/api/portfolio/history')
def get_portfolio_history():
    """Get portfolio history"""
    return jsonify(dashboard_data['portfolio_history'])

@app.route('/api/orders')
def get_orders():
    """Get recent orders"""
    return jsonify(dashboard_data['orders_history'])

@app.route('/api/performance')
def get_performance():
    """Get performance metrics"""
    return jsonify(dashboard_data['performance_metrics'])

@app.route('/api/config')
def get_bot_config():
    """Get current bot configuration"""
    if not bot:
        return jsonify({
            'initial_capital': 100000,
            'target_amount': None,
            'trading_period_days': 30,
            'max_position_size': 0.1,
            'max_daily_loss': 0.05,
            'risk_tolerance': 'medium',
            'trading_strategy': 'momentum',
            'enable_ml_learning': True,
            'status': 'not_initialized'
        })
        
    return jsonify({
        'initial_capital': bot.initial_capital,
        'target_amount': getattr(bot, 'target_amount', None),
        'trading_period_days': getattr(bot, 'trading_period_days', 30),
        'max_position_size': getattr(bot, 'max_position_size', 0.1),
        'max_daily_loss': getattr(bot, 'max_daily_loss', 0.05),
        'risk_tolerance': getattr(bot, 'risk_tolerance', 'medium'),
        'trading_strategy': getattr(bot, 'trading_strategy', 'momentum'),
        'enable_ml_learning': getattr(bot, 'enable_ml_learning', True),
        'status': 'running' if bot.running else 'stopped'
    })

@app.route('/api/learning/insights')
def get_ml_insights():
    """Get machine learning insights and patterns"""
    if not bot:
        return jsonify({
            'patterns_learned': 0,
            'accuracy_score': 0.0,
            'market_conditions': 'Bot not initialized',
            'recommendations': ['Start the bot to begin AI learning']
        })
        
    if not getattr(bot, 'enable_ml_learning', False):
        return jsonify({
            'patterns_learned': 0,
            'accuracy_score': 0.0,
            'market_conditions': 'ML learning disabled',
            'recommendations': ['Enable ML learning in bot configuration']
        })
        
    # Get ML insights from bot
    insights = getattr(bot, 'get_ml_insights', lambda: {
        'patterns_learned': 0,
        'accuracy_score': 0.0,
        'market_conditions': 'unknown',
        'recommendations': []
    })()
    
    return jsonify(insights)

@app.route('/api/watchlist')
def get_watchlist():
    """Get current watchlist"""
    if not bot:
        return jsonify({'watchlist': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']})
    return jsonify({'watchlist': bot.watchlist})

@app.route('/api/watchlist', methods=['POST'])
def update_watchlist():
    """Update watchlist"""
    if not bot:
        return jsonify({'error': 'Bot not initialized'}), 400
        
    data = request.get_json()
    action = data.get('action')
    symbol = data.get('symbol', '').upper()
    
    if action == 'add':
        bot.add_to_watchlist(symbol)
        return jsonify({'message': f'Added {symbol} to watchlist'})
    elif action == 'remove':
        bot.remove_from_watchlist(symbol)
        return jsonify({'message': f'Removed {symbol} from watchlist'})
    else:
        return jsonify({'error': 'Invalid action'}), 400

@app.route('/api/strategies')
def get_strategies():
    """Get available strategies"""
    if not bot:
        return jsonify({
            'momentum': {'name': 'Momentum Trading', 'parameters': {}},
            'mean_reversion': {'name': 'Mean Reversion', 'parameters': {}},
            'ml_enhanced': {'name': 'ML Enhanced', 'parameters': {}},
            'multi_strategy': {'name': 'Multi-Strategy', 'parameters': {}}
        })
        
    strategies = {}
    for name, strategy in bot.strategies.items():
        strategies[name] = {
            'name': strategy.name,
            'parameters': strategy.parameters
        }
    return jsonify(strategies)

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the trading bot with configuration"""
    global bot, bot_thread
    
    if bot and bot.running:
        return jsonify({'error': 'Bot is already running'}), 400
        
    try:
        config = request.get_json() or {}
        
        # Bot configuration parameters
        initial_capital = config.get('initial_capital', 100000.0)
        target_amount = config.get('target_amount', None)
        trading_period_days = config.get('trading_period_days', 30)
        max_position_size = config.get('max_position_size', 0.1)
        max_daily_loss = config.get('max_daily_loss', 0.05)
        risk_tolerance = config.get('risk_tolerance', 'medium')  # low, medium, high
        trading_strategy = config.get('trading_strategy', 'momentum')
        enable_ml_learning = config.get('enable_ml_learning', True)
        
        if not bot:
            bot = ShadowTradingBot(
                initial_capital=initial_capital,
                target_amount=target_amount,
                trading_period_days=trading_period_days,
                max_position_size=max_position_size,
                max_daily_loss=max_daily_loss,
                risk_tolerance=risk_tolerance,
                trading_strategy=trading_strategy,
                enable_ml_learning=enable_ml_learning
            )
        
        # Start bot in separate thread
        bot_thread = threading.Thread(target=bot.run, daemon=True)
        bot_thread.start()
        
        return jsonify({
            'message': 'Bot started successfully',
            'config': {
                'initial_capital': initial_capital,
                'target_amount': target_amount,
                'trading_period_days': trading_period_days,
                'max_position_size': max_position_size,
                'max_daily_loss': max_daily_loss,
                'risk_tolerance': risk_tolerance,
                'trading_strategy': trading_strategy,
                'enable_ml_learning': enable_ml_learning
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start bot: {str(e)}'}), 500

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot
    
    if not bot:
        return jsonify({'error': 'Bot not initialized'}), 400
        
    if not bot.running:
        return jsonify({'error': 'Bot is not running'}), 400
        
    bot.stop()
    return jsonify({'message': 'Trading bot stopped'})

@app.route('/api/status')
def get_status():
    """Get bot status"""
    if not bot:
        return jsonify({'status': 'stopped'})
        
    return jsonify({
        'status': 'running' if bot.running else 'stopped',
        'watchlist': bot.watchlist,
        'last_update': dashboard_data.get('last_update')
    })

def background_updater():
    """Background thread to update dashboard data"""
    while True:
        try:
            if bot and bot.running:
                update_dashboard_data()
            time.sleep(30)  # Update every 30 seconds
        except Exception as e:
            logging.error(f"Error in background updater: {e}")
            time.sleep(30)

if __name__ == '__main__':
    # Start background updater
    updater_thread = threading.Thread(target=background_updater)
    updater_thread.daemon = True
    updater_thread.start()
    
    # Get port from environment variable (for Cloud Run)
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    app.run(debug=False, host='0.0.0.0', port=port)
