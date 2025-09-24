#!/usr/bin/env python3
"""
Agent Service for AI Stock Trading Platform
Handles agent operations, customer management, and portfolio oversight
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func, desc

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_manager
from models.user import User, UserRole, UserStatus
from models.agent_models import (
    CustomerPortfolio, PortfolioHolding, TradingSuggestion, TradeExecution,
    AgentDecisionFeedback, CustomerInteraction, AgentPerformanceMetrics,
    CustomerPortfolioStatus, TradingSuggestionType, SuggestionStatus
)

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        pass

    def create_customer(self, agent_id: int, customer_data: Dict) -> Dict:
        """Create a new customer and assign to agent"""
        with db_manager.get_session() as session:
            try:
                # Verify agent exists and has agent role
                agent = session.query(User).filter_by(id=agent_id, role=UserRole.AGENT).first()
                if not agent:
                    raise ValueError("Agent not found or invalid role")

                # Check if customer email already exists
                existing_customer = session.query(User).filter_by(email=customer_data['email'].lower()).first()
                if existing_customer:
                    raise ValueError("Customer with this email already exists")

                # Create customer user
                customer = User(
                    email=customer_data['email'],
                    username=customer_data.get('username', customer_data['email'].split('@')[0]),
                    password=customer_data['password'],
                    first_name=customer_data.get('first_name'),
                    last_name=customer_data.get('last_name'),
                    role=UserRole.CUSTOMER,
                    status=UserStatus.ACTIVE,
                    assigned_agent_id=agent_id,
                    trading_experience=customer_data.get('trading_experience', 'beginner'),
                    risk_tolerance=customer_data.get('risk_tolerance', 'moderate'),
                    investment_goals=customer_data.get('investment_goals'),
                    initial_capital=float(customer_data.get('initial_capital', 0)),
                    email_verified_at=datetime.utcnow()
                )

                session.add(customer)
                session.flush()

                # Create initial portfolio
                portfolio = CustomerPortfolio(
                    customer_id=customer.id,
                    agent_id=agent_id,
                    portfolio_name=f"{customer.first_name or customer.username}'s Portfolio",
                    initial_capital=customer.initial_capital,
                    current_cash=customer.initial_capital,
                    total_value=customer.initial_capital,
                    risk_level=customer.risk_tolerance
                )

                session.add(portfolio)
                session.flush()

                # Log initial interaction
                interaction = CustomerInteraction(
                    agent_id=agent_id,
                    customer_id=customer.id,
                    interaction_type="onboarding",
                    subject="Customer account created and portfolio initialized",
                    notes=f"Initial capital: ${customer.initial_capital}, Risk tolerance: {customer.risk_tolerance}"
                )
                session.add(interaction)

                logger.info(f"Customer {customer.email} created and assigned to agent {agent.username}")

                return {
                    'success': True,
                    'customer': customer.to_dict(),
                    'portfolio': {
                        'id': portfolio.id,
                        'portfolio_name': portfolio.portfolio_name,
                        'initial_capital': portfolio.initial_capital,
                        'current_cash': portfolio.current_cash,
                        'total_value': portfolio.total_value
                    }
                }

            except Exception as e:
                logger.error(f"Error creating customer: {e}")
                raise

    def get_agent_customers(self, agent_id: int, include_portfolios: bool = True) -> List[Dict]:
        """Get all customers assigned to an agent"""
        with db_manager.get_session() as session:
            try:
                query = session.query(User).filter_by(assigned_agent_id=agent_id, role=UserRole.CUSTOMER)
                customers = query.all()

                result = []
                for customer in customers:
                    customer_dict = customer.to_dict()

                    if include_portfolios:
                        portfolios = session.query(CustomerPortfolio).filter_by(
                            customer_id=customer.id,
                            agent_id=agent_id
                        ).all()

                        customer_dict['portfolios'] = [
                            {
                                'id': p.id,
                                'portfolio_name': p.portfolio_name,
                                'initial_capital': p.initial_capital,
                                'current_cash': p.current_cash,
                                'total_value': p.total_value,
                                'total_return_percent': p.total_return_percent,
                                'status': p.status.value,
                                'auto_trading_enabled': p.auto_trading_enabled,
                                'created_at': p.created_at.isoformat() if p.created_at else None
                            }
                            for p in portfolios
                        ]

                    result.append(customer_dict)

                return result

            except Exception as e:
                logger.error(f"Error getting agent customers: {e}")
                raise

    def get_portfolio_details(self, portfolio_id: int, agent_id: int) -> Dict:
        """Get detailed portfolio information with holdings"""
        with db_manager.get_session() as session:
            try:
                # Verify agent has access to this portfolio
                portfolio = session.query(CustomerPortfolio).filter_by(
                    id=portfolio_id,
                    agent_id=agent_id
                ).first()

                if not portfolio:
                    raise ValueError("Portfolio not found or access denied")

                # Get holdings
                holdings = session.query(PortfolioHolding).filter_by(
                    portfolio_id=portfolio_id
                ).all()

                # Get recent trades
                recent_trades = session.query(TradeExecution).filter_by(
                    portfolio_id=portfolio_id
                ).order_by(desc(TradeExecution.created_at)).limit(10).all()

                # Get pending suggestions
                pending_suggestions = session.query(TradingSuggestion).filter_by(
                    portfolio_id=portfolio_id,
                    status=SuggestionStatus.PENDING
                ).order_by(desc(TradingSuggestion.created_at)).all()

                return {
                    'portfolio': {
                        'id': portfolio.id,
                        'portfolio_name': portfolio.portfolio_name,
                        'customer_name': f"{portfolio.customer.first_name} {portfolio.customer.last_name}",
                        'customer_email': portfolio.customer.email,
                        'initial_capital': portfolio.initial_capital,
                        'current_cash': portfolio.current_cash,
                        'total_value': portfolio.total_value,
                        'invested_amount': portfolio.invested_amount,
                        'unrealized_pnl': portfolio.unrealized_pnl,
                        'realized_pnl': portfolio.realized_pnl,
                        'total_return': portfolio.total_return,
                        'total_return_percent': portfolio.total_return_percent,
                        'risk_level': portfolio.risk_level,
                        'auto_trading_enabled': portfolio.auto_trading_enabled,
                        'status': portfolio.status.value
                    },
                    'holdings': [
                        {
                            'id': h.id,
                            'symbol': h.symbol,
                            'company_name': h.company_name,
                            'quantity': h.quantity,
                            'average_price': h.average_price,
                            'current_price': h.current_price,
                            'market_value': h.market_value,
                            'unrealized_pnl': h.unrealized_pnl,
                            'unrealized_pnl_percent': h.unrealized_pnl_percent,
                            'sector': h.sector,
                            'stop_loss_price': h.stop_loss_price,
                            'take_profit_price': h.take_profit_price
                        }
                        for h in holdings
                    ],
                    'recent_trades': [
                        {
                            'id': t.id,
                            'symbol': t.symbol,
                            'trade_type': t.trade_type.value,
                            'quantity': t.quantity,
                            'executed_price': t.executed_price,
                            'total_amount': t.total_amount,
                            'status': t.status.value,
                            'executed_at': t.executed_at.isoformat() if t.executed_at else None
                        }
                        for t in recent_trades
                    ],
                    'pending_suggestions': [
                        {
                            'id': s.id,
                            'symbol': s.symbol,
                            'suggestion_type': s.suggestion_type.value,
                            'suggested_quantity': s.suggested_quantity,
                            'suggested_price': s.suggested_price,
                            'ai_confidence': s.ai_confidence,
                            'predicted_return': s.predicted_return,
                            'reasoning': s.reasoning,
                            'created_at': s.created_at.isoformat() if s.created_at else None,
                            'valid_until': s.valid_until.isoformat() if s.valid_until else None
                        }
                        for s in pending_suggestions
                    ]
                }

            except Exception as e:
                logger.error(f"Error getting portfolio details: {e}")
                raise

    def approve_suggestion(self, suggestion_id: int, agent_id: int, notes: str = None) -> Dict:
        """Approve a trading suggestion and execute the trade"""
        with db_manager.get_session() as session:
            try:
                # Get suggestion and verify agent access
                suggestion = session.query(TradingSuggestion).filter_by(
                    id=suggestion_id,
                    agent_id=agent_id,
                    status=SuggestionStatus.PENDING
                ).first()

                if not suggestion:
                    raise ValueError("Suggestion not found or already processed")

                # Update suggestion status
                suggestion.status = SuggestionStatus.APPROVED
                suggestion.agent_notes = notes
                suggestion.reviewed_at = datetime.utcnow()

                # Create trade execution record
                trade = TradeExecution(
                    portfolio_id=suggestion.portfolio_id,
                    suggestion_id=suggestion.id,
                    agent_id=agent_id,
                    symbol=suggestion.symbol,
                    trade_type=suggestion.suggestion_type,
                    quantity=suggestion.suggested_quantity,
                    executed_price=suggestion.suggested_price,
                    total_amount=suggestion.suggested_quantity * suggestion.suggested_price,
                    expected_return=suggestion.predicted_return,
                    execution_method="agent_approved"
                )

                session.add(trade)
                session.flush()

                # Create agent decision feedback for learning
                feedback = AgentDecisionFeedback(
                    agent_id=agent_id,
                    suggestion_id=suggestion.id,
                    agent_decision="approved",
                    decision_reasoning=notes,
                    confidence_in_ai=suggestion.ai_confidence
                )

                session.add(feedback)

                # Update portfolio holdings (simplified - in real system would integrate with broker)
                self._update_portfolio_after_trade(session, trade)

                logger.info(f"Agent {agent_id} approved suggestion {suggestion_id} for {suggestion.symbol}")

                return {
                    'success': True,
                    'message': 'Suggestion approved and trade executed',
                    'trade_id': trade.id,
                    'symbol': trade.symbol,
                    'quantity': trade.quantity,
                    'price': trade.executed_price
                }

            except Exception as e:
                logger.error(f"Error approving suggestion: {e}")
                raise

    def reject_suggestion(self, suggestion_id: int, agent_id: int, reason: str) -> Dict:
        """Reject a trading suggestion"""
        with db_manager.get_session() as session:
            try:
                suggestion = session.query(TradingSuggestion).filter_by(
                    id=suggestion_id,
                    agent_id=agent_id,
                    status=SuggestionStatus.PENDING
                ).first()

                if not suggestion:
                    raise ValueError("Suggestion not found or already processed")

                suggestion.status = SuggestionStatus.REJECTED
                suggestion.agent_notes = reason
                suggestion.reviewed_at = datetime.utcnow()

                # Create agent decision feedback for learning
                feedback = AgentDecisionFeedback(
                    agent_id=agent_id,
                    suggestion_id=suggestion.id,
                    agent_decision="rejected",
                    decision_reasoning=reason,
                    confidence_in_ai=suggestion.ai_confidence
                )

                session.add(feedback)

                logger.info(f"Agent {agent_id} rejected suggestion {suggestion_id} for {suggestion.symbol}")

                return {
                    'success': True,
                    'message': 'Suggestion rejected',
                    'reason': reason
                }

            except Exception as e:
                logger.error(f"Error rejecting suggestion: {e}")
                raise

    def get_agent_dashboard_data(self, agent_id: int) -> Dict:
        """Get comprehensive dashboard data for agent"""
        with db_manager.get_session() as session:
            try:
                # Get agent info
                agent = session.query(User).filter_by(id=agent_id, role=UserRole.AGENT).first()
                if not agent:
                    raise ValueError("Agent not found")

                # Customer metrics
                total_customers = session.query(User).filter_by(
                    assigned_agent_id=agent_id,
                    role=UserRole.CUSTOMER
                ).count()

                active_portfolios = session.query(CustomerPortfolio).filter_by(
                    agent_id=agent_id,
                    status=CustomerPortfolioStatus.ACTIVE
                ).count()

                # Portfolio performance
                portfolio_metrics = session.query(
                    func.sum(CustomerPortfolio.total_value).label('total_aum'),
                    func.sum(CustomerPortfolio.total_return).label('total_returns'),
                    func.avg(CustomerPortfolio.total_return_percent).label('avg_return_percent')
                ).filter_by(agent_id=agent_id).first()

                # Recent suggestions
                pending_suggestions = session.query(TradingSuggestion).filter_by(
                    agent_id=agent_id,
                    status=SuggestionStatus.PENDING
                ).count()

                # Recent trades
                recent_trades = session.query(TradeExecution).filter_by(
                    agent_id=agent_id
                ).filter(
                    TradeExecution.created_at >= datetime.utcnow() - timedelta(days=30)
                ).count()

                # Commission earned (simplified calculation)
                commission_earned = session.query(
                    func.sum(TradeExecution.commission)
                ).filter_by(agent_id=agent_id).scalar() or 0

                return {
                    'agent': agent.to_dict(),
                    'metrics': {
                        'total_customers': total_customers,
                        'active_portfolios': active_portfolios,
                        'total_aum': float(portfolio_metrics.total_aum or 0),
                        'total_returns': float(portfolio_metrics.total_returns or 0),
                        'avg_return_percent': float(portfolio_metrics.avg_return_percent or 0),
                        'pending_suggestions': pending_suggestions,
                        'recent_trades_30d': recent_trades,
                        'commission_earned': float(commission_earned)
                    }
                }

            except Exception as e:
                logger.error(f"Error getting agent dashboard data: {e}")
                raise

    def _update_portfolio_after_trade(self, session: Session, trade: TradeExecution):
        """Update portfolio holdings after a trade (simplified implementation)"""
        try:
            portfolio = session.query(CustomerPortfolio).get(trade.portfolio_id)

            if trade.trade_type == TradingSuggestionType.BUY:
                # Check if holding exists
                holding = session.query(PortfolioHolding).filter_by(
                    portfolio_id=trade.portfolio_id,
                    symbol=trade.symbol
                ).first()

                if holding:
                    # Update existing holding
                    total_cost = (holding.quantity * holding.average_price) + trade.total_amount
                    holding.quantity += trade.quantity
                    holding.average_price = total_cost / holding.quantity
                else:
                    # Create new holding
                    holding = PortfolioHolding(
                        portfolio_id=trade.portfolio_id,
                        symbol=trade.symbol,
                        quantity=trade.quantity,
                        average_price=trade.executed_price,
                        current_price=trade.executed_price
                    )
                    session.add(holding)

                # Update portfolio cash
                portfolio.current_cash -= trade.total_amount
                portfolio.invested_amount += trade.total_amount

            elif trade.trade_type == TradingSuggestionType.SELL:
                # Find and update holding
                holding = session.query(PortfolioHolding).filter_by(
                    portfolio_id=trade.portfolio_id,
                    symbol=trade.symbol
                ).first()

                if holding and holding.quantity >= trade.quantity:
                    # Calculate realized P&L
                    realized_pnl = (trade.executed_price - holding.average_price) * trade.quantity
                    holding.realized_pnl += realized_pnl
                    holding.quantity -= trade.quantity

                    # Update portfolio
                    portfolio.current_cash += trade.total_amount
                    portfolio.invested_amount -= (holding.average_price * trade.quantity)
                    portfolio.realized_pnl += realized_pnl

                    # Remove holding if fully sold
                    if holding.quantity <= 0:
                        session.delete(holding)

            # Update portfolio total value
            portfolio.total_value = portfolio.current_cash + portfolio.invested_amount
            trade.status = TradeExecution.TradeExecutionStatus.FILLED
            trade.executed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error updating portfolio after trade: {e}")
            raise

# Global agent service instance
agent_service = AgentService()