#!/usr/bin/env python3
"""
Agent Routes for AI Stock Trading Platform
API endpoints for agent operations, customer management, and trading suggestions
"""

import os
import sys
import asyncio
from flask import Blueprint, request, jsonify
from functools import wraps

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.auth_middleware import require_auth, require_role
from models.user import UserRole
from services.agent_service import agent_service
from services.trading_suggestion_service import trading_suggestion_service

agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

def async_route(f):
    """Decorator to handle async functions in Flask routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return decorated_function

@agent_bp.route('/dashboard', methods=['GET'])
@require_auth
@require_role(UserRole.AGENT)
def get_agent_dashboard():
    """Get agent dashboard data"""
    try:
        agent_id = request.user['id']
        dashboard_data = agent_service.get_agent_dashboard_data(agent_id)
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers', methods=['GET'])
@require_auth
@require_role(UserRole.AGENT)
def get_agent_customers():
    """Get all customers assigned to the agent"""
    try:
        agent_id = request.user['id']
        include_portfolios = request.args.get('include_portfolios', 'true').lower() == 'true'

        customers = agent_service.get_agent_customers(agent_id, include_portfolios)
        return jsonify({'customers': customers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers', methods=['POST'])
@require_auth
@require_role(UserRole.AGENT)
def create_customer():
    """Create a new customer and assign to agent"""
    try:
        agent_id = request.user['id']
        customer_data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'initial_capital']
        missing_fields = [field for field in required_fields if field not in customer_data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        result = agent_service.create_customer(agent_id, customer_data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/portfolios/<int:portfolio_id>', methods=['GET'])
@require_auth
@require_role(UserRole.AGENT)
def get_portfolio_details(portfolio_id):
    """Get detailed portfolio information"""
    try:
        agent_id = request.user['id']
        portfolio_data = agent_service.get_portfolio_details(portfolio_id, agent_id)
        return jsonify(portfolio_data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/portfolios/<int:portfolio_id>/suggestions/generate', methods=['POST'])
@require_auth
@require_role(UserRole.AGENT)
@async_route
async def generate_portfolio_suggestions(portfolio_id):
    """Generate AI trading suggestions for a portfolio"""
    try:
        agent_id = request.user['id']

        # Verify agent has access to this portfolio
        portfolio_data = agent_service.get_portfolio_details(portfolio_id, agent_id)

        # Generate suggestions
        suggestions = await trading_suggestion_service.generate_suggestions_for_portfolio(portfolio_id)

        return jsonify({
            'success': True,
            'suggestions_generated': len(suggestions),
            'suggestions': suggestions
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/suggestions/<int:suggestion_id>/approve', methods=['POST'])
@require_auth
@require_role(UserRole.AGENT)
def approve_suggestion(suggestion_id):
    """Approve a trading suggestion and execute the trade"""
    try:
        agent_id = request.user['id']
        data = request.get_json() or {}
        notes = data.get('notes', '')

        result = agent_service.approve_suggestion(suggestion_id, agent_id, notes)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/suggestions/<int:suggestion_id>/reject', methods=['POST'])
@require_auth
@require_role(UserRole.AGENT)
def reject_suggestion(suggestion_id):
    """Reject a trading suggestion"""
    try:
        agent_id = request.user['id']
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')

        result = agent_service.reject_suggestion(suggestion_id, agent_id, reason)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers/<int:customer_id>/interactions', methods=['GET'])
@require_auth
@require_role(UserRole.AGENT)
def get_customer_interactions(customer_id):
    """Get interaction history with a customer"""
    try:
        # This would be implemented in the agent_service
        # For now, return placeholder
        return jsonify({
            'interactions': [],
            'message': 'Feature coming soon'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/customers/<int:customer_id>/interactions', methods=['POST'])
@require_auth
@require_role(UserRole.AGENT)
def create_customer_interaction(customer_id):
    """Create a new customer interaction record"""
    try:
        # This would be implemented in the agent_service
        # For now, return placeholder
        return jsonify({
            'success': True,
            'message': 'Feature coming soon'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/performance', methods=['GET'])
@require_auth
@require_role(UserRole.AGENT)
def get_agent_performance():
    """Get agent performance metrics"""
    try:
        agent_id = request.user['id']
        period = request.args.get('period', '30')  # days

        # This would be implemented to get detailed performance metrics
        # For now, return basic data from dashboard
        dashboard_data = agent_service.get_agent_dashboard_data(agent_id)

        return jsonify({
            'performance': dashboard_data.get('metrics', {}),
            'period_days': period
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/suggestions/pending', methods=['GET'])
@require_auth
@require_role(UserRole.AGENT)
def get_pending_suggestions():
    """Get all pending suggestions for the agent"""
    try:
        agent_id = request.user['id']

        # This would query the database for pending suggestions
        from database import db_manager
        from models.agent_models import TradingSuggestion, SuggestionStatus

        with db_manager.get_session() as session:
            suggestions = session.query(TradingSuggestion).filter_by(
                agent_id=agent_id,
                status=SuggestionStatus.PENDING
            ).order_by(TradingSuggestion.priority.desc(), TradingSuggestion.created_at.desc()).all()

            suggestions_data = []
            for s in suggestions:
                suggestions_data.append({
                    'id': s.id,
                    'symbol': s.symbol,
                    'suggestion_type': s.suggestion_type.value,
                    'suggested_quantity': s.suggested_quantity,
                    'suggested_price': s.suggested_price,
                    'current_price': s.current_price,
                    'ai_confidence': s.ai_confidence,
                    'predicted_return': s.predicted_return,
                    'risk_score': s.risk_score,
                    'reasoning': s.reasoning,
                    'priority': s.priority,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                    'valid_until': s.valid_until.isoformat() if s.valid_until else None,
                    'portfolio_id': s.portfolio_id
                })

        return jsonify({'suggestions': suggestions_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agent_bp.route('/suggestions/batch-process', methods=['POST'])
@require_auth
@require_role(UserRole.AGENT)
def batch_process_suggestions():
    """Process multiple suggestions at once"""
    try:
        agent_id = request.user['id']
        data = request.get_json()

        if not data or 'suggestions' not in data:
            return jsonify({'error': 'Missing suggestions data'}), 400

        results = []
        for suggestion_data in data['suggestions']:
            suggestion_id = suggestion_data.get('id')
            action = suggestion_data.get('action')  # 'approve' or 'reject'
            notes = suggestion_data.get('notes', '')

            try:
                if action == 'approve':
                    result = agent_service.approve_suggestion(suggestion_id, agent_id, notes)
                elif action == 'reject':
                    result = agent_service.reject_suggestion(suggestion_id, agent_id, notes)
                else:
                    result = {'success': False, 'error': 'Invalid action'}

                results.append({
                    'suggestion_id': suggestion_id,
                    'action': action,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'suggestion_id': suggestion_id,
                    'action': action,
                    'result': {'success': False, 'error': str(e)}
                })

        return jsonify({
            'success': True,
            'processed': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@agent_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@agent_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access denied'}), 403

@agent_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500