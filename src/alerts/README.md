# Stock Alert System 🚨

A comprehensive, intelligent stock alert system that sends real-time notifications to Slack when buy/sell opportunities are detected.

## Features

✅ **Slack Integration** - Rich, formatted notifications sent directly to your DMs
✅ **Smart Triggers** - Configurable rules for when to send alerts
✅ **Rate Limiting** - Prevents spam with daily limits and frequency controls
✅ **Market Hours** - Respects trading hours (configurable)
✅ **Risk Management** - Warns about high allocation recommendations
✅ **Comprehensive Testing** - 68 tests with 95%+ coverage

## Quick Start

### 1. Set Up Slack App (Free!)

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "Stock Alerts" and select your workspace
4. Go to "OAuth & Permissions"
5. Add these scopes:
    - `chat:write`
    - `chat:write.public`
6. Click "Install to Workspace"
7. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 2. Get Your Slack User ID

1. In Slack, click your profile picture
2. Click "Profile" → "More" → "Copy member ID"
3. Save this ID (starts with `U`)

### 3. Set Environment Variables

```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_USER_ID="U1234567890"
```

### 4. Test the System

```bash
python alert_manager.py test
```

You should receive a test message in your Slack DMs!

## Usage Examples

### Test Alert System

```bash
python alert_manager.py test
```

### Scan Specific Stocks

```bash
python alert_manager.py scan AAPL MSFT GOOGL
```

### Scan Default Watchlist

```bash
python alert_manager.py watchlist
```

### Send Daily Summary

```bash
python alert_manager.py daily-summary
```

### Check System Status

```bash
python alert_manager.py status
```

## Programmatic Usage

```python
from src.alerts import create_alert_system, AlertConfig

# Create alert system
alert_system = create_alert_system()

# Test the system
success = await alert_system.test_alert_system()

# Scan a single stock
alert_sent = await alert_system.analyze_and_alert("AAPL")

# Scan multiple stocks
results = await alert_system.scan_watchlist(["AAPL", "MSFT", "GOOGL"])

# Send daily summary
await alert_system.run_daily_summary()
```

## Configuration

### Alert Triggers

```python
from src.alerts import AlertConfig

config = AlertConfig(
    min_buy_score=75.0,           # Minimum score for buy alerts
    min_strong_buy_score=85.0,    # Minimum score for strong buy alerts
    min_confidence_threshold="Medium",  # Minimum confidence level
    trigger_ratings=["Buy", "Strong Buy"],  # Which ratings trigger alerts

    # Time restrictions
    market_hours_only=True,       # Only send during market hours
    start_time=time(9, 30),       # Market open (9:30 AM)
    end_time=time(16, 0),         # Market close (4:00 PM)

    # Rate limiting
    max_alerts_per_day=10,        # Maximum alerts per day
    min_hours_between_same_stock=4,  # Minimum hours between alerts for same stock

    # Risk management
    max_allocation_threshold=10.0,  # Warn if allocation > 10%
    exclude_symbols=["TSLA"],     # Never alert for these symbols
)

# Apply configuration
alert_system.update_config(config)
```

### Custom Filters

```python
def only_tech_stocks(analysis):
    """Only alert for tech stocks"""
    tech_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    return analysis.get("symbol") in tech_symbols

def high_volume_only(analysis):
    """Only alert for high volume stocks"""
    volume = analysis.get("fundamentals", {}).get("volume", 0)
    return volume > 1_000_000

config = AlertConfig(
    custom_filters=[only_tech_stocks, high_volume_only]
)
```

## Alert Types

| Type              | Description             | Trigger Conditions                    |
| ----------------- | ----------------------- | ------------------------------------- |
| **BUY_SIGNAL**    | Regular buy opportunity | Score ≥ 75, Rating = "Buy"            |
| **STRONG_BUY**    | High-confidence buy     | Score ≥ 85, Rating = "Buy/Strong Buy" |
| **RISK_WARNING**  | High allocation warning | Suggested allocation > 10%            |
| **DAILY_SUMMARY** | End-of-day summary      | Manual trigger                        |

## Slack Message Format

### Stock Alert Example

```
🚀 BUY_SIGNAL: AAPL

Rating: Buy                    Confidence: High
Score: 85.2/100               Allocation: 5.0%

Current Price: $180.50        Target Price: $200.00
Upside Potential: +10.8%      Time: 14:30:15
```

### Daily Summary Example

```
📊 Daily Analysis Summary - 2024-06-14

Top 5 Stock Picks Today

1. AAPL - Buy (85.2/100)
2. MSFT - Strong Buy (90.1/100)
3. GOOGL - Buy (82.7/100)

Total Analyzed: 3
Avg Score: 86.0
Buy Signals: 3
```

## Architecture

```
src/alerts/
├── __init__.py              # Module exports
├── slack_alerts.py          # Slack notification system
├── alert_triggers.py        # Alert trigger logic
├── automated_alerts.py      # Main orchestrator
└── README.md               # This file

alert_manager.py            # CLI tool
```

### Components

-   **SlackNotifier**: Handles Slack API communication and message formatting
-   **AlertTrigger**: Determines when alerts should be sent based on analysis
-   **AutomatedAlertSystem**: Orchestrates analysis, triggers, and notifications

## Testing

Run the comprehensive test suite:

```bash
# Run all alert tests
uv run pytest tests/unit/test_slack_alerts.py tests/unit/test_alert_triggers.py tests/unit/test_automated_alerts.py -v

# Run with coverage
uv run pytest tests/unit/test_*alerts*.py --cov=src/alerts --cov-report=html
```

**Test Coverage**: 68 tests covering:

-   Slack API integration
-   Alert trigger logic
-   Rate limiting
-   Error handling
-   Market hours restrictions
-   Custom filters

## Automation Ideas

### Cron Job (Daily Summary)

```bash
# Add to crontab for daily 4 PM summary
0 16 * * 1-5 cd /path/to/stock-analysis && python alert_manager.py daily-summary
```

### Continuous Monitoring

```python
import asyncio
from src.alerts import create_alert_system

async def monitor_stocks():
    alert_system = create_alert_system()
    watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    while True:
        await alert_system.scan_watchlist(watchlist)
        await asyncio.sleep(300)  # Check every 5 minutes

# Run continuously
asyncio.run(monitor_stocks())
```

### Trigger.dev Integration

```javascript
// Example Trigger.dev job
import {cronTrigger} from "@trigger.dev/sdk";

export const stockAlerts = cronTrigger({
    id: "stock-alerts",
    cron: "0 */15 9-16 * * 1-5", // Every 15 minutes during market hours
    run: async (payload, io) => {
        await io.runTask("scan-stocks", async () => {
            // Call your Python alert system
            const result = await exec("python alert_manager.py watchlist");
            return result;
        });
    },
});
```

## Troubleshooting

### Common Issues

**"Slack bot token required"**

-   Make sure `SLACK_BOT_TOKEN` environment variable is set
-   Token should start with `xoxb-`

**"Failed to connect to Slack API"**

-   Check your bot token is valid
-   Ensure your Slack app has proper permissions
-   Verify your workspace allows the app

**"No alerts triggered"**

-   Check if you're within market hours (if enabled)
-   Verify stock scores meet minimum thresholds
-   Check daily alert limits haven't been reached

**"Analysis failed"**

-   Ensure DeepSeek API key is set for LLM analysis
-   Check internet connection for stock data
-   Verify stock symbols are valid

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your alert system - you'll see detailed logs
```

## Security Notes

-   **API Keys**: Never commit Slack tokens to version control
-   **Rate Limits**: Slack has API rate limits - the system respects them
-   **Permissions**: Bot only needs `chat:write` - minimal permissions
-   **Privacy**: Messages are sent as DMs only to you

## Cost

-   **Slack**: Completely free
-   **Stock Data**: Free (yfinance)
-   **LLM Analysis**: ~$0.01 per analysis (DeepSeek)
-   **Total**: Virtually free for personal use

## Next Steps

1. **Set up Slack app** (5 minutes)
2. **Test the system** (`python alert_manager.py test`)
3. **Configure your preferences** (edit AlertConfig)
4. **Set up automation** (cron job or Trigger.dev)
5. **Monitor and refine** (adjust thresholds based on results)

Happy trading! 📈
