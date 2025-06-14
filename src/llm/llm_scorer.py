"""
LLM-Enhanced Scoring System

Integrates DeepSeek AI analysis into the composite stock scoring system,
implementing the new scoring weights:
- 40% Fundamentals
- 20% Technical Analysis
- 30% LLM Analysis
- 10% Risk Assessment
"""

import logging
from typing import Dict, Optional

from .deepseek_analyzer import DeepSeekAnalyzer

logger = logging.getLogger(__name__)


class LLMScorer:
    """
    Enhanced scoring system that integrates LLM analysis with traditional metrics.

    Combines fundamental, technical, sentiment, and AI-powered analysis
    to generate comprehensive investment scores.
    """

    def __init__(self, deepseek_api_key: Optional[str] = None):
        """
        Initialize LLM scorer.

        Args:
            deepseek_api_key: DeepSeek API key for AI analysis
        """
        self.llm_analyzer = None

        # Try to initialize DeepSeek analyzer
        try:
            self.llm_analyzer = DeepSeekAnalyzer(deepseek_api_key)
            self.llm_enabled = True
            logger.info("LLM analysis enabled with DeepSeek")
        except Exception as e:
            logger.warning(f"LLM analysis disabled: {e}")
            self.llm_enabled = False

        # New scoring weights with LLM integration
        self.weights = {
            "fundamentals": 0.40,  # Reduced from 0.50
            "technical": 0.20,  # Reduced from 0.25
            "llm_analysis": 0.30,  # New component
            "risk": 0.10,  # Reduced from 0.15
        }

        # Fallback weights when LLM is disabled
        self.fallback_weights = {
            "fundamentals": 0.50,
            "technical": 0.25,
            "sentiment": 0.15,  # Traditional sentiment analysis
            "risk": 0.10,
        }

    def calculate_enhanced_score(
        self,
        symbol: str,
        fundamental_score: float,
        technical_score: float,
        sentiment_score: float,
        risk_score: float,
        financial_data: Dict,
        news_data: list,
        technical_data: Dict,
        market_context: Dict,
    ) -> Dict:
        """
        Calculate enhanced composite score with LLM integration.

        Args:
            symbol: Stock symbol
            fundamental_score: Traditional fundamental analysis score (0-100)
            technical_score: Technical analysis score (0-100)
            sentiment_score: Traditional sentiment score (0-100)
            risk_score: Risk assessment score (0-100)
            financial_data: Financial metrics for LLM analysis
            news_data: News articles for LLM analysis
            technical_data: Technical indicators for LLM analysis
            market_context: Market context for LLM analysis

        Returns:
            Dict with enhanced scores and analysis
        """

        if self.llm_enabled and self.llm_analyzer:
            return self._calculate_llm_enhanced_score(
                symbol,
                fundamental_score,
                technical_score,
                sentiment_score,
                risk_score,
                financial_data,
                news_data,
                technical_data,
                market_context,
            )
        else:
            return self._calculate_traditional_score(symbol, fundamental_score, technical_score, sentiment_score, risk_score)

    def _calculate_llm_enhanced_score(
        self,
        symbol: str,
        fundamental_score: float,
        technical_score: float,
        sentiment_score: float,
        risk_score: float,
        financial_data: Dict,
        news_data: list,
        technical_data: Dict,
        market_context: Dict,
    ) -> Dict:
        """Calculate score with LLM analysis integration."""

        try:
            # Get comprehensive LLM analysis
            llm_analysis = self.llm_analyzer.analyze_stock_comprehensive(symbol, financial_data, news_data, technical_data, market_context)

            # Get news impact analysis
            news_analysis = self.llm_analyzer.analyze_news_impact(symbol, news_data)

            # Get growth catalyst analysis
            catalyst_analysis = self.llm_analyzer.identify_growth_catalysts(symbol, financial_data, news_data)

            # Extract LLM score (0-100)
            llm_score = llm_analysis.get("overall_score", 50)
            llm_confidence = llm_analysis.get("confidence", 50)

            # Calculate weighted composite score
            composite_score = fundamental_score * self.weights["fundamentals"] + technical_score * self.weights["technical"] + llm_score * self.weights["llm_analysis"] + risk_score * self.weights["risk"]

            # Risk-adjusted score from LLM
            risk_adjusted_score = llm_analysis.get("risk_adjusted_score", composite_score)

            # Determine investment rating
            rating = self._get_investment_rating(composite_score, llm_confidence)

            return {
                "composite_score": round(composite_score, 1),
                "risk_adjusted_score": round(risk_adjusted_score, 1),
                "rating": rating,
                "confidence": llm_confidence,
                "component_scores": {
                    "fundamental": round(fundamental_score, 1),
                    "technical": round(technical_score, 1),
                    "llm_analysis": round(llm_score, 1),
                    "risk": round(risk_score, 1),
                },
                "weights_used": self.weights,
                "llm_analysis": {
                    "investment_thesis": llm_analysis.get("investment_thesis", ""),
                    "key_strengths": llm_analysis.get("key_strengths", []),
                    "key_risks": llm_analysis.get("key_risks", []),
                    "time_horizon": llm_analysis.get("time_horizon", "medium"),
                    "position_size": llm_analysis.get("position_size", 3.0),
                    "catalyst_timeline": llm_analysis.get("catalyst_timeline", "medium-term"),
                },
                "news_impact": {
                    "impact_score": news_analysis.get("impact_score", 50),
                    "sentiment": news_analysis.get("sentiment", "neutral"),
                    "key_catalysts": news_analysis.get("key_catalysts", []),
                    "risk_factors": news_analysis.get("risk_factors", []),
                },
                "growth_catalysts": {
                    "catalysts": catalyst_analysis.get("catalysts", []),
                    "conviction": catalyst_analysis.get("overall_conviction", "medium"),
                    "thesis_strength": catalyst_analysis.get("thesis_strength", 50),
                },
                "analysis_method": "llm_enhanced",
            }

        except Exception as e:
            logger.error(f"Error in LLM analysis for {symbol}: {e}")
            # Fallback to traditional scoring
            return self._calculate_traditional_score(symbol, fundamental_score, technical_score, sentiment_score, risk_score)

    def _calculate_traditional_score(
        self,
        symbol: str,
        fundamental_score: float,
        technical_score: float,
        sentiment_score: float,
        risk_score: float,
    ) -> Dict:
        """Calculate traditional composite score without LLM."""

        # Use fallback weights
        composite_score = fundamental_score * self.fallback_weights["fundamentals"] + technical_score * self.fallback_weights["technical"] + sentiment_score * self.fallback_weights["sentiment"] + risk_score * self.fallback_weights["risk"]

        # Estimate confidence based on score consistency
        score_variance = self._calculate_score_variance([fundamental_score, technical_score, sentiment_score, risk_score])
        confidence = max(30, 100 - score_variance * 2)

        rating = self._get_investment_rating(composite_score, confidence)

        return {
            "composite_score": round(composite_score, 1),
            "risk_adjusted_score": round(composite_score, 1),
            "rating": rating,
            "confidence": round(confidence, 1),
            "component_scores": {
                "fundamental": round(fundamental_score, 1),
                "technical": round(technical_score, 1),
                "sentiment": round(sentiment_score, 1),
                "risk": round(risk_score, 1),
            },
            "weights_used": self.fallback_weights,
            "llm_analysis": {
                "investment_thesis": "Traditional analysis without AI enhancement",
                "key_strengths": ["Requires detailed analysis"],
                "key_risks": ["Limited AI insights"],
                "time_horizon": "medium",
                "position_size": 3.0,
                "catalyst_timeline": "unknown",
            },
            "news_impact": {
                "impact_score": sentiment_score,
                "sentiment": self._score_to_sentiment(sentiment_score),
                "key_catalysts": [],
                "risk_factors": [],
            },
            "growth_catalysts": {
                "catalysts": [],
                "conviction": "medium",
                "thesis_strength": round(composite_score, 1),
            },
            "analysis_method": "traditional",
        }

    def _get_investment_rating(self, score: float, confidence: float) -> str:
        """
        Determine investment rating based on score and confidence.

        Args:
            score: Composite score (0-100)
            confidence: Confidence level (0-100)

        Returns:
            Investment rating string
        """
        # Adjust rating based on confidence
        if confidence < 40:
            # Low confidence downgrades rating
            if score >= 80:
                return "Hold"  # Downgrade from Strong Buy
            elif score >= 70:
                return "Hold"  # Downgrade from Buy
            elif score >= 50:
                return "Hold"
            else:
                return "Avoid"

        # Normal confidence ratings
        if score >= 80:
            return "Strong Buy"
        elif score >= 70:
            return "Buy"
        elif score >= 50:
            return "Hold"
        elif score >= 30:
            return "Sell"
        else:
            return "Strong Sell"

    def _score_to_sentiment(self, score: float) -> str:
        """Convert numeric score to sentiment string."""
        if score >= 60:
            return "positive"
        elif score >= 40:
            return "neutral"
        else:
            return "negative"

    def _calculate_score_variance(self, scores: list) -> float:
        """Calculate variance in component scores."""
        if not scores:
            return 50

        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return variance**0.5  # Standard deviation

    def get_scoring_explanation(self) -> Dict:
        """
        Get explanation of the scoring methodology.

        Returns:
            Dict explaining scoring weights and methodology
        """
        if self.llm_enabled:
            return {
                "method": "LLM-Enhanced Scoring",
                "weights": self.weights,
                "description": {
                    "fundamentals": "Financial health, valuation metrics, growth indicators (40%)",
                    "technical": "Price momentum, moving averages, volume analysis (20%)",
                    "llm_analysis": "AI-powered news analysis, catalyst identification, thesis validation (30%)",
                    "risk": "Volatility, debt levels, market risk assessment (10%)",
                },
                "advantages": [
                    "AI-enhanced news interpretation",
                    "Sophisticated catalyst identification",
                    "Context-aware market analysis",
                    "Dynamic thesis validation",
                ],
            }
        else:
            return {
                "method": "Traditional Scoring",
                "weights": self.fallback_weights,
                "description": {
                    "fundamentals": "Financial health, valuation metrics, growth indicators (50%)",
                    "technical": "Price momentum, moving averages, volume analysis (25%)",
                    "sentiment": "Basic news sentiment and analyst ratings (15%)",
                    "risk": "Volatility, debt levels, market risk assessment (10%)",
                },
                "limitations": [
                    "Basic sentiment analysis only",
                    "Limited news interpretation",
                    "No AI-powered insights",
                ],
            }
