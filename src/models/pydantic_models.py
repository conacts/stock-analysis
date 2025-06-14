"""
Pydantic models for type generation and API validation.

These models serve as the single source of truth for data structures
and are used to generate TypeScript types for the automation system.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Core Analysis Models
class DailyAnalysisModel(BaseModel):
    """Individual stock analysis results"""

    id: Optional[int] = None
    date: date
    symbol: str = Field(..., max_length=10)
    analysis_data: Dict[str, Any]
    composite_score: Optional[Decimal] = Field(None, decimal_places=2)
    rating: Optional[str] = Field(None, max_length=20)
    confidence: Optional[str] = Field(None, max_length=20)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DailyDecisionModel(BaseModel):
    """Daily investment decisions and reasoning"""

    id: Optional[int] = None
    date: date
    decision_type: str = Field(..., max_length=50)
    reasoning: str
    selected_stocks: Optional[Dict[str, Any]] = None
    market_context: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PerformanceTrackingModel(BaseModel):
    """Track recommendation performance over time"""

    id: Optional[int] = None
    symbol: str = Field(..., max_length=10)
    recommendation_date: date
    entry_price: Optional[Decimal] = Field(None, decimal_places=2)
    current_price: Optional[Decimal] = Field(None, decimal_places=2)
    target_price: Optional[Decimal] = Field(None, decimal_places=2)
    rating: Optional[str] = Field(None, max_length=20)
    days_held: Optional[int] = None
    return_pct: Optional[Decimal] = Field(None, decimal_places=4)
    status: Optional[str] = Field(None, max_length=20)  # active, closed
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketContextModel(BaseModel):
    """Daily market conditions and context"""

    id: Optional[int] = None
    date: date
    market_sentiment: Optional[str] = Field(None, max_length=50)
    vix_level: Optional[Decimal] = Field(None, decimal_places=2)
    sector_rotation: Optional[Dict[str, Any]] = None
    economic_indicators: Optional[Dict[str, Any]] = None
    news_themes: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Portfolio Management Models
class PortfolioModel(BaseModel):
    """Portfolio model for tracking multiple investment accounts"""

    id: Optional[int] = None
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    portfolio_type: str = Field(default="personal", max_length=50)
    base_currency: str = Field(default="USD", max_length=3)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class PortfolioPositionModel(BaseModel):
    """Current holdings in a portfolio"""

    id: Optional[int] = None
    portfolio_id: int
    symbol: str = Field(..., max_length=10)
    quantity: Decimal = Field(..., decimal_places=6)
    average_cost: Decimal = Field(..., decimal_places=2)
    current_price: Decimal = Field(..., decimal_places=2)
    market_value: Decimal = Field(..., decimal_places=2)
    unrealized_pnl: Decimal = Field(..., decimal_places=2)
    unrealized_pnl_pct: Decimal = Field(..., decimal_places=4)
    sector: Optional[str] = Field(None, max_length=50)
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioTransactionModel(BaseModel):
    """Transaction history for portfolio positions"""

    id: Optional[int] = None
    portfolio_id: int
    symbol: str = Field(..., max_length=10)
    transaction_type: str = Field(..., max_length=20)  # buy, sell, dividend, split
    quantity: Decimal = Field(..., decimal_places=6)
    price: Decimal = Field(..., decimal_places=2)
    total_amount: Decimal = Field(..., decimal_places=2)
    fees: Decimal = Field(default=0, decimal_places=2)
    transaction_date: date
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PortfolioSnapshotModel(BaseModel):
    """Daily portfolio value and performance snapshots"""

    id: Optional[int] = None
    portfolio_id: int
    snapshot_date: date
    total_value: Decimal = Field(..., decimal_places=2)
    cash_balance: Decimal = Field(..., decimal_places=2)
    invested_amount: Decimal = Field(..., decimal_places=2)
    unrealized_pnl: Decimal = Field(..., decimal_places=2)
    unrealized_pnl_pct: Decimal = Field(..., decimal_places=4)
    day_change: Decimal = Field(..., decimal_places=2)
    day_change_pct: Decimal = Field(..., decimal_places=4)
    positions_count: int
    top_holdings: Optional[str] = None  # JSON string
    sector_allocation: Optional[str] = None  # JSON string
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Analysis Result Models
class StockAnalysisResult(BaseModel):
    """Complete stock analysis result"""

    symbol: str
    analysis_date: date
    composite_score: Optional[float] = None
    rating: Optional[str] = None
    confidence: Optional[str] = None
    fundamentals: Optional[Dict[str, Any]] = None
    technical: Optional[Dict[str, Any]] = None
    news_sentiment: Optional[Dict[str, Any]] = None
    recommendation: Optional[Dict[str, Any]] = None
    risk_factors: Optional[List[str]] = None
    catalysts: Optional[List[str]] = None

    class Config:
        from_attributes = True


class PortfolioAnalysisResult(BaseModel):
    """Portfolio analysis and health check result"""

    portfolio_id: int
    analysis_date: date
    total_value: Decimal
    day_change: Decimal
    day_change_pct: Decimal
    positions_count: int
    top_performers: List[Dict[str, Any]]
    underperformers: List[Dict[str, Any]]
    sector_allocation: Dict[str, float]
    risk_metrics: Dict[str, float]
    recommendations: List[str]

    class Config:
        from_attributes = True


# Task Payload Models (for Trigger.dev)
class StockAnalysisPayload(BaseModel):
    """Payload for stock analysis tasks"""

    symbols: Optional[List[str]] = None
    force_run: bool = False
    sector: Optional[str] = None
    deep_analysis: bool = False

    class Config:
        from_attributes = True


class PortfolioPayload(BaseModel):
    """Payload for portfolio tasks"""

    portfolio_id: Optional[int] = None
    action: str = Field(default="monitor")  # monitor, rebalance, snapshot
    force_run: bool = False

    class Config:
        from_attributes = True


class AlertPayload(BaseModel):
    """Payload for alert tasks"""

    type: str  # stock, portfolio, system
    symbol: Optional[str] = None
    portfolio_id: Optional[int] = None
    threshold: Optional[float] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


# Response Models
class TaskResult(BaseModel):
    """Generic task execution result"""

    status: str  # completed, failed, skipped
    timestamp: datetime
    duration_ms: Optional[int] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisTaskResult(TaskResult):
    """Stock analysis task result"""

    date: date
    stocks_analyzed: int
    top_picks: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class PortfolioTaskResult(TaskResult):
    """Portfolio task result"""

    portfolio_id: int
    action_taken: str
    positions_updated: int
    alerts_sent: int

    class Config:
        from_attributes = True


# Health Check Models
class DatabaseHealth(BaseModel):
    """Database health status"""

    status: str  # healthy, degraded, unhealthy
    connection_time_ms: Optional[float] = None
    query_time_ms: Optional[float] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class EnvironmentHealth(BaseModel):
    """Environment/service health status"""

    status: str  # healthy, degraded, unhealthy
    version: Optional[str] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class HealthCheckResult(BaseModel):
    """Complete system health check result"""

    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    checks: Dict[str, Any]  # database, python, environment, etc.

    class Config:
        from_attributes = True
