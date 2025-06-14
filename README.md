# 🚀 Advanced Stock Analysis System

A comprehensive, AI-powered stock analysis platform with automated monitoring, portfolio management, and intelligent alerts powered by Trigger.dev automation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 157 Passing](https://img.shields.io/badge/tests-157%20passing-green.svg)](#testing)

## ✨ Key Features

### 🤖 **Automated Stock Monitoring**

-   **Real-time Price Alerts**: Automated notifications for significant price movements (±5%, ±10%, ±15%)
-   **Portfolio Analysis**: Scheduled analysis with LLM-powered insights
-   **Health Monitoring**: System health checks with email alerts
-   **Trigger.dev Integration**: 18 automated tasks for comprehensive monitoring

### 🧠 **AI-Enhanced Analysis**

-   **DeepSeek LLM Integration**: Sophisticated market analysis and insights
-   **Intelligent Scoring**: AI-enhanced composite scoring system (157 passing tests)
-   **News Impact Analysis**: Real-time sentiment and catalyst identification
-   **Growth Catalyst Detection**: AI-powered identification of growth drivers

### 💼 **Portfolio Management**

-   **Multi-Portfolio Support**: Personal, IRA, 401k tracking with real-time P&L
-   **Risk Assessment**: Volatility analysis, sector risk, market correlation
-   **Rebalancing**: Automated recommendations and portfolio health scoring
-   **Slack Integration**: Real-time alerts and daily summaries

## 🚀 Quick Start

### Prerequisites

-   Python 3.11+ with [uv](https://docs.astral.sh/uv/) package manager
-   Node.js 18+ with Bun (for Trigger.dev automation)
-   DeepSeek API key (optional, for AI features)

### Installation & Setup

```bash
# 1. Clone and setup
git clone https://github.com/your-username/stock-analysis.git
cd stock-analysis
make dev-setup

# 2. Verify installation
make test-fast  # Should show 157 passing tests

# 3. Start the API server
make run-api    # Starts FastAPI server on http://localhost:8000

# 4. Test basic analysis
python -c "
from src.core.analyzer import StockAnalyzer
analyzer = StockAnalyzer()
result = analyzer.analyze_stock('NVDA')
print(f'Rating: {result[\"rating\"]} | Score: {result[\"composite_score\"]:.1f}')
"
```

### Environment Configuration

Create a `.env` file with your API keys:

```bash
# Required for AI features
DEEPSEEK_API_KEY=your-deepseek-api-key

# Required for automation (Trigger.dev dashboard)
PYTHON_API_URL=http://localhost:8000
API_TOKEN=your-secure-api-token

# Optional for enhanced features
DATABASE_URL=postgresql://user:pass@localhost/stockdb
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_USER_ID=@your-username
```

## 🏗️ System Architecture

```
stock-analysis/
├── src/
│   ├── api/main.py              # FastAPI server (NEW)
│   ├── automation/              # Trigger.dev tasks (NEW)
│   │   ├── tasks/              # 18 automated monitoring tasks
│   │   └── shared/             # Environment validation & utilities
│   ├── core/analyzer.py        # Main analysis engine
│   ├── portfolio/              # Portfolio management system
│   ├── llm/deepseek_analyzer.py # AI integration
│   ├── alerts/slack_alerts.py  # Notification system
│   └── db/                     # Database models & migrations
├── tests/                      # 157 comprehensive tests
├── scripts/run_api.py          # API server runner
└── trigger.config.ts           # Trigger.dev configuration
```

## 🤖 Automation System (NEW)

Our Trigger.dev-powered automation provides 24/7 monitoring:

### Available Tasks

-   **Health Monitor**: System health checks every minute
-   **Stock Price Alerts**: Real-time price movement notifications
-   **Portfolio Analysis**: Scheduled LLM-powered portfolio insights
-   **Pre-market Analysis**: Overnight news analysis and market prep
-   **Scheduled Orchestrator**: Coordinated multi-task execution

### Setup Automation

```bash
# 1. Deploy to Trigger.dev
bunx trigger.dev@latest deploy

# 2. Set environment variables in Trigger.dev dashboard:
PYTHON_API_URL=http://your-api-server.com
API_TOKEN=your-secure-token
DEEPSEEK_API_KEY=your-deepseek-key
DATABASE_URL=your-database-url

# 3. Start development server for testing
bunx trigger.dev@latest dev
```

## 💼 Portfolio Management

### Quick Commands

```bash
# Create and manage portfolios
uv run portfolio_manager.py create "My Portfolio" personal "Main investment portfolio"
uv run portfolio_manager.py add 1 AAPL 100 150.00
uv run portfolio_manager.py show 1

# Get AI-powered recommendations
uv run portfolio_manager.py sells 1    # Sell recommendations
uv run portfolio_manager.py health 1   # Portfolio health check

# Set up Slack alerts
uv run alert_manager.py test
uv run alert_manager.py watchlist
```

### Features

-   **Real-time P&L**: Live position tracking with current market prices
-   **Risk Analysis**: Sector concentration and volatility assessment
-   **AI Recommendations**: LLM-powered buy/sell suggestions
-   **Performance Analytics**: Historical analysis and backtesting

## 🧪 Testing & Quality

We maintain high code quality with comprehensive testing:

```bash
make test-fast          # Quick unit tests (157 tests, ~10s)
make test-integration   # Integration tests (~30s)
make test-all          # Complete test suite
make coverage          # Generate coverage report (88%+ coverage)
```

### Test Coverage

-   **Core Analyzer**: 80%+ coverage
-   **Portfolio Management**: 90%+ coverage
-   **LLM Components**: 88-92% coverage
-   **Automation Tasks**: Comprehensive integration tests
-   **Total**: 157 tests across unit and integration suites

## 📊 Analysis Output Example

```python
{
    "symbol": "NVDA",
    "rating": "Buy",
    "composite_score": 78.5,
    "confidence": 85,
    "analysis_method": "llm_enhanced",
    "fundamental_score": 82.0,
    "technical_score": 75.0,
    "sentiment_score": 80.0,
    "llm_analysis": {
        "investment_thesis": "Strong AI market position with robust fundamentals",
        "key_strengths": ["Market leadership", "Strong margins", "AI growth"],
        "key_risks": ["Market volatility", "Competition"],
        "time_horizon": "medium"
    },
    "recommendation": {
        "allocation": "6.0% of portfolio",
        "time_horizon": "6-18 months",
        "risk_level": "Medium"
    }
}
```

## 🛠️ Development

### Daily Workflow

```bash
make check             # Quick lint + test
make format            # Format code
make pre-commit        # Full pre-commit checks (automatic via git hooks)
```

### API Development

```bash
make run-api           # Start FastAPI server
curl http://localhost:8000/health  # Test API health
curl http://localhost:8000/docs    # View API documentation
```

### Automation Development

```bash
bunx trigger.dev@latest dev        # Start development server
bunx trigger.dev@latest deploy     # Deploy to production
```

## 📚 Documentation Structure

-   **[DEVELOPMENT.md](DEVELOPMENT.md)**: Complete development setup and workflow
-   **[DEPLOYMENT.md](DEPLOYMENT.md)**: GitHub Actions and Trigger.dev deployment guide
-   **[src/automation/README.md](src/automation/README.md)**: Trigger.dev automation guide
-   **[tests/README.md](tests/README.md)**: Testing framework and practices
-   **[src/alerts/README.md](src/alerts/README.md)**: Slack alerts setup guide

## 🚨 Important Notes

### Environment Validation

The system now uses **fail-fast environment validation**. Missing required environment variables will cause tasks to fail immediately with clear error messages, rather than silently using mock data.

### Mock Testing

For development, you can use mock values:

```bash
export API_TOKEN="mock-api-token-12345"
export PYTHON_API_URL="http://localhost:8000"
export DEEPSEEK_API_KEY="mock-deepseek-key-67890"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Add tests for your changes
4. Run the test suite: `make test-all`
5. Commit using conventional commits: `git commit -m "feat: add amazing feature"`
6. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⚠️ Disclaimer**: This tool is for educational and research purposes only. Always consult with financial professionals before making investment decisions. Past performance does not guarantee future results.
