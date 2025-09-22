#!/usr/bin/env python3
"""
Demo Script for AI Trading Bot
Quick demonstration of the trading bot capabilities
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_trading_bot import ShadowTradingBot, OrderType

def demo_basic_trading():
    """Demonstrate basic trading bot functionality"""
    print("🤖 AI Trading Bot Demo")
    print("="*50)
    print("This demo shows shadow trading with real market data")
    print("No real money is involved - it's all simulated!")
    print("="*50)
    
    # Create bot with $10,000 starting capital
    bot = ShadowTradingBot(initial_capital=10000.0)
    
    # Add some popular stocks to watchlist
    stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    print(f"📊 Adding stocks to watchlist: {', '.join(stocks)}")
    for stock in stocks:
        bot.add_to_watchlist(stock)
    
    print(f"\n💰 Starting Capital: ${bot.portfolio.cash:,.2f}")
    print(f"📈 Portfolio Value: ${bot.portfolio.total_value:,.2f}")
    
    # Run one trading cycle
    print("\n🚀 Running one trading cycle...")
    print("Analyzing market data and executing strategies...")
    
    try:
        bot.run_trading_cycle()
        
        # Show results
        print("\n📊 Trading Cycle Results:")
        print(f"💰 Cash: ${bot.portfolio.cash:,.2f}")
        print(f"📈 Portfolio Value: ${bot.portfolio.total_value:,.2f}")
        print(f"📋 Positions: {len(bot.portfolio.positions)}")
        print(f"📝 Orders: {len(bot.portfolio.orders)}")
        
        # Show positions
        if bot.portfolio.positions:
            print("\n📊 Current Positions:")
            for symbol, position in bot.portfolio.positions.items():
                print(f"  {symbol}: {position.quantity} shares @ ${position.avg_price:.2f}")
                print(f"    Current: ${position.current_price:.2f}")
                print(f"    P&L: ${position.unrealized_pnl:,.2f}")
        
        # Show recent orders
        if bot.portfolio.orders:
            print("\n📝 Recent Orders:")
            for order in bot.portfolio.orders[-3:]:  # Show last 3 orders
                print(f"  {order.order_type.value} {order.quantity} {order.symbol} @ ${order.price:.2f}")
                print(f"    Strategy: {order.strategy}, Reason: {order.reason}")
        
        # Performance report
        report = bot.get_performance_report()
        print(f"\n📈 Performance Report:")
        print(f"  Total Return: {report['total_return_pct']:.2f}%")
        print(f"  Profit/Loss: ${report['current_value'] - report['initial_capital']:,.2f}")
        
    except Exception as e:
        print(f"❌ Error during trading cycle: {e}")
    
    print("\n✅ Demo completed!")
    print("="*50)
    print("To run the full trading bot with dashboard:")
    print("python run_trading_bot.py --mode full")
    print("Then visit: http://localhost:5000")
    print("="*50)

if __name__ == "__main__":
    try:
        demo_basic_trading()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)
