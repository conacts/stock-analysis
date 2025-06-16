# 📁 Source Code Structure

## 🎯 TypeScript AI Trading System

This is the **TypeScript-only** codebase focused on **Trigger.dev automation**, **DeepSeek AI integration**, and **portfolio management** with configurable AI advisors.

## 🏗️ Module Organization

```
src/
├── automation/tasks/           # Trigger.dev automation tasks
│   ├── market-opening-analysis.ts  # Market open coordinator
│   ├── ai-trading-analysis.ts      # Individual stock analysis
│   ├── health-check.ts             # System monitoring
│   ├── alpaca-health-check.ts      # Alpaca API health
│   └── deepseek-health-check.ts    # DeepSeek API health
├── clients/                    # API clients
│   ├── deepseek.ts            # DeepSeek AI client
│   └── alpaca.ts              # Alpaca Markets client
├── db/                        # Database layer (individual functions)
│   ├── schema.ts              # All table definitions & types
│   ├── connection.ts          # Database connection
│   ├── advisors.ts            # Advisor operations
│   ├── portfolios.ts          # Portfolio operations
│   ├── holdings.ts            # Holdings operations
│   ├── transactions.ts        # Transaction operations
│   ├── balances.ts            # Balance operations
│   ├── analysis.ts            # Analysis operations
│   ├── triggers.ts            # Trigger operations
│   ├── conversations.ts       # Conversation operations
│   ├── performance.ts         # Performance operations
│   └── utils.ts               # Utility operations
└── utils/                     # Configuration utilities
    └── config.ts              # Environment configuration
```

## 🎯 Key Components

### 🤖 **Automation Tasks** (`automation/tasks/`)

**Core Value**: Scheduled AI-powered portfolio analysis

- **`market-opening-analysis.ts`**: Weekday 9:30 AM ET coordinator that triggers portfolio analysis
- **`ai-trading-analysis.ts`**: Individual stock analysis using DeepSeek AI
- **`health-check.ts`**: System health monitoring with comprehensive checks
- **`alpaca-health-check.ts`**: Alpaca Markets API connectivity monitoring
- **`deepseek-health-check.ts`**: DeepSeek AI API connectivity monitoring

### 🔌 **API Clients** (`clients/`)

**Purpose**: Clean, type-safe API integrations

- **`deepseek.ts`**: DeepSeek AI client with comprehensive analysis methods
- **`alpaca.ts`**: Alpaca Markets client for market data and trading
- **Error handling**: Robust error handling and timeout management
- **Cost tracking**: Built-in API cost monitoring

### 🗄️ **Database Layer** (`db/`)

**Approach**: Individual function exports with Drizzle ORM

- **`schema.ts`**: All table definitions and TypeScript types in one file
- **`connection.ts`**: Database connection with Drizzle ORM setup
- **Individual operation files**: Specific functions for each domain
  - `advisors.ts` - `getAllAdvisors()`, `createAdvisor()`, etc.
  - `portfolios.ts` - `getAllPortfolios()`, `getPortfolioById()`, etc.
  - `holdings.ts` - `getHoldingsByPortfolio()`, `upsertHolding()`, etc.
  - `transactions.ts` - `getTransactionsByPortfolio()`, `createTransaction()`, etc.
  - `balances.ts` - `getLatestBalance()`, `recordBalance()`, etc.
  - `analysis.ts` - `getAnalysisByPortfolio()`, `createAnalysis()`, etc.
  - `triggers.ts` - `getActiveTriggers()`, `createTrigger()`, etc.
  - `conversations.ts` - `createConversationThread()`, `addThreadMessage()`, etc.
  - `performance.ts` - `getPerformanceByAdvisor()`, `createPerformance()`, etc.
  - `utils.ts` - `testDatabaseConnection()`, `getTableCounts()`, etc.

### 🔧 **Configuration** (`utils/`)

**Strategy**: Environment-based configuration

- **`config.ts`**: Centralized environment variable management
- **Type-safe**: All config values properly typed and validated
- **Direct access**: Simple `process.env` access pattern

## 🗄️ Database Schema

### Core Tables

#### Advisors (Simplified)

```sql
CREATE TABLE advisors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    system_prompt TEXT NOT NULL,
    model VARCHAR(50) DEFAULT 'deepseek/r1',
    temperature DECIMAL(3,2) DEFAULT 0.1,
    max_tokens INTEGER DEFAULT 2000,
    status VARCHAR(20) DEFAULT 'active'
);
```

#### Performance (Separate Table)

```sql
CREATE TABLE performance (
    id SERIAL PRIMARY KEY,
    advisor_id INTEGER REFERENCES advisors(id),
    portfolio_id INTEGER REFERENCES portfolios(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    total_return DECIMAL(10,4) DEFAULT 0,
    sharpe_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    win_rate DECIMAL(5,4)
);
```

#### Portfolios

```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    advisor_id INTEGER REFERENCES advisors(id),
    status VARCHAR(20) DEFAULT 'active'
);
```

#### Analysis Results

```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    advisor_id INTEGER NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    analysis_data JSONB,
    recommendations JSONB,
    status VARCHAR(20) DEFAULT 'completed'
);
```

## 🔧 Development Patterns

### Database Operations

```typescript
// Import specific functions
import { getAllAdvisors, createAdvisor } from '@/db/advisors';
import { getAllPortfolios } from '@/db/portfolios';
import { createAnalysis } from '@/db/analysis';

// Use functions directly
const advisors = await getAllAdvisors();
const portfolios = await getAllPortfolios();
const analysis = await createAnalysis({
  portfolioId: 1,
  advisorId: 1,
  analysisType: 'market_opening',
  symbol: 'AAPL',
  analysisData: { recommendation: 'buy' },
  recommendations: { action: 'buy', confidence: 0.8 },
});
```

### Task Development

```typescript
// automation/tasks/market-opening-analysis.ts
export const marketOpeningAnalysis = schedules.task({
  id: 'market-opening-analysis',
  cron: '30 13 * * 1-5', // 9:30 AM ET weekdays
  run: async () => {
    // Check market status
    const marketClock = await alpaca.getMarketClock();
    if (!marketClock.is_open) return;

    // Get active portfolios
    const portfolios = await getAllPortfolios();

    // Trigger analysis for each portfolio
    for (const portfolio of portfolios) {
      // Trigger individual portfolio analysis
    }
  },
});
```

### Client Usage

```typescript
// clients/deepseek.ts
export class DeepSeekClient {
  async analyzeStockComprehensive(
    symbol: string,
    financialData: any,
    newsData: any[],
    technicalData: any,
    marketContext: any
  ): Promise<DeepSeekAnalysisResult> {
    const response = await this.makeRequest({
      model: 'deepseek/r1',
      messages: [
        { role: 'system', content: this.systemPrompt },
        { role: 'user', content: this.buildAnalysisPrompt(...) }
      ]
    });

    return this.parseAnalysisResponse(response);
  }
}
```

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── unit/
│   └── basic.test.ts           # Database type validation tests
└── setup.ts                    # Test configuration
```

### Testing Focus

- **Database type validation**: Drizzle schema and type checking
- **Type checking**: Comprehensive TypeScript validation
- **Unit tests**: Core logic and utilities
- **Integration tests**: API client functionality (planned)

## 🔄 Migration History

- **Simplified Schema**: Removed complex AI agent fields, moved to advisor model
- **Performance Separation**: Moved performance metrics to separate table
- **Individual Functions**: Converted from object-based to function-based operations
- **Consolidated Types**: All types and schema in single file

## 🚧 Development Status

### ✅ Completed

- TypeScript-only architecture
- Trigger.dev v3 integration
- Drizzle ORM database layer with individual functions
- Simplified advisor model (renamed from AI agents)
- Separate performance tracking table
- Consolidated schema and types
- Individual function exports for better IntelliSense
- Absolute imports with @/db/... pattern

### 🔄 In Progress

- Individual portfolio analysis tasks
- AI advisor prompt optimization
- Analysis result processing

### 📋 Planned

- Web dashboard for portfolio management
- Real-time analysis triggers
- Performance tracking and reporting
- Advanced risk management
- Trading execution integration

## 🧪 Testing

```bash
# Run tests
npm test

# Type checking
npm run type-check

# Build verification
npm run build
```

## 📝 Contributing

1. Follow TypeScript best practices
2. Use Drizzle ORM for all database operations
3. Import individual functions instead of object exports
4. Write tests for new functionality
5. Update documentation for schema changes
6. Use conventional commit messages

## 📄 License

MIT License - see LICENSE file for details
