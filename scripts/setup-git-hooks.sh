#!/bin/bash
# Setup Git hooks for the stock analysis project

set -e

echo "🔧 Setting up Git hooks for stock-analysis project..."

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    uv add --dev pre-commit
fi

# Install the pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
uv run pre-commit install

# Install commit-msg hook for conventional commits
echo "📝 Installing commit-msg hook..."
uv run pre-commit install --hook-type commit-msg

# Create a simple commit-msg hook for conventional commits
cat > .git/hooks/commit-msg << 'EOF'
#!/bin/sh
# Conventional commit format check

commit_regex='^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "❌ Invalid commit message format!"
    echo ""
    echo "Commit message should follow conventional commits format:"
    echo "  type(scope): description"
    echo ""
    echo "Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert"
    echo ""
    echo "Examples:"
    echo "  feat: add LLM integration"
    echo "  fix(analyzer): handle missing data gracefully"
    echo "  test: add comprehensive unit tests"
    echo "  docs: update testing documentation"
    echo ""
    exit 1
fi
EOF

chmod +x .git/hooks/commit-msg

# Create pre-push hook for comprehensive testing
cat > .git/hooks/pre-push << 'EOF'
#!/bin/sh
# Pre-push hook: run comprehensive tests before pushing

echo "🧪 Running comprehensive tests before push..."

# Run all tests except LLM (which require API key)
if ! uv run python run_tests.py --all; then
    echo "❌ Tests failed! Push aborted."
    echo "Fix the failing tests before pushing."
    exit 1
fi

echo "✅ All tests passed! Proceeding with push..."
EOF

chmod +x .git/hooks/pre-push

echo "✅ Git hooks setup complete!"
echo ""
echo "📋 What happens now:"
echo "  • On commit: Code formatting, linting, fast unit tests"
echo "  • On push: All tests (unit + integration)"
echo "  • On GitHub: Full CI/CD pipeline with security checks"
echo ""
echo "🚀 You're ready to commit with confidence!"
