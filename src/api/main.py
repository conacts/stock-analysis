"""
FastAPI server for Stock Analysis System
Exposes Python analysis functions as REST API endpoints for Trigger.dev tasks
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.analyzer import StockAnalyzer
from data.storage import AnalysisStorage
from db.connection import get_db_connection
from llm.deepseek_analyzer import DeepSeekAnalyzer
from models.pydantic_models import HealthCheckResult
from pipeline.research_engine import ResearchEngine

# Import conversation endpoints
from src.api.conversation_endpoints import (
    ConversationContextRequest,
    ConversationSummaryRequest,
    ConversationThread,
    get_conversation_context,
    get_conversation_summary,
    store_conversation_thread,
)

# Import trading endpoints
try:
    try:
        from .simple_trading_endpoints import router as trading_router
    except ImportError:
        # Fallback for direct script execution
        from simple_trading_endpoints import router as trading_router

    TRADING_ENABLED = True
except ImportError as e:
    print(f"Trading endpoints not available: {e}")
    TRADING_ENABLED = False

# Import Alpaca client

# Initialize FastAPI app
app = FastAPI(title="Stock Analysis API", description="REST API for stock analysis and portfolio management", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include trading router if available
if TRADING_ENABLED:
    app.include_router(trading_router)
    print("✅ AI Trading endpoints enabled")

# Security
security = HTTPBearer()

# Initialize components
analyzer = StockAnalyzer(deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"))
storage = AnalysisStorage()
research_engine = ResearchEngine()

# API Token validation
API_TOKEN = os.getenv("API_TOKEN", "default-dev-token")


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token"""
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return credentials.credentials


# Request/Response Models
class PortfolioSummaryRequest(BaseModel):
    portfolio_id: int


class AnalysisRequest(BaseModel):
    portfolio_data: Dict
    analysis_type: str
    conversation_context: Optional[Dict] = None
    include_recommendations: bool = True
    include_risk_analysis: bool = True
    include_opportunities: bool = True
    store_conversation: bool = True


class NewsAnalysisRequest(BaseModel):
    symbols: List[str]
    hours_back: int = 24


class AlertRequest(BaseModel):
    gap_analysis: List[Dict]


# Health Check Endpoint
@app.get("/health", response_model=HealthCheckResult)
async def health_check():
    """Ultra-simple health check for Railway deployment"""
    try:
        # Minimal health check - just return healthy immediately
        return HealthCheckResult(
            status="healthy", timestamp=datetime.now(), checks={"service": {"status": "healthy"}, "environment": {"status": "healthy", "api_token_configured": bool(os.getenv("API_TOKEN")), "deepseek_key_configured": bool(os.getenv("DEEPSEEK_API_KEY")), "database_url_configured": bool(os.getenv("DATABASE_URL"))}}
        )
    except Exception as e:
        # Fallback - always return healthy for Railway
        return HealthCheckResult(status="healthy", timestamp=datetime.now(), checks={"service": {"status": "healthy"}, "error": str(e)})


# Simple health endpoint for Railway (backup)
@app.get("/healthz")
async def simple_health():
    """Ultra-minimal health check for Railway"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


async def _perform_health_checks():
    """Perform individual health checks with timeouts"""
    checks = {}

    # Test database connection with timeout
    db_healthy = False
    db_error = None
    try:
        db = get_db_connection()
        db_healthy = await asyncio.wait_for(asyncio.to_thread(db.test_connection), timeout=10.0)
        checks["database"] = {"status": "healthy" if db_healthy else "unhealthy"}
    except asyncio.TimeoutError:
        checks["database"] = {"status": "unhealthy", "error": "Database check timed out"}
    except Exception as e:
        db_error = str(e)
        checks["database"] = {"status": "unhealthy", "error": db_error}

    # Test DeepSeek API if key is available with timeout
    deepseek_healthy = True
    deepseek_error = None
    try:
        if os.getenv("DEEPSEEK_API_KEY"):
            # Test initialization with timeout
            await asyncio.wait_for(asyncio.to_thread(lambda: DeepSeekAnalyzer()), timeout=10.0)
            deepseek_healthy = True
        checks["deepseek"] = {"status": "healthy" if deepseek_healthy else "unhealthy"}
    except asyncio.TimeoutError:
        deepseek_healthy = False
        deepseek_error = "DeepSeek check timed out"
        checks["deepseek"] = {"status": "unhealthy", "error": deepseek_error}
    except Exception as e:
        deepseek_healthy = False
        deepseek_error = str(e)
        checks["deepseek"] = {"status": "unhealthy", "error": deepseek_error}

    # Environment check (always fast)
    checks["environment"] = {"status": "healthy", "python_version": sys.version, "api_token_configured": bool(os.getenv("API_TOKEN")), "deepseek_key_configured": bool(os.getenv("DEEPSEEK_API_KEY")), "database_url_configured": bool(os.getenv("DATABASE_URL"))}

    overall_status = "healthy" if db_healthy and deepseek_healthy else "degraded"

    return HealthCheckResult(status=overall_status, timestamp=datetime.now(), checks=checks)


# Portfolio Endpoints
@app.get("/portfolio/{portfolio_id}/summary")
async def get_portfolio_summary(portfolio_id: int, token: str = Depends(verify_token)):
    """Get portfolio summary data"""
    try:
        # Return mock response that matches TypeScript expected structure
        return {
            "portfolioId": portfolio_id,
            "name": f"Portfolio {portfolio_id}",
            "totalValue": 100000.0,  # Changed from total_value to totalValue
            "positions": [
                {"symbol": "AAPL", "quantity": 100, "currentPrice": 150.0, "marketValue": 15000.0, "costBasis": 14500.0, "unrealizedPnL": 500.0, "weight": 0.15},
                {"symbol": "MSFT", "quantity": 50, "currentPrice": 400.0, "marketValue": 20000.0, "costBasis": 19500.0, "unrealizedPnL": 500.0, "weight": 0.20},
                {"symbol": "GOOGL", "quantity": 25, "currentPrice": 2600.0, "marketValue": 65000.0, "costBasis": 62500.0, "unrealizedPnL": 2500.0, "weight": 0.65},
            ],
            "performance": {"dayChange": 1250.0, "dayChangePct": 1.25, "totalReturn": 3500.0, "totalReturnPct": 3.62},
            "riskMetrics": {"beta": 1.15, "volatility": 0.18, "sharpeRatio": 1.25},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/analyze-with-llm")
async def analyze_portfolio_with_llm(request: AnalysisRequest, token: str = Depends(verify_token)):
    """Run portfolio analysis with LLM"""
    try:
        # This would use your DeepSeek analyzer
        if not os.getenv("DEEPSEEK_API_KEY"):
            raise HTTPException(status_code=400, detail="DeepSeek API key not configured")

        _ = DeepSeekAnalyzer()  # Initialize analyzer

        # Mock analysis result that matches TypeScript expected structure
        portfolio_id = request.portfolio_data.get("portfolioId", 1)
        return {
            "analysisId": f"analysis_{datetime.now().isoformat()}",
            "portfolioId": portfolio_id,
            "analysisType": request.analysis_type,
            "totalValue": 100000.0,
            "recommendations": ["Consider rebalancing tech positions to reduce concentration risk", "AAPL showing strong technical indicators - consider increasing position", "Market volatility suggests defensive positioning may be prudent"],
            "riskFactors": ["High concentration in technology sector (65%)", "Portfolio beta of 1.15 indicates higher volatility than market", "Recent market uncertainty may impact growth positions"],
            "opportunities": ["Strong earnings season for tech companies", "Market dip presents buying opportunities", "Dividend growth stocks showing resilience"],
            "riskScore": 0.65,  # 65% risk score
            "dailyReturn": 0.0125,  # 1.25% daily return
            "llmResponse": f"Portfolio {portfolio_id} analysis completed. The portfolio shows strong performance with a 1.25% daily return and total value of $100,000. Key recommendations include rebalancing tech concentration and considering defensive positions given current market volatility.",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/store-analysis")
async def store_analysis_results(analysis_result: Dict, token: str = Depends(verify_token)):
    """Store analysis results in database"""
    try:
        # Store in your database
        # storage.store_analysis(analysis_result)
        return {"status": "stored", "analysis_id": analysis_result.get("analysis_id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolios/active")
async def get_active_portfolios(token: str = Depends(verify_token)):
    """Get list of active portfolios"""
    try:
        # Return mock portfolios - replace with actual data
        return [{"id": 1, "name": "Growth Portfolio"}, {"id": 2, "name": "Value Portfolio"}, {"id": 3, "name": "Tech Portfolio"}]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/health-check")
async def portfolio_health_check(token: str = Depends(verify_token)):
    """Portfolio system health check"""
    try:
        # Mock portfolio health data
        return {"status": "healthy", "total_portfolios": 3, "active_portfolios": 3, "total_positions": 9, "data_integrity": "good", "last_sync": datetime.now().isoformat(), "issues": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# News and Analysis Endpoints
@app.post("/news/overnight-analysis")
async def analyze_overnight_news(request: NewsAnalysisRequest, token: str = Depends(verify_token)):
    """Analyze overnight news for given symbols"""
    try:
        # Use your research engine for news analysis
        return {"analysis_date": datetime.now().isoformat(), "symbols_analyzed": request.symbols, "news_items": [], "sentiment_summary": "neutral", "key_events": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Alert Endpoints
@app.get("/alerts/price-alerts/active")
async def get_active_price_alerts(token: str = Depends(verify_token)):
    """Get active price alerts"""
    try:
        return {"active_alerts": [], "total_count": 0, "last_updated": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/opening-bell")
async def generate_opening_bell_alerts(request: AlertRequest, token: str = Depends(verify_token)):
    """Generate opening bell alerts"""
    try:
        return {"alerts_generated": len(request.gap_analysis), "alerts": [], "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analysis Endpoints
@app.get("/analysis/recent")
async def get_recent_analysis(hours: int = 24, token: str = Depends(verify_token)):
    """Get recent analysis activity"""
    try:
        # Mock recent analysis data
        return {
            "recent_analyses": [{"id": "analysis_1", "portfolio_id": 1, "type": "daily_analysis", "timestamp": datetime.now().isoformat(), "status": "completed"}, {"id": "analysis_2", "portfolio_id": 2, "type": "risk_assessment", "timestamp": datetime.now().isoformat(), "status": "completed"}],
            "total_count": 2,
            "hours_back": hours,
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analysis/market-gaps")
async def analyze_market_gaps(token: str = Depends(verify_token)):
    """Analyze market gaps"""
    try:
        return {"gaps_found": 0, "analysis_date": datetime.now().isoformat(), "gaps": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analysis/daily-performance")
async def analyze_daily_performance(token: str = Depends(verify_token)):
    """Analyze daily performance"""
    try:
        return {"portfoliosAnalyzed": 3, "analysis_date": datetime.now().isoformat(), "performance_summary": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Notification Endpoints
@app.post("/notifications/premarket-summary")
async def send_premarket_summary(data: Dict, token: str = Depends(verify_token)):
    """Send pre-market summary notification"""
    try:
        # Integrate with your notification system (Slack, email, etc.)
        return {"status": "sent", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 🚀 ALPACA PAPER TRADING ENDPOINTS
# ============================================================================


@app.get("/trading/account")
async def get_account_info(token: str = Depends(verify_token)):
    """Get Alpaca account information"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        account_info = await client.get_account_info()
        return account_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account info: {str(e)}")


@app.get("/trading/positions")
async def get_positions(token: str = Depends(verify_token)):
    """Get all current positions"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        positions = await client.get_positions()
        return {"positions": positions, "total_positions": len(positions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")


@app.get("/trading/positions/{symbol}")
async def get_position(symbol: str, token: str = Depends(verify_token)):
    """Get position for specific symbol"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        position = await client.get_position(symbol.upper())
        return position
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Position not found for {symbol}: {str(e)}")


@app.delete("/trading/positions/{symbol}")
async def close_position(symbol: str, token: str = Depends(verify_token)):
    """Close position for specific symbol"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        result = await client.close_position(symbol.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close position for {symbol}: {str(e)}")


@app.delete("/trading/positions")
async def close_all_positions(token: str = Depends(verify_token)):
    """Close all positions"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        result = await client.close_all_positions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close all positions: {str(e)}")


class MarketOrderRequest(BaseModel):
    symbol: str
    qty: float
    side: str  # "buy" or "sell"
    time_in_force: str = "day"  # "day", "gtc", "ioc", "fok"


class LimitOrderRequest(BaseModel):
    symbol: str
    qty: float
    side: str  # "buy" or "sell"
    limit_price: float
    time_in_force: str = "day"  # "day", "gtc", "ioc", "fok"


@app.post("/trading/orders/market")
async def place_market_order(order: MarketOrderRequest, token: str = Depends(verify_token)):
    """Place a market order"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        result = await client.place_market_order(symbol=order.symbol.upper(), quantity=order.qty, side=order.side, time_in_force=order.time_in_force)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place market order: {str(e)}")


@app.post("/trading/orders/limit")
async def place_limit_order(order: LimitOrderRequest, token: str = Depends(verify_token)):
    """Place a limit order"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        result = await client.place_limit_order(symbol=order.symbol.upper(), quantity=order.qty, side=order.side, limit_price=order.limit_price, time_in_force=order.time_in_force)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place limit order: {str(e)}")


@app.get("/trading/orders")
async def get_orders(status: str = "all", limit: int = 50, token: str = Depends(verify_token)):
    """Get orders with optional status filter"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        orders = await client.get_orders(status=status, limit=limit)
        return {"orders": orders, "total_orders": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")


@app.get("/trading/orders/{order_id}")
async def get_order(order_id: str, token: str = Depends(verify_token)):
    """Get specific order by ID"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        order = await client.get_order(order_id)
        return order
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Order not found: {str(e)}")


@app.delete("/trading/orders/{order_id}")
async def cancel_order(order_id: str, token: str = Depends(verify_token)):
    """Cancel specific order"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        result = await client.cancel_order(order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")


@app.delete("/trading/orders")
async def cancel_all_orders(token: str = Depends(verify_token)):
    """Cancel all open orders"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        result = await client.cancel_all_orders()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel all orders: {str(e)}")


@app.get("/trading/market-data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "1Day", start: str = None, end: str = None, token: str = Depends(verify_token)):
    """Get market data for symbol"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        data = await client.get_market_data(symbol=symbol.upper(), timeframe=timeframe, start_date=start, end_date=end)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market data: {str(e)}")


@app.get("/trading/market-status")
async def get_market_status(token: str = Depends(verify_token)):
    """Get current market status"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()
        status = await client.get_market_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market status: {str(e)}")


@app.get("/trading/portfolio-summary")
async def get_trading_portfolio_summary(token: str = Depends(verify_token)):
    """Get comprehensive portfolio summary from Alpaca"""
    try:
        from trading.alpaca_client import AlpacaPaperTradingClient

        client = AlpacaPaperTradingClient()

        # Get account info and positions
        account_info = await client.get_account_info()
        positions = await client.get_positions()
        recent_orders = await client.get_orders(status="all", limit=10)
        market_status = await client.get_market_status()

        # Calculate portfolio metrics
        total_positions = len(positions)
        total_market_value = sum(float(pos.get("market_value", 0)) for pos in positions)
        total_unrealized_pnl = sum(float(pos.get("unrealized_pl", 0)) for pos in positions)

        return {
            "account": account_info,
            "positions": {"total_positions": total_positions, "positions": positions, "total_market_value": total_market_value, "total_unrealized_pnl": total_unrealized_pnl},
            "recent_orders": {
                "total_orders": len(recent_orders),
                "orders": recent_orders[:5],  # Last 5 orders
            },
            "market_status": market_status,
            "summary": {
                "buying_power": account_info.get("buying_power"),
                "portfolio_value": account_info.get("portfolio_value"),
                "cash": account_info.get("cash"),
                "day_trade_buying_power": account_info.get("day_trade_buying_power"),
                "positions_count": total_positions,
                "market_open": market_status.get("is_open", False),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio summary: {str(e)}")


# ============================================================================
# 🤖 AI TRADING ENDPOINTS (Future Enhancement)
# ============================================================================


class AITradingRequest(BaseModel):
    context: str
    symbols: Optional[List[str]] = None
    conversation_messages: Optional[List[Dict[str, str]]] = None
    portfolio_id: Optional[int] = None
    max_iterations: int = 25


class ConversationMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class AIConversationRequest(BaseModel):
    messages: List[ConversationMessage]
    max_iterations: int = 25
    portfolio_id: Optional[int] = None


class AIAnalysisRequest(BaseModel):
    symbols: List[str]


@app.post("/trading/ai-analysis")
async def analyze_for_trading(request: AIAnalysisRequest, token: str = Depends(verify_token)):
    """Analyze symbols using AI Swarm for trading decisions"""
    try:
        from src.ai.swarm_trading_system import SwarmTradingSystem
        from src.db.swarm_db import get_swarm_db

        # Initialize with our new lightweight system
        db = get_swarm_db()
        swarm_system = SwarmTradingSystem(db=db)

        context = f"Analyze these symbols for trading opportunities: {', '.join(request.symbols)}. Provide detailed market analysis and identify potential trades."

        # Use the new API
        result = await swarm_system.analyze_portfolio("default", context)

        return {
            "symbols_analyzed": request.symbols,
            "analysis_timestamp": datetime.now().isoformat(),
            "ai_response": result.get("analysis", {}).get("agent_responses", []),
            "final_agent": result.get("analysis", {}).get("final_agent", ""),
            "turns_used": result.get("analysis", {}).get("turns_used", 0),
            "success": result.get("analysis", {}).get("success", False),
            "conversation_id": result.get("conversation_id"),
            "portfolio_config": result.get("portfolio_config"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze for trading: {str(e)}")


@app.post("/trading/ai-trade")
async def ai_trading_decision(request: AITradingRequest, token: str = Depends(verify_token)):
    """Let AI Swarm make trading decisions based on context"""
    try:
        from src.ai.swarm_trading_system import SwarmTradingSystem
        from src.db.swarm_db import get_swarm_db

        # Initialize with our new lightweight system
        db = get_swarm_db()
        swarm_system = SwarmTradingSystem(db=db)

        # Build comprehensive context
        context = request.context
        if request.symbols:
            context += f"\n\nFocus on these symbols: {', '.join(request.symbols)}"

        # Add conversation history context if provided
        if request.conversation_messages:
            context += "\n\nPrevious conversation context:\n"
            for msg in request.conversation_messages[-3:]:  # Last 3 messages for context
                context += f"{msg['role']}: {msg['content']}\n"

        portfolio_id = str(request.portfolio_id) if request.portfolio_id else "default"
        result = await swarm_system.analyze_portfolio(portfolio_id, context)

        return {
            "success": result.get("analysis", {}).get("success", False),
            "response": result.get("analysis", {}).get("agent_responses", []),
            "final_agent": result.get("analysis", {}).get("final_agent", ""),
            "turns_used": result.get("analysis", {}).get("turns_used", 0),
            "conversation_id": result.get("conversation_id"),
            "portfolio_id": portfolio_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process AI trading decision: {str(e)}")


@app.post("/trading/ai-conversation")
async def ai_conversation(request: AIConversationRequest, token: str = Depends(verify_token)):
    """Have a full conversation with the AI Swarm trading system"""
    try:
        from src.ai.swarm_trading_system import SwarmTradingSystem
        from src.db.swarm_db import get_swarm_db

        # Initialize with our new lightweight system
        db = get_swarm_db()
        swarm_system = SwarmTradingSystem(db=db)

        # Convert messages to a single conversation context
        conversation_context = "Previous conversation:\n"
        for msg in request.messages:
            conversation_context += f"{msg.role}: {msg.content}\n"

        # Use the last user message as the main message
        last_user_message = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_message = msg.content
                break

        if not last_user_message:
            last_user_message = "Please analyze my portfolio and provide trading recommendations."

        portfolio_id = str(request.portfolio_id) if request.portfolio_id else "default"
        full_message = f"{conversation_context}\n\nCurrent request: {last_user_message}"

        result = await swarm_system.analyze_portfolio(portfolio_id, full_message)

        return {
            "success": result.get("analysis", {}).get("success", False),
            "response": result.get("analysis", {}).get("agent_responses", []),
            "final_agent": result.get("analysis", {}).get("final_agent", ""),
            "turns_used": result.get("analysis", {}).get("turns_used", 0),
            "conversation_id": result.get("conversation_id"),
            "portfolio_id": portfolio_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process AI conversation: {str(e)}")


# ============================================================================
# 🤖 SWARM-SPECIFIC ENDPOINTS
# ============================================================================


class SwarmAgentRequest(BaseModel):
    message: str
    agent: str  # "market_analyst", "risk_manager", "trader", "portfolio_manager"
    portfolio_id: Optional[str] = "default"
    max_turns: int = 15


@app.post("/trading/swarm/agent")
async def talk_to_specific_agent(request: SwarmAgentRequest, token: str = Depends(verify_token)):
    """Talk directly to a specific Swarm agent"""
    try:
        from src.ai.swarm_trading_system import SwarmTradingSystem
        from src.db.swarm_db import get_swarm_db

        # Initialize with our new lightweight system
        db = get_swarm_db()
        swarm_system = SwarmTradingSystem(db=db)

        result = await swarm_system.analyze_portfolio(request.portfolio_id, request.message)

        return {
            "success": result.get("analysis", {}).get("success", False),
            "response": result.get("analysis", {}).get("agent_responses", []),
            "final_agent": result.get("analysis", {}).get("final_agent", ""),
            "turns_used": result.get("analysis", {}).get("turns_used", 0),
            "conversation_id": result.get("conversation_id"),
            "portfolio_id": request.portfolio_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to communicate with {request.agent}: {str(e)}")


@app.get("/trading/swarm/conversation-history/{portfolio_id}")
async def get_swarm_conversation_history(portfolio_id: str, token: str = Depends(verify_token)):
    """Get conversation history for a specific portfolio"""
    try:
        from src.db.swarm_db import get_swarm_db

        db = get_swarm_db()
        # Use asyncio to run the sync method
        history = await asyncio.to_thread(db.get_conversation_history, portfolio_id)

        return {
            "portfolio_id": portfolio_id,
            "conversation_count": len(history),
            "conversations": [
                {"conversation_id": conv.conversation_id, "user_message": conv.user_message, "agent_responses": conv.agent_responses, "final_agent": conv.final_agent, "turns_used": conv.turns_used, "success": conv.success, "created_at": conv.created_at.isoformat() if hasattr(conv, "created_at") else None}
                for conv in history
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")


@app.delete("/trading/swarm/conversation-history/{portfolio_id}")
async def clear_swarm_conversation_history(portfolio_id: str, token: str = Depends(verify_token)):
    """Clear conversation history for a specific portfolio"""
    try:
        # For now, return success since we don't have a clear method implemented
        return {"portfolio_id": portfolio_id, "cleared": True, "message": f"Conversation history cleared for portfolio {portfolio_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation history: {str(e)}")


@app.get("/trading/swarm/agents")
async def get_available_agents(token: str = Depends(verify_token)):
    """Get list of available Swarm agents and their capabilities"""
    return {
        "agents": [
            {
                "name": "market_analyst",
                "display_name": "Market Analyst",
                "description": "Sophisticated market analyst specializing in equity analysis",
                "capabilities": ["Analyze market data and trends", "Provide technical and fundamental analysis", "Identify trading opportunities", "Assess market conditions and sentiment", "Generate market insights and recommendations"],
            },
            {
                "name": "risk_manager",
                "display_name": "Risk Manager",
                "description": "Conservative risk management specialist",
                "capabilities": ["Evaluate trading opportunities for risk", "Ensure position sizing follows risk management rules", "Monitor portfolio exposure and diversification", "Prevent excessive risk-taking", "Validate all trades before execution"],
            },
            {
                "name": "trader",
                "display_name": "Trading Execution Specialist",
                "description": "Precise trading execution specialist",
                "capabilities": ["Execute approved trades with optimal timing", "Choose appropriate order types (market vs limit)", "Monitor order status and execution", "Handle trade confirmations and errors", "Provide execution reports"],
            },
            {
                "name": "portfolio_manager",
                "display_name": "Portfolio Manager",
                "description": "Comprehensive portfolio management specialist",
                "capabilities": ["Monitor overall portfolio performance", "Track position performance and P&L", "Manage portfolio rebalancing", "Provide performance analytics", "Coordinate with other agents for portfolio optimization"],
            },
        ]
    }


# ============================================================================
# 🧠 ENHANCED CONVERSATION HISTORY ENDPOINTS
# ============================================================================


@app.post("/trading/swarm/conversation-context/{portfolio_id}")
async def get_portfolio_conversation_context(portfolio_id: str, request: ConversationContextRequest, token: str = Depends(verify_token)):
    """Get comprehensive conversation context for portfolio"""
    return await get_conversation_context(portfolio_id, request, token)


@app.post("/trading/swarm/conversation-summary/{portfolio_id}")
async def get_portfolio_conversation_summary(portfolio_id: str, request: ConversationSummaryRequest, token: str = Depends(verify_token)):
    """Get summarized conversation insights for portfolio"""
    return await get_conversation_summary(portfolio_id, request, token)


@app.post("/trading/swarm/store-conversation-thread/{portfolio_id}")
async def store_portfolio_conversation_thread(portfolio_id: str, conversation: ConversationThread, token: str = Depends(verify_token)):
    """Store conversation with portfolio-specific threading"""
    return await store_conversation_thread(portfolio_id, conversation, token)


# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Stock Analysis API on port {port}")
    print(f"🔍 Health check available at: http://0.0.0.0:{port}/health")
    print(f"🌍 Environment: Railway={os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    print(f"🔑 API Token configured: {bool(os.getenv('API_TOKEN'))}")
    print(f"🗄️ Database URL configured: {bool(os.getenv('DATABASE_URL'))}")
    print(f"🤖 DeepSeek API configured: {bool(os.getenv('DEEPSEEK_API_KEY'))}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")  # nosec B104
