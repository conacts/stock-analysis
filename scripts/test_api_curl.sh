#!/bin/bash
# Quick curl-based API testing for Railway deployment

# Configuration
RAILWAY_URL="https://stock-analysis-production-31e9.up.railway.app"
API_TOKEN="${API_TOKEN:-your-api-token-here}"  # nosec B105

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function to print section headers
print_header() {
    echo -e "\n${BLUE}$1${NC}"
    echo "$(printf '=%.0s' {1..50})"
}

# Helper function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint"

    if [ "$method" = "GET" ]; then
        if [ "$endpoint" = "/health" ]; then
            # Health endpoint doesn't require auth
            curl -s -w "\nStatus: %{http_code}\n" "$RAILWAY_URL$endpoint"
        else
            # Other GET endpoints require auth
            curl -s -w "\nStatus: %{http_code}\n" \
                -H "Authorization: Bearer $API_TOKEN" \
                "$RAILWAY_URL$endpoint"
        fi
    else
        # POST endpoints
        curl -s -w "\nStatus: %{http_code}\n" \
            -X POST \
            -H "Authorization: Bearer $API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$RAILWAY_URL$endpoint"
    fi

    echo -e "\n${GREEN}✓ Test completed${NC}"
}

# Main testing function
main() {
    print_header "🚀 Railway API Testing with curl"
    echo "Base URL: $RAILWAY_URL"
    echo "API Token: ${API_TOKEN:0:10}..."

    # Test 1: Health Check (no auth required)
    test_endpoint "GET" "/health" "" "Health Check"

    # Test 2: Active Portfolios
    test_endpoint "GET" "/portfolios/active" "" "Active Portfolios"

    # Test 3: Portfolio Summary
    test_endpoint "GET" "/portfolio/1/summary" "" "Portfolio Summary (ID: 1)"

    # Test 4: LLM Analysis
    llm_data='{
        "portfolio_data": {
            "portfolio_id": 1,
            "positions": [
                {"symbol": "AAPL", "shares": 100, "current_price": 150.0},
                {"symbol": "GOOGL", "shares": 50, "current_price": 2500.0}
            ]
        },
        "analysis_type": "risk_assessment",
        "include_recommendations": true,
        "include_risk_analysis": true,
        "include_opportunities": true
    }'
    test_endpoint "POST" "/portfolio/analyze-with-llm" "$llm_data" "LLM Portfolio Analysis"

    # Test 5: News Analysis
    news_data='{
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "hours_back": 24
    }'
    test_endpoint "POST" "/news/overnight-analysis" "$news_data" "Overnight News Analysis"

    # Test 6: Market Gaps
    test_endpoint "POST" "/analysis/market-gaps" "{}" "Market Gaps Analysis"

    # Test 7: Price Alerts
    test_endpoint "GET" "/alerts/price-alerts/active" "" "Active Price Alerts"

    # Test 8: Daily Performance
    test_endpoint "POST" "/analysis/daily-performance" "{}" "Daily Performance Analysis"

    print_header "🎉 All tests completed!"
    echo "Check the status codes and responses above."
    echo "Status 200 = Success, 401 = Auth Error, 500 = Server Error"
}

# Check if API token is set
if [ "$API_TOKEN" = "your-api-token-here" ]; then  # nosec B105
    echo -e "${RED}⚠️  Warning: API_TOKEN not set!${NC}"
    echo "Set it with: export API_TOKEN=your-actual-token"
    echo "Or run: API_TOKEN=your-token ./scripts/test_api_curl.sh"
    echo ""
fi

# Run main function
main
