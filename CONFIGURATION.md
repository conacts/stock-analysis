# 🔧 Configuration Guide

## 🎯 Overview

This simplified AI stock analysis system requires minimal configuration for **Trigger.dev automation**, **DeepSeek AI integration**, and **type-safe database operations** with Drizzle ORM.

## 📋 Required Environment Variables

### Core Configuration

Create a `.env` file in the project root:

```bash
# Required for AI analysis
DEEPSEEK_API_KEY=sk-your-deepseek-api-key

# Required for automation
TRIGGER_SECRET_KEY=tr_prod_your-trigger-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-trigger-token

# Required for database (SQLite)
DATABASE_URL=file:./database.db

# Optional for notifications
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#your-channel
```

## 🗄️ Database Configuration

### Drizzle ORM Setup

The system uses **Drizzle ORM** with individual function exports for type-safe database operations:

```typescript
// src/db/connection.ts
import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';

const sqlite = new Database(process.env.DATABASE_URL!);
export const db = drizzle(sqlite);
```

### Database Operations Structure

```
src/db/
├── schema.ts              # All table definitions & TypeScript types
├── connection.ts          # Database connection setup
├── migrate.ts            # Migration runner
├── advisors.ts           # getAllAdvisors(), createAdvisor(), etc.
├── portfolios.ts         # getAllPortfolios(), getPortfolioById(), etc.
├── performance.ts        # getPerformanceByAdvisor(), etc.
└── utils.ts              # testDatabaseConnection(), getTableCounts()
```

### Migration Setup

```bash
# Run database migrations
npm run db:migrate

# Generate new migration
npm run db:generate

# Reset database (development only)
npm run db:reset
```

## 🔑 API Key Setup

### 1. DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Create account and generate API key
3. Add to `.env` as `DEEPSEEK_API_KEY`

### 2. Trigger.dev Setup

1. Visit [Trigger.dev](https://trigger.dev/)
2. Create project and get access token
3. Add `TRIGGER_ACCESS_TOKEN` to `.env`
4. Set `TRIGGER_SECRET_KEY` for webhooks

### 3. Slack (Optional)

1. Create Slack app and get bot token
2. Add to `.env` as `SLACK_BOT_TOKEN`
3. Set target channel with `SLACK_CHANNEL`

## 🚀 Deployment Configuration

### Development

```bash
# Install dependencies
npm install

# Run database migrations
npm run db:migrate

# Start development server
npx trigger.dev@latest dev
```

### Production

```bash
# Build the project
npm run build

# Deploy to Trigger.dev
npx trigger.dev@latest deploy
```

## 📁 Configuration Files

### `.env.example`

Template file showing required variables:

```bash
# AI Configuration
DEEPSEEK_API_KEY=sk-your-key-here

# Trigger.dev Configuration
TRIGGER_ACCESS_TOKEN=tr_pat_your-token
TRIGGER_SECRET_KEY=tr_prod_your-secret

# Database Configuration
DATABASE_URL=file:./database.db

# Optional Notifications
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL=#trading-alerts
```

### `trigger.config.ts`

Trigger.dev project configuration:

```typescript
import { defineConfig } from '@trigger.dev/sdk/v3';

export default defineConfig({
  project: 'your-project-id',
  logLevel: 'info',
  retries: {
    enabledInDev: false,
    default: {
      maxAttempts: 3,
      minTimeoutInMs: 1000,
      maxTimeoutInMs: 10000,
    },
  },
});
```

### `drizzle.config.ts`

Database configuration for Drizzle ORM:

```typescript
import type { Config } from 'drizzle-kit';

export default {
  schema: './src/db/schema.ts',
  out: './src/db/migrations',
  driver: 'better-sqlite',
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
} satisfies Config;
```

## 🔧 TypeScript Configuration

### Path Aliases

Configured in `tsconfig.json` for clean imports:

```json
{
  "compilerOptions": {
    "baseUrl": "src",
    "paths": {
      "@/*": ["*"],
      "@/db/*": ["db/*"],
      "@/automation/*": ["automation/*"],
      "@/clients/*": ["clients/*"]
    }
  }
}
```

### Usage Examples

```typescript
// Import database functions directly
import { getAllAdvisors, createAdvisor } from '@/db/advisors';
import { getAllPortfolios } from '@/db/portfolios';
import { testDatabaseConnection } from '@/db/utils';

// Import types from schema
import type { AdvisorSelect, AdvisorInsert } from '@/db/schema';

// Use in your code
const advisors = await getAllAdvisors();
const newAdvisor: AdvisorInsert = {
  name: 'New Advisor',
  systemPrompt: 'You are a trading advisor',
  model: 'deepseek/r1',
  temperature: 0.1,
  status: 'active',
};
```

## 🔍 Validation

### Test Configuration

```bash
# Check TypeScript configuration
npm run type-check

# Test database connection
npm run db:test

# Run all tests
npm test

# Test tasks locally
npx trigger.dev@latest dev
```

### Database Health Check

```typescript
// Import and use the health check
import { testDatabaseConnection, getTableCounts } from '@/db/utils';

// Test database connectivity
const isConnected = await testDatabaseConnection();
console.log('Database connected:', isConnected);

// Get table statistics
const counts = await getTableCounts();
console.log('Table counts:', counts);
```

### Verify API Keys

The system will validate API keys on startup and log any issues:

```typescript
// Environment validation happens automatically
import { config } from '@/utils/config';

// This will throw if required keys are missing
const deepseekKey = config.DEEPSEEK_API_KEY;
const triggerToken = config.TRIGGER_ACCESS_TOKEN;
```

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Database File**

   - Error: `Database file not found`
   - Solution: Run `npm run db:migrate` to create database

2. **DeepSeek API Key Invalid**

   - Error: `DeepSeek API key not found or invalid`
   - Solution: Check `.env` has valid `DEEPSEEK_API_KEY`

3. **Trigger.dev Authentication Failed**

   - Error: `Unauthorized`
   - Solution: Verify `TRIGGER_ACCESS_TOKEN` is correct

4. **Database Type Errors**

   - Error: TypeScript compilation errors
   - Solution: Run `npm run db:generate` to update types

5. **Task Not Running**
   - Check Trigger.dev dashboard for errors
   - Verify environment variables are set
   - Check task logs for specific errors

### Debug Mode

Set log level to debug in `trigger.config.ts`:

```typescript
export default defineConfig({
  logLevel: 'debug',
  // ... other config
});
```

### Database Debugging

```bash
# Check database schema
npm run db:studio

# View database directly
sqlite3 database.db ".schema"

# Check migrations status
npm run db:check
```

## 📊 Monitoring

### Health Checks

The system includes automatic health monitoring with individual functions:

```typescript
import { testDatabaseConnection } from '@/db/utils';
import { getAllAdvisors } from '@/db/advisors';

// Database connectivity
const dbHealth = await testDatabaseConnection();

// Data availability
const advisors = await getAllAdvisors();
const hasData = advisors.length > 0;
```

### Performance Monitoring

```typescript
// Monitor individual function performance
import { performance } from 'perf_hooks';

const start = performance.now();
const portfolios = await getAllPortfolios();
const duration = performance.now() - start;

console.log(`getAllPortfolios took ${duration}ms`);
```

### Logs

View logs in multiple places:

1. **Local Development**: Terminal output
2. **Trigger.dev Dashboard**: Task execution logs
3. **Database Logs**: SQLite query logs (if enabled)

## 🔄 Migration from Previous Setup

### Key Changes

- **Individual Functions**: Import specific functions instead of object methods
- **Drizzle ORM**: Type-safe database operations with auto-completion
- **Consolidated Schema**: All types in single `src/db/schema.ts` file
- **Absolute Imports**: Clean `@/db/...` import paths

### Migration Benefits

- ✅ **Better Type Safety**: Full TypeScript support with Drizzle
- ✅ **Faster Development**: Auto-completion and IntelliSense
- ✅ **Explicit Dependencies**: Import only what you use
- ✅ **Better Performance**: Optimized database operations

---

_Configuration is now focused on type-safe database operations and AI integration!_
