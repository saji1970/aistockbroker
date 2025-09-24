#!/usr/bin/env python3
"""
Setup Script for Converting Admin Users to Agents
Updates Saji and Ranjit to be agents and initializes the agent system
"""

import os
import sys
from datetime import datetime, timezone

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from models.user import User, UserRole, UserStatus, Base
import models.agent_models  # Import to register the models

def setup_database():
    """Initialize database with agent models"""
    try:
        # Initialize main database
        init_database()

        # Create agent-specific tables (they use the same Base as user models)
        Base.metadata.create_all(bind=db_manager.engine)

        print("Database initialized with agent models")
        return True
    except Exception as e:
        print(f"Database setup failed: {e}")
        return False

def convert_users_to_agents():
    """Convert Saji and Ranjit from admin to agent role"""
    with db_manager.get_session() as session:
        try:
            # Find and update Saji
            saji = session.query(User).filter_by(email='saji@aitrader.com').first()
            if saji:
                saji.role = UserRole.AGENT
                print(f"Converted {saji.email} to agent")
            else:
                print("Saji not found")

            # Find and update Ranjit
            ranjit = session.query(User).filter_by(email='ranjit@aitrader.com').first()
            if ranjit:
                ranjit.role = UserRole.AGENT
                print(f"Converted {ranjit.email} to agent")
            else:
                print("Ranjit not found")

            return True
        except Exception as e:
            print(f"Error converting users to agents: {e}")
            return False

def create_sample_customer():
    """Create a sample customer for testing"""
    with db_manager.get_session() as session:
        try:
            # Check if sample customer already exists
            existing = session.query(User).filter_by(email='demo.customer@aitrader.com').first()
            if existing:
                print("Sample customer already exists")
                return True

            # Get an agent to assign
            agent = session.query(User).filter_by(role=UserRole.AGENT).first()
            if not agent:
                print("No agents found to assign customer")
                return False

            # Create sample customer
            customer = User(
                email='demo.customer@aitrader.com',
                username='democustomer',
                password='DemoPassword123!',
                first_name='Demo',
                last_name='Customer',
                role=UserRole.CUSTOMER,
                status=UserStatus.ACTIVE,
                assigned_agent_id=agent.id,
                trading_experience='beginner',
                risk_tolerance='moderate',
                investment_goals='Long-term growth',
                initial_capital=10000.0,
                email_verified_at=datetime.now(timezone.utc)
            )

            session.add(customer)
            session.flush()

            # Create initial portfolio
            from models.agent_models import CustomerPortfolio
            portfolio = CustomerPortfolio(
                customer_id=customer.id,
                agent_id=agent.id,
                portfolio_name=f"{customer.first_name}'s Demo Portfolio",
                initial_capital=customer.initial_capital,
                current_cash=customer.initial_capital,
                total_value=customer.initial_capital,
                risk_level=customer.risk_tolerance
            )

            session.add(portfolio)

            print(f"Created sample customer: {customer.email}")
            print(f"Assigned to agent: {agent.email}")
            print(f"Created portfolio with ${customer.initial_capital} initial capital")

            return True
        except Exception as e:
            print(f"Error creating sample customer: {e}")
            return False

def verify_setup():
    """Verify the agent system setup"""
    with db_manager.get_session() as session:
        try:
            # Count agents
            agent_count = session.query(User).filter_by(role=UserRole.AGENT).count()
            print(f"Total agents: {agent_count}")

            # Count customers
            customer_count = session.query(User).filter_by(role=UserRole.CUSTOMER).count()
            print(f"Total customers: {customer_count}")

            # Count portfolios
            from models.agent_models import CustomerPortfolio
            portfolio_count = session.query(CustomerPortfolio).count()
            print(f"Total portfolios: {portfolio_count}")

            # List agents and their customers
            agents = session.query(User).filter_by(role=UserRole.AGENT).all()
            for agent in agents:
                customer_count = session.query(User).filter_by(
                    assigned_agent_id=agent.id,
                    role=UserRole.CUSTOMER
                ).count()
                print(f"  - {agent.email}: {customer_count} customers")

            return True
        except Exception as e:
            print(f"Verification failed: {e}")
            return False

def main():
    """Main setup function"""
    print("Setting up Agent System...")
    print("=" * 50)

    # Step 1: Setup database
    print("\nStep 1: Database Setup")
    if not setup_database():
        print("Setup failed at database initialization")
        return False

    # Step 2: Convert users to agents
    print("\nStep 2: Converting Users to Agents")
    if not convert_users_to_agents():
        print("Setup failed at user conversion")
        return False

    # Step 3: Create sample customer
    print("\nStep 3: Creating Sample Customer")
    if not create_sample_customer():
        print("Sample customer creation failed, but continuing...")

    # Step 4: Verify setup
    print("\nStep 4: Verification")
    if not verify_setup():
        print("Verification issues detected")

    print("\n" + "=" * 50)
    print("AGENT SYSTEM SETUP COMPLETE!")
    print("=" * 50)

    print("\nAGENT CREDENTIALS:")
    print("Agent 1: saji@aitrader.com / sajiai123@")
    print("Agent 2: ranjit@aitrader.com / ranjitai123@")

    print("\nSAMPLE CUSTOMER:")
    print("Customer: demo.customer@aitrader.com / DemoPassword123!")

    print("\nAPI ENDPOINTS:")
    print("Agent Dashboard: GET /api/agent/dashboard")
    print("Manage Customers: GET/POST /api/agent/customers")
    print("Portfolio Details: GET /api/agent/portfolios/<id>")
    print("Generate Suggestions: POST /api/agent/portfolios/<id>/suggestions/generate")
    print("Approve Suggestion: POST /api/agent/suggestions/<id>/approve")
    print("Reject Suggestion: POST /api/agent/suggestions/<id>/reject")

    print("\nNEXT STEPS:")
    print("1. Start the API server: python api_server.py")
    print("2. Login as agent to access dashboard")
    print("3. Create customers and manage portfolios")
    print("4. Generate AI trading suggestions")
    print("5. Approve/reject suggestions to train the AI")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)