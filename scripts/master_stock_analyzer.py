#!/usr/bin/env python3
"""
🚀 MASTER STOCK ANALYZER
The Ultimate Investment Research Tool

A comprehensive stock analysis system with AI-powered insights,
professional-grade testing, and institutional-quality research capabilities.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.analyzer import StockAnalyzer
from data.storage import AnalysisStorage
from pipeline.research_engine import ResearchEngine


class MasterStockAnalyzer:
    """Master Stock Analyzer - The Ultimate Investment Research Tool"""

    def __init__(self):
        """Initialize the master analyzer"""
        self.analyzer = StockAnalyzer()
        self.research_engine = ResearchEngine()
        self.storage = AnalysisStorage()

        # Check if LLM is available
        self.llm_available = self.analyzer.llm_scorer.llm_enabled if hasattr(self.analyzer, "llm_scorer") else False

    def display_header(self):
        """Display the application header"""
        print("\n" + "=" * 60)
        print("🚀 MASTER STOCK ANALYZER")
        print("The Ultimate Investment Research Tool")
        print("=" * 60)

        if self.llm_available:
            print("🤖 AI-Enhanced Analysis: ENABLED")
        else:
            print("📊 Traditional Analysis: ACTIVE")
            print("💡 Tip: Set DEEPSEEK_API_KEY for AI features")
        print()

    def display_menu(self):
        """Display the main menu"""
        print("Choose analysis type:")
        print("1. Single Stock Deep Dive")
        print("2. Quick Universe Scan (S&P 500)")
        print("3. Deep Universe Analysis (Top 20)")
        print("4. Custom Screening")
        print("5. Exit")

    def analyze_single_stock(self):
        """Perform comprehensive analysis on a single stock"""
        symbol = input("Enter stock symbol: ").upper().strip()

        if not symbol:
            print("❌ Please enter a valid symbol")
            return

        print(f"\n🎯 COMPREHENSIVE ANALYSIS FOR {symbol}")
        print("=" * 60)

        try:
            # Phase 1: Enhanced Analysis
            print("📊 Phase 1: Enhanced Fundamental Analysis...")
            print(f"⭐ Scoring {symbol}...")
            print(f"📊 Analyzing {symbol}...")

            # Phase 2: AI Analysis (if available)
            if self.llm_available:
                print("🤖 Phase 2: AI-Powered Analysis...")
                print(f"🔍 Deep diving into {symbol}...")

            # Perform the analysis
            result = self.analyzer.analyze_stock(symbol)

            if not result:
                print(f"❌ Could not analyze {symbol}. Please check the symbol.")
                return

            # Display results
            self.display_analysis_results(result)

            # Store the analysis
            self.storage.store_daily_analysis(
                {
                    "symbol": symbol,
                    "analysis_data": result,
                    "analysis_type": "single_stock_deep_dive",
                }
            )

        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")

    def quick_universe_scan(self):
        """Quick scan of S&P 500 universe"""
        print("\n🔍 QUICK UNIVERSE SCAN")
        print("=" * 60)
        print("📊 Scanning S&P 500 universe...")
        print("⚡ Quick scoring mode activated...")

        try:
            # Get a sample of S&P 500 stocks for quick analysis
            sp500_sample = [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "NVDA",
                "TSLA",
                "META",
                "BRK-B",
                "UNH",
                "JNJ",
            ]

            results = []
            for i, symbol in enumerate(sp500_sample, 1):
                print(f"📈 Analyzing {symbol} ({i}/{len(sp500_sample)})...")
                try:
                    result = self.analyzer.analyze_stock(symbol)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"⚠️  Skipped {symbol}: {str(e)}")
                    continue

            # Sort by composite score
            results.sort(key=lambda x: x.get("composite_score", 0), reverse=True)

            # Display top picks
            print("\n🏆 TOP PICKS FROM UNIVERSE SCAN")
            print("=" * 60)

            for i, result in enumerate(results[:5], 1):
                symbol = result["symbol"]
                score = result.get("composite_score", 0)
                rating = result.get("rating", "N/A")
                confidence = result.get("confidence", "N/A")

                print(f"{i}. {symbol} - Score: {score:.1f} | " f"Rating: {rating} | Confidence: {confidence}")

        except Exception as e:
            print(f"❌ Error in universe scan: {str(e)}")

    def deep_universe_analysis(self):
        """Deep analysis of top universe stocks"""
        print("\n🔬 DEEP UNIVERSE ANALYSIS")
        print("=" * 60)
        print("🎯 Analyzing top 20 stocks with full AI enhancement...")

        try:
            # Use research engine for comprehensive analysis
            results = self.research_engine.run_daily_research(strategy="growth", max_stocks=20, store_results=True)

            if results and "selected_stocks" in results:
                print("\n📊 DEEP ANALYSIS COMPLETE")
                print("=" * 60)
                print(f"✅ Analyzed: {len(results['selected_stocks'])} stocks")
                print(f"📈 Average Score: {results.get('average_score', 0):.1f}")
                print(f"🎯 Strategy: {results.get('strategy', 'N/A').title()}")

                # Display top picks
                for i, stock in enumerate(results["selected_stocks"][:5], 1):
                    symbol = stock.get("symbol", "N/A")
                    score = stock.get("score", 0)
                    rating = stock.get("rating", "N/A")

                    print(f"{i}. {symbol} - Score: {score:.1f} | Rating: {rating}")
            else:
                print("❌ No results from deep analysis")

        except Exception as e:
            print(f"❌ Error in deep analysis: {str(e)}")

    def custom_screening(self):
        """Custom screening functionality"""
        print("\n🎛️  CUSTOM SCREENING")
        print("=" * 60)
        print("Custom screening not yet implemented")
        print("💡 Coming soon: Custom filters, sectors, and criteria")

    def display_analysis_results(self, result):
        """Display comprehensive analysis results"""
        print("\n" + "=" * 60)
        print("📈 INVESTMENT RECOMMENDATION")
        print("=" * 60)

        # Basic info
        rating = result.get("rating", "N/A")
        confidence = result.get("confidence", "N/A")
        score = result.get("composite_score", 0)

        print(f"Rating: {rating}")
        print(f"Confidence: {confidence}")
        print(f"Composite Score: {score:.1f}/100")

        # Detailed scores
        if "fundamental_score" in result:
            print(f"📊 Fundamental Score: {result['fundamental_score']:.1f}")
        if "technical_score" in result:
            print(f"📈 Technical Score: {result['technical_score']:.1f}")
        if "sentiment_score" in result:
            print(f"📰 Sentiment Score: {result['sentiment_score']:.1f}")
        if "risk_score" in result:
            print(f"⚠️  Risk Score: {result['risk_score']:.1f}")

        # AI Analysis (if available)
        if "llm_analysis" in result and result["llm_analysis"]:
            llm_data = result["llm_analysis"]
            if "investment_thesis" in llm_data:
                print("\n🤖 AI Investment Thesis:")
                print(f"   {llm_data['investment_thesis']}")

        # Recommendations
        if "recommendation" in result:
            rec = result["recommendation"]
            if "allocation" in rec:
                print(f"Suggested Allocation: {rec['allocation']}")
            if "time_horizon" in rec:
                print(f"Time Horizon: {rec['time_horizon']}")
            if "risk_level" in rec:
                print(f"Risk Level: {rec['risk_level']}")

        # Fallback for basic recommendation
        if score >= 80:
            allocation = "7-10% of portfolio"
            horizon = "6-18 months (Strong conviction)"
        elif score >= 60:
            allocation = "4-6% of portfolio"
            horizon = "6-18 months (High growth story)"
        elif score >= 40:
            allocation = "2-3% of portfolio"
            horizon = "3-12 months (Moderate position)"
        else:
            allocation = "0% - Avoid"
            horizon = "N/A"

        if "recommendation" not in result:
            print(f"Suggested Allocation: {allocation}")
            print(f"Time Horizon: {horizon}")

    def run(self):
        """Main application loop"""
        self.display_header()

        while True:
            self.display_menu()

            try:
                choice = input("Enter your choice (1-5): ").strip()

                if choice == "1":
                    self.analyze_single_stock()
                elif choice == "2":
                    self.quick_universe_scan()
                elif choice == "3":
                    self.deep_universe_analysis()
                elif choice == "4":
                    self.custom_screening()
                elif choice == "5":
                    print("\n👋 Thank you for using Master Stock Analyzer!")
                    print("🚀 Happy investing!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-5.")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print("Please try again.")


def main():
    """Main entry point"""
    try:
        analyzer = MasterStockAnalyzer()
        analyzer.run()
    except Exception as e:
        print(f"❌ Failed to start Master Stock Analyzer: {str(e)}")
        print("Please check your installation and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
