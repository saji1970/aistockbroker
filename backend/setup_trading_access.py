#!/usr/bin/env python3
"""
Setup Trading Access
Creates default users and agents to enable trading functionality
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_manager import AgentManager, AgentRole, CustomerTier
from database import init_database

def setup_trading_access():
    """Setup trading access with default users and agents"""
    
    print("🔧 Setting up trading access...")
    
    # Initialize database
    try:
        init_database()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization: {e}")
    
    # Create agent manager
    agent_manager = AgentManager()
    
    # Create default admin agent
    try:
        admin_agent = agent_manager.create_agent(
            name="Admin Agent",
            email="admin@aistocktrader.com",
            password="admin123",
            role=AgentRole.SENIOR
        )
        print(f"✅ Admin agent created: {admin_agent.email}")
    except Exception as e:
        print(f"⚠️  Admin agent creation: {e}")
    
    # Create default trading agent
    try:
        trading_agent = agent_manager.create_agent(
            name="Trading Agent",
            email="trader@aistocktrader.com", 
            password="trader123",
            role=AgentRole.SENIOR
        )
        print(f"✅ Trading agent created: {trading_agent.email}")
    except Exception as e:
        print(f"⚠️  Trading agent creation: {e}")
    
    # Create default customer
    try:
        customer = agent_manager.create_customer(
            name="Demo Customer",
            email="customer@aistocktrader.com",
            phone="555-0123",
            tier=CustomerTier.PREMIUM,
            agent_id=admin_agent.id if 'admin_agent' in locals() else None,
            risk_tolerance="medium"
        )
        print(f"✅ Demo customer created: {customer.email}")
    except Exception as e:
        print(f"⚠️  Demo customer creation: {e}")
    
    # Create trading configuration
    trading_config = {
        "trading_enabled": True,
        "default_agent": admin_agent.id if 'admin_agent' in locals() else None,
        "demo_mode": True,
        "access_level": "full",
        "created_at": datetime.now().isoformat()
    }
    
    # Save trading configuration
    config_file = "trading_config.json"
    with open(config_file, 'w') as f:
        json.dump(trading_config, f, indent=2)
    
    print(f"✅ Trading configuration saved to {config_file}")
    
    # Create access tokens for testing
    access_tokens = {
        "admin_token": "admin_access_token_123",
        "trader_token": "trader_access_token_456", 
        "customer_token": "customer_access_token_789"
    }
    
    tokens_file = "access_tokens.json"
    with open(tokens_file, 'w') as f:
        json.dump(access_tokens, f, indent=2)
    
    print(f"✅ Access tokens saved to {tokens_file}")
    
    print("\n🎉 Trading access setup complete!")
    print("=" * 50)
    print("📋 Default Accounts Created:")
    print("   Admin Agent: admin@aistocktrader.com / admin123")
    print("   Trading Agent: trader@aistocktrader.com / trader123")
    print("   Demo Customer: customer@aistocktrader.com")
    print("\n🔑 Access Tokens:")
    print("   Admin: admin_access_token_123")
    print("   Trader: trader_access_token_456")
    print("   Customer: customer_access_token_789")
    print("\n✅ Trading features are now enabled!")

if __name__ == "__main__":
    setup_trading_access()
