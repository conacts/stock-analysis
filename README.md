# 🚀 Advanced Stock Analysis & AI Trading System

A comprehensive, AI-powered stock analysis platform with automated monitoring, portfolio management, intelligent alerts, and **AI-driven trading capabilities** powered by DeepSeek AI and Trigger.dev automation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 169 Passing](https://img.shields.io/badge/tests-169%20passing-green.svg)](#testing)
[![API Status](https://img.shields.io/badge/API-100%25%20operational-brightgreen.svg)](https://stock-analysis-production-31e9.up.railway.app/health)

## ✨ Key Features

### 🤖 **AI Trading System** (NEW)

-   **DeepSeek AI Integration**: Advanced portfolio analysis and trading signal generation
-   **Risk Management**: Comprehensive risk assessment with position limits and emergency stops
-   **Trading Endpoints**: RESTful API for portfolio analysis, signal generation, and trade recommendations
-   **Market Data Integration**: Real-time price data with technical indicators
-   **30-Second Timeouts**: Robust timeout handling across all endpoints

### 🔄 **Automated Stock Monitoring**

-   **Real-time Price Alerts**: Automated notifications for significant price movements (±5%, ±10%, ±15%)
-   **Portfolio Analysis**: Scheduled analysis with LLM-powered insights
-   **Health Monitoring**: System health checks with comprehensive status reporting
-   **Trigger.dev Integration**: Automated tasks for comprehensive monitoring

### 🧠 **AI-Enhanced Analysis**

-   **DeepSeek LLM Integration**: Sophisticated market analysis and insights with working API integration
-   **Intelligent Scoring**: AI-enhanced composite scoring system (169 passing tests)
-   **News Impact Analysis**: Real-time sentiment and catalyst identification
-   **Growth Catalyst Detection**: AI-powered identification of growth drivers

### 💼 **Portfolio Management**

-   **Multi-Portfolio Support**: Personal, IRA, 401k tracking with real-time P&L
-   **Risk Assessment**: Volatility analysis, sector risk, market correlation
-   **AI Trading Recommendations**: Automated trade suggestions with position sizing
-   **Slack Integration**: Real-time alerts and daily summaries

## 🚀 Quick Start

### Prerequisites

-   Python 3.11+ with [uv](https://docs.astral.sh/uv/) package manager
-   Node.js 18+ with Bun (for Trigger.dev automation)
-   DeepSeek API key (required for AI features)

### Installation & Setup

```bash
# 1. Clone and setup
git clone https://github.com/your-username/stock-analysis.git
cd stock-analysis
make dev-setup

# 2. Configure environment variables
cp .env.example .env.local
# Edit .env.local with your API keys (see Environment Configuration below)

# 3. Verify installation
./run_with_env.sh make test-fast  # Should show 169 passing tests

# 4. Start the API server with environment
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
# Server starts on http://localhost:8000 with all services configured

# 5. Test the system
./run_with_env.sh bash -c "API_BASE_URL=http://localhost:8000 uv run python tools/check_api_environments.py"
# Should show 100% success rate with all endpoints working
```

### Environment Configuration

Create a `.env.local` file with your API keys:

```bash
# Required for AI features
DEEPSEEK_API_KEY=sk-your-deepseek-api-key

# Required for database
DATABASE_URL=postgresql://user:pass@host:port/database

# Required for API authentication
API_TOKEN=your-secure-api-token

# Required for automation
PYTHON_API_URL=http://localhost:8000
TRIGGER_SECRET_KEY=tr_prod_your-trigger-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-trigger-token

# Optional for enhanced features
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#your-channel
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
```

**Important**: Always use `./run_with_env.sh` to run commands that need environment variables loaded.

## 🏗️ System Architecture

```
stock-analysis/
├── src/
│   ├── api/
│   │   ├── main.py                    # FastAPI server with all endpoints
│   │   ├── simple_trading_endpoints.py # AI trading API endpoints
│   │   └── trading_endpoints.py       # Advanced trading system (Phase 2)
│   ├── trading/                       # AI Trading System (NEW)
│   │   ├── ai_engine.py              # DeepSeek-powered trading engine
│   │   ├── market_data.py            # Real-time market data provider
│   │   ├── risk_manager.py           # Risk assessment and management
│   │   └── README.md                 # Trading system documentation
│   ├── models/
│   │   └── trading_models.py         # Pydantic models for trading
│   ├── core/analyzer.py              # Main analysis engine
│   ├── portfolio/                    # Portfolio management system
│   ├── llm/deepseek_analyzer.py      # AI integration
│   ├── alerts/slack_alerts.py        # Notification system
│   └── db/                           # Database models & migrations
├── tools/
│   └── check_api_environments.py     # Comprehensive API testing
├── tests/                            # 169 comprehensive tests
├── run_with_env.sh                   # Environment loader script
└── trigger.config.ts                 # Trigger.dev configuration
```

## 🤖 AI Trading System

### Available Endpoints

**Production API**: `https://stock-analysis-production-31e9.up.railway.app`

-   `GET /trading/trading-config` - Get trading configuration and limits
-   `GET /trading/market-status` - Current market status and hours
-   `GET /trading/risk-status/{portfolio_id}` - Portfolio risk assessment
-   `POST /trading/emergency-stop` - Emergency trading halt
-   `GET /health` - System health with 30-second timeout

### Testing the API

```bash
# Test production environment
./run_with_env.sh uv run python tools/check_api_environments.py

# Test local environment
./run_with_env.sh bash -c "API_BASE_URL=http://localhost:8000 uv run python tools/check_api_environments.py"

# Test specific endpoint
curl -H "Authorization: Bearer your-token" \
  https://stock-analysis-production-31e9.up.railway.app/trading/trading-config
```

### AI Trading Features

-   **Portfolio Analysis**: AI-powered analysis using DeepSeek for market insights
-   **Signal Generation**: Technical and fundamental analysis with confidence scoring
-   **Risk Management**: Position limits (10%), daily loss limits (2%), emergency stops
-   **Trade Recommendations**: Position sizing and entry/exit strategies
-   **Market Data**: Real-time prices, technical indicators, sentiment analysis

## 🤖 Automation System

### Setup Trigger.dev Development

```bash
# 1. Start development server
npx trigger.dev@latest dev

# 2. Test portfolio analysis task
# The task will call your local/production API endpoints

# 3. Deploy to production
bunx trigger.dev@latest deploy
```

### Available Tasks

-   **Portfolio Analysis**: AI-powered portfolio insights with 300s timeout
-   **Daily Portfolio Analysis**: Scheduled analysis with 600s timeout
-   **Health Monitor**: System health checks
-   **Stock Price Alerts**: Real-time price movement notifications

## 💼 Portfolio Management

### Quick Commands

```bash
# Create and manage portfolios (with environment)
./run_with_env.sh uv run scripts/portfolio_manager.py create "My Portfolio" personal "Main investment portfolio"
./run_with_env.sh uv run scripts/portfolio_manager.py add 1 AAPL 100 150.00
./run_with_env.sh uv run scripts/portfolio_manager.py show 1

# Get AI-powered recommendations
./run_with_env.sh uv run scripts/portfolio_manager.py sells 1    # Sell recommendations
./run_with_env.sh uv run scripts/portfolio_manager.py health 1   # Portfolio health check
```

### Features

-   **Real-time P&L**: Live position tracking with current market prices
-   **AI Risk Analysis**: DeepSeek-powered risk assessment and recommendations
-   **Trading Signals**: AI-generated buy/sell signals with confidence scores
-   **Performance Analytics**: Historical analysis and backtesting

## 🧪 Testing & Quality

We maintain high code quality with comprehensive testing:

```bash
# Run tests with environment loaded
./run_with_env.sh make test-fast          # Quick unit tests (169 tests, ~10s)
./run_with_env.sh make test-integration   # Integration tests (~30s)
./run_with_env.sh make test-all          # Complete test suite
./run_with_env.sh make coverage          # Generate coverage report
```

### Test Coverage

-   **Core Analyzer**: 80%+ coverage
-   **Portfolio Management**: 90%+ coverage
-   **LLM Components**: 88-92% coverage
-   **AI Trading System**: Comprehensive integration tests
-   **API Endpoints**: 100% operational (7/7 tests passing)
-   **Total**: 169 tests across unit and integration suites

### API Status

-   **Production**: ✅ 100% success rate (7/7 endpoints)
-   **Local**: ✅ 100% success rate with proper environment setup
-   **Trading Endpoints**: ✅ Fully operational
-   **DeepSeek Integration**: ✅ Working with API key
-   **30-Second Timeouts**: ✅ Implemented across all endpoints

## 📊 AI Trading Analysis Example

```python
{
    "portfolio_id": 1,
    "market_condition": "bullish",
    "ai_summary": "Portfolio shows strong performance with balanced risk profile",
    "key_opportunities": [
        "Tech sector showing momentum with AI growth drivers",
        "Market dip presents buying opportunities in quality names"
    ],
    "key_risks": [
        "High concentration in technology sector (65%)",
        "Portfolio beta of 1.15 indicates higher volatility"
    ],
    "recommended_actions": [
        "Consider rebalancing tech positions to reduce concentration",
        "Add defensive positions given current market volatility"
    ],
    "risk_assessment": {
        "overall_risk": "medium",
        "risk_score": 0.65,
        "daily_pnl": 125.50,
        "trading_halted": false
    }
}
```

## 🛠️ Development

### Daily Workflow

```bash
# Always use environment loader for development
./run_with_env.sh make check             # Quick lint + test
./run_with_env.sh make format            # Format code
./run_with_env.sh make pre-commit        # Full pre-commit checks
```

### API Development

```bash
# Start API server with environment
./run_with_env.sh bash -c "cd src/api && uv run python main.py"

# Test endpoints
curl http://localhost:8000/health  # Test API health
curl http://localhost:8000/docs    # View API documentation

# Test trading endpoints
curl -H "Authorization: Bearer default-dev-token" \
  http://localhost:8000/trading/trading-config
```

### Automation Development

```bash
npx trigger.dev@latest dev        # Start development server
bunx trigger.dev@latest deploy     # Deploy to production
```

## 📚 Documentation Structure

-   **[AI_TRADING_PLAN.md](AI_TRADING_PLAN.md)**: Complete AI trading system roadmap
-   **[API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)**: API testing and validation guide
-   **[DEVELOPMENT.md](DEVELOPMENT.md)**: Complete development setup and workflow
-   **[DEPLOYMENT.md](DEPLOYMENT.md)**: GitHub Actions and Railway deployment guide
-   **[CONFIGURATION.md](CONFIGURATION.md)**: Environment and configuration guide
-   **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines and standards

## 🚨 Important Notes

### Environment Setup

-   **Always use `./run_with_env.sh`** for commands that need environment variables
-   **DeepSeek API key is required** for AI features to work properly
-   **Database URL is required** for portfolio and trading functionality
-   **API token is required** for authentication

### Production Deployment

-   **Railway**: Automatic deployment from main branch
-   **Environment Variables**: Set in Railway dashboard
-   **Health Monitoring**: Available at `/health` endpoint
-   **API Documentation**: Available at `/docs` endpoint

### AI Trading System Status

-   **Phase 1**: ✅ Complete - AI Analysis Engine with DeepSeek integration
-   **Phase 2**: 🚧 In Development - Trade execution and broker integration
-   **Phase 3**: 📋 Planned - Live broker integration
-   **Phase 4**: 📋 Planned - Advanced monitoring and control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Set up environment: Copy `.env.example` to `.env.local` and configure
4. Add tests for your changes
5. Run the test suite: `./run_with_env.sh make test-all`
6. Commit using conventional commits: `git commit -m "feat: add amazing feature"`
7. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⚠️ Disclaimer**: This tool is for educational and research purposes only. The AI trading system is currently in development and should not be used for live trading without proper testing and risk management. Always consult with financial professionals before making investment decisions. Past performance does not guarantee future results.
