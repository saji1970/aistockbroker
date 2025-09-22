#!/usr/bin/env python3
"""
Robo Trading Interface - User-friendly interface for the robo trading agent
"""

import asyncio
import json
from datetime import datetime, timedelta
from robo_trading_agent import RoboTradingAgent, AssetType, TradingStatus

class RoboTradingInterface:
    """User-friendly interface for the robo trading agent."""
    
    def __init__(self):
        self.agent = RoboTradingAgent("SmartTrader")
        self.running = False
    
    def print_banner(self):
        """Print the application banner."""
        print("🤖" + "="*60 + "🤖")
        print("           ROBO TRADING AGENT - SHADOW TRADING SYSTEM")
        print("🤖" + "="*60 + "🤖")
        print()
        print("🎯 Features:")
        print("   • Shadow trading with profit targets")
        print("   • Support for stocks, crypto, forex, commodities")
        print("   • AI-powered technical analysis")
        print("   • Risk management and position sizing")
        print("   • Real-time market monitoring")
        print("   • Performance tracking and reporting")
        print()
    
    def print_menu(self):
        """Print the main menu."""
        print("📋 MAIN MENU:")
        print("1. 📈 Create Trading Task")
        print("2. 🚀 Start Trading Task")
        print("3. 🛑 Stop Trading Task")
        print("4. 📊 View Task Status")
        print("5. 📋 List All Tasks")
        print("6. 📈 View Performance Summary")
        print("7. 📄 Get Detailed Report")
        print("8. 🔄 Run Trading Simulation")
        print("9. 🎯 Quick Start Example")
        print("0. ❌ Exit")
        print()
    
    def get_user_input(self, prompt: str, input_type: str = "str") -> any:
        """Get user input with type conversion."""
        while True:
            try:
                user_input = input(prompt)
                if input_type == "float":
                    return float(user_input)
                elif input_type == "int":
                    return int(user_input)
                elif input_type == "list":
                    return [s.strip() for s in user_input.split(",")]
                else:
                    return user_input
            except ValueError:
                print("❌ Invalid input. Please try again.")
    
    def create_trading_task_interactive(self):
        """Interactive trading task creation."""
        print("\n📈 CREATE TRADING TASK")
        print("-" * 30)
        
        # Get basic parameters
        initial_capital = self.get_user_input("💰 Initial capital ($): ", "float")
        target_amount = self.get_user_input("🎯 Target amount ($): ", "float")
        
        if target_amount <= initial_capital:
            print("❌ Target amount must be greater than initial capital!")
            return None
        
        # Calculate profit percentage
        profit_percent = ((target_amount - initial_capital) / initial_capital) * 100
        print(f"📊 Target profit: {profit_percent:.1f}%")
        
        # Get asset type
        print("\n📊 Asset Type:")
        print("1. Stock")
        print("2. Crypto")
        print("3. Forex")
        print("4. Commodity")
        print("5. ETF")
        
        asset_choice = self.get_user_input("Select asset type (1-5): ", "int")
        asset_types = {
            1: AssetType.STOCK,
            2: AssetType.CRYPTO,
            3: AssetType.FOREX,
            4: AssetType.COMMODITY,
            5: AssetType.ETF
        }
        
        asset_type = asset_types.get(asset_choice, AssetType.STOCK)
        
        # Get symbols
        if asset_type == AssetType.STOCK:
            default_symbols = "AAPL,TSLA,MSFT,GOOGL,NVDA"
        elif asset_type == AssetType.CRYPTO:
            default_symbols = "BTC,ETH,SOL,ADA,DOT"
        elif asset_type == AssetType.FOREX:
            default_symbols = "EUR/USD,GBP/USD,USD/JPY,USD/CHF"
        elif asset_type == AssetType.COMMODITY:
            default_symbols = "GOLD,SILVER,OIL,NATURAL_GAS"
        else:
            default_symbols = "SPY,QQQ,IWM,VTI,VEA"
        
        print(f"📊 Default symbols for {asset_type.value}: {default_symbols}")
        symbols_input = self.get_user_input(f"Enter symbols (comma-separated) or press Enter for defaults: ")
        
        if symbols_input.strip():
            symbols = self.get_user_input("", "list")
        else:
            symbols = default_symbols.split(",")
        
        # Get duration
        duration_hours = self.get_user_input("⏰ Duration (hours, default 8): ", "int")
        if duration_hours <= 0:
            duration_hours = 8
        
        # Get risk tolerance
        print("\n⚠️ Risk Tolerance:")
        print("1. Low (Conservative)")
        print("2. Medium (Balanced)")
        print("3. High (Aggressive)")
        
        risk_choice = self.get_user_input("Select risk tolerance (1-3, default 2): ", "int")
        risk_levels = {1: "low", 2: "medium", 3: "high"}
        risk_tolerance = risk_levels.get(risk_choice, "medium")
        
        # Create task
        try:
            task_id = self.agent.create_trading_task(
                initial_capital=initial_capital,
                target_amount=target_amount,
                asset_type=asset_type,
                symbols=symbols,
                duration_hours=duration_hours,
                risk_tolerance=risk_tolerance
            )
            
            print(f"\n✅ Trading task created successfully!")
            print(f"🆔 Task ID: {task_id}")
            print(f"💰 Capital: ${initial_capital:.2f} → ${target_amount:.2f}")
            print(f"📊 Symbols: {', '.join(symbols)}")
            print(f"⏰ Duration: {duration_hours} hours")
            print(f"⚠️ Risk: {risk_tolerance}")
            
            return task_id
            
        except Exception as e:
            print(f"❌ Error creating task: {e}")
            return None
    
    def start_trading_task_interactive(self):
        """Interactive trading task start."""
        print("\n🚀 START TRADING TASK")
        print("-" * 25)
        
        # List available tasks
        tasks = self.agent.get_all_tasks()
        if not tasks:
            print("❌ No tasks available. Create a task first.")
            return
        
        print("📋 Available Tasks:")
        for i, task in enumerate(tasks, 1):
            status_emoji = "🟢" if task.status == TradingStatus.MONITORING else "🔴"
            print(f"{i}. {status_emoji} {task.id}")
            print(f"   💰 ${task.initial_capital:.2f} → ${task.target_amount:.2f}")
            print(f"   📊 {', '.join(task.symbols[:3])}...")
            print(f"   ⏰ {task.start_time.strftime('%H:%M')} - {task.end_time.strftime('%H:%M')}")
            print()
        
        task_choice = self.get_user_input("Select task to start (number): ", "int")
        if 1 <= task_choice <= len(tasks):
            task = tasks[task_choice - 1]
            try:
                self.agent.start_task(task.id)
                print(f"✅ Started trading task: {task.id}")
            except Exception as e:
                print(f"❌ Error starting task: {e}")
        else:
            print("❌ Invalid task selection.")
    
    def stop_trading_task_interactive(self):
        """Interactive trading task stop."""
        print("\n🛑 STOP TRADING TASK")
        print("-" * 22)
        
        # List active tasks
        tasks = self.agent.get_all_tasks()
        active_tasks = [t for t in tasks if t.status == TradingStatus.MONITORING]
        
        if not active_tasks:
            print("❌ No active tasks to stop.")
            return
        
        print("📋 Active Tasks:")
        for i, task in enumerate(active_tasks, 1):
            print(f"{i}. {task.id}")
            print(f"   💰 Current: ${task.current_balance:.2f} / Target: ${task.target_amount:.2f}")
            print(f"   📊 Trades: {task.trades_count}")
            print()
        
        task_choice = self.get_user_input("Select task to stop (number): ", "int")
        if 1 <= task_choice <= len(active_tasks):
            task = active_tasks[task_choice - 1]
            try:
                self.agent.stop_task(task.id)
                print(f"✅ Stopped trading task: {task.id}")
            except Exception as e:
                print(f"❌ Error stopping task: {e}")
        else:
            print("❌ Invalid task selection.")
    
    def view_task_status_interactive(self):
        """Interactive task status viewing."""
        print("\n📊 TASK STATUS")
        print("-" * 15)
        
        tasks = self.agent.get_all_tasks()
        if not tasks:
            print("❌ No tasks available.")
            return
        
        print("📋 All Tasks:")
        for i, task in enumerate(tasks, 1):
            status_emoji = {
                TradingStatus.IDLE: "⚪",
                TradingStatus.MONITORING: "🟢",
                TradingStatus.TARGET_REACHED: "🎯",
                TradingStatus.STOPPED: "🔴",
                TradingStatus.ERROR: "❌"
            }.get(task.status, "❓")
            
            print(f"{i}. {status_emoji} {task.id}")
            print(f"   💰 ${task.current_balance:.2f} / ${task.target_amount:.2f}")
            print(f"   📊 Status: {task.status.value}")
            print(f"   🔄 Trades: {task.trades_count}")
            print(f"   📈 P&L: ${task.total_pnl:.2f}")
            print()
        
        task_choice = self.get_user_input("Select task for detailed view (number, 0 for none): ", "int")
        if 1 <= task_choice <= len(tasks):
            task = tasks[task_choice - 1]
            self.show_detailed_task_info(task)
    
    def show_detailed_task_info(self, task):
        """Show detailed information for a specific task."""
        print(f"\n📄 DETAILED TASK INFO: {task.id}")
        print("=" * 50)
        print(f"💰 Initial Capital: ${task.initial_capital:.2f}")
        print(f"🎯 Target Amount: ${task.target_amount:.2f}")
        print(f"📊 Current Balance: ${task.current_balance:.2f}")
        print(f"📈 Total P&L: ${task.total_pnl:.2f}")
        print(f"📊 Target Profit: {task.target_profit_percent:.1f}%")
        print(f"🔄 Trades Count: {task.trades_count}")
        print(f"📈 Success Rate: {task.success_rate:.1f}%")
        print(f"📊 Asset Type: {task.asset_type.value}")
        print(f"📈 Symbols: {', '.join(task.symbols)}")
        print(f"⚠️ Risk Tolerance: {task.risk_tolerance}")
        print(f"⏰ Start Time: {task.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ End Time: {task.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Status: {task.status.value}")
        
        # Show recent trades
        report = self.agent.get_detailed_report(task.id)
        trades = report.get('trades', [])
        if trades:
            print(f"\n📋 Recent Trades ({len(trades)}):")
            for trade in trades[-5:]:  # Show last 5 trades
                side_emoji = "📈" if trade['side'] == 'buy' else "📉"
                print(f"   {side_emoji} {trade['symbol']}: {trade['side'].upper()} {trade['quantity']:.6f} @ ${trade['price']:.2f}")
                if 'pnl' in trade:
                    pnl_emoji = "💰" if trade['pnl'] > 0 else "💸"
                    print(f"      {pnl_emoji} P&L: ${trade['pnl']:.2f}")
    
    def view_performance_summary(self):
        """View overall performance summary."""
        print("\n📊 PERFORMANCE SUMMARY")
        print("-" * 25)
        
        performance = self.agent.get_performance_summary()
        
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
    
    def run_trading_simulation(self):
        """Run a trading simulation."""
        print("\n🔄 TRADING SIMULATION")
        print("-" * 25)
        
        # Create a quick example task
        task_id = self.agent.create_trading_task(
            initial_capital=100.0,
            target_amount=110.0,
            asset_type=AssetType.STOCK,
            symbols=['AAPL', 'TSLA', 'MSFT'],
            duration_hours=1,
            risk_tolerance="medium"
        )
        
        self.agent.start_task(task_id)
        print(f"✅ Created and started simulation task: {task_id}")
        
        # Run simulation cycles
        print("\n🔄 Running simulation cycles...")
        for cycle in range(10):
            self.agent.execute_trading_cycle(task_id)
            task = self.agent.get_task_status(task_id)
            
            print(f"Cycle {cycle + 1}: ${task.current_balance:.2f} / ${task.target_amount:.2f} ({task.status.value})")
            
            if task.status in [TradingStatus.TARGET_REACHED, TradingStatus.STOPPED]:
                break
        
        print("\n✅ Simulation complete!")
        self.show_detailed_task_info(task)
    
    def quick_start_example(self):
        """Quick start with predefined examples."""
        print("\n🎯 QUICK START EXAMPLES")
        print("-" * 25)
        
        print("Choose an example:")
        print("1. 💰 Conservative Stock Trading ($100 → $105)")
        print("2. 🚀 Aggressive Crypto Trading ($200 → $220)")
        print("3. ⚖️ Balanced Portfolio ($500 → $550)")
        
        choice = self.get_user_input("Select example (1-3): ", "int")
        
        if choice == 1:
            # Conservative stock trading
            task_id = self.agent.create_trading_task(
                initial_capital=100.0,
                target_amount=105.0,
                asset_type=AssetType.STOCK,
                symbols=['AAPL', 'MSFT', 'GOOGL'],
                duration_hours=4,
                risk_tolerance="low"
            )
            print("✅ Created conservative stock trading task")
            
        elif choice == 2:
            # Aggressive crypto trading
            task_id = self.agent.create_trading_task(
                initial_capital=200.0,
                target_amount=220.0,
                asset_type=AssetType.CRYPTO,
                symbols=['BTC', 'ETH', 'SOL'],
                duration_hours=2,
                risk_tolerance="high"
            )
            print("✅ Created aggressive crypto trading task")
            
        elif choice == 3:
            # Balanced portfolio
            task_id = self.agent.create_trading_task(
                initial_capital=500.0,
                target_amount=550.0,
                asset_type=AssetType.ETF,
                symbols=['SPY', 'QQQ', 'IWM'],
                duration_hours=6,
                risk_tolerance="medium"
            )
            print("✅ Created balanced portfolio task")
            
        else:
            print("❌ Invalid choice.")
            return
        
        # Start the task
        self.agent.start_task(task_id)
        print(f"🚀 Started task: {task_id}")
        
        # Run a few cycles
        print("\n🔄 Running initial trading cycles...")
        for cycle in range(5):
            self.agent.execute_trading_cycle(task_id)
            task = self.agent.get_task_status(task_id)
            print(f"Cycle {cycle + 1}: ${task.current_balance:.2f} / ${task.target_amount:.2f}")
            
            if task.status in [TradingStatus.TARGET_REACHED, TradingStatus.STOPPED]:
                break
        
        print(f"\n✅ Quick start complete! Task status: {task.status.value}")
    
    async def run_interface(self):
        """Run the main interface loop."""
        self.print_banner()
        
        while True:
            self.print_menu()
            choice = self.get_user_input("Select option (0-9): ", "int")
            
            if choice == 0:
                print("\n👋 Thank you for using Robo Trading Agent!")
                break
            elif choice == 1:
                self.create_trading_task_interactive()
            elif choice == 2:
                self.start_trading_task_interactive()
            elif choice == 3:
                self.stop_trading_task_interactive()
            elif choice == 4:
                self.view_task_status_interactive()
            elif choice == 5:
                tasks = self.agent.get_all_tasks()
                if tasks:
                    print(f"\n📋 All Tasks ({len(tasks)}):")
                    for task in tasks:
                        print(f"   • {task.id}: ${task.current_balance:.2f} / ${task.target_amount:.2f} ({task.status.value})")
                else:
                    print("\n❌ No tasks available.")
            elif choice == 6:
                self.view_performance_summary()
            elif choice == 7:
                tasks = self.agent.get_all_tasks()
                if tasks:
                    task_choice = self.get_user_input("Enter task ID for detailed report: ")
                    task = next((t for t in tasks if t.id == task_choice), None)
                    if task:
                        self.show_detailed_task_info(task)
                    else:
                        print("❌ Task not found.")
                else:
                    print("❌ No tasks available.")
            elif choice == 8:
                self.run_trading_simulation()
            elif choice == 9:
                self.quick_start_example()
            else:
                print("❌ Invalid option. Please try again.")
            
            print("\n" + "="*60)
            input("Press Enter to continue...")

def main():
    """Main function."""
    interface = RoboTradingInterface()
    asyncio.run(interface.run_interface())

if __name__ == "__main__":
    main()
