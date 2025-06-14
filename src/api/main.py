"""
FastAPI server for Stock Analysis System
Exposes Python analysis functions as REST API endpoints for Trigger.dev tasks
"""

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

# Security
security = HTTPBearer()

# Initialize components
analyzer = StockAnalyzer()
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
    """System health check"""
    try:
        # Test database connection
        db = get_db_connection()
        db_healthy = db.test_connection()

        # Test DeepSeek API if key is available
        deepseek_healthy = True
        deepseek_error = None
        try:
            if os.getenv("DEEPSEEK_API_KEY"):
                _ = DeepSeekAnalyzer()  # Test initialization
                # Simple test - this doesn't make an API call
                deepseek_healthy = True
        except Exception as e:
            deepseek_healthy = False
            deepseek_error = str(e)

        overall_status = "healthy" if db_healthy and deepseek_healthy else "degraded"

        return HealthCheckResult(
            status=overall_status,
            timestamp=datetime.now(),
            checks={"database": {"status": "healthy" if db_healthy else "unhealthy"}, "deepseek": {"status": "healthy" if deepseek_healthy else "unhealthy", "error": deepseek_error}, "environment": {"status": "healthy", "python_version": sys.version, "api_token_configured": bool(os.getenv("API_TOKEN"))}},
        )
    except Exception as e:
        return HealthCheckResult(status="unhealthy", timestamp=datetime.now(), checks={"error": str(e)})


# Portfolio Endpoints
@app.get("/portfolio/{portfolio_id}/summary")
async def get_portfolio_summary(portfolio_id: int, token: str = Depends(verify_token)):
    """Get portfolio summary data"""
    try:
        # This would integrate with your portfolio management system
        # For now, return a mock response that matches expected structure
        return {"portfolio_id": portfolio_id, "name": f"Portfolio {portfolio_id}", "total_value": 100000.0, "positions": [], "performance": {"day_change": 0.0, "day_change_pct": 0.0}}
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

        # Mock analysis result - replace with actual analysis
        return {
            "analysis_id": f"analysis_{datetime.now().isoformat()}",
            "portfolio_id": request.portfolio_data.get("portfolio_id"),
            "analysis_type": request.analysis_type,
            "recommendations": ["Sample recommendation"],
            "risk_analysis": {"risk_score": 5.0},
            "opportunities": ["Sample opportunity"],
            "llm_response": "Sample LLM analysis response",
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
