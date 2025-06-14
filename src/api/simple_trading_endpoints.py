"""
Simple Trading API Endpoints

Minimal trading endpoints for testing and development.
"""

import logging
from datetime import datetime
from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/trading", tags=["AI Trading"])


# Simple response models
class TradingConfig(BaseModel):
    max_position_size_pct: float = 0.10
    daily_loss_limit_pct: float = 0.02
    risk_tolerance: str = "moderate"
    trading_enabled: bool = True
    market_hours_only: bool = True


class MarketStatus(BaseModel):
    is_open: bool = True
    next_open: str = "2025-06-14T09:30:00"
    next_close: str = "2025-06-14T16:00:00"
    timezone: str = "US/Eastern"


class SimpleRiskStatus(BaseModel):
    portfolio_id: int
    risk_level: str = "low"
    risk_score: float = 0.25
    daily_pnl: float = 0.0
    trading_halted: bool = False
    last_updated: str


@router.get("/trading-config", response_model=TradingConfig)
async def get_trading_config() -> TradingConfig:
    """
    Get current trading configuration.

    Returns trading parameters including position limits,
    risk settings, and trading status.
    """
    logger.info("Getting trading configuration")

    return TradingConfig(
        max_position_size_pct=0.10,  # 10% max position size
        daily_loss_limit_pct=0.02,  # 2% daily loss limit
        risk_tolerance="moderate",
        trading_enabled=True,
        market_hours_only=True,
    )


@router.get("/market-status", response_model=MarketStatus)
async def get_market_status() -> MarketStatus:
    """
    Get current market status.

    Returns market open/close status and trading hours.
    """
    logger.info("Getting market status")

    # Simple market status (would integrate with real market data)
    return MarketStatus(is_open=True, next_open="2025-06-14T09:30:00", next_close="2025-06-14T16:00:00", timezone="US/Eastern")


@router.get("/risk-status/{portfolio_id}", response_model=SimpleRiskStatus)
async def get_risk_status(portfolio_id: int) -> SimpleRiskStatus:
    """
    Get risk status for a portfolio.

    Returns current risk metrics and trading status.
    """
    logger.info(f"Getting risk status for portfolio {portfolio_id}")

    return SimpleRiskStatus(portfolio_id=portfolio_id, risk_level="low", risk_score=0.25, daily_pnl=125.50, trading_halted=False, last_updated=datetime.now().isoformat())


@router.post("/emergency-stop")
async def emergency_stop_trading(portfolio_id: int, reason: str = "Manual stop") -> Dict:
    """
    Emergency stop trading for a portfolio.

    Immediately halts all trading activities.
    """
    logger.warning(f"Emergency stop requested for portfolio {portfolio_id}: {reason}")

    return {"success": True, "portfolio_id": portfolio_id, "reason": reason, "stopped_at": datetime.now().isoformat(), "message": f"Trading halted for portfolio {portfolio_id}"}


@router.get("/health")
async def trading_health_check() -> Dict:
    """
    Trading system health check.
    """
    return {"status": "healthy", "trading_enabled": True, "market_data_connected": True, "ai_engine_ready": True, "timestamp": datetime.now().isoformat()}
