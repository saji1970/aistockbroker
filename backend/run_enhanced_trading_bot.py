#!/usr/bin/env python3
"""
Enhanced Shadow Trading Bot Runner
Demonstrates the new AI-powered day trading capabilities with Gemini integration
"""

import argparse
import sys
from shadow_trading_bot import ShadowTradingBot

def main():
    parser = argparse.ArgumentParser(description='Run Enhanced AI Shadow Trading Bot')
    parser.add_argument('--capital', type=float, default=100000.0, help='Initial capital (default: $100,000)')
    parser.add_argument('--target', type=float, help='Target amount (default: 10% above capital)')
    parser.add_argument('--strategy', default='ai_gemini', choices=['ai_gemini', 'momentum', 'mean_reversion', 'rsi'],
                       help='Trading strategy to use (default: ai_gemini)')
    parser.add_argument('--interval', type=int, default=300, help='Trading interval in seconds (default: 300)')
    parser.add_argument('--watchlist', nargs='+', default=['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'NVDA'],
                       help='Stock symbols to watch (default: tech stocks)')
    parser.add_argument('--target-percent', type=float, default=0.1, help='Target percentage gain (default: 0.1 = 10%)')
    parser.add_argument('--demo', action='store_true', help='Run in demo mode with reduced position sizes')
    parser.add_argument('--evaluation-hour', type=int, default=16, help='Hour for daily evaluation (default: 16 = 4PM)')

    args = parser.parse_args()

    # Calculate target amount if not provided
    if args.target is None:
        args.target = args.capital * (1 + args.target_percent)

    print("🤖 Enhanced AI Shadow Trading Bot")
    print("="*60)
    print(f"💰 Initial Capital: ${args.capital:,.2f}")
    print(f"🎯 Target Amount: ${args.target:,.2f} ({args.target_percent:.1%} gain)")
    print(f"📈 Strategy: {args.strategy}")
    print(f"📊 Watchlist: {', '.join(args.watchlist)}")
    print(f"🔄 Interval: {args.interval} seconds")
    print(f"📅 Daily Evaluation: {args.evaluation_hour}:00")
    if args.demo:
        print("🚧 Demo Mode: Reduced position sizes")
    print("="*60)

    # Create enhanced trading bot
    bot = ShadowTradingBot(
        initial_capital=args.capital,
        target_amount=args.target,
        trading_strategy=args.strategy,
        enable_ml_learning=True,
        milestone_target_percent=args.target_percent,
        max_position_size=0.05 if args.demo else 0.1  # Smaller positions in demo mode
    )

    # Add watchlist symbols
    for symbol in args.watchlist:
        bot.add_to_watchlist(symbol)

    # Schedule daily evaluation
    bot.schedule_daily_evaluation(hour=args.evaluation_hour)

    try:
        # Start trading
        print(f"🚀 Starting trading bot...")
        bot.start(interval=args.interval)

    except KeyboardInterrupt:
        print("\n🛑 Trading bot stopped by user.")

    finally:
        # Stop the bot
        bot.stop()

        # Perform final evaluation
        print("🔍 Performing final evaluation...")
        bot.perform_daily_evaluation()

        # Print final report
        report = bot.get_performance_report()
        ml_insights = bot.get_ml_insights()
        strategy_insights = bot.get_strategy_insights()

        print("\n" + "="*60)
        print("🏁 FINAL PERFORMANCE REPORT")
        print("="*60)
        print(f"📊 Portfolio Performance:")
        print(f"   Initial Capital: ${report['initial_capital']:,.2f}")
        print(f"   Final Value: ${report['current_value']:,.2f}")
        print(f"   Total Return: {report['total_return_pct']:.2f}%")
        print(f"   Cash Available: ${report['cash']:,.2f}")
        print(f"   Active Positions: {report['positions_count']}")
        print(f"   Total Orders: {report['orders_count']}")
        print()

        print(f"🎯 Milestone Progress:")
        print(f"   Target Amount: ${args.target:,.2f}")
        print(f"   Progress: {bot.portfolio.milestone_progress:.1%}")
        print(f"   Daily Trades: {len(bot.portfolio.daily_trades)}")

        if bot.portfolio.milestone_progress >= 1.0:
            print("   🎉 MILESTONE ACHIEVED! 🎉")
        else:
            remaining = args.target - report['current_value']
            print(f"   Remaining to Target: ${remaining:,.2f}")
        print()

        print(f"🤖 AI Performance:")
        print(f"   Patterns Learned: {ml_insights['patterns_learned']}")
        print(f"   Model Accuracy: {ml_insights['accuracy_score']:.1%}")
        print(f"   Market Conditions: {ml_insights['market_conditions']}")
        print(f"   Total AI Trades: {ml_insights['total_trades']}")
        print(f"   Successful Trades: {ml_insights['successful_trades']}")
        print()

        if strategy_insights and 'message' not in strategy_insights:
            print(f"📈 Strategy Insights:")
            for strategy, data in strategy_insights.items():
                print(f"   {strategy}:")
                print(f"     Total Trades: {data['total_trades']}")
                print(f"     Total P&L: ${data['total_pnl']:,.2f}")
                print(f"     Accuracy: {data['average_accuracy']:.1%}")
                print(f"     Trend: {data['performance_trend']}")

        print("\n💡 AI Recommendations:")
        for rec in ml_insights['recommendations']:
            print(f"   • {rec}")

        print("\n📁 Data Files:")
        # Check if we're in a cloud environment
        import os
        is_cloud = os.environ.get('GAE_APPLICATION') or os.environ.get('GOOGLE_CLOUD_PROJECT')
        if is_cloud:
            print("   • Daily evaluation data logged to console (cloud deployment)")
            if bot.portfolio.milestone_progress >= 1.0:
                print("   • Milestone achievement data logged to console (cloud deployment)")
            print("   • Trading log available in cloud logs")
        else:
            print("   • Daily evaluation saved to daily_evaluation_YYYYMMDD.json")
            if bot.portfolio.milestone_progress >= 1.0:
                print("   • Milestone achievement saved to milestone_achievement_YYYYMMDD_HHMMSS.json")
            print("   • Trading log saved to trading_bot.log")

        print("\n" + "="*60)
        print("✅ Enhanced AI Shadow Trading Session Complete")
        print("="*60)

if __name__ == "__main__":
    main()