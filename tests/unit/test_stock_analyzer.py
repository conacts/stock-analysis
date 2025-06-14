"""
Unit tests for StockAnalyzer class
"""

from unittest.mock import Mock, patch

import pandas as pd

from core.analyzer import StockAnalyzer


class TestStockAnalyzer:
    """Test cases for StockAnalyzer class"""

    def test_init_traditional_mode(self):
        """Test initialization in traditional mode"""
        analyzer = StockAnalyzer(enable_llm=False)

        assert analyzer.llm_scorer is None
        assert len(analyzer.sector_benchmarks) == 11
        assert "Technology" in analyzer.sector_benchmarks

    def test_init_llm_mode_without_api_key(self):
        """Test initialization with LLM enabled but no API key"""
        with patch.dict("os.environ", {}, clear=True):
            analyzer = StockAnalyzer(enable_llm=True)
            # Should fall back to traditional mode
            assert analyzer.llm_scorer is None

    @patch("yfinance.Ticker")
    def test_analyze_stock_success(self, mock_ticker_class, mock_yfinance_ticker):
        """Test successful stock analysis"""
        mock_ticker_class.return_value = mock_yfinance_ticker

        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer.analyze_stock("TEST")

        assert result is not None
        assert result["symbol"] == "TEST"
        assert "fundamentals" in result
        assert "technical" in result
        assert "sentiment" in result
        assert "risk" in result
        assert "score" in result
        assert "recommendation" in result
        assert "timestamp" in result

    @patch("yfinance.Ticker")
    def test_analyze_stock_invalid_ticker(self, mock_ticker_class):
        """Test analysis with invalid ticker"""
        mock_ticker = Mock()
        mock_ticker.info = {}  # Empty info indicates invalid ticker
        mock_ticker_class.return_value = mock_ticker

        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer.analyze_stock("INVALID")

        assert result is None

    def test_analyze_fundamentals(self, mock_yfinance_ticker):
        """Test fundamental analysis"""
        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer._analyze_fundamentals(mock_yfinance_ticker.info, "TEST")

        assert result["company_name"] == "Test Company Inc."
        assert result["sector"] == "Technology"
        assert result["market_cap"] == 1000000000000
        assert result["current_price"] == 150.0
        assert result["pe_ratio"] == 25.0
        assert "fundamental_score" in result
        assert 0 <= result["fundamental_score"] <= 100

    def test_analyze_technical(self, mock_yfinance_ticker):
        """Test technical analysis"""
        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer._analyze_technical(mock_yfinance_ticker, "TEST")

        assert "technical_score" in result
        assert "indicators" in result
        assert 0 <= result["technical_score"] <= 100

        indicators = result["indicators"]
        assert "current_price" in indicators
        assert "ma_20" in indicators
        assert "ma_50" in indicators
        assert "momentum_1m" in indicators
        assert "volatility" in indicators

    def test_analyze_sentiment(self, mock_yfinance_ticker):
        """Test sentiment analysis"""
        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer._analyze_sentiment(
            mock_yfinance_ticker, mock_yfinance_ticker.info, "TEST"
        )

        assert "sentiment_score" in result
        assert "overall_sentiment" in result
        assert "news_count" in result
        assert -5 <= result["sentiment_score"] <= 5

    def test_assess_risk(self, mock_yfinance_ticker):
        """Test risk assessment"""
        analyzer = StockAnalyzer(enable_llm=False)
        sentiment_data = {"sentiment_score": 2, "overall_sentiment": "Positive"}

        result = analyzer._assess_risk(mock_yfinance_ticker.info, sentiment_data)

        assert "risk_score" in result
        assert "risk_level" in result
        assert "identified_risks" in result
        assert 0 <= result["risk_score"] <= 10
        assert result["risk_level"] in ["Low", "Medium", "High"]

    def test_score_fundamentals(self):
        """Test fundamental scoring"""
        analyzer = StockAnalyzer(enable_llm=False)

        # Good metrics
        good_metrics = {
            "pe_ratio": 20,  # Below benchmark
            "roe": 0.25,  # Above benchmark
            "revenue_growth": 0.25,  # Strong growth
            "debt_to_equity": 0.2,  # Low debt
            "current_ratio": 2.5,  # Good liquidity
        }

        benchmarks = analyzer.sector_benchmarks["Technology"]
        score = analyzer._score_fundamentals(good_metrics, benchmarks)

        assert 70 <= score <= 100  # Should be high score

        # Poor metrics
        poor_metrics = {
            "pe_ratio": 50,  # High PE
            "roe": 0.05,  # Low ROE
            "revenue_growth": -0.1,  # Negative growth
            "debt_to_equity": 1.0,  # High debt
            "current_ratio": 0.8,  # Poor liquidity
        }

        score = analyzer._score_fundamentals(poor_metrics, benchmarks)
        assert 0 <= score <= 30  # Should be low score

    def test_score_technical(self):
        """Test technical scoring"""
        analyzer = StockAnalyzer(enable_llm=False)

        # Bullish indicators
        bullish_indicators = {
            "price_vs_ma20": 0.10,  # 10% above MA20
            "price_vs_ma50": 0.08,  # 8% above MA50
            "momentum_1m": 0.15,  # Strong momentum
            "volume_ratio": 2.0,  # High volume
        }

        score = analyzer._score_technical(bullish_indicators)
        assert 70 <= score <= 100

        # Bearish indicators
        bearish_indicators = {
            "price_vs_ma20": -0.10,  # 10% below MA20
            "price_vs_ma50": -0.08,  # 8% below MA50
            "momentum_1m": -0.15,  # Negative momentum
            "volume_ratio": 0.3,  # Low volume
        }

        score = analyzer._score_technical(bearish_indicators)
        assert 0 <= score <= 40  # Adjusted range for bearish indicators

    def test_calculate_composite_score(self):
        """Test composite score calculation"""
        analyzer = StockAnalyzer(enable_llm=False)

        fundamentals = {"fundamental_score": 80}
        technical = {"technical_score": 70}
        sentiment = {"sentiment_score": 2}  # Positive
        risk = {"risk_score": 3}  # Medium risk

        result = analyzer._calculate_composite_score(
            fundamentals, technical, sentiment, risk
        )

        assert "composite_score" in result
        assert "fundamental_score" in result
        assert "technical_score" in result
        assert "sentiment_score" in result
        assert "risk_score" in result
        assert "weights" in result

        # Check score is reasonable
        assert 50 <= result["composite_score"] <= 90

        # Check weights sum to 1
        weights = result["weights"]
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_generate_recommendation_strong_buy(self):
        """Test recommendation generation for strong buy"""
        analyzer = StockAnalyzer(enable_llm=False)

        # High scores across the board
        fundamentals = {
            "fundamental_score": 90,
            "revenue_growth": 0.4,
            "num_analysts": 15,
        }
        technical = {"technical_score": 85, "indicators": {"volatility": 0.2}}
        sentiment = {"sentiment_score": 3, "overall_sentiment": "Very Positive"}
        risk = {"risk_score": 2, "identified_risks": ["Market volatility"]}
        score = {"composite_score": 85}

        result = analyzer._generate_recommendation(
            fundamentals, technical, sentiment, risk, score
        )

        assert result["rating"] == "Strong Buy"
        assert result["confidence"] == "High"
        assert "8-10%" in result["suggested_allocation"]
        assert result["time_horizon"] == "6-18 months"  # High growth

    def test_generate_recommendation_sell(self):
        """Test recommendation generation for sell"""
        analyzer = StockAnalyzer(enable_llm=False)

        # Low scores
        fundamentals = {
            "fundamental_score": 20,
            "revenue_growth": -0.1,
            "num_analysts": 5,
        }
        technical = {"technical_score": 25, "indicators": {"volatility": 0.5}}
        sentiment = {"sentiment_score": -3, "overall_sentiment": "Very Negative"}
        risk = {"risk_score": 8, "identified_risks": ["High debt", "Declining margins"]}
        score = {"composite_score": 25}

        result = analyzer._generate_recommendation(
            fundamentals, technical, sentiment, risk, score
        )

        assert result["rating"] == "Sell"
        assert "0%" in result["suggested_allocation"]

    def test_identify_strengths(self):
        """Test strength identification"""
        analyzer = StockAnalyzer(enable_llm=False)

        fundamentals = {
            "roe": 0.25,  # High ROE
            "profit_margin": 0.20,  # High margins
            "revenue_growth": 0.20,  # Strong growth
        }
        technical = {"indicators": {"momentum_1m": 0.10}}  # Positive momentum
        sentiment = {"overall_sentiment": "Very Positive"}

        strengths = analyzer._identify_strengths(fundamentals, technical, sentiment)

        assert len(strengths) <= 5
        assert any("ROE" in strength for strength in strengths)
        assert any("margin" in strength for strength in strengths)
        assert any("growth" in strength for strength in strengths)

    def test_enhanced_scoring_with_llm(self, mock_llm_scorer, mock_yfinance_ticker):
        """Test enhanced scoring with LLM"""
        with patch("core.analyzer.LLM_AVAILABLE", True):
            analyzer = StockAnalyzer(enable_llm=False)  # Start with traditional
            analyzer.llm_scorer = mock_llm_scorer  # Manually set the scorer

            # Mock the required data
            fundamentals = {"fundamental_score": 80, "market_cap": 1000000000}
            technical = {"technical_score": 70, "indicators": {}}
            sentiment = {"sentiment_score": 2}
            risk = {"risk_score": 3}

            result = analyzer._calculate_enhanced_score(
                "TEST",
                fundamentals,
                technical,
                sentiment,
                risk,
                mock_yfinance_ticker.info,
                mock_yfinance_ticker,
            )

            # Should use LLM enhanced scoring
            assert result["analysis_method"] == "llm_enhanced"
            assert result["composite_score"] == 75.5
            assert "llm_analysis" in result
            assert "news_impact" in result
            assert "growth_catalysts" in result

    def test_enhanced_scoring_fallback(self, mock_yfinance_ticker):
        """Test fallback to traditional scoring when LLM fails"""
        # Mock LLM scorer that raises exception
        mock_llm_scorer = Mock()
        mock_llm_scorer.calculate_enhanced_score.side_effect = Exception("API Error")

        analyzer = StockAnalyzer(enable_llm=False)
        analyzer.llm_scorer = mock_llm_scorer

        fundamentals = {"fundamental_score": 80}
        technical = {"technical_score": 70}
        sentiment = {"sentiment_score": 2}
        risk = {"risk_score": 3}

        result = analyzer._calculate_enhanced_score(
            "TEST",
            fundamentals,
            technical,
            sentiment,
            risk,
            mock_yfinance_ticker.info,
            mock_yfinance_ticker,
        )

        # Should fallback to traditional scoring
        assert "weights" in result
        assert result["weights"]["fundamental"] == 0.50  # Traditional weights


class TestStockAnalyzerEdgeCases:
    """Test edge cases and error handling"""

    @patch("yfinance.Ticker")
    def test_analyze_stock_exception_handling(self, mock_ticker_class):
        """Test exception handling in analyze_stock"""
        mock_ticker_class.side_effect = Exception("Network error")

        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer.analyze_stock("TEST")

        assert result is None

    def test_technical_analysis_empty_history(self):
        """Test technical analysis with empty history"""
        analyzer = StockAnalyzer(enable_llm=False)

        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()  # Empty DataFrame

        result = analyzer._analyze_technical(mock_ticker, "TEST")

        assert result["technical_score"] == 50  # Default score
        assert result["indicators"] == {}

    def test_sentiment_analysis_no_news(self):
        """Test sentiment analysis with no news"""
        analyzer = StockAnalyzer(enable_llm=False)

        mock_ticker = Mock()
        mock_ticker.news = []  # No news

        result = analyzer._analyze_sentiment(mock_ticker, {}, "TEST")

        assert result["sentiment_score"] == 0  # Neutral
        assert result["news_count"] == 0

    def test_score_fundamentals_missing_data(self):
        """Test fundamental scoring with missing data"""
        analyzer = StockAnalyzer(enable_llm=False)

        # Metrics with missing values
        incomplete_metrics = {
            "pe_ratio": 0,  # Missing
            "roe": None,  # Missing
            "revenue_growth": 0.15,  # Present
        }

        benchmarks = analyzer.sector_benchmarks["Technology"]
        score = analyzer._score_fundamentals(incomplete_metrics, benchmarks)

        # Should handle missing data gracefully
        assert 0 <= score <= 100

    def test_sector_benchmark_fallback(self):
        """Test fallback to default sector when sector unknown"""
        analyzer = StockAnalyzer(enable_llm=False)

        info = {
            "sector": "Unknown Sector",  # Not in benchmarks
            "longName": "Test Company",
            "currentPrice": 100,
        }

        result = analyzer._analyze_fundamentals(info, "TEST")

        # Should use Technology as default
        assert result["sector_benchmarks"] == analyzer.sector_benchmarks["Technology"]
