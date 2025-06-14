"""
DeepSeek LLM Analyzer

Provides AI-powered analysis using DeepSeek API for:
- News sentiment and impact analysis
- Growth catalyst identification
- Market context interpretation
- Investment thesis validation
"""

import json
import logging
import os
from typing import Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class DeepSeekAnalyzer:
    """
    AI-powered stock analysis using DeepSeek LLM.

    Provides sophisticated analysis of news, financial data, and market context
    to generate enhanced investment insights and scoring.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DeepSeek analyzer.

        Args:
            api_key: DeepSeek API key. If None, reads from DEEPSEEK_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable.")

        # Initialize OpenAI client with DeepSeek endpoint
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

        self.model = "deepseek-chat"

    def analyze_stock_comprehensive(
        self,
        symbol: str,
        financial_data: Dict,
        news_data: List[Dict],
        technical_data: Dict,
        market_context: Dict,
    ) -> Dict:
        """
        Comprehensive AI analysis of a stock combining all available data.

        Args:
            symbol: Stock symbol
            financial_data: Financial metrics and ratios
            news_data: Recent news articles and sentiment
            technical_data: Technical indicators and price action
            market_context: Broader market conditions

        Returns:
            Dict containing AI analysis results with scores and insights
        """
        try:
            # Prepare comprehensive prompt
            prompt = self._build_comprehensive_prompt(symbol, financial_data, news_data, technical_data, market_context)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=2000,
            )

            # Parse the response
            analysis_text = response.choices[0].message.content
            return self._parse_analysis_response(analysis_text)

        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {e}")
            return self._get_fallback_analysis()

    def analyze_news_impact(self, symbol: str, news_data: List[Dict]) -> Dict:
        """
        Analyze news impact on stock with detailed sentiment and catalyst identification.

        Args:
            symbol: Stock symbol
            news_data: List of news articles with titles, summaries, dates

        Returns:
            Dict with news impact score, sentiment, and key catalysts
        """
        try:
            if not news_data:
                return {
                    "impact_score": 50,  # Neutral
                    "sentiment": "neutral",
                    "confidence": 0.3,
                    "key_catalysts": [],
                    "risk_factors": [],
                }

            prompt = self._build_news_analysis_prompt(symbol, news_data)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial analyst specializing in news impact analysis. Provide precise, actionable insights about how news affects stock performance.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )

            analysis_text = response.choices[0].message.content
            return self._parse_news_analysis(analysis_text)

        except Exception as e:
            logger.error(f"Error in news analysis for {symbol}: {e}")
            return {
                "impact_score": 50,
                "sentiment": "neutral",
                "confidence": 0.3,
                "key_catalysts": [],
                "risk_factors": [],
            }

    def identify_growth_catalysts(self, symbol: str, financial_data: Dict, news_data: List[Dict]) -> Dict:
        """
        Identify potential growth catalysts and investment thesis.

        Args:
            symbol: Stock symbol
            financial_data: Financial metrics
            news_data: Recent news

        Returns:
            Dict with growth catalysts, timeline, and conviction level
        """
        try:
            prompt = self._build_catalyst_prompt(symbol, financial_data, news_data)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a growth investor and analyst. Identify specific, actionable growth catalysts with realistic timelines and conviction levels.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1200,
            )

            analysis_text = response.choices[0].message.content
            return self._parse_catalyst_analysis(analysis_text)

        except Exception as e:
            logger.error(f"Error in catalyst analysis for {symbol}: {e}")
            return {
                "catalysts": [],
                "timeline": "unknown",
                "conviction": "low",
                "thesis_strength": 50,
            }

    def _get_system_prompt(self) -> str:
        """Get the system prompt for comprehensive analysis."""
        return """You are an expert quantitative analyst and portfolio manager with 20+ years of experience.

        Your task is to provide comprehensive stock analysis that combines:
        - Fundamental analysis (financial health, valuation, growth)
        - Technical analysis (momentum, trends, support/resistance)
        - News sentiment and market impact
        - Risk assessment and portfolio fit

        Provide your analysis in a structured JSON format with specific scores (0-100) and clear reasoning.
        Be precise, actionable, and focus on investment-relevant insights.

        Always include:
        1. Overall investment score (0-100)
        2. Confidence level (0-100)
        3. Key strengths (3-5 points)
        4. Key risks (3-5 points)
        5. Investment thesis (2-3 sentences)
        6. Time horizon recommendation
        7. Position sizing suggestion (% of portfolio)"""

    def _build_comprehensive_prompt(
        self,
        symbol: str,
        financial_data: Dict,
        news_data: List[Dict],
        technical_data: Dict,
        market_context: Dict,
    ) -> str:
        """Build comprehensive analysis prompt."""

        # Format financial data
        financial_summary = self._format_financial_data(financial_data)

        # Format news data
        news_summary = self._format_news_data(news_data)

        # Format technical data
        technical_summary = self._format_technical_data(technical_data)

        # Format market context
        market_summary = self._format_market_context(market_context)

        return f"""
        Analyze {symbol} for investment potential using the following data:

        FINANCIAL DATA:
        {financial_summary}

        RECENT NEWS & SENTIMENT:
        {news_summary}

        TECHNICAL INDICATORS:
        {technical_summary}

        MARKET CONTEXT:
        {market_summary}

        Provide a comprehensive analysis in JSON format with the following structure:
        {{
            "overall_score": <0-100>,
            "confidence": <0-100>,
            "investment_thesis": "<2-3 sentence thesis>",
            "key_strengths": ["<strength 1>", "<strength 2>", ...],
            "key_risks": ["<risk 1>", "<risk 2>", ...],
            "time_horizon": "<short/medium/long>",
            "position_size": <percentage of portfolio>,
            "catalyst_timeline": "<timeline for key catalysts>",
            "risk_adjusted_score": <0-100>
        }}
        """

    def _build_news_analysis_prompt(self, symbol: str, news_data: List[Dict]) -> str:
        """Build news analysis prompt."""
        news_text = "\n".join([f"- {article.get('title', 'No title')}: {article.get('summary', 'No summary')[:200]}..." for article in news_data[:10]])  # Limit to recent 10 articles

        return f"""
        Analyze the news impact for {symbol} based on these recent articles:

        {news_text}

        Provide analysis in JSON format:
        {{
            "impact_score": <0-100>,
            "sentiment": "<positive/negative/neutral>",
            "confidence": <0-1>,
            "key_catalysts": ["<catalyst 1>", "<catalyst 2>", ...],
            "risk_factors": ["<risk 1>", "<risk 2>", ...],
            "timeline_impact": "<immediate/short-term/long-term>"
        }}
        """

    def _build_catalyst_prompt(self, symbol: str, financial_data: Dict, news_data: List[Dict]) -> str:
        """Build growth catalyst identification prompt."""
        return f"""
        Identify growth catalysts for {symbol} based on:

        Financial Performance:
        - Revenue Growth: {financial_data.get('revenue_growth', 'N/A')}
        - Profit Margins: {financial_data.get('profit_margin', 'N/A')}
        - ROE: {financial_data.get('roe', 'N/A')}
        - Debt/Equity: {financial_data.get('debt_to_equity', 'N/A')}

        Recent Developments:
        {self._format_news_data(news_data[:5])}

        Identify specific, actionable growth catalysts in JSON format:
        {{
            "catalysts": [
                {{
                    "catalyst": "<specific catalyst>",
                    "impact_potential": "<high/medium/low>",
                    "timeline": "<timeframe>",
                    "probability": <0-100>
                }}
            ],
            "overall_conviction": "<high/medium/low>",
            "thesis_strength": <0-100>,
            "key_risks_to_thesis": ["<risk 1>", "<risk 2>"]
        }}
        """

    def _format_financial_data(self, data: Dict) -> str:
        """Format financial data for prompt."""
        key_metrics = [
            "market_cap",
            "pe_ratio",
            "revenue_growth",
            "profit_margin",
            "roe",
            "debt_to_equity",
            "current_ratio",
            "price_to_book",
        ]

        formatted = []
        for metric in key_metrics:
            value = data.get(metric, "N/A")
            formatted.append(f"- {metric.replace('_', ' ').title()}: {value}")

        return "\n".join(formatted)

    def _format_news_data(self, news_data: List[Dict]) -> str:
        """Format news data for prompt."""
        if not news_data:
            return "No recent news available"

        formatted = []
        for article in news_data[:5]:  # Limit to 5 most recent
            title = article.get("title", "No title")
            summary = article.get("summary", "No summary")[:150]
            formatted.append(f"- {title}: {summary}...")

        return "\n".join(formatted)

    def _format_technical_data(self, data: Dict) -> str:
        """Format technical data for prompt."""
        return f"""
        - Price Trend: {data.get('trend', 'N/A')}
        - RSI: {data.get('rsi', 'N/A')}
        - Moving Average Position: {data.get('ma_position', 'N/A')}
        - Volume Trend: {data.get('volume_trend', 'N/A')}
        - Support/Resistance: {data.get('support_resistance', 'N/A')}
        """

    def _format_market_context(self, data: Dict) -> str:
        """Format market context for prompt."""
        return f"""
        - Market Trend: {data.get('market_trend', 'N/A')}
        - Sector Performance: {data.get('sector_performance', 'N/A')}
        - VIX Level: {data.get('vix', 'N/A')}
        - Interest Rate Environment: {data.get('interest_rates', 'N/A')}
        """

    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the comprehensive analysis response."""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._parse_text_response(response_text)

        except json.JSONDecodeError:
            return self._parse_text_response(response_text)

    def _parse_news_analysis(self, response_text: str) -> Dict:
        """Parse news analysis response."""
        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "impact_score": 50,
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "key_catalysts": [],
                    "risk_factors": [],
                }

        except json.JSONDecodeError:
            return {
                "impact_score": 50,
                "sentiment": "neutral",
                "confidence": 0.5,
                "key_catalysts": [],
                "risk_factors": [],
            }

    def _parse_catalyst_analysis(self, response_text: str) -> Dict:
        """Parse catalyst analysis response."""
        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "catalysts": [],
                    "overall_conviction": "medium",
                    "thesis_strength": 50,
                    "key_risks_to_thesis": [],
                }

        except json.JSONDecodeError:
            return {
                "catalysts": [],
                "overall_conviction": "medium",
                "thesis_strength": 50,
                "key_risks_to_thesis": [],
            }

    def _parse_text_response(self, response_text: str) -> Dict:
        """Fallback text parsing for non-JSON responses."""
        # Basic text parsing fallback
        score = 50  # Default neutral score

        # Look for score indicators in text
        if any(word in response_text.lower() for word in ["strong buy", "excellent", "outstanding"]):
            score = 85
        elif any(word in response_text.lower() for word in ["buy", "positive", "good"]):
            score = 70
        elif any(word in response_text.lower() for word in ["hold", "neutral", "mixed"]):
            score = 50
        elif any(word in response_text.lower() for word in ["sell", "negative", "poor"]):
            score = 30

        return {
            "overall_score": score,
            "confidence": 60,
            "investment_thesis": "Analysis based on available data",
            "key_strengths": ["Market position"],
            "key_risks": ["Market volatility"],
            "time_horizon": "medium",
            "position_size": 3.0,
            "catalyst_timeline": "medium-term",
            "risk_adjusted_score": score,
        }

    def _get_fallback_analysis(self) -> Dict:
        """Get fallback analysis when API fails."""
        return {
            "overall_score": 50,
            "confidence": 30,
            "investment_thesis": "Unable to complete AI analysis",
            "key_strengths": ["Requires manual analysis"],
            "key_risks": ["Analysis incomplete"],
            "time_horizon": "medium",
            "position_size": 2.0,
            "catalyst_timeline": "unknown",
            "risk_adjusted_score": 50,
        }
