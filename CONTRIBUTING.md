# 🤝 Contributing to AI Stock Analysis System

## 🎯 Welcome!

Thank you for your interest in contributing to the **simplified AI stock analysis system**! This project focuses on **AI-powered market analysis** through **Trigger.dev automation** with **type-safe database operations**.

## 🏗️ Project Overview

### Core Philosophy

- **Simplicity First**: Avoid complexity that defeats the original purpose
- **AI-Focused**: DeepSeek integration for market insights
- **Automation-Driven**: Trigger.dev tasks for scheduled analysis
- **TypeScript-Only**: Clean, typed codebase with Drizzle ORM
- **Function-Based**: Individual database functions for better type safety

### What We DON'T Want

- Complex API servers
- Object-based database operations
- Multiple deployment platforms
- Heavy database systems
- Timeout-prone architectures

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- TypeScript knowledge
- Basic understanding of AI/market analysis
- Familiarity with Drizzle ORM (helpful)

### Setup

```bash
# Clone and setup
git clone <repository>
cd stock-analysis
npm install

# Configure environment
cp .env.example .env
# Add your DeepSeek API key and Trigger.dev tokens

# Setup database
npm run db:migrate

# Start development
npx trigger.dev@latest dev
```

## 📁 Project Structure

```
src/
├── automation/tasks/           # Trigger.dev tasks (main focus)
│   ├── ai-trading-analysis.ts  # DeepSeek AI analysis
│   └── health-check.ts         # System monitoring
├── clients/                    # API clients
├── db/                         # Database operations (NEW!)
│   ├── schema.ts              # All table definitions & types
│   ├── connection.ts          # Database connection
│   ├── advisors.ts            # getAllAdvisors(), createAdvisor()
│   ├── portfolios.ts          # getAllPortfolios(), getPortfolioById()
│   ├── performance.ts         # getPerformanceByAdvisor()
│   └── utils.ts               # testDatabaseConnection()
├── types/                      # TypeScript types
└── utils/                      # Configuration utils
```

## 🎯 Contribution Areas

### 1. Database Operations (High Priority)

- Improve individual database functions
- Add new type-safe operations
- Enhance error handling for database operations
- Optimize query performance with Drizzle

### 2. AI Task Development (High Priority)

- Improve DeepSeek prompts and analysis quality
- Add new market analysis capabilities
- Enhance error handling and reliability
- Optimize task scheduling and performance

### 3. TypeScript Infrastructure

- Add new TypeScript types using Drizzle inferred types
- Improve configuration management
- Enhance testing coverage
- Code quality improvements

### 4. Documentation

- Update guides and examples
- Improve code comments
- Create tutorials for new features
- Document best practices

## 🔄 Development Workflow

### 1. Pick an Issue

- Check [Issues](https://github.com/your-repo/issues) for open tasks
- Look for "good first issue" labels
- Focus on database functions, AI tasks, and TypeScript improvements

### 2. Create Branch

```bash
git checkout -b feat/improve-advisor-functions
# or
git checkout -b fix/database-error-handling
```

### 3. Develop & Test

```bash
# Make changes to database functions
npm run type-check                  # Check TypeScript
npm test                           # Run tests
npm run db:test                    # Test database connection
npx trigger.dev@latest dev         # Test tasks locally
```

### 4. Submit PR

- Write clear commit messages
- Include tests for new database functions
- Update documentation
- Request review

## 📝 Code Standards

### Database Function Style

```typescript
// src/db/advisors.ts
import { db } from '@/db/connection';
import { advisors } from '@/db/schema';
import type { AdvisorSelect, AdvisorInsert } from '@/db/schema';

// Individual function exports (NOT object exports)
export async function getAllAdvisors(): Promise<AdvisorSelect[]> {
  return await db.select().from(advisors);
}

export async function createAdvisor(data: AdvisorInsert): Promise<AdvisorSelect> {
  const [advisor] = await db.insert(advisors).values(data).returning();
  return advisor;
}
```

### TypeScript Style

```typescript
// Use Drizzle inferred types
import type { AdvisorSelect, AdvisorInsert } from '@/db/schema';

// Prefer individual function imports
import { getAllAdvisors, createAdvisor } from '@/db/advisors';
import { getAllPortfolios } from '@/db/portfolios';

// Use absolute imports with @/ prefix
import { testDatabaseConnection } from '@/db/utils';
```

### Task Development

```typescript
export const myAnalysisTask = task({
  id: 'my-analysis-task',
  run: async (payload: { symbols: string[] }) => {
    // Use individual database functions
    const advisors = await getAllAdvisors();
    const portfolios = await getAllPortfolios();

    // Clear input validation
    // Robust error handling
    // Meaningful return values
    return analysis;
  },
});
```

### Testing

```typescript
import { describe, it, expect } from 'vitest';
import type { AdvisorSelect } from '@/db/schema';

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
    expect(typeof advisor.temperature).toBe('number');
  });
});
```

## 🧪 Testing Guidelines

### Required Tests

- Type validation tests for database operations
- Unit tests for individual functions
- Integration tests for Trigger.dev tasks
- Type checking must pass
- Database connection tests

### Test Commands

```bash
npm test                    # All tests
npm test -- --watch        # Watch mode
npm test -- basic.test.ts   # Specific test
npm run type-check          # TypeScript validation
npm run db:test            # Database connectivity
```

## 📋 Pull Request Guidelines

### PR Requirements

- [ ] Clear description of changes
- [ ] Tests pass (`npm test`)
- [ ] TypeScript compiles (`npm run type-check`)
- [ ] Database functions tested (`npm run db:test`)
- [ ] Code follows individual function pattern
- [ ] Uses absolute imports with `@/db/...`
- [ ] Documentation updated if needed

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New database function
- [ ] New AI task feature
- [ ] Documentation update
- [ ] Performance improvement

## Database Changes

- [ ] Added new individual functions
- [ ] Updated schema types
- [ ] Migration required
- [ ] No database changes

## Testing

- [ ] Tests pass locally
- [ ] Database connectivity tested
- [ ] Tested with Trigger.dev dev server
- [ ] Added/updated tests for changes

## Checklist

- [ ] TypeScript compiles without errors
- [ ] Uses individual function exports
- [ ] Uses absolute imports (@/db/...)
- [ ] Code follows project style
- [ ] Self-review completed
```

## 🚫 What NOT to Contribute

### Avoid These Additions

- ❌ Object-based database operations (`export const advisorOps = {...}`)
- ❌ New API servers or web frameworks
- ❌ Complex database migrations without clear purpose
- ❌ Multiple deployment platforms
- ❌ Heavy external dependencies
- ❌ Features that add complexity without clear value

### Before Adding Features

Ask yourself:

1. Does this solve a real problem?
2. Can it be solved with individual functions?
3. Does it maintain focus on AI analysis?
4. Will it add complexity that defeats our purpose?
5. Does it follow the function-based pattern?

## 🤖 Database & AI Focus Areas

### Priority Contributions

1. **Better Database Functions**: Improve type safety and performance
2. **Enhanced AI Prompts**: Improve DeepSeek analysis quality
3. **Error Handling**: Robust failure recovery for database and AI operations
4. **Task Optimization**: Faster, more reliable execution
5. **Monitoring**: Better health checks and alerting

### Examples of Good Contributions

#### Database Functions

```typescript
// Adding a new advisor function
export async function getAdvisorByStatus(status: 'active' | 'inactive'): Promise<AdvisorSelect[]> {
  return await db.select().from(advisors).where(eq(advisors.status, status));
}
```

#### AI Task Improvements

- Adding market context to AI analysis
- Improving error messages and logging
- Adding new stock analysis indicators
- Optimizing task scheduling

#### Type Safety Enhancements

- Better TypeScript types with Drizzle inferred types
- Improved error handling patterns
- Enhanced type validation

## 🔍 Code Review Process

### What We Look For

- **Simplicity**: Is this the simplest solution?
- **Type Safety**: Proper Drizzle ORM usage and TypeScript types
- **Function Pattern**: Individual functions instead of object exports
- **Testing**: Adequate test coverage
- **Documentation**: Clear code and comments
- **Focus**: Does it align with project goals?

### Review Timeline

- Initial feedback within 24-48 hours
- Final review within 1 week
- Merge after approval and passing CI

## 🛠️ Development Tips

### Database Development

```bash
# Check database schema
npm run db:studio

# Generate new migration
npm run db:generate

# Reset database (development only)
npm run db:reset

# Test specific database function
npm run test -- advisors.test.ts
```

### Local Development

```bash
# Start Trigger.dev development server
npx trigger.dev@latest dev

# Test database connectivity
npm run db:test

# Run type checking
npm run type-check

# Test specific task
# Use Trigger.dev dashboard to manually trigger tasks

# Monitor logs
# Check both terminal and Trigger.dev dashboard
```

### Debugging

- Use TypeScript strict mode
- Test database functions individually
- Add comprehensive logging
- Test edge cases thoroughly
- Monitor task execution in Trigger.dev dashboard

## 📚 Resources

### Documentation

- [Drizzle ORM Docs](https://orm.drizzle.team/docs/overview)
- [Trigger.dev Docs](https://trigger.dev/docs)
- [DeepSeek API Docs](https://platform.deepseek.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Project Docs

- [README.md](README.md) - Project overview
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [CONFIGURATION.md](CONFIGURATION.md) - Setup guide
- [TESTING_STRATEGY.md](TESTING_STRATEGY.md) - Testing approach

## 🆘 Getting Help

### Community Support

- Open an issue for bugs or feature requests
- Ask questions in pull request comments
- Check existing issues and documentation first

### Contact

- Create GitHub issue for bugs
- Submit PR for feature proposals
- Use discussions for general questions

---

## 🎉 Recognition

Contributors will be:

- Added to project contributors list
- Mentioned in release notes for significant contributions
- Invited to provide input on project direction

**Thank you for helping keep this project simple, focused, and effective with type-safe database operations!**
