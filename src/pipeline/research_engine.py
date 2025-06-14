#!/usr/bin/env python3
"""
Automated Research Pipeline
Handles triggers, screening, analysis, and LLM integration
"""

import asyncio
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import yfinance as yf

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.analyzer import StockAnalyzer
from data.storage import AnalysisStorage, DecisionTracker


class StockScreener:
    """
    Advanced stock screening and filtering
    """

    def __init__(self):
        """Initialize screener"""
        self.logger = logging.getLogger(__name__)

    def get_stock_universe(self, strategy: str = "sp500") -> List[str]:
        """Get stock universe based on strategy"""
        universes = {
            "sp500": self._get_sp500_symbols(),
            "nasdaq100": self._get_nasdaq100_symbols(),
            "growth": self._get_growth_symbols(),
            "value": self._get_value_symbols(),
            "mega_cap": self._get_mega_cap_symbols(),
            "ai_stocks": self._get_ai_symbols(),
        }

        return universes.get(strategy, universes["sp500"])

    def _get_sp500_symbols(self) -> List[str]:
        """Get S&P 500 symbols (fallback list)"""
        return [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "NVDA",
            "BRK-B",
            "META",
            "TSLA",
            "UNH",
            "JNJ",
            "JPM",
            "V",
            "PG",
            "HD",
            "MA",
            "ABBV",
            "PFE",
            "KO",
            "AVGO",
            "COST",
            "PEP",
            "TMO",
            "MRK",
            "BAC",
            "NFLX",
            "CRM",
            "DHR",
            "ABT",
            "ORCL",
            "VZ",
            "ADBE",
            "WMT",
            "LLY",
            "CSCO",
            "ACN",
            "NKE",
            "XOM",
            "DIS",
            "MDT",
            "CVX",
            "WFC",
            "BMY",
            "QCOM",
            "NEE",
            "TXN",
            "UPS",
            "AMGN",
            "HON",
            "T",
            "SBUX",
            "LOW",
            "RTX",
            "INTU",
            "PM",
        ]

    def _get_nasdaq100_symbols(self) -> List[str]:
        """Get NASDAQ 100 symbols"""
        return [
            "AAPL",
            "MSFT",
            "GOOGL",
            "GOOG",
            "AMZN",
            "NVDA",
            "META",
            "TSLA",
            "AVGO",
            "COST",
            "NFLX",
            "PEP",
            "ADBE",
            "CSCO",
            "TMUS",
            "CMCSA",
            "INTC",
            "QCOM",
            "TXN",
            "AMGN",
            "HON",
            "AMAT",
            "SBUX",
            "GILD",
            "BKNG",
            "MDLZ",
            "ADP",
            "ISRG",
            "VRTX",
            "FISV",
            "CSX",
            "ADI",
        ]

    def _get_growth_symbols(self) -> List[str]:
        """Get growth stock symbols"""
        return [
            "NVDA",
            "AMD",
            "GOOGL",
            "MSFT",
            "AMZN",
            "META",
            "CRM",
            "SNOW",
            "PLTR",
            "AI",
            "DDOG",
            "CRWD",
            "ZS",
            "NET",
            "OKTA",
            "MRNA",
            "BNTX",
            "REGN",
            "VRTX",
            "ISRG",
            "DXCM",
            "ILMN",
            "SQ",
            "PYPL",
            "TSLA",
            "RIVN",
            "LCID",
            "NIO",
            "SHOP",
            "SE",
            "MELI",
            "ETSY",
        ]

    def _get_value_symbols(self) -> List[str]:
        """Get value stock symbols"""
        return [
            "BRK-B",
            "JPM",
            "BAC",
            "WFC",
            "C",
            "GS",
            "MS",
            "JNJ",
            "PG",
            "KO",
            "PEP",
            "WMT",
            "HD",
            "MCD",
            "ABBV",
            "XOM",
            "CVX",
            "COP",
            "GE",
            "CAT",
            "DE",
            "MMM",
            "BA",
            "VZ",
            "T",
            "NEE",
            "SO",
        ]

    def _get_mega_cap_symbols(self) -> List[str]:
        """Get mega-cap symbols (>$500B market cap)"""
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B"]

    def _get_ai_symbols(self) -> List[str]:
        """Get AI-focused symbols"""
        return [
            "NVDA",
            "AMD",
            "GOOGL",
            "MSFT",
            "AMZN",
            "META",
            "CRM",
            "ORCL",
            "PLTR",
            "AI",
            "SNOW",
            "DDOG",
            "CRWD",
            "ZS",
            "NET",
            "SMCI",
            "AVGO",
            "QCOM",
            "INTC",
            "MU",
            "LRCX",
            "KLAC",
            "AMAT",
            "MRVL",
        ]

    def apply_filters(self, symbols: List[str], filters: Dict) -> List[str]:
        """Apply screening filters to symbol list"""
        filtered_symbols = []

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                if self._passes_filters(info, filters):
                    filtered_symbols.append(symbol)

            except Exception as e:
                self.logger.warning(f"Error filtering {symbol}: {e}")
                continue

        return filtered_symbols

    def _passes_filters(self, info: Dict, filters: Dict) -> bool:
        """Check if stock passes all filters"""
        # Market cap filter
        market_cap = info.get("marketCap", 0)
        if filters.get("min_market_cap") and market_cap < filters["min_market_cap"]:
            return False
        if filters.get("max_market_cap") and market_cap > filters["max_market_cap"]:
            return False

        # P/E filter
        pe_ratio = info.get("trailingPE", 0)
        if filters.get("max_pe") and pe_ratio and pe_ratio > filters["max_pe"]:
            return False
        if filters.get("min_pe") and pe_ratio and pe_ratio < filters["min_pe"]:
            return False

        # ROE filter
        roe = info.get("returnOnEquity", 0)
        if filters.get("min_roe") and roe and roe < filters["min_roe"]:
            return False

        # Revenue growth filter
        revenue_growth = info.get("revenueGrowth", 0)
        if (
            filters.get("min_revenue_growth")
            and revenue_growth
            and revenue_growth < filters["min_revenue_growth"]
        ):
            return False

        # Sector filter
        if filters.get("sectors") and info.get("sector") not in filters["sectors"]:
            return False

        return True


class ResearchEngine:
    """
    Main automated research engine
    Orchestrates screening, analysis, and decision making
    """

    def __init__(self, storage_path: str = "data/stock_analysis.db"):
        """Initialize research engine"""
        self.analyzer = StockAnalyzer()
        self.screener = StockScreener()
        self.storage = AnalysisStorage(storage_path)
        self.decision_tracker = DecisionTracker(self.storage)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    async def run_daily_research(
        self, strategy: str = "growth", max_stocks: int = 50
    ) -> Dict:
        """
        Run complete daily research pipeline

        Args:
            strategy: Stock universe strategy
            max_stocks: Maximum stocks to analyze

        Returns:
            Research results and recommendations
        """
        self.logger.info(f"🚀 Starting daily research pipeline - Strategy: {strategy}")

        try:
            # Step 1: Get stock universe
            universe = self.screener.get_stock_universe(strategy)
            self.logger.info(f"📊 Stock universe: {len(universe)} symbols")

            # Step 2: Apply initial filters (optional)
            filters = self._get_strategy_filters(strategy)
            if filters:
                universe = self.screener.apply_filters(universe, filters)
                self.logger.info(f"🔍 After filtering: {len(universe)} symbols")

            # Step 3: Limit for performance
            if len(universe) > max_stocks:
                universe = universe[:max_stocks]
                self.logger.info(f"⚡ Limited to {max_stocks} stocks for performance")

            # Step 4: Analyze all stocks
            analysis_results = await self._analyze_stock_batch(universe)
            self.logger.info(f"✅ Analyzed {len(analysis_results)} stocks successfully")

            # Step 5: Rank and select top picks
            top_picks = self._select_top_picks(analysis_results)
            self.logger.info(f"🏆 Selected {len(top_picks)} top picks")

            # Step 6: Generate reasoning and decision
            decision_summary = self._generate_decision_reasoning(top_picks, strategy)

            # Step 7: Store results
            await self._store_results(analysis_results, decision_summary)

            # Step 8: Generate final report
            report = self._generate_research_report(
                top_picks, decision_summary, strategy
            )

            self.logger.info("🎯 Daily research pipeline completed successfully")
            return report

        except Exception as e:
            self.logger.error(f"❌ Research pipeline failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def _analyze_stock_batch(self, symbols: List[str]) -> List[Dict]:
        """Analyze a batch of stocks efficiently"""
        results = []

        for i, symbol in enumerate(symbols, 1):
            self.logger.info(f"[{i}/{len(symbols)}] Analyzing {symbol}...")

            try:
                analysis = self.analyzer.analyze_stock(symbol)
                if analysis:
                    results.append(analysis)

                # Small delay to avoid overwhelming APIs
                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.warning(f"Failed to analyze {symbol}: {e}")
                continue

        return results

    def _select_top_picks(
        self, analysis_results: List[Dict], top_n: int = 5
    ) -> List[Dict]:
        """Select top stock picks based on composite scores"""
        # Sort by composite score
        sorted_results = sorted(
            analysis_results, key=lambda x: x["score"]["composite_score"], reverse=True
        )

        # Filter for quality picks (score >= 60)
        quality_picks = [
            r for r in sorted_results if r["score"]["composite_score"] >= 60
        ]

        # Return top N or all quality picks if fewer than N
        return quality_picks[:top_n]

    def _generate_decision_reasoning(
        self, top_picks: List[Dict], strategy: str
    ) -> Dict:
        """Generate comprehensive reasoning for stock selections"""
        if not top_picks:
            return {
                "reasoning": "No stocks met our quality criteria today.",
                "selected_stocks": [],
                "strategy": strategy,
                "market_context": {},
            }

        # Analyze the selections
        avg_score = sum(pick["score"]["composite_score"] for pick in top_picks) / len(
            top_picks
        )
        sectors = list(set(pick["fundamentals"]["sector"] for pick in top_picks))
        ratings = [pick["recommendation"]["rating"] for pick in top_picks]

        # Generate reasoning
        reasoning_parts = [
            f"Selected {len(top_picks)} stocks using {strategy} strategy.",
            f"Average composite score: {avg_score:.1f}/100.",
            f"Sectors represented: {', '.join(sectors)}.",
            f"Ratings distribution: {', '.join(set(ratings))}.",
        ]

        # Add specific insights
        if avg_score >= 75:
            reasoning_parts.append(
                "Exceptionally strong fundamentals across selections."
            )
        elif avg_score >= 65:
            reasoning_parts.append(
                "Solid fundamental strength with good upside potential."
            )

        # Check for common themes
        high_growth_count = sum(
            1 for pick in top_picks if pick["fundamentals"]["revenue_growth"] > 0.15
        )
        if high_growth_count >= len(top_picks) * 0.6:
            reasoning_parts.append(
                f"{high_growth_count} stocks show strong revenue growth (>15%)."
            )

        reasoning = " ".join(reasoning_parts)

        # Prepare stock summaries
        selected_stocks = []
        for pick in top_picks:
            selected_stocks.append(
                {
                    "symbol": pick["symbol"],
                    "score": pick["score"]["composite_score"],
                    "rating": pick["recommendation"]["rating"],
                    "sector": pick["fundamentals"]["sector"],
                    "current_price": pick["fundamentals"]["current_price"],
                    "target_price": pick["fundamentals"]["analyst_target"],
                    "key_strengths": pick["recommendation"]["key_strengths"][:3],
                    "risk_level": pick["risk"]["risk_level"],
                }
            )

        return self.decision_tracker.generate_decision_summary(
            selected_stocks, reasoning
        )

    async def _store_results(
        self, analysis_results: List[Dict], decision_summary: Dict
    ):
        """Store analysis results and decision"""
        # Store individual analyses
        for analysis in analysis_results:
            self.storage.store_daily_analysis(analysis)

        # Store decision summary
        self.storage.store_daily_decision(decision_summary)

        self.logger.info(
            f"💾 Stored {len(analysis_results)} analyses and decision summary"
        )

    def _generate_research_report(
        self, top_picks: List[Dict], decision_summary: Dict, strategy: str
    ) -> Dict:
        """Generate comprehensive research report"""
        report = {
            "date": date.today().isoformat(),
            "strategy": strategy,
            "summary": {
                "total_picks": len(top_picks),
                "avg_score": decision_summary["decision_metadata"]["avg_score"],
                "sectors": decision_summary["decision_metadata"]["sectors_represented"],
                "reasoning": decision_summary["reasoning"],
            },
            "top_picks": [],
            "market_insights": self._generate_market_insights(top_picks),
            "next_actions": self._suggest_next_actions(top_picks),
        }

        # Detailed pick information
        for pick in top_picks:
            pick_detail = {
                "symbol": pick["symbol"],
                "company": pick["fundamentals"]["company_name"],
                "sector": pick["fundamentals"]["sector"],
                "score": pick["score"]["composite_score"],
                "rating": pick["recommendation"]["rating"],
                "confidence": pick["recommendation"]["confidence"],
                "current_price": pick["fundamentals"]["current_price"],
                "target_price": pick["fundamentals"]["analyst_target"],
                "upside_potential": self._calculate_upside(pick),
                "key_metrics": {
                    "pe_ratio": pick["fundamentals"]["pe_ratio"],
                    "roe": pick["fundamentals"]["roe"],
                    "revenue_growth": pick["fundamentals"]["revenue_growth"],
                    "profit_margin": pick["fundamentals"]["profit_margin"],
                },
                "strengths": pick["recommendation"]["key_strengths"],
                "risks": pick["risk"]["identified_risks"],
                "allocation": pick["recommendation"]["suggested_allocation"],
                "time_horizon": pick["recommendation"]["time_horizon"],
            }
            report["top_picks"].append(pick_detail)

        return report

    def _calculate_upside(self, pick: Dict) -> float:
        """Calculate upside potential"""
        current = pick["fundamentals"]["current_price"]
        target = pick["fundamentals"]["analyst_target"]

        if current and target and current > 0:
            return ((target - current) / current) * 100
        return 0

    def _generate_market_insights(self, top_picks: List[Dict]) -> Dict:
        """Generate market insights from analysis"""
        if not top_picks:
            return {}

        # Sector analysis
        sector_counts = {}
        for pick in top_picks:
            sector = pick["fundamentals"]["sector"]
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        # Risk analysis
        risk_levels = [pick["risk"]["risk_level"] for pick in top_picks]
        avg_risk = (
            "Low" if risk_levels.count("Low") > len(risk_levels) / 2 else "Moderate"
        )

        # Growth analysis
        high_growth = sum(
            1 for pick in top_picks if pick["fundamentals"]["revenue_growth"] > 0.15
        )
        growth_focus = high_growth >= len(top_picks) * 0.5

        return {
            "dominant_sectors": sorted(
                sector_counts.items(), key=lambda x: x[1], reverse=True
            ),
            "overall_risk_level": avg_risk,
            "growth_focused": growth_focus,
            "market_sentiment": "Positive" if len(top_picks) >= 3 else "Cautious",
        }

    def _suggest_next_actions(self, top_picks: List[Dict]) -> List[str]:
        """Suggest next actions based on analysis"""
        actions = []

        if not top_picks:
            actions.append(
                "Consider expanding screening criteria or different strategy"
            )
            return actions

        # Portfolio actions
        strong_buys = [
            p for p in top_picks if p["recommendation"]["rating"] == "Strong Buy"
        ]
        if strong_buys:
            actions.append(
                f"Consider immediate positions in {len(strong_buys)} Strong Buy stocks"
            )

        # Monitoring actions
        actions.append("Set price alerts for target prices")
        actions.append("Monitor upcoming earnings dates")

        # Risk management
        high_risk = [p for p in top_picks if p["risk"]["risk_level"] == "High"]
        if high_risk:
            actions.append(
                f"Use smaller position sizes for {len(high_risk)} higher-risk stocks"
            )

        return actions

    def _get_strategy_filters(self, strategy: str) -> Optional[Dict]:
        """Get filters based on strategy"""
        filters = {
            "growth": {"min_revenue_growth": 0.10, "min_market_cap": 1e9},
            "value": {"max_pe": 20, "min_roe": 0.10, "min_market_cap": 5e9},
            "quality": {
                "min_roe": 0.15,
                "max_debt_to_equity": 0.5,
                "min_market_cap": 10e9,
            },
        }

        return filters.get(strategy)

    def get_historical_performance(self, days: int = 30) -> Dict:
        """Get historical performance of recommendations"""
        return self.storage.get_performance_summary()

    def generate_llm_prompt(self, research_report: Dict) -> str:
        """Generate prompt for LLM analysis"""
        prompt = f"""
        Analyze this stock research report and provide deeper insights:

        Date: {research_report['date']}
        Strategy: {research_report['strategy']}

        Summary:
        - Total picks: {research_report['summary']['total_picks']}
        - Average score: {research_report['summary']['avg_score']:.1f}/100
        - Sectors: {', '.join(research_report['summary']['sectors'])}
        - Reasoning: {research_report['summary']['reasoning']}

        Top Picks:
        """

        for pick in research_report["top_picks"]:
            prompt += f"""
        {pick['symbol']} ({pick['company']}):
        - Score: {pick['score']:.1f}/100, Rating: {pick['rating']}
        - Price: ${pick['current_price']:.2f}, Target: ${pick['target_price']:.2f}
        - Upside: {pick['upside_potential']:.1f}%
        - Key metrics: PE {pick['key_metrics']['pe_ratio']:.1f}, ROE {pick['key_metrics']['roe']*100:.1f}%
        - Strengths: {', '.join(pick['strengths'][:2])}
        """

        prompt += """

        Please provide:
        1. Market trend analysis based on these selections
        2. Risk assessment and portfolio allocation suggestions
        3. Timing considerations for entry/exit
        4. Alternative stocks to consider
        5. Overall investment thesis
        """

        return prompt


# Trigger system for automated execution
class ResearchTrigger:
    """
    Handles automated triggers for research pipeline
    """

    def __init__(self, engine: ResearchEngine):
        """Initialize trigger system"""
        self.engine = engine
        self.logger = logging.getLogger(__name__)

    async def daily_trigger(self, strategy: str = "growth"):
        """Daily research trigger"""
        self.logger.info("🔔 Daily research trigger activated")

        try:
            report = await self.engine.run_daily_research(strategy)

            if "error" not in report:
                self.logger.info("✅ Daily research completed successfully")
                return report
            else:
                self.logger.error(f"❌ Daily research failed: {report['error']}")
                return None

        except Exception as e:
            self.logger.error(f"❌ Trigger execution failed: {e}")
            return None

    def market_hours_trigger(self):
        """Trigger during market hours for real-time updates"""
        # Implementation for market hours monitoring
        pass

    def news_event_trigger(self, event_type: str):
        """Trigger based on news events"""
        # Implementation for news-based triggers
        pass
