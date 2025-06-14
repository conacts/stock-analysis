# Development Guide

This guide covers the development workflow, testing strategy, and Git practices for the Stock Analysis System.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd stock-analysis
make dev-setup

# Verify everything works
make test-fast
```

## 📋 Development Workflow

### Git Workflow Strategy

We use a **feature branch workflow** with automated testing at each stage:

```
main (production) ← develop (integration) ← feature/your-feature
```

### Testing Strategy by Git Stage

| Git Stage      | Tests Run                      | Purpose              | Speed   |
| -------------- | ------------------------------ | -------------------- | ------- |
| **git add**    | None                           | Stage files          | Instant |
| **git commit** | Fast unit tests + linting      | Catch basic issues   | ~10s    |
| **git push**   | All tests (unit + integration) | Ensure quality       | ~30s    |
| **GitHub PR**  | Full CI/CD pipeline            | Production readiness | ~2min   |

## 🔧 Development Commands

### Using Make (Recommended)

```bash
# Show all available commands
make help

# Development setup
make dev-setup          # Complete setup with Git hooks
make install            # Install dependencies only

# Testing
make test-fast          # Quick feedback (10s)
make test-unit          # All unit tests
make test-integration   # Integration tests
make test-all           # Everything except slow tests
make coverage           # Tests with coverage report

# Code Quality
make lint               # Check code style
make format             # Auto-format code
make security           # Security checks

# Quick development commands
make check              # lint + fast tests
make quick-test         # Alias for test-fast

# Run applications
make run-analyzer       # Master stock analyzer
make run-app           # Main research app
```

### Using Python directly

```bash
# Testing
python run_tests.py --fast
python run_tests.py --integration
python run_tests.py --all --coverage

# Code quality
uv run black src/ tests/
uv run flake8 src/ tests/
uv run bandit -r src/
```

## 🪝 Git Hooks Setup

### Automatic Setup

```bash
make setup-hooks
```

### Manual Setup

```bash
chmod +x scripts/setup-git-hooks.sh
./scripts/setup-git-hooks.sh
```

### What Gets Installed

1. **Pre-commit hooks**:

    - Code formatting (black, isort)
    - Linting (flake8)
    - Security checks (bandit)
    - Fast unit tests
    - File checks (trailing whitespace, etc.)

2. **Commit message validation**:

    - Enforces conventional commit format
    - Examples: `feat: add new feature`, `fix: resolve bug`

3. **Pre-push hooks**:
    - Comprehensive test suite
    - Prevents pushing broken code

## 📝 Commit Message Format

We use **Conventional Commits** for clear, semantic commit messages:

```
type(scope): description

feat: add LLM integration for enhanced analysis
fix(analyzer): handle missing financial data gracefully
test: add comprehensive unit tests for scoring
docs: update API documentation
refactor: simplify technical analysis logic
```

### Types

-   `feat`: New features
-   `fix`: Bug fixes
-   `docs`: Documentation changes
-   `test`: Adding or updating tests
-   `refactor`: Code refactoring
-   `style`: Code style changes
-   `perf`: Performance improvements
-   `chore`: Maintenance tasks
-   `ci`: CI/CD changes

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests** (`tests/unit/`)

    - Fast, isolated tests
    - Mock external dependencies
    - 80%+ coverage target
    - Run on every commit

2. **Integration Tests** (`tests/integration/`)

    - Test component interactions
    - Mock external services
    - Test complete workflows
    - Run on push

3. **LLM Tests** (`tests/unit/test_llm_components.py`)
    - Require API keys
    - Cost money to run
    - Only run in CI on main branch

### Writing Tests

```python
# Unit test example
def test_analyze_fundamentals(mock_yfinance_ticker):
    analyzer = StockAnalyzer(enable_llm=False)
    result = analyzer._analyze_fundamentals(
        mock_yfinance_ticker.info, "TEST"
    )
    assert result['fundamental_score'] >= 0

# Integration test example
@pytest.mark.integration
def test_full_workflow(mock_ticker_class, mock_yfinance_ticker):
    mock_ticker_class.return_value = mock_yfinance_ticker
    analyzer = StockAnalyzer(enable_llm=False)
    result = analyzer.analyze_stock("TEST")
    assert result is not None
```

### Test Markers

```bash
# Run specific test types
pytest -m "unit"                    # Unit tests only
pytest -m "integration"             # Integration tests only
pytest -m "not llm"                 # Everything except LLM tests
pytest -m "unit and not slow"       # Fast unit tests only
```

## 🔍 Code Quality Standards

### Formatting

-   **Black**: Code formatting (88 char line length)
-   **isort**: Import sorting
-   **flake8**: Linting and style checks

### Security

-   **Bandit**: Security vulnerability scanning
-   **Safety**: Dependency vulnerability checking

### Coverage

-   **Target**: 80%+ for core components
-   **Reports**: HTML reports in `htmlcov/`

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

1. **On Pull Request**:

    - Lint checks
    - Security scans
    - Unit tests
    - Integration tests
    - Multiple Python versions (3.11, 3.12, 3.13)

2. **On Push to Main**:
    - All above tests
    - LLM tests (if API key available)
    - Coverage reporting
    - Security artifact uploads

### Local CI Simulation

```bash
# Run the full CI pipeline locally
make ci
```

## 🛠️ Development Environment

### Required Tools

-   **Python 3.11+**
-   **uv** (package manager)
-   **make** (task runner)
-   **git** (version control)

### Optional Tools

-   **pre-commit** (Git hooks)
-   **VS Code** with Python extension
-   **GitHub CLI** for PR management

### Environment Variables

```bash
# Required for LLM tests
export DEEPSEEK_API_KEY="your-api-key"

# Optional for database tests
export DATABASE_URL="postgresql://..."
```

## 📁 Project Structure

```
stock-analysis/
├── src/                    # Source code
│   ├── core/              # Core analysis logic
│   ├── llm/               # LLM integration
│   ├── data/              # Data handling
│   └── db/                # Database operations
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── conftest.py        # Test configuration
├── scripts/               # Development scripts
├── .github/workflows/     # CI/CD configuration
└── docs/                  # Documentation
```

## 🐛 Debugging

### Test Debugging

```bash
# Run specific test with verbose output
pytest tests/unit/test_stock_analyzer.py::TestStockAnalyzer::test_analyze_fundamentals -v -s

# Debug with pdb
pytest --pdb tests/unit/test_stock_analyzer.py

# Run tests with coverage and open report
make coverage && open htmlcov/index.html
```

### Application Debugging

```bash
# Run with debug logging
PYTHONPATH=src python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from core.analyzer import StockAnalyzer
analyzer = StockAnalyzer()
result = analyzer.analyze_stock('AAPL')
print(result)
"
```

## 🚨 Troubleshooting

### Common Issues

1. **Tests failing locally but passing in CI**

    - Check Python version differences
    - Verify environment variables
    - Clear pytest cache: `rm -rf .pytest_cache/`

2. **Pre-commit hooks failing**

    - Update hooks: `pre-commit autoupdate`
    - Run manually: `pre-commit run --all-files`

3. **Import errors in tests**

    - Check PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:./src"`
    - Verify test structure matches source structure

4. **LLM tests failing**
    - Check API key: `echo $DEEPSEEK_API_KEY`
    - Verify account balance
    - Skip LLM tests: `pytest -m "not llm"`

### Getting Help

1. Check the test output for specific error messages
2. Run `make help` for available commands
3. Check the GitHub Actions logs for CI failures
4. Review the test documentation in `tests/README.md`

## 🎯 Best Practices

### Development

-   Write tests first (TDD approach)
-   Keep commits small and focused
-   Use descriptive commit messages
-   Run `make check` before committing

### Testing

-   Mock external dependencies
-   Test both success and failure scenarios
-   Aim for 80%+ coverage on new code
-   Use appropriate test markers

### Code Quality

-   Follow PEP 8 style guidelines
-   Use type hints where helpful
-   Write docstrings for public functions
-   Keep functions small and focused

### Git

-   Create feature branches for new work
-   Rebase before merging to keep history clean
-   Use conventional commit messages
-   Don't commit sensitive data (API keys, etc.)

---

**Happy coding! 🚀**
