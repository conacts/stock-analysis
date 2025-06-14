# 📁 Source Code Structure

Overview of the Stock Analysis System codebase architecture.

## 🏗️ Module Organization

```
src/
├── api/                     # FastAPI server (NEW)
│   └── main.py             # REST API endpoints for automation
├── automation/             # Trigger.dev automation (NEW)
│   ├── tasks/              # 18 automated monitoring tasks
│   └── shared/             # Environment validation & utilities
├── core/                   # Core analysis engine
│   └── analyzer.py         # Main stock analysis logic
├── portfolio/              # Portfolio management
│   ├── portfolio_analyzer.py
│   └── portfolio_manager.py
├── llm/                    # AI integration
│   ├── deepseek_analyzer.py
│   └── llm_scorer.py
├── alerts/                 # Notification system
│   └── slack_alerts.py
├── data/                   # Data handling
│   ├── stock_data.py
│   └── storage.py
├── db/                     # Database layer
│   ├── models.py
│   ├── connection.py
│   └── migrations.py
└── pipeline/               # Research workflows
    └── research_engine.py
```

## 🎯 Key Components

### 🤖 **API Server** (`api/`)

-   **FastAPI server** for automation integration
-   **Health checks** and system monitoring
-   **REST endpoints** for Trigger.dev tasks
-   **Authentication** and request validation

### 🔄 **Automation** (`automation/`)

-   **18 Trigger.dev tasks** for 24/7 monitoring
-   **Environment validation** with fail-fast approach
-   **Scheduled analysis** and price alerts
-   **Health monitoring** with email notifications

### 🧠 **Core Analysis** (`core/`)

-   **StockAnalyzer** - Main analysis engine
-   **Multi-factor scoring** (fundamental, technical, sentiment)
-   **AI-enhanced analysis** with DeepSeek integration
-   **157 comprehensive tests** with 80%+ coverage

### 💼 **Portfolio Management** (`portfolio/`)

-   **Multi-portfolio support** (Personal, IRA, 401k)
-   **Real-time P&L tracking** with current market prices
-   **Risk assessment** and rebalancing recommendations
-   **Performance analytics** and health scoring

### 🤖 **LLM Integration** (`llm/`)

-   **DeepSeek AI** for sophisticated market analysis
-   **Investment thesis generation** with reasoning
-   **News impact analysis** and catalyst identification
-   **Confidence-adjusted scoring** and risk assessment

### 📱 **Alerts System** (`alerts/`)

-   **Slack integration** for real-time notifications
-   **Smart filtering** with market hours awareness
-   **Rich formatting** with stock data and upside potential
-   **Rate limiting** and duplicate prevention

## 🔧 Development Patterns

### Import Structure

```python
# Core analysis
from src.core.analyzer import StockAnalyzer

# Portfolio management
from src.portfolio.portfolio_manager import PortfolioManager

# AI integration
from src.llm.deepseek_analyzer import DeepSeekAnalyzer

# Database operations
from src.db.connection import get_db_connection
from src.db.models import Portfolio, PortfolioPosition

# Alerts
from src.alerts.slack_alerts import SlackAlerts
```

### Configuration

```python
# Environment-based configuration
import os
from src.automation.shared.env_validation import getValidatedEnv

# API server configuration
from src.api.main import app

# Database configuration
from src.db.connection import get_db_connection
```

## 🧪 Testing Strategy

### Test Coverage by Module

-   **Core (`core/`)**: 80%+ coverage, 45+ unit tests
-   **Portfolio (`portfolio/`)**: 90%+ coverage, 35+ tests
-   **LLM (`llm/`)**: 88-92% coverage, 25+ tests
-   **Automation (`automation/`)**: Integration test coverage
-   **Alerts (`alerts/`)**: 68 comprehensive tests

### Test Organization

```
tests/
├── unit/                   # Fast unit tests by module
│   ├── test_stock_analyzer.py
│   ├── test_portfolio_*.py
│   └── test_llm_components.py
├── integration/            # Cross-module integration tests
└── conftest.py            # Shared test configuration
```

## 🚀 Usage Examples

### Basic Stock Analysis

```python
from src.core.analyzer import StockAnalyzer

analyzer = StockAnalyzer()
result = analyzer.analyze_stock('NVDA')
print(f"Rating: {result['rating']} | Score: {result['composite_score']:.1f}")
```

### Portfolio Management

```python
from src.portfolio.portfolio_manager import PortfolioManager

pm = PortfolioManager()
portfolio = pm.create_portfolio("My Portfolio", "personal")
pm.add_position(portfolio.id, "AAPL", 100, 150.00)
```

### AI-Enhanced Analysis

```python
from src.llm.deepseek_analyzer import DeepSeekAnalyzer

llm = DeepSeekAnalyzer()
analysis = llm.analyze_stock_with_context("NVDA", market_data)
print(analysis['investment_thesis'])
```

### Slack Alerts

```python
from src.alerts.slack_alerts import SlackAlerts

alerts = SlackAlerts()
alerts.send_buy_signal("AAPL", analysis_result)
```

## 📚 Module Documentation

-   **[Core Analysis](core/README.md)**: Stock analysis engine details
-   **[LLM Integration](llm/README.md)**: AI-powered analysis features
-   **[Portfolio Management](portfolio/README.md)**: Portfolio tracking system
-   **[Alerts System](alerts/README.md)**: Slack notification setup
-   **[Data Layer](data/README.md)**: Data handling and storage
-   **[Automation](automation/README.md)**: Trigger.dev task system

## 🔄 Data Flow

```
Market Data → Core Analyzer → LLM Enhancement → Portfolio Integration → Alerts
     ↓              ↓              ↓                    ↓              ↓
Stock APIs    Fundamental    AI Analysis      Position Tracking   Slack
yfinance      Technical      DeepSeek         Real-time P&L       Notifications
News APIs     Sentiment      Investment       Risk Assessment     Email Alerts
              Risk           Thesis           Rebalancing         Dashboard
```

## 🛠️ Development Guidelines

### Code Organization

-   **Single responsibility** - Each module has a clear purpose
-   **Dependency injection** - Easy testing and configuration
-   **Error handling** - Graceful degradation and clear error messages
-   **Type hints** - Enhanced IDE support and documentation

### Performance Considerations

-   **Caching** - Market data and analysis results
-   **Async operations** - Non-blocking API calls
-   **Database optimization** - Efficient queries and indexing
-   **Rate limiting** - Respectful API usage

### Security Best Practices

-   **Environment variables** - No hardcoded secrets
-   **Input validation** - Sanitize all external data
-   **API authentication** - Secure token-based auth
-   **Database security** - Parameterized queries

---

**💡 Pro Tip**: Start with the `core/` module for stock analysis, then add `portfolio/` management, and finally integrate `automation/` for 24/7 monitoring.
