# 🧪 Railway API Testing Guide

Quick reference for testing your Railway-deployed Stock Analysis API at:
**https://stock-analysis-production-31e9.up.railway.app**

## 🚀 Quick Start

### 1. **Health Check (No Auth Required)**

```bash
curl https://stock-analysis-production-31e9.up.railway.app/health
```

### 2. **Using the Python Testing Script**

```bash
# Test all endpoints
API_TOKEN=default-dev-token uv run python scripts/test_api_endpoints.py

# Test specific endpoint
API_TOKEN=default-dev-token uv run python scripts/test_api_endpoints.py --endpoint health
API_TOKEN=default-dev-token uv run python scripts/test_api_endpoints.py --endpoint portfolios
API_TOKEN=default-dev-token uv run python scripts/test_api_endpoints.py --endpoint portfolio --portfolio-id 2
API_TOKEN=default-dev-token uv run python scripts/test_api_endpoints.py --endpoint llm
```

### 3. **Using the Curl Script**

```bash
# Test all endpoints
API_TOKEN=default-dev-token ./scripts/test_api_curl.sh
```

## 📋 Available Endpoints

### **GET Endpoints**

| Endpoint                      | Description            | Auth Required |
| ----------------------------- | ---------------------- | ------------- |
| `/health`                     | System health check    | ❌ No         |
| `/portfolios/active`          | List active portfolios | ✅ Yes        |
| `/portfolio/{id}/summary`     | Portfolio summary      | ✅ Yes        |
| `/alerts/price-alerts/active` | Active price alerts    | ✅ Yes        |

### **POST Endpoints**

| Endpoint                      | Description            | Auth Required |
| ----------------------------- | ---------------------- | ------------- |
| `/portfolio/analyze-with-llm` | LLM portfolio analysis | ✅ Yes        |
| `/news/overnight-analysis`    | News analysis          | ✅ Yes        |
| `/analysis/market-gaps`       | Market gaps analysis   | ✅ Yes        |
| `/analysis/daily-performance` | Daily performance      | ✅ Yes        |
| `/alerts/opening-bell`        | Opening bell alerts    | ✅ Yes        |

## 🔑 Authentication

**API Token**: `default-dev-token` (for testing)

**Header Format**:

```
Authorization: Bearer default-dev-token
```

## 📊 Sample Requests

### **Portfolio Analysis with LLM**

```bash
curl -X POST https://stock-analysis-production-31e9.up.railway.app/portfolio/analyze-with-llm \
  -H "Authorization: Bearer default-dev-token" \
  -H "Content-Type: application/json" \
  -d '{
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
```

### **News Analysis**

```bash
curl -X POST https://stock-analysis-production-31e9.up.railway.app/news/overnight-analysis \
  -H "Authorization: Bearer default-dev-token" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "hours_back": 24
  }'
```

### **Market Gaps Analysis**

```bash
curl -X POST https://stock-analysis-production-31e9.up.railway.app/analysis/market-gaps \
  -H "Authorization: Bearer default-dev-token" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 🎯 Testing Options

### **Option 1: Python Script (Recommended)**

-   **File**: `scripts/test_api_endpoints.py`
-   **Features**: Detailed output, error handling, specific endpoint testing
-   **Usage**: `API_TOKEN=default-dev-token uv run python scripts/test_api_endpoints.py --endpoint health`

### **Option 2: Curl Script**

-   **File**: `scripts/test_api_curl.sh`
-   **Features**: Quick bash testing, all endpoints at once
-   **Usage**: `API_TOKEN=default-dev-token ./scripts/test_api_curl.sh`

### **Option 3: Manual Curl**

-   **Features**: Direct control, custom parameters
-   **Usage**: Copy commands from this guide

### **Option 4: Interactive API Docs**

-   **URL**: https://stock-analysis-production-31e9.up.railway.app/docs
-   **Features**: Swagger UI, try endpoints directly in browser

## 🔍 Expected Responses

### **Health Check Response**

```json
{
    "status": "healthy",
    "timestamp": "2025-06-14T07:30:00.000Z",
    "checks": {
        "database": {"status": "healthy"},
        "deepseek": {"status": "healthy"},
        "environment": {
            "status": "healthy",
            "api_token_configured": true
        }
    }
}
```

### **Portfolio Summary Response**

```json
{
    "portfolio_id": 1,
    "name": "Portfolio 1",
    "total_value": 100000.0,
    "positions": [],
    "performance": {
        "day_change": 0.0,
        "day_change_pct": 0.0
    }
}
```

### **LLM Analysis Response**

```json
{
    "analysis_id": "analysis_2025-06-14T07:30:00.000Z",
    "portfolio_id": 1,
    "analysis_type": "risk_assessment",
    "recommendations": ["Sample recommendation"],
    "risk_analysis": {"risk_score": 5.0},
    "opportunities": ["Sample opportunity"],
    "llm_response": "Sample LLM analysis response"
}
```

## 🚨 Common Status Codes

-   **200**: ✅ Success
-   **401**: ❌ Invalid API token
-   **404**: ❌ Endpoint not found
-   **422**: ❌ Invalid request data
-   **500**: ❌ Server error

## 🎉 Quick Test Commands

```bash
# Health check (no auth)
curl https://stock-analysis-production-31e9.up.railway.app/health

# List portfolios
curl -H "Authorization: Bearer default-dev-token" \
  https://stock-analysis-production-31e9.up.railway.app/portfolios/active

# Get portfolio summary
curl -H "Authorization: Bearer default-dev-token" \
  https://stock-analysis-production-31e9.up.railway.app/portfolio/1/summary

# Test all endpoints with Python script
API_TOKEN=default-dev-token uv run python scripts/test_api_endpoints.py
```

---

**🔗 Railway URL**: https://stock-analysis-production-31e9.up.railway.app
**📖 API Docs**: https://stock-analysis-production-31e9.up.railway.app/docs
**🔍 Health Check**: https://stock-analysis-production-31e9.up.railway.app/health
