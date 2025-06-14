"""
SQLAlchemy models for stock analysis database
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class DailyAnalysis(Base):
    """Individual stock analysis results"""

    __tablename__ = "daily_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    analysis_data = Column(JSONB, nullable=False)
    composite_score = Column(Numeric(5, 2))
    rating = Column(String(20))
    confidence = Column(String(20))
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("date", "symbol", name="uq_daily_analysis_date_symbol"),)

    def __repr__(self):
        return f"<DailyAnalysis(symbol='{self.symbol}', date='{self.date}', score={self.composite_score})>"


class DailyDecision(Base):
    """Daily investment decisions and reasoning"""

    __tablename__ = "daily_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    decision_type = Column(String(50), nullable=False)
    reasoning = Column(Text, nullable=False)
    selected_stocks = Column(JSONB)
    market_context = Column(JSONB)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<DailyDecision(date='{self.date}', type='{self.decision_type}')>"


class PerformanceTracking(Base):
    """Track recommendation performance over time"""

    __tablename__ = "performance_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    recommendation_date = Column(Date, nullable=False)
    entry_price = Column(Numeric(10, 2))
    current_price = Column(Numeric(10, 2))
    target_price = Column(Numeric(10, 2))
    rating = Column(String(20))
    days_held = Column(Integer)
    return_pct = Column(Numeric(8, 4))
    status = Column(String(20))  # active, closed
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PerformanceTracking(symbol='{self.symbol}', return={self.return_pct}%)>"


class MarketContext(Base):
    """Daily market conditions and context"""

    __tablename__ = "market_context"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    market_sentiment = Column(String(50))
    vix_level = Column(Numeric(6, 2))
    sector_rotation = Column(JSONB)
    economic_indicators = Column(JSONB)
    news_themes = Column(JSONB)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<MarketContext(date='{self.date}', sentiment='{self.market_sentiment}')>"


# Migration tracking table
class MigrationHistory(Base):
    """Track database migrations"""

    __tablename__ = "migration_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), nullable=False, unique=True)
    description = Column(String(200))
    applied_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<MigrationHistory(version='{self.version}', applied='{self.applied_at}')>"


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""

    symbol: str
    recommendation_date: str
    entry_price: float
    current_price: float
    target_price: float
    rating: str
    days_held: int
    return_pct: float
    status: str
    updated_at: str


# Portfolio Management Models


@dataclass
class Portfolio:
    """Portfolio model for tracking multiple investment accounts"""

    id: Optional[int] = None
    name: str = ""
    description: str = ""
    portfolio_type: str = "personal"  # personal, ira, 401k, etc.
    base_currency: str = "USD"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool = True


@dataclass
class PortfolioPosition:
    """Current holdings in a portfolio"""

    id: Optional[int] = None
    portfolio_id: int = 0
    symbol: str = ""
    quantity: float = 0.0
    average_cost: float = 0.0
    current_price: float = 0.0
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    sector: str = ""
    last_updated: Optional[str] = None


@dataclass
class PortfolioTransaction:
    """Transaction history for portfolio positions"""

    id: Optional[int] = None
    portfolio_id: int = 0
    symbol: str = ""
    transaction_type: str = ""  # buy, sell, dividend, split
    quantity: float = 0.0
    price: float = 0.0
    total_amount: float = 0.0
    fees: float = 0.0
    transaction_date: str = ""
    notes: str = ""
    created_at: Optional[str] = None


@dataclass
class PortfolioSnapshot:
    """Daily portfolio value and performance snapshots"""

    id: Optional[int] = None
    portfolio_id: int = 0
    snapshot_date: str = ""
    total_value: float = 0.0
    cash_balance: float = 0.0
    invested_amount: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    day_change: float = 0.0
    day_change_pct: float = 0.0
    positions_count: int = 0
    top_holdings: str = ""  # JSON string of top 5 holdings
    sector_allocation: str = ""  # JSON string of sector breakdown
    created_at: Optional[str] = None


# Swarm AI Trading System Models


class SwarmAgentPrompt(Base):
    """Agent system prompts for Swarm AI trading system"""

    __tablename__ = "agent_prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False, index=True)
    prompt_version = Column(String(50), nullable=False)
    system_prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    description = Column(Text)

    __table_args__ = (UniqueConstraint("agent_name", "prompt_version", name="uq_agent_prompts_name_version"),)

    def __repr__(self):
        return f"<SwarmAgentPrompt(agent='{self.agent_name}', version='{self.prompt_version}')>"


class SwarmPortfolioConfig(Base):
    """Portfolio configurations for Swarm AI trading system"""

    __tablename__ = "portfolio_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    symbols = Column(JSONB, nullable=False)
    risk_tolerance = Column(String(50), nullable=False)
    max_position_size_pct = Column(Numeric(5, 2), default=5.0)
    max_sector_exposure_pct = Column(Numeric(5, 2), default=20.0)
    cash_reserve_pct = Column(Numeric(5, 2), default=10.0)
    trading_enabled = Column(Boolean, default=True)
    rebalance_frequency = Column(String(50), default="weekly")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<SwarmPortfolioConfig(portfolio_id='{self.portfolio_id}', name='{self.name}')>"


class SwarmConversationHistory(Base):
    """Conversation history for Swarm AI trading system"""

    __tablename__ = "swarm_conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(String(100), nullable=False, index=True)
    conversation_id = Column(String(100), unique=True, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    agent_responses = Column(JSONB, nullable=False)
    final_agent = Column(String(100), nullable=False)
    turns_used = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    conversation_metadata = Column(JSONB)  # Renamed from metadata to avoid conflict

    def __repr__(self):
        return f"<SwarmConversationHistory(portfolio_id='{self.portfolio_id}', conversation_id='{self.conversation_id}')>"


class SwarmTradingDecision(Base):
    """Trading decisions made by Swarm AI system"""

    __tablename__ = "trading_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(100), nullable=False, index=True)
    portfolio_id = Column(String(100), nullable=False, index=True)
    decision_type = Column(String(50), nullable=False)
    symbol = Column(String(20), index=True)
    quantity = Column(Numeric(15, 6))
    price = Column(Numeric(15, 6))
    reasoning = Column(Text, nullable=False)
    confidence_score = Column(Numeric(3, 2))
    risk_assessment = Column(Text)
    executed = Column(Boolean, default=False)
    execution_result = Column(JSONB)
    created_at = Column(DateTime, default=func.now())
    executed_at = Column(DateTime)

    def __repr__(self):
        return f"<SwarmTradingDecision(symbol='{self.symbol}', decision_type='{self.decision_type}')>"


class SwarmMarketContext(Base):
    """Market context data for Swarm AI trading system"""

    __tablename__ = "swarm_market_context"  # Renamed to avoid conflict

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(String(100), nullable=False, index=True)
    context_type = Column(String(100), nullable=False, index=True)
    symbol = Column(String(20), index=True)
    data = Column(JSONB, nullable=False)
    relevance_score = Column(Numeric(3, 2))
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)

    def __repr__(self):
        return f"<SwarmMarketContext(portfolio_id='{self.portfolio_id}', context_type='{self.context_type}')>"
