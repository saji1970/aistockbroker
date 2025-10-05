#!/usr/bin/env python3
"""
Portfolio Database Models for AI Stock Trading Platform
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .user import Base


class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    DIVIDEND = "DIVIDEND"


class Portfolio(Base):
    """User's portfolio"""
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), default="My Portfolio")
    initial_capital = Column(Float, default=100000.0)
    current_cash = Column(Float, default=100000.0)
    total_value = Column(Float, default=100000.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")


class Holding(Base):
    """Stock holdings in a portfolio"""
    __tablename__ = 'holdings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    symbol = Column(String(10), nullable=False)
    quantity = Column(Float, default=0.0)
    avg_cost = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")


class Transaction(Base):
    """Portfolio transactions"""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    symbol = Column(String(10), nullable=True)  # Null for cash transactions
    quantity = Column(Float, default=0.0)
    price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
