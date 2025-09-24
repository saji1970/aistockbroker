"""
Agent Management API Routes
Handles agent authentication, customer management, and trade suggestions
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from functools import wraps
from typing import Dict, List, Optional

from agent_manager import agent_manager, AgentRole, CustomerTier, TradeSuggestion
from ai_suggestion_engine import ai_suggestion_engine, AISuggestion
from shadow_trading_bot import ShadowTradingBot

logger = logging.getLogger(__name__)

# Create blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

def require_auth(f):
    """Decorator to require agent authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            
            # For now, use simple token validation
            # In production, use JWT tokens
            agent_id = session.get('agent_id')
            if not agent_id or agent_id not in agent_manager.agents:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add agent to request context
            request.agent = agent_manager.agents[agent_id]
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

@agent_bp.route('/auth/login', methods=['POST'])
def login():
    """Agent login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Authenticate agent
        agent = agent_manager.authenticate_agent(email, password)
        if not agent:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create session
        session['agent_id'] = agent.id
        session['agent_email'] = agent.email
        
        return jsonify({
            'success': True,
            'agent': {
                'id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'role': agent.role.value,
                'customers_count': len(agent.customers)
            },
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Agent logout endpoint"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout successful'}), 200
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get agent profile"""
    try:
        agent = request.agent
        stats = agent_manager.get_agent_stats(agent.id)
        
        return jsonify({
            'agent': {
                'id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'role': agent.role.value,
                'created_at': agent.created_at.isoformat(),
                'last_login': agent.last_login.isoformat() if agent.last_login else None,
                'is_active': agent.is_active
            },
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers', methods=['GET'])
@require_auth
def get_customers():
    """Get agent's customers"""
    try:
        agent = request.agent
        customers = agent_manager.get_agent_customers(agent.id)
        
        customer_list = []
        for customer in customers:
            customer_list.append({
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'tier': customer.tier.value,
                'risk_tolerance': customer.risk_tolerance,
                'investment_goals': customer.investment_goals,
                'portfolio_id': customer.portfolio_id,
                'created_at': customer.created_at.isoformat(),
                'last_contact': customer.last_contact.isoformat() if customer.last_contact else None,
                'is_active': customer.is_active
            })
        
        return jsonify({
            'customers': customer_list,
            'total': len(customer_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting customers: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers', methods=['POST'])
@require_auth
def create_customer():
    """Create new customer"""
    try:
        agent = request.agent
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'tier']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate tier
        try:
            tier = CustomerTier(data['tier'])
        except ValueError:
            return jsonify({'error': 'Invalid customer tier'}), 400
        
        # Create customer
        customer = agent_manager.create_customer(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            tier=tier,
            agent_id=agent.id,
            risk_tolerance=data.get('risk_tolerance', 'medium')
        )
        
        return jsonify({
            'success': True,
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'tier': customer.tier.value,
                'risk_tolerance': customer.risk_tolerance,
                'portfolio_id': customer.portfolio_id,
                'created_at': customer.created_at.isoformat()
            },
            'message': 'Customer created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers/<customer_id>', methods=['GET'])
@require_auth
def get_customer(customer_id):
    """Get specific customer details"""
    try:
        agent = request.agent
        
        # Check if agent has access to this customer
        agent_customers = [c.id for c in agent_manager.get_agent_customers(agent.id)]
        if customer_id not in agent_customers:
            return jsonify({'error': 'Customer not found or access denied'}), 404
        
        customer = agent_manager.customers.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'tier': customer.tier.value,
                'risk_tolerance': customer.risk_tolerance,
                'investment_goals': customer.investment_goals,
                'portfolio_id': customer.portfolio_id,
                'created_at': customer.created_at.isoformat(),
                'last_contact': customer.last_contact.isoformat() if customer.last_contact else None,
                'is_active': customer.is_active
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting customer: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/suggestions', methods=['GET'])
@require_auth
def get_suggestions():
    """Get pending trade suggestions for agent's customers"""
    try:
        agent = request.agent
        suggestions = agent_manager.get_pending_suggestions(agent.id)
        
        suggestion_list = []
        for suggestion in suggestions:
            suggestion_list.append({
                'id': suggestion.id,
                'customer_id': suggestion.customer_id,
                'symbol': suggestion.symbol,
                'action': suggestion.action,
                'quantity': suggestion.quantity,
                'price': suggestion.price,
                'confidence': suggestion.confidence,
                'reasoning': suggestion.reasoning,
                'ai_model': suggestion.ai_model,
                'created_at': suggestion.created_at.isoformat(),
                'expires_at': suggestion.expires_at.isoformat(),
                'status': suggestion.status,
                'agent_notes': suggestion.agent_notes
            })
        
        return jsonify({
            'suggestions': suggestion_list,
            'total': len(suggestion_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/suggestions/<suggestion_id>/decision', methods=['POST'])
@require_auth
def make_decision(suggestion_id):
    """Agent makes decision on trade suggestion"""
    try:
        agent = request.agent
        data = request.get_json()
        
        decision = data.get('decision')
        if decision not in ['accept', 'reject', 'modify']:
            return jsonify({'error': 'Invalid decision. Must be accept, reject, or modify'}), 400
        
        # Make decision
        decision_obj = agent_manager.make_agent_decision(
            suggestion_id=suggestion_id,
            agent_id=agent.id,
            decision=decision,
            modified_quantity=data.get('modified_quantity'),
            modified_price=data.get('modified_price'),
            reasoning=data.get('reasoning', '')
        )
        
        return jsonify({
            'success': True,
            'decision': {
                'suggestion_id': decision_obj.suggestion_id,
                'agent_id': decision_obj.agent_id,
                'decision': decision_obj.decision,
                'modified_quantity': decision_obj.modified_quantity,
                'modified_price': decision_obj.modified_price,
                'reasoning': decision_obj.reasoning,
                'created_at': decision_obj.created_at.isoformat()
            },
            'message': f'Decision {decision} recorded successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error making decision: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/suggestions/generate', methods=['POST'])
@require_auth
def generate_suggestions():
    """Generate AI suggestions for a customer"""
    try:
        agent = request.agent
        data = request.get_json()
        
        customer_id = data.get('customer_id')
        if not customer_id:
            return jsonify({'error': 'customer_id is required'}), 400
        
        # Check if agent has access to this customer
        agent_customers = [c.id for c in agent_manager.get_agent_customers(agent.id)]
        if customer_id not in agent_customers:
            return jsonify({'error': 'Customer not found or access denied'}), 404
        
        # Generate suggestions
        max_suggestions = data.get('max_suggestions', 5)
        suggestions = await ai_suggestion_engine.generate_suggestions_for_customer(
            customer_id, max_suggestions
        )
        
        suggestion_list = []
        for suggestion in suggestions:
            suggestion_list.append({
                'symbol': suggestion.symbol,
                'action': suggestion.action,
                'quantity': suggestion.quantity,
                'price': suggestion.price,
                'confidence': suggestion.confidence,
                'reasoning': suggestion.reasoning,
                'risk_level': suggestion.risk_level,
                'expected_return': suggestion.expected_return,
                'time_horizon': suggestion.time_horizon,
                'ai_model': suggestion.ai_model,
                'technical_analysis': suggestion.technical_analysis,
                'fundamental_analysis': suggestion.fundamental_analysis,
                'market_conditions': suggestion.market_conditions
            })
        
        return jsonify({
            'success': True,
            'suggestions': suggestion_list,
            'total': len(suggestion_list),
            'message': f'Generated {len(suggestion_list)} suggestions'
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/learning/insights', methods=['GET'])
@require_auth
def get_learning_insights():
    """Get learning insights from agent decisions"""
    try:
        insights = agent_manager.get_learning_insights()
        return jsonify(insights), 200
        
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/learning/update-weights', methods=['POST'])
@require_auth
def update_learning_weights():
    """Update AI learning weights based on agent feedback"""
    try:
        agent = request.agent
        data = request.get_json()
        
        # Update learning weights
        ai_suggestion_engine.update_learning_weights(data)
        
        return jsonify({
            'success': True,
            'message': 'Learning weights updated successfully',
            'weights': ai_suggestion_engine.learning_weights
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating learning weights: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """Get agent dashboard data"""
    try:
        agent = request.agent
        
        # Get basic stats
        stats = agent_manager.get_agent_stats(agent.id)
        
        # Get recent suggestions
        recent_suggestions = agent_manager.get_pending_suggestions(agent.id)[:5]
        
        # Get learning insights
        learning_insights = agent_manager.get_learning_insights()
        
        dashboard_data = {
            'agent': {
                'id': agent.id,
                'name': agent.name,
                'role': agent.role.value
            },
            'stats': stats,
            'recent_suggestions': [
                {
                    'id': s.id,
                    'symbol': s.symbol,
                    'action': s.action,
                    'confidence': s.confidence,
                    'created_at': s.created_at.isoformat()
                } for s in recent_suggestions
            ],
            'learning_insights': learning_insights,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers/<customer_id>/portfolio', methods=['GET'])
@require_auth
def get_customer_portfolio(customer_id):
    """Get customer portfolio data"""
    try:
        agent = request.agent
        
        # Check if agent has access to this customer
        agent_customers = [c.id for c in agent_manager.get_agent_customers(agent.id)]
        if customer_id not in agent_customers:
            return jsonify({'error': 'Customer not found or access denied'}), 404
        
        customer = agent_manager.customers.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get portfolio data (this would integrate with actual portfolio system)
        portfolio_data = {
            'customer_id': customer_id,
            'portfolio_id': customer.portfolio_id,
            'total_value': 100000,  # Mock data
            'cash': 20000,
            'positions': {},
            'performance': {
                'total_return': 0.0,
                'daily_return': 0.0,
                'sharpe_ratio': 0.0
            },
            'risk_metrics': {
                'risk_tolerance': customer.risk_tolerance,
                'volatility': 0.15,
                'max_drawdown': 0.05
            }
        }
        
        return jsonify(portfolio_data), 200
        
    except Exception as e:
        logger.error(f"Error getting customer portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'agent_management'
    }), 200
