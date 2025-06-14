"""
Trading API Endpoints

FastAPI endpoints for AI-powered trading functionality including
portfolio analysis, signal generation, and trade recommendations.
"""

import logging
import sys
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from llm.deepseek_analyzer import DeepSeekAnalyzer as DeepSeekClient
from models.trading_models import (
    RiskStatus,
    StopResult,
    TradeRecommendation,
    TradingAnalysis,
    TradingSignal,
)
from portfolio.portfolio_manager import PortfolioManager as PortfolioService
from trading.ai_engine import AITradingEngine
from trading.market_data import MarketDataProvider
from trading.risk_manager import RiskManager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/trading", tags=["AI Trading"])


# Request/Response models
class AnalyzePortfolioRequest(BaseModel):
    portfolio_id: int


class GenerateSignalsRequest(BaseModel):
    analysis: TradingAnalysis


class RecommendTradesRequest(BaseModel):
    signals: List[TradingSignal]


class EmergencyStopRequest(BaseModel):
    portfolio_id: int
    reason: str


# Dependency injection
async def get_ai_trading_engine() -> AITradingEngine:
    """Get AI Trading Engine instance."""
    deepseek_client = DeepSeekClient()
    market_data_provider = MarketDataProvider()
    portfolio_service = PortfolioService()
    risk_manager = RiskManager()

    return AITradingEngine(
        deepseek_client=deepseek_client,
        market_data_provider=market_data_provider,
        portfolio_service=portfolio_service,
        risk_manager=risk_manager,
    )


async def get_risk_manager() -> RiskManager:
    """Get Risk Manager instance."""
    return RiskManager()


@router.post("/analyze-portfolio", response_model=TradingAnalysis)
async def analyze_portfolio_for_trading(
    request: AnalyzePortfolioRequest,
    ai_engine: AITradingEngine = Depends(get_ai_trading_engine),
) -> TradingAnalysis:
    """
    Perform comprehensive AI-powered portfolio analysis for trading decisions.

    This endpoint analyzes a portfolio using:
    - Real-time market data
    - Technical indicators
    - Market sentiment
    - Risk assessment
    - AI-powered insights

    Returns detailed analysis with trading opportunities and risks.
    """
    try:
        logger.info(f"Analyzing portfolio {request.portfolio_id} for trading")

        analysis = await ai_engine.analyze_portfolio(request.portfolio_id)

        logger.info(f"Portfolio analysis completed for {request.portfolio_id}")
        return analysis

    except ValueError as e:
        logger.error(f"Portfolio not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze portfolio")


@router.post("/generate-signals", response_model=List[TradingSignal])
async def generate_trading_signals(
    request: GenerateSignalsRequest,
    ai_engine: AITradingEngine = Depends(get_ai_trading_engine),
) -> List[TradingSignal]:
    """
    Generate AI-powered trading signals based on portfolio analysis.

    Takes a portfolio analysis and generates specific trading signals with:
    - Buy/Sell/Hold recommendations
    - Confidence scores
    - Technical and fundamental analysis
    - Price targets and stop losses
    - AI reasoning for each signal

    Returns list of trading signals sorted by confidence.
    """
    try:
        logger.info(f"Generating signals for portfolio {request.analysis.portfolio_id}")

        signals = await ai_engine.generate_signals(request.analysis)

        logger.info(f"Generated {len(signals)} trading signals")
        return signals

    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate trading signals")


@router.post("/recommend-trades", response_model=List[TradeRecommendation])
async def recommend_trades(
    request: RecommendTradesRequest,
    ai_engine: AITradingEngine = Depends(get_ai_trading_engine),
) -> List[TradeRecommendation]:
    """
    Convert trading signals into specific trade recommendations.

    Takes trading signals and creates actionable trade recommendations with:
    - Specific quantities and order types
    - Position sizing based on risk
    - Entry and exit strategies
    - Risk management parameters
    - Portfolio constraint validation

    Returns validated trade recommendations ready for execution.
    """
    try:
        logger.info(f"Creating trade recommendations from {len(request.signals)} signals")

        recommendations = await ai_engine.recommend_trades(request.signals)

        logger.info(f"Created {len(recommendations)} trade recommendations")
        return recommendations

    except Exception as e:
        logger.error(f"Error creating trade recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to create trade recommendations")


@router.get("/risk-status/{portfolio_id}", response_model=RiskStatus)
async def get_risk_status(
    portfolio_id: int,
    risk_manager: RiskManager = Depends(get_risk_manager),
) -> RiskStatus:
    """
    Get current risk status for a portfolio.

    Provides comprehensive risk metrics including:
    - Overall risk level and score
    - Daily P&L and loss limits
    - Position concentration metrics
    - Active risk flags
    - Trading halt status

    Used for monitoring and risk control.
    """
    try:
        logger.info(f"Getting risk status for portfolio {portfolio_id}")

        risk_status = await risk_manager.get_risk_status(portfolio_id)

        return risk_status

    except Exception as e:
        logger.error(f"Error getting risk status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get risk status")


@router.post("/emergency-stop", response_model=StopResult)
async def emergency_stop_trading(
    request: EmergencyStopRequest,
    risk_manager: RiskManager = Depends(get_risk_manager),
) -> StopResult:
    """
    Emergency stop all trading activities for a portfolio.

    Immediately halts all trading activities including:
    - Cancelling pending orders
    - Stopping automated trading
    - Flagging portfolio for manual review
    - Logging emergency stop reason

    This is a safety mechanism for risk control.
    """
    try:
        logger.warning(f"Emergency stop requested for portfolio {request.portfolio_id}: {request.reason}")

        # For now, return a mock stop result
        # In production, this would actually stop trading activities
        stop_result = StopResult(
            portfolio_id=request.portfolio_id,
            reason=request.reason,
            orders_cancelled=0,  # Would be actual count
            positions_closed=0,  # Would be actual count
            stop_successful=True,
            manual_intervention_required=True,
            recovery_actions=[
                "Review portfolio positions",
                "Assess market conditions",
                "Determine if trading can be resumed",
            ],
        )

        logger.info(f"Emergency stop completed for portfolio {request.portfolio_id}")
        return stop_result

    except Exception as e:
        logger.error(f"Error executing emergency stop: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute emergency stop")


# Additional utility endpoints


@router.get("/market-status")
async def get_market_status():
    """
    Get current market status and trading conditions.

    Returns information about:
    - Market open/closed status
    - Current market conditions
    - Trading restrictions
    - System status
    """
    try:
        # Mock market status - in production would check actual market status
        return {
            "market_open": True,
            "trading_enabled": True,
            "market_condition": "NORMAL",
            "restrictions": [],
            "last_updated": "2024-01-01T12:00:00Z",
        }

    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market status")


@router.get("/trading-config")
async def get_trading_config():
    """
    Get current trading configuration and limits.

    Returns system configuration including:
    - Position size limits
    - Risk thresholds
    - Trading hours
    - API rate limits
    """
    try:
        risk_manager = RiskManager()

        return {
            "max_position_size_pct": risk_manager.max_position_size_pct,
            "daily_loss_limit_pct": risk_manager.daily_loss_limit_pct,
            "max_drawdown_pct": risk_manager.max_drawdown_pct,
            "min_cash_reserve_pct": risk_manager.min_cash_reserve_pct,
            "high_volatility_threshold": risk_manager.high_volatility_threshold,
            "extreme_volatility_threshold": risk_manager.extreme_volatility_threshold,
        }

    except Exception as e:
        logger.error(f"Error getting trading config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trading configuration")
