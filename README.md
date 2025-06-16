# AI Trading System

A TypeScript-based AI stock analysis system using DeepSeek AI with automated Trigger.dev workflows.

## Features

- **AI Analysis**: DeepSeek AI integration for market analysis
- **Database**: PostgreSQL with Drizzle ORM
- **Automation**: Trigger.dev for scheduled tasks
- **Type Safety**: Full TypeScript support

## Quick Start

### Prerequisites

- Node.js 18+
- PostgreSQL database
- DeepSeek API key
- Trigger.dev account

### Setup

1. **Install dependencies:**

```bash
npm install
```

2. **Environment variables:**
   Create `.env` file:

```bash
DATABASE_URL=your_postgres_connection_string
DEEPSEEK_API_KEY=your_deepseek_api_key
TRIGGER_SECRET_KEY=your_trigger_secret
```

3. **Database setup:**

```bash
npm run db:migrate
npm run db:health
```

4. **Development:**

```bash
npm run build
npm run trigger:dev
```

## Available Scripts

### Development

- `npm run build` - Compile TypeScript
- `npm test` - Run tests
- `npm run type-check` - Type checking

### Database

- `npm run db:migrate` - Run migrations
- `npm run db:studio` - Open Drizzle Studio
- `npm run db:health` - Test connection

### Trigger.dev

- `npm run trigger:dev` - Development server
- `npm run trigger:deploy` - Deploy tasks

### Code Quality

- `npm run format` - Format with Prettier
- `npm run ci` - Full CI pipeline

## Architecture

```
src/
├── automation/       # Trigger.dev tasks
├── clients/          # API clients
├── db/              # Database layer
├── types/           # TypeScript types
└── utils/           # Utilities
```

## Database

The system uses PostgreSQL with Drizzle ORM for type-safe database operations. Database files are organized by function (advisors, portfolios, analysis, etc.).

---

**Built with TypeScript, PostgreSQL, and Trigger.dev**
