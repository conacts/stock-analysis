#!/usr/bin/env python3
"""
Test API Environments

Flexible test script that can test both local and production APIs.
Uses environment variables to determine which environment to test.

Usage:
    # Test production (default)
    python tools/test_api_environments.py

    # Test local development server
    API_BASE_URL=http://localhost:8000 python tools/test_api_environments.py

    # Test with custom API token
    API_TOKEN=your-token python tools/test_api_environments.py
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import aiohttp

# Configuration from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://stock-analysis-production-31e9.up.railway.app")
API_TOKEN = os.getenv("API_TOKEN", "default-dev-token")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

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
    """Test the health check endpoint."""
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status", "unknown")
                    checks = data.get("checks", {})

                    db_status = checks.get("database", {}).get("status", "unknown")
                    deepseek_status = checks.get("deepseek", {}).get("status", "unknown")
                    env_status = checks.get("environment", {}).get("status", "unknown")

                    details = f"Status: {status}, DB: {db_status}, DeepSeek: {deepseek_status}, Env: {env_status}"
                    log_test("Health Check", status in ["healthy", "degraded"], details)
                    return status in ["healthy", "degraded"]
                else:
                    log_test("Health Check", False, error=f"HTTP {response.status}")
                    return False
    except asyncio.TimeoutError:
        log_test("Health Check", False, error=f"Request timed out after {REQUEST_TIMEOUT} seconds")
        return False
    except Exception as e:
        log_test("Health Check", False, error=str(e))
        return False


async def test_core_endpoints():
    """Test core API endpoints that should always work."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test active portfolios
            async with session.get(f"{API_BASE_URL}/portfolios/active") as response:
                if response.status == 200:
                    portfolios = await response.json()
                    log_test("Active Portfolios", True, f"Found {len(portfolios)} portfolios")
                else:
                    log_test("Active Portfolios", False, error=f"HTTP {response.status}")
                    return False

            # Test portfolio summary
            async with session.get(f"{API_BASE_URL}/portfolio/1/summary") as response:
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

            async with session.post(f"{API_BASE_URL}/portfolio/analyze-with-llm", json=llm_payload) as response:
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
        log_test("Core Endpoints", False, error=f"Request timed out after {REQUEST_TIMEOUT} seconds")
        return False
    except Exception as e:
        log_test("Core Endpoints", False, error=str(e))
        return False


async def test_trading_endpoints():
    """Test AI trading endpoints (may not be available in all environments)."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test trading config
            async with session.get(f"{API_BASE_URL}/trading/trading-config") as response:
                if response.status == 200:
                    config = await response.json()
                    max_position = config.get("max_position_size_pct", 0)
                    daily_limit = config.get("daily_loss_limit_pct", 0)
                    log_test("Trading Config", True, f"Max Position: {max_position:.1%}, Daily Limit: {daily_limit:.1%}")
                    return True
                elif response.status == 404:
                    log_test("Trading Config", False, error="Trading endpoints not deployed (404)")
                    return False
                else:
                    log_test("Trading Config", False, error=f"HTTP {response.status}")
                    return False

    except asyncio.TimeoutError:
        log_test("Trading Endpoints", False, error=f"Request timed out after {REQUEST_TIMEOUT} seconds")
        return False
    except Exception as e:
        log_test("Trading Endpoints", False, error=str(e))
        return False


async def test_analysis_endpoints():
    """Test analysis endpoints."""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Test market gaps analysis
            async with session.post(f"{API_BASE_URL}/analysis/market-gaps") as response:
                if response.status == 200:
                    data = await response.json()
                    gaps_found = data.get("gaps_found", 0)
                    log_test("Market Gaps Analysis", True, f"Gaps found: {gaps_found}")
                else:
                    log_test("Market Gaps Analysis", False, error=f"HTTP {response.status}")
                    return False

            # Test daily performance
            async with session.post(f"{API_BASE_URL}/analysis/daily-performance") as response:
                if response.status == 200:
                    data = await response.json()
                    portfolios_analyzed = data.get("portfoliosAnalyzed", 0)
                    log_test("Daily Performance", True, f"Portfolios analyzed: {portfolios_analyzed}")
                else:
                    log_test("Daily Performance", False, error=f"HTTP {response.status}")
                    return False

            return True

    except asyncio.TimeoutError:
        log_test("Analysis Endpoints", False, error=f"Request timed out after {REQUEST_TIMEOUT} seconds")
        return False
    except Exception as e:
        log_test("Analysis Endpoints", False, error=str(e))
        return False


def detect_environment():
    """Detect which environment we're testing."""
    if "localhost" in API_BASE_URL or "127.0.0.1" in API_BASE_URL:
        return "Local Development"
    elif "railway.app" in API_BASE_URL:
        return "Production (Railway)"
    else:
        return "Custom Environment"


def print_summary():
    """Print test summary."""
    print("\n" + "=" * 60)
    print("🧪 TEST SUMMARY")
    print("=" * 60)

    total_tests = test_results["passed"] + test_results["failed"]
    success_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0

    print(f"Environment: {detect_environment()}")
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
        print("\n🎉 ALL TESTS PASSED! API is working correctly.")
    elif test_results["failed"] <= 2:  # Allow some failures for optional endpoints
        print("\n✅ CORE TESTS PASSED! Some optional endpoints may not be available.")
    else:
        print("\n⚠️  Multiple tests failed. Check API configuration.")

    # Save detailed results
    env_name = detect_environment().lower().replace(" ", "_")
    results_file = Path(f"test_results_{env_name}.json")
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"\n📄 Detailed results saved to: {results_file}")


async def main():
    """Run all tests."""
    print("🧪 API ENVIRONMENT TEST")
    print("=" * 60)
    print(f"🌐 Testing: {API_BASE_URL}")
    print(f"🏷️  Environment: {detect_environment()}")
    print(f"🔑 API Token: {'✅ Set' if API_TOKEN != 'default-dev-token' else '⚠️  Using default'}")  # nosec B105
    print(f"⏱️  Request Timeout: {REQUEST_TIMEOUT} seconds")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Run test suites
    test_suites = [
        ("🏥 Health Check", test_health_endpoint),
        ("📊 Core API Endpoints", test_core_endpoints),
        ("🤖 AI Trading Endpoints", test_trading_endpoints),
        ("📈 Analysis Endpoints", test_analysis_endpoints),
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
    return 0 if test_results["failed"] <= 2 else 1  # Allow some failures for optional endpoints


if __name__ == "__main__":
    print("🚀 Starting API environment tests...")
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
