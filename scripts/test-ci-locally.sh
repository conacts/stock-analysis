#!/bin/bash
# Test CI pipeline locally
# This script simulates what happens in GitHub Actions

set -e

echo "🚀 Testing CI pipeline locally..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Create test environment
echo "📝 Setting up test environment..."
export DATABASE_URL="sqlite:///test.db"
export ALPHA_VANTAGE_API_KEY="test_key"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/test"
export SLACK_USER_ID="test_user"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --all-extras --dev

# Run database migrations
echo "🗄️ Running database migrations..."
uv run python -c "
from src.db.migrations import MigrationRunner
runner = MigrationRunner()
runner.run_all_migrations()
"

# Lint and format check
echo "🔍 Running linting and formatting checks..."
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Security check
echo "🔒 Running security checks..."
uv run bandit -r src/ -f json

# Run tests
echo "🧪 Running fast unit tests..."
uv run python run_tests.py --fast

echo "🧪 Running all unit tests..."
uv run python run_tests.py --unit

echo "🧪 Running integration tests..."
uv run python run_tests.py --integration

# Test portfolio CLI
echo "💼 Testing portfolio CLI functionality..."
uv run portfolio_manager.py create "Test Portfolio" personal "CI test portfolio"
uv run portfolio_manager.py list
uv run portfolio_manager.py add 1 AAPL 100 150.00
uv run portfolio_manager.py show 1

# Clean up test database
rm -f test.db

echo "✅ All CI checks passed locally!"
echo "🎉 Ready to push to GitHub!"
