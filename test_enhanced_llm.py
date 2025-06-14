#!/usr/bin/env python3
"""
Test Enhanced LLM Integration

Demonstrates the new features:
- Enhanced prompts with sector-specific analysis
- Cost tracking and optimization
- Response caching
- Batch processing
- Improved error handling
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, "src")

from core.analyzer import StockAnalyzer
from llm.deepseek_analyzer import DeepSeekAnalyzer


def test_enhanced_features():
    """Test the enhanced LLM features."""
    print("🚀 Testing Enhanced LLM Integration")
    print("=" * 60)

    # Check if API key is available
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️  DEEPSEEK_API_KEY not found. Testing with LLM disabled.")
        print("   Set DEEPSEEK_API_KEY environment variable to test LLM features.")
        test_without_llm()
        return

    print(f"✅ DeepSeek API key found: {api_key[:8]}...")

    # Test 1: Enhanced Analyzer with Caching
    print("\n📊 Test 1: Enhanced Stock Analyzer")
    print("-" * 40)

    analyzer = StockAnalyzer(enable_llm=True, deepseek_api_key=api_key)

    # Analyze a stock
    print("Analyzing AAPL...")
    result = analyzer.analyze_stock("AAPL")

    if result:
        score = result.get("score", {})
        recommendation = result.get("recommendation", {})

        print("✅ Analysis completed successfully")
        print(f"   Composite Score: {score.get('composite_score', 'N/A')}")
        print(f"   Rating: {recommendation.get('rating', 'N/A')}")
        print(f"   Analysis Method: {score.get('analysis_method', 'traditional')}")

        if score.get("analysis_method") == "llm_enhanced":
            llm_analysis = score.get("llm_analysis", {})
            print(f"   Investment Thesis: {llm_analysis.get('investment_thesis', 'N/A')[:100]}...")
            print(f"   Time Horizon: {llm_analysis.get('time_horizon', 'N/A')}")
            print(f"   Position Size: {llm_analysis.get('position_size', 'N/A')}%")
    else:
        print("❌ Analysis failed")

    # Test 2: Cost Summary
    print("\n💰 Test 2: Cost Tracking")
    print("-" * 40)

    cost_summary = analyzer.get_llm_cost_summary()
    print(f"API Calls Made: {cost_summary.get('api_calls_made', 0)}")
    print(f"Total Tokens Used: {cost_summary.get('total_tokens_used', 0)}")
    print(f"Total Cost: ${cost_summary.get('total_cost_usd', 0):.4f}")
    print(f"Average Cost per Call: ${cost_summary.get('average_cost_per_call', 0):.4f}")
    print(f"Cache Hit Rate: {cost_summary.get('cache_hit_rate', 0):.1%}")

    # Test 3: Batch Analysis
    print("\n🔄 Test 3: Batch Analysis")
    print("-" * 40)

    symbols = ["AAPL", "GOOGL", "MSFT"]
    print(f"Batch analyzing: {', '.join(symbols)}")

    batch_results = analyzer.batch_analyze_stocks(symbols)

    for symbol, result in batch_results.items():
        if result:
            score = result.get("score", {})
            print(f"   {symbol}: Score {score.get('composite_score', 'N/A')} " f"({score.get('analysis_method', 'traditional')})")
        else:
            print(f"   {symbol}: Analysis failed")

    # Test 4: Cache Performance
    print("\n⚡ Test 4: Cache Performance")
    print("-" * 40)

    print("Re-analyzing AAPL to test caching...")
    start_time = datetime.now()
    analyzer.analyze_stock("AAPL")  # Second analysis to test caching
    end_time = datetime.now()

    duration = (end_time - start_time).total_seconds()
    print(f"Second analysis took: {duration:.2f} seconds")

    # Updated cost summary
    cost_summary2 = analyzer.get_llm_cost_summary()
    print(f"Updated Cache Hit Rate: {cost_summary2.get('cache_hit_rate', 0):.1%}")

    # Test 5: Direct LLM Components
    print("\n🧠 Test 5: Direct LLM Components")
    print("-" * 40)

    try:
        llm_analyzer = DeepSeekAnalyzer(api_key=api_key, enable_caching=True)

        # Test news analysis
        sample_news = [{"title": "Apple Reports Strong Q4 Earnings", "summary": "Apple exceeded expectations with revenue growth of 8% year-over-year", "date": "2024-01-01"}]

        news_result = llm_analyzer.analyze_news_impact("AAPL", sample_news)
        print(f"News Impact Score: {news_result.get('impact_score', 'N/A')}")
        print(f"News Sentiment: {news_result.get('sentiment', 'N/A')}")

        # Get final cost summary
        final_cost = llm_analyzer.get_cost_summary()
        print("\nFinal LLM Cost Summary:")
        print(f"   Total API Calls: {final_cost.get('api_calls_made', 0)}")
        print(f"   Total Cost: ${final_cost.get('total_cost_usd', 0):.4f}")

    except Exception as e:
        print(f"❌ Direct LLM test failed: {e}")

    print("\n🎉 Enhanced LLM Integration Test Complete!")


def test_without_llm():
    """Test analyzer without LLM to show fallback behavior."""
    print("\n📊 Testing Traditional Analysis (No LLM)")
    print("-" * 40)

    analyzer = StockAnalyzer(enable_llm=False)

    result = analyzer.analyze_stock("AAPL")

    if result:
        score = result.get("score", {})
        recommendation = result.get("recommendation", {})

        print("✅ Traditional analysis completed")
        print(f"   Composite Score: {score.get('composite_score', 'N/A')}")
        print(f"   Rating: {recommendation.get('rating', 'N/A')}")
        print(f"   Analysis Method: {score.get('analysis_method', 'traditional')}")
        print(f"   Weights Used: {score.get('weights', {})}")
    else:
        print("❌ Analysis failed")

    # Cost summary should show LLM not enabled
    cost_summary = analyzer.get_llm_cost_summary()
    print(f"\nCost Summary: {cost_summary.get('status', 'Unknown')}")


if __name__ == "__main__":
    test_enhanced_features()
