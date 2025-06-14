# Contributing to Stock Analysis & AI Trading System

Thank you for contributing to our AI-powered stock analysis and trading system! This guide will help you set up your development environment and ensure your contributions meet our quality standards.

**Current Status**: ✅ **Production System with AI Trading**

-   **Production**: https://stock-analysis-production-31e9.up.railway.app
-   **AI Integration**: DeepSeek API fully operational
-   **Test Coverage**: 169 passing tests
-   **API Status**: 100% operational (7/7 endpoints)

## 🚀 Quick Start

### **1. Clone and Setup**

```bash
git clone <repository-url>
cd stock-analysis

# Install dependencies
make dev-setup
```

### **2. Environment Configuration**

```bash
# Create environment file (never commit this)
cp .env.example .env.local

# Edit .env.local with your API keys
# Required: DEEPSEEK_API_KEY, DATABASE_URL, API_TOKEN
# Optional: ALPHA_VANTAGE_API_KEY, SLACK_BOT_TOKEN
```

### **3. Verify Setup**

```bash
# Test with environment loaded
./run_with_env.sh make test-fast

# Start local server
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
# Should show: API Token: True, Database: True, DeepSeek: True

# Test all endpoints
./run_with_env.sh bash -c "API_BASE_URL=http://localhost:8000 uv run python tools/check_api_environments.py"
# Expected: 100% success rate (7/7 endpoints)
```

## ✅ Before You Push - CRITICAL

**ALWAYS use environment loading and run the full CI pipeline locally:**

```bash
# Run the complete CI pipeline with environment
./run_with_env.sh make ci
```

This command runs:

-   Code formatting and linting
-   Security checks
-   All unit tests (169 tests)
-   Integration tests
-   AI trading system tests
-   Database connectivity tests

**If `./run_with_env.sh make ci` passes locally, your push should pass CI.**

### **Environment-Aware Testing**

```bash
# Format and lint with environment
./run_with_env.sh uv run ruff format src/ tests/
./run_with_env.sh uv run ruff check src/ tests/

# Run security checks
./run_with_env.sh uv run bandit -r src/

# Run all tests with environment
./run_with_env.sh uv run python run_tests.py --unit
./run_with_env.sh uv run python run_tests.py --integration

# Test AI trading endpoints
./run_with_env.sh uv run python tools/check_api_environments.py
```

## 🏗️ Development Workflow

### **1. Create Feature Branch**

```bash
git checkout -b feature/your-feature-name
```

### **2. Make Changes with Environment**

-   **Always use `./run_with_env.sh`** for commands that need environment variables
-   Follow existing code patterns
-   Add tests for new functionality
-   Update documentation as needed

### **3. Test Thoroughly**

```bash
# CRITICAL: Always run this before pushing
./run_with_env.sh make ci

# Test specific components
./run_with_env.sh bash -c "cd src/api && uv run python main.py"  # API server
./run_with_env.sh uv run python tools/check_api_environments.py   # All endpoints
```

### **4. Commit and Push**

```bash
git add .
git commit -m "feat: your descriptive commit message"
git push origin feature/your-feature-name
```

### **5. Create Pull Request**

Use the PR template below and ensure all checks pass.

## 🧪 Testing Guidelines

### **Test Categories**

-   **Unit Tests**: Fast, isolated tests (`./run_with_env.sh uv run python run_tests.py --unit`)
-   **Integration Tests**: Database and API integration (`./run_with_env.sh uv run python run_tests.py --integration`)
-   **AI Trading Tests**: Trading system functionality (`./run_with_env.sh uv run python tools/check_api_environments.py`)
-   **LLM Tests**: DeepSeek AI functionality (requires API key)

### **Writing Tests**

-   Place unit tests in `tests/unit/`
-   Place integration tests in `tests/integration/`
-   Use descriptive test names
-   Mock external dependencies in unit tests
-   Test both success and failure cases
-   **Always use environment loading** for tests that need API keys

### **Test Environment**

```bash
# Tests use environment variables from .env.local
# Database: Uses configured DATABASE_URL
# AI: Uses DEEPSEEK_API_KEY if available
# API: Uses API_TOKEN for authentication
```

## 📁 Project Structure

```
src/
├── api/                    # FastAPI web server with all endpoints
│   ├── main.py            # Main API server
│   ├── simple_trading_endpoints.py  # AI trading endpoints
│   └── trading_endpoints.py         # Advanced trading (Phase 2)
├── trading/               # AI Trading System (NEW)
│   ├── ai_engine.py      # DeepSeek-powered trading engine
│   ├── market_data.py    # Real-time market data provider
│   ├── risk_manager.py   # Risk assessment and management
│   └── README.md         # Trading system documentation
├── models/
│   └── trading_models.py # Pydantic models for trading
├── core/                 # Core analysis logic
├── db/                   # Database models and migrations
├── portfolio/            # Portfolio management
├── llm/                  # AI/LLM integration (DeepSeek)
└── alerts/               # Alert system

tools/                    # Development and testing tools
├── check_api_environments.py  # Comprehensive API testing
└── ...

tests/                    # Test suite (169 tests)
run_with_env.sh          # Environment loader script
.env.local               # Local environment (never commit)
```

## 🔧 Common Development Tasks

### **API Development**

```bash
# Start local API server with environment
./run_with_env.sh bash -c "cd src/api && uv run python main.py"

# Test all endpoints
./run_with_env.sh uv run python tools/check_api_environments.py

# Test specific endpoint
curl -H "Authorization: Bearer default-dev-token" \
  http://localhost:8000/trading/trading-config
```

### **AI Trading Development**

```bash
# Test DeepSeek integration
./run_with_env.sh python -c "
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
analyzer = DeepSeekAnalyzer()
print('DeepSeek configured:', analyzer.is_configured())
"

# Test trading engine
./run_with_env.sh python -c "
from src.trading.ai_engine import AITradingEngine
engine = AITradingEngine()
print('Trading engine ready')
"
```

### **Database Operations**

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

### **Portfolio Management**

```bash
# Create portfolio with environment
./run_with_env.sh uv run scripts/portfolio_manager.py create "My Portfolio" personal "Description"

# Add positions
./run_with_env.sh uv run scripts/portfolio_manager.py add 1 AAPL 100 150.00

# View portfolio
./run_with_env.sh uv run scripts/portfolio_manager.py show 1
```

### **Trigger.dev Development**

```bash
# Start local development server
npx trigger.dev@latest dev

# Deploy to production
bunx trigger.dev@latest deploy
```

## 🚨 Common Issues and Solutions

### **Environment Issues**

**Problem**: Environment variables not loading
**Solution**: Always use `./run_with_env.sh` and ensure `.env.local` exists

**Problem**: DeepSeek API not configured
**Solution**: Add `DEEPSEEK_API_KEY=sk-your-key` to `.env.local`

**Problem**: Database connection failed
**Solution**: Check `DATABASE_URL` in `.env.local` and ensure database is accessible

### **API Issues**

**Problem**: API server shows "DeepSeek API configured: False"
**Solution**: Start with `./run_with_env.sh bash -c "cd src/api && uv run python main.py"`

**Problem**: Trading endpoints return 404
**Solution**: Ensure you're using the correct import paths and environment loading

### **Testing Issues**

**Problem**: Tests fail with missing environment variables
**Solution**: Run tests with `./run_with_env.sh make test-fast`

**Problem**: API endpoint tests fail
**Solution**: Use `./run_with_env.sh uv run python tools/check_api_environments.py`

### **Linting Issues**

**Problem**: Ruff formatting errors
**Solution**: Run `./run_with_env.sh uv run ruff format src/ tests/`

**Problem**: Security warnings (bandit)
**Solution**: Add `# nosec` comments for false positives, fix real issues

## 📋 Code Quality Standards

### **Python Code Style**

-   Use `ruff` for formatting and linting
-   Follow PEP 8 conventions
-   Add type hints for function parameters and returns
-   Write docstrings for public functions and classes
-   Use Pydantic models for data validation

### **AI Trading Code**

-   Follow existing patterns in `src/trading/`
-   Use proper error handling for API calls
-   Implement comprehensive logging
-   Add risk management checks
-   Test with both mock and real data

### **Security**

-   **Never commit** API keys or secrets to version control
-   Use `.env.local` for local development (in .gitignore)
-   Use Railway dashboard for production secrets
-   Run `bandit` security checks before pushing
-   Validate all user inputs

### **Performance**

-   Use database indexes for frequently queried columns
-   Cache expensive computations (especially AI calls)
-   Implement proper timeout handling (30-second limits)
-   Profile code for bottlenecks

## 🤝 Pull Request Guidelines

### **Before Submitting**

-   [ ] `./run_with_env.sh make ci` passes locally
-   [ ] All tests pass with environment loading
-   [ ] API endpoints tested with comprehensive tool
-   [ ] Code is properly formatted
-   [ ] Security checks pass
-   [ ] Documentation is updated
-   [ ] Commit messages are descriptive

### **PR Description Template**

```markdown
## Description

Brief description of changes

## Type of Change

-   [ ] Bug fix
-   [ ] New feature (AI trading, API endpoint, etc.)
-   [ ] Breaking change
-   [ ] Documentation update
-   [ ] AI/ML improvement

## Testing

-   [ ] Unit tests added/updated
-   [ ] Integration tests added/updated
-   [ ] API endpoint tests pass (7/7)
-   [ ] AI trading functionality tested
-   [ ] Manual testing completed
-   [ ] `./run_with_env.sh make ci` passes locally

## AI Trading Impact

-   [ ] No impact on trading system
-   [ ] Enhances existing trading features
-   [ ] Adds new trading capabilities
-   [ ] Requires configuration changes

## Checklist

-   [ ] Code follows project style guidelines
-   [ ] Environment loading used where needed
-   [ ] Self-review completed
-   [ ] Documentation updated
-   [ ] No breaking changes (or properly documented)
-   [ ] API endpoints tested and working
```

## 🆘 Getting Help

-   **Environment Issues**: Check [CONFIGURATION.md](CONFIGURATION.md)
-   **API Testing**: Use `./run_with_env.sh uv run python tools/check_api_environments.py`
-   **AI Trading**: See [AI_TRADING_PLAN.md](AI_TRADING_PLAN.md)
-   **Deployment**: Check [DEPLOYMENT.md](DEPLOYMENT.md)
-   **General Setup**: See [README.md](README.md)

## 🎯 Key Reminders

1. **ALWAYS use `./run_with_env.sh`** for commands that need environment variables
2. **Test your changes thoroughly** with the comprehensive testing tool
3. **Follow existing code patterns** especially in AI trading components
4. **Update documentation** when adding new features
5. **Keep commits focused and descriptive**
6. **Never commit `.env.local`** or any secrets
7. **Test both local and production scenarios**

## 🚀 Contributing to AI Trading Features

### **Phase 1 (Complete)**: AI Analysis Engine

-   ✅ DeepSeek integration working
-   ✅ Trading signal generation
-   ✅ Risk assessment
-   ✅ Market data integration

### **Phase 2 (In Progress)**: Trade Execution System

-   📋 Paper trading infrastructure
-   📋 Trade validation workflows
-   📋 Advanced risk management
-   📋 Performance tracking

### **How to Contribute**

1. **Check the [AI_TRADING_PLAN.md](AI_TRADING_PLAN.md)** for current status
2. **Pick a Phase 2 task** that interests you
3. **Follow the development workflow** with environment loading
4. **Test thoroughly** with the comprehensive testing tool
5. **Submit PR** with proper documentation

Happy coding! 🚀

---

**💡 Pro Tip**: The system is designed to work seamlessly with proper environment management. Always use `./run_with_env.sh` and you'll have access to all the AI trading features and database connectivity.
