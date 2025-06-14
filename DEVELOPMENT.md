# ��️ Development Guide - AI Trading System

Complete development setup and workflow for the Stock Analysis & AI Trading System with DeepSeek integration.

**Current Status**: ✅ **Production-Ready Development Environment**

-   **AI Trading**: Phase 1 complete with DeepSeek integration
-   **API System**: 100% operational (7/7 endpoints)
-   **Test Coverage**: 169 passing tests
-   **Environment Management**: Seamless local/production workflow

## 🚀 Quick Setup

### **Prerequisites**

-   **Python 3.11+** with [uv](https://docs.astral.sh/uv/) package manager
-   **Node.js 18+** for Trigger.dev automation
-   **Git** with conventional commit support
-   **API Keys**: DeepSeek, Database URL, Alpha Vantage (optional)

### **One-Command Setup**

```bash
git clone https://github.com/your-username/stock-analysis.git
cd stock-analysis
make dev-setup  # Complete development environment setup
```

This command:

-   Installs Python dependencies with `uv`
-   Installs Node.js dependencies
-   Sets up pre-commit hooks
-   Configures the database
-   Runs initial tests to verify setup

### **Environment Configuration**

```bash
# Create environment file (never commit this)
cp .env.example .env.local

# Edit .env.local with your API keys
# Required: DEEPSEEK_API_KEY, DATABASE_URL, API_TOKEN
# Optional: ALPHA_VANTAGE_API_KEY, SLACK_BOT_TOKEN
```

### **Verify Setup**

```bash
# Test with environment loaded
./run_with_env.sh make test-fast

# Start local server
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
# Should show: API Token: True, Database: True, DeepSeek: True

# Test all endpoints
./run_with_env.sh uv run python tools/check_api_environments.py
# Expected: 100% success rate (7/7 endpoints)
```

## 🔧 Development Workflow

### **Daily Commands (with Environment)**

```bash
# Quick development cycle
./run_with_env.sh make check          # Fast lint + test (~10s)
./run_with_env.sh make format         # Auto-format code
./run_with_env.sh make test-fast      # Quick unit tests (169 tests)

# Before committing (automatic via git hooks)
./run_with_env.sh make pre-commit     # Full pre-commit checks

# API development
./run_with_env.sh bash -c "cd src/api && uv run python main.py"  # Start API server
./run_with_env.sh uv run python tools/check_api_environments.py  # Test all endpoints

# AI Trading development
./run_with_env.sh python -c "from src.trading.ai_engine import AITradingEngine; print('Trading engine ready')"
```

### **Testing Strategy**

```bash
# Test categories (all with environment loading)
./run_with_env.sh make test-fast          # Unit tests (~10s) - 169 tests
./run_with_env.sh make test-integration   # Integration tests (~30s)
./run_with_env.sh make test-all          # Complete test suite
./run_with_env.sh make coverage          # Generate coverage report

# AI Trading specific tests
./run_with_env.sh uv run python tools/check_api_environments.py  # API endpoints
./run_with_env.sh python -c "from src.llm.deepseek_analyzer import DeepSeekAnalyzer; print('DeepSeek:', DeepSeekAnalyzer().is_configured())"
```

## 🏗️ Architecture Overview

### **Core Components**

```
src/
├── api/                           # FastAPI server with all endpoints
│   ├── main.py                   # Main API server
│   ├── simple_trading_endpoints.py  # AI trading endpoints (Phase 1)
│   └── trading_endpoints.py      # Advanced trading (Phase 2)
├── trading/                      # AI Trading System (NEW)
│   ├── ai_engine.py             # DeepSeek-powered trading engine
│   ├── market_data.py           # Real-time market data provider
│   ├── risk_manager.py          # Risk assessment and management
│   └── README.md                # Trading system documentation
├── models/
│   └── trading_models.py        # Pydantic models for trading
├── core/analyzer.py             # Main analysis engine
├── portfolio/                   # Portfolio management
├── llm/deepseek_analyzer.py     # AI integration
├── alerts/slack_alerts.py      # Notification system
└── db/                          # Database models

tools/                           # Development and testing tools
├── check_api_environments.py   # Comprehensive API testing
└── ...

run_with_env.sh                 # Environment loader script
.env.local                      # Local environment (never commit)
```

### **Key Technologies**

-   **Python**: Core analysis engine with 169 passing tests
-   **FastAPI**: REST API server with AI trading endpoints
-   **DeepSeek AI**: Advanced portfolio analysis and trading signals
-   **PostgreSQL**: Production database with proper connection handling
-   **Trigger.dev**: Automation platform for scheduled tasks
-   **Railway**: Production deployment platform
-   **Alpha Vantage**: Real-time market data (optional)

## 🧪 Testing Framework

### **Test Structure**

```
tests/
├── unit/                        # Fast unit tests (169 tests)
│   ├── test_stock_analyzer.py
│   ├── test_portfolio_*.py
│   ├── test_llm_components.py
│   └── test_trading_*.py       # AI trading tests
├── integration/                 # Integration tests
│   └── test_analyzer_integration.py
└── conftest.py                 # Test configuration

tools/
└── check_api_environments.py   # Comprehensive API testing
```

### **Coverage Targets**

-   **Core Analyzer**: 80%+ coverage
-   **Portfolio Management**: 90%+ coverage
-   **LLM Components**: 88-92% coverage
-   **AI Trading System**: Comprehensive integration tests
-   **API Endpoints**: 100% operational (7/7 tests passing)
-   **Overall**: 169 tests across unit and integration suites

### **Test Environment Management**

```python
# Tests use environment variables from .env.local
# Always run tests with environment loading
./run_with_env.sh make test-fast

# Test specific components
./run_with_env.sh python -c "
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
analyzer = DeepSeekAnalyzer()
print('DeepSeek configured:', analyzer.is_configured())
"
```

## 🔄 Git Workflow

### **Commit Standards**

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# AI Trading features
git commit -m "feat: add DeepSeek portfolio analysis endpoint"
git commit -m "feat: implement risk management for trading system"

# Bug fixes
git commit -m "fix: resolve environment loading in API server"
git commit -m "fix: correct trading signal confidence calculation"

# Tests
git commit -m "test: add comprehensive AI trading endpoint tests"

# Documentation
git commit -m "docs: update AI trading system documentation"

# Environment improvements
git commit -m "feat: add environment loader script for development"
```

### **Automated Checks**

-   **On Commit**: Fast tests + linting with environment (~10s)
-   **On Push**: Full test suite with environment (~30s)
-   **On PR**: Complete CI/CD pipeline including API tests

### **Branch Strategy**

```bash
# AI Trading feature development
git checkout -b feat/paper-trading-system
./run_with_env.sh make ci  # Test before committing
git commit -m "feat: implement paper trading infrastructure"
git push origin feat/paper-trading-system

# Bug fixes
git checkout -b fix/deepseek-api-timeout
./run_with_env.sh make test-fast
git commit -m "fix: add timeout handling for DeepSeek API calls"
```

## 🚀 API Development

### **FastAPI Server with AI Trading**

```bash
# Start development server with environment
./run_with_env.sh bash -c "cd src/api && uv run python main.py"

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Interactive API docs

# Test AI trading endpoints
curl -H "Authorization: Bearer default-dev-token" \
  http://localhost:8000/trading/trading-config

# Comprehensive endpoint testing
./run_with_env.sh uv run python tools/check_api_environments.py
```

### **API Structure**

```python
# src/api/main.py - Main API server
@app.get("/health")
async def health_check():
    return {"status": "healthy", "deepseek": "configured"}

# src/api/simple_trading_endpoints.py - AI Trading endpoints
@app.get("/trading/trading-config")
async def get_trading_config():
    return {"max_position_size": 0.10, "max_daily_loss": 0.02}

@app.get("/trading/risk-status/{portfolio_id}")
async def get_risk_status(portfolio_id: int):
    # AI-powered risk assessment
    return risk_manager.get_risk_status(portfolio_id)
```

## 🤖 AI Trading Development

### **DeepSeek Integration**

```bash
# Test DeepSeek configuration
./run_with_env.sh python -c "
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
analyzer = DeepSeekAnalyzer()
print('Configured:', analyzer.is_configured())
print('API key valid:', len(analyzer.api_key) > 10 if analyzer.api_key else False)
"

# Test AI trading engine
./run_with_env.sh python -c "
from src.trading.ai_engine import AITradingEngine
engine = AITradingEngine()
print('Trading engine initialized')
"
```

### **Trading System Development Pattern**

```python
# src/trading/ai_engine.py - AI Trading Engine
class AITradingEngine:
    def __init__(self):
        self.deepseek = DeepSeekAnalyzer()
        self.risk_manager = RiskManager()
        self.market_data = MarketDataProvider()

    async def analyze_portfolio(self, portfolio_id: int) -> TradingAnalysis:
        # AI-powered portfolio analysis
        pass
```

### **Risk Management**

```python
# src/trading/risk_manager.py - Risk Management
class RiskManager:
    MAX_POSITION_SIZE = 0.10  # 10% of portfolio
    MAX_DAILY_LOSS = 0.02     # 2% daily loss limit

    def assess_portfolio_risk(self, portfolio_id: int) -> RiskAssessment:
        # Comprehensive risk assessment
        pass
```

## 🤖 Automation Development

### **Trigger.dev Tasks**

```bash
# Local development
npx trigger.dev@latest dev

# Deploy to production
bunx trigger.dev@latest deploy

# Monitor tasks
# Visit: https://cloud.trigger.dev/
```

### **Task Development Pattern**

```typescript
// Portfolio analysis task with AI integration
export const portfolioAnalysisTask = task({
    id: "portfolio-analysis",
    run: async (payload) => {
        const response = await fetch(
            `${env.PYTHON_API_URL}/portfolio/analyze-with-llm`,
            {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${env.API_TOKEN}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            }
        );
        return response.json();
    },
});
```

## 🔧 Environment Configuration

### **Development Environment (.env.local)**

```bash
# Required for AI features
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Required for database
DATABASE_URL=postgresql://user:pass@host:port/database

# Required for API authentication
API_TOKEN=default-dev-token

# Required for Trigger.dev
PYTHON_API_URL=http://localhost:8000
TRIGGER_SECRET_KEY=tr_dev_your-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-token

# Optional for enhanced features
ALPHA_VANTAGE_API_KEY=your-alpha-key
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#dev-alerts

# Environment identifier
ENVIRONMENT=development
```

### **Production Environment (Railway Dashboard)**

Set these in your Railway project dashboard:

-   `DEEPSEEK_API_KEY` - AI analysis features
-   `DATABASE_URL` - Auto-generated by Railway
-   `API_TOKEN` - Secure authentication token
-   `PYTHON_API_URL` - Production API URL
-   `TRIGGER_SECRET_KEY` - Trigger.dev production secret
-   `TRIGGER_ACCESS_TOKEN` - Trigger.dev access token
-   `ENVIRONMENT` - Set to "production"

## 🐛 Debugging & Troubleshooting

### **Common Issues**

**Environment Variables Not Loading:**

```bash
# Check if .env.local exists
ls -la .env.local

# Test environment loading
./run_with_env.sh env | grep -E "(DEEPSEEK|DATABASE|API_TOKEN)"

# Verify script permissions
chmod +x run_with_env.sh
```

**API Connection Issues:**

```bash
# Test local API server
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
# Should show all services configured: True

# Test all endpoints
./run_with_env.sh uv run python tools/check_api_environments.py

# Check specific endpoint
curl -H "Authorization: Bearer default-dev-token" \
  http://localhost:8000/trading/trading-config
```

**DeepSeek API Issues:**

```bash
# Test DeepSeek configuration
./run_with_env.sh python -c "
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
analyzer = DeepSeekAnalyzer()
print('Configured:', analyzer.is_configured())
print('API key valid:', len(analyzer.api_key) > 10 if analyzer.api_key else False)
"
```

**Database Connection Issues:**

```bash
# Test database connection
./run_with_env.sh python -c "
from src.db.connection import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connected')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

### **Performance Optimization**

```bash
# Profile test performance
./run_with_env.sh make test-fast --profile

# Check API response times
./run_with_env.sh uv run python tools/check_api_environments.py

# Monitor DeepSeek API usage
./run_with_env.sh python -c "
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
analyzer = DeepSeekAnalyzer()
# Check API usage and rate limits
"
```

## 📦 Dependency Management

### **Python Dependencies**

```bash
# Add new dependency
uv add package-name

# Add AI/ML dependency
uv add openai  # For AI integrations

# Update dependencies
uv sync

# Check for security issues
uv audit
```

### **Node.js Dependencies**

```bash
# Add automation dependency
bun add package-name

# Update dependencies
bun update

# Check bundle size
bun analyze
```

## 🚀 Deployment

### **Local Testing**

```bash
# Test complete system locally
./run_with_env.sh bash -c "cd src/api && uv run python main.py" &  # Start API server
./run_with_env.sh make test-all           # Run all tests
npx trigger.dev@latest dev                # Test automation
./run_with_env.sh uv run python tools/check_api_environments.py  # Test endpoints
```

### **Production Deployment**

```bash
# Deploy to Railway (automatic on push to main)
git push origin main

# Deploy automation tasks
bunx trigger.dev@latest deploy

# Verify deployment
curl https://stock-analysis-production-31e9.up.railway.app/health
./run_with_env.sh bash -c "API_BASE_URL=https://stock-analysis-production-31e9.up.railway.app uv run python tools/check_api_environments.py"
```

## 📚 Additional Resources

-   **[README.md](README.md)**: System overview and quick start
-   **[AI_TRADING_PLAN.md](AI_TRADING_PLAN.md)**: AI trading system roadmap
-   **[API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)**: Comprehensive API testing
-   **[CONFIGURATION.md](CONFIGURATION.md)**: Environment setup guide
-   **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment guide
-   **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines

---

**💡 Pro Tips:**

-   **Always use `./run_with_env.sh`** for commands that need environment variables
-   Use `./run_with_env.sh make check` for quick feedback during development
-   Test AI trading features with `./run_with_env.sh uv run python tools/check_api_environments.py`
-   Monitor the comprehensive test suite (169 tests) for regression detection
-   Use the Railway dashboard for production monitoring and logs
-   Set up your IDE with Python and TypeScript language servers
-   The system is designed to work seamlessly in both local and production environments

**🚀 Ready to contribute to the AI trading system?** Check out [AI_TRADING_PLAN.md](AI_TRADING_PLAN.md) for Phase 2 development opportunities!
