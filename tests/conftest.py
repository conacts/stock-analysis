"""
Pytest configuration and shared fixtures
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test environment setup
os.environ["TESTING"] = "1"
# Always use in-memory SQLite for tests - fast, reliable, and sufficient
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_yfinance_ticker():
    """Mock yfinance Ticker object with sample data"""
    mock_ticker = Mock()

    # Sample stock info
    mock_ticker.info = {
        "longName": "Test Company Inc.",
        "sector": "Technology",
        "industry": "Software",
        "marketCap": 1000000000000,
        "currentPrice": 150.0,
        "trailingPE": 25.0,
        "forwardPE": 22.0,
        "pegRatio": 1.5,
        "priceToSalesTrailing12Months": 8.0,
        "priceToBook": 5.0,
        "enterpriseToEbitda": 20.0,
        "profitMargins": 0.25,
        "operatingMargins": 0.30,
        "grossMargins": 0.60,
        "returnOnEquity": 0.20,
        "returnOnAssets": 0.15,
        "revenueGrowth": 0.15,
        "earningsGrowth": 0.20,
        "debtToEquity": 0.30,
        "currentRatio": 2.0,
        "quickRatio": 1.5,
        "totalCashPerShare": 10.0,
        "freeCashflow": 5000000000,
        "dividendYield": 0.02,
        "beta": 1.2,
        "targetMeanPrice": 180.0,
        "numberOfAnalystOpinions": 15,
        "recommendationMean": 2.0,
    }

    # Sample historical data
    import numpy as np
    import pandas as pd

    dates = pd.date_range(start="2024-01-01", end="2024-06-01", freq="D")
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
    volumes = np.random.randint(1000000, 10000000, len(dates))

    mock_ticker.history.return_value = pd.DataFrame({"Close": prices, "Volume": volumes}, index=dates)

    # Sample news
    mock_ticker.news = [
        {
            "title": "Company Reports Strong Q1 Results",
            "summary": "Revenue up 15% year-over-year with strong margins",
            "providerPublishTime": "2024-05-01",
        },
        {
            "title": "New Product Launch Expected",
            "summary": "Company announces innovative product for Q3 launch",
            "providerPublishTime": "2024-05-15",
        },
    ]

    return mock_ticker


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing"""
    return {
        "market_cap": 1000000000000,
        "pe_ratio": 25.0,
        "revenue_growth": 0.15,
        "profit_margin": 0.25,
        "roe": 0.20,
        "debt_to_equity": 0.30,
        "current_ratio": 2.0,
        "price_to_book": 5.0,
    }


@pytest.fixture
def sample_news_data():
    """Sample news data for testing"""
    return [
        {
            "title": "Company Reports Strong Q1 Results",
            "summary": "Revenue up 15% year-over-year with strong margins",
            "date": "2024-05-01",
        },
        {
            "title": "New Product Launch Expected",
            "summary": "Company announces innovative product for Q3 launch",
            "date": "2024-05-15",
        },
    ]


@pytest.fixture
def sample_technical_data():
    """Sample technical data for testing"""
    return {
        "trend": "upward",
        "rsi": 65,
        "ma_position": "above",
        "volume_trend": "increasing",
        "support_resistance": "strong_support_at_140",
    }


@pytest.fixture
def sample_market_context():
    """Sample market context for testing"""
    return {
        "market_trend": "bullish",
        "sector_performance": "outperforming",
        "vix": "low",
        "interest_rates": "stable",
    }


@pytest.fixture
def mock_deepseek_response():
    """Mock DeepSeek API response"""
    return {
        "overall_score": 78,
        "confidence": 85,
        "investment_thesis": "Strong fundamentals with AI growth catalysts",
        "key_strengths": [
            "Market-leading position",
            "Strong revenue growth",
            "Expanding market opportunity",
        ],
        "key_risks": [
            "High valuation multiples",
            "Regulatory concerns",
            "Competition intensifying",
        ],
        "time_horizon": "medium",
        "position_size": 5.5,
        "catalyst_timeline": "6-12 months",
        "risk_adjusted_score": 74,
    }


@pytest.fixture
def mock_llm_scorer(mock_deepseek_response):
    """Mock LLM scorer for testing"""
    mock_scorer = Mock()
    mock_scorer.llm_enabled = True
    mock_scorer.weights = {
        "fundamentals": 0.40,
        "technical": 0.20,
        "llm_analysis": 0.30,
        "risk": 0.10,
    }

    mock_scorer.calculate_enhanced_score.return_value = {
        "composite_score": 75.5,
        "risk_adjusted_score": 72.0,
        "rating": "Buy",
        "confidence": 85,
        "component_scores": {
            "fundamental": 80.0,
            "technical": 70.0,
            "llm_analysis": 78.0,
            "risk": 85.0,
        },
        "weights_used": mock_scorer.weights,
        "llm_analysis": mock_deepseek_response,
        "news_impact": {
            "impact_score": 75,
            "sentiment": "positive",
            "key_catalysts": ["Strong earnings", "Product launch"],
            "risk_factors": ["Market volatility"],
        },
        "growth_catalysts": {
            "catalysts": [
                {
                    "catalyst": "AI market expansion",
                    "impact_potential": "high",
                    "timeline": "12-18 months",
                    "probability": 80,
                }
            ],
            "conviction": "high",
            "thesis_strength": 85,
        },
        "analysis_method": "llm_enhanced",
    }

    return mock_scorer


@pytest.fixture
def mock_database():
    """Mock database for testing"""
    mock_db = Mock()
    mock_db.store_daily_analysis.return_value = True
    mock_db.get_daily_decisions.return_value = []
    mock_db.get_performance_summary.return_value = {
        "total_positions": 5,
        "average_return": 12.5,
        "total_return": 62.5,
        "active_positions": [],
    }
    return mock_db


# Skip markers for different test types
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "llm: mark test as requiring LLM API")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "database: mark test as requiring database")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add unit marker to all tests by default
        if not any(marker.name in ["integration", "llm", "slow", "database"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)

        # Add markers based on test file names
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "llm" in item.nodeid:
            item.add_marker(pytest.mark.llm)
        if "database" in item.nodeid:
            item.add_marker(pytest.mark.database)
