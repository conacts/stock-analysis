# 🚀 Advanced Stock Analysis System

A comprehensive, AI-powered stock analysis platform that combines traditional financial analysis with cutting-edge LLM technology for enhanced investment decision-making.

[![CI/CD Pipeline](https://github.com/your-username/stock-analysis/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/your-username/stock-analysis/actions)
[![Coverage](https://codecov.io/gh/your-username/stock-analysis/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/stock-analysis)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

### 🧠 AI-Enhanced Analysis

-   **LLM Integration**: DeepSeek AI for sophisticated market analysis
-   **Intelligent Scoring**: AI-enhanced composite scoring system
-   **News Impact Analysis**: Real-time news sentiment and catalyst identification
-   **Growth Catalyst Detection**: AI-powered identification of growth drivers

### 📊 Comprehensive Analysis Engine

-   **Fundamental Analysis**: P/E ratios, growth metrics, financial health
-   **Technical Analysis**: Moving averages, RSI, MACD, volatility metrics
-   **Sentiment Analysis**: News sentiment, social media trends
-   **Risk Assessment**: Volatility analysis, sector risk, market correlation

### 🎯 Investment Tools

-   **Master Stock Analyzer**: Interactive analysis for individual stocks
-   **Universe Screening**: S&P 500 scanning and ranking
-   **Portfolio Recommendations**: AI-driven allocation suggestions
-   **Performance Tracking**: Historical analysis and backtesting
-   **Slack Alerts**: Real-time stock alerts and daily summaries via Slack

### 🔧 Professional Development Setup

-   **Comprehensive Testing**: 120 unit tests, 7 integration tests, 88%+ coverage
-   **CI/CD Pipeline**: GitHub Actions with multi-Python version testing
-   **Code Quality**: Pre-commit hooks, linting, security scanning
-   **Documentation**: Extensive guides and API documentation

## 🚀 Quick Start

### Prerequisites

-   Python 3.11 or higher
-   [uv](https://docs.astral.sh/uv/) package manager
-   DeepSeek API key (optional, for AI features)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/stock-analysis.git
cd stock-analysis

# Complete development setup
make dev-setup

# Verify installation
make test-fast
```

### Basic Usage

```bash
# Run the master stock analyzer
make run-analyzer

# Or run the research application
make run-app

# Set up Slack alerts (optional)
uv run alert_manager.py test
uv run alert_manager.py watchlist

# Analyze a specific stock
python -c "
from src.core.analyzer import StockAnalyzer
analyzer = StockAnalyzer()
result = analyzer.analyze_stock('NVDA')
print(f'Rating: {result[\"rating\"]} | Score: {result[\"composite_score\"]:.1f}')
"
```

## 📋 System Architecture

```
stock-analysis/
├── src/                    # Core application code
│   ├── core/              # Analysis engine and scoring
│   ├── llm/               # AI integration (DeepSeek)
│   ├── data/              # Data storage and retrieval
│   ├── db/                # Database models and migrations
│   ├── alerts/            # Slack notification system
│   └── pipeline/          # Research and screening pipelines
├── tests/                 # Comprehensive test suite
│   ├── unit/              # Fast unit tests (113 tests)
│   ├── integration/       # Integration tests (7 tests)
│   └── conftest.py        # Test configuration and fixtures
├── alert_manager.py       # CLI tool for managing alerts
├── .github/workflows/     # CI/CD pipeline configuration
└── scripts/               # Development and deployment scripts
```

## 🧪 Testing & Quality

Our system maintains high code quality through comprehensive testing:

```bash
# Run different test suites
make test-fast          # Quick unit tests (~10s)
make test-integration   # Integration tests (~30s)
make test-all          # Complete test suite
make coverage          # Generate coverage report

# Code quality checks
make lint              # Linting and style checks
make security          # Security vulnerability scanning
make format            # Auto-format code
```

### Test Coverage

-   **Core Analyzer**: 80%+ coverage
-   **LLM Components**: 88-92% coverage
-   **Slack Alerts**: 68 comprehensive tests
-   **Integration Tests**: Full workflow validation
-   **Total Tests**: 120 tests across unit and integration suites

## 📱 Slack Alerts System

Get real-time stock alerts and daily summaries delivered directly to your Slack workspace - completely free!

### Features

-   **Real-time Alerts**: Instant notifications for Buy/Strong Buy signals
-   **Rich Formatting**: Beautiful Slack blocks with stock data, prices, and upside potential
-   **Smart Filtering**: Market hours awareness, rate limiting, and duplicate prevention
-   **Daily Summaries**: End-of-day reports with top picks and portfolio statistics
-   **Risk Warnings**: Alerts for high allocation recommendations
-   **CLI Management**: Professional command-line tool for system control

### Quick Setup

```bash
# 1. Create a free Slack app at https://api.slack.com/apps
# 2. Add chat:write permission and install to your workspace
# 3. Set environment variables
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_USER_ID="@your-username"

# 4. Test the system
uv run alert_manager.py test

# 5. Start monitoring your watchlist
uv run alert_manager.py watchlist
```

### Alert Types

-   **BUY_SIGNAL**: Score ≥75, Rating="Buy"
-   **STRONG_BUY**: Score ≥85, Rating="Buy/Strong Buy"
-   **RISK_WARNING**: High allocation recommendations (>10%)
-   **DAILY_SUMMARY**: Portfolio overview with top picks

See [Slack Alerts Documentation](src/alerts/README.md) for complete setup guide.

## 🤖 AI Integration

### DeepSeek LLM Features

-   **Comprehensive Analysis**: Multi-factor AI evaluation
-   **News Impact Scoring**: Real-time news sentiment analysis
-   **Growth Catalyst Identification**: AI-powered catalyst detection
-   **Risk Assessment**: Enhanced risk evaluation with market context

### Configuration

```bash
# Set your DeepSeek API key
export DEEPSEEK_API_KEY="your-api-key-here"

# Test LLM integration
make test-llm
```

## 📊 Analysis Capabilities

### Scoring System

-   **Traditional Mode**: 50% fundamentals, 25% technical, 15% sentiment, 10% risk
-   **AI-Enhanced Mode**: 40% fundamentals, 20% technical, 30% LLM analysis, 10% risk

### Investment Ratings

-   **Strong Buy**: Score 80+ with high confidence
-   **Buy**: Score 60-79 with good confidence
-   **Hold**: Score 40-59 or low confidence
-   **Sell**: Score 20-39
-   **Strong Sell**: Score <20

### Risk Assessment

-   **Low Risk**: Stable, established companies
-   **Medium Risk**: Growth companies with moderate volatility
-   **High Risk**: Speculative or highly volatile stocks

## 🛠️ Development

### Development Workflow

```bash
# Set up development environment
make dev-setup

# Daily development commands
make check             # Quick lint + test
make format            # Format code
make test-fast         # Quick feedback

# Before committing (automatic via git hooks)
make pre-commit        # Full pre-commit checks

# Before pushing (automatic via git hooks)
make pre-push          # Comprehensive test suite
```

### Git Workflow

We use conventional commits and automated testing:

```bash
# Commit format
git commit -m "feat: add new analysis feature"
git commit -m "fix: resolve data parsing issue"
git commit -m "test: add comprehensive unit tests"

# Automated checks
# On commit: Fast tests + linting (~10s)
# On push: Full test suite (~30s)
# On PR: Complete CI/CD pipeline (~2min)
```

## 📈 Example Analysis Output

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
    "risk_score": 70.0,
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

## 📚 Documentation

-   **[Development Guide](DEVELOPMENT.md)**: Complete development workflow
-   **[Configuration Guide](CONFIGURATION.md)**: Setup and configuration
-   **[Testing Guide](tests/README.md)**: Testing framework and practices
-   **[API Documentation](src/README.md)**: Code structure and APIs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `make test-all`
5. Commit using conventional commits: `git commit -m "feat: add amazing feature"`
6. Push to your branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

-   **yfinance**: Financial data retrieval
-   **DeepSeek**: AI-powered analysis capabilities
-   **pandas**: Data manipulation and analysis
-   **pytest**: Comprehensive testing framework
-   **GitHub Actions**: CI/CD pipeline automation

## 📞 Support

-   **Issues**: [GitHub Issues](https://github.com/your-username/stock-analysis/issues)
-   **Discussions**: [GitHub Discussions](https://github.com/your-username/stock-analysis/discussions)
-   **Documentation**: [Project Wiki](https://github.com/your-username/stock-analysis/wiki)

---

**⚠️ Disclaimer**: This tool is for educational and research purposes only. Always consult with financial professionals before making investment decisions. Past performance does not guarantee future results.
