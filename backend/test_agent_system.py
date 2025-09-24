"""
Comprehensive Unit Tests for Agent System
Tests agent management, customer management, AI suggestions, and learning capabilities
"""

import os
import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import shutil

# Import the modules to test
from agent_manager import AgentManager, AgentRole, CustomerTier, Agent, Customer, TradeSuggestion, AgentDecision
from ai_suggestion_engine import AISuggestionEngine, MarketAnalysis, AISuggestion
from agent_routes import agent_bp
from flask import Flask

class TestAgentManager:
    """Test cases for AgentManager"""
    
    @pytest.fixture
    def temp_data_file(self):
        """Create temporary data file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"agents": [], "customers": [], "trade_suggestions": [], "agent_decisions": [], "learning_data": []}')
            return f.name
    
    @pytest.fixture
    def agent_manager(self, temp_data_file):
        """Create AgentManager instance with temporary data file"""
        return AgentManager(data_file=temp_data_file)
    
    def test_create_agent(self, agent_manager):
        """Test agent creation"""
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        assert agent.name == "Test Agent"
        assert agent.email == "test@example.com"
        assert agent.role == AgentRole.SENIOR
        assert agent.id in agent_manager.agents
    
    def test_authenticate_agent(self, agent_manager):
        """Test agent authentication"""
        # Create agent first
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        # Test successful authentication
        authenticated_agent = agent_manager.authenticate_agent("test@example.com", "password123")
        assert authenticated_agent is not None
        assert authenticated_agent.id == agent.id
        
        # Test failed authentication
        failed_agent = agent_manager.authenticate_agent("test@example.com", "wrongpassword")
        assert failed_agent is None
    
    def test_create_customer(self, agent_manager):
        """Test customer creation"""
        # Create agent first
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        # Create customer
        customer = agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id,
            risk_tolerance="high"
        )
        
        assert customer.name == "Test Customer"
        assert customer.email == "customer@example.com"
        assert customer.tier == CustomerTier.PREMIUM
        assert customer.agent_id == agent.id
        assert customer.id in agent_manager.customers
        assert customer.id in agent.customers
    
    def test_get_agent_customers(self, agent_manager):
        """Test getting agent's customers"""
        # Create agent and customers
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        customer1 = agent_manager.create_customer(
            name="Customer 1",
            email="customer1@example.com",
            phone="123-456-7890",
            tier=CustomerTier.BASIC,
            agent_id=agent.id
        )
        
        customer2 = agent_manager.create_customer(
            name="Customer 2",
            email="customer2@example.com",
            phone="123-456-7891",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        # Get agent's customers
        customers = agent_manager.get_agent_customers(agent.id)
        assert len(customers) == 2
        assert customer1.id in [c.id for c in customers]
        assert customer2.id in [c.id for c in customers]
    
    def test_create_trade_suggestion(self, agent_manager):
        """Test trade suggestion creation"""
        # Create agent and customer
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        customer = agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        # Create trade suggestion
        suggestion = agent_manager.create_trade_suggestion(
            customer_id=customer.id,
            symbol="AAPL",
            action="buy",
            quantity=100,
            price=150.0,
            confidence=0.8,
            reasoning="Strong technical indicators",
            ai_model="gemini"
        )
        
        assert suggestion.symbol == "AAPL"
        assert suggestion.action == "buy"
        assert suggestion.quantity == 100
        assert suggestion.price == 150.0
        assert suggestion.confidence == 0.8
        assert suggestion.id in agent_manager.trade_suggestions
    
    def test_make_agent_decision(self, agent_manager):
        """Test agent decision making"""
        # Create agent, customer, and suggestion
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        customer = agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        suggestion = agent_manager.create_trade_suggestion(
            customer_id=customer.id,
            symbol="AAPL",
            action="buy",
            quantity=100,
            price=150.0,
            confidence=0.8,
            reasoning="Strong technical indicators",
            ai_model="gemini"
        )
        
        # Make decision
        decision = agent_manager.make_agent_decision(
            suggestion_id=suggestion.id,
            agent_id=agent.id,
            decision="accept",
            reasoning="Good technical analysis"
        )
        
        assert decision.suggestion_id == suggestion.id
        assert decision.agent_id == agent.id
        assert decision.decision == "accept"
        assert suggestion.status == "accept"
        assert suggestion.id in agent_manager.agent_decisions
    
    def test_get_learning_insights(self, agent_manager):
        """Test learning insights generation"""
        # Create some test data
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        customer = agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        # Add some learning data
        agent_manager.learning_data = [
            {
                'timestamp': datetime.now().isoformat(),
                'suggestion_id': 'test1',
                'customer_id': customer.id,
                'agent_id': agent.id,
                'agent_decision': {'decision': 'accept'},
                'learning_type': 'agent_decision'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'suggestion_id': 'test2',
                'customer_id': customer.id,
                'agent_id': agent.id,
                'agent_decision': {'decision': 'reject'},
                'learning_type': 'agent_decision'
            }
        ]
        
        insights = agent_manager.get_learning_insights()
        assert 'total_decisions' in insights
        assert 'acceptance_rate' in insights
        assert insights['total_decisions'] == 2
        assert insights['acceptance_rate'] == 50.0

class TestAISuggestionEngine:
    """Test cases for AISuggestionEngine"""
    
    @pytest.fixture
    def ai_engine(self):
        """Create AISuggestionEngine instance"""
        return AISuggestionEngine()
    
    @pytest.fixture
    def mock_market_data(self):
        """Mock market data for testing"""
        return {
            'symbol': 'AAPL',
            'current_price': 150.0,
            'historical_data': Mock(),
            'volume': 1000000,
            'high_52w': 200.0,
            'low_52w': 100.0,
            'timestamp': datetime.now()
        }
    
    def test_initialize_learning_weights(self, ai_engine):
        """Test learning weights initialization"""
        assert 'technical_indicators' in ai_engine.learning_weights
        assert 'fundamental_analysis' in ai_engine.learning_weights
        assert 'market_sentiment' in ai_engine.learning_weights
        assert 'agent_feedback' in ai_engine.learning_weights
        assert 'historical_performance' in ai_engine.learning_weights
        
        # Check that weights sum to 1
        total_weight = sum(ai_engine.learning_weights.values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_calculate_technical_indicators(self, ai_engine, mock_market_data):
        """Test technical indicators calculation"""
        # Mock pandas Series for testing
        with patch('pandas.Series') as mock_series:
            mock_series.return_value.rolling.return_value.mean.return_value = 150.0
            mock_series.return_value.ewm.return_value.mean.return_value = 150.0
            mock_series.return_value.iloc = [150.0]
            
            indicators = ai_engine._calculate_technical_indicators(mock_market_data)
            
            assert 'rsi' in indicators
            assert 'macd' in indicators
            assert 'moving_averages' in indicators
            assert 'bollinger_bands' in indicators
    
    def test_calculate_volatility(self, ai_engine, mock_market_data):
        """Test volatility calculation"""
        # Mock pandas operations
        with patch('pandas.Series') as mock_series:
            mock_series.return_value.pct_change.return_value.dropna.return_value.std.return_value = 0.2
            
            volatility = ai_engine._calculate_volatility(mock_market_data)
            assert isinstance(volatility, float)
            assert volatility >= 0
    
    def test_determine_trend(self, ai_engine, mock_market_data):
        """Test trend determination"""
        # Mock pandas operations
        with patch('pandas.Series') as mock_series:
            mock_series.return_value.tail.return_value.mean.return_value = 150.0
            
            trend = ai_engine._determine_trend(mock_market_data)
            assert trend in ['strong_uptrend', 'uptrend', 'sideways', 'downtrend', 'strong_downtrend']
    
    def test_calculate_confidence_score(self, ai_engine):
        """Test confidence score calculation"""
        technical_indicators = {'rsi': 50}
        sentiment = 'neutral'
        volatility = 0.2
        trend = 'sideways'
        
        confidence = ai_engine._calculate_confidence_score(
            technical_indicators, sentiment, volatility, trend
        )
        
        assert 0.0 <= confidence <= 1.0
    
    def test_update_learning_weights(self, ai_engine):
        """Test learning weights update"""
        initial_weights = ai_engine.learning_weights.copy()
        
        feedback_data = {
            'agent_acceptance_rate': 0.9
        }
        
        ai_engine.update_learning_weights(feedback_data)
        
        # Weights should be normalized
        total_weight = sum(ai_engine.learning_weights.values())
        assert abs(total_weight - 1.0) < 0.01

class TestAgentRoutes:
    """Test cases for agent API routes"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.secret_key = 'test_secret_key'
        app.register_blueprint(agent_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/agent/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_login_success(self, client):
        """Test successful login"""
        # Create agent first
        agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        response = client.post('/api/agent/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'agent' in data
        assert data['agent']['email'] == 'test@example.com'
    
    def test_login_failure(self, client):
        """Test failed login"""
        response = client.post('/api/agent/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_customer(self, client):
        """Test customer creation"""
        # Create agent first
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        # Login to get session
        login_response = client.post('/api/agent/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert login_response.status_code == 200
        
        # Create customer
        response = client.post('/api/agent/customers', json={
            'name': 'Test Customer',
            'email': 'customer@example.com',
            'phone': '123-456-7890',
            'tier': 'premium',
            'risk_tolerance': 'high'
        })
        
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'customer' in data
        assert data['customer']['name'] == 'Test Customer'
    
    def test_get_customers(self, client):
        """Test getting agent's customers"""
        # Create agent and customer
        agent = agent_manager.create_agent(
            name="Test Agent",
            email="test@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        agent_manager.create_customer(
            name="Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        # Login
        login_response = client.post('/api/agent/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert login_response.status_code == 200
        
        # Get customers
        response = client.get('/api/agent/customers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'customers' in data
        assert len(data['customers']) == 1
        assert data['customers'][0]['name'] == 'Test Customer'

class TestIntegration:
    """Integration tests for the complete agent system"""
    
    @pytest.fixture
    def temp_data_file(self):
        """Create temporary data file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"agents": [], "customers": [], "trade_suggestions": [], "agent_decisions": [], "learning_data": []}')
            return f.name
    
    @pytest.fixture
    def test_agent_manager(self, temp_data_file):
        """Create AgentManager instance with temporary data file"""
        return AgentManager(data_file=temp_data_file)
    
    @pytest.fixture
    def test_ai_engine(self):
        """Create AISuggestionEngine instance"""
        return AISuggestionEngine()
    
    def test_complete_workflow(self, test_agent_manager, test_ai_engine):
        """Test complete workflow from agent creation to decision making"""
        # 1. Create agent
        agent = test_agent_manager.create_agent(
            name="Integration Test Agent",
            email="integration@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        assert agent.id in test_agent_manager.agents
        
        # 2. Create customer
        customer = test_agent_manager.create_customer(
            name="Integration Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id,
            risk_tolerance="medium"
        )
        assert customer.id in test_agent_manager.customers
        
        # 3. Create trade suggestion
        suggestion = test_agent_manager.create_trade_suggestion(
            customer_id=customer.id,
            symbol="AAPL",
            action="buy",
            quantity=100,
            price=150.0,
            confidence=0.8,
            reasoning="Strong technical indicators",
            ai_model="gemini"
        )
        assert suggestion.id in test_agent_manager.trade_suggestions
        
        # 4. Agent makes decision
        decision = test_agent_manager.make_agent_decision(
            suggestion_id=suggestion.id,
            agent_id=agent.id,
            decision="accept",
            reasoning="Good analysis"
        )
        assert decision.suggestion_id == suggestion.id
        assert suggestion.status == "accept"
        
        # 5. Check learning data
        assert len(test_agent_manager.learning_data) == 1
        learning_entry = test_agent_manager.learning_data[0]
        assert learning_entry['agent_id'] == agent.id
        assert learning_entry['agent_decision']['decision'] == 'accept'
        
        # 6. Get learning insights
        insights = test_agent_manager.get_learning_insights()
        assert insights['total_decisions'] == 1
        assert insights['acceptance_rate'] == 100.0
    
    def test_agent_stats(self, test_agent_manager):
        """Test agent statistics calculation"""
        # Create agent and some data
        agent = test_agent_manager.create_agent(
            name="Stats Test Agent",
            email="stats@example.com",
            password="password123",
            role=AgentRole.SENIOR
        )
        
        customer = test_agent_manager.create_customer(
            name="Stats Test Customer",
            email="customer@example.com",
            phone="123-456-7890",
            tier=CustomerTier.PREMIUM,
            agent_id=agent.id
        )
        
        # Add some learning data
        test_agent_manager.learning_data = [
            {
                'timestamp': datetime.now().isoformat(),
                'suggestion_id': 'test1',
                'customer_id': customer.id,
                'agent_id': agent.id,
                'agent_decision': {'decision': 'accept'},
                'learning_type': 'agent_decision'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'suggestion_id': 'test2',
                'customer_id': customer.id,
                'agent_id': agent.id,
                'agent_decision': {'decision': 'reject'},
                'learning_type': 'agent_decision'
            }
        ]
        
        stats = test_agent_manager.get_agent_stats(agent.id)
        assert stats['agent_id'] == agent.id
        assert stats['total_customers'] == 1
        assert stats['total_decisions'] == 2
        assert stats['acceptance_rate'] == 50.0

# Performance tests
class TestPerformance:
    """Performance tests for the agent system"""
    
    def test_large_dataset_performance(self):
        """Test performance with large dataset"""
        import time
        
        # Create temporary data file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"agents": [], "customers": [], "trade_suggestions": [], "agent_decisions": [], "learning_data": []}')
            temp_file = f.name
        
        try:
            agent_manager = AgentManager(data_file=temp_file)
            
            # Create multiple agents and customers
            start_time = time.time()
            
            agents = []
            for i in range(100):
                agent = agent_manager.create_agent(
                    name=f"Agent {i}",
                    email=f"agent{i}@example.com",
                    password="password123",
                    role=AgentRole.SENIOR
                )
                agents.append(agent)
            
            customers = []
            for i in range(1000):
                customer = agent_manager.create_customer(
                    name=f"Customer {i}",
                    email=f"customer{i}@example.com",
                    phone=f"123-456-{i:04d}",
                    tier=CustomerTier.BASIC,
                    agent_id=agents[i % 100].id
                )
                customers.append(customer)
            
            end_time = time.time()
            creation_time = end_time - start_time
            
            # Should complete within reasonable time
            assert creation_time < 10.0  # 10 seconds max
            
            # Test data loading performance
            start_time = time.time()
            agent_manager.load_data()
            end_time = time.time()
            load_time = end_time - start_time
            
            # Should load quickly
            assert load_time < 5.0  # 5 seconds max
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
