# Contributing to Stock Analysis System

Thank you for contributing to our stock analysis system! This guide will help you set up your development environment and ensure your contributions meet our quality standards.

## 🚀 Quick Start

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd stock-analysis
    ```

2. **Install dependencies**

    ```bash
    # Install uv (Python package manager)
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Install Python dependencies
    uv sync --all-extras --dev

    # Install Node.js dependencies (for Trigger.dev)
    npm install
    ```

3. **Set up environment**

    ```bash
    # Copy example environment file
    cp .env.example .env.local

    # Edit .env.local with your API keys
    # Required: ALPHA_VANTAGE_API_KEY, DATABASE_URL
    # Optional: DEEPSEEK_API_KEY, SLACK_BOT_TOKEN, etc.
    ```

## ✅ Before You Push - CRITICAL

**ALWAYS run the full CI pipeline locally before pushing to avoid GitHub Actions failures:**

```bash
# Run the complete CI pipeline locally
make ci
```

This single command runs:

-   Code formatting and linting
-   Security checks
-   All unit tests (161 tests)
-   Integration tests
-   Portfolio CLI functionality tests
-   Database migrations

**If `make ci` passes locally, your push should pass CI. If it fails locally, fix the issues before pushing.**

### Alternative: Manual Testing

If you prefer to run tests step by step:

```bash
# 1. Format and lint code
uv run ruff format src/ tests/
uv run ruff check src/ tests/

# 2. Run security checks
uv run bandit -r src/

# 3. Run all tests
uv run python run_tests.py --unit
uv run python run_tests.py --integration

# 4. Test portfolio CLI
uv run scripts/portfolio_manager.py create "Test Portfolio" personal "Test"
uv run scripts/portfolio_manager.py list

# 5. Run local CI simulation
./scripts/test-ci-locally.sh
```

## 🏗️ Development Workflow

1. **Create a feature branch**

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. **Make your changes**

    - Follow existing code patterns
    - Add tests for new functionality
    - Update documentation as needed

3. **Test thoroughly**

    ```bash
    # CRITICAL: Always run this before pushing
    make ci
    ```

4. **Commit and push**

    ```bash
    git add .
    git commit -m "feat: your descriptive commit message"
    git push origin feature/your-feature-name
    ```

5. **Create a pull request**

## 🧪 Testing Guidelines

### Test Categories

-   **Unit Tests**: Fast, isolated tests (`run_tests.py --unit`)
-   **Integration Tests**: Database and API integration (`run_tests.py --integration`)
-   **LLM Tests**: AI/ML functionality (`run_tests.py --llm`)

### Writing Tests

-   Place unit tests in `tests/unit/`
-   Place integration tests in `tests/integration/`
-   Use descriptive test names
-   Mock external dependencies in unit tests
-   Test both success and failure cases

### Test Environment

Tests use a separate SQLite database (`test.db`) that's automatically created and cleaned up.

## 📁 Project Structure

```
src/
├── api/           # FastAPI web server
├── automation/    # Trigger.dev tasks
├── core/          # Core analysis logic
├── db/            # Database models and migrations
├── portfolio/     # Portfolio management
├── alerts/        # Alert system
└── llm/           # AI/LLM integration

scripts/           # CLI tools and utilities
tests/             # Test suite
.github/workflows/ # CI/CD pipelines
```

## 🔧 Common Development Tasks

### Database Operations

```bash
# Run migrations
uv run python -c "from src.db.migrations import MigrationRunner; MigrationRunner().run_all_migrations()"

# Reset test database
rm -f test.db
```

### Portfolio Management

```bash
# Create portfolio
uv run scripts/portfolio_manager.py create "My Portfolio" personal "Description"

# Add positions
uv run scripts/portfolio_manager.py add 1 AAPL 100 150.00

# View portfolio
uv run scripts/portfolio_manager.py show 1
```

### Trigger.dev Development

```bash
# Start local development server
npm run trigger:dev

# Deploy to staging
npm run trigger:deploy:dev

# Deploy to production
npm run trigger:deploy:prod
```

## 🚨 Common Issues and Solutions

### CI Failures

**Problem**: `Failed to spawn: portfolio_manager.py`
**Solution**: Use `scripts/portfolio_manager.py` instead of `portfolio_manager.py`

**Problem**: Import errors in tests
**Solution**: Ensure you're running tests with `uv run python run_tests.py`

**Problem**: Database connection errors
**Solution**: Check your `DATABASE_URL` in `.env.local`

### Linting Issues

**Problem**: Ruff formatting errors
**Solution**: Run `uv run ruff format src/ tests/` to auto-fix

**Problem**: Security warnings (bandit)
**Solution**: Add `# nosec` comments for false positives, fix real issues

## 📋 Code Quality Standards

### Python Code Style

-   Use `ruff` for formatting and linting
-   Follow PEP 8 conventions
-   Add type hints for function parameters and returns
-   Write docstrings for public functions and classes

### Security

-   Never commit API keys or secrets
-   Use environment variables for configuration
-   Run `bandit` security checks before pushing
-   Validate all user inputs

### Performance

-   Use database indexes for frequently queried columns
-   Cache expensive computations
-   Avoid N+1 query patterns
-   Profile code for bottlenecks

## 🤝 Pull Request Guidelines

### Before Submitting

-   [ ] `make ci` passes locally
-   [ ] All tests pass
-   [ ] Code is properly formatted
-   [ ] Security checks pass
-   [ ] Documentation is updated
-   [ ] Commit messages are descriptive

### PR Description Template

```markdown
## Description

Brief description of changes

## Type of Change

-   [ ] Bug fix
-   [ ] New feature
-   [ ] Breaking change
-   [ ] Documentation update

## Testing

-   [ ] Unit tests added/updated
-   [ ] Integration tests added/updated
-   [ ] Manual testing completed
-   [ ] `make ci` passes locally

## Checklist

-   [ ] Code follows project style guidelines
-   [ ] Self-review completed
-   [ ] Documentation updated
-   [ ] No breaking changes (or properly documented)
```

## 🆘 Getting Help

-   Check existing issues and documentation
-   Run `make ci` to identify specific problems
-   Look at similar code patterns in the codebase
-   Ask questions in pull request discussions

## 🎯 Key Reminders

1. **ALWAYS run `make ci` before pushing**
2. **Test your changes thoroughly**
3. **Follow existing code patterns**
4. **Update documentation when needed**
5. **Keep commits focused and descriptive**

Happy coding! 🚀
