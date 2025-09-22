#!/usr/bin/env python3
"""
Trading Bot Startup Script
Run this script to start the AI trading bot with dashboard
"""

import sys
import os
import argparse
import logging
import threading
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_trading_bot import ShadowTradingBot
from advanced_trading_bot import AdvancedTradingBot
from trading_dashboard import app, bot, bot_thread

def setup_logging(level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('trading_bot.log'),
            logging.StreamHandler()
        ]
    )

def run_basic_bot(initial_capital=100000.0, interval=300):
    """Run the basic trading bot"""
    print("🤖 Starting Basic AI Trading Bot...")
    print(f"💰 Initial Capital: ${initial_capital:,.2f}")
    print(f"⏰ Trading Interval: {interval} seconds")
    print("="*50)
    
    bot_instance = ShadowTradingBot(initial_capital=initial_capital)
    
    # Add default watchlist
    default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
    for stock in default_stocks:
        bot_instance.add_to_watchlist(stock)
    
    print(f"📊 Watchlist: {', '.join(bot_instance.watchlist)}")
    print("🚀 Bot is running... Press Ctrl+C to stop")
    print("="*50)
    
    try:
        bot_instance.start(interval=interval)
    except KeyboardInterrupt:
        print("\n🛑 Stopping trading bot...")
        bot_instance.stop()
        
        # Print final report
        report = bot_instance.get_performance_report()
        print("\n" + "="*50)
        print("📈 FINAL PERFORMANCE REPORT")
        print("="*50)
        print(f"Initial Capital: ${report['initial_capital']:,.2f}")
        print(f"Final Value: ${report['current_value']:,.2f}")
        print(f"Total Return: {report['total_return_pct']:.2f}%")
        print(f"Cash: ${report['cash']:,.2f}")
        print(f"Positions: {report['positions_count']}")
        print(f"Total Orders: {report['orders_count']}")
        print("="*50)

def run_advanced_bot(initial_capital=100000.0, interval=300):
    """Run the advanced trading bot with ML"""
    print("🧠 Starting Advanced AI Trading Bot with ML...")
    print(f"💰 Initial Capital: ${initial_capital:,.2f}")
    print(f"⏰ Trading Interval: {interval} seconds")
    print("="*50)
    
    bot_instance = AdvancedTradingBot(initial_capital=initial_capital)
    
    # Add default watchlist
    default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
    for stock in default_stocks:
        bot_instance.add_to_watchlist(stock)
    
    print(f"📊 Watchlist: {', '.join(bot_instance.watchlist)}")
    print("🤖 Training ML models...")
    bot_instance.train_ml_models()
    print("🚀 Bot is running... Press Ctrl+C to stop")
    print("="*50)
    
    try:
        bot_instance.start(interval=interval)
    except KeyboardInterrupt:
        print("\n🛑 Stopping advanced trading bot...")
        bot_instance.stop()
        
        # Print final report
        report = bot_instance.get_advanced_performance_report()
        print("\n" + "="*60)
        print("📈 ADVANCED TRADING BOT PERFORMANCE REPORT")
        print("="*60)
        print(f"Initial Capital: ${report['initial_capital']:,.2f}")
        print(f"Final Value: ${report['current_value']:,.2f}")
        print(f"Total Return: {report['total_return_pct']:.2f}%")
        print(f"ML Model Trained: {report['ml_model_trained']}")
        print(f"Active Strategies: {report['strategies_active']}")
        print(f"Total Trades: {report['orders_count']}")
        print(f"Portfolio VaR: {report['risk_metrics']['portfolio_var']:.3f}")
        print("="*60)

def run_dashboard_only():
    """Run only the dashboard"""
    print("🌐 Starting Trading Bot Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🚀 Dashboard is running... Press Ctrl+C to stop")
    print("="*50)
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")

def run_bot_with_dashboard(bot_type='basic', initial_capital=100000.0, interval=300):
    """Run bot with dashboard"""
    print(f"🚀 Starting {bot_type.title()} Trading Bot with Dashboard...")
    print(f"💰 Initial Capital: ${initial_capital:,.2f}")
    print(f"⏰ Trading Interval: {interval} seconds")
    print("🌐 Dashboard: http://localhost:5000")
    print("="*50)
    
    # Initialize bot
    if bot_type == 'advanced':
        bot_instance = AdvancedTradingBot(initial_capital=initial_capital)
        bot_instance.train_ml_models()
    else:
        bot_instance = ShadowTradingBot(initial_capital=initial_capital)
    
    # Add default watchlist
    default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
    for stock in default_stocks:
        bot_instance.add_to_watchlist(stock)
    
    # Set global bot instance for dashboard
    global bot
    bot = bot_instance
    
    # Start bot in separate thread
    bot_thread_instance = threading.Thread(target=bot_instance.start, kwargs={'interval': interval})
    bot_thread_instance.daemon = True
    bot_thread_instance.start()
    
    print(f"📊 Watchlist: {', '.join(bot_instance.watchlist)}")
    print("🚀 Bot and Dashboard are running... Press Ctrl+C to stop")
    print("="*50)
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot and dashboard...")
        bot_instance.stop()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Trading Bot')
    parser.add_argument('--mode', choices=['basic', 'advanced', 'dashboard', 'full'], 
                       default='full', help='Bot mode to run')
    parser.add_argument('--capital', type=float, default=100000.0, 
                       help='Initial capital (default: 100000)')
    parser.add_argument('--interval', type=int, default=300, 
                       help='Trading interval in seconds (default: 300)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level)
    
    print("🤖 AI Stock Trading Bot")
    print("="*50)
    print(f"Mode: {args.mode}")
    print(f"Capital: ${args.capital:,.2f}")
    print(f"Interval: {args.interval}s")
    print(f"Log Level: {args.log_level}")
    print("="*50)
    
    try:
        if args.mode == 'basic':
            run_basic_bot(args.capital, args.interval)
        elif args.mode == 'advanced':
            run_advanced_bot(args.capital, args.interval)
        elif args.mode == 'dashboard':
            run_dashboard_only()
        elif args.mode == 'full':
            run_bot_with_dashboard('advanced', args.capital, args.interval)
            
    except Exception as e:
        logging.error(f"Error running trading bot: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
