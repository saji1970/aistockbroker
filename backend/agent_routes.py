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
    """Decorator to require agent authentication using unified auth system"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from middleware.auth_middleware import extract_token_from_request, decode_jwt_token
        from database import db_manager
        from models.user import User, UserRole
        
        try:
            # Extract token from request
            token = extract_token_from_request()
            if not token:
                return jsonify({'error': 'Authorization token required'}), 401
            
            # Decode JWT token
            payload = decode_jwt_token(token)
            user_id = payload.get('user_id')
            
            if not user_id:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Get user from database
            with db_manager.get_session() as session:
                user = session.query(User).get(user_id)
                if not user or not user.is_active():
                    return jsonify({'error': 'User not found or inactive'}), 401
                
                # Check if user is an agent
                if user.role != UserRole.AGENT:
                    return jsonify({'error': 'Access denied. Agent role required.'}), 403
                
                # Add user to request context
                request.user = user.to_dict()
                return f(*args, **kwargs)
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function

# Note: Agent authentication is now handled by the unified auth system at /api/auth/login
# Agents should use the same login endpoint as other users, with role-based access control

@agent_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get agent profile"""
    try:
        user = request.user
        
        # Get agent stats from the agent manager
        stats = agent_manager.get_agent_stats(user['id'])
        
        return jsonify({
            'agent': {
                'id': user['id'],
                'name': f"{user['first_name']} {user['last_name']}".strip() or user['username'],
                'email': user['email'],
                'role': user['role'],
                'created_at': user['created_at'],
                'last_login': user['last_login'],
                'is_active': user['status'] == 'active'
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
        user = request.user
        customers = agent_manager.get_agent_customers(user['id'])
        
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
        user = request.user
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
            agent_id=user['id'],
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
        user = request.user
        
        # Check if agent has access to this customer
        agent_customers = [c.id for c in agent_manager.get_agent_customers(user['id'])]
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
        user = request.user
        suggestions = agent_manager.get_pending_suggestions(user['id'])
        
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
        user = request.user
        data = request.get_json()
        
        decision = data.get('decision')
        if decision not in ['accept', 'reject', 'modify']:
            return jsonify({'error': 'Invalid decision. Must be accept, reject, or modify'}), 400
        
        # Make decision
        decision_obj = agent_manager.make_agent_decision(
            suggestion_id=suggestion_id,
            agent_id=user['id'],
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
        user = request.user
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
        user = request.user
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
        user = request.user
        
        # Get basic stats
        stats = agent_manager.get_agent_stats(user['id'])
        
        # Get recent suggestions
        recent_suggestions = agent_manager.get_pending_suggestions(user['id'])[:5]
        
        # Get learning insights
        learning_insights = agent_manager.get_learning_insights()
        
        dashboard_data = {
            'agent': {
                'id': user['id'],
                'name': f"{user['first_name']} {user['last_name']}".strip() or user['username'],
                'role': user['role']
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
        user = request.user
        
        # Check if agent has access to this customer
        agent_customers = [c.id for c in agent_manager.get_agent_customers(user['id'])]
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
