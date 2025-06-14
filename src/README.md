# 📁 Source Code Structure

## 🎯 Simplified AI Stock Analysis System

This is the **simplified TypeScript-only** codebase focused on **Trigger.dev automation** and **DeepSeek AI integration**.

## 🏗️ Module Organization

```
src/
├── automation/tasks/       # Core functionality (Trigger.dev)
│   ├── ai-trading-analysis.ts  # DeepSeek AI analysis
│   ├── health-check.ts         # System monitoring
│   └── index.ts                # Task exports
├── clients/                # API clients
│   ├── deepseek.ts        # DeepSeek AI client
│   └── alpaca.ts          # Alpaca trading client
├── database/              # Minimal data layer
│   ├── models.ts          # Database models
│   └── connection.ts      # Database connection
├── types/                 # TypeScript types
│   └── index.ts          # Type definitions
└── utils/                 # Configuration utilities
    └── config.ts         # Environment config
```

## 🎯 Key Components

### 🤖 **Automation Tasks** (`automation/tasks/`)

**Core Value**: Direct AI analysis execution in Trigger.dev environment

- **`ai-trading-analysis.ts`**: Main DeepSeek AI market analysis
- **`health-check.ts`**: System monitoring and alerting
- **No API layers**: Direct function execution avoids timeout issues

### 🔌 **API Clients** (`clients/`)

**Purpose**: Simple, focused API integrations

- **`deepseek.ts`**: DeepSeek AI client with proper error handling
- **`alpaca.ts`**: Market data and trading client (when needed)
- **Minimal abstraction**: Direct API calls, no complex wrappers

### 🗄️ **Database** (`database/`)

**Approach**: Minimal data persistence

- **`models.ts`**: Essential data types only
- **`connection.ts`**: Simple database connection
- **No complex migrations**: Keep data handling simple

### 📝 **Types** (`types/`)

**Strategy**: Strong TypeScript typing

- **Market data types**: Stock prices, analysis results
- **Task payload types**: Trigger.dev task inputs/outputs
- **API response types**: Client response interfaces

## 🔧 Development Patterns

### Task Development

```typescript
// automation/tasks/ai-trading-analysis.ts
export const aiTradingAnalysis = task({
  id: 'ai-trading-analysis',
  run: async (payload: { symbols: string[] }) => {
    // Direct DeepSeek API call
    const analysis = await deepseekClient.analyze(payload.symbols);

    // Return structured results
    return {
      recommendations: analysis.recommendations,
      risks: analysis.risks,
      confidence: analysis.confidence,
    };
  },
});
```

### Client Usage

```typescript
// clients/deepseek.ts
export class DeepSeekClient {
  async analyze(symbols: string[]): Promise<AnalysisResult> {
    // Direct API integration
    const response = await fetch(this.apiUrl, {
      method: 'POST',
      headers: { Authorization: `Bearer ${this.apiKey}` },
      body: JSON.stringify({ symbols }),
    });

    return response.json();
  }
}
```

### Type Safety

```typescript
// types/index.ts
export interface AnalysisResult {
  symbol: string;
  recommendation: 'buy' | 'sell' | 'hold';
  confidence: number;
  reasoning: string;
  risks: string[];
}

export interface TaskPayload {
  symbols: string[];
  portfolioId?: string;
}
```

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── unit/
│   ├── config.test.ts          # Configuration tests
│   └── typescript-core.test.ts # Core TypeScript tests
└── setup.ts                    # Test configuration
```

### Testing Focus

- **Unit tests**: Core logic and utilities
- **Integration tests**: API client functionality
- **Type checking**: Comprehensive TypeScript validation
- **No complex mocking**: Simple, focused tests

## 🚀 Usage Examples

### Basic Task Execution

```typescript
// Trigger.dev will handle task execution
// No direct imports needed - tasks run in cloud environment
```

### Local Development

```bash
# Start development server
npx trigger.dev@latest dev

# Tasks appear in dashboard for manual testing
# Logs show in both terminal and web interface
```

### Configuration

```typescript
// utils/config.ts
export const config = {
  deepseek: {
    apiKey: process.env.DEEPSEEK_API_KEY!,
    baseUrl: 'https://api.deepseek.com',
  },
  trigger: {
    secretKey: process.env.TRIGGER_SECRET_KEY!,
    accessToken: process.env.TRIGGER_ACCESS_TOKEN!,
  },
};
```

## 🎯 Architecture Principles

### 🚫 What We Avoid

- ❌ **Complex API servers**: No FastAPI, Express, etc.
- ❌ **Multiple deployment platforms**: Trigger.dev only
- ❌ **Heavy database systems**: Minimal data persistence
- ❌ **Timeout-prone architectures**: Direct function execution
- ❌ **Complex abstractions**: Simple, direct code

### ✅ What We Embrace

- ✅ **Direct AI integration**: DeepSeek calls in task functions
- ✅ **TypeScript safety**: Strong typing throughout
- ✅ **Simple configuration**: Environment variables only
- ✅ **Reliable execution**: Trigger.dev handles scaling/reliability
- ✅ **Clear logging**: Comprehensive task execution logs

## 🔄 Data Flow

```
Trigger.dev Scheduler → Task Execution → DeepSeek API → Results
                            ↓              ↓           ↓
                    Type Validation    AI Analysis    Logging
                    Error Handling     Market Data    Monitoring
                    Configuration      Recommendations Alerts
```

## 🛠️ Development Workflow

### 1. Local Development

```bash
npx trigger.dev@latest dev  # Start development server
```

### 2. Task Development

- Create new task in `src/automation/tasks/`
- Add to `index.ts` exports
- Test via Trigger.dev dashboard

### 3. Deploy

```bash
npx trigger.dev@latest deploy  # Deploy to production
```

## 📈 Success Metrics

- ✅ **Zero timeout failures**: Tasks run reliably
- ✅ **Simple maintenance**: Easy to understand and modify
- ✅ **Fast development**: Quick iterations on AI logic
- ✅ **Cost effective**: Minimal infrastructure costs

---

## 💡 Key Insight

_"This architecture eliminates the complexity that defeated our original purpose. AI analysis runs directly in the cloud with proper timeouts and error handling."_

**Focus**: AI task logic, not infrastructure management.
