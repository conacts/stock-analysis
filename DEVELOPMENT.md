# 🛠️ Development Guide

Complete development setup and workflow for the Stock Analysis System.

## 🚀 Quick Setup

### Prerequisites

-   **Python 3.11+** with [uv](https://docs.astral.sh/uv/) package manager
-   **Node.js 18+** with Bun (for Trigger.dev automation)
-   **Git** with conventional commit support

### One-Command Setup

```bash
git clone https://github.com/your-username/stock-analysis.git
cd stock-analysis
make dev-setup  # Complete development environment setup
```

This command:

-   Installs Python dependencies with `uv`
-   Installs Node.js dependencies with `bun`
-   Sets up pre-commit hooks
-   Configures the database
-   Runs initial tests to verify setup

## 🔧 Development Workflow

### Daily Commands

```bash
# Quick development cycle
make check          # Fast lint + test (~10s)
make format         # Auto-format code
make test-fast      # Quick unit tests (157 tests)

# Before committing (automatic via git hooks)
make pre-commit     # Full pre-commit checks

# API development
make run-api        # Start FastAPI server on :8000
make run-analyzer   # Interactive stock analyzer

# Automation development
bunx trigger.dev@latest dev     # Start Trigger.dev development server
bunx trigger.dev@latest deploy  # Deploy automation tasks
```

### Testing Strategy

```bash
# Test categories
make test-fast          # Unit tests (~10s) - 157 tests
make test-integration   # Integration tests (~30s)
make test-llm          # LLM tests (requires DEEPSEEK_API_KEY)
make test-all          # Complete test suite
make coverage          # Generate coverage report (88%+)

# Specific test areas
make test-portfolio    # Portfolio management tests
make test-alerts       # Slack alerts tests
make test-automation   # Trigger.dev automation tests
```

## 🏗️ Architecture Overview

### Core Components

```
src/
├── api/main.py              # FastAPI server (NEW)
├── automation/              # Trigger.dev tasks (18 tasks)
├── core/analyzer.py         # Main analysis engine
├── portfolio/               # Portfolio management
├── llm/deepseek_analyzer.py # AI integration
├── alerts/slack_alerts.py  # Notification system
└── db/                      # Database models
```

### Key Technologies

-   **Python**: Core analysis engine with 157 passing tests
-   **FastAPI**: REST API server for automation integration
-   **Trigger.dev**: Automation platform (18 tasks deployed)
-   **PostgreSQL**: Production database with Prisma ORM
-   **DeepSeek LLM**: AI-powered analysis
-   **Slack API**: Real-time notifications

## 🧪 Testing Framework

### Test Structure

```
tests/
├── unit/                    # Fast unit tests (157 tests)
│   ├── test_stock_analyzer.py
│   ├── test_portfolio_*.py
│   └── test_llm_components.py
├── integration/             # Integration tests
│   └── test_analyzer_integration.py
└── conftest.py             # Test configuration
```

### Coverage Targets

-   **Core Analyzer**: 80%+ coverage
-   **Portfolio Management**: 90%+ coverage
-   **LLM Components**: 88-92% coverage
-   **Automation Tasks**: Integration test coverage
-   **Overall**: 88%+ coverage maintained

### Test Data Management

```python
# Use fixtures for consistent test data
@pytest.fixture
def sample_portfolio():
    return create_test_portfolio()

# Mock external APIs in tests
@pytest.fixture
def mock_yfinance():
    with patch('yfinance.Ticker') as mock:
        yield mock
```

## 🔄 Git Workflow

### Commit Standards

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Feature additions
git commit -m "feat: add automated price alerts"

# Bug fixes
git commit -m "fix: resolve portfolio calculation error"

# Tests
git commit -m "test: add comprehensive LLM integration tests"

# Documentation
git commit -m "docs: update automation setup guide"

# Refactoring
git commit -m "refactor: improve error handling in analyzer"
```

### Automated Checks

-   **On Commit**: Fast tests + linting (~10s)
-   **On Push**: Full test suite (~30s)
-   **On PR**: Complete CI/CD pipeline

### Branch Strategy

```bash
# Feature development
git checkout -b feat/automated-alerts
git commit -m "feat: implement price alert system"
git push origin feat/automated-alerts

# Bug fixes
git checkout -b fix/portfolio-calculation
git commit -m "fix: correct P&L calculation logic"
```

## 🚀 API Development

### FastAPI Server

```bash
# Start development server
make run-api

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Interactive API docs
curl http://localhost:8000/analyze/AAPL
```

### API Structure

```python
# src/api/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    analyzer = StockAnalyzer()
    return analyzer.analyze_stock(symbol)
```

## 🤖 Automation Development

### Trigger.dev Tasks

```bash
# Local development
export API_TOKEN="mock-api-token-12345"
export PYTHON_API_URL="http://localhost:8000"
bunx trigger.dev@latest dev

# Deploy to production
bunx trigger.dev@latest deploy

# Monitor tasks
# Visit: https://cloud.trigger.dev/
```

### Task Development Pattern

```typescript
// src/automation/tasks/example-task.ts
import {task} from "@trigger.dev/sdk/v3";
import {getValidatedEnv} from "../shared/env-validation";

export const exampleTask = task({
    id: "example-task",
    run: async (payload) => {
        const env = getValidatedEnv();
        // Task implementation
    },
});
```

## 🔧 Environment Configuration

### Development Environment

```bash
# .env (for local development)
DEEPSEEK_API_KEY=your-deepseek-key
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_USER_ID=@your-username
DATABASE_URL=sqlite:///data/stock_analysis.db

# Mock values for testing
API_TOKEN=mock-api-token-12345
PYTHON_API_URL=http://localhost:8000
```

### Production Environment

Set these in your Trigger.dev dashboard:

-   `PYTHON_API_URL` - Production API server URL
-   `API_TOKEN` - Secure authentication token
-   `DEEPSEEK_API_KEY` - AI analysis features
-   `DATABASE_URL` - Production database connection

## 🐛 Debugging & Troubleshooting

### Common Issues

**Tests Failing:**

```bash
# Check specific test category
make test-fast --verbose
make test-integration --verbose

# Check coverage
make coverage
```

**API Connection Issues:**

```bash
# Verify API server is running
curl http://localhost:8000/health

# Check logs
tail -f logs/api.log
```

**Automation Task Failures:**

```bash
# Check Trigger.dev logs in dashboard
# Verify environment variables are set
# Test with mock values locally
```

### Performance Optimization

```bash
# Profile test performance
make test-fast --profile

# Check database query performance
make db-analyze

# Monitor API response times
make api-benchmark
```

## 📦 Dependency Management

### Python Dependencies

```bash
# Add new dependency
uv add package-name

# Update dependencies
uv sync

# Check for security issues
uv audit
```

### Node.js Dependencies

```bash
# Add automation dependency
bun add package-name

# Update dependencies
bun update

# Check bundle size
bun analyze
```

## 🚀 Deployment

### Local Testing

```bash
# Test complete system locally
make run-api &          # Start API server
make test-all           # Run all tests
bunx trigger.dev@latest dev  # Test automation
```

### Production Deployment

```bash
# Deploy API server (your choice of platform)
# Deploy automation tasks
bunx trigger.dev@latest deploy

# Verify deployment
make test-production
```

## 📚 Additional Resources

-   **[Main README](README.md)**: System overview and quick start
-   **[Automation Guide](src/automation/README.md)**: Trigger.dev setup and tasks
-   **[Testing Guide](tests/README.md)**: Testing framework details
-   **[Configuration Guide](CONFIGURATION.md)**: Environment setup

---

**💡 Pro Tips:**

-   Use `make check` for quick feedback during development
-   Set up your IDE with Python and TypeScript language servers
-   Use the Trigger.dev dashboard for monitoring automation tasks
-   Run `make pre-commit` before pushing to catch issues early
