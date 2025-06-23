# Stock Analysis Trading System

A TypeScript-based trading system with AI agents, web scraping capabilities, and comprehensive market analysis tools.

## Features

- **AI Trading Agents**: OpenAI Agents SDK integration with conversation history
- **Firecrawl MCP Integration**: Web scraping and research capabilities via Model Context Protocol
- **Database Management**: PostgreSQL with Drizzle ORM
- **Workflow Automation**: Trigger.dev integration for scheduled tasks
- **Type Safety**: Comprehensive TypeScript types throughout

## Firecrawl MCP Integration

This system integrates the official [Firecrawl MCP Server](https://github.com/mendableai/firecrawl-mcp-server) to provide powerful web scraping and research capabilities to AI agents.

### Available Tools

The Firecrawl MCP integration provides the following tools to agents:

- **`firecrawl_scrape`**: Scrape content from individual URLs
- **`firecrawl_batch_scrape`**: Scrape multiple URLs efficiently with rate limiting
- **`firecrawl_search`**: Search the web for market news and data
- **`firecrawl_crawl`**: Crawl websites for comprehensive data gathering
- **`firecrawl_extract`**: Extract structured data from financial websites
- **`firecrawl_deep_research`**: Conduct deep research on market topics

### Configuration

Set your Firecrawl API key in your environment:

```bash
export FIRECRAWL_API_KEY=fc-your-api-key-here
```

Get your API key from [https://firecrawl.dev/app/api-keys](https://firecrawl.dev/app/api-keys)

### MCP Server Modes

The system supports three MCP server modes:

#### 1. Hosted MCP (Recommended)

Uses the remote hosted Firecrawl MCP server:

```typescript
const agent = new GeneralTradingAgent({
  enableFirecrawl: true,
  firecrawlMode: 'hosted', // Default
});
```

#### 2. Streamable HTTP

For custom server configurations:

```typescript
const agent = new GeneralTradingAgent({
  enableFirecrawl: true,
  firecrawlMode: 'streamable',
});
```

#### 3. Stdio (Local)

For local MCP server instances:

```typescript
const agent = new GeneralTradingAgent({
  enableFirecrawl: true,
  firecrawlMode: 'stdio',
});
```

### Usage Examples

#### Basic Market Analysis with Web Research

```typescript
import { GeneralTradingAgent } from '@/agents/general-trading-agent';

const agent = new GeneralTradingAgent({
  enableFirecrawl: true,
  firecrawlMode: 'hosted',
});

await agent.initializeWithHistory();
await agent.connect();

try {
  const result = await agent.analyze({
    analysisType: 'market_research',
    symbol: 'AAPL',
    parameters: {
      prompt: 'Research recent Apple earnings and provide investment analysis',
    },
  });

  console.log(result.result);
} finally {
  await agent.disconnect();
}
```

#### Market Open Workflow with News Scraping

```typescript
import { runMarketOpenWorkflow } from '@/agents/general-trading-agent';

const result = await runMarketOpenWorkflow(
  'Analyze current market conditions using recent financial news and provide trading insights'
);

console.log('Market Analysis:', result.analysis);
```

### Agent Instructions

The `GeneralTradingAgent` is pre-configured with instructions for using Firecrawl tools:

- Uses `firecrawl_search` to find recent market news and data
- Uses `firecrawl_scrape` for detailed financial website analysis
- Uses `firecrawl_extract` for structured data from earnings reports and SEC filings
- Uses `firecrawl_deep_research` for comprehensive market trend analysis

### Error Handling

The integration includes comprehensive error handling:

- Automatic retries with exponential backoff
- Rate limit management
- Credit usage monitoring
- Connection management

### Testing

Run the test suite to verify Firecrawl integration:

```bash
pnpm test
```

Tests will automatically skip Firecrawl-dependent tests if no API key is provided.

## Setup

1. **Environment Variables**

   ```bash
   cp .env.example .env.local
   # Add your API keys
   ```

2. **Database Setup**

   ```bash
   pnpm db:push
   ```

3. **Install Dependencies**

   ```bash
   pnpm install
   ```

4. **Run Tests**
   ```bash
   pnpm test
   ```

## Architecture

### Type-First Approach

- Database types are the source of truth
- Explicit TypeScript types throughout
- No index.ts files - explicit imports only

### Agent Structure

- `BaseAgent`: Abstract base class with MCP integration
- `GeneralTradingAgent`: Concrete implementation with Firecrawl
- Conversation history management
- Database persistence

### Workflow Integration

- Trigger.dev workflows for automation
- Market open analysis
- Scheduled research tasks

## Development

### Adding New Agents

```typescript
import {
  BaseAgent,
  type BaseAgentConfig,
  type AnalysisRequest,
  type AnalysisResponse,
} from '@/agents/base/base-agent';

export class MyCustomAgent extends BaseAgent {
  constructor(config?: Partial<BaseAgentConfig>) {
    super({
      name: 'MyCustomAgent',
      instructions: 'Your agent instructions here...',
      enableFirecrawl: true, // Enable web scraping
      ...config,
    });
  }

  async analyze(request: AnalysisRequest): Promise<AnalysisResponse> {
    // Your analysis logic here
  }
}
```

### Configuration Management

All configuration is centralized in `src/config/`:

- `environment.ts`: Environment variables
- `agents.ts`: Agent configurations
- `schedules.ts`: Workflow schedules

## License

MIT
