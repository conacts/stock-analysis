# �� Testing Strategy - AI Stock Analysis System

## 🎯 Overview

**Philosophy**: Simple, focused testing for a simple, focused architecture. Test AI logic, database functions, and configuration without infrastructure complexity.

## 🏗️ Testing Architecture

### Core Principles

- ✅ **Unit Tests**: Core TypeScript logic and database functions
- ✅ **Type Safety**: Comprehensive TypeScript validation using Drizzle inferred types
- ✅ **Integration Tests**: AI API client functionality
- ❌ **No Infrastructure Tests**: Avoid complex deployment/infrastructure testing
- ❌ **No UI Tests**: Focus on backend AI logic only

### Test Structure

```
tests/
├── unit/
│   └── basic.test.ts           # Database type validation tests
├── setup.ts                    # Test configuration and environment
└── README.md                   # Test documentation
```

## 🎯 What We Test

### 1. **Database Type Safety**

- Drizzle schema validation
- TypeScript type inference testing
- Database operation function types
- Error handling for invalid data

### 2. **Individual Database Functions**

- Advisor operations: `getAllAdvisors()`, `createAdvisor()`
- Portfolio operations: `getAllPortfolios()`, `getPortfolioById()`
- Analysis operations: `createAnalysis()`, `getAnalysisByPortfolio()`
- Utility operations: `testDatabaseConnection()`, `getTableCounts()`

### 3. **Configuration Management**

- Environment variable validation
- API key configuration checks
- Trigger.dev connection settings
- Error handling for missing config

### 4. **AI Client Integration**

- DeepSeek API client functionality
- API response parsing
- Error handling for API failures
- Timeout and retry logic

### 5. **Task Logic** (Future)

- Trigger.dev task input/output validation
- Analysis result formatting
- Error handling in task execution

## 🚫 What We DON'T Test

### Avoided Complexity

- ❌ **Database Integration**: No actual database connections in tests
- ❌ **API Server Testing**: No FastAPI or Express servers
- ❌ **Complex Mocking**: Keep mocks simple and focused
- ❌ **End-to-End Testing**: Focus on unit and integration only
- ❌ **UI Testing**: No frontend components to test

## 🧪 Testing Tools

### Test Framework

- **Vitest**: Fast, modern test runner for TypeScript
- **Node.js Built-ins**: Minimal external dependencies
- **TypeScript**: Native TypeScript testing support
- **Drizzle ORM**: Type-safe database operations

### Why Vitest?

- ✅ **TypeScript Native**: No transpilation needed
- ✅ **Fast Execution**: Parallel test running
- ✅ **Simple Setup**: Minimal configuration
- ✅ **Modern Features**: ESM support, async/await
- ✅ **Good DX**: Excellent developer experience

## 🚀 Test Execution

### Development Testing

```bash
# Run all tests
npm test

# Watch mode for development
npm test -- --watch

# Run specific test
npm test -- basic.test.ts

# Debug mode
npm test -- --reporter=verbose

# Type checking
npm run type-check

# Build verification
npm run build
```

### CI/CD Testing

```bash
# Full validation pipeline
npm run lint && npm run type-check && npm test

# Coverage report (if enabled)
npm run test:coverage

# Build validation
npm run build
```

## 📝 Current Test Suite

### Database Type Validation Tests

Our current test suite focuses on validating our Drizzle schema types:

```typescript
// tests/unit/basic.test.ts
import { describe, it, expect } from 'vitest';
import type {
  AdvisorSelect,
  AdvisorInsert,
  PortfolioSelect,
  AnalysisResultInsert,
} from '@/db/schema';

describe('Database Types', () => {
  it('should have proper Advisor type structure', () => {
    const advisor: AdvisorSelect = {
      id: 1,
      name: 'Test Advisor',
      systemPrompt: 'Test prompt',
      model: 'deepseek/r1',
      temperature: 0.1,
      maxTokens: 2000,
      status: 'active',
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    expect(advisor.name).toBe('Test Advisor');
    expect(advisor.temperature).toBe(0.1);
    expect(advisor.status).toBe('active');
  });

  it('should have proper Portfolio type structure', () => {
    const portfolio: PortfolioSelect = {
      id: 1,
      name: 'Test Portfolio',
      description: 'A test portfolio',
      advisorId: 1,
      status: 'active',
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    expect(portfolio.name).toBe('Test Portfolio');
    expect(portfolio.advisorId).toBe(1);
  });

  it('should have proper AnalysisResult type structure', () => {
    const analysis: AnalysisResultInsert = {
      portfolioId: 1,
      advisorId: 1,
      analysisType: 'market_opening',
      symbol: 'AAPL',
      analysisData: { recommendation: 'buy' },
      recommendations: { action: 'buy', confidence: 0.8 },
      status: 'completed',
    };

    expect(analysis.portfolioId).toBe(1);
    expect(analysis.analysisType).toBe('market_opening');
  });

  it('should demonstrate type safety', () => {
    // Type checking ensures this works at compile time
    const createAdvisorData: AdvisorInsert = {
      name: 'New Advisor',
      systemPrompt: 'You are a trading advisor',
      model: 'deepseek/r1',
      temperature: 0.1,
      maxTokens: 2000,
      status: 'active',
    };

    expect(createAdvisorData.name).toBe('New Advisor');
    expect(typeof createAdvisorData.temperature).toBe('number');
  });
});
```

## 📋 Test Writing Guidelines

### Database Function Test Pattern

```typescript
import { describe, it, expect, vi } from 'vitest';
import { getAllAdvisors, createAdvisor } from '@/db/advisors';

// Mock the database connection
vi.mock('@/db/connection', () => ({
  db: {
    select: vi.fn(),
    insert: vi.fn(),
  },
}));

describe('Advisor Operations', () => {
  it('should get all advisors', async () => {
    // Mock database response
    const mockAdvisors = [{ id: 1, name: 'Test Advisor', status: 'active' }];

    // Test the function
    // Note: Actual implementation would require proper mocking
    expect(typeof getAllAdvisors).toBe('function');
  });
});
```

### Type Safety Test Pattern

```typescript
describe('Type Safety', () => {
  it('should enforce correct types', () => {
    // This test passes if TypeScript compilation succeeds
    const advisorData: AdvisorInsert = {
      name: 'Test',
      systemPrompt: 'Test prompt',
      // temperature: 'invalid', // This would cause TypeScript error
      temperature: 0.1, // Correct type
    };

    expect(typeof advisorData.temperature).toBe('number');
  });
});
```

### Error Handling Test Pattern

```typescript
describe('Error Handling', () => {
  it('should handle database errors gracefully', async () => {
    // Mock database error
    vi.spyOn(console, 'error').mockImplementation(() => {});

    // Test error scenarios
    // Implementation depends on how functions handle errors
  });
});
```

## ⚡ Performance Considerations

### Test Speed Goals

- ✅ **Unit Tests**: <5 seconds total
- ✅ **Type Checking**: <10 seconds total
- ✅ **Full Suite**: <30 seconds total
- ✅ **CI Pipeline**: <2 minutes total

### Optimization Strategies

- **Parallel Execution**: Vitest runs tests in parallel
- **Simple Mocks**: Avoid complex mock setups
- **Minimal I/O**: No actual database connections
- **Focused Tests**: Test only what matters
- **Type-First**: Leverage TypeScript for validation

## 📊 Test Metrics

### Success Criteria

- ✅ **100% TypeScript Compilation**
- ✅ **All Tests Passing**
- ✅ **Fast Execution** (<30s total)
- ✅ **Zero Flaky Tests**
- ✅ **Type Safety Validation**

### Coverage Strategy

Focus on:

- Database function type safety
- Individual function behavior
- Error handling patterns
- Configuration validation

## 📁 Test Configuration

### Environment Setup

```typescript
// tests/setup.ts
import { beforeAll, afterAll } from 'vitest';
import { config } from 'dotenv';

beforeAll(() => {
  // Load test environment variables
  config({ path: '.env.local' });
  console.log('✅ Test setup loaded');
});

afterAll(() => {
  console.log('🧹 Cleaning up test environment...');
});
```

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.ts', 'tests/**/*.spec.ts'],
    exclude: ['node_modules', 'dist', '**/*.d.ts'],
    reporters: ['default'], // Removed JSON output
  },
  resolve: {
    alias: {
      '@': new URL('./src', import.meta.url).pathname,
    },
  },
});
```

## 🔄 Migration from Previous Approach

### What Changed

- **Drizzle Types**: Using `$inferSelect` and `$inferInsert` instead of Zod schemas
- **Individual Functions**: Testing specific database operations instead of object methods
- **Type-First**: Leveraging TypeScript compilation for validation
- **Simplified Mocking**: Focus on function behavior rather than complex integrations

### Migration Benefits

- ✅ **Better Type Safety**: Drizzle provides superior type inference
- ✅ **Faster Tests**: No schema validation overhead
- ✅ **Explicit Dependencies**: Import only what you test
- ✅ **Better IntelliSense**: Direct function imports

## 🎯 Future Testing Plans

### Phase 1: Current (Type Safety)

- Database type validation
- Function signature testing
- Basic error handling

### Phase 2: Integration Testing

- Mock database operations
- Test individual functions with mocked db
- API client integration tests

### Phase 3: Advanced Testing

- Task execution testing
- Performance benchmarks
- Load testing for AI operations

---

**Testing Philosophy**: Keep it simple, focus on types and core logic, avoid infrastructure complexity.
