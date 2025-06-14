"""
SQLAlchemy models for stock analysis database
"""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
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

    __table_args__ = (
        UniqueConstraint("date", "symbol", name="uq_daily_analysis_date_symbol"),
    )

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
        return (
            f"<PerformanceTracking(symbol='{self.symbol}', return={self.return_pct}%)>"
        )


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
        return (
            f"<MarketContext(date='{self.date}', sentiment='{self.market_sentiment}')>"
        )


# Migration tracking table
class MigrationHistory(Base):
    """Track database migrations"""

    __tablename__ = "migration_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), nullable=False, unique=True)
    description = Column(String(200))
    applied_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return (
            f"<MigrationHistory(version='{self.version}', applied='{self.applied_at}')>"
        )
