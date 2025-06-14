#!/usr/bin/env python3
"""
Stock Research System - Main Application
Clean, modular interface for automated stock research
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data.storage import AnalysisStorage
from pipeline.research_engine import ResearchEngine, ResearchTrigger


class StockResearchApp:
    """
    Main application for the stock research system
    """

    def __init__(self):
        """Initialize the application"""
        self.engine = ResearchEngine()
        self.trigger = ResearchTrigger(self.engine)
        self.storage = AnalysisStorage()

        print("🚀 Stock Research System Initialized")
        print("=" * 60)

    async def run_daily_research(self, strategy: str = "growth", max_stocks: int = 30):
        """Run daily research pipeline"""
        print(f"\n🔍 Running Daily Research - Strategy: {strategy.upper()}")
        print("-" * 50)

        try:
            # Run the research pipeline
            report = await self.engine.run_daily_research(strategy, max_stocks)

            if "error" in report:
                print(f"❌ Research failed: {report['error']}")
                return None

            # Display results
            self._display_research_report(report)

            # Generate LLM prompt for deeper analysis
            llm_prompt = self.engine.generate_llm_prompt(report)
            self._save_llm_prompt(llm_prompt, report["date"])

            return report

        except Exception as e:
            print(f"❌ Application error: {e}")
            return None

    def _display_research_report(self, report: Dict):
        """Display research report in a clean format"""
        print(f"\n📊 RESEARCH REPORT - {report['date']}")
        print("=" * 60)

        # Summary
        summary = report["summary"]
        print(f"Strategy: {report['strategy'].upper()}")
        print(f"Total Picks: {summary['total_picks']}")
        print(f"Average Score: {summary['avg_score']:.1f}/100")
        print(f"Sectors: {', '.join(summary['sectors'])}")
        print(f"\nReasoning: {summary['reasoning']}")

        # Top Picks
        print("\n🏆 TOP STOCK PICKS")
        print("-" * 50)

        for i, pick in enumerate(report["top_picks"], 1):
            print(f"\n{i}. {pick['symbol']} - {pick['company']}")
            print(
                f"   Score: {pick['score']:.1f}/100 | Rating: {pick['rating']} | Confidence: {pick['confidence']}"
            )
            print(f"   Sector: {pick['sector']}")
            print(
                f"   Price: ${pick['current_price']:.2f} → Target: ${pick['target_price']:.2f} ({pick['upside_potential']:+.1f}%)"
            )
            print(
                f"   Allocation: {pick['allocation']} | Time Horizon: {pick['time_horizon']}"
            )

            # Key metrics
            metrics = pick["key_metrics"]
            print(
                f"   Metrics: PE {metrics['pe_ratio']:.1f} | ROE {metrics['roe']*100:.1f}% | Growth {metrics['revenue_growth']*100:.1f}%"
            )

            # Strengths (top 3)
            if pick["strengths"]:
                print(f"   Strengths: {', '.join(pick['strengths'][:3])}")

        # Market Insights
        insights = report["market_insights"]
        print("\n💡 MARKET INSIGHTS")
        print("-" * 30)
        print(f"Dominant Sectors: {dict(insights['dominant_sectors'][:3])}")
        print(f"Overall Risk Level: {insights['overall_risk_level']}")
        print(f"Growth Focused: {'Yes' if insights['growth_focused'] else 'No'}")
        print(f"Market Sentiment: {insights['market_sentiment']}")

        # Next Actions
        print("\n📋 RECOMMENDED ACTIONS")
        print("-" * 30)
        for action in report["next_actions"]:
            print(f"• {action}")

    def _save_llm_prompt(self, prompt: str, date: str):
        """Save LLM prompt for external analysis"""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        prompt_file = output_dir / f"llm_prompt_{date}.txt"
        with open(prompt_file, "w") as f:
            f.write(prompt)

        print(f"\n💾 LLM prompt saved to: {prompt_file}")

    def get_historical_performance(self):
        """Display historical performance"""
        print("\n📈 HISTORICAL PERFORMANCE")
        print("-" * 40)

        performance = self.storage.get_performance_summary()

        if not performance:
            print("No historical performance data available.")
            return

        print(f"Active Positions: {performance['total_positions']}")
        print(f"Average Return: {performance['average_return']:.2f}%")
        print(f"Total Return: {performance['total_return']:.2f}%")

        if performance["active_positions"]:
            print("\nActive Positions:")
            for pos in performance["active_positions"]:
                print(
                    f"  {pos['symbol']}: {pos['return_pct']:+.2f}% ({pos['days_held']} days)"
                )

    def get_recent_decisions(self, days: int = 7):
        """Display recent decisions"""
        print(f"\n📋 RECENT DECISIONS ({days} days)")
        print("-" * 40)

        decisions = self.storage.get_daily_decisions(days)

        if not decisions:
            print("No recent decisions found.")
            return

        for decision in decisions:
            print(f"\n{decision['date']} - {decision['decision_type']}")
            print(f"Reasoning: {decision['reasoning']}")

            if decision["selected_stocks"]:
                symbols = [
                    stock.get("symbol", "Unknown")
                    for stock in decision["selected_stocks"]
                ]
                print(f"Selected: {', '.join(symbols)}")

    def analyze_single_stock(self, symbol: str):
        """Analyze a single stock"""
        print(f"\n🔍 ANALYZING {symbol.upper()}")
        print("-" * 30)

        analysis = self.engine.analyzer.analyze_stock(symbol)

        if not analysis:
            print(f"❌ Failed to analyze {symbol}")
            return

        # Display key information
        fund = analysis["fundamentals"]
        rec = analysis["recommendation"]
        score = analysis["score"]

        print(f"Company: {fund['company_name']}")
        print(f"Sector: {fund['sector']}")
        print(f"Score: {score['composite_score']:.1f}/100")
        print(f"Rating: {rec['rating']} ({rec['confidence']} confidence)")
        print(f"Current Price: ${fund['current_price']:.2f}")
        print(f"Target Price: ${fund['analyst_target']:.2f}")
        print(f"Allocation: {rec['suggested_allocation']}")
        print(f"Time Horizon: {rec['time_horizon']}")

        if rec["key_strengths"]:
            print(f"Key Strengths: {', '.join(rec['key_strengths'][:3])}")

        # Store the analysis
        self.storage.store_daily_analysis(analysis)
        print(f"✅ Analysis stored for {symbol}")


async def main():
    """Main application entry point"""
    app = StockResearchApp()

    print("\n🎯 STOCK RESEARCH SYSTEM")
    print("Choose an option:")
    print("1. Run Daily Research (Growth Strategy)")
    print("2. Run Daily Research (Value Strategy)")
    print("3. Run Daily Research (AI Stocks)")
    print("4. Analyze Single Stock")
    print("5. View Historical Performance")
    print("6. View Recent Decisions")
    print("7. Exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                await app.run_daily_research("growth", 25)

            elif choice == "2":
                await app.run_daily_research("value", 25)

            elif choice == "3":
                await app.run_daily_research("ai_stocks", 20)

            elif choice == "4":
                symbol = input("Enter stock symbol: ").strip().upper()
                if symbol:
                    app.analyze_single_stock(symbol)

            elif choice == "5":
                app.get_historical_performance()

            elif choice == "6":
                app.get_recent_decisions()

            elif choice == "7":
                print("\n👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1-7.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
