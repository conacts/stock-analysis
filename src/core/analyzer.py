#!/usr/bin/env python3
"""
Core Stock Analyzer
Consolidated, clean analysis engine combining fundamental + AI insights
Enhanced with LLM integration for sophisticated analysis
"""

import logging
import warnings
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import yfinance as yf

warnings.filterwarnings("ignore")

# Import LLM components
try:
    from ..llm import LLMScorer

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.warning("LLM module not available. Using traditional scoring only.")

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """
    Core stock analysis engine
    Combines fundamental analysis, AI insights, and market data
    """

    def __init__(self, enable_llm: bool = True, deepseek_api_key: Optional[str] = None):
        """
        Initialize the analyzer

        Args:
            enable_llm: Whether to enable LLM-enhanced analysis
            deepseek_api_key: DeepSeek API key for LLM analysis
        """
        self.sector_benchmarks = {
            "Technology": {"avg_pe": 25, "avg_roe": 0.20, "avg_debt_equity": 0.3},
            "Healthcare": {"avg_pe": 20, "avg_roe": 0.15, "avg_debt_equity": 0.4},
            "Financial Services": {
                "avg_pe": 12,
                "avg_roe": 0.12,
                "avg_debt_equity": 0.8,
            },
            "Consumer Cyclical": {
                "avg_pe": 18,
                "avg_roe": 0.15,
                "avg_debt_equity": 0.5,
            },
            "Consumer Defensive": {
                "avg_pe": 22,
                "avg_roe": 0.18,
                "avg_debt_equity": 0.4,
            },
            "Energy": {"avg_pe": 15, "avg_roe": 0.10, "avg_debt_equity": 0.6},
            "Industrials": {"avg_pe": 20, "avg_roe": 0.12, "avg_debt_equity": 0.5},
            "Materials": {"avg_pe": 16, "avg_roe": 0.10, "avg_debt_equity": 0.4},
            "Real Estate": {"avg_pe": 25, "avg_roe": 0.08, "avg_debt_equity": 0.7},
            "Utilities": {"avg_pe": 18, "avg_roe": 0.09, "avg_debt_equity": 0.6},
            "Communication Services": {
                "avg_pe": 22,
                "avg_roe": 0.15,
                "avg_debt_equity": 0.4,
            },
        }

        # Initialize LLM scorer if available and enabled
        self.llm_scorer = None
        if enable_llm and LLM_AVAILABLE:
            try:
                self.llm_scorer = LLMScorer(deepseek_api_key)
                logger.info("LLM-enhanced analysis enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM scorer: {e}")
                self.llm_scorer = None
        else:
            logger.info("Using traditional analysis (LLM disabled or unavailable)")

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """
        Comprehensive stock analysis

        Args:
            symbol: Stock ticker symbol

        Returns:
            Complete analysis dictionary or None if failed
        """
        try:
            # Get stock data
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or "currentPrice" not in info:
                return None

            # Core analysis components
            fundamentals = self._analyze_fundamentals(info, symbol)
            technical = self._analyze_technical(ticker, symbol)
            sentiment = self._analyze_sentiment(ticker, info, symbol)
            risk = self._assess_risk(info, sentiment)

            # Calculate enhanced composite score with LLM if available
            if self.llm_scorer:
                score = self._calculate_enhanced_score(
                    symbol, fundamentals, technical, sentiment, risk, info, ticker
                )
            else:
                score = self._calculate_composite_score(
                    fundamentals, technical, sentiment, risk
                )

            # Generate recommendation
            recommendation = self._generate_recommendation(
                fundamentals, technical, sentiment, risk, score
            )

            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "fundamentals": fundamentals,
                "technical": technical,
                "sentiment": sentiment,
                "risk": risk,
                "score": score,
                "recommendation": recommendation,
            }

        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None

    def _analyze_fundamentals(self, info: Dict, symbol: str) -> Dict:
        """Analyze fundamental metrics"""
        sector = info.get("sector", "Unknown")
        benchmarks = self.sector_benchmarks.get(
            sector, self.sector_benchmarks["Technology"]
        )

        # Extract key metrics
        metrics = {
            "company_name": info.get("longName", symbol),
            "sector": sector,
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap", 0),
            "current_price": info.get("currentPrice", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "forward_pe": info.get("forwardPE", 0),
            "peg_ratio": info.get("pegRatio", 0),
            "price_to_sales": info.get("priceToSalesTrailing12Months", 0),
            "price_to_book": info.get("priceToBook", 0),
            "ev_ebitda": info.get("enterpriseToEbitda", 0),
            "profit_margin": info.get("profitMargins", 0),
            "operating_margin": info.get("operatingMargins", 0),
            "gross_margin": info.get("grossMargins", 0),
            "roe": info.get("returnOnEquity", 0),
            "roa": info.get("returnOnAssets", 0),
            "revenue_growth": info.get("revenueGrowth", 0),
            "earnings_growth": info.get("earningsGrowth", 0),
            "debt_to_equity": info.get("debtToEquity", 0),
            "current_ratio": info.get("currentRatio", 0),
            "quick_ratio": info.get("quickRatio", 0),
            "cash_per_share": info.get("totalCashPerShare", 0),
            "free_cash_flow": info.get("freeCashflow", 0),
            "dividend_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 1.0),
            "analyst_target": info.get("targetMeanPrice", 0),
            "num_analysts": info.get("numberOfAnalystOpinions", 0),
            "recommendation_mean": info.get("recommendationMean", 3),
        }

        # Calculate fundamental score (0-100)
        score = self._score_fundamentals(metrics, benchmarks)

        return {**metrics, "fundamental_score": score, "sector_benchmarks": benchmarks}

    def _analyze_technical(self, ticker, symbol: str) -> Dict:
        """Analyze technical indicators"""
        try:
            # Get historical data
            hist = ticker.history(period="6mo")

            if hist.empty:
                return {"technical_score": 50, "indicators": {}}

            # Calculate technical indicators
            current_price = hist["Close"].iloc[-1]

            # Moving averages
            ma_20 = hist["Close"].rolling(20).mean().iloc[-1]
            ma_50 = hist["Close"].rolling(50).mean().iloc[-1]

            # Price momentum
            momentum_1m = (
                (current_price - hist["Close"].iloc[-21]) / hist["Close"].iloc[-21]
                if len(hist) > 21
                else 0
            )
            momentum_3m = (
                (current_price - hist["Close"].iloc[-63]) / hist["Close"].iloc[-63]
                if len(hist) > 63
                else 0
            )

            # Volume analysis
            avg_volume = hist["Volume"].mean()
            recent_volume = hist["Volume"].iloc[-5:].mean()
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

            # Volatility
            volatility = hist["Close"].pct_change().std() * np.sqrt(252)  # Annualized

            indicators = {
                "current_price": current_price,
                "ma_20": ma_20,
                "ma_50": ma_50,
                "price_vs_ma20": (current_price - ma_20) / ma_20 if ma_20 > 0 else 0,
                "price_vs_ma50": (current_price - ma_50) / ma_50 if ma_50 > 0 else 0,
                "momentum_1m": momentum_1m,
                "momentum_3m": momentum_3m,
                "volume_ratio": volume_ratio,
                "volatility": volatility,
            }

            # Calculate technical score
            score = self._score_technical(indicators)

            return {"technical_score": score, "indicators": indicators}

        except Exception as e:
            return {"technical_score": 50, "indicators": {}, "error": str(e)}

    def _analyze_sentiment(self, ticker, info: Dict, symbol: str) -> Dict:
        """Analyze market sentiment and news"""
        try:
            # Get recent news
            news = ticker.news[:10] if hasattr(ticker, "news") else []

            # Analyze news sentiment
            sentiment_score = 0
            themes = []

            if news:
                # Simple sentiment analysis based on keywords
                positive_words = [
                    "beat",
                    "strong",
                    "growth",
                    "positive",
                    "upgrade",
                    "buy",
                    "outperform",
                ]
                negative_words = [
                    "miss",
                    "weak",
                    "decline",
                    "negative",
                    "downgrade",
                    "sell",
                    "underperform",
                ]

                for article in news:
                    title = article.get("title", "").lower()

                    pos_count = sum(1 for word in positive_words if word in title)
                    neg_count = sum(1 for word in negative_words if word in title)

                    if pos_count > neg_count:
                        sentiment_score += 1
                    elif neg_count > pos_count:
                        sentiment_score -= 1

            # Analyst sentiment
            recommendation = info.get("recommendationMean", 3)
            analyst_sentiment = (
                "Buy"
                if recommendation < 2.5
                else "Hold"
                if recommendation < 3.5
                else "Sell"
            )

            # Overall sentiment
            if sentiment_score > 2:
                overall_sentiment = "Very Positive"
            elif sentiment_score > 0:
                overall_sentiment = "Positive"
            elif sentiment_score < -2:
                overall_sentiment = "Very Negative"
            elif sentiment_score < 0:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"

            return {
                "sentiment_score": sentiment_score,
                "overall_sentiment": overall_sentiment,
                "analyst_sentiment": analyst_sentiment,
                "news_count": len(news),
                "themes": themes,
            }

        except Exception as e:
            return {
                "sentiment_score": 0,
                "overall_sentiment": "Neutral",
                "analyst_sentiment": "Hold",
                "news_count": 0,
                "themes": [],
                "error": str(e),
            }

    def _assess_risk(self, info: Dict, sentiment: Dict) -> Dict:
        """Assess investment risks"""
        risks = []
        risk_score = 0  # 0-10 scale (higher = more risky)

        # Financial risks
        debt_to_equity = info.get("debtToEquity", 0)
        if debt_to_equity > 1.0:
            risks.append("High debt levels")
            risk_score += 2

        current_ratio = info.get("currentRatio", 0)
        if current_ratio and current_ratio < 1.0:
            risks.append("Liquidity concerns")
            risk_score += 2

        # Market risks
        beta = info.get("beta", 1.0)
        if beta > 1.5:
            risks.append("High market volatility")
            risk_score += 1

        # Sentiment risks
        if sentiment.get("overall_sentiment") in ["Negative", "Very Negative"]:
            risks.append("Negative market sentiment")
            risk_score += 1

        # Valuation risks
        pe_ratio = info.get("trailingPE", 0)
        if pe_ratio > 40:
            risks.append("High valuation risk")
            risk_score += 1

        risk_level = (
            "Low" if risk_score <= 3 else "Moderate" if risk_score <= 6 else "High"
        )

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "identified_risks": risks,
        }

    def _score_fundamentals(self, metrics: Dict, benchmarks: Dict) -> float:
        """Score fundamental metrics (0-100)"""
        score = 0
        max_score = 100

        # Valuation scoring (25 points)
        pe_ratio = metrics.get("pe_ratio", 0)
        if pe_ratio > 0:
            if pe_ratio < benchmarks["avg_pe"] * 0.8:
                score += 25
            elif pe_ratio < benchmarks["avg_pe"]:
                score += 15
            elif pe_ratio < benchmarks["avg_pe"] * 1.2:
                score += 10

        # Profitability scoring (25 points)
        roe = metrics.get("roe", 0)
        if roe is not None and roe > 0:
            if roe > benchmarks["avg_roe"] * 1.5:
                score += 25
            elif roe > benchmarks["avg_roe"]:
                score += 15
            elif roe > benchmarks["avg_roe"] * 0.5:
                score += 10

        # Growth scoring (25 points)
        revenue_growth = metrics.get("revenue_growth", 0)
        if revenue_growth > 0.20:
            score += 25
        elif revenue_growth > 0.10:
            score += 15
        elif revenue_growth > 0.05:
            score += 10

        # Financial health scoring (25 points)
        debt_to_equity = metrics.get("debt_to_equity", 0)
        current_ratio = metrics.get("current_ratio", 0)

        if debt_to_equity < benchmarks["avg_debt_equity"] * 0.5:
            score += 15
        elif debt_to_equity < benchmarks["avg_debt_equity"]:
            score += 10

        if current_ratio > 2.0:
            score += 10
        elif current_ratio > 1.5:
            score += 5

        return min(score, max_score)

    def _score_technical(self, indicators: Dict) -> float:
        """Score technical indicators (0-100)"""
        score = 50  # Base score

        # Price vs moving averages
        if indicators.get("price_vs_ma20", 0) > 0.05:
            score += 15
        elif indicators.get("price_vs_ma20", 0) > 0:
            score += 5

        if indicators.get("price_vs_ma50", 0) > 0.05:
            score += 15
        elif indicators.get("price_vs_ma50", 0) > 0:
            score += 5

        # Momentum
        momentum_1m = indicators.get("momentum_1m", 0)
        if momentum_1m > 0.10:
            score += 10
        elif momentum_1m > 0.05:
            score += 5
        elif momentum_1m < -0.10:
            score -= 10
        elif momentum_1m < -0.05:
            score -= 5

        # Volume
        volume_ratio = indicators.get("volume_ratio", 1)
        if volume_ratio > 1.5:
            score += 5
        elif volume_ratio < 0.5:
            score -= 5

        return max(0, min(100, score))

    def _calculate_enhanced_score(
        self,
        symbol: str,
        fundamentals: Dict,
        technical: Dict,
        sentiment: Dict,
        risk: Dict,
        info: Dict,
        ticker,
    ) -> Dict:
        """Calculate LLM-enhanced composite score"""
        try:
            # Prepare data for LLM analysis
            financial_data = {
                "market_cap": fundamentals.get("market_cap", 0),
                "pe_ratio": fundamentals.get("pe_ratio", 0),
                "revenue_growth": fundamentals.get("revenue_growth", 0),
                "profit_margin": fundamentals.get("profit_margin", 0),
                "roe": fundamentals.get("roe", 0),
                "debt_to_equity": fundamentals.get("debt_to_equity", 0),
                "current_ratio": fundamentals.get("current_ratio", 0),
                "price_to_book": fundamentals.get("price_to_book", 0),
            }

            # Get news data for LLM analysis
            news_data = []
            try:
                news = ticker.news[:10] if hasattr(ticker, "news") else []
                for article in news:
                    news_data.append(
                        {
                            "title": article.get("title", ""),
                            "summary": article.get("summary", ""),
                            "date": article.get("providerPublishTime", ""),
                        }
                    )
            except Exception:
                news_data = []

            # Prepare technical data
            technical_data = technical.get("indicators", {})

            # Prepare market context
            market_context = {
                "sector": fundamentals.get("sector", "Unknown"),
                "market_trend": "neutral",  # Could be enhanced with market data
                "sector_performance": "neutral",
                "vix": "unknown",
                "interest_rates": "unknown",
            }

            # Get individual component scores
            fund_score = fundamentals.get("fundamental_score", 50)
            tech_score = technical.get("technical_score", 50)
            sent_score = 50 + (sentiment.get("sentiment_score", 0) * 10)
            sent_score = max(0, min(100, sent_score))
            risk_score = max(0, 100 - (risk.get("risk_score", 5) * 10))

            # Use LLM scorer for enhanced analysis
            enhanced_result = self.llm_scorer.calculate_enhanced_score(
                symbol=symbol,
                fundamental_score=fund_score,
                technical_score=tech_score,
                sentiment_score=sent_score,
                risk_score=risk_score,
                financial_data=financial_data,
                news_data=news_data,
                technical_data=technical_data,
                market_context=market_context,
            )

            # Add traditional component scores for compatibility
            enhanced_result.update(
                {
                    "fundamental_score": fund_score,
                    "technical_score": tech_score,
                    "sentiment_score": sent_score,
                    "risk_score": risk_score,
                }
            )

            return enhanced_result

        except Exception as e:
            logger.error(f"Error in enhanced scoring for {symbol}: {e}")
            # Fallback to traditional scoring
            return self._calculate_composite_score(
                fundamentals, technical, sentiment, risk
            )

    def _calculate_composite_score(
        self, fundamentals: Dict, technical: Dict, sentiment: Dict, risk: Dict
    ) -> Dict:
        """Calculate weighted composite score"""
        # Weights
        fundamental_weight = 0.50
        technical_weight = 0.25
        sentiment_weight = 0.15
        risk_weight = 0.10

        # Individual scores
        fund_score = fundamentals.get("fundamental_score", 50)
        tech_score = technical.get("technical_score", 50)

        # Sentiment score (convert to 0-100)
        sent_score = 50 + (sentiment.get("sentiment_score", 0) * 10)
        sent_score = max(0, min(100, sent_score))

        # Risk score (invert - lower risk = higher score)
        risk_score = max(0, 100 - (risk.get("risk_score", 5) * 10))

        # Weighted composite
        composite = (
            fund_score * fundamental_weight
            + tech_score * technical_weight
            + sent_score * sentiment_weight
            + risk_score * risk_weight
        )

        return {
            "composite_score": round(composite, 1),
            "fundamental_score": fund_score,
            "technical_score": tech_score,
            "sentiment_score": sent_score,
            "risk_score": risk_score,
            "weights": {
                "fundamental": fundamental_weight,
                "technical": technical_weight,
                "sentiment": sentiment_weight,
                "risk": risk_weight,
            },
        }

    def _generate_recommendation(
        self,
        fundamentals: Dict,
        technical: Dict,
        sentiment: Dict,
        risk: Dict,
        score: Dict,
    ) -> Dict:
        """Generate investment recommendation"""
        composite_score = score["composite_score"]

        # Check if this is LLM-enhanced analysis
        is_llm_enhanced = score.get("analysis_method") == "llm_enhanced"

        if is_llm_enhanced:
            # Use LLM-generated recommendation data
            llm_analysis = score.get("llm_analysis", {})
            news_impact = score.get("news_impact", {})
            growth_catalysts = score.get("growth_catalysts", {})

            rating = score.get("rating", "Hold")
            confidence = score.get("confidence", 50)

            # Convert confidence to string
            if confidence >= 80:
                confidence_str = "High"
            elif confidence >= 60:
                confidence_str = "Moderate"
            else:
                confidence_str = "Low"

            # Get allocation from LLM analysis
            position_size = llm_analysis.get("position_size", 3.0)
            allocation = f"{position_size:.1f}%"

            return {
                "rating": rating,
                "confidence": confidence_str,
                "confidence_score": confidence,
                "suggested_allocation": allocation,
                "time_horizon": llm_analysis.get("time_horizon", "medium"),
                "investment_thesis": llm_analysis.get("investment_thesis", ""),
                "key_strengths": llm_analysis.get("key_strengths", []),
                "key_risks": llm_analysis.get("key_risks", []),
                "price_target": fundamentals.get("analyst_target", 0),
                "current_price": fundamentals.get("current_price", 0),
                "catalyst_timeline": llm_analysis.get("catalyst_timeline", "unknown"),
                "news_sentiment": news_impact.get("sentiment", "neutral"),
                "key_catalysts": news_impact.get("key_catalysts", []),
                "growth_conviction": growth_catalysts.get("conviction", "medium"),
                "analysis_method": "llm_enhanced",
            }
        else:
            # Traditional recommendation logic
            if composite_score >= 80:
                rating = "Strong Buy"
                allocation = "8-10%"
            elif composite_score >= 70:
                rating = "Buy"
                allocation = "5-7%"
            elif composite_score >= 60:
                rating = "Moderate Buy"
                allocation = "3-5%"
            elif composite_score >= 50:
                rating = "Hold"
                allocation = "1-3%"
            elif composite_score >= 40:
                rating = "Weak Hold"
                allocation = "0-1%"
            else:
                rating = "Sell"
                allocation = "0%"

            # Time horizon based on growth
            revenue_growth = fundamentals.get("revenue_growth", 0)

            if revenue_growth > 0.3:
                time_horizon = "6-18 months"
            elif revenue_growth > 0.15:
                time_horizon = "1-3 years"
            else:
                time_horizon = "3-5 years"

            # Confidence based on data quality
            confidence = (
                "High" if fundamentals.get("num_analysts", 0) > 10 else "Moderate"
            )

            return {
                "rating": rating,
                "confidence": confidence,
                "suggested_allocation": allocation,
                "time_horizon": time_horizon,
                "key_strengths": self._identify_strengths(
                    fundamentals, technical, sentiment
                ),
                "key_risks": risk.get("identified_risks", []),
                "price_target": fundamentals.get("analyst_target", 0),
                "current_price": fundamentals.get("current_price", 0),
                "analysis_method": "traditional",
            }

    def _identify_strengths(
        self, fundamentals: Dict, technical: Dict, sentiment: Dict
    ) -> List[str]:
        """Identify key investment strengths"""
        strengths = []

        # Fundamental strengths
        if fundamentals.get("roe", 0) > 0.20:
            strengths.append(f"Excellent ROE ({fundamentals['roe']*100:.1f}%)")

        if fundamentals.get("profit_margin", 0) > 0.15:
            strengths.append(
                f"High profit margins ({fundamentals['profit_margin']*100:.1f}%)"
            )

        if fundamentals.get("revenue_growth", 0) > 0.15:
            strengths.append(
                f"Strong revenue growth ({fundamentals['revenue_growth']*100:.1f}%)"
            )

        # Technical strengths
        indicators = technical.get("indicators", {})
        if indicators.get("momentum_1m", 0) > 0.05:
            strengths.append("Positive price momentum")

        # Sentiment strengths
        if sentiment.get("overall_sentiment") in ["Positive", "Very Positive"]:
            strengths.append("Positive market sentiment")

        return strengths[:5]  # Top 5 strengths
