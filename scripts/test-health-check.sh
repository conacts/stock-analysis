#!/bin/bash
# Test Health Check Functionality
# Manually tests the health check endpoints that Trigger.dev tasks use

echo "🏥 Testing Health Check Functionality"
echo "====================================="

# Load environment variables
source .env.local 2>/dev/null || true

# Set API URL (default to production if not set)
API_URL=${PYTHON_API_URL:-https://stock-analysis-production-31e9.up.railway.app}

# Override with command line if provided
if [ ! -z "$1" ]; then
  API_URL=$1
fi
echo "📍 Testing API: $API_URL"
echo ""

# Test 1: Basic Health Check
echo "1️⃣ Testing Basic Health Check"
echo "GET $API_URL/health"
curl -s -X GET "$API_URL/health" -H "Content-Type: application/json" | jq '.'
echo ""

# Test 2: Recent Analysis Endpoint
echo "2️⃣ Testing Recent Analysis Endpoint"
echo "GET $API_URL/analysis/recent?hours=24"
curl -s -X GET "$API_URL/analysis/recent?hours=24" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""

# Test 3: Portfolio Health Check
echo "3️⃣ Testing Portfolio Health Check"
echo "GET $API_URL/portfolio/health-check"
curl -s -X GET "$API_URL/portfolio/health-check" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""

# Test 4: Active Portfolios
echo "4️⃣ Testing Active Portfolios"
echo "GET $API_URL/portfolios/active"
curl -s -X GET "$API_URL/portfolios/active" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" | jq '.'
echo ""

echo "✅ Health check tests completed!"
