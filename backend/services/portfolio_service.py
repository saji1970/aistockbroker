#!/usr/bin/env python3
"""
Portfolio Service - Database-backed portfolio management
"""

from sqlalchemy.orm import Session
from models.portfolio import Portfolio, Holding, Transaction, TransactionType
from models.user import User
from database import db_manager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for managing user portfolios with database persistence"""

    @staticmethod
    def get_or_create_portfolio(user_id: int, initial_capital: float = 100000.0) -> Portfolio:
        """Get existing portfolio or create a new one for user"""
        try:
            with db_manager.get_session() as session:
                # Check if portfolio exists
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if portfolio:
                    return portfolio

                # Create new portfolio
                portfolio = Portfolio(
                    user_id=user_id,
                    name="My Portfolio",
                    initial_capital=initial_capital,
                    current_cash=initial_capital,
                    total_value=initial_capital
                )
                session.add(portfolio)
                session.commit()
                session.refresh(portfolio)

                logger.info(f"Created new portfolio for user {user_id}")
                return portfolio

        except Exception as e:
            logger.error(f"Error getting/creating portfolio: {e}")
            raise

    @staticmethod
    def get_portfolio_summary(user_id: int) -> dict:
        """Get portfolio summary with holdings and totals"""
        try:
            with db_manager.get_session() as session:
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if not portfolio:
                    # Create default portfolio within the same session
                    portfolio = Portfolio(
                        user_id=user_id,
                        name="My Portfolio",
                        initial_capital=100000.0,
                        current_cash=100000.0,
                        total_value=100000.0
                    )
                    session.add(portfolio)
                    session.commit()
                    session.refresh(portfolio)
                    logger.info(f"Created new portfolio for user {user_id}")

                # Get all holdings
                holdings = session.query(Holding).filter_by(portfolio_id=portfolio.id).all()

                holdings_data = []
                total_holdings_value = 0.0

                for holding in holdings:
                    if holding.quantity > 0:
                        value = holding.quantity * holding.current_price
                        total_holdings_value += value

                        holdings_data.append({
                            'symbol': holding.symbol,
                            'quantity': holding.quantity,
                            'avg_cost': holding.avg_cost,
                            'current_price': holding.current_price,
                            'value': value,
                            'profit_loss': (holding.current_price - holding.avg_cost) * holding.quantity,
                            'profit_loss_pct': ((holding.current_price / holding.avg_cost) - 1) * 100 if holding.avg_cost > 0 else 0
                        })

                # Calculate total value
                total_value = portfolio.current_cash + total_holdings_value

                # Update portfolio total value
                portfolio.total_value = total_value
                portfolio.updated_at = datetime.utcnow()
                session.commit()

                return {
                    'portfolio_id': portfolio.id,
                    'initial_capital': portfolio.initial_capital,
                    'current_cash': portfolio.current_cash,
                    'holdings_value': total_holdings_value,
                    'total_value': total_value,
                    'total_return': total_value - portfolio.initial_capital,
                    'total_return_pct': ((total_value / portfolio.initial_capital) - 1) * 100 if portfolio.initial_capital > 0 else 0,
                    'holdings': holdings_data,
                    'updated_at': portfolio.updated_at.isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            raise

    @staticmethod
    def buy_stock(user_id: int, symbol: str, quantity: float, price: float) -> dict:
        """Buy stock and update portfolio"""
        try:
            with db_manager.get_session() as session:
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if not portfolio:
                    portfolio = PortfolioService.get_or_create_portfolio(user_id)
                    session.add(portfolio)
                    session.flush()

                # Calculate total cost
                total_cost = quantity * price

                # Check if sufficient cash
                if total_cost > portfolio.current_cash:
                    return {
                        'success': False,
                        'error': 'Insufficient cash'
                    }

                # Update cash
                portfolio.current_cash -= total_cost

                # Update or create holding
                holding = session.query(Holding).filter_by(
                    portfolio_id=portfolio.id,
                    symbol=symbol
                ).first()

                if holding:
                    # Update existing holding
                    total_quantity = holding.quantity + quantity
                    total_cost_basis = (holding.quantity * holding.avg_cost) + total_cost
                    holding.avg_cost = total_cost_basis / total_quantity
                    holding.quantity = total_quantity
                    holding.current_price = price
                    holding.updated_at = datetime.utcnow()
                else:
                    # Create new holding
                    holding = Holding(
                        portfolio_id=portfolio.id,
                        symbol=symbol,
                        quantity=quantity,
                        avg_cost=price,
                        current_price=price
                    )
                    session.add(holding)

                # Create transaction record
                transaction = Transaction(
                    portfolio_id=portfolio.id,
                    transaction_type=TransactionType.BUY,
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    total_amount=total_cost
                )
                session.add(transaction)

                # Update portfolio
                portfolio.updated_at = datetime.utcnow()

                session.commit()

                logger.info(f"User {user_id} bought {quantity} shares of {symbol} at ${price}")

                return {
                    'success': True,
                    'message': f'Bought {quantity} shares of {symbol} at ${price:.2f}',
                    'transaction_id': transaction.id
                }

        except Exception as e:
            logger.error(f"Error buying stock: {e}")
            raise

    @staticmethod
    def sell_stock(user_id: int, symbol: str, quantity: float, price: float) -> dict:
        """Sell stock and update portfolio"""
        try:
            with db_manager.get_session() as session:
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if not portfolio:
                    return {
                        'success': False,
                        'error': 'Portfolio not found'
                    }

                # Get holding
                holding = session.query(Holding).filter_by(
                    portfolio_id=portfolio.id,
                    symbol=symbol
                ).first()

                if not holding or holding.quantity < quantity:
                    return {
                        'success': False,
                        'error': 'Insufficient shares'
                    }

                # Calculate proceeds
                proceeds = quantity * price

                # Update cash
                portfolio.current_cash += proceeds

                # Update holding
                holding.quantity -= quantity
                holding.current_price = price
                holding.updated_at = datetime.utcnow()

                # If no shares left, delete holding
                if holding.quantity <= 0:
                    session.delete(holding)

                # Create transaction record
                transaction = Transaction(
                    portfolio_id=portfolio.id,
                    transaction_type=TransactionType.SELL,
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    total_amount=proceeds
                )
                session.add(transaction)

                # Update portfolio
                portfolio.updated_at = datetime.utcnow()

                session.commit()

                logger.info(f"User {user_id} sold {quantity} shares of {symbol} at ${price}")

                return {
                    'success': True,
                    'message': f'Sold {quantity} shares of {symbol} at ${price:.2f}',
                    'transaction_id': transaction.id
                }

        except Exception as e:
            logger.error(f"Error selling stock: {e}")
            raise

    @staticmethod
    def deposit_cash(user_id: int, amount: float, notes: str = None) -> dict:
        """Deposit cash to portfolio"""
        try:
            with db_manager.get_session() as session:
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if not portfolio:
                    portfolio = PortfolioService.get_or_create_portfolio(user_id)
                    session.add(portfolio)
                    session.flush()

                # Update cash
                portfolio.current_cash += amount

                # Create transaction record
                transaction = Transaction(
                    portfolio_id=portfolio.id,
                    transaction_type=TransactionType.DEPOSIT,
                    total_amount=amount,
                    notes=notes or f"Deposited ${amount:.2f}"
                )
                session.add(transaction)

                # Update portfolio
                portfolio.updated_at = datetime.utcnow()

                session.commit()

                logger.info(f"User {user_id} deposited ${amount}")

                return {
                    'success': True,
                    'message': f'Deposited ${amount:.2f}',
                    'new_balance': portfolio.current_cash
                }

        except Exception as e:
            logger.error(f"Error depositing cash: {e}")
            raise

    @staticmethod
    def withdraw_cash(user_id: int, amount: float, notes: str = None) -> dict:
        """Withdraw cash from portfolio"""
        try:
            with db_manager.get_session() as session:
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if not portfolio:
                    return {
                        'success': False,
                        'error': 'Portfolio not found'
                    }

                # Check if sufficient cash
                if amount > portfolio.current_cash:
                    return {
                        'success': False,
                        'error': 'Insufficient cash'
                    }

                # Update cash
                portfolio.current_cash -= amount

                # Create transaction record
                transaction = Transaction(
                    portfolio_id=portfolio.id,
                    transaction_type=TransactionType.WITHDRAWAL,
                    total_amount=amount,
                    notes=notes or f"Withdrew ${amount:.2f}"
                )
                session.add(transaction)

                # Update portfolio
                portfolio.updated_at = datetime.utcnow()

                session.commit()

                logger.info(f"User {user_id} withdrew ${amount}")

                return {
                    'success': True,
                    'message': f'Withdrew ${amount:.2f}',
                    'new_balance': portfolio.current_cash
                }

        except Exception as e:
            logger.error(f"Error withdrawing cash: {e}")
            raise

    @staticmethod
    def get_transactions(user_id: int, limit: int = 50) -> list:
        """Get transaction history"""
        try:
            with db_manager.get_session() as session:
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if not portfolio:
                    return []

                transactions = session.query(Transaction).filter_by(
                    portfolio_id=portfolio.id
                ).order_by(Transaction.created_at.desc()).limit(limit).all()

                return [{
                    'id': t.id,
                    'type': t.transaction_type.value,
                    'symbol': t.symbol,
                    'quantity': t.quantity,
                    'price': t.price,
                    'total_amount': t.total_amount,
                    'notes': t.notes,
                    'created_at': t.created_at.isoformat()
                } for t in transactions]

        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise

    @staticmethod
    def update_holding_prices(user_id: int, prices: dict):
        """Update current prices for holdings"""
        try:
            with db_manager.get_session() as session:
                portfolio = session.query(Portfolio).filter_by(user_id=user_id).first()

                if not portfolio:
                    return

                holdings = session.query(Holding).filter_by(portfolio_id=portfolio.id).all()

                for holding in holdings:
                    if holding.symbol in prices:
                        holding.current_price = prices[holding.symbol]
                        holding.updated_at = datetime.utcnow()

                session.commit()

        except Exception as e:
            logger.error(f"Error updating holding prices: {e}")
            raise
