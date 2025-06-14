"""
DeepSeek LLM Analyzer

Provides AI-powered analysis using DeepSeek API for:
- News sentiment and impact analysis
- Growth catalyst identification
- Market context interpretation
- Investment thesis validation
"""

import hashlib
import json
import logging
import os
import time
from typing import Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)


class DeepSeekAnalyzer:
    """
    AI-powered stock analysis using DeepSeek LLM.

    Provides sophisticated analysis of news, financial data, and market context
    to generate enhanced investment insights and scoring.
    """

    def __init__(self, api_key: Optional[str] = None, enable_caching: bool = True):
        """
        Initialize DeepSeek analyzer.

        Args:
            api_key: DeepSeek API key. If None, reads from DEEPSEEK_API_KEY env var.
            enable_caching: Whether to enable response caching for cost optimization
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable.")

        # Initialize OpenAI client with DeepSeek endpoint
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

        self.model = "deepseek-chat"
        self.enable_caching = enable_caching

        # Cost tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.api_calls_made = 0

        # Rate limiting
        self.last_api_call = 0
        self.min_api_interval = 0.1  # 100ms between calls

        # Cache for responses (in-memory for now)
        self._response_cache = {}

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
            # Check cache first
            cache_key = self._generate_cache_key("comprehensive", symbol, financial_data, news_data, technical_data, market_context)
            if self.enable_caching and cache_key in self._response_cache:
                logger.info(f"Using cached comprehensive analysis for {symbol}")
                return self._response_cache[cache_key]

            # Prepare enhanced prompt with sector-specific analysis
            prompt = self._build_enhanced_comprehensive_prompt(symbol, financial_data, news_data, technical_data, market_context)

            response = self._make_api_call(
                messages=[
                    {"role": "system", "content": self._get_enhanced_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=2500,  # Increased for more detailed analysis
            )

            # Parse the response
            analysis_text = response.choices[0].message.content
            result = self._parse_analysis_response(analysis_text)

            # Cache the result
            if self.enable_caching:
                self._response_cache[cache_key] = result

            return result

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

            # Check cache
            cache_key = self._generate_cache_key("news", symbol, news_data)
            if self.enable_caching and cache_key in self._response_cache:
                logger.info(f"Using cached news analysis for {symbol}")
                return self._response_cache[cache_key]

            prompt = self._build_enhanced_news_analysis_prompt(symbol, news_data)

            response = self._make_api_call(
                messages=[
                    {
                        "role": "system",
                        "content": self._get_news_analysis_system_prompt(),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1200,
            )

            analysis_text = response.choices[0].message.content
            result = self._parse_news_analysis(analysis_text)

            # Cache the result
            if self.enable_caching:
                self._response_cache[cache_key] = result

            return result

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
            # Check cache
            cache_key = self._generate_cache_key("catalysts", symbol, financial_data, news_data)
            if self.enable_caching and cache_key in self._response_cache:
                logger.info(f"Using cached catalyst analysis for {symbol}")
                return self._response_cache[cache_key]

            prompt = self._build_enhanced_catalyst_prompt(symbol, financial_data, news_data)

            response = self._make_api_call(
                messages=[
                    {
                        "role": "system",
                        "content": self._get_catalyst_analysis_system_prompt(),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1500,
            )

            analysis_text = response.choices[0].message.content
            result = self._parse_catalyst_analysis(analysis_text)

            # Cache the result
            if self.enable_caching:
                self._response_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(f"Error in catalyst analysis for {symbol}: {e}")
            return {
                "catalysts": [],
                "timeline": "unknown",
                "conviction": "low",
                "thesis_strength": 50,
            }

    def batch_analyze_stocks(self, stock_data_list: List[Dict]) -> Dict[str, Dict]:
        """
        Batch analyze multiple stocks for cost efficiency.

        Args:
            stock_data_list: List of dicts containing stock analysis data

        Returns:
            Dict mapping symbols to analysis results
        """
        results = {}
        batch_size = 3  # Process in small batches to avoid token limits

        for i in range(0, len(stock_data_list), batch_size):
            batch = stock_data_list[i : i + batch_size]

            try:
                # Build batch prompt
                batch_prompt = self._build_batch_analysis_prompt(batch)

                response = self._make_api_call(
                    messages=[
                        {"role": "system", "content": self._get_batch_system_prompt()},
                        {"role": "user", "content": batch_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=3000,
                )

                # Parse batch response
                batch_results = self._parse_batch_response(response.choices[0].message.content, batch)
                results.update(batch_results)

            except Exception as e:
                logger.error(f"Error in batch analysis: {e}")
                # Fallback to individual analysis
                for stock_data in batch:
                    symbol = stock_data.get("symbol", "UNKNOWN")
                    results[symbol] = self._get_fallback_analysis()

        return results

    def get_cost_summary(self) -> Dict:
        """Get summary of API usage and costs."""
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_cost_usd": round(self.total_cost, 4),
            "api_calls_made": self.api_calls_made,
            "average_cost_per_call": round(self.total_cost / max(1, self.api_calls_made), 4),
            "cache_hit_rate": len(self._response_cache) / max(1, self.api_calls_made) if self.enable_caching else 0,
        }

    def clear_cache(self):
        """Clear the response cache."""
        self._response_cache.clear()
        logger.info("Response cache cleared")

    def _make_api_call(self, messages: List[Dict], temperature: float = 0.1, max_tokens: int = 2000) -> any:
        """Make rate-limited API call with cost tracking."""
        # Rate limiting
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_api_interval:
            time.sleep(self.min_api_interval - time_since_last_call)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Track usage
            self.api_calls_made += 1
            self.last_api_call = time.time()

            if hasattr(response, "usage") and response.usage and hasattr(response.usage, "total_tokens"):
                tokens_used = response.usage.total_tokens
                if isinstance(tokens_used, (int, float)):
                    self.total_tokens_used += tokens_used
                    # DeepSeek pricing: ~$0.14 per 1M tokens (approximate)
                    self.total_cost += (tokens_used / 1_000_000) * 0.14

            return response

        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise

    def _generate_cache_key(self, analysis_type: str, symbol: str, *args) -> str:
        """Generate cache key for response caching."""
        # Create a hash of the input data for caching
        data_str = f"{analysis_type}_{symbol}_{str(args)}"
        return hashlib.md5(data_str.encode(), usedforsecurity=False).hexdigest()  # nosec B324

    def _get_enhanced_system_prompt(self) -> str:
        """Get enhanced system prompt for comprehensive analysis."""
        return """You are an expert quantitative analyst and portfolio manager with 20+ years of experience in equity research and investment management.

Your expertise includes:
- Fundamental analysis across all sectors with deep industry knowledge
- Technical analysis and market timing
- Risk assessment and portfolio construction
- Macroeconomic analysis and market cycles
- ESG considerations and sustainable investing

Provide comprehensive stock analysis that combines:
1. **Fundamental Analysis**: Financial health, valuation metrics, competitive position, management quality
2. **Technical Analysis**: Price momentum, volume patterns, support/resistance levels
3. **News & Sentiment**: Market sentiment, analyst coverage, news impact assessment
4. **Risk Assessment**: Company-specific risks, sector risks, macroeconomic risks
5. **Investment Thesis**: Clear, actionable investment rationale

**Output Format**: Provide analysis in structured JSON format with:
- overall_score (0-100): Comprehensive investment score
- confidence (0-100): Confidence in the analysis
- risk_adjusted_score (0-100): Score adjusted for risk factors
- investment_thesis (string): 2-3 sentence clear thesis
- key_strengths (array): 3-5 specific strengths
- key_risks (array): 3-5 specific risks
- time_horizon (string): "short" (3-6mo), "medium" (6-18mo), "long" (18mo+)
- position_size (number): Suggested portfolio allocation percentage (0-10%)
- catalyst_timeline (string): Expected timeline for key catalysts

Be precise, actionable, and focus on investment-relevant insights. Consider sector-specific factors and current market conditions."""

    def _get_news_analysis_system_prompt(self) -> str:
        """Get system prompt for news analysis."""
        return """You are an expert financial news analyst specializing in market impact assessment.

Your task is to analyze news articles and determine their impact on stock performance. Consider:

1. **Immediate Impact**: How will this news affect stock price in the next 1-5 days?
2. **Fundamental Impact**: Does this news change the company's long-term prospects?
3. **Market Sentiment**: How will investors and analysts react to this news?
4. **Competitive Implications**: How does this affect the company's competitive position?
5. **Catalyst Identification**: Are there specific events or developments that could drive future performance?

**Output Format**: JSON with:
- impact_score (0-100): Overall news impact score (50 = neutral)
- sentiment (string): "very_positive", "positive", "neutral", "negative", "very_negative"
- confidence (0-100): Confidence in the assessment
- key_catalysts (array): Specific positive catalysts identified
- risk_factors (array): Specific risks or concerns identified
- timeline (string): Expected timeline for impact realization

Focus on actionable insights and specific, measurable impacts."""

    def _get_catalyst_analysis_system_prompt(self) -> str:
        """Get system prompt for catalyst analysis."""
        return """You are a growth investor and equity research analyst specializing in identifying investment catalysts.

Your expertise includes:
- Product launch cycles and market adoption
- Regulatory approvals and policy changes
- Management changes and strategic initiatives
- Market expansion and competitive dynamics
- Financial inflection points and margin expansion

Identify specific, measurable catalysts that could drive stock outperformance. Consider:

1. **Near-term Catalysts** (0-6 months): Earnings beats, product launches, partnerships
2. **Medium-term Catalysts** (6-18 months): Market expansion, operational improvements
3. **Long-term Catalysts** (18+ months): Structural advantages, market leadership

**Output Format**: JSON with:
- catalysts (array): List of specific catalysts with descriptions and timelines
- overall_conviction (string): "high", "medium", "low"
- thesis_strength (0-100): Strength of the overall investment thesis
- primary_catalyst (string): Most important catalyst
- risk_to_thesis (array): Key risks that could derail the thesis

Be specific about timelines, measurable outcomes, and probability of success."""

    def _get_batch_system_prompt(self) -> str:
        """Get system prompt for batch analysis."""
        return """You are an expert portfolio manager analyzing multiple stocks simultaneously for relative comparison and ranking.

Provide concise but comprehensive analysis for each stock, focusing on:
1. Relative attractiveness within the group
2. Risk-adjusted return potential
3. Portfolio fit and diversification benefits
4. Key differentiating factors

Output JSON array with analysis for each stock."""

    def _build_enhanced_comprehensive_prompt(
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

        # Get sector-specific context
        sector = market_context.get("sector", "Unknown")
        sector_context = self._get_sector_specific_context(sector)

        return f"""
        Analyze {symbol} for investment potential using the following comprehensive data:

        **COMPANY OVERVIEW:**
        - Symbol: {symbol}
        - Sector: {sector}
        - Sector Context: {sector_context}

        **FINANCIAL METRICS:**
        {financial_summary}

        **RECENT NEWS & MARKET SENTIMENT:**
        {news_summary}

        **TECHNICAL ANALYSIS:**
        {technical_summary}

        **MARKET CONTEXT:**
        {market_summary}

        **ANALYSIS REQUIREMENTS:**
        1. Provide sector-specific analysis considering industry dynamics
        2. Assess competitive positioning within the sector
        3. Evaluate financial health relative to sector benchmarks
        4. Identify key catalysts and risks specific to this industry
        5. Consider current market conditions and their impact on this sector
        6. Provide clear investment thesis with specific reasoning

        Please provide your analysis in the specified JSON format with precise scores and actionable insights.

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

    def _build_enhanced_news_analysis_prompt(self, symbol: str, news_data: List[Dict]) -> str:
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

    def _build_enhanced_catalyst_prompt(self, symbol: str, financial_data: Dict, news_data: List[Dict]) -> str:
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

    def _get_sector_specific_context(self, sector: str) -> str:
        """Get sector-specific analysis context."""
        sector_contexts = {
            "Technology": "Focus on innovation, R&D spending, competitive moats, scalability, and disruption potential. Consider regulatory risks and market saturation.",
            "Healthcare": "Analyze pipeline strength, regulatory approvals, patent cliffs, clinical trial results, and demographic trends. Consider FDA risks and reimbursement issues.",
            "Financial Services": "Evaluate interest rate sensitivity, credit quality, regulatory capital, digital transformation, and economic cycle exposure.",
            "Consumer Discretionary": "Assess consumer spending trends, brand strength, supply chain efficiency, and economic sensitivity. Consider inflation and wage pressures.",
            "Consumer Staples": "Focus on market share, pricing power, distribution networks, and defensive characteristics. Consider commodity cost pressures.",
            "Energy": "Analyze commodity price exposure, production efficiency, ESG considerations, and transition to renewable energy.",
            "Industrials": "Evaluate economic cycle sensitivity, order backlogs, operational efficiency, and infrastructure spending trends.",
            "Materials": "Focus on commodity cycles, supply-demand dynamics, cost structure, and environmental regulations.",
            "Utilities": "Assess regulatory environment, dividend sustainability, infrastructure investments, and renewable energy transition.",
            "Real Estate": "Evaluate interest rate sensitivity, occupancy rates, development pipeline, and market fundamentals.",
            "Communication Services": "Focus on subscriber growth, content costs, competitive positioning, and regulatory environment.",
        }
        return sector_contexts.get(sector, "General market analysis focusing on competitive position, financial health, and growth prospects.")

    def _build_batch_analysis_prompt(self, stock_data_list: List[Dict]) -> str:
        """Build prompt for batch stock analysis."""
        stocks_summary = []
        for i, stock_data in enumerate(stock_data_list, 1):
            symbol = stock_data.get("symbol", f"STOCK{i}")
            financial = stock_data.get("financial_data", {})
            sector = stock_data.get("market_context", {}).get("sector", "Unknown")

            summary = f"""
            **{i}. {symbol}** (Sector: {sector})
            - Market Cap: {financial.get('market_cap', 'N/A')}
            - P/E Ratio: {financial.get('pe_ratio', 'N/A')}
            - Revenue Growth: {financial.get('revenue_growth', 'N/A')}
            - ROE: {financial.get('roe', 'N/A')}
            - Debt/Equity: {financial.get('debt_to_equity', 'N/A')}
            """
            stocks_summary.append(summary)

        return f"""
        Analyze the following {len(stock_data_list)} stocks for relative investment attractiveness:

        {chr(10).join(stocks_summary)}

        For each stock, provide analysis in JSON format within an array:
        [
            {{
                "symbol": "STOCK1",
                "overall_score": <0-100>,
                "confidence": <0-100>,
                "relative_rank": <1-{len(stock_data_list)}>,
                "investment_thesis": "Brief thesis",
                "key_strength": "Primary strength",
                "key_risk": "Primary risk",
                "position_size": <0-10>
            }},
            ...
        ]

        Focus on relative comparison and ranking within this group.
        """

    def _parse_batch_response(self, response_text: str, batch_data: List[Dict]) -> Dict[str, Dict]:
        """Parse batch analysis response."""
        try:
            # Try to extract JSON array from response
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]") + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                batch_results = json.loads(json_str)

                # Convert to dict mapping symbols to results
                results = {}
                for result in batch_results:
                    symbol = result.get("symbol", "UNKNOWN")
                    results[symbol] = {
                        "overall_score": result.get("overall_score", 50),
                        "confidence": result.get("confidence", 50),
                        "investment_thesis": result.get("investment_thesis", ""),
                        "key_strengths": [result.get("key_strength", "")],
                        "key_risks": [result.get("key_risk", "")],
                        "position_size": result.get("position_size", 3.0),
                        "relative_rank": result.get("relative_rank", 1),
                        "analysis_method": "batch_llm",
                    }
                return results
            else:
                # Fallback to individual analysis
                results = {}
                for stock_data in batch_data:
                    symbol = stock_data.get("symbol", "UNKNOWN")
                    results[symbol] = self._get_fallback_analysis()
                return results

        except json.JSONDecodeError:
            # Fallback to individual analysis
            results = {}
            for stock_data in batch_data:
                symbol = stock_data.get("symbol", "UNKNOWN")
                results[symbol] = self._get_fallback_analysis()
            return results

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
