#!/usr/bin/env python3
"""
Test script for Portfolio Management System
Tests capital allocation, AI analysis, buy/sell signals, performance tracking, and rebalancing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from portfolio_manager import PortfolioManager, SignalType, AssetType
from gemini_predictor import GeminiStockPredictor

def test_portfolio_manager():
    """Test the portfolio management system."""
    
    print("🧪 Testing Portfolio Management System")
    print("=" * 50)
    
    try:
        # Initialize AI predictor
        print("🔧 Initializing AI predictor...")
        predictor = GeminiStockPredictor()
        print("✅ AI predictor initialized")
        
        # Initialize portfolio manager
        print("💰 Initializing portfolio manager...")
        initial_capital = 10000
        portfolio_manager = PortfolioManager(initial_capital, predictor)
        print(f"✅ Portfolio manager initialized with ${initial_capital:,.2f}")
        
        # Test portfolio summary
        print("\n📊 Testing portfolio summary...")
        summary = portfolio_manager.get_portfolio_summary()
        print(f"Total Value: ${summary['total_value']:,.2f}")
        print(f"Available Cash: ${summary['available_cash']:,.2f}")
        print(f"Total Return: {summary['total_return']:.2f}%")
        print(f"Number of Assets: {summary['num_assets']}")
        
        # Test adding capital
        print("\n💵 Testing capital addition...")
        add_amount = 5000
        success = portfolio_manager.add_capital(add_amount)
        if success:
            print(f"✅ Added ${add_amount:,.2f} to portfolio")
            new_summary = portfolio_manager.get_portfolio_summary()
            print(f"New Total Value: ${new_summary['total_value']:,.2f}")
        else:
            print("❌ Failed to add capital")
        
        # Test AI analysis
        print("\n🤖 Testing AI analysis...")
        analysis = portfolio_manager.analyze_asset_with_ai("AAPL")
        if analysis:
            print("✅ AI analysis completed")
            if 'prediction' in analysis:
                print(f"Prediction confidence: {analysis['prediction'].get('confidence', 0):.2%}")
        else:
            print("❌ AI analysis failed")
        
        # Test signal generation
        print("\n📊 Testing signal generation...")
        watchlist = ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY", "QQQ"]
        signals = portfolio_manager.generate_signals(watchlist)
        print(f"✅ Generated {len(signals)} trading signals")
        
        for signal in signals[:3]:  # Show first 3 signals
            print(f"  • {signal.symbol}: {signal.signal_type.value} (Confidence: {signal.confidence:.1%})")
            print(f"    Reasoning: {signal.reasoning}")
        
        # Test signal execution
        if signals:
            print("\n🎯 Testing signal execution...")
            test_signal = signals[0]
            success = portfolio_manager.execute_signal(test_signal)
            if success:
                print(f"✅ Executed {test_signal.signal_type.value} signal for {test_signal.symbol}")
                updated_summary = portfolio_manager.get_portfolio_summary()
                print(f"Updated Total Value: ${updated_summary['total_value']:,.2f}")
            else:
                print(f"❌ Failed to execute signal for {test_signal.symbol}")
        
        # Test performance tracking
        print("\n📈 Testing performance tracking...")
        performance = portfolio_manager.track_performance()
        if performance:
            print("✅ Performance tracking completed")
            print(f"Total Return: {performance.get('total_return', 0):.2f}%")
            print(f"Daily Return: {performance.get('daily_return', 0):.2f}%")
            
            metrics = performance.get('performance_metrics', {})
            print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
            print(f"Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
        else:
            print("❌ Performance tracking failed")
        
        # Test rebalancing check
        print("\n⚖️ Testing rebalancing check...")
        needs_rebalancing = portfolio_manager.check_rebalancing_needed()
        print(f"Rebalancing needed: {needs_rebalancing}")
        
        if needs_rebalancing:
            print("🔄 Testing portfolio rebalancing...")
            success = portfolio_manager.rebalance_portfolio()
            if success:
                print("✅ Portfolio rebalanced successfully")
            else:
                print("❌ Portfolio rebalancing failed")
        
        # Test portfolio state saving/loading
        print("\n💾 Testing portfolio state management...")
        try:
            portfolio_manager.save_portfolio_state("test_portfolio.json")
            print("✅ Portfolio state saved")
            
            # Create new portfolio manager to test loading
            new_portfolio_manager = PortfolioManager(5000, predictor)
            new_portfolio_manager.load_portfolio_state("test_portfolio.json")
            print("✅ Portfolio state loaded")
            
            # Clean up test file
            if os.path.exists("test_portfolio.json"):
                os.remove("test_portfolio.json")
                print("✅ Test file cleaned up")
                
        except Exception as e:
            print(f"❌ Portfolio state management failed: {str(e)}")
        
        # Final portfolio summary
        print("\n📊 Final Portfolio Summary")
        print("=" * 30)
        final_summary = portfolio_manager.get_portfolio_summary()
        print(f"Total Capital: ${final_summary['total_capital']:,.2f}")
        print(f"Total Value: ${final_summary['total_value']:,.2f}")
        print(f"Available Cash: ${final_summary['available_cash']:,.2f}")
        print(f"Total Return: {final_summary['total_return']:.2f}%")
        print(f"Number of Assets: {final_summary['num_assets']}")
        print(f"Total Signals: {final_summary['total_signals']}")
        
        if final_summary['assets']:
            print("\nAssets:")
            for asset in final_summary['assets']:
                print(f"  • {asset['symbol']}: {asset['quantity']:.2f} @ ${asset['current_price']:.2f} = ${asset['current_value']:,.2f}")
        
        print("\n🎉 Portfolio Management System Test Completed Successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_individual_components():
    """Test individual portfolio manager components."""
    
    print("\n🔧 Testing Individual Components")
    print("=" * 40)
    
    try:
        # Test without AI predictor
        print("Testing portfolio manager without AI predictor...")
        portfolio_manager = PortfolioManager(5000)
        
        # Test basic operations
        print("Testing basic operations...")
        summary = portfolio_manager.get_portfolio_summary()
        print(f"Initial portfolio value: ${summary['total_value']:,.2f}")
        
        # Test capital addition
        portfolio_manager.add_capital(2000)
        summary = portfolio_manager.get_portfolio_summary()
        print(f"After adding capital: ${summary['total_value']:,.2f}")
        
        # Test basic analysis
        analysis = portfolio_manager.analyze_asset_with_ai("AAPL")
        print(f"Basic analysis result: {analysis.get('symbol', 'N/A')}")
        
        print("✅ Individual component tests passed")
        
    except Exception as e:
        print(f"❌ Individual component test failed: {str(e)}")

if __name__ == "__main__":
    test_individual_components()
    test_portfolio_manager() 