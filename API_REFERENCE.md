# 🚀 Stock Analysis API Reference

**Production URL**: `https://stock-analysis-production-31e9.up.railway.app`
**Local Development**: `http://localhost:8000`

## 🔐 Authentication

All endpoints (except `/health` and `/healthz`) require Bearer token authentication:

```bash
Authorization: Bearer default-dev-token
```

## 📊 Health & Status Endpoints

### GET `/health`

**Description**: Comprehensive health check with environment validation
**Authentication**: None required
**Response**:

```json
{
    "status": "healthy",
    "timestamp": "2025-06-14T19:13:19.293570",
    "checks": {
        "service": {"status": "healthy"},
        "environment": {
            "status": "healthy",
            "api_token_configured": true,
            "deepseek_key_configured": true,
            "database_url_configured": true
        }
    }
}
```

### GET `/healthz`

**Description**: Ultra-minimal health check
**Authentication**: None required
**Response**:

```json
{
    "status": "ok",
    "timestamp": "2025-06-14T19:13:19.293570"
}
```

## 💼 Portfolio Management Endpoints

### GET `/portfolios/active`

**Description**: Get list of active portfolios
**Authentication**: Required
**Response**:

```json
[
    {"id": 1, "name": "Growth Portfolio"},
    {"id": 2, "name": "Value Portfolio"},
    {"id": 3, "name": "Tech Portfolio"}
]
```

### GET `/portfolio/{portfolio_id}/summary`

**Description**: Get detailed portfolio summary
**Authentication**: Required
**Parameters**:

-   `portfolio_id` (path): Portfolio ID

**Response**:

```json
{
    "portfolioId": 1,
    "name": "Portfolio 1",
    "totalValue": 100000.0,
    "positions": [
        {
            "symbol": "AAPL",
            "quantity": 100,
            "currentPrice": 150.0,
            "marketValue": 15000.0,
            "costBasis": 14500.0,
            "unrealizedPnL": 500.0,
            "weight": 0.15
        }
    ],
    "performance": {
        "dayChange": 1250.0,
        "dayChangePct": 1.25,
        "totalReturn": 3500.0,
        "totalReturnPct": 3.62
    },
    "riskMetrics": {
        "beta": 1.15,
        "volatility": 0.18,
        "sharpeRatio": 1.25
    }
}
```

### POST `/portfolio/analyze-with-llm`

**Description**: Run AI-powered portfolio analysis
**Authentication**: Required
**Request Body**:

```json
{
    "portfolio_data": {
        "portfolioId": 1,
        "positions": [{"symbol": "AAPL", "shares": 100, "current_price": 150.0}]
    },
    "analysis_type": "risk_assessment",
    "include_recommendations": true,
    "include_risk_analysis": true,
    "include_opportunities": true
}
```

**Response**:

```json
{
    "analysisId": "analysis_2025-06-14T19:13:19",
    "portfolioId": 1,
    "analysisType": "risk_assessment",
    "totalValue": 100000.0,
    "recommendations": ["Consider rebalancing tech positions"],
    "riskFactors": ["High concentration in technology sector"],
    "opportunities": ["Strong earnings season for tech companies"],
    "riskScore": 0.65,
    "dailyReturn": 0.0125,
    "llmResponse": "Portfolio analysis completed...",
    "timestamp": "2025-06-14T19:13:19"
}
```

### GET `/portfolio/health-check`

**Description**: Portfolio system health check
**Authentication**: Required
**Response**:

```json
{
    "status": "healthy",
    "total_portfolios": 3,
    "active_portfolios": 3,
    "total_positions": 9,
    "data_integrity": "good",
    "last_sync": "2025-06-14T19:13:19",
    "issues": []
}
```

## 🤖 AI Trading Endpoints

### GET `/trading/swarm/agents`

**Description**: Get available AI trading agents
**Authentication**: Required
**Response**:

```json
{
    "agents": [
        {
            "name": "market_analyst",
            "display_name": "Market Analyst",
            "description": "Sophisticated market analyst specializing in equity analysis",
            "capabilities": [
                "Analyze market data and trends",
                "Provide technical and fundamental analysis",
                "Identify trading opportunities"
            ]
        }
    ]
}
```

### POST `/trading/ai-analysis`

**Description**: Analyze symbols using AI Swarm for trading decisions
**Authentication**: Required
**Request Body**:

```json
{
    "symbols": ["AAPL", "MSFT"]
}
```

**Response**:

```json
{
  "symbols_analyzed": ["AAPL", "MSFT"],
  "analysis_timestamp": "2025-06-14T19:13:19",
  "ai_response": [
    {
      "agent": "market_analyst",
      "message": "AAPL shows strong technical indicators..."
    }
  ],
  "final_agent": "market_analyst",
  "turns_used": 3,
  "success": true,
  "conversation_id": "conv_20250614_191319",
  "portfolio_config": {...}
}
```

### POST `/trading/ai-trade`

**Description**: Let AI Swarm make trading decisions
**Authentication**: Required
**Request Body**:

```json
{
    "context": "Analyze current market conditions and suggest trades",
    "symbols": ["AAPL", "MSFT"],
    "conversation_messages": [
        {"role": "user", "content": "What's your view on tech stocks?"}
    ],
    "portfolio_id": 1,
    "max_iterations": 25
}
```

### POST `/trading/ai-conversation`

**Description**: Have a conversation with the AI Swarm
**Authentication**: Required
**Request Body**:

```json
{
    "messages": [
        {"role": "user", "content": "Analyze my portfolio"},
        {"role": "assistant", "content": "I'll analyze your portfolio..."}
    ],
    "max_iterations": 25,
    "portfolio_id": 1
}
```

### POST `/trading/swarm/agent`

**Description**: Talk directly to a specific Swarm agent
**Authentication**: Required
**Request Body**:

```json
{
    "message": "What's your analysis of AAPL?",
    "agent": "market_analyst",
    "portfolio_id": "default",
    "max_turns": 15
}
```

### GET `/trading/swarm/conversation-history/{portfolio_id}`

**Description**: Get conversation history for a portfolio
**Authentication**: Required
**Parameters**:

-   `portfolio_id` (path): Portfolio ID

### DELETE `/trading/swarm/conversation-history/{portfolio_id}`

**Description**: Clear conversation history for a portfolio
**Authentication**: Required
**Parameters**:

-   `portfolio_id` (path): Portfolio ID

## 📰 News & Analysis Endpoints

### POST `/news/overnight-analysis`

**Description**: Analyze overnight news for given symbols
**Authentication**: Required
**Request Body**:

```json
{
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "hours_back": 24
}
```

**Response**:

```json
{
    "analysis_date": "2025-06-14T19:13:19",
    "symbols_analyzed": ["AAPL", "GOOGL", "MSFT"],
    "news_items": [],
    "sentiment_summary": "neutral",
    "key_events": []
}
```

### GET `/analysis/recent`

**Description**: Get recent analysis activity
**Authentication**: Required
**Parameters**:

-   `hours` (query, optional): Hours to look back (default: 24)

### POST `/analysis/market-gaps`

**Description**: Analyze market gaps
**Authentication**: Required
**Response**:

```json
{
    "analysis_date": "2025-06-14T19:13:19",
    "gaps_found": 0,
    "gaps": []
}
```

### POST `/analysis/daily-performance`

**Description**: Analyze daily performance
**Authentication**: Required

## 🚨 Alert Endpoints

### GET `/alerts/price-alerts/active`

**Description**: Get active price alerts
**Authentication**: Required
**Response**:

```json
{
    "active_alerts": [],
    "total_count": 0,
    "last_updated": "2025-06-14T19:13:19"
}
```

### POST `/alerts/opening-bell`

**Description**: Generate opening bell alerts
**Authentication**: Required
**Request Body**:

```json
{
    "gap_analysis": [{"symbol": "AAPL", "gap_percent": 5.2}]
}
```

## 📈 Trading Endpoints

### GET `/trading/account`

**Description**: Get trading account information
**Authentication**: Required

### GET `/trading/positions`

**Description**: Get all trading positions
**Authentication**: Required

### GET `/trading/positions/{symbol}`

**Description**: Get position for specific symbol
**Authentication**: Required
**Parameters**:

-   `symbol` (path): Stock symbol

### DELETE `/trading/positions/{symbol}`

**Description**: Close position for specific symbol
**Authentication**: Required
**Parameters**:

-   `symbol` (path): Stock symbol

### DELETE `/trading/positions`

**Description**: Close all positions
**Authentication**: Required

### POST `/trading/orders/market`

**Description**: Place market order
**Authentication**: Required
**Request Body**:

```json
{
    "symbol": "AAPL",
    "qty": 100,
    "side": "buy",
    "time_in_force": "day"
}
```

### POST `/trading/orders/limit`

**Description**: Place limit order
**Authentication**: Required
**Request Body**:

```json
{
    "symbol": "AAPL",
    "qty": 100,
    "side": "buy",
    "limit_price": 150.0,
    "time_in_force": "day"
}
```

### GET `/trading/orders`

**Description**: Get orders
**Authentication**: Required
**Parameters**:

-   `status` (query, optional): Order status filter (default: "all")
-   `limit` (query, optional): Number of orders to return (default: 50)

### GET `/trading/orders/{order_id}`

**Description**: Get specific order
**Authentication**: Required
**Parameters**:

-   `order_id` (path): Order ID

### DELETE `/trading/orders/{order_id}`

**Description**: Cancel specific order
**Authentication**: Required
**Parameters**:

-   `order_id` (path): Order ID

### DELETE `/trading/orders`

**Description**: Cancel all orders
**Authentication**: Required

### GET `/trading/market-data/{symbol}`

**Description**: Get market data for symbol
**Authentication**: Required
**Parameters**:

-   `symbol` (path): Stock symbol
-   `timeframe` (query, optional): Timeframe (default: "1Day")
-   `start` (query, optional): Start date
-   `end` (query, optional): End date

### GET `/trading/market-status`

**Description**: Get market status
**Authentication**: Required

### GET `/trading/portfolio-summary`

**Description**: Get trading portfolio summary
**Authentication**: Required

## 📬 Notification Endpoints

### POST `/notifications/premarket-summary`

**Description**: Send premarket summary
**Authentication**: Required
**Request Body**:

```json
{
    "summary": "Market outlook for today..."
}
```

## 🧪 Testing the API

### Using curl:

```bash
# Health check (no auth)
curl https://stock-analysis-production-31e9.up.railway.app/health

# Get portfolios (with auth)
curl -H "Authorization: Bearer default-dev-token" \
  https://stock-analysis-production-31e9.up.railway.app/portfolios/active

# AI analysis (with auth)
curl -X POST \
  -H "Authorization: Bearer default-dev-token" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL"]}' \
  https://stock-analysis-production-31e9.up.railway.app/trading/ai-analysis
```

### Using the test script:

```bash
# Test all endpoints
RAILWAY_URL="https://stock-analysis-production-31e9.up.railway.app" \
API_TOKEN="default-dev-token" \
uv run python scripts/test_api_endpoints.py

# Test specific endpoint
RAILWAY_URL="https://stock-analysis-production-31e9.up.railway.app" \
API_TOKEN="default-dev-token" \
uv run python scripts/test_api_endpoints.py --endpoint health
```

## 📊 Response Codes

-   `200` - Success
-   `401` - Unauthorized (missing or invalid token)
-   `403` - Forbidden (valid token but insufficient permissions)
-   `404` - Not Found
-   `422` - Validation Error (invalid request body)
-   `500` - Internal Server Error

## 🔄 Rate Limits

Currently no rate limits are enforced, but this may change in future versions.

---

**Last Updated**: 2025-06-14
**API Version**: 1.0
**Total Endpoints**: 43+
