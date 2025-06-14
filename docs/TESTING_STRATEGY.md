# Testing Strategy

## Overview

Our stock analysis system uses a **hybrid testing approach** optimized for speed, reliability, and comprehensive coverage.

## Database Testing Strategy

### ✅ **In-Memory SQLite for All Tests**

We use `sqlite:///:memory:` for all test scenarios because:

**Speed Benefits:**

-   10-100x faster than network database calls
-   Tests complete in seconds instead of minutes
-   Faster CI/CD pipeline execution

**Reliability Benefits:**

-   No network dependencies or connection issues
-   No external service failures
-   Consistent test environment every time

**Isolation Benefits:**

-   Each test gets a completely fresh database
-   No test pollution or cleanup issues
-   Perfect test isolation

**Simplicity Benefits:**

-   No database setup or teardown required
-   No connection management complexity
-   Works identically on all developer machines

### 🔄 **SQLAlchemy Abstraction Layer**

Our approach works because:

-   SQLAlchemy handles database differences transparently
-   `JSONB` columns automatically map to `TEXT` with JSON serialization in SQLite
-   Same ORM interface works for both PostgreSQL and SQLite
-   95% of database functionality is identical between engines

### 🚫 **Why We Don't Test Against PostgreSQL**

**Avoided Complexity:**

-   No PostgreSQL service setup in CI
-   No database connection management
-   No cleanup between test runs
-   No flaky network-related test failures

**Cost Efficiency:**

-   Faster CI builds (less compute time)
-   No external database resources needed
-   Reduced infrastructure complexity

**Sufficient Coverage:**

-   We don't use complex PostgreSQL-specific features
-   No custom functions, stored procedures, or advanced indexing
-   JSONB usage is abstracted by SQLAlchemy
-   Business logic testing is database-agnostic

## Test Categories

### 🏃‍♂️ **Fast Unit Tests** (`--fast`)

-   Core business logic
-   Data transformations
-   Calculations and algorithms
-   **Runtime:** < 1 second

### 🧪 **Unit Tests** (`--unit`)

-   All fast tests plus database operations
-   Portfolio management functionality
-   Data storage and retrieval
-   **Runtime:** < 10 seconds

### 🔗 **Integration Tests** (`--integration`)

-   External API interactions (mocked)
-   End-to-end workflows
-   Component integration
-   **Runtime:** < 30 seconds

### 🤖 **LLM Tests** (`--llm`)

-   AI analysis functionality
-   Requires `DEEPSEEK_API_KEY`
-   Only runs when API key is available
-   **Runtime:** Variable (depends on API)

## CI/CD Pipeline

### **Multi-Python Testing**

-   Tests run on Python 3.11, 3.12, and 3.13
-   Ensures compatibility across versions
-   Matrix builds for comprehensive coverage

### **Comprehensive Checks**

1. **Linting:** Ruff for code quality
2. **Type Checking:** MyPy for type safety
3. **Security:** Bandit for security issues
4. **Testing:** All test categories
5. **Performance:** Benchmark critical operations
6. **Coverage:** Code coverage reporting

### **Portfolio CLI Testing**

-   Tests real CLI functionality in CI
-   Verifies database operations work end-to-end
-   Ensures deployment readiness

## Local Development

### **Quick Testing**

```bash
make test          # Fast unit tests
make test-all      # All tests except slow ones
make test-coverage # With coverage report
```

### **Specific Categories**

```bash
uv run python run_tests.py --fast        # Fastest tests only
uv run python run_tests.py --unit        # Unit tests
uv run python run_tests.py --integration # Integration tests
uv run python run_tests.py --llm         # LLM tests (needs API key)
```

## Benefits of Our Approach

### ⚡ **Performance**

-   157 tests complete in ~8 seconds
-   No network latency or database overhead
-   Instant feedback for developers

### 🛡️ **Reliability**

-   Zero flaky tests due to external dependencies
-   Consistent results across all environments
-   No "works on my machine" issues

### 🔧 **Maintainability**

-   Simple test setup and configuration
-   No complex database management
-   Easy to add new tests

### 💰 **Cost Effective**

-   Minimal CI resource usage
-   No external database costs
-   Faster development cycles

## When to Consider PostgreSQL Testing

We would only add PostgreSQL testing if we:

-   Used complex PostgreSQL-specific features
-   Had custom database functions or procedures
-   Needed to test specific PostgreSQL performance characteristics
-   Used advanced indexing strategies that differ between engines

**Current Assessment:** Not needed for our use case.

## Test Coverage

-   **157 passing tests** covering all major functionality
-   **Unit tests:** Core business logic and database operations
-   **Integration tests:** End-to-end workflows with mocked external services
-   **Portfolio tests:** Complete portfolio management system
-   **LLM tests:** AI-enhanced analysis features

## Conclusion

Our in-memory SQLite testing strategy provides:

-   **Maximum speed** for rapid development
-   **Maximum reliability** with zero external dependencies
-   **Maximum simplicity** for easy maintenance
-   **Sufficient coverage** for our application's needs

This approach delivers 95% of the confidence at 5% of the complexity and cost.
