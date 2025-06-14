#!/bin/bash

# 🚀 Alpaca Paper Trading Endpoints Test Script
# Tests all the new trading endpoints with the Railway deployment

set -e

# Configuration
if [ "$1" = "local" ]; then
    BASE_URL="http://localhost:8000"
    echo "🏠 Testing LOCAL endpoints at $BASE_URL"
else
    BASE_URL="https://stock-analysis-production-31e9.up.railway.app"
    echo "🌐 Testing PRODUCTION endpoints at $BASE_URL"
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

API_TOKEN=${API_TOKEN:-"your-api-token-here"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4

    echo -e "\n${BLUE}🧪 Testing: $description${NC}"
    echo "   $method $BASE_URL$endpoint"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" \
            -H "Authorization: Bearer $API_TOKEN" \
            -H "Content-Type: application/json" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" \
            -X "$method" \
            -H "Authorization: Bearer $API_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi

    # Extract HTTP status code (last line)
    http_code=$(echo "$response" | tail -n 1)
    # Extract response body (all but last line)
    response_body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        echo -e "   ${GREEN}✅ SUCCESS ($http_code)${NC}"
        echo "   Response: $(echo "$response_body" | jq -r 'keys[]' 2>/dev/null | head -5 | tr '\n' ' ' || echo "Raw response")"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${RED}❌ FAILED ($http_code)${NC}"
        echo "   Error: $(echo "$response_body" | jq -r '.detail // .' 2>/dev/null || echo "$response_body")"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo -e "${YELLOW}🚀 ALPACA PAPER TRADING ENDPOINTS TEST${NC}"
echo "=================================================="

# Test 1: Account Information
test_endpoint "GET" "/trading/account" "Get Account Information"

# Test 2: Get All Positions
test_endpoint "GET" "/trading/positions" "Get All Positions"

# Test 3: Get Specific Position (will likely fail if no AAPL position)
test_endpoint "GET" "/trading/positions/AAPL" "Get AAPL Position"

# Test 4: Get All Orders
test_endpoint "GET" "/trading/orders" "Get All Orders"

# Test 5: Get Orders with Status Filter
test_endpoint "GET" "/trading/orders?status=filled&limit=10" "Get Filled Orders"

# Test 6: Market Data for AAPL
test_endpoint "GET" "/trading/market-data/AAPL" "Get AAPL Market Data"

# Test 7: Market Data with Custom Timeframe
test_endpoint "GET" "/trading/market-data/AAPL?timeframe=1Hour" "Get AAPL Hourly Data"

# Test 8: Market Status
test_endpoint "GET" "/trading/market-status" "Get Market Status"

# Test 9: Portfolio Summary (comprehensive)
test_endpoint "GET" "/trading/portfolio-summary" "Get Portfolio Summary"

# Test 10: Place Market Order (small test order)
market_order_data='{
    "symbol": "AAPL",
    "qty": 1,
    "side": "buy",
    "time_in_force": "day"
}'
test_endpoint "POST" "/trading/orders/market" "Place Market Order" "$market_order_data"

# Test 11: Place Limit Order (small test order)
limit_order_data='{
    "symbol": "AAPL",
    "qty": 1,
    "side": "buy",
    "limit_price": 100.00,
    "time_in_force": "day"
}'
test_endpoint "POST" "/trading/orders/limit" "Place Limit Order" "$limit_order_data"

# Test 12: AI Analysis (placeholder)
ai_analysis_data='["AAPL", "MSFT", "GOOGL"]'
test_endpoint "POST" "/trading/ai-analysis" "AI Trading Analysis" "$ai_analysis_data"

echo -e "\n${YELLOW}=================================================="
echo "🏁 TEST SUMMARY"
echo "=================================================="
echo -e "✅ Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "📊 Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! Alpaca integration is working perfectly!${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. This might be expected for:"
    echo "   - Position queries (if no positions exist)"
    echo "   - Order placement (if market is closed)"
    echo "   - Specific symbol queries (if not in portfolio)"
    echo -e "${NC}"
    exit 1
fi
