# 🚀 AI Stock Analysis System

A simplified TypeScript-based AI stock analysis system that uses **DeepSeek AI** for market analysis with **Trigger.dev automation**. Features type-safe database operations with **Drizzle ORM** and individual function exports for better developer experience.

[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Trigger.dev](https://img.shields.io/badge/Trigger.dev-v3-purple.svg)](https://trigger.dev/)
[![Drizzle](https://img.shields.io/badge/Drizzle-ORM-green.svg)](https://orm.drizzle.team/)

## ✨ Key Features

### 🤖 **AI-Powered Analysis**

- **DeepSeek AI Integration**: Advanced market analysis with configurable advisors
- **Custom System Prompts**: Each advisor uses different AI strategies
- **Automated Analysis**: Scheduled market analysis with Trigger.dev
- **Type-Safe Operations**: Full TypeScript support with Drizzle ORM

### 🗄️ **Simplified Database Layer**

- **Individual Functions**: Import specific functions like `getAllAdvisors()`, `createPortfolio()`
- **Drizzle ORM**: Type-safe database operations with auto-completion
- **SQLite**: Lightweight, file-based database for simplicity
- **Consolidated Schema**: All tables and types in single `src/db/schema.ts` file

### 📊 **Advisor-Based Architecture**

- **Simplified Model**: Streamlined from complex AI agent system
- **Performance Tracking**: Separate table for advisor performance metrics
- **Portfolio Association**: Each portfolio linked to specific advisor
- **Status Management**: Active/inactive advisor and portfolio tracking

### 🏗️ **Modern TypeScript Architecture**

- **Function-Based**: Individual database functions for better IntelliSense
- **Absolute Imports**: Clean `@/db/...` import paths
- **Type Inference**: Drizzle's `$inferSelect` and `$inferInsert` for automatic types
- **Trigger.dev v3**: Scheduled task automation and workflow orchestration

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- DeepSeek API account
- Trigger.dev account

### Installation

1. **Clone and install dependencies:**

```bash
git clone <repository-url>
cd stock-analysis
npm install
```

2. **Environment Setup:**
   Create `.env` with your API keys:

```bash
# Database (SQLite)
DATABASE_URL=file:./database.db

# DeepSeek AI API
DEEPSEEK_API_KEY=sk-your-deepseek-api-key

# Trigger.dev
TRIGGER_SECRET_KEY=tr_prod_your-trigger-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-trigger-token

# Optional: Slack notifications
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#trading-alerts
```

3. **Database Setup:**

```bash
# Run database migrations
npm run db:migrate

# Check database connection
npm run db:test
```

4. **Development:**

```bash
# Build the project
npm run build

# Start Trigger.dev development server
npx trigger.dev@latest dev

# Run tests
npm test
```

## 📊 System Workflow

### Market Analysis Process

The system performs automated analysis through:

1. **Scheduled Tasks** - Trigger.dev runs analysis on schedule
2. **Advisor Selection** - Each portfolio uses its assigned advisor
3. **AI Analysis** - DeepSeek processes market data with custom prompts
4. **Result Storage** - Analysis results stored with full type safety

### Database Operations

All database operations use individual functions for better type safety:

```typescript
// Import specific functions
import { getAllAdvisors, createAdvisor } from '@/db/advisors';
import { getAllPortfolios, getPortfolioById } from '@/db/portfolios';
import { testDatabaseConnection } from '@/db/utils';

// Use with full TypeScript support
const advisors = await getAllAdvisors();
const portfolio = await getPortfolioById(1);
const isConnected = await testDatabaseConnection();
```

## 🛠️ Available Scripts

### Development

- `npm run build` - Compile TypeScript
- `npm test` - Run test suite
- `npm run type-check` - TypeScript type checking

### Database

- `npm run db:migrate` - Run database migrations
- `npm run db:generate` - Generate new migration
- `npm run db:studio` - Open Drizzle Studio
- `npm run db:test` - Test database connection

### Trigger.dev

- `npx trigger.dev@latest dev` - Development server
- `npx trigger.dev@latest deploy` - Deploy to production

### Code Quality

- `npm run format` - Format code with Prettier
- `npm run lint` - Run ESLint
- `npm run ci` - Full CI pipeline

## 📈 Current Tasks

### Active Trigger.dev Tasks

1. **`market-opening-analysis`** - Scheduled market analysis coordinator
2. **`ai-trading-analysis`** - Individual stock analysis with DeepSeek
3. **`health-check`** - System health monitoring

### Task Features

- **Type-Safe Payloads** - Full TypeScript support for task inputs/outputs
- **Error Handling** - Robust error recovery and logging
- **Database Integration** - Uses individual database functions

## 🗄️ Database Layer

### Architecture

```
src/db/
├── schema.ts              # All table definitions & TypeScript types
├── connection.ts          # Database connection setup
├── migrate.ts            # Migration runner
├── advisors.ts           # getAllAdvisors(), createAdvisor(), etc.
├── portfolios.ts         # getAllPortfolios(), getPortfolioById(), etc.
├── performance.ts        # getPerformanceByAdvisor(), createPerformance(), etc.
├── analysis.ts           # getAnalysisByPortfolio(), createAnalysis(), etc.
├── utils.ts              # testDatabaseConnection(), getTableCounts(), etc.
└── migrations/           # SQL migration files
```

### Key Features

- **Individual Functions**: Import specific functions instead of object exports
- **Drizzle ORM**: Type-safe database operations with auto-completion
- **Consolidated Schema**: All tables and types in single file
- **Advisor Architecture**: Simplified from complex AI agent model
- **Performance Tracking**: Separate table for performance metrics

### Usage Examples

```typescript
// Import specific functions (NOT object exports)
import { getAllAdvisors, createAdvisor } from '@/db/advisors';
import { getAllPortfolios } from '@/db/portfolios';
import { getPerformanceByAdvisor } from '@/db/performance';

// Import types from schema
import type { AdvisorSelect, AdvisorInsert } from '@/db/schema';

// Use with full type safety
const advisors: AdvisorSelect[] = await getAllAdvisors();

const newAdvisor: AdvisorInsert = {
  name: 'Growth Advisor',
  systemPrompt: 'You are a growth-focused investment advisor.',
  model: 'deepseek/r1',
  temperature: 0.1,
  status: 'active',
};

const advisor = await createAdvisor(newAdvisor);
```

## 🗄️ Database Schema

### Core Tables

#### Advisors (Simplified from AI Agents)

```sql
CREATE TABLE advisors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    model TEXT DEFAULT 'deepseek/r1',
    temperature REAL DEFAULT 0.1,
    max_tokens INTEGER DEFAULT 2000,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### Performance (Separated from Advisors)

```sql
CREATE TABLE performance (
    id INTEGER PRIMARY KEY,
    advisor_id INTEGER REFERENCES advisors(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    total_return REAL DEFAULT 0,
    sharpe_ratio REAL,
    max_drawdown REAL,
    win_rate REAL
);
```

#### Portfolios

```sql
CREATE TABLE portfolios (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    advisor_id INTEGER REFERENCES advisors(id),
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### Analysis Results

```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    advisor_id INTEGER NOT NULL,
    analysis_type TEXT NOT NULL,
    symbol TEXT,
    analysis_data TEXT, -- JSON string
    recommendations TEXT, -- JSON string
    status TEXT DEFAULT 'completed',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Key Improvements

- **Simplified Schema**: Removed complex fields from advisor table
- **Performance Separation**: Dedicated table for performance metrics
- **SQLite**: Lightweight, file-based database
- **Type Safety**: Full TypeScript support with Drizzle inferred types

## 🏗️ Architecture

```
stock-analysis/
├── src/
│   ├── automation/
│   │   └── tasks/                    # Trigger.dev automation tasks
│   │       ├── market-opening-analysis.ts
│   │       ├── ai-trading-analysis.ts
│   │       └── health-check.ts
│   ├── clients/                      # API clients
│   │   ├── deepseek.ts               # DeepSeek AI API
│   │   └── alpaca.ts                 # Alpaca Markets API (optional)
│   ├── db/                           # Database layer (individual functions)
│   │   ├── schema.ts                 # All table definitions & types
│   │   ├── connection.ts             # Database connection
│   │   ├── advisors.ts               # getAllAdvisors(), createAdvisor()
│   │   ├── portfolios.ts             # getAllPortfolios(), getPortfolioById()
│   │   ├── performance.ts            # getPerformanceByAdvisor()
│   │   ├── analysis.ts               # createAnalysis(), getAnalysisByPortfolio()
│   │   ├── utils.ts                  # testDatabaseConnection()
│   │   └── migrations/               # SQL migration files
│   ├── types/                        # Additional TypeScript types
│   └── utils/
│       └── config.ts                 # Environment configuration
├── tests/                            # Test suite
│   ├── unit/
│   │   └── basic.test.ts             # Database type validation
│   └── setup.ts                     # Test configuration
├── trigger.config.ts                 # Trigger.dev configuration
├── drizzle.config.ts                 # Drizzle ORM configuration
└── package.json                      # Dependencies and scripts
```

## 🔄 Migration History

### Major Refactoring (Recent)

- **Individual Functions**: Converted from object-based to function-based operations
- **Drizzle ORM**: Migrated from raw SQL to type-safe Drizzle operations
- **Simplified Schema**: Removed complex AI agent fields, renamed to advisors
- **Performance Separation**: Moved performance metrics to separate table
- **Consolidated Types**: All types and schema in single file
- **SQLite**: Simplified from PostgreSQL to SQLite
- **Absolute Imports**: Clean `@/db/...` import paths throughout

### Benefits

- ✅ **Better Type Safety**: Full TypeScript support with Drizzle
- ✅ **Faster Development**: Auto-completion and IntelliSense
- ✅ **Explicit Dependencies**: Import only what you use
- ✅ **Better Performance**: Optimized database operations
- ✅ **Simpler Architecture**: Focused on core AI value

## 🚧 Development Status

### ✅ Completed

- TypeScript-only architecture
- Trigger.dev v3 integration
- Drizzle ORM database layer with individual functions
- Simplified advisor model (renamed from AI agents)
- Separate performance tracking table
- Consolidated schema and types
- Individual function exports for better IntelliSense
- Absolute imports with `@/db/...` pattern
- SQLite database with migrations
- Type-safe operations with Drizzle inferred types

### 🔄 In Progress

- Enhanced AI advisor prompt optimization
- Analysis result processing improvements
- Performance tracking implementation

### 📋 Planned

- Web dashboard for advisor management
- Real-time analysis triggers
- Advanced performance metrics
- Risk management features

## 🧪 Testing

### Current Test Suite

```bash
# Run all tests
npm test

# Type checking
npm run type-check

# Database connectivity
npm run db:test

# Build verification
npm run build
```

### Test Focus

- Database type validation with Drizzle inferred types
- Individual function behavior
- TypeScript compilation
- Configuration validation

## 📝 Contributing

1. **Follow Function-Based Pattern**: Use individual functions, not object exports
2. **Use Drizzle ORM**: All database operations through Drizzle
3. **Absolute Imports**: Use `@/db/...` import paths
4. **Type Safety**: Leverage Drizzle inferred types
5. **Write Tests**: Add tests for new functionality
6. **Update Documentation**: Keep docs current with changes

### Example Contribution

```typescript
// ✅ Good: Individual function export
export async function getAdvisorByStatus(status: 'active' | 'inactive'): Promise<AdvisorSelect[]> {
  return await db.select().from(advisors).where(eq(advisors.status, status));
}

// ❌ Avoid: Object-based exports
export const advisorOps = {
  async getByStatus() {
    /* ... */
  },
};
```

## 📄 License

MIT License - see LICENSE file for details

---

**Focus**: Simple, type-safe AI stock analysis with individual database functions and modern TypeScript architecture.
