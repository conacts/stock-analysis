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

# AI Trading System - Automation Tasks

This directory contains all automated tasks for the AI Trading System using Trigger.dev v3 with comprehensive scheduling.

## 📋 Overview

The automation system provides:

-   **Portfolio Analysis**: Daily, weekly, and end-of-day analysis with DeepSeek AI
-   **Health Monitoring**: System health checks, daily summaries, and weekly analysis
-   **Stock Price Alerts**: Continuous monitoring, after-hours setup, and pre-market review
-   **Market Hours Awareness**: Tasks automatically adjust based on market hours
-   **Comprehensive Logging**: Detailed logging and error handling for all tasks

## 🕐 Scheduled Tasks

### Portfolio Analysis Tasks

| Task                                | Schedule        | Timezone         | Description                                 |
| ----------------------------------- | --------------- | ---------------- | ------------------------------------------- |
| `dailyPortfolioAnalysisScheduled`   | `45 9 * * 1-5`  | America/New_York | Daily analysis 15 minutes after market open |
| `weeklyPortfolioAnalysisScheduled`  | `0 20 * * 0`    | America/New_York | Deep weekly analysis on Sundays at 8 PM     |
| `endOfDayPortfolioSummaryScheduled` | `30 16 * * 1-5` | America/New_York | End-of-day summary after market close       |

### Health Monitoring Tasks

| Task                            | Schedule       | Timezone         | Description                               |
| ------------------------------- | -------------- | ---------------- | ----------------------------------------- |
| `systemHealthCheckScheduled`    | `*/15 * * * *` | UTC              | System health check every 15 minutes      |
| `dailyHealthSummaryScheduled`   | `0 6 * * *`    | America/New_York | Daily health summary at 6 AM              |
| `weeklyHealthAnalysisScheduled` | `0 7 * * 0`    | America/New_York | Weekly health analysis on Sundays at 7 AM |

### Stock Price Alert Tasks

| Task                                      | Schedule           | Timezone         | Description                                          |
| ----------------------------------------- | ------------------ | ---------------- | ---------------------------------------------------- |
| `continuousStockPriceMonitoringScheduled` | `*/5 9-16 * * 1-5` | America/New_York | Price monitoring every 5 minutes during market hours |
| `afterHoursPriceAlertSetupScheduled`      | `15 16 * * 1-5`    | America/New_York | After-hours alert setup at 4:15 PM                   |
| `preMarketAlertReviewScheduled`           | `0 8 * * 1-5`      | America/New_York | Pre-market alert review at 8 AM                      |
| `weeklyAlertCleanupScheduled`             | `0 21 * * 0`       | America/New_York | Weekly alert cleanup on Sundays at 9 PM              |

## 📁 File Structure

```
src/automation/
├── tasks/
│   ├── scheduled-portfolio-analysis.ts    # Portfolio analysis schedules
│   ├── scheduled-health-monitoring.ts     # Health monitoring schedules
│   ├── scheduled-stock-alerts.ts          # Stock alert schedules
│   ├── portfolio-analysis.ts              # Original portfolio tasks
│   ├── health-monitor.ts                  # Original health tasks
│   ├── stock-price-alerts.ts              # Original alert tasks
│   ├── scheduled-orchestrator.ts          # Market hours orchestration
│   ├── simple-test.ts                     # Simple test task
│   └── index.ts                           # Task exports
├── shared/
│   ├── types.ts                           # TypeScript interfaces
│   └── env-validation.ts                  # Environment validation
└── README.md                              # This file
```

## 🚀 Key Features

### Market Hours Awareness

-   Tasks automatically check market status before execution
-   Different schedules for market hours vs. after-hours
-   Timezone-aware scheduling (America/New_York for market-related tasks)

### Comprehensive Error Handling

-   All tasks include try-catch blocks with detailed logging
-   Failed tasks send alerts to configured channels
-   Graceful degradation when services are unavailable

### Batch Processing

-   Stock price monitoring processes alerts in batches to avoid rate limiting
-   Configurable batch sizes and delays between batches

### AI Integration

-   DeepSeek AI integration for portfolio analysis
-   LLM conversation history for context-aware analysis
-   AI-powered alert analysis and recommendations

### Flexible Scheduling

-   Uses Trigger.dev's `schedules.task()` for declarative scheduling
-   Cron syntax support with timezone specification
-   Easy to modify schedules without code changes

## 📊 Task Details

### Portfolio Analysis

#### Daily Portfolio Analysis (`dailyPortfolioAnalysisScheduled`)

-   **When**: Every weekday at 9:45 AM EST (15 minutes after market open)
-   **What**: Analyzes all active portfolios with 7-day LLM history
-   **Output**: Portfolio analysis results, alerts, and recommendations

#### Weekly Portfolio Analysis (`weeklyPortfolioAnalysisScheduled`)

-   **When**: Every Sunday at 8:00 PM EST
-   **What**: Deep analysis with 30-day LLM history, risk assessment, rebalancing recommendations
-   **Output**: Comprehensive weekly reports and insights

#### End-of-Day Summary (`endOfDayPortfolioSummaryScheduled`)

-   **When**: Every weekday at 4:30 PM EST (after market close)
-   **What**: Daily performance summary, top performers/losers, consolidated reporting
-   **Output**: Daily portfolio reports sent to configured channels

### Health Monitoring

#### System Health Check (`systemHealthCheckScheduled`)

-   **When**: Every 15 minutes
-   **What**: Checks database, API keys, recent analysis, portfolio data
-   **Output**: Health status, alerts for issues, uptime tracking

#### Daily Health Summary (`dailyHealthSummaryScheduled`)

-   **When**: Every day at 6:00 AM EST
-   **What**: 24-hour health metrics, uptime calculation, issue summary
-   **Output**: Daily health report with recommendations

#### Weekly Health Analysis (`weeklyHealthAnalysisScheduled`)

-   **When**: Every Sunday at 7:00 AM EST
-   **What**: 7-day trend analysis, performance insights, critical issue identification
-   **Output**: Weekly health analysis with improvement recommendations

### Stock Price Alerts

#### Continuous Price Monitoring (`continuousStockPriceMonitoringScheduled`)

-   **When**: Every 5 minutes during market hours (9:30 AM - 4:00 PM EST, Mon-Fri)
-   **What**: Monitors all active price alerts, triggers notifications
-   **Output**: Alert triggers, LLM analysis, portfolio impact assessment

#### After-Hours Alert Setup (`afterHoursPriceAlertSetupScheduled`)

-   **When**: Every weekday at 4:15 PM EST
-   **What**: Creates enhanced alerts for positions with significant daily moves
-   **Output**: Tighter threshold alerts for after-hours monitoring

#### Pre-Market Alert Review (`preMarketAlertReviewScheduled`)

-   **When**: Every weekday at 8:00 AM EST
-   **What**: Reviews overnight moves, adjusts alert thresholds, creates gap alerts
-   **Output**: Updated alerts, pre-market summary, gap analysis

#### Weekly Alert Cleanup (`weeklyAlertCleanupScheduled`)

-   **When**: Every Sunday at 9:00 PM EST
-   **What**: Cleans old alerts, deactivates orphaned alerts, resets trigger counts
-   **Output**: Cleanup summary, weekly alert performance report

## 🔧 Configuration

### Environment Variables

All tasks use the shared environment validation system:

-   `DATABASE_URL`: PostgreSQL connection (Neon database)
-   `DEEPSEEK_API_KEY`: DeepSeek AI API key
-   `PYTHON_API_URL`: Python API base URL
-   `API_TOKEN`: Internal API authentication token

### Task Configuration

Tasks are configured in `trigger.config.ts`:

```typescript
export default defineConfig({
    project: "proj_mzlhbsovcueeykfqqakl",
    dirs: ["./src/automation/tasks"],
    maxDuration: 3600,
    retries: {
        enabledInDev: true,
        default: {
            maxAttempts: 3,
            minTimeoutInMs: 1000,
            maxTimeoutInMs: 10000,
            factor: 2,
            randomize: true,
        },
    },
});
```

## 📈 Monitoring and Alerts

### Task Execution Monitoring

-   All tasks return detailed execution results
-   Success/failure tracking with timestamps
-   Next run information for scheduling verification

### Alert Channels

-   Slack notifications for critical issues
-   Email alerts for system health problems
-   Portfolio-specific alerts for trading opportunities

### Logging

-   Comprehensive console logging with emojis for easy identification
-   Error logging with stack traces
-   Performance metrics and execution times

## 🧪 Testing

### Manual Task Triggering

Original tasks are still available for manual triggering:

-   `portfolioAnalysisTask`
-   `healthCheckTask`
-   `stockPriceMonitorTask`
-   etc.

### Development Testing

-   Use `simpleTestTask` for basic functionality testing
-   Environment-aware testing (development vs. production)
-   Comprehensive error handling for testing scenarios

## 🔄 Deployment

### Railway Deployment

-   Tasks are automatically deployed with the main application
-   Environment variables managed through Railway dashboard
-   Automatic scaling based on task execution needs

### Schedule Management

-   Schedules are declarative and version-controlled
-   No manual cron job setup required
-   Easy to modify schedules through code changes

## 📚 Usage Examples

### Importing Tasks

```typescript
import {
    dailyPortfolioAnalysisScheduled,
    systemHealthCheckScheduled,
    continuousStockPriceMonitoringScheduled,
} from "./src/automation/tasks";
```

### Manual Task Execution

```typescript
import {portfolioAnalysisTask} from "./src/automation/tasks";

// Trigger manual portfolio analysis
await portfolioAnalysisTask.trigger({
    portfolioId: 1,
    portfolioName: "My Portfolio",
    analysisType: "daily",
    includeLLMHistory: true,
    maxHistoryDays: 7,
});
```

## 🔍 Troubleshooting

### Common Issues

1. **Environment Variables**: Ensure all required environment variables are set
2. **Database Connection**: Verify DATABASE_URL points to accessible Neon database
3. **API Endpoints**: Confirm Python API is running and accessible
4. **Market Hours**: Tasks may skip execution when markets are closed

### Debug Mode

-   Enable detailed logging by setting log level in trigger.config.ts
-   Use development environment for testing without affecting production data
-   Monitor task execution through Trigger.dev dashboard

## 🚀 Future Enhancements

### Planned Features

-   Dynamic schedule adjustment based on market volatility
-   Machine learning-based alert threshold optimization
-   Integration with additional data sources
-   Advanced portfolio rebalancing automation
-   Real-time market sentiment analysis

### Extensibility

-   Easy to add new scheduled tasks
-   Modular design for adding new analysis types
-   Configurable alert channels and notification preferences
-   Support for custom portfolio analysis strategies
