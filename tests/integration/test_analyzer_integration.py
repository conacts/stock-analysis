"""
Integration tests for StockAnalyzer with real-world scenarios
"""

from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

from core.analyzer import StockAnalyzer


@pytest.mark.integration
class TestStockAnalyzerIntegration:
    """Integration tests for complete analysis workflow"""

    @patch("yfinance.Ticker")
    def test_full_analysis_workflow_traditional(
        self, mock_ticker_class, mock_yfinance_ticker
    ):
        """Test complete analysis workflow in traditional mode"""
        mock_ticker_class.return_value = mock_yfinance_ticker

        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer.analyze_stock("NVDA")

        # Verify complete result structure
        assert result is not None
        assert result["symbol"] == "NVDA"

        # Check all main sections exist
        required_sections = [
            "fundamentals",
            "technical",
            "sentiment",
            "risk",
            "score",
            "recommendation",
        ]
        for section in required_sections:
            assert section in result

        # Check fundamentals section
        fundamentals = result["fundamentals"]
        assert "company_name" in fundamentals
        assert "sector" in fundamentals
        assert "fundamental_score" in fundamentals
        assert 0 <= fundamentals["fundamental_score"] <= 100

        # Check technical section
        technical = result["technical"]
        assert "technical_score" in technical
        assert "indicators" in technical
        assert 0 <= technical["technical_score"] <= 100

        # Check sentiment section
        sentiment = result["sentiment"]
        assert "sentiment_score" in sentiment
        assert "overall_sentiment" in sentiment
        assert -5 <= sentiment["sentiment_score"] <= 5

        # Check risk section
        risk = result["risk"]
        assert "risk_score" in risk
        assert "risk_level" in risk
        assert 0 <= risk["risk_score"] <= 10

        # Check score section
        score = result["score"]
        assert "composite_score" in score
        assert "weights" in score
        assert 0 <= score["composite_score"] <= 100

        # Check recommendation section
        recommendation = result["recommendation"]
        assert "rating" in recommendation
        assert "confidence" in recommendation
        assert "suggested_allocation" in recommendation
        assert recommendation["rating"] in [
            "Strong Sell",
            "Sell",
            "Hold",
            "Buy",
            "Strong Buy",
        ]

    @patch("yfinance.Ticker")
    def test_full_analysis_workflow_llm_enhanced(
        self, mock_ticker_class, mock_yfinance_ticker, mock_llm_scorer
    ):
        """Test complete analysis workflow with LLM enhancement"""
        mock_ticker_class.return_value = mock_yfinance_ticker

        analyzer = StockAnalyzer(enable_llm=False)
        analyzer.llm_scorer = mock_llm_scorer

        result = analyzer.analyze_stock("NVDA")

        # Verify LLM-enhanced result structure
        assert result is not None
        assert result["symbol"] == "NVDA"

        # Should have enhanced score section
        score = result["score"]
        assert score["analysis_method"] == "llm_enhanced"
        assert "llm_analysis" in score
        assert "news_impact" in score
        assert "growth_catalysts" in score

        # Verify LLM analysis components
        llm_analysis = score["llm_analysis"]
        assert "investment_thesis" in llm_analysis
        assert "key_strengths" in llm_analysis
        assert "key_risks" in llm_analysis

        news_impact = score["news_impact"]
        assert "sentiment" in news_impact
        assert "key_catalysts" in news_impact

        growth_catalysts = score["growth_catalysts"]
        assert "catalysts" in growth_catalysts
        assert "conviction" in growth_catalysts

    @patch("yfinance.Ticker")
    def test_analysis_with_different_sectors(self, mock_ticker_class):
        """Test analysis across different sectors"""
        analyzer = StockAnalyzer(enable_llm=False)

        # Test different sector configurations
        sectors = [
            "Technology",
            "Healthcare",
            "Financial Services",
            "Energy",
            "Unknown Sector",
        ]

        for sector in sectors:
            # Create mock ticker for each sector
            mock_ticker = Mock()
            mock_ticker.info = {
                "longName": f"{sector} Company Inc.",
                "sector": sector,
                "industry": f"{sector} Industry",
                "marketCap": 1000000000000,
                "currentPrice": 150.0,
                "trailingPE": 25.0,
                "returnOnEquity": 0.20,
                "revenueGrowth": 0.15,
                "debtToEquity": 0.30,
                "currentRatio": 2.0,
            }

            # Mock historical data
            dates = pd.date_range(start="2024-01-01", end="2024-06-01", freq="D")
            prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.02)
            mock_ticker.history.return_value = pd.DataFrame(
                {
                    "Close": prices,
                    "Volume": np.random.randint(1000000, 10000000, len(dates)),
                },
                index=dates,
            )

            mock_ticker.news = []
            mock_ticker_class.return_value = mock_ticker

            result = analyzer.analyze_stock("TEST")

            # Verify sector-specific analysis
            assert result is not None
            fundamentals = result["fundamentals"]
            assert fundamentals["sector"] == sector

            # Check that appropriate benchmarks were used
            if sector in analyzer.sector_benchmarks:
                assert (
                    fundamentals["sector_benchmarks"]
                    == analyzer.sector_benchmarks[sector]
                )
            else:
                # Should fallback to Technology
                assert (
                    fundamentals["sector_benchmarks"]
                    == analyzer.sector_benchmarks["Technology"]
                )

    @patch("yfinance.Ticker")
    def test_analysis_with_extreme_values(self, mock_ticker_class):
        """Test analysis with extreme financial values"""
        analyzer = StockAnalyzer(enable_llm=False)

        # Test with extremely high valuations
        high_valuation_ticker = Mock()
        high_valuation_ticker.info = {
            "longName": "High Valuation Corp",
            "sector": "Technology",
            "marketCap": 5000000000000,  # $5T market cap
            "currentPrice": 1000.0,
            "trailingPE": 100.0,  # Very high PE
            "priceToBook": 20.0,  # Very high P/B
            "returnOnEquity": 0.50,  # Very high ROE
            "revenueGrowth": 1.0,  # 100% growth
            "debtToEquity": 0.0,  # No debt
            "currentRatio": 10.0,  # Very high liquidity
        }

        dates = pd.date_range(start="2024-01-01", end="2024-06-01", freq="D")
        high_valuation_ticker.history.return_value = pd.DataFrame(
            {
                "Close": np.linspace(500, 1000, len(dates)),  # Strong uptrend
                "Volume": np.random.randint(1000000, 10000000, len(dates)),
            },
            index=dates,
        )

        high_valuation_ticker.news = []
        mock_ticker_class.return_value = high_valuation_ticker

        result = analyzer.analyze_stock("HIGH")

        # Should handle extreme values gracefully
        assert result is not None
        assert 0 <= result["score"]["composite_score"] <= 100

        # Test with distressed company
        distressed_ticker = Mock()
        distressed_ticker.info = {
            "longName": "Distressed Corp",
            "sector": "Energy",
            "marketCap": 100000000,  # Small market cap
            "currentPrice": 5.0,
            "trailingPE": -1,  # Negative earnings
            "returnOnEquity": -0.30,  # Negative ROE
            "revenueGrowth": -0.50,  # Declining revenue
            "debtToEquity": 5.0,  # Very high debt
            "currentRatio": 0.5,  # Poor liquidity
        }

        distressed_ticker.history.return_value = pd.DataFrame(
            {
                "Close": np.linspace(20, 5, len(dates)),  # Strong downtrend
                "Volume": np.random.randint(100000, 1000000, len(dates)),
            },
            index=dates,
        )

        distressed_ticker.news = []
        mock_ticker_class.return_value = distressed_ticker

        result = analyzer.analyze_stock("DIST")

        # Should handle distressed company
        assert result is not None
        assert result["score"]["composite_score"] < 50  # Should be low score
        assert result["recommendation"]["rating"] in ["Sell", "Strong Sell", "Avoid"]

    @patch("yfinance.Ticker")
    def test_analysis_error_recovery(self, mock_ticker_class):
        """Test error recovery in analysis workflow"""
        analyzer = StockAnalyzer(enable_llm=False)

        # Test with ticker that has partial data
        partial_ticker = Mock()
        partial_ticker.info = {
            "longName": "Partial Data Corp",
            "sector": "Technology",
            "currentPrice": 100.0,
            # Missing many fields
        }

        # Empty history
        partial_ticker.history.return_value = pd.DataFrame()
        partial_ticker.news = []
        mock_ticker_class.return_value = partial_ticker

        result = analyzer.analyze_stock("PARTIAL")

        # Should still produce a result with defaults
        assert result is not None
        assert result["technical"]["technical_score"] == 50  # Default score
        assert result["sentiment"]["sentiment_score"] == 0  # Neutral

    @patch("yfinance.Ticker")
    def test_concurrent_analysis(self, mock_ticker_class, mock_yfinance_ticker):
        """Test multiple concurrent analyses"""
        mock_ticker_class.return_value = mock_yfinance_ticker

        analyzer = StockAnalyzer(enable_llm=False)

        # Simulate analyzing multiple stocks
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
        results = []

        for symbol in symbols:
            result = analyzer.analyze_stock(symbol)
            results.append(result)

        # All analyses should succeed
        assert len(results) == 5
        assert all(result is not None for result in results)

        # Each should have correct symbol
        for i, result in enumerate(results):
            assert result["symbol"] == symbols[i]

    @patch("yfinance.Ticker")
    def test_performance_benchmarking(self, mock_ticker_class, mock_yfinance_ticker):
        """Test analysis performance with timing"""
        import time

        mock_ticker_class.return_value = mock_yfinance_ticker
        analyzer = StockAnalyzer(enable_llm=False)

        # Time a single analysis
        start_time = time.time()
        result = analyzer.analyze_stock("PERF")
        end_time = time.time()

        analysis_time = end_time - start_time

        # Analysis should complete reasonably quickly (< 5 seconds for mocked data)
        assert analysis_time < 5.0
        assert result is not None

        # Verify all components were calculated
        assert "fundamentals" in result
        assert "technical" in result
        assert "sentiment" in result
        assert "risk" in result
        assert "score" in result
        assert "recommendation" in result


@pytest.mark.integration
@pytest.mark.slow
class TestRealDataIntegration:
    """Integration tests that could use real data (marked as slow)"""

    @pytest.mark.skip(reason="Requires real network access")
    def test_real_stock_analysis(self):
        """Test analysis with real stock data (skipped by default)"""
        # This test would use real yfinance data
        # Only run when specifically testing with real data
        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer.analyze_stock("AAPL")

        assert result is not None
        assert result["symbol"] == "AAPL"
        assert result["fundamentals"]["company_name"] == "Apple Inc."

    @pytest.mark.skip(reason="Requires LLM API access and costs money")
    @pytest.mark.llm
    def test_real_llm_analysis(self):
        """Test analysis with real LLM API (skipped by default)"""
        # This test would use real DeepSeek API
        # Only run when specifically testing LLM integration
        import os

        if not os.getenv("DEEPSEEK_API_KEY"):
            pytest.skip("No DeepSeek API key available")

        analyzer = StockAnalyzer(enable_llm=True)
        result = analyzer.analyze_stock("NVDA")

        assert result is not None
        assert result["score"]["analysis_method"] == "llm_enhanced"
