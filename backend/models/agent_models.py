#!/usr/bin/env python3
"""
Agent-Customer Trading Models for AI Stock Trading Platform
Defines models for agent operations, customer portfolios, trading suggestions, and learning system
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import json
from enum import Enum as PyEnum
from models.user import Base

class CustomerPortfolioStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LIQUIDATING = "liquidating"

class TradingSuggestionType(PyEnum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class SuggestionStatus(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class TradeExecutionStatus(PyEnum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class CustomerPortfolio(Base):
    __tablename__ = 'customer_portfolios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    portfolio_name = Column(String(200), nullable=False, default="Main Portfolio")

    # Portfolio metrics
    initial_capital = Column(Float, nullable=False)
    current_cash = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False, default=0.0)
    invested_amount = Column(Float, nullable=False, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    total_return = Column(Float, default=0.0)
    total_return_percent = Column(Float, default=0.0)

    # Risk management
    max_position_size = Column(Float, default=0.1)  # 10% max per position
    stop_loss_percent = Column(Float, default=0.05)  # 5% stop loss
    take_profit_percent = Column(Float, default=0.15)  # 15% take profit

    # Status and settings
    status = Column(Enum(CustomerPortfolioStatus), default=CustomerPortfolioStatus.ACTIVE)
    auto_trading_enabled = Column(Boolean, default=False)
    risk_level = Column(String(20), default="moderate")  # conservative, moderate, aggressive

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    agent = relationship("User", foreign_keys=[agent_id])
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    suggestions = relationship("TradingSuggestion", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("TradeExecution", back_populates="portfolio", cascade="all, delete-orphan")

class PortfolioHolding(Base):
    __tablename__ = 'portfolio_holdings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('customer_portfolios.id'), nullable=False)
    symbol = Column(String(20), nullable=False)

    # Position details
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False, default=0.0)
    market_value = Column(Float, nullable=False, default=0.0)

    # P&L tracking
    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_percent = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)

    # Risk management
    stop_loss_price = Column(Float, nullable=True)
    take_profit_price = Column(Float, nullable=True)

    # Metadata
    sector = Column(String(100), nullable=True)
    company_name = Column(String(200), nullable=True)

    # Timestamps
    first_acquired = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("CustomerPortfolio", back_populates="holdings")

class TradingSuggestion(Base):
    __tablename__ = 'trading_suggestions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('customer_portfolios.id'), nullable=False)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Suggestion details
    symbol = Column(String(20), nullable=False)
    suggestion_type = Column(Enum(TradingSuggestionType), nullable=False)
    suggested_quantity = Column(Float, nullable=False)
    suggested_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)

    # AI predictions and reasoning
    ai_confidence = Column(Float, nullable=False)  # 0-1 confidence score
    predicted_return = Column(Float, nullable=False)  # Expected return %
    risk_score = Column(Float, nullable=False)  # 0-1 risk score
    reasoning = Column(Text, nullable=False)
    technical_indicators = Column(JSON, nullable=True)  # Store technical analysis data

    # Market context
    market_sentiment = Column(String(20), nullable=True)  # bullish, bearish, neutral
    news_sentiment = Column(Float, nullable=True)  # -1 to 1 sentiment score
    sector_performance = Column(Float, nullable=True)

    # Time management
    valid_until = Column(DateTime, nullable=True)
    priority = Column(Integer, default=5)  # 1-10 priority scale

    # Status tracking
    status = Column(Enum(SuggestionStatus), default=SuggestionStatus.PENDING)
    agent_notes = Column(Text, nullable=True)
    customer_feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)

    # Relationships
    portfolio = relationship("CustomerPortfolio", back_populates="suggestions")
    agent = relationship("User", foreign_keys=[agent_id])
    execution = relationship("TradeExecution", back_populates="suggestion", uselist=False)

class TradeExecution(Base):
    __tablename__ = 'trade_executions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('customer_portfolios.id'), nullable=False)
    suggestion_id = Column(Integer, ForeignKey('trading_suggestions.id'), nullable=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Trade details
    symbol = Column(String(20), nullable=False)
    trade_type = Column(Enum(TradingSuggestionType), nullable=False)
    quantity = Column(Float, nullable=False)
    executed_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)

    # Execution tracking
    status = Column(Enum(TradeExecutionStatus), default=TradeExecutionStatus.PENDING)
    order_id = Column(String(100), nullable=True)  # External broker order ID
    execution_method = Column(String(50), default="manual")  # manual, auto, scheduled

    # Performance tracking
    expected_return = Column(Float, nullable=True)
    actual_return = Column(Float, nullable=True)  # Filled when position is closed
    holding_period = Column(Integer, nullable=True)  # Days held

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    settled_at = Column(DateTime, nullable=True)

    # Relationships
    portfolio = relationship("CustomerPortfolio", back_populates="trades")
    suggestion = relationship("TradingSuggestion", back_populates="execution")
    agent = relationship("User", foreign_keys=[agent_id])

class AgentDecisionFeedback(Base):
    __tablename__ = 'agent_decision_feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    suggestion_id = Column(Integer, ForeignKey('trading_suggestions.id'), nullable=False)

    # Decision details
    agent_decision = Column(String(20), nullable=False)  # approved, rejected, modified
    decision_reasoning = Column(Text, nullable=True)
    confidence_in_ai = Column(Float, nullable=True)  # Agent's confidence in AI suggestion

    # Outcome tracking (for learning)
    actual_outcome = Column(String(20), nullable=True)  # profitable, loss, neutral
    outcome_value = Column(Float, nullable=True)  # Actual return achieved
    days_to_outcome = Column(Integer, nullable=True)

    # Learning metrics
    ai_accuracy = Column(Float, nullable=True)  # How accurate was AI prediction
    decision_quality = Column(Float, nullable=True)  # Quality of agent's decision

    # Context that influenced decision
    market_conditions = Column(JSON, nullable=True)
    customer_preferences = Column(JSON, nullable=True)
    portfolio_context = Column(JSON, nullable=True)

    # Timestamps
    decision_at = Column(DateTime, default=datetime.utcnow)
    outcome_determined_at = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("User", foreign_keys=[agent_id])
    suggestion = relationship("TradingSuggestion", foreign_keys=[suggestion_id])

class CustomerInteraction(Base):
    __tablename__ = 'customer_interactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # consultation, trade_discussion, review, etc.
    subject = Column(String(200), nullable=False)
    notes = Column(Text, nullable=True)

    # Follow-up tracking
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=3)  # 1-5 priority scale

    # Customer satisfaction
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 rating
    feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent = relationship("User", foreign_keys=[agent_id])
    customer = relationship("User", foreign_keys=[customer_id])

class AgentPerformanceMetrics(Base):
    __tablename__ = 'agent_performance_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Customer management metrics
    total_customers = Column(Integer, default=0)
    active_customers = Column(Integer, default=0)
    new_customers_acquired = Column(Integer, default=0)
    customer_retention_rate = Column(Float, default=0.0)
    avg_customer_satisfaction = Column(Float, default=0.0)

    # Trading performance
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    avg_return_per_trade = Column(Float, default=0.0)

    # AI interaction metrics
    suggestions_reviewed = Column(Integer, default=0)
    suggestions_approved = Column(Integer, default=0)
    suggestions_rejected = Column(Integer, default=0)
    ai_suggestion_accuracy = Column(Float, default=0.0)

    # Commission and revenue
    total_commission_earned = Column(Float, default=0.0)
    avg_commission_per_customer = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agent = relationship("User", foreign_keys=[agent_id])