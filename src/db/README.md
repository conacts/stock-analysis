# Database Operations with Drizzle ORM

This directory contains our simplified database schema, connection management, and individual operation functions using Drizzle ORM.

## Structure

```
src/db/
├── schema.ts            # All table definitions and TypeScript types
├── connection.ts        # Database connection setup
├── migrate.ts          # Migration runner
├── migrations/         # SQL migration files (existing)
├── advisors.ts         # Advisor operations
├── portfolios.ts       # Portfolio operations
├── holdings.ts         # Holdings operations
├── transactions.ts     # Transaction operations
├── balances.ts         # Balance operations
├── analysis.ts         # Analysis operations
├── triggers.ts         # Trigger operations
├── conversations.ts    # Conversation operations
├── performance.ts      # Performance operations
├── utils.ts           # Utility operations
└── README.md          # This file
```

## Key Improvements over Previous Approach

✅ **Individual Functions**: Direct function exports instead of object patterns  
✅ **Type Safety**: Full TypeScript support with auto-completion  
✅ **Simplified Imports**: Import specific functions you need  
✅ **Auto-Generated Types**: Schema-driven type inference  
✅ **Consolidated Schema**: Single file with all table definitions and types  
✅ **Migration Management**: Integrated with Drizzle Kit

## Usage Examples

### Import Specific Functions

```typescript
// Import only what you need
import { getAllAdvisors, createAdvisor } from '@/db/advisors';
import { getAllPortfolios, getPortfolioById } from '@/db/portfolios';
import { createAnalysis } from '@/db/analysis';
import { testDatabaseConnection } from '@/db/utils';
```

### Basic CRUD Operations

```typescript
// Create an advisor
const advisor = await createAdvisor({
  name: 'Trading Bot Alpha',
  systemPrompt: 'You are a conservative trading assistant...',
  model: 'deepseek/r1',
  temperature: 0.1,
  maxTokens: 2000,
  status: 'active',
});

// Get portfolios with filters
const activePortfolios = await getAllPortfolios({
  status: 'active',
});

// Update holdings
const holding = await upsertHolding({
  portfolioId: 1,
  symbol: 'AAPL',
  quantity: '100',
  averageCost: '150.00',
});

// Create analysis
const analysis = await createAnalysis({
  portfolioId: 1,
  advisorId: 1,
  analysisType: 'market_opening',
  symbol: 'AAPL',
  analysisData: { recommendation: 'buy' },
  recommendations: { action: 'buy', confidence: 0.8 },
});
```

### Advanced Operations

```typescript
// Test database connection
const isConnected = await testDatabaseConnection();

// Get performance metrics
const performance = await getPerformanceByAdvisor(1, 1);

// Create conversation thread
const thread = await createConversationThread({
  portfolioId: 1,
  advisorId: 1,
  threadType: 'analysis',
  title: 'Q1 Portfolio Review',
});
```

## Migration Commands

```bash
# Generate new migrations from schema changes
npm run db:generate

# Run pending migrations
npm run db:migrate

# Open Drizzle Studio for database inspection
npm run db:studio

# Drop all tables (be careful!)
npm run db:drop
```

## Schema Overview

- **`advisors`**: AI advisor configurations (simplified from ai_agents)
- **`performance`**: Separate performance tracking table
- **`portfolios`**: Portfolio management linked to advisors
- **`portfolioHoldings`**: Current stock positions
- **`transactions`**: Buy/sell transaction history
- **`portfolioBalances`**: Balance snapshots over time
- **`analysisResults`**: AI analysis results and recommendations
- **`marketTriggers`**: Automated trading triggers
- **`triggerExecutions`**: Trigger execution tracking
- **`conversationThreads`**: AI conversation threads
- **`threadMessages`**: Individual messages in threads
- **`advisorFunctionCalls`**: Function call tracking

## Benefits vs. Previous Approach

### Before (Object-based Operations)

```typescript
// Old pattern
import { advisorOps } from '@/db/operations';
await advisorOps.getAll();
await advisorOps.getById(1);
```

### After (Individual Functions)

```typescript
// New pattern - better IntelliSense and type safety
import { getAllAdvisors, getAdvisorById } from '@/db/advisors';
await getAllAdvisors();
await getAdvisorById(1);
```

### Advantages

- ✅ **Better IntelliSense**: Direct function imports
- ✅ **Explicit imports**: Only import what you use
- ✅ **Type safety**: Each function has explicit return types
- ✅ **Tree shaking**: Better for bundling
- ✅ **Simplified testing**: Mock individual functions easily

## Connection Management

The database connection is managed through a singleton pattern in `connection.ts`:

```typescript
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

const queryClient = postgres(process.env.DATABASE_URL!);
export const db = drizzle(queryClient, { schema });
```

## Key Changes from Previous Architecture

1. **Consolidated Schema**: All tables and types in single `schema.ts` file
2. **Individual Functions**: No more object-based exports
3. **Simplified Directory**: `src/db/` instead of `src/database/`
4. **Absolute Imports**: Uses `@/db/...` imports throughout
5. **Type-First**: Drizzle inferred types instead of Zod schemas
6. **Advisor Focused**: Renamed from "AI Agents" to "Advisors"
