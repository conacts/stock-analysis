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
    """System health check with 30-second timeout"""
    try:
        # Run health checks with timeout
        return await asyncio.wait_for(_perform_health_checks(), timeout=30.0)
    except asyncio.TimeoutError:
        return HealthCheckResult(status="unhealthy", timestamp=datetime.now(), checks={"error": "Health check timed out after 30 seconds"})
    except Exception as e:
        return HealthCheckResult(status="unhealthy", timestamp=datetime.now(), checks={"error": str(e)})


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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Stock Analysis API on port {port}")
    print(f"🔍 Health check available at: http://0.0.0.0:{port}/health")
    print(f"🌍 Environment: Railway={os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    print(f"🔑 API Token configured: {bool(os.getenv('API_TOKEN'))}")
    print(f"🗄️ Database URL configured: {bool(os.getenv('DATABASE_URL'))}")
    print(f"🤖 DeepSeek API configured: {bool(os.getenv('DEEPSEEK_API_KEY'))}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")  # nosec B104
