# 🤖 Stock Analysis Automation System

Comprehensive automation powered by Trigger.dev for 24/7 stock monitoring, portfolio analysis, and intelligent alerts.

## 🎯 Overview

Our automation system provides:

-   **18 Automated Tasks** for comprehensive monitoring
-   **Real-time Price Alerts** with configurable thresholds
-   **Scheduled Portfolio Analysis** with LLM insights
-   **Health Monitoring** with email notifications
-   **Fail-fast Environment Validation** for production reliability

## 🏗️ Architecture

```
src/automation/
├── index.ts                    # Main entry point
├── schedules/                  # Cron schedule definitions
├── shared/
│   ├── env-validation.ts      # Environment validation utilities
│   ├── types.ts               # TypeScript type definitions
│   └── utils.ts               # Shared utilities
├── tasks/
│   ├── health-monitor.ts      # System health checks
│   ├── portfolio-analysis.ts  # LLM-powered portfolio insights
│   ├── scheduled-orchestrator.ts # Coordinated task execution
│   └── stock-price-alerts.ts  # Real-time price monitoring
└── test-payloads.json         # Test data for development
```

## 🚀 Quick Setup

### 1. Deploy to Trigger.dev

```bash
# Deploy the automation system
bunx trigger.dev@latest deploy

# Start development server for testing
bunx trigger.dev@latest dev
```

### 2. Configure Environment Variables

In your Trigger.dev dashboard, set these environment variables:

**Required:**

-   `PYTHON_API_URL` - Your FastAPI server URL (e.g., `http://localhost:8000`)
-   `API_TOKEN` - Secure token for API authentication

**Optional but Recommended:**

-   `DEEPSEEK_API_KEY` - For AI-powered analysis
-   `DATABASE_URL` - For portfolio data storage

### 3. Test the System

```bash
# Test with mock environment variables locally
export API_TOKEN="mock-api-token-12345"
export PYTHON_API_URL="http://localhost:8000"
export DEEPSEEK_API_KEY="mock-deepseek-key-67890"

# Start the API server
make run-api

# Start Trigger.dev development server
bunx trigger.dev@latest dev
```

## 📋 Available Tasks

### 🏥 Health Monitor (`health-monitor`)

-   **Frequency**: Every minute
-   **Purpose**: System health checks with email alerts
-   **Checks**: Environment variables, API connectivity, database status, recent analysis

### 📈 Stock Price Alerts (`stock-price-alerts`)

-   **Frequency**: Real-time monitoring
-   **Purpose**: Price movement notifications
-   **Thresholds**: ±5%, ±10%, ±15% price changes
-   **Features**: Market hours awareness, duplicate prevention

### 💼 Portfolio Analysis (`portfolio-analysis`)

-   **Frequency**: Scheduled (configurable)
-   **Purpose**: LLM-powered portfolio insights
-   **Features**: Risk assessment, rebalancing recommendations, performance analytics

### 🌅 Scheduled Orchestrator (`scheduled-orchestrator`)

-   **Frequency**: Multiple schedules
-   **Purpose**: Coordinated execution of multiple tasks
-   **Functions**: Pre-market analysis, overnight news analysis, market prep

## 🔧 Environment Validation

The system uses **fail-fast environment validation** to ensure reliability:

### Required Environment Variables

```typescript
interface RequiredEnvVars {
    PYTHON_API_URL: string; // FastAPI server URL
    API_TOKEN: string; // API authentication token
    DEEPSEEK_API_KEY?: string; // Optional: AI features
    DATABASE_URL?: string; // Optional: Enhanced storage
}
```

### Validation Features

-   **Immediate Failure**: Tasks fail fast when required variables are missing
-   **Clear Error Messages**: Detailed setup instructions in error output
-   **Environment Status**: Health checks report configuration status
-   **Mock Support**: Development-friendly mock values

## 🧪 Testing & Development

### Test Payloads

Use the provided test payloads for development:

```json
{
    "health_check": {},
    "price_alert": {
        "symbol": "AAPL",
        "current_price": 150.0,
        "previous_price": 145.0,
        "change_percent": 3.45
    },
    "portfolio_analysis": {
        "portfolio_id": 1,
        "analysis_type": "daily"
    }
}
```

### Local Development

```bash
# 1. Start the FastAPI server
make run-api

# 2. Set mock environment variables
export API_TOKEN="mock-api-token-12345"
export PYTHON_API_URL="http://localhost:8000"
export DEEPSEEK_API_KEY="mock-deepseek-key-67890"

# 3. Start Trigger.dev development server
bunx trigger.dev@latest dev

# 4. Test tasks in the Trigger.dev dashboard
# Visit: https://cloud.trigger.dev/
```

### Testing Individual Tasks

```bash
# Test health monitor
curl -X POST "https://api.trigger.dev/api/v1/projects/YOUR_PROJECT_ID/tasks/health-monitor/test" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'

# Test price alerts
curl -X POST "https://api.trigger.dev/api/v1/projects/YOUR_PROJECT_ID/tasks/stock-price-alerts/test" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "current_price": 150.00, "previous_price": 145.00}'
```

## 📊 Monitoring & Observability

### Health Check Results

The health monitor provides comprehensive system status:

```typescript
interface HealthCheckResult {
    status: "healthy" | "unhealthy";
    timestamp: string;
    checks: {
        environment: EnvironmentCheck;
        api_connectivity: ApiCheck;
        database: DatabaseCheck;
        recent_analysis: AnalysisCheck;
    };
    summary: string;
}
```

### Task Execution Logs

Monitor task execution in the Trigger.dev dashboard:

-   **Execution History**: Complete log of all task runs
-   **Error Tracking**: Detailed error messages and stack traces
-   **Performance Metrics**: Execution time and resource usage
-   **Environment Status**: Real-time configuration validation

## 🚨 Error Handling

### Common Issues & Solutions

**Missing Environment Variables:**

```
❌ Missing environment variables: PYTHON_API_URL, API_TOKEN
```

**Solution**: Set required variables in Trigger.dev dashboard

**API Connectivity Issues:**

```
❌ Failed to connect to Python API: Connection refused
```

**Solution**: Ensure FastAPI server is running and accessible

**Database Connection Errors:**

```
⚠️ DATABASE_URL not configured
```

**Solution**: Set DATABASE_URL for enhanced features (optional)

### Production Deployment

1. **Set Production Environment Variables** in Trigger.dev dashboard
2. **Deploy FastAPI Server** to a production environment
3. **Update PYTHON_API_URL** to point to production server
4. **Monitor Health Checks** for system status
5. **Set up Email Alerts** for critical failures

## 🔄 Continuous Integration

The automation system integrates with your CI/CD pipeline:

```bash
# Test automation tasks
make test-automation

# Deploy to production
bunx trigger.dev@latest deploy

# Verify deployment
bunx trigger.dev@latest status
```

## 📚 Additional Resources

-   **[Trigger.dev Documentation](https://trigger.dev/docs)**
-   **[FastAPI Documentation](https://fastapi.tiangolo.com/)**
-   **[Environment Configuration Guide](../../CONFIGURATION.md)**
-   **[Main README](../../README.md)**

---

**💡 Pro Tip**: Use the Trigger.dev dashboard to monitor task execution, view logs, and test individual tasks during development.
