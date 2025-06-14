# Testing Framework Documentation

This document describes the comprehensive testing framework for the Stock Analysis System.

## Overview

Our testing framework uses **pytest** with a structured approach that includes:

-   **Unit Tests**: Fast, isolated tests for individual components
-   **Integration Tests**: Tests for component interactions with mocked external services
-   **LLM Tests**: Tests requiring actual LLM API calls (marked and skippable)
-   **Coverage Reporting**: Code coverage analysis with HTML reports

## Test Structure

```
tests/
├── __init__.py                 # Tests package
├── conftest.py                 # Pytest configuration and fixtures
├── unit/                       # Unit tests
│   ├── test_stock_analyzer.py  # Core analyzer tests
│   └── test_llm_components.py  # LLM component tests
├── integration/                # Integration tests
│   └── test_analyzer_integration.py
└── README.md                   # This file
```

## Running Tests

### Quick Start

```bash
# Run all unit tests (default)
python run_tests.py

# Run with coverage report
python run_tests.py --coverage

# Run integration tests
python run_tests.py --integration

# Run all tests
python run_tests.py --all
```

### Test Categories

#### Unit Tests (Default)

```bash
python run_tests.py --unit
# or just
python run_tests.py
```

-   Fast execution (< 30 seconds)
-   No external dependencies
-   Comprehensive mocking
-   70%+ code coverage target

#### Integration Tests

```bash
python run_tests.py --integration
```

-   Test component interactions
-   Mock external services (yfinance, APIs)
-   Verify complete workflows
-   Test error handling and edge cases

#### LLM Tests

```bash
python run_tests.py --llm
```

-   **Requires**: `DEEPSEEK_API_KEY` environment variable
-   **Warning**: These tests make actual API calls and may cost money
-   Tests real LLM integration
-   Skipped by default

#### Fast Tests Only

```bash
python run_tests.py --fast
```

-   Only the fastest unit tests
-   For quick development feedback
-   Excludes slower integration scenarios

### Advanced Options

```bash
# Verbose output
python run_tests.py --verbose

# Parallel execution
python run_tests.py --parallel 4

# Coverage with HTML report
python run_tests.py --coverage
# Report available at: htmlcov/index.html
```

## Test Markers

Tests are categorized using pytest markers:

-   `@pytest.mark.unit`: Unit tests (default)
-   `@pytest.mark.integration`: Integration tests
-   `@pytest.mark.llm`: Tests requiring LLM API
-   `@pytest.mark.slow`: Slow-running tests
-   `@pytest.mark.database`: Tests requiring database

### Running Specific Markers

```bash
# Run only unit tests
pytest -m "unit"

# Run integration but not slow tests
pytest -m "integration and not slow"

# Run everything except LLM tests
pytest -m "not llm"
```

## Fixtures

### Core Fixtures (conftest.py)

#### Mock Data Fixtures

-   `mock_yfinance_ticker`: Complete mock yfinance Ticker object
-   `sample_financial_data`: Sample financial metrics
-   `sample_news_data`: Sample news articles
-   `sample_technical_data`: Sample technical indicators
-   `sample_market_context`: Sample market conditions

#### Mock Component Fixtures

-   `mock_deepseek_response`: Mock LLM API response
-   `mock_llm_scorer`: Mock LLM scorer with pre-configured responses
-   `mock_database`: Mock database operations

### Using Fixtures

```python
def test_my_function(mock_yfinance_ticker, sample_financial_data):
    # Fixtures are automatically injected
    analyzer = StockAnalyzer()
    result = analyzer.analyze_fundamentals(
        mock_yfinance_ticker.info,
        "TEST"
    )
    assert result is not None
```

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from core.analyzer import StockAnalyzer

class TestStockAnalyzer:
    def test_analyze_fundamentals(self, mock_yfinance_ticker):
        """Test fundamental analysis with mocked data"""
        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer._analyze_fundamentals(
            mock_yfinance_ticker.info,
            "TEST"
        )

        assert result['company_name'] == 'Test Company Inc.'
        assert 0 <= result['fundamental_score'] <= 100

    @patch('yfinance.Ticker')
    def test_analyze_stock_success(self, mock_ticker_class, mock_yfinance_ticker):
        """Test complete stock analysis"""
        mock_ticker_class.return_value = mock_yfinance_ticker

        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer.analyze_stock("TEST")

        assert result is not None
        assert result['symbol'] == 'TEST'
```

### Integration Test Example

```python
@pytest.mark.integration
class TestStockAnalyzerIntegration:
    @patch('yfinance.Ticker')
    def test_full_analysis_workflow(self, mock_ticker_class, mock_yfinance_ticker):
        """Test complete analysis workflow"""
        mock_ticker_class.return_value = mock_yfinance_ticker

        analyzer = StockAnalyzer(enable_llm=False)
        result = analyzer.analyze_stock("NVDA")

        # Verify complete result structure
        required_sections = ['fundamentals', 'technical', 'sentiment', 'risk']
        for section in required_sections:
            assert section in result
```

### LLM Test Example

```python
@pytest.mark.llm
class TestLLMIntegration:
    def test_real_llm_analysis(self):
        """Test with real LLM API (requires API key)"""
        import os

        if not os.getenv('DEEPSEEK_API_KEY'):
            pytest.skip("No DeepSeek API key available")

        analyzer = StockAnalyzer(enable_llm=True)
        result = analyzer.analyze_stock("NVDA")

        assert result['score']['analysis_method'] == 'llm_enhanced'
```

## Best Practices

### 1. Test Naming

-   Use descriptive test names: `test_analyze_fundamentals_with_missing_data`
-   Group related tests in classes: `TestStockAnalyzer`
-   Use consistent naming patterns

### 2. Mocking Strategy

-   Mock external dependencies (yfinance, APIs, databases)
-   Use fixtures for common mock objects
-   Test both success and failure scenarios

### 3. Assertions

-   Test specific behaviors, not implementation details
-   Use meaningful assertion messages
-   Test edge cases and error conditions

### 4. Test Organization

-   One test file per module/class
-   Group related tests in classes
-   Use appropriate markers for categorization

### 5. Performance

-   Keep unit tests fast (< 1 second each)
-   Use mocks to avoid network calls
-   Mark slow tests appropriately

## Coverage Goals

-   **Unit Tests**: 80%+ coverage
-   **Integration Tests**: Cover all major workflows
-   **Critical Paths**: 95%+ coverage for core analysis logic

### Viewing Coverage

```bash
# Generate coverage report
python run_tests.py --coverage

# Open HTML report
open htmlcov/index.html
```

## Continuous Integration

The testing framework is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
      python run_tests.py --coverage
      python run_tests.py --integration

- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
      file: ./coverage.xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**

    ```bash
    # Ensure src is in Python path
    export PYTHONPATH="${PYTHONPATH}:./src"
    ```

2. **Missing Dependencies**

    ```bash
    uv add pytest pytest-asyncio pytest-mock pytest-cov
    ```

3. **LLM Tests Failing**

    ```bash
    # Set API key
    export DEEPSEEK_API_KEY="your-api-key"

    # Or skip LLM tests
    pytest -m "not llm"
    ```

4. **Slow Tests**
    ```bash
    # Run only fast tests
    python run_tests.py --fast
    ```

### Debug Mode

```bash
# Run with maximum verbosity
python run_tests.py --verbose

# Run specific test with debugging
pytest tests/unit/test_stock_analyzer.py::TestStockAnalyzer::test_analyze_fundamentals -v -s
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure 80%+ coverage for new code
3. Add appropriate markers
4. Update fixtures if needed
5. Run full test suite before committing

```bash
# Pre-commit test run
python run_tests.py --all --coverage
```
