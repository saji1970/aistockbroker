"""
Agent Management System
Handles agent authentication, customer management, and portfolio oversight
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib
import secrets

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Agent role levels"""
    JUNIOR = "junior"
    SENIOR = "senior"
    MANAGER = "manager"
    DIRECTOR = "director"

class CustomerTier(Enum):
    """Customer tier levels"""
    BASIC = "basic"
    PREMIUM = "premium"
    VIP = "vip"
    INSTITUTIONAL = "institutional"

@dataclass
class Agent:
    """Agent data structure"""
    id: str
    name: str
    email: str
    role: AgentRole
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    customers: List[str] = None  # Customer IDs assigned to this agent
    
    def __post_init__(self):
        if self.customers is None:
            self.customers = []

@dataclass
class Customer:
    """Customer data structure"""
    id: str
    name: str
    email: str
    phone: str
    tier: CustomerTier
    agent_id: str
    created_at: datetime
    risk_tolerance: str = "medium"
    investment_goals: List[str] = None
    portfolio_id: str = None
    is_active: bool = True
    last_contact: Optional[datetime] = None
    
    def __post_init__(self):
        if self.investment_goals is None:
            self.investment_goals = []

@dataclass
class TradeSuggestion:
    """Trade suggestion from AI system"""
    id: str
    customer_id: str
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    quantity: int
    price: float
    confidence: float
    reasoning: str
    ai_model: str
    created_at: datetime
    expires_at: datetime
    status: str = "pending"  # 'pending', 'accepted', 'rejected', 'expired'
    agent_notes: str = ""

@dataclass
class AgentDecision:
    """Agent decision on trade suggestion"""
    suggestion_id: str
    agent_id: str
    decision: str  # 'accept', 'reject', 'modify'
    modified_quantity: Optional[int] = None
    modified_price: Optional[float] = None
    reasoning: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class AgentManager:
    """Main agent management system"""
    
    def __init__(self, data_file: str = "agent_data.json"):
        self.data_file = data_file
        self.agents: Dict[str, Agent] = {}
        self.customers: Dict[str, Customer] = {}
        self.trade_suggestions: Dict[str, TradeSuggestion] = {}
        self.agent_decisions: Dict[str, AgentDecision] = {}
        self.learning_data: List[Dict] = []
        
        # Load existing data
        self.load_data()
        
        # Initialize with default admin agent if none exist
        if not self.agents:
            self.create_default_admin()
    
    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                # Load agents
                for agent_data in data.get('agents', []):
                    agent_data['role'] = AgentRole(agent_data['role'])
                    agent_data['created_at'] = datetime.fromisoformat(agent_data['created_at'])
                    if agent_data.get('last_login'):
                        agent_data['last_login'] = datetime.fromisoformat(agent_data['last_login'])
                    self.agents[agent_data['id']] = Agent(**agent_data)
                
                # Load customers
                for customer_data in data.get('customers', []):
                    customer_data['tier'] = CustomerTier(customer_data['tier'])
                    customer_data['created_at'] = datetime.fromisoformat(customer_data['created_at'])
                    if customer_data.get('last_contact'):
                        customer_data['last_contact'] = datetime.fromisoformat(customer_data['last_contact'])
                    self.customers[customer_data['id']] = Customer(**customer_data)
                
                # Load trade suggestions
                for suggestion_data in data.get('trade_suggestions', []):
                    suggestion_data['created_at'] = datetime.fromisoformat(suggestion_data['created_at'])
                    suggestion_data['expires_at'] = datetime.fromisoformat(suggestion_data['expires_at'])
                    self.trade_suggestions[suggestion_data['id']] = TradeSuggestion(**suggestion_data)
                
                # Load agent decisions
                for decision_data in data.get('agent_decisions', []):
                    decision_data['created_at'] = datetime.fromisoformat(decision_data['created_at'])
                    self.agent_decisions[decision_data['suggestion_id']] = AgentDecision(**decision_data)
                
                self.learning_data = data.get('learning_data', [])
                
                logger.info(f"Loaded {len(self.agents)} agents, {len(self.customers)} customers")
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            data = {
                'agents': [asdict(agent) for agent in self.agents.values()],
                'customers': [asdict(customer) for customer in self.customers.values()],
                'trade_suggestions': [asdict(suggestion) for suggestion in self.trade_suggestions.values()],
                'agent_decisions': [asdict(decision) for decision in self.agent_decisions.values()],
                'learning_data': self.learning_data
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def create_default_admin(self):
        """Create default admin agent"""
        admin_agent = Agent(
            id=str(uuid.uuid4()),
            name="Admin Agent",
            email="admin@aistockbroker.com",
            role=AgentRole.DIRECTOR,
            password_hash=self._hash_password("admin123"),
            created_at=datetime.now()
        )
        self.agents[admin_agent.id] = admin_agent
        self.save_data()
        logger.info("Created default admin agent")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_agent(self, email: str, password: str) -> Optional[Agent]:
        """Authenticate agent"""
        password_hash = self._hash_password(password)
        
        for agent in self.agents.values():
            if agent.email == email and agent.password_hash == password_hash and agent.is_active:
                agent.last_login = datetime.now()
                self.save_data()
                return agent
        return None
    
    def create_agent(self, name: str, email: str, password: str, role: AgentRole) -> Agent:
        """Create new agent"""
        # Check if email already exists
        for agent in self.agents.values():
            if agent.email == email:
                raise ValueError("Agent with this email already exists")
        
        agent = Agent(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            role=role,
            password_hash=self._hash_password(password),
            created_at=datetime.now()
        )
        
        self.agents[agent.id] = agent
        self.save_data()
        logger.info(f"Created new agent: {name} ({role.value})")
        return agent
    
    def create_customer(self, name: str, email: str, phone: str, tier: CustomerTier, 
                       agent_id: str, risk_tolerance: str = "medium") -> Customer:
        """Create new customer"""
        # Check if agent exists
        if agent_id not in self.agents:
            raise ValueError("Agent not found")
        
        # Check if email already exists
        for customer in self.customers.values():
            if customer.email == email:
                raise ValueError("Customer with this email already exists")
        
        customer = Customer(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            phone=phone,
            tier=tier,
            agent_id=agent_id,
            created_at=datetime.now(),
            risk_tolerance=risk_tolerance,
            portfolio_id=str(uuid.uuid4())
        )
        
        self.customers[customer.id] = customer
        
        # Add customer to agent's list
        if agent_id in self.agents:
            self.agents[agent_id].customers.append(customer.id)
        
        self.save_data()
        logger.info(f"Created new customer: {name} ({tier.value})")
        return customer
    
    def get_agent_customers(self, agent_id: str) -> List[Customer]:
        """Get all customers for an agent"""
        if agent_id not in self.agents:
            return []
        
        customers = []
        for customer_id in self.agents[agent_id].customers:
            if customer_id in self.customers:
                customers.append(self.customers[customer_id])
        
        return customers
    
    def create_trade_suggestion(self, customer_id: str, symbol: str, action: str, 
                               quantity: int, price: float, confidence: float, 
                               reasoning: str, ai_model: str) -> TradeSuggestion:
        """Create trade suggestion from AI system"""
        if customer_id not in self.customers:
            raise ValueError("Customer not found")
        
        suggestion = TradeSuggestion(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            confidence=confidence,
            reasoning=reasoning,
            ai_model=ai_model,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24)  # Expires in 24 hours
        )
        
        self.trade_suggestions[suggestion.id] = suggestion
        self.save_data()
        logger.info(f"Created trade suggestion for {symbol} - {action}")
        return suggestion
    
    def get_pending_suggestions(self, agent_id: str) -> List[TradeSuggestion]:
        """Get pending trade suggestions for agent's customers"""
        agent_customers = [c.id for c in self.get_agent_customers(agent_id)]
        
        pending_suggestions = []
        for suggestion in self.trade_suggestions.values():
            if (suggestion.customer_id in agent_customers and 
                suggestion.status == "pending" and 
                suggestion.expires_at > datetime.now()):
                pending_suggestions.append(suggestion)
        
        return sorted(pending_suggestions, key=lambda x: x.created_at, reverse=True)
    
    def make_agent_decision(self, suggestion_id: str, agent_id: str, decision: str,
                           modified_quantity: Optional[int] = None,
                           modified_price: Optional[float] = None,
                           reasoning: str = "") -> AgentDecision:
        """Agent makes decision on trade suggestion"""
        if suggestion_id not in self.trade_suggestions:
            raise ValueError("Trade suggestion not found")
        
        suggestion = self.trade_suggestions[suggestion_id]
        
        # Check if agent has access to this customer
        agent_customers = [c.id for c in self.get_agent_customers(agent_id)]
        if suggestion.customer_id not in agent_customers:
            raise ValueError("Agent does not have access to this customer")
        
        # Create decision
        decision_obj = AgentDecision(
            suggestion_id=suggestion_id,
            agent_id=agent_id,
            decision=decision,
            modified_quantity=modified_quantity,
            modified_price=modified_price,
            reasoning=reasoning
        )
        
        self.agent_decisions[suggestion_id] = decision_obj
        
        # Update suggestion status
        suggestion.status = decision
        if decision == "modify":
            if modified_quantity:
                suggestion.quantity = modified_quantity
            if modified_price:
                suggestion.price = modified_price
        
        # Add to learning data
        self.learning_data.append({
            'timestamp': datetime.now().isoformat(),
            'suggestion_id': suggestion_id,
            'customer_id': suggestion.customer_id,
            'agent_id': agent_id,
            'original_suggestion': asdict(suggestion),
            'agent_decision': asdict(decision_obj),
            'learning_type': 'agent_decision'
        })
        
        self.save_data()
        logger.info(f"Agent {agent_id} made decision: {decision} on suggestion {suggestion_id}")
        return decision_obj
    
    def get_learning_insights(self) -> Dict:
        """Get learning insights from agent decisions"""
        if not self.learning_data:
            return {"message": "No learning data available"}
        
        # Analyze agent decisions
        total_decisions = len(self.learning_data)
        accepted_decisions = sum(1 for d in self.learning_data if d.get('agent_decision', {}).get('decision') == 'accept')
        rejected_decisions = sum(1 for d in self.learning_data if d.get('agent_decision', {}).get('decision') == 'reject')
        modified_decisions = sum(1 for d in self.learning_data if d.get('agent_decision', {}).get('decision') == 'modify')
        
        # Calculate acceptance rate
        acceptance_rate = (accepted_decisions / total_decisions * 100) if total_decisions > 0 else 0
        
        # Get most common modifications
        modifications = []
        for data in self.learning_data:
            if data.get('agent_decision', {}).get('decision') == 'modify':
                modifications.append({
                    'symbol': data.get('original_suggestion', {}).get('symbol'),
                    'original_quantity': data.get('original_suggestion', {}).get('quantity'),
                    'modified_quantity': data.get('agent_decision', {}).get('modified_quantity'),
                    'original_price': data.get('original_suggestion', {}).get('price'),
                    'modified_price': data.get('agent_decision', {}).get('modified_price')
                })
        
        return {
            'total_decisions': total_decisions,
            'acceptance_rate': round(acceptance_rate, 2),
            'accepted_decisions': accepted_decisions,
            'rejected_decisions': rejected_decisions,
            'modified_decisions': modified_decisions,
            'modifications': modifications[-10:],  # Last 10 modifications
            'learning_insights': {
                'agent_preferences': self._analyze_agent_preferences(),
                'common_rejections': self._analyze_common_rejections(),
                'modification_patterns': self._analyze_modification_patterns()
            }
        }
    
    def _analyze_agent_preferences(self) -> Dict:
        """Analyze agent preferences from decisions"""
        # This would analyze patterns in agent decisions
        return {
            'preferred_symbols': [],
            'risk_tolerance_patterns': {},
            'timing_preferences': {}
        }
    
    def _analyze_common_rejections(self) -> List[Dict]:
        """Analyze common reasons for rejections"""
        rejections = []
        for data in self.learning_data:
            if data.get('agent_decision', {}).get('decision') == 'reject':
                rejections.append({
                    'symbol': data.get('original_suggestion', {}).get('symbol'),
                    'reasoning': data.get('agent_decision', {}).get('reasoning'),
                    'confidence': data.get('original_suggestion', {}).get('confidence')
                })
        return rejections[-5:]  # Last 5 rejections
    
    def _analyze_modification_patterns(self) -> Dict:
        """Analyze patterns in modifications"""
        return {
            'quantity_adjustments': {},
            'price_adjustments': {},
            'timing_preferences': {}
        }
    
    def get_agent_stats(self, agent_id: str) -> Dict:
        """Get statistics for an agent"""
        if agent_id not in self.agents:
            return {}
        
        agent_decisions = [d for d in self.learning_data if d.get('agent_id') == agent_id]
        
        return {
            'agent_id': agent_id,
            'total_customers': len(self.get_agent_customers(agent_id)),
            'total_decisions': len(agent_decisions),
            'acceptance_rate': self._calculate_agent_acceptance_rate(agent_id),
            'recent_activity': agent_decisions[-5:] if agent_decisions else []
        }
    
    def _calculate_agent_acceptance_rate(self, agent_id: str) -> float:
        """Calculate agent's acceptance rate"""
        agent_decisions = [d for d in self.learning_data if d.get('agent_id') == agent_id]
        if not agent_decisions:
            return 0.0
        
        accepted = sum(1 for d in agent_decisions if d.get('agent_decision', {}).get('decision') == 'accept')
        return (accepted / len(agent_decisions)) * 100

# Global instance
agent_manager = AgentManager()
