"""
Unit tests for LLM components
"""

import json
from unittest.mock import Mock, patch

import pytest

from llm.deepseek_analyzer import DeepSeekAnalyzer
from llm.llm_scorer import LLMScorer


class TestDeepSeekAnalyzer:
    """Test cases for DeepSeekAnalyzer"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch("llm.deepseek_analyzer.OpenAI") as mock_openai:
            analyzer = DeepSeekAnalyzer(api_key="test_key")

            assert analyzer.api_key == "test_key"
            assert analyzer.model == "deepseek-chat"
            mock_openai.assert_called_once_with(api_key="test_key", base_url="https://api.deepseek.com")

    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="DeepSeek API key required"):
                DeepSeekAnalyzer()

    @patch("llm.deepseek_analyzer.OpenAI")
    def test_analyze_stock_comprehensive_success(
        self,
        mock_openai,
        sample_financial_data,
        sample_news_data,
        sample_technical_data,
        sample_market_context,
    ):
        """Test successful comprehensive stock analysis"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps(
            {
                "overall_score": 78,
                "confidence": 85,
                "investment_thesis": "Strong fundamentals with growth potential",
                "key_strengths": ["Market leadership", "Strong margins"],
                "key_risks": ["Market volatility", "Competition"],
                "time_horizon": "medium",
                "position_size": 5.5,
                "catalyst_timeline": "6-12 months",
                "risk_adjusted_score": 74,
            }
        )
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(api_key="test_key")

        result = analyzer.analyze_stock_comprehensive(
            symbol="TEST",
            financial_data=sample_financial_data,
            news_data=sample_news_data,
            technical_data=sample_technical_data,
            market_context=sample_market_context,
        )

        assert result["overall_score"] == 78
        assert result["confidence"] == 85
        assert result["investment_thesis"] == "Strong fundamentals with growth potential"
        assert len(result["key_strengths"]) == 2
        assert len(result["key_risks"]) == 2

    @patch("llm.deepseek_analyzer.OpenAI")
    def test_analyze_stock_comprehensive_api_error(
        self,
        mock_openai,
        sample_financial_data,
        sample_news_data,
        sample_technical_data,
        sample_market_context,
    ):
        """Test handling of API errors in comprehensive analysis"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(api_key="test_key")

        result = analyzer.analyze_stock_comprehensive(
            symbol="TEST",
            financial_data=sample_financial_data,
            news_data=sample_news_data,
            technical_data=sample_technical_data,
            market_context=sample_market_context,
        )

        # Should return fallback analysis
        assert result["overall_score"] == 50
        assert result["confidence"] == 30
        assert result["investment_thesis"] == "Unable to complete AI analysis"

    @patch("llm.deepseek_analyzer.OpenAI")
    def test_analyze_news_impact_success(self, mock_openai, sample_news_data):
        """Test successful news impact analysis"""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps(
            {
                "impact_score": 75,
                "sentiment": "positive",
                "confidence": 0.9,
                "key_catalysts": ["Strong earnings", "Product launch"],
                "risk_factors": ["Market volatility"],
                "timeline_impact": "short-term",
            }
        )
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(api_key="test_key")

        result = analyzer.analyze_news_impact("TEST", sample_news_data)

        assert result["impact_score"] == 75
        assert result["sentiment"] == "positive"
        assert result["confidence"] == 0.9
        assert len(result["key_catalysts"]) == 2
        assert len(result["risk_factors"]) == 1

    @patch("llm.deepseek_analyzer.OpenAI")
    def test_analyze_news_impact_no_news(self, mock_openai):
        """Test news impact analysis with no news"""
        mock_openai.return_value = Mock()

        analyzer = DeepSeekAnalyzer(api_key="test_key")

        result = analyzer.analyze_news_impact("TEST", [])

        # Should return neutral result
        assert result["impact_score"] == 50
        assert result["sentiment"] == "neutral"
        assert result["confidence"] == 0.3
        assert result["key_catalysts"] == []
        assert result["risk_factors"] == []

    @patch("llm.deepseek_analyzer.OpenAI")
    def test_identify_growth_catalysts_success(self, mock_openai, sample_financial_data, sample_news_data):
        """Test successful growth catalyst identification"""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps(
            {
                "catalysts": [
                    {
                        "catalyst": "AI market expansion",
                        "impact_potential": "high",
                        "timeline": "12-18 months",
                        "probability": 85,
                    }
                ],
                "overall_conviction": "high",
                "thesis_strength": 88,
                "key_risks_to_thesis": ["Market saturation"],
            }
        )
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        analyzer = DeepSeekAnalyzer(api_key="test_key")

        result = analyzer.identify_growth_catalysts("TEST", sample_financial_data, sample_news_data)

        assert len(result["catalysts"]) == 1
        assert result["catalysts"][0]["catalyst"] == "AI market expansion"
        assert result["catalysts"][0]["impact_potential"] == "high"
        assert result["overall_conviction"] == "high"
        assert result["thesis_strength"] == 88

    def test_format_financial_data(self, sample_financial_data):
        """Test financial data formatting"""
        analyzer = DeepSeekAnalyzer(api_key="test_key")

        formatted = analyzer._format_financial_data(sample_financial_data)

        assert "Market Cap:" in formatted
        assert "Pe Ratio:" in formatted
        assert "Revenue Growth:" in formatted
        assert "Profit Margin:" in formatted

    def test_format_news_data(self, sample_news_data):
        """Test news data formatting"""
        analyzer = DeepSeekAnalyzer(api_key="test_key")

        formatted = analyzer._format_news_data(sample_news_data)

        assert "Company Reports Strong Q1 Results" in formatted
        assert "New Product Launch Expected" in formatted

    def test_format_news_data_empty(self):
        """Test news data formatting with empty list"""
        analyzer = DeepSeekAnalyzer(api_key="test_key")

        formatted = analyzer._format_news_data([])

        assert formatted == "No recent news available"

    def test_parse_analysis_response_valid_json(self):
        """Test parsing valid JSON response"""
        analyzer = DeepSeekAnalyzer(api_key="test_key")

        response_text = """
        Here is the analysis:
        {
            "overall_score": 75,
            "confidence": 80,
            "investment_thesis": "Good investment"
        }
        Additional text here.
        """

        result = analyzer._parse_analysis_response(response_text)

        assert result["overall_score"] == 75
        assert result["confidence"] == 80
        assert result["investment_thesis"] == "Good investment"

    def test_parse_analysis_response_invalid_json(self):
        """Test parsing invalid JSON response"""
        analyzer = DeepSeekAnalyzer(api_key="test_key")

        response_text = "This is not JSON and contains strong buy recommendation"

        result = analyzer._parse_analysis_response(response_text)

        # Should use text parsing fallback
        assert result["overall_score"] == 85  # "strong buy" detected
        assert result["confidence"] == 60

    def test_parse_text_response_sentiment_detection(self):
        """Test text response parsing with sentiment detection"""
        analyzer = DeepSeekAnalyzer(api_key="test_key")

        # Test different sentiment keywords
        test_cases = [
            ("This is an excellent investment opportunity", 85),
            ("I recommend buying this stock", 70),
            ("This is a neutral hold position", 50),
            ("I would sell this poor performing stock", 30),
        ]

        for text, expected_score in test_cases:
            result = analyzer._parse_text_response(text)
            assert result["overall_score"] == expected_score


class TestLLMScorer:
    """Test cases for LLMScorer"""

    def test_init_with_llm_enabled(self):
        """Test initialization with LLM enabled"""
        with patch("llm.llm_scorer.DeepSeekAnalyzer"):
            scorer = LLMScorer(deepseek_api_key="test_key")

            assert scorer.llm_enabled is True
            assert scorer.weights["fundamentals"] == 0.40
            assert scorer.weights["technical"] == 0.20
            assert scorer.weights["llm_analysis"] == 0.30
            assert scorer.weights["risk"] == 0.10

    def test_init_with_llm_disabled(self):
        """Test initialization with LLM disabled due to error"""
        with patch("llm.llm_scorer.DeepSeekAnalyzer") as mock_analyzer:
            mock_analyzer.side_effect = Exception("API Error")

            scorer = LLMScorer(deepseek_api_key="test_key")

            assert scorer.llm_enabled is False
            assert scorer.llm_analyzer is None

    def test_calculate_enhanced_score_with_llm(
        self,
        mock_llm_scorer,
        sample_financial_data,
        sample_news_data,
        sample_technical_data,
        sample_market_context,
    ):
        """Test enhanced score calculation with LLM"""
        # Use the mock_llm_scorer fixture which has pre-configured responses
        result = mock_llm_scorer.calculate_enhanced_score(
            symbol="TEST",
            fundamental_score=80.0,
            technical_score=70.0,
            sentiment_score=65.0,
            risk_score=85.0,
            financial_data=sample_financial_data,
            news_data=sample_news_data,
            technical_data=sample_technical_data,
            market_context=sample_market_context,
        )

        assert result["analysis_method"] == "llm_enhanced"
        assert result["composite_score"] == 75.5
        assert result["rating"] == "Buy"
        assert result["confidence"] == 85
        assert "llm_analysis" in result
        assert "news_impact" in result
        assert "growth_catalysts" in result

    def test_calculate_traditional_score(self):
        """Test traditional score calculation"""
        scorer = LLMScorer()
        scorer.llm_enabled = False  # Force traditional mode

        result = scorer._calculate_traditional_score(
            symbol="TEST",
            fundamental_score=80.0,
            technical_score=70.0,
            sentiment_score=65.0,
            risk_score=85.0,
        )

        assert result["analysis_method"] == "traditional"
        assert "composite_score" in result
        assert result["weights_used"] == scorer.fallback_weights
        assert result["llm_analysis"]["investment_thesis"] == "Traditional analysis without AI enhancement"

    def test_get_investment_rating_high_confidence(self):
        """Test investment rating with high confidence"""
        scorer = LLMScorer()

        # High score, high confidence
        rating = scorer._get_investment_rating(85, 90)
        assert rating == "Strong Buy"

        # Medium score, high confidence
        rating = scorer._get_investment_rating(65, 80)
        assert rating == "Hold"

        # Low score, high confidence
        rating = scorer._get_investment_rating(25, 80)
        assert rating == "Strong Sell"

    def test_get_investment_rating_low_confidence(self):
        """Test investment rating with low confidence"""
        scorer = LLMScorer()

        # High score, low confidence - should downgrade
        rating = scorer._get_investment_rating(85, 30)
        assert rating == "Hold"  # Downgraded from Strong Buy

        # Medium score, low confidence
        rating = scorer._get_investment_rating(65, 30)
        assert rating == "Hold"

        # Low score, low confidence
        rating = scorer._get_investment_rating(25, 30)
        assert rating == "Avoid"

    def test_score_to_sentiment(self):
        """Test score to sentiment conversion"""
        scorer = LLMScorer()

        assert scorer._score_to_sentiment(75) == "positive"
        assert scorer._score_to_sentiment(50) == "neutral"
        assert scorer._score_to_sentiment(25) == "negative"

    def test_calculate_score_variance(self):
        """Test score variance calculation"""
        scorer = LLMScorer()

        # Low variance (consistent scores)
        low_variance = scorer._calculate_score_variance([80, 82, 78, 81])
        assert low_variance < 5

        # High variance (inconsistent scores)
        high_variance = scorer._calculate_score_variance([90, 50, 30, 85])
        assert high_variance > 20

        # Empty list
        empty_variance = scorer._calculate_score_variance([])
        assert empty_variance == 50

    def test_get_scoring_explanation_llm_enabled(self):
        """Test scoring explanation with LLM enabled"""
        with patch("llm.llm_scorer.DeepSeekAnalyzer"):
            scorer = LLMScorer(deepseek_api_key="test_key")
            scorer.llm_enabled = True

            explanation = scorer.get_scoring_explanation()

            assert explanation["method"] == "LLM-Enhanced Scoring"
            assert explanation["weights"] == scorer.weights
            assert "AI-enhanced news interpretation" in explanation["advantages"]

    def test_get_scoring_explanation_llm_disabled(self):
        """Test scoring explanation with LLM disabled"""
        scorer = LLMScorer()
        scorer.llm_enabled = False

        explanation = scorer.get_scoring_explanation()

        assert explanation["method"] == "Traditional Scoring"
        assert explanation["weights"] == scorer.fallback_weights
        assert "Basic sentiment analysis only" in explanation["limitations"]


class TestLLMComponentsIntegration:
    """Integration tests for LLM components"""

    @patch("llm.deepseek_analyzer.OpenAI")
    def test_end_to_end_llm_analysis(
        self,
        mock_openai,
        sample_financial_data,
        sample_news_data,
        sample_technical_data,
        sample_market_context,
    ):
        """Test end-to-end LLM analysis flow"""
        # Mock comprehensive analysis response
        comprehensive_response = Mock()
        comp_choice = Mock()
        comp_message = Mock()
        comp_message.content = json.dumps(
            {
                "overall_score": 78,
                "confidence": 85,
                "investment_thesis": "Strong fundamentals with AI growth catalysts",
                "key_strengths": ["Market leadership", "Strong margins"],
                "key_risks": ["Market volatility", "Competition"],
                "time_horizon": "medium",
                "position_size": 5.5,
                "catalyst_timeline": "6-12 months",
                "risk_adjusted_score": 74,
            }
        )
        comp_choice.message = comp_message
        comprehensive_response.choices = [comp_choice]

        # Mock news analysis response
        news_response = Mock()
        news_choice = Mock()
        news_message = Mock()
        news_message.content = json.dumps(
            {
                "impact_score": 75,
                "sentiment": "positive",
                "confidence": 0.9,
                "key_catalysts": ["Strong earnings"],
                "risk_factors": ["Market volatility"],
                "timeline_impact": "short-term",
            }
        )
        news_choice.message = news_message
        news_response.choices = [news_choice]

        # Mock catalyst analysis response
        catalyst_response = Mock()
        cat_choice = Mock()
        cat_message = Mock()
        cat_message.content = json.dumps(
            {
                "catalysts": [{"catalyst": "AI expansion", "impact_potential": "high"}],
                "overall_conviction": "high",
                "thesis_strength": 85,
                "key_risks_to_thesis": ["Competition"],
            }
        )
        cat_choice.message = cat_message
        catalyst_response.choices = [cat_choice]

        # Configure mock client to return different responses for different calls
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            comprehensive_response,
            news_response,
            catalyst_response,
        ]
        mock_openai.return_value = mock_client

        # Create scorer and run analysis
        scorer = LLMScorer(deepseek_api_key="test_key")

        result = scorer.calculate_enhanced_score(
            symbol="TEST",
            fundamental_score=80.0,
            technical_score=70.0,
            sentiment_score=65.0,
            risk_score=85.0,
            financial_data=sample_financial_data,
            news_data=sample_news_data,
            technical_data=sample_technical_data,
            market_context=sample_market_context,
        )

        # Verify the complete analysis
        assert result["analysis_method"] == "llm_enhanced"
        assert result["composite_score"] > 0
        assert result["llm_analysis"]["investment_thesis"] == "Strong fundamentals with AI growth catalysts"
        assert result["news_impact"]["sentiment"] == "positive"
        assert len(result["growth_catalysts"]["catalysts"]) == 1

        # Verify API was called 3 times (comprehensive, news, catalyst)
        assert mock_client.chat.completions.create.call_count == 3
