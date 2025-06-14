# Stock Analysis System - Development Makefile

.PHONY: help install test test-fast test-integration test-llm test-all coverage lint format security clean setup-hooks

help: ## Show this help message
	@echo "Stock Analysis System - Development Commands"
	@echo "============================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	uv sync --all-extras --dev

setup-hooks: ## Set up Git hooks for development
	chmod +x scripts/setup-git-hooks.sh
	./scripts/setup-git-hooks.sh

test-fast: ## Run fast unit tests only
	uv run python run_tests.py --fast

test-unit: ## Run all unit tests
	uv run python run_tests.py --unit

test-integration: ## Run integration tests
	uv run python run_tests.py --integration

test-llm: ## Run LLM tests (requires API key)
	uv run python run_tests.py --llm

test-all: ## Run all tests except slow ones
	uv run python run_tests.py --all

test: test-all ## Alias for test-all

coverage: ## Run tests with coverage report
	uv run python run_tests.py --coverage
	@echo "📊 Coverage report: htmlcov/index.html"

lint: ## Run linting checks
	uv run flake8 src/ tests/ --max-line-length=320 --ignore=E203,W503,E402,E501,E226
	uv run black --check src/ tests/ --line-length=320
	uv run isort --check-only src/ tests/ --line-length=320

format: ## Format code with black and isort
	uv run black src/ tests/ --line-length=320
	uv run isort src/ tests/ --line-length=320

security: ## Run security checks
	uv run bandit -r src/
	uv run safety check

clean: ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-analyzer: ## Run the master stock analyzer
	uv run master_stock_analyzer.py

run-app: ## Run the main research app
	uv run main_app.py

# Development workflow commands
dev-setup: install setup-hooks ## Complete development setup
	@echo "🎉 Development environment ready!"
	@echo "Run 'make test-fast' to verify everything works"

pre-commit: lint test-fast ## Run pre-commit checks manually
	@echo "✅ Pre-commit checks passed!"

pre-push: test-all ## Run pre-push checks manually
	@echo "✅ Pre-push checks passed!"

ci: lint security test-all ## Run full CI pipeline locally
	@echo "✅ CI pipeline completed successfully!"

# Quick commands for daily development
quick-test: test-fast ## Quick test for development feedback

check: lint test-fast ## Quick check (lint + fast tests)

all: clean install setup-hooks test-all ## Full setup and test
