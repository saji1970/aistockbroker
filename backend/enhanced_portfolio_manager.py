#!/usr/bin/env python3
"""
Enhanced Portfolio Management System
Handles investment configuration, shadow trading, buy/sell operations at market prices,
and persistent portfolio state management.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class AssetType(Enum):
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    ETF = "ETF"

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"

@dataclass
class Asset:
    symbol: str
    name: str
    asset_type: AssetType
    current_price: float
    quantity: float = 0.0
    avg_cost: float = 0.0
    target_allocation: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

@dataclass
class Transaction:
    id: str
    symbol: str
    transaction_type: TransactionType
    quantity: float
    price: float
    total_amount: float
    timestamp: datetime
    fees: float = 0.0
    notes: str = ""

@dataclass
class PortfolioConfig:
    investment_amount: float
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    max_position_size: float = 0.20  # Maximum 20% in single asset
    min_position_size: float = 0.02  # Minimum 2% in single asset
    rebalance_threshold: float = 0.05  # 5% deviation triggers rebalancing
    trading_fees: float = 0.001  # 0.1% trading fees
    auto_rebalance: bool = True
    stop_loss_percentage: float = 0.10  # 10% stop loss
    take_profit_percentage: float = 0.20  # 20% take profit

@dataclass
class Portfolio:
    id: str
    name: str
    config: PortfolioConfig
    total_capital: float
    available_cash: float
    total_value: float
    assets: Dict[str, Asset]
    transactions: List[Transaction]
    performance_history: List[Dict]
    created_at: datetime
    last_updated: datetime
    last_rebalance: Optional[datetime] = None

class EnhancedPortfolioManager:
    def __init__(self, investment_amount: float, portfolio_name: str = "Main Portfolio", 
                 ai_predictor=None, data_fetcher=None, config: Optional[PortfolioConfig] = None):
        """
        Initialize enhanced portfolio manager with investment configuration.
        
        Args:
            investment_amount: Starting investment amount in dollars
            portfolio_name: Name of the portfolio
            ai_predictor: AI predictor instance for analysis
            data_fetcher: Data fetcher for real-time prices
            config: Portfolio configuration (optional)
        """
        self.portfolio_id = str(uuid.uuid4())
        self.portfolio_name = portfolio_name
        self.ai_predictor = ai_predictor
        self.data_fetcher = data_fetcher
        
        # Set up configuration
        if config:
            self.config = config
        else:
            self.config = PortfolioConfig(investment_amount=investment_amount)
        
        # Initialize portfolio
        self.portfolio = self._initialize_portfolio()
        
        # Performance tracking
        self.performance_metrics = {
            'total_return': 0.0,
            'total_return_percentage': 0.0,
            'daily_return': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
        
        # Load existing portfolio if it exists
        self._load_portfolio()
        
        logger.info(f"Enhanced Portfolio Manager initialized: {portfolio_name}")
        logger.info(f"Investment Amount: ${investment_amount:,.2f}")
        logger.info(f"Portfolio ID: {self.portfolio_id}")

    def _initialize_portfolio(self) -> Portfolio:
        """Initialize a new portfolio."""
        return Portfolio(
            id=self.portfolio_id,
            name=self.portfolio_name,
            config=self.config,
            total_capital=self.config.investment_amount,
            available_cash=self.config.investment_amount,
            total_value=self.config.investment_amount,
            assets={},
            transactions=[],
            performance_history=[],
            created_at=datetime.now(),
            last_updated=datetime.now(),
            last_rebalance=None
        )

    def update_investment_amount(self, new_amount: float) -> bool:
        """Update the investment amount and add/remove cash accordingly."""
        if new_amount <= 0:
            logger.error("Investment amount must be positive")
            return False
        
        difference = new_amount - self.config.investment_amount
        
        if difference > 0:
            # Adding capital
            self.portfolio.available_cash += difference
            self.portfolio.total_capital += difference
            self.portfolio.total_value += difference
            
            # Record transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                symbol="CASH",
                transaction_type=TransactionType.DEPOSIT,
                quantity=difference,
                price=1.0,
                total_amount=difference,
                timestamp=datetime.now(),
                notes=f"Cash deposit of ${difference:,.2f}"
            )
            self.portfolio.transactions.append(transaction)
            
        elif difference < 0:
            # Removing capital
            if abs(difference) > self.portfolio.available_cash:
                logger.error("Cannot withdraw more than available cash")
                return False
            
            self.portfolio.available_cash += difference  # difference is negative
            self.portfolio.total_capital += difference
            self.portfolio.total_value += difference
            
            # Record transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                symbol="CASH",
                transaction_type=TransactionType.WITHDRAWAL,
                quantity=abs(difference),
                price=1.0,
                total_amount=abs(difference),
                timestamp=datetime.now(),
                notes=f"Cash withdrawal of ${abs(difference):,.2f}"
            )
            self.portfolio.transactions.append(transaction)
        
        self.config.investment_amount = new_amount
        self._save_portfolio()
        
        logger.info(f"Investment amount updated to ${new_amount:,.2f}")
        return True

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for a symbol."""
        try:
            if self.data_fetcher:
                data = self.data_fetcher.fetch_stock_data(symbol, period="1d")
                if data is not None and not data.empty:
                    return float(data['Close'].iloc[-1])
            
            # Fallback to AI predictor if available
            if self.ai_predictor and hasattr(self.ai_predictor, 'data_fetcher'):
                data = self.ai_predictor.data_fetcher.fetch_stock_data(symbol, period="1d")
                if data is not None and not data.empty:
                    return float(data['Close'].iloc[-1])
            
            logger.warning(f"Could not fetch current price for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return None

    def buy_shares(self, symbol: str, quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Buy shares at market price (shadow trading).
        
        Args:
            symbol: Stock symbol to buy
            quantity: Number of shares to buy
            price: Price per share (if None, uses current market price)
            
        Returns:
            Dictionary with transaction result
        """
        try:
            # Get current market price if not provided
            if price is None:
                price = self.get_current_price(symbol)
                if price is None:
                    return {
                        'success': False,
                        'error': f'Could not fetch current price for {symbol}',
                        'transaction_id': None
                    }
            
            # Ensure quantity and price are numeric
            quantity = float(quantity)
            price = float(price)
            
            # Calculate total cost including fees
            total_cost = quantity * price
            fees = total_cost * self.config.trading_fees
            total_cost_with_fees = total_cost + fees
            
            # Check if we have enough cash
            if total_cost_with_fees > self.portfolio.available_cash:
                return {
                    'success': False,
                    'error': f'Insufficient cash. Need ${total_cost_with_fees:,.2f}, have ${self.portfolio.available_cash:,.2f}',
                    'transaction_id': None
                }
            
            # Create transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                symbol=symbol,
                transaction_type=TransactionType.BUY,
                quantity=quantity,
                price=price,
                total_amount=total_cost_with_fees,
                timestamp=datetime.now(),
                fees=fees,
                notes=f"Bought {quantity:.2f} shares at market price"
            )
            
            # Update portfolio
            if symbol in self.portfolio.assets:
                asset = self.portfolio.assets[symbol]
                # Update average cost
                total_quantity = asset.quantity + quantity
                total_cost_basis = (asset.quantity * asset.avg_cost) + total_cost
                asset.avg_cost = total_cost_basis / total_quantity
                asset.quantity = total_quantity
            else:
                # Create new asset
                asset = Asset(
                    symbol=symbol,
                    name=symbol,
                    asset_type=AssetType.STOCK,
                    current_price=price,
                    quantity=quantity,
                    avg_cost=price,
                    market_value=quantity * price
                )
                self.portfolio.assets[symbol] = asset
            
            # Update cash and total value
            self.portfolio.available_cash -= total_cost_with_fees
            self.portfolio.total_value = self._calculate_total_value()
            self.portfolio.last_updated = datetime.now()
            
            # Add transaction
            self.portfolio.transactions.append(transaction)
            
            # Update performance metrics
            self.performance_metrics['total_trades'] += 1
            
            # Save portfolio
            self._save_portfolio()
            
            logger.info(f"Bought {quantity:.2f} {symbol} at ${price:.2f} (Total: ${total_cost_with_fees:,.2f})")
            
            return {
                'success': True,
                'transaction_id': transaction.id,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'total_cost': total_cost_with_fees,
                'fees': fees,
                'remaining_cash': self.portfolio.available_cash
            }
            
        except Exception as e:
            logger.error(f"Error buying {symbol}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transaction_id': None
            }

    def sell_shares(self, symbol: str, quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Sell shares at market price (shadow trading).
        
        Args:
            symbol: Stock symbol to sell
            quantity: Number of shares to sell
            price: Price per share (if None, uses current market price)
            
        Returns:
            Dictionary with transaction result
        """
        try:
            # Check if we have the asset
            if symbol not in self.portfolio.assets:
                return {
                    'success': False,
                    'error': f'No position in {symbol} to sell',
                    'transaction_id': None
                }
            
            asset = self.portfolio.assets[symbol]
            
            # Check if we have enough shares
            if quantity > asset.quantity:
                return {
                    'success': False,
                    'error': f'Insufficient shares. Have {asset.quantity:.2f}, trying to sell {quantity:.2f}',
                    'transaction_id': None
                }
            
            # Get current market price if not provided
            if price is None:
                price = self.get_current_price(symbol)
                if price is None:
                    return {
                        'success': False,
                        'error': f'Could not fetch current price for {symbol}',
                        'transaction_id': None
                    }
            
            # Ensure quantity and price are numeric
            quantity = float(quantity)
            price = float(price)
            
            # Calculate proceeds and fees
            gross_proceeds = quantity * price
            fees = gross_proceeds * self.config.trading_fees
            net_proceeds = gross_proceeds - fees
            
            # Calculate realized P&L
            cost_basis = quantity * asset.avg_cost
            realized_pnl = gross_proceeds - cost_basis - fees
            
            # Create transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                symbol=symbol,
                transaction_type=TransactionType.SELL,
                quantity=quantity,
                price=price,
                total_amount=net_proceeds,
                timestamp=datetime.now(),
                fees=fees,
                notes=f"Sold {quantity:.2f} shares at market price. P&L: ${realized_pnl:,.2f}"
            )
            
            # Update portfolio
            asset.quantity -= quantity
            asset.realized_pnl += realized_pnl
            
            if asset.quantity <= 0:
                # Remove asset if fully sold
                del self.portfolio.assets[symbol]
            
            # Update cash and total value
            self.portfolio.available_cash += net_proceeds
            self.portfolio.total_value = self._calculate_total_value()
            self.portfolio.last_updated = datetime.now()
            
            # Add transaction
            self.portfolio.transactions.append(transaction)
            
            # Update performance metrics
            self.performance_metrics['total_trades'] += 1
            if realized_pnl > 0:
                self.performance_metrics['winning_trades'] += 1
            else:
                self.performance_metrics['losing_trades'] += 1
            
            # Save portfolio
            self._save_portfolio()
            
            logger.info(f"Sold {quantity:.2f} {symbol} at ${price:.2f} (Net: ${net_proceeds:,.2f}, P&L: ${realized_pnl:,.2f})")
            
            return {
                'success': True,
                'transaction_id': transaction.id,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'gross_proceeds': gross_proceeds,
                'net_proceeds': net_proceeds,
                'fees': fees,
                'realized_pnl': realized_pnl,
                'remaining_cash': self.portfolio.available_cash
            }
            
        except Exception as e:
            logger.error(f"Error selling {symbol}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transaction_id': None
            }

    def _calculate_total_value(self) -> float:
        """Calculate total portfolio value including current market prices."""
        total = self.portfolio.available_cash
        
        for symbol, asset in self.portfolio.assets.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                asset.current_price = current_price
                asset.market_value = asset.quantity * current_price
                asset.unrealized_pnl = asset.market_value - (asset.quantity * asset.avg_cost)
                total += asset.market_value
            else:
                # Use last known price if current price unavailable
                total += asset.quantity * asset.current_price
        
        return total

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary."""
        self.portfolio.total_value = self._calculate_total_value()
        
        # Calculate performance metrics
        total_return = self.portfolio.total_value - self.portfolio.total_capital
        total_return_percentage = (total_return / self.portfolio.total_capital) * 100
        
        self.performance_metrics['total_return'] = total_return
        self.performance_metrics['total_return_percentage'] = total_return_percentage
        
        # Calculate win rate
        if self.performance_metrics['total_trades'] > 0:
            self.performance_metrics['win_rate'] = (
                self.performance_metrics['winning_trades'] / 
                self.performance_metrics['total_trades']
            ) * 100
        
        # Get asset breakdown
        assets_breakdown = []
        for symbol, asset in self.portfolio.assets.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                asset.current_price = current_price
                asset.market_value = asset.quantity * current_price
                asset.unrealized_pnl = asset.market_value - (asset.quantity * asset.avg_cost)
            
            assets_breakdown.append({
                'symbol': symbol,
                'name': asset.name,
                'quantity': asset.quantity,
                'avg_cost': asset.avg_cost,
                'current_price': asset.current_price,
                'market_value': asset.market_value,
                'unrealized_pnl': asset.unrealized_pnl,
                'realized_pnl': asset.realized_pnl,
                'allocation_percentage': (asset.market_value / self.portfolio.total_value) * 100
            })
        
        # Get recent transactions
        recent_transactions = []
        for transaction in sorted(self.portfolio.transactions, key=lambda x: x.timestamp, reverse=True)[:10]:
            recent_transactions.append({
                'id': transaction.id,
                'symbol': transaction.symbol,
                'type': transaction.transaction_type.value,
                'quantity': transaction.quantity,
                'price': transaction.price,
                'total_amount': transaction.total_amount,
                'fees': transaction.fees,
                'timestamp': transaction.timestamp.isoformat(),
                'notes': transaction.notes
            })
        
        return {
            'portfolio_id': self.portfolio.id,
            'portfolio_name': self.portfolio.name,
            'config': asdict(self.config),
            'total_capital': self.portfolio.total_capital,
            'available_cash': self.portfolio.available_cash,
            'total_value': self.portfolio.total_value,
            'total_return': total_return,
            'total_return_percentage': total_return_percentage,
            'performance_metrics': self.performance_metrics,
            'assets': assets_breakdown,
            'recent_transactions': recent_transactions,
            'created_at': self.portfolio.created_at.isoformat(),
            'last_updated': self.portfolio.last_updated.isoformat(),
            'last_rebalance': self.portfolio.last_rebalance.isoformat() if self.portfolio.last_rebalance else None
        }

    def _save_portfolio(self):
        """Save portfolio state to file."""
        try:
            portfolio_data = {
                'portfolio': asdict(self.portfolio),
                'performance_metrics': self.performance_metrics,
                'config': asdict(self.config)
            }
            
            # Convert datetime objects to strings and enums to values
            def convert_for_json(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'AssetType':
                    return obj.value  # Convert enum to its value
                elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'TransactionType':
                    return obj.value  # Convert enum to its value
                elif isinstance(obj, dict):
                    return {k: convert_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_for_json(item) for item in obj]
                return obj
            
            portfolio_data = convert_for_json(portfolio_data)
            
            # Save to file
            filename = f"portfolio_{self.portfolio_id}.json"
            with open(filename, 'w') as f:
                json.dump(portfolio_data, f, indent=2)
            
            logger.info(f"Portfolio saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving portfolio: {str(e)}")

    def _load_portfolio(self):
        """Load portfolio state from file."""
        try:
            filename = f"portfolio_{self.portfolio_id}.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    portfolio_data = json.load(f)
                
                # Restore portfolio
                portfolio_dict = portfolio_data['portfolio']
                
                # Convert string timestamps back to datetime
                def convert_datetime_strings(obj):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if key in ['timestamp', 'created_at', 'last_updated', 'last_rebalance'] and isinstance(value, str):
                                obj[key] = datetime.fromisoformat(value)
                            elif isinstance(value, (dict, list)):
                                convert_datetime_strings(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            convert_datetime_strings(item)
                
                convert_datetime_strings(portfolio_dict)
                
                # Reconstruct portfolio object
                self.portfolio = Portfolio(**portfolio_dict)
                self.performance_metrics = portfolio_data['performance_metrics']
                self.config = PortfolioConfig(**portfolio_data['config'])
                
                logger.info(f"Portfolio loaded from {filename}")
            
        except Exception as e:
            logger.error(f"Error loading portfolio: {str(e)}")

    def get_transaction_history(self, limit: int = 50) -> List[Dict]:
        """Get transaction history."""
        transactions = sorted(self.portfolio.transactions, key=lambda x: x.timestamp, reverse=True)
        return [
            {
                'id': t.id,
                'symbol': t.symbol,
                'type': t.transaction_type.value,
                'quantity': t.quantity,
                'price': t.price,
                'total_amount': t.total_amount,
                'fees': t.fees,
                'timestamp': t.timestamp.isoformat(),
                'notes': t.notes
            }
            for t in transactions[:limit]
        ]

    def get_asset_performance(self, symbol: str) -> Optional[Dict]:
        """Get performance details for a specific asset."""
        if symbol not in self.portfolio.assets:
            return None
        
        asset = self.portfolio.assets[symbol]
        current_price = self.get_current_price(symbol)
        
        if current_price:
            asset.current_price = current_price
            asset.market_value = asset.quantity * current_price
            asset.unrealized_pnl = asset.market_value - (asset.quantity * asset.avg_cost)
        
        # Get transactions for this asset
        asset_transactions = [t for t in self.portfolio.transactions if t.symbol == symbol]
        
        return {
            'symbol': symbol,
            'name': asset.name,
            'quantity': asset.quantity,
            'avg_cost': asset.avg_cost,
            'current_price': asset.current_price,
            'market_value': asset.market_value,
            'unrealized_pnl': asset.unrealized_pnl,
            'realized_pnl': asset.realized_pnl,
            'total_pnl': asset.unrealized_pnl + asset.realized_pnl,
            'return_percentage': ((asset.current_price - asset.avg_cost) / asset.avg_cost) * 100 if asset.avg_cost > 0 else 0,
            'transactions': len(asset_transactions)
        }