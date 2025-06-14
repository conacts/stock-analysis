# 🤖 Trigger.dev Automation

**Automated stock analysis and portfolio management workflows**

## 📋 Overview

This directory contains trigger.dev automation scripts for the stock analysis system. These scripts enable scheduled and event-driven automation of:

-   Daily market analysis
-   Portfolio monitoring and rebalancing
-   News-driven stock alerts
-   Performance reporting

## 🚀 Setup

### Prerequisites

1. **Trigger.dev Account**: Sign up at [trigger.dev](https://trigger.dev)
2. **Node.js Project**: Initialize trigger.dev in the root directory
3. **Python Extension**: Configure Python support for trigger.dev

### Installation Steps

```bash
# 1. Initialize trigger.dev project (run from root directory)
npx @trigger.dev/cli@latest init

# 2. Install Python extension
npm add @trigger.dev/python

# 3. Configure trigger.config.ts (see example below)
```

### Configuration

Create `trigger.config.ts` in the root directory:

```typescript
import {defineConfig} from "@trigger.dev/sdk/v3";
import {pythonExtension} from "@trigger.dev/python/extension";

export default defineConfig({
    project: "<your-project-ref>",
    build: {
        extensions: [
            pythonExtension({
                scripts: ["./scripts/**/*.py", "./src/**/*.py"],
                requirementsFile: "./requirements.txt",
                devPythonBinaryPath: ".venv/bin/python",
            }),
        ],
    },
});
```

## 📊 Automation Workflows

### Daily Analysis Workflow

**Trigger**: Every weekday at 9:30 AM EST (market open)

**Actions**:

-   Fetch latest market data
-   Run LLM-enhanced analysis on watchlist
-   Generate buy/sell recommendations
-   Send Slack alerts for high-confidence signals
-   Store results in database

### Portfolio Monitoring Workflow

**Trigger**: Every weekday at 4:00 PM EST (market close)

**Actions**:

-   Check current portfolio positions
-   Analyze position performance
-   Generate rebalancing recommendations
-   Alert on significant position changes
-   Update portfolio snapshots

### News-Driven Analysis Workflow

**Trigger**: Real-time news events for portfolio stocks

**Actions**:

-   Monitor news feeds for portfolio stocks
-   Run LLM analysis on breaking news
-   Generate immediate alerts for significant events
-   Update stock analysis scores based on news

### Weekly Deep Analysis

**Trigger**: Every Sunday at 8:00 PM EST

**Actions**:

-   Comprehensive analysis of top 100 stocks
-   Portfolio performance attribution
-   Risk assessment and rebalancing recommendations
-   Weekly performance report generation

## 🔧 Technical Implementation

### Environment Variables

Required environment variables for trigger.dev:

```bash
# Database
DATABASE_URL=postgresql://...

# API Keys
DEEPSEEK_API_KEY=your_deepseek_key
SLACK_WEBHOOK_URL=your_slack_webhook

# Optional
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

### Python Script Integration

The automation scripts leverage existing Python modules:

-   `src/core/analyzer.py` - Stock analysis engine
-   `src/portfolio/portfolio_manager.py` - Portfolio management
-   `src/alerts/automated_alerts.py` - Alert system
-   `src/llm/deepseek_analyzer.py` - LLM analysis

### Error Handling

All automation workflows include:

-   Retry logic for API failures
-   Graceful degradation when services are unavailable
-   Comprehensive logging and monitoring
-   Slack notifications for critical errors

## 📈 Monitoring and Logging

### Performance Metrics

-   Analysis execution time
-   API call success rates
-   Database operation performance
-   Alert delivery success

### Cost Tracking

-   LLM API usage and costs
-   Database query optimization
-   Resource utilization monitoring

## 🚨 Alerts and Notifications

### High-Priority Alerts

-   Strong buy/sell signals (score > 70 or < 30)
-   Significant portfolio position changes (> 5%)
-   Breaking news affecting portfolio stocks
-   System errors and failures

### Daily Summaries

-   Market analysis results
-   Portfolio performance updates
-   Top stock recommendations
-   System health status

## 🔄 Development Workflow

### Testing Automation Scripts

```bash
# Test individual workflows locally
npm run dev

# Run specific trigger
npx @trigger.dev/cli@latest dev --filter="daily-analysis"

# Deploy to staging
npx @trigger.dev/cli@latest deploy --env staging
```

### Deployment

```bash
# Deploy to production
npx @trigger.dev/cli@latest deploy --env production

# Monitor deployments
npx @trigger.dev/cli@latest logs
```

## 📝 Next Steps

1. **Initialize trigger.dev project**
2. **Create automation task files**
3. **Configure environment variables**
4. **Test workflows in development**
5. **Deploy to production**
6. **Monitor and optimize performance**

---

**Ready to automate your stock analysis system!** 🚀
