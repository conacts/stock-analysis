# 🚀 AI Trading System

A TypeScript-based AI trading system that uses DeepSeek for market analysis and Alpaca for market data. The system features automated portfolio analysis with configurable AI agents and scheduled market monitoring.

[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Trigger.dev](https://img.shields.io/badge/Trigger.dev-v3-purple.svg)](https://trigger.dev/)

## ✨ Key Features

### 🤖 **AI-Powered Analysis**

- **DeepSeek AI Integration**: Advanced market analysis with configurable AI agents
- **Custom System Prompts**: Each portfolio can use different AI strategies
- **Automated Analysis**: Scheduled market opening analysis every weekday
- **Flexible Storage**: JSONB-based analysis result storage

### 🔄 **Automated Portfolio Management**

- **Multi-Agent System**: Different AI agents for different trading strategies
- **Portfolio-Agent Association**: Each portfolio linked to specific AI agent
- **Market Opening Coordination**: Automated analysis when markets open
- **Status Tracking**: Portfolio and agent status management

### 📊 **Real-Time Market Data**

- **Alpaca Markets Integration**: Live market data and trading capabilities
- **Market Status Monitoring**: Automatic market open/close detection
- **Symbol Analysis**: Individual stock analysis with AI insights
- **Health Monitoring**: Comprehensive system health checks

### 🏗️ **Modern Architecture**

- **TypeScript-Only**: Clean, type-safe codebase
- **Trigger.dev v3**: Scheduled task automation and workflow orchestration
- **PostgreSQL**: Robust data storage with JSONB for flexible data
- **Zod Validation**: Runtime type validation and schema enforcement

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- PostgreSQL database
- Alpaca Markets API account
- DeepSeek API account
- Trigger.dev account

### Installation

1. **Clone and install dependencies:**

```bash
git clone <repository-url>
cd ai-trading-system
npm install
```

2. **Environment Setup:**
   Create `.env.local` with your API keys:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Alpaca Markets API
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # or live API

# DeepSeek AI API
DEEPSEEK_API_KEY=your_deepseek_api_key

# Trigger.dev
TRIGGER_SECRET_KEY=your_trigger_secret_key
```

3. **Database Setup:**

```bash
# Run database migrations
npm run db:migrate:latest

# Inspect database structure
npm run db:inspect
```

4. **Development:**

```bash
# Build the project
npm run build

# Start Trigger.dev development server
npm run trigger:dev

# Run tests
npm test
```

## 📊 System Workflow

### Market Opening Analysis

Every weekday at 9:30 AM ET (market open), the system:

1. **Checks Market Status** - Verifies markets are open via Alpaca API
2. **Fetches Active Portfolios** - Gets all portfolios with `status = 'active'`
3. **Agent Assignment** - Each portfolio uses its assigned AI agent
4. **Analysis Coordination** - Triggers individual portfolio analysis tasks

### AI Agent System

- **Configurable Prompts** - Each agent has a custom system prompt for different strategies
- **Model Settings** - Temperature, max tokens, and model selection per agent
- **Strategy Specialization** - Growth-focused, conservative, sector-specific agents

### Analysis Storage

Results are stored in `analysis_results` with:

- **Portfolio Context** - Links to specific portfolio and agent
- **Analysis Type** - Market opening, daily check, manual analysis
- **Flexible Data** - JSONB storage for complex analysis results
- **Recommendations** - Structured trading recommendations

## 🛠️ Available Scripts

### Development

- `npm run build` - Compile TypeScript
- `npm run dev` - Development server with hot reload
- `npm test` - Run test suite
- `npm run type-check` - TypeScript type checking

### Database

- `npm run db:migrate <file>` - Run specific migration
- `npm run db:migrate:latest` - Run latest migration
- `npm run db:inspect` - Inspect database structure

### Trigger.dev

- `npm run trigger:dev` - Development server
- `npm run trigger:deploy` - Deploy to production
- `npm run trigger:whoami` - Check authentication

### Code Quality

- `npm run format` - Format code with Prettier
- `npm run lint` - Run ESLint (currently disabled)
- `npm run ci` - Full CI pipeline

## 📈 Current Tasks

### Active Trigger.dev Tasks

1. **`market-opening-analysis`** - Scheduled weekday market open coordinator
2. **`ai-trading-analysis`** - Individual stock analysis with DeepSeek
3. **`health-check`** - System health monitoring
4. **`alpaca-health-check`** - Alpaca API connectivity check
5. **`deepseek-health-check`** - DeepSeek API connectivity check

### Task Schedule

- **Market Opening Analysis**: `30 13 * * 1-5` (9:30 AM ET weekdays)
- **Health Checks**: Various intervals for system monitoring

## 🔧 Configuration

### AI Agent Configuration

Create custom AI agents with different trading strategies:

```sql
INSERT INTO ai_agents (name, system_prompt, model, temperature) VALUES (
    'Growth Investor',
    'You are a growth-focused investment advisor. Prioritize companies with strong revenue growth, innovative products, and expanding markets. Focus on technology, healthcare, and emerging sectors.',
    'deepseek-chat',
    0.1
);
```

### Portfolio Setup

Link portfolios to specific AI agents:

```sql
INSERT INTO portfolios (name, description, agent_id, status) VALUES (
    'Tech Growth Portfolio',
    'High-growth technology stocks',
    1,  -- Growth Investor agent
    'active'
);
```

## 🏛️ Database Schema

### Core Tables

#### AI Agents

```sql
CREATE TABLE ai_agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    system_prompt TEXT NOT NULL,
    model VARCHAR(50) DEFAULT 'deepseek-chat',
    temperature DECIMAL(3,2) DEFAULT 0.1,
    max_tokens INTEGER DEFAULT 2000,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Portfolios

```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    agent_id INTEGER REFERENCES ai_agents(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Analysis Results

```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    symbol VARCHAR(20),
    analysis_data JSONB,
    recommendations JSONB,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Key Features

- **Agent-Portfolio Association** - Each portfolio can use a different AI agent
- **Flexible Analysis Storage** - JSONB fields for storing complex analysis data
- **Status Tracking** - Portfolio and agent status management
- **Audit Trail** - Timestamps and status tracking for all operations

## 🏗️ Architecture

```
ai-trading-system/
├── src/
│   ├── automation/
│   │   └── tasks/                    # Trigger.dev automation tasks
│   │       ├── market-opening-analysis.ts
│   │       ├── ai-trading-analysis.ts
│   │       └── health-check.ts
│   ├── clients/                      # API clients
│   │   ├── alpaca.ts                 # Alpaca Markets API
│   │   └── deepseek.ts               # DeepSeek AI API
│   ├── database/                     # Database layer
│   │   ├── connection.ts             # Database connection
│   │   ├── models.ts                 # Zod schemas and types
│   │   ├── migrate.ts                # Migration runner
│   │   └── migrations/               # SQL migration files
│   └── utils/
│       └── config.ts                 # Environment configuration
├── tests/                            # Test suite
├── trigger.config.ts                 # Trigger.dev configuration
└── package.json                      # Dependencies and scripts
```

## 🔄 Migration History

- **004_core_portfolio_and_agents.sql** - Core schema with AI agents and simplified portfolio structure

## 🚧 Development Status

### ✅ Completed

- TypeScript-only architecture
- Trigger.dev v3 integration
- Database migration system
- Core AI agent and portfolio models
- Market opening analysis framework
- Health monitoring tasks
- Alpaca Markets integration
- DeepSeek AI integration

### 🔄 In Progress

- Individual portfolio analysis tasks
- AI agent prompt optimization
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
2. Use Zod for all data validation
3. Write tests for new functionality
4. Update documentation for schema changes
5. Use conventional commit messages

## 📄 License

MIT License - see LICENSE file for details
