# Trigger.dev Scheduled Tasks Summary

## 🎯 Overview

This document provides a comprehensive overview of all scheduled tasks in the AI Trading System using Trigger.dev v3 with cron-based scheduling.

**Total Scheduled Tasks**: 10
**Task Categories**: Portfolio Analysis (3), Health Monitoring (3), Stock Price Alerts (4)

## 📅 Complete Schedule Overview

### Daily Schedule (Eastern Time)

| Time    | Task                         | Frequency    | Description                                   |
| ------- | ---------------------------- | ------------ | --------------------------------------------- |
| 6:00 AM | Daily Health Summary         | Daily        | System health metrics and uptime report       |
| 7:00 AM | Weekly Health Analysis       | Sundays only | Weekly health trends and performance insights |
| 8:00 AM | Pre-Market Alert Review      | Weekdays     | Review overnight moves, adjust alerts         |
| 9:45 AM | Daily Portfolio Analysis     | Weekdays     | Portfolio analysis 15 min after market open   |
| 4:15 PM | After-Hours Alert Setup      | Weekdays     | Setup enhanced alerts for significant moves   |
| 4:30 PM | End-of-Day Portfolio Summary | Weekdays     | Daily performance summary and reports         |
| 8:00 PM | Weekly Portfolio Analysis    | Sundays only | Deep portfolio analysis with AI insights      |
| 9:00 PM | Weekly Alert Cleanup         | Sundays only | Clean old alerts, reset counters              |

### Continuous Monitoring

| Task                   | Schedule                       | Description                         |
| ---------------------- | ------------------------------ | ----------------------------------- |
| System Health Check    | Every 15 minutes               | Continuous system health monitoring |
| Stock Price Monitoring | Every 5 minutes (market hours) | Real-time price alert monitoring    |

## 📊 Detailed Task Breakdown

### 1. Portfolio Analysis Tasks

#### `dailyPortfolioAnalysisScheduled`

-   **Schedule**: `45 9 * * 1-5` (9:45 AM, Monday-Friday)
-   **Timezone**: America/New_York
-   **Purpose**: Daily portfolio analysis with DeepSeek AI
-   **Features**:
    -   Analyzes all active portfolios
    -   7-day LLM conversation history
    -   Risk assessment and recommendations
    -   Alert generation for significant changes
-   **Output**: Analysis results, alerts, performance metrics

#### `weeklyPortfolioAnalysisScheduled`

-   **Schedule**: `0 20 * * 0` (8:00 PM, Sundays)
-   **Timezone**: America/New_York
-   **Purpose**: Comprehensive weekly portfolio deep dive
-   **Features**:
    -   30-day LLM conversation history
    -   Risk assessment and rebalancing recommendations
    -   Sector analysis and correlation studies
    -   Performance attribution analysis
-   **Output**: Weekly reports, rebalancing suggestions, insights

#### `endOfDayPortfolioSummaryScheduled`

-   **Schedule**: `30 16 * * 1-5` (4:30 PM, Monday-Friday)
-   **Timezone**: America/New_York
-   **Purpose**: Daily portfolio performance summary
-   **Features**:
    -   Daily return calculations
    -   Top performers and losers identification
    -   Consolidated reporting across portfolios
    -   Alert generation for significant moves
-   **Output**: Daily reports, performance summaries

### 2. Health Monitoring Tasks

#### `systemHealthCheckScheduled`

-   **Schedule**: `*/15 * * * *` (Every 15 minutes)
-   **Timezone**: UTC
-   **Purpose**: Continuous system health monitoring
-   **Features**:
    -   Database connectivity checks
    -   API key validation
    -   Recent analysis activity verification
    -   Portfolio data integrity checks
-   **Output**: Health status, alerts for issues, uptime tracking

#### `dailyHealthSummaryScheduled`

-   **Schedule**: `0 6 * * *` (6:00 AM daily)
-   **Timezone**: America/New_York
-   **Purpose**: Daily system health summary
-   **Features**:
    -   24-hour health metrics compilation
    -   Uptime percentage calculation
    -   Issue summary and recommendations
    -   Performance trend analysis
-   **Output**: Daily health report, recommendations

#### `weeklyHealthAnalysisScheduled`

-   **Schedule**: `0 7 * * 0` (7:00 AM, Sundays)
-   **Timezone**: America/New_York
-   **Purpose**: Weekly health trend analysis
-   **Features**:
    -   7-day performance trend analysis
    -   Critical issue identification
    -   Performance improvement recommendations
    -   System reliability metrics
-   **Output**: Weekly health analysis, improvement plan

### 3. Stock Price Alert Tasks

#### `continuousStockPriceMonitoringScheduled`

-   **Schedule**: `*/5 9-16 * * 1-5` (Every 5 minutes, 9 AM-4 PM, Monday-Friday)
-   **Timezone**: America/New_York
-   **Purpose**: Real-time stock price alert monitoring
-   **Features**:
    -   Market hours awareness
    -   Batch processing to avoid rate limits
    -   AI-powered alert analysis
    -   Portfolio impact assessment
-   **Output**: Alert triggers, analysis, notifications

#### `afterHoursPriceAlertSetupScheduled`

-   **Schedule**: `15 16 * * 1-5` (4:15 PM, Monday-Friday)
-   **Timezone**: America/New_York
-   **Purpose**: Setup enhanced after-hours alerts
-   **Features**:
    -   Identifies positions with significant daily moves
    -   Creates tighter threshold alerts
    -   16-hour expiration for after-hours relevance
    -   Portfolio-specific alert configuration
-   **Output**: Enhanced alert configurations

#### `preMarketAlertReviewScheduled`

-   **Schedule**: `0 8 * * 1-5` (8:00 AM, Monday-Friday)
-   **Timezone**: America/New_York
-   **Purpose**: Pre-market alert review and adjustment
-   **Features**:
    -   Overnight price movement analysis
    -   Alert threshold adjustments based on volatility
    -   Gap alert creation for significant moves
    -   Pre-market summary generation
-   **Output**: Updated alerts, gap analysis, summaries

#### `weeklyAlertCleanupScheduled`

-   **Schedule**: `0 21 * * 0` (9:00 PM, Sundays)
-   **Timezone**: America/New_York
-   **Purpose**: Weekly alert maintenance and cleanup
-   **Features**:
    -   Removes alerts older than 30 days
    -   Deactivates orphaned alerts
    -   Resets trigger counters
    -   Generates performance reports
-   **Output**: Cleanup summary, performance metrics

## 🔧 Technical Implementation

### Cron Syntax Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

### Timezone Considerations

-   **Market-related tasks**: `America/New_York` (Eastern Time)
-   **System monitoring**: `UTC` for consistency
-   **Automatic DST handling**: Trigger.dev handles daylight saving time transitions

### Error Handling

-   All tasks include comprehensive error handling
-   Failed tasks send alerts to configured channels
-   Retry logic with exponential backoff
-   Graceful degradation when services are unavailable

## 📈 Monitoring and Observability

### Task Execution Tracking

-   Each task returns detailed execution results
-   Success/failure rates tracked
-   Execution duration monitoring
-   Next run scheduling verification

### Alert Channels

-   **Slack**: Real-time notifications for critical issues
-   **Email**: Daily/weekly summaries and reports
-   **Dashboard**: Trigger.dev dashboard for task monitoring

### Logging Strategy

-   Structured logging with consistent formatting
-   Emoji-based log categorization for easy scanning
-   Error stack traces for debugging
-   Performance metrics logging

## 🚀 Deployment and Management

### Environment Configuration

```bash
# Required Environment Variables
DATABASE_URL=postgresql://...          # Neon PostgreSQL database
DEEPSEEK_API_KEY=sk-...               # DeepSeek AI API key
PYTHON_API_URL=https://...            # Python API base URL
API_TOKEN=...                         # Internal API authentication
```

### Trigger.dev Configuration

```typescript
// trigger.config.ts
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

### Railway Deployment

-   Automatic deployment with main application
-   Environment variables managed via Railway dashboard
-   Scaling based on task execution requirements
-   Zero-downtime deployments

## 📋 Task Dependencies

### Internal Dependencies

-   All tasks depend on `src/automation/shared/env-validation.ts`
-   Portfolio tasks require active portfolios in database
-   Alert tasks require configured price alert rules
-   Health tasks require system endpoints to be accessible

### External Dependencies

-   **Neon PostgreSQL**: Database connectivity required
-   **DeepSeek API**: AI analysis functionality
-   **Python API**: Core trading system integration
-   **Market Data APIs**: Real-time price information

## 🔍 Troubleshooting Guide

### Common Issues

1. **Task Not Executing**

    - Check Trigger.dev dashboard for errors
    - Verify environment variables are set
    - Confirm cron syntax is correct

2. **Database Connection Errors**

    - Verify DATABASE_URL is accessible
    - Check Neon database status
    - Confirm connection pool limits

3. **API Integration Issues**

    - Verify PYTHON_API_URL is reachable
    - Check API_TOKEN authentication
    - Confirm API endpoints are responding

4. **Market Hours Issues**
    - Tasks may skip execution when markets are closed
    - Verify timezone configuration
    - Check market holiday calendars

### Debug Commands

```bash
# Test environment configuration
./run_with_env.sh python -c "from src.core.config import get_config; print(get_config())"

# Check database connectivity
./run_with_env.sh python -c "from src.db.database import get_db_connection; get_db_connection()"

# Verify API endpoints
curl -H "Authorization: Bearer $API_TOKEN" $PYTHON_API_URL/health
```

## 📊 Performance Metrics

### Expected Execution Times

-   **Portfolio Analysis**: 30-120 seconds per portfolio
-   **Health Checks**: 5-15 seconds
-   **Price Monitoring**: 10-30 seconds per batch
-   **Alert Processing**: 5-10 seconds per alert

### Resource Usage

-   **Memory**: 256MB-512MB per task execution
-   **CPU**: Low to moderate usage
-   **Network**: API calls to external services
-   **Database**: Read/write operations for data persistence

## 🎯 Success Metrics

### System Reliability

-   **Target Uptime**: 99.9%
-   **Task Success Rate**: >95%
-   **Alert Response Time**: <5 minutes
-   **Analysis Accuracy**: Continuous improvement through AI feedback

### Business Impact

-   **Portfolio Performance**: Enhanced through AI insights
-   **Risk Management**: Proactive alert system
-   **Operational Efficiency**: Automated analysis and reporting
-   **Decision Support**: Data-driven investment recommendations

---

**Last Updated**: December 2024
**System Status**: ✅ All tasks operational
**Next Review**: Weekly health analysis will identify any needed adjustments
