# AI Trading System

A TypeScript-based AI trading analysis system using OpenAI Agents SDK with automated Trigger.dev workflows for intelligent market analysis.

## Overview

This system provides AI-powered market analysis through specialized trading agents that can analyze market conditions, assess risk, and provide trading insights. Built with type safety and modular architecture as core principles.

## Key Features

- **AI Agents**: OpenAI Agents SDK integration for specialized trading analysis
- **Type-Safe Architecture**: Comprehensive TypeScript types for all trading data
- **Automated Workflows**: Trigger.dev scheduling for market analysis tasks
- **Database Integration**: PostgreSQL with Drizzle ORM for data persistence
- **Configuration Management**: Centralized config system for all settings

## Quick Start

### Prerequisites

- Node.js 18+
- PostgreSQL database
- OpenAI API key
- Trigger.dev account

### Setup

1. **Install dependencies:**

```bash
npm install
```

2. **Environment variables:**

```bash
DATABASE_URL=your_postgres_connection_string
OPENAI_API_KEY=your_openai_api_key
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

## Project Structure

```
src/
├── agents/          # AI trading agents
├── config/          # Configuration management
├── db/              # Database layer
├── types/           # TypeScript type definitions
├── workflows/       # Trigger.dev workflows
└── utils/           # Shared utilities
```

## Development Status

Currently building the foundational architecture with focus on:

- Base agent framework
- Type system organization
- Configuration management
- Workflow orchestration

---

**Built with TypeScript, OpenAI Agents SDK, PostgreSQL, and Trigger.dev**
