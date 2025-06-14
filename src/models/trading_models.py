"""
Trading Data Models

Pydantic models for AI-powered trading system including signals,
recommendations, risk assessment, and trade execution.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class SignalType(str, Enum):
    """Trading signal types"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class OrderType(str, Enum):
    """Order types for trade execution"""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class TradeAction(str, Enum):
    """Trade actions"""

    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    """Trade execution status"""

    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class RiskLevel(str, Enum):
    """Risk assessment levels"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class MarketCondition(str, Enum):
    """Market condition assessment"""

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    VOLATILE = "VOLATILE"
    TRENDING = "TRENDING"


# Core Trading Models


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators"""

    rsi: Optional[float] = Field(None, ge=0, le=100, description="Relative Strength Index")
    macd: Optional[float] = Field(None, description="MACD value")
    macd_signal: Optional[float] = Field(None, description="MACD signal line")
    sma_20: Optional[float] = Field(None, gt=0, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, gt=0, description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(None, gt=0, description="200-day Simple Moving Average")
    bollinger_upper: Optional[float] = Field(None, gt=0, description="Bollinger Band Upper")
    bollinger_lower: Optional[float] = Field(None, gt=0, description="Bollinger Band Lower")
    volume_avg: Optional[float] = Field(None, ge=0, description="Average volume")
    volatility: Optional[float] = Field(None, ge=0, description="Price volatility")


class MarketSentiment(BaseModel):
    """Market sentiment analysis"""

    overall_sentiment: float = Field(..., ge=-1, le=1, description="Overall sentiment score (-1 to 1)")
    news_sentiment: float = Field(..., ge=-1, le=1, description="News sentiment score")
    social_sentiment: Optional[float] = Field(None, ge=-1, le=1, description="Social media sentiment")
    analyst_sentiment: Optional[float] = Field(None, ge=-1, le=1, description="Analyst sentiment")
    confidence: float = Field(..., ge=0, le=1, description="Sentiment confidence score")
    key_themes: List[str] = Field(default_factory=list, description="Key sentiment themes")


class Price(BaseModel):
    """Real-time price data"""

    symbol: str = Field(..., description="Stock symbol")
    current_price: Decimal = Field(..., gt=0, description="Current price")
    open_price: Decimal = Field(..., gt=0, description="Opening price")
    high_price: Decimal = Field(..., gt=0, description="Day high")
    low_price: Decimal = Field(..., gt=0, description="Day low")
    volume: int = Field(..., ge=0, description="Trading volume")
    previous_close: Decimal = Field(..., gt=0, description="Previous close price")
    change: Decimal = Field(..., description="Price change")
    change_percent: float = Field(..., description="Percentage change")
    timestamp: datetime = Field(default_factory=datetime.now, description="Price timestamp")


class TradingSignal(BaseModel):
    """AI-generated trading signal"""

    id: Optional[int] = Field(None, description="Signal ID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    symbol: str = Field(..., description="Stock symbol")
    signal_type: SignalType = Field(..., description="Signal type")
    confidence: float = Field(..., ge=0, le=1, description="Signal confidence (0-1)")
    reasoning: str = Field(..., description="AI reasoning for signal")

    # Scoring components
    technical_score: float = Field(..., ge=0, le=1, description="Technical analysis score")
    fundamental_score: float = Field(..., ge=0, le=1, description="Fundamental analysis score")
    sentiment_score: float = Field(..., ge=0, le=1, description="Sentiment analysis score")

    # Supporting data
    current_price: Decimal = Field(..., gt=0, description="Current stock price")
    target_price: Optional[Decimal] = Field(None, gt=0, description="Target price")
    stop_loss: Optional[Decimal] = Field(None, gt=0, description="Stop loss price")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Signal creation time")
    expires_at: Optional[datetime] = Field(None, description="Signal expiration time")

    @validator("confidence")
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v


class TradeRecommendation(BaseModel):
    """AI-generated trade recommendation"""

    id: Optional[int] = Field(None, description="Recommendation ID")
    signal_id: int = Field(..., description="Source signal ID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    symbol: str = Field(..., description="Stock symbol")
    action: TradeAction = Field(..., description="Trade action")

    # Order details
    quantity: int = Field(..., gt=0, description="Number of shares")
    order_type: OrderType = Field(..., description="Order type")
    limit_price: Optional[Decimal] = Field(None, gt=0, description="Limit price")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="Stop price")

    # Analysis
    reasoning: str = Field(..., description="Recommendation reasoning")
    risk_score: float = Field(..., ge=0, le=1, description="Risk assessment score")
    expected_return: float = Field(..., description="Expected return percentage")
    holding_period: Optional[int] = Field(None, gt=0, description="Expected holding period in days")

    # Risk management
    position_size_pct: float = Field(..., gt=0, le=1, description="Position size as % of portfolio")
    max_loss_pct: float = Field(..., gt=0, description="Maximum acceptable loss %")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Recommendation creation time")
    expires_at: Optional[datetime] = Field(None, description="Recommendation expiration")


class RiskAssessment(BaseModel):
    """Comprehensive risk assessment"""

    overall_risk: RiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(..., ge=0, le=1, description="Numerical risk score")

    # Risk factors
    position_concentration_risk: float = Field(..., ge=0, le=1, description="Position concentration risk")
    market_risk: float = Field(..., ge=0, le=1, description="Market risk")
    volatility_risk: float = Field(..., ge=0, le=1, description="Volatility risk")
    liquidity_risk: float = Field(..., ge=0, le=1, description="Liquidity risk")

    # Portfolio metrics
    portfolio_beta: Optional[float] = Field(None, description="Portfolio beta")
    var_1day: Optional[float] = Field(None, description="1-day Value at Risk")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown")

    # Risk limits
    daily_loss_limit: float = Field(..., description="Daily loss limit")
    position_limit: float = Field(..., description="Position size limit")

    # Recommendations
    risk_warnings: List[str] = Field(default_factory=list, description="Risk warnings")
    risk_mitigation: List[str] = Field(default_factory=list, description="Risk mitigation suggestions")


class TradingAnalysis(BaseModel):
    """Comprehensive trading analysis"""

    portfolio_id: int = Field(..., description="Portfolio ID")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

    # Market context
    market_condition: MarketCondition = Field(..., description="Current market condition")
    market_sentiment: MarketSentiment = Field(..., description="Market sentiment analysis")

    # Portfolio analysis
    current_positions: List[Dict] = Field(default_factory=list, description="Current portfolio positions")
    portfolio_value: Decimal = Field(..., gt=0, description="Total portfolio value")
    cash_available: Decimal = Field(..., ge=0, description="Available cash")

    # Risk assessment
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")

    # AI insights
    ai_summary: str = Field(..., description="AI analysis summary")
    key_opportunities: List[str] = Field(default_factory=list, description="Key opportunities identified")
    key_risks: List[str] = Field(default_factory=list, description="Key risks identified")

    # Recommendations
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    portfolio_adjustments: List[str] = Field(default_factory=list, description="Portfolio adjustment suggestions")


class PaperTradeResult(BaseModel):
    """Paper trade execution result"""

    id: Optional[int] = Field(None, description="Paper trade ID")
    recommendation_id: int = Field(..., description="Source recommendation ID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    symbol: str = Field(..., description="Stock symbol")
    action: TradeAction = Field(..., description="Trade action")

    # Execution details
    quantity: int = Field(..., gt=0, description="Shares traded")
    price: Decimal = Field(..., gt=0, description="Execution price")
    total_value: Decimal = Field(..., description="Total trade value")
    fees: Decimal = Field(default=Decimal("0"), ge=0, description="Trading fees")

    # Results
    executed_at: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    status: TradeStatus = Field(default=TradeStatus.EXECUTED, description="Trade status")

    # Performance tracking
    unrealized_pnl: Optional[Decimal] = Field(None, description="Unrealized P&L")
    realized_pnl: Optional[Decimal] = Field(None, description="Realized P&L")


class LiveTradeResult(BaseModel):
    """Live trade execution result"""

    id: Optional[int] = Field(None, description="Trade ID")
    recommendation_id: int = Field(..., description="Source recommendation ID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    symbol: str = Field(..., description="Stock symbol")
    action: TradeAction = Field(..., description="Trade action")

    # Order details
    order_id: str = Field(..., description="Broker order ID")
    quantity: int = Field(..., gt=0, description="Shares ordered")
    filled_quantity: int = Field(default=0, ge=0, description="Shares filled")

    # Execution details
    order_type: OrderType = Field(..., description="Order type")
    limit_price: Optional[Decimal] = Field(None, gt=0, description="Limit price")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="Stop price")
    avg_fill_price: Optional[Decimal] = Field(None, gt=0, description="Average fill price")

    # Status and timing
    status: TradeStatus = Field(..., description="Trade status")
    submitted_at: datetime = Field(default_factory=datetime.now, description="Order submission time")
    filled_at: Optional[datetime] = Field(None, description="Order fill time")

    # Costs
    commission: Decimal = Field(default=Decimal("0"), ge=0, description="Commission paid")
    fees: Decimal = Field(default=Decimal("0"), ge=0, description="Other fees")

    # Broker response
    broker_response: Optional[Dict] = Field(None, description="Raw broker response")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class PositionStatus(BaseModel):
    """Current position status"""

    portfolio_id: int = Field(..., description="Portfolio ID")
    symbol: str = Field(..., description="Stock symbol")
    quantity: int = Field(..., description="Current shares held")
    avg_cost: Decimal = Field(..., gt=0, description="Average cost basis")
    current_price: Decimal = Field(..., gt=0, description="Current market price")
    market_value: Decimal = Field(..., description="Current market value")
    unrealized_pnl: Decimal = Field(..., description="Unrealized P&L")
    unrealized_pnl_pct: float = Field(..., description="Unrealized P&L percentage")
    day_change: Decimal = Field(..., description="Day change in value")
    day_change_pct: float = Field(..., description="Day change percentage")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update time")


class ValidationResult(BaseModel):
    """Trade validation result"""

    is_valid: bool = Field(..., description="Whether trade is valid")
    validation_score: float = Field(..., ge=0, le=1, description="Validation confidence score")

    # Validation checks
    risk_check_passed: bool = Field(..., description="Risk check result")
    position_limit_check: bool = Field(..., description="Position limit check")
    cash_check_passed: bool = Field(..., description="Cash availability check")
    market_hours_check: bool = Field(..., description="Market hours check")

    # Issues and warnings
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")

    # Recommendations
    suggested_adjustments: List[str] = Field(default_factory=list, description="Suggested trade adjustments")


class RiskStatus(BaseModel):
    """Portfolio risk status"""

    portfolio_id: int = Field(..., description="Portfolio ID")
    overall_risk: RiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score")

    # Daily metrics
    daily_pnl: Decimal = Field(..., description="Daily P&L")
    daily_pnl_pct: float = Field(..., description="Daily P&L percentage")
    daily_loss_limit: Decimal = Field(..., description="Daily loss limit")
    daily_loss_remaining: Decimal = Field(..., description="Remaining daily loss budget")

    # Position metrics
    largest_position_pct: float = Field(..., description="Largest position as % of portfolio")
    position_concentration: float = Field(..., description="Position concentration score")

    # Risk flags
    risk_flags: List[str] = Field(default_factory=list, description="Active risk flags")
    trading_halted: bool = Field(default=False, description="Whether trading is halted")

    # Timestamps
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update time")


class StopResult(BaseModel):
    """Emergency stop result"""

    portfolio_id: int = Field(..., description="Portfolio ID")
    stopped_at: datetime = Field(default_factory=datetime.now, description="Stop timestamp")
    reason: str = Field(..., description="Reason for stop")

    # Actions taken
    orders_cancelled: int = Field(default=0, ge=0, description="Number of orders cancelled")
    positions_closed: int = Field(default=0, ge=0, description="Number of positions closed")

    # Status
    stop_successful: bool = Field(..., description="Whether stop was successful")
    error_message: Optional[str] = Field(None, description="Error message if stop failed")

    # Recovery
    manual_intervention_required: bool = Field(default=False, description="Whether manual intervention is needed")
    recovery_actions: List[str] = Field(default_factory=list, description="Recommended recovery actions")
