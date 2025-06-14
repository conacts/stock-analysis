#!/usr/bin/env python3
"""
Test All Trigger.dev Endpoints with Timeouts

Comprehensive test script with 30-second timeouts for all health checks
and API endpoint tests. This ensures fast failure detection.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import aiohttp

# Configuration
RAILWAY_URL = "https://stock-analysis-production-31e9.up.railway.app"
API_TOKEN = os.getenv("API_TOKEN", "default-dev-token")
REQUEST_TIMEOUT = 30  # 30 second timeout for all requests

# Test results tracking
test_results = {"passed": 0, "failed": 0, "errors": [], "details": []}


def log_test(name: str, success: bool, details: str = "", error: str = ""):
    """Log test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {name}")
    if details:
        print(f"    {details}")
    if error:
        print(f"    Error: {error}")

    test_results["passed" if success else "failed"] += 1
    if not success:
        test_results["errors"].append(f"{name}: {error}")
    test_results["details"].append({"name": name, "success": success, "details": details, "error": error, "timestamp": datetime.now().isoformat()})


async def test_health_endpoint():
    """Test the health check endpoint with timeout."""
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{RAILWAY_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status", "unknown")
                    checks = data.get("checks", {})

                    db_status = checks.get("database", {}).get("status", "unknown")
                    deepseek_status = checks.get("deepseek", {}).get("status", "unknown")
                    env_status = checks.get("environment", {}).get("status", "unknown")

                    details = f"Status: {status}, DB: {db_status}, DeepSeek: {deepseek_status}, Env: {env_status}"
                    log_test("Health Check", status == "healthy", details)
                    return status == "healthy"
                else:
                    log_test("Health Check", False, error=f"HTTP {response.status}")
                    return False
    except asyncio.TimeoutError:
        log_test("Health Check", False, error="Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("Health Check", False, error=str(e))
        return False


async def test_portfolio_endpoints():
    """Test portfolio-related endpoints with timeout."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test active portfolios
            async with session.get(f"{RAILWAY_URL}/portfolios/active") as response:
                if response.status == 200:
                    portfolios = await response.json()
                    log_test("Active Portfolios", True, f"Found {len(portfolios)} portfolios")
                else:
                    log_test("Active Portfolios", False, error=f"HTTP {response.status}")
                    return False

            # Test portfolio summary
            async with session.get(f"{RAILWAY_URL}/portfolio/1/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    total_value = data.get("totalValue", 0)
                    positions = data.get("positions", [])
                    log_test("Portfolio Summary", True, f"Value: ${total_value:,.2f}, Positions: {len(positions)}")
                else:
                    log_test("Portfolio Summary", False, error=f"HTTP {response.status}")
                    return False

            # Test LLM analysis
            llm_payload = {"portfolio_data": {"portfolioId": 1, "totalValue": 100000}, "analysis_type": "comprehensive", "include_recommendations": True, "include_risk_analysis": True, "include_opportunities": True}

            async with session.post(f"{RAILWAY_URL}/portfolio/analyze-with-llm", json=llm_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    analysis_id = data.get("analysisId", "")
                    recommendations = data.get("recommendations", [])
                    risk_score = data.get("riskScore", 0)
                    log_test("LLM Analysis", True, f"ID: {analysis_id[:20]}..., Recommendations: {len(recommendations)}, Risk: {risk_score}")
                else:
                    log_test("LLM Analysis", False, error=f"HTTP {response.status}")
                    return False

            return True

    except asyncio.TimeoutError:
        log_test("Portfolio Endpoints", False, error="Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("Portfolio Endpoints", False, error=str(e))
        return False


async def test_trading_endpoints():
    """Test AI trading endpoints with timeout."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test trading config
            async with session.get(f"{RAILWAY_URL}/trading/trading-config") as response:
                if response.status == 200:
                    config = await response.json()
                    max_position = config.get("max_position_size_pct", 0)
                    daily_limit = config.get("daily_loss_limit_pct", 0)
                    log_test("Trading Config", True, f"Max Position: {max_position:.1%}, Daily Limit: {daily_limit:.1%}")
                else:
                    log_test("Trading Config", False, error=f"HTTP {response.status}")
                    return False

            # Test market status
            async with session.get(f"{RAILWAY_URL}/trading/market-status") as response:
                if response.status == 200:
                    status = await response.json()
                    market_open = status.get("market_open", False)
                    trading_enabled = status.get("trading_enabled", False)
                    log_test("Market Status", True, f"Market Open: {market_open}, Trading: {trading_enabled}")
                else:
                    log_test("Market Status", False, error=f"HTTP {response.status}")
                    return False

            # Test risk status
            async with session.get(f"{RAILWAY_URL}/trading/risk-status/1") as response:
                if response.status == 200:
                    risk = await response.json()
                    risk_level = risk.get("overall_risk", "UNKNOWN")
                    risk_score = risk.get("risk_score", 0)
                    trading_halted = risk.get("trading_halted", True)
                    log_test("Risk Status", True, f"Level: {risk_level}, Score: {risk_score:.2f}, Halted: {trading_halted}")
                else:
                    log_test("Risk Status", False, error=f"HTTP {response.status}")
                    return False

            return True

    except asyncio.TimeoutError:
        log_test("Trading Endpoints", False, error="Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("Trading Endpoints", False, error=str(e))
        return False


async def test_analysis_endpoints():
    """Test analysis endpoints with timeout."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test market gaps analysis
            async with session.post(f"{RAILWAY_URL}/analysis/market-gaps") as response:
                if response.status == 200:
                    data = await response.json()
                    gaps_found = data.get("gaps_found", 0)
                    log_test("Market Gaps Analysis", True, f"Gaps found: {gaps_found}")
                else:
                    log_test("Market Gaps Analysis", False, error=f"HTTP {response.status}")
                    return False

            # Test daily performance
            async with session.post(f"{RAILWAY_URL}/analysis/daily-performance") as response:
                if response.status == 200:
                    data = await response.json()
                    portfolios_analyzed = data.get("portfoliosAnalyzed", 0)
                    log_test("Daily Performance", True, f"Portfolios analyzed: {portfolios_analyzed}")
                else:
                    log_test("Daily Performance", False, error=f"HTTP {response.status}")
                    return False

            return True

    except asyncio.TimeoutError:
        log_test("Analysis Endpoints", False, error="Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("Analysis Endpoints", False, error=str(e))
        return False


async def test_alert_endpoints():
    """Test alert endpoints with timeout."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test active price alerts
            async with session.get(f"{RAILWAY_URL}/alerts/price-alerts/active") as response:
                if response.status == 200:
                    data = await response.json()
                    total_count = data.get("total_count", 0)
                    log_test("Active Price Alerts", True, f"Active alerts: {total_count}")
                else:
                    log_test("Active Price Alerts", False, error=f"HTTP {response.status}")
                    return False

            # Test opening bell alerts
            alert_payload = {"gap_analysis": []}
            async with session.post(f"{RAILWAY_URL}/alerts/opening-bell", json=alert_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    alerts_generated = data.get("alerts_generated", 0)
                    log_test("Opening Bell Alerts", True, f"Alerts generated: {alerts_generated}")
                else:
                    log_test("Opening Bell Alerts", False, error=f"HTTP {response.status}")
                    return False

            return True

    except asyncio.TimeoutError:
        log_test("Alert Endpoints", False, error="Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("Alert Endpoints", False, error=str(e))
        return False


async def test_news_endpoints():
    """Test news analysis endpoints with timeout."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test overnight news analysis
            news_payload = {"symbols": ["AAPL", "MSFT", "GOOGL"], "hours_back": 24}

            async with session.post(f"{RAILWAY_URL}/news/overnight-analysis", json=news_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    symbols_analyzed = data.get("symbols_analyzed", [])
                    sentiment = data.get("sentiment_summary", "unknown")
                    log_test("Overnight News Analysis", True, f"Symbols: {len(symbols_analyzed)}, Sentiment: {sentiment}")
                else:
                    log_test("Overnight News Analysis", False, error=f"HTTP {response.status}")
                    return False

            return True

    except asyncio.TimeoutError:
        log_test("News Endpoints", False, error="Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("News Endpoints", False, error=str(e))
        return False


async def test_trigger_compatibility():
    """Test that all endpoints return data compatible with Trigger.dev tasks."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test portfolio summary structure
            async with session.get(f"{RAILWAY_URL}/portfolio/1/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["portfolioId", "totalValue", "positions"]
                    missing_fields = [field for field in required_fields if field not in data]

                    if not missing_fields:
                        log_test("Portfolio Summary Structure", True, "All required fields present")
                    else:
                        log_test("Portfolio Summary Structure", False, error=f"Missing fields: {missing_fields}")
                        return False
                else:
                    log_test("Portfolio Summary Structure", False, error=f"HTTP {response.status}")
                    return False

            # Test LLM analysis structure
            llm_payload = {"portfolio_data": {"portfolioId": 1, "totalValue": 100000}, "analysis_type": "comprehensive"}

            async with session.post(f"{RAILWAY_URL}/portfolio/analyze-with-llm", json=llm_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["analysisId", "portfolioId", "totalValue", "recommendations", "riskScore"]
                    missing_fields = [field for field in required_fields if field not in data]

                    if not missing_fields:
                        log_test("LLM Analysis Structure", True, "All required fields present")
                    else:
                        log_test("LLM Analysis Structure", False, error=f"Missing fields: {missing_fields}")
                        return False
                else:
                    log_test("LLM Analysis Structure", False, error=f"HTTP {response.status}")
                    return False

            return True

    except asyncio.TimeoutError:
        log_test("Trigger.dev Compatibility", False, error="Request timed out after 30 seconds")
        return False
    except Exception as e:
        log_test("Trigger.dev Compatibility", False, error=str(e))
        return False


def print_summary():
    """Print test summary."""
    print("\n" + "=" * 60)
    print("🧪 TEST SUMMARY")
    print("=" * 60)

    total_tests = test_results["passed"] + test_results["failed"]
    success_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Timeout: {REQUEST_TIMEOUT} seconds per request")

    if test_results["errors"]:
        print(f"\n❌ ERRORS ({len(test_results['errors'])}):")
        for error in test_results["errors"]:
            print(f"  • {error}")

    # Overall status
    if test_results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        print("🚀 Trigger.dev tasks should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Review errors before deploying Trigger.dev tasks.")

    # Save detailed results
    results_file = Path("test_results_timeout.json")
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"\n📄 Detailed results saved to: {results_file}")


async def main():
    """Run all tests with timeouts."""
    print("🧪 COMPREHENSIVE PRODUCTION API TEST (WITH TIMEOUTS)")
    print("=" * 60)
    print(f"🌐 Testing: {RAILWAY_URL}")
    print(f"🔑 API Token: {'✅ Set' if API_TOKEN != 'default-dev-token' else '⚠️  Using default'}")  # nosec B105
    print(f"⏱️  Request Timeout: {REQUEST_TIMEOUT} seconds")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Run all test suites
    test_suites = [
        ("🏥 Health Check", test_health_endpoint),
        ("📊 Portfolio Endpoints", test_portfolio_endpoints),
        ("🤖 AI Trading Endpoints", test_trading_endpoints),
        ("📈 Analysis Endpoints", test_analysis_endpoints),
        ("🚨 Alert Endpoints", test_alert_endpoints),
        ("📰 News Endpoints", test_news_endpoints),
        ("🔧 Trigger.dev Compatibility", test_trigger_compatibility),
    ]

    for suite_name, test_func in test_suites:
        print(f"\n{suite_name}")
        print("-" * 40)

        start_time = time.time()
        try:
            success = await test_func()
            duration = time.time() - start_time

            if success:
                print(f"✅ {suite_name} completed in {duration:.2f}s")
            else:
                print(f"❌ {suite_name} failed after {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {suite_name} crashed after {duration:.2f}s: {e}")
            log_test(suite_name, False, error=str(e))

    # Print final summary
    print_summary()

    # Return exit code
    return 0 if test_results["failed"] == 0 else 1


if __name__ == "__main__":
    print("🚀 Starting comprehensive production API tests with timeouts...")
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
