#!/usr/bin/env python3
"""
Test Railway API Endpoints

Quick testing script for the Railway-deployed Stock Analysis API.
Tests all available endpoints with sample data.

Usage:
    python scripts/test_api_endpoints.py
    python scripts/test_api_endpoints.py --endpoint health
    python scripts/test_api_endpoints.py --endpoint portfolio --portfolio-id 1
"""

import argparse
import os

import requests

# Railway API Configuration
RAILWAY_URL = "https://stock-analysis-production-31e9.up.railway.app"
API_TOKEN = os.getenv("API_TOKEN", "your-api-token-here")  # nosec B105

# Headers for authenticated requests
HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


def test_health():
    """Test health endpoint (no auth required)"""
    print("🔍 Testing Health Endpoint")
    print("-" * 40)

    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status')}")
            print(f"📊 Database: {data.get('checks', {}).get('database', {}).get('status')}")
            print(f"🤖 DeepSeek: {data.get('checks', {}).get('deepseek', {}).get('status')}")
            print(f"🔧 Environment: {data.get('checks', {}).get('environment', {}).get('status')}")
            print(f"🔑 API Token Configured: {data.get('checks', {}).get('environment', {}).get('api_token_configured')}")
        else:
            print(f"❌ Health check failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def test_portfolio_summary(portfolio_id=1):
    """Test portfolio summary endpoint"""
    print(f"📊 Testing Portfolio Summary (ID: {portfolio_id})")
    print("-" * 40)

    try:
        response = requests.get(f"{RAILWAY_URL}/portfolio/{portfolio_id}/summary", headers=HEADERS, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Portfolio: {data.get('name')}")
            print(f"💰 Total Value: ${data.get('total_value'):,.2f}")
            print(f"📈 Day Change: {data.get('performance', {}).get('day_change_pct', 0):.2f}%")
        else:
            print(f"❌ Request failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def test_active_portfolios():
    """Test active portfolios endpoint"""
    print("📋 Testing Active Portfolios")
    print("-" * 40)

    try:
        response = requests.get(f"{RAILWAY_URL}/portfolios/active", headers=HEADERS, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} active portfolios:")
            for portfolio in data:
                print(f"   - {portfolio.get('name')} (ID: {portfolio.get('id')})")
        else:
            print(f"❌ Request failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def test_llm_analysis():
    """Test LLM analysis endpoint"""
    print("🤖 Testing LLM Analysis")
    print("-" * 40)

    sample_request = {
        "portfolio_data": {"portfolio_id": 1, "positions": [{"symbol": "AAPL", "shares": 100, "current_price": 150.0}, {"symbol": "GOOGL", "shares": 50, "current_price": 2500.0}]},
        "analysis_type": "risk_assessment",
        "include_recommendations": True,
        "include_risk_analysis": True,
        "include_opportunities": True,
    }

    try:
        response = requests.post(f"{RAILWAY_URL}/portfolio/analyze-with-llm", headers=HEADERS, json=sample_request, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis ID: {data.get('analysis_id')}")
            print(f"📊 Analysis Type: {data.get('analysis_type')}")
            print(f"💡 Recommendations: {len(data.get('recommendations', []))}")
            print(f"⚠️  Risk Score: {data.get('risk_analysis', {}).get('risk_score')}")
        else:
            print(f"❌ Request failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def test_news_analysis():
    """Test news analysis endpoint"""
    print("📰 Testing News Analysis")
    print("-" * 40)

    sample_request = {"symbols": ["AAPL", "GOOGL", "MSFT"], "hours_back": 24}

    try:
        response = requests.post(f"{RAILWAY_URL}/news/overnight-analysis", headers=HEADERS, json=sample_request, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis Date: {data.get('analysis_date')}")
            print(f"📊 Symbols Analyzed: {', '.join(data.get('symbols_analyzed', []))}")
            print(f"📰 News Items: {len(data.get('news_items', []))}")
            print(f"😊 Sentiment: {data.get('sentiment_summary')}")
        else:
            print(f"❌ Request failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def test_market_gaps():
    """Test market gaps analysis"""
    print("📈 Testing Market Gaps Analysis")
    print("-" * 40)

    try:
        response = requests.post(f"{RAILWAY_URL}/analysis/market-gaps", headers=HEADERS, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis Date: {data.get('analysis_date')}")
            print(f"📊 Gaps Found: {data.get('gaps_found')}")
            print(f"📋 Gap Details: {len(data.get('gaps', []))} items")
        else:
            print(f"❌ Request failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def test_price_alerts():
    """Test price alerts endpoint"""
    print("🚨 Testing Price Alerts")
    print("-" * 40)

    try:
        response = requests.get(f"{RAILWAY_URL}/alerts/price-alerts/active", headers=HEADERS, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Active Alerts: {data.get('total_count')}")
            print(f"🕐 Last Updated: {data.get('last_updated')}")
        else:
            print(f"❌ Request failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    print()


def test_all_endpoints():
    """Test all available endpoints"""
    print("🚀 Testing All Railway API Endpoints")
    print("=" * 50)
    print(f"🌐 Base URL: {RAILWAY_URL}")
    print(f"🔑 API Token: {'✅ Set' if API_TOKEN != 'your-api-token-here' else '❌ Not Set'}")  # nosec B105
    print("=" * 50)
    print()

    # Test endpoints in order
    test_health()
    test_active_portfolios()
    test_portfolio_summary(1)
    test_portfolio_summary(2)
    test_llm_analysis()
    test_news_analysis()
    test_market_gaps()
    test_price_alerts()

    print("🎉 All endpoint tests completed!")


def main():
    """Main function with CLI argument parsing"""
    parser = argparse.ArgumentParser(description="Test Railway API Endpoints")
    parser.add_argument("--endpoint", choices=["health", "portfolio", "portfolios", "llm", "news", "gaps", "alerts", "all"], default="all", help="Specific endpoint to test")
    parser.add_argument("--portfolio-id", type=int, default=1, help="Portfolio ID for testing")
    parser.add_argument("--api-token", help="Override API token")

    args = parser.parse_args()

    # Override API token if provided
    if args.api_token:
        global API_TOKEN, HEADERS
        API_TOKEN = args.api_token
        HEADERS["Authorization"] = f"Bearer {API_TOKEN}"

    # Check if API token is set
    if API_TOKEN == "your-api-token-here":  # nosec B105
        print("⚠️  Warning: API_TOKEN not set!")
        print("Set it with: export API_TOKEN=your-actual-token")
        print("Or pass it with: --api-token your-token")
        print()

    # Run specific test or all tests
    if args.endpoint == "health":
        test_health()
    elif args.endpoint == "portfolio":
        test_portfolio_summary(args.portfolio_id)
    elif args.endpoint == "portfolios":
        test_active_portfolios()
    elif args.endpoint == "llm":
        test_llm_analysis()
    elif args.endpoint == "news":
        test_news_analysis()
    elif args.endpoint == "gaps":
        test_market_gaps()
    elif args.endpoint == "alerts":
        test_price_alerts()
    else:
        test_all_endpoints()


if __name__ == "__main__":
    main()
