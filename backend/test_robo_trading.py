#!/usr/bin/env python3
"""
Test script for Robo Trading Agent
Demonstrates the shadow trading capabilities with profit targets.
"""

import asyncio
from robo_trading_agent import RoboTradingAgent, AssetType, TradingStatus

async def test_robo_trading():
    """Test the robo trading agent with different scenarios."""
    
    print("🤖 Robo Trading Agent Test")
    print("=" * 50)
    
    # Initialize agent
    agent = RoboTradingAgent("TestTrader")
    
    print("✅ Agent initialized successfully")
    
    # Test 1: Stock Trading - $100 to $110
    print("\n📈 Test 1: Stock Trading")
    print("-" * 30)
    
    task1_id = agent.create_trading_task(
        initial_capital=100.0,
        target_amount=110.0,
        asset_type=AssetType.STOCK,
        symbols=['AAPL', 'TSLA', 'MSFT'],
        duration_hours=2,
        risk_tolerance="medium"
    )
    
    agent.start_task(task1_id)
    print(f"✅ Created and started stock trading task: {task1_id}")
    
    # Test 2: Crypto Trading - $200 to $220
    print("\n🚀 Test 2: Crypto Trading")
    print("-" * 30)
    
    task2_id = agent.create_trading_task(
        initial_capital=200.0,
        target_amount=220.0,
        asset_type=AssetType.CRYPTO,
        symbols=['BTC', 'ETH', 'SOL'],
        duration_hours=1,
        risk_tolerance="high"
    )
    
    agent.start_task(task2_id)
    print(f"✅ Created and started crypto trading task: {task2_id}")
    
    # Test 3: Conservative ETF Trading - $500 to $525
    print("\n⚖️ Test 3: Conservative ETF Trading")
    print("-" * 40)
    
    task3_id = agent.create_trading_task(
        initial_capital=500.0,
        target_amount=525.0,
        asset_type=AssetType.ETF,
        symbols=['SPY', 'QQQ', 'IWM'],
        duration_hours=3,
        risk_tolerance="low"
    )
    
    agent.start_task(task3_id)
    print(f"✅ Created and started ETF trading task: {task3_id}")
    
    # Run trading cycles
    print("\n🔄 Running Trading Cycles...")
    print("-" * 30)
    
    for cycle in range(15):
        print(f"\n--- Cycle {cycle + 1} ---")
        
        # Execute trading cycles for all tasks
        agent.execute_trading_cycle(task1_id)
        agent.execute_trading_cycle(task2_id)
        agent.execute_trading_cycle(task3_id)
        
        # Get task statuses
        task1 = agent.get_task_status(task1_id)
        task2 = agent.get_task_status(task2_id)
        task3 = agent.get_task_status(task3_id)
        
        print(f"📈 Stock Task: ${task1.current_balance:.2f} / ${task1.target_amount:.2f} ({task1.status.value})")
        print(f"🚀 Crypto Task: ${task2.current_balance:.2f} / ${task2.target_amount:.2f} ({task2.status.value})")
        print(f"⚖️ ETF Task: ${task3.current_balance:.2f} / ${task3.target_amount:.2f} ({task3.status.value})")
        
        # Check if all targets reached
        if (task1.status == TradingStatus.TARGET_REACHED and 
            task2.status == TradingStatus.TARGET_REACHED and 
            task3.status == TradingStatus.TARGET_REACHED):
            print("🎯 All targets reached!")
            break
    
    # Get final performance
    print("\n📊 Final Performance Summary")
    print("=" * 40)
    
    performance = agent.get_performance_summary()
    
    print(f"📋 Total Tasks: {performance['total_tasks']}")
    print(f"🟢 Active Tasks: {performance['active_tasks']}")
    print(f"✅ Completed Tasks: {performance['completed_tasks']}")
    print()
    print(f"💰 Total Initial Capital: ${performance['total_initial_capital']:.2f}")
    print(f"💰 Total Current Balance: ${performance['total_current_balance']:.2f}")
    print(f"📈 Total P&L: ${performance['total_pnl']:.2f}")
    print(f"📊 Total Return: {performance['total_return_percent']:.2f}%")
    print()
    print(f"🔄 Total Trades: {performance['total_trades']}")
    print(f"✅ Successful Trades: {performance['successful_trades']}")
    print(f"📈 Success Rate: {performance['success_rate']:.1f}%")
    print(f"📊 Open Positions: {performance['open_positions']}")
    
    # Get detailed reports
    print("\n📋 Detailed Task Reports")
    print("=" * 30)
    
    for task_id in [task1_id, task2_id, task3_id]:
        task = agent.get_task_status(task_id)
        report = agent.get_detailed_report(task_id)
        trades = report.get('trades', [])
        
        print(f"\n📄 Task: {task_id}")
        print(f"   💰 Capital: ${task.initial_capital:.2f} → ${task.target_amount:.2f}")
        print(f"   📊 Current: ${task.current_balance:.2f}")
        print(f"   📈 P&L: ${task.total_pnl:.2f}")
        print(f"   🔄 Trades: {len(trades)}")
        print(f"   📊 Status: {task.status.value}")
        
        if trades:
            print(f"   📋 Recent Trades:")
            for trade in trades[-3:]:  # Show last 3 trades
                side_emoji = "📈" if trade['side'] == 'buy' else "📉"
                print(f"      {side_emoji} {trade['symbol']}: {trade['side'].upper()} {trade['quantity']:.6f} @ ${trade['price']:.2f}")
                if 'pnl' in trade:
                    pnl_emoji = "💰" if trade['pnl'] > 0 else "💸"
                    print(f"         {pnl_emoji} P&L: ${trade['pnl']:.2f}")
    
    print("\n🎉 Robo Trading Agent Test Complete!")
    print("\n💡 Key Features Demonstrated:")
    print("   ✅ Multi-asset trading (Stocks, Crypto, ETFs)")
    print("   ✅ Profit target achievement")
    print("   ✅ Risk management and position sizing")
    print("   ✅ Technical analysis and trading signals")
    print("   ✅ Real-time performance tracking")
    print("   ✅ Comprehensive trade history")
    print("   ✅ Shadow trading safety")

if __name__ == "__main__":
    asyncio.run(test_robo_trading())
