# 🛠️ Development Guide

## 🎯 Overview

This guide covers development for the **simplified AI stock analysis system** built with TypeScript and Trigger.dev.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

```bash
# Clone and install
git clone <repository>
cd stock-analysis
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start development
npx trigger.dev@latest dev
```

## 🏗️ Architecture

### Core Structure

```
src/
├── automation/tasks/           # Trigger.dev tasks
│   ├── ai-trading-analysis.ts  # Main AI analysis task
│   └── health-check.ts         # System monitoring
├── clients/                    # API clients
│   ├── deepseek.ts            # DeepSeek AI client
│   └── alpaca.ts              # Alpaca trading client
├── database/                   # Data models
│   ├── models.ts              # Database models
│   └── connection.ts          # Database connection
├── types/                      # TypeScript types
└── utils/                      # Utilities
```

## 🤖 AI Task Development

### Main Analysis Task

Located in `src/automation/tasks/ai-trading-analysis.ts`:

```typescript
export const aiTradingAnalysis = task({
  id: 'ai-trading-analysis',
  run: async (payload: { symbols: string[] }) => {
    // DeepSeek AI analysis
    const analysis = await analyzeMarket(payload.symbols);

    // Return insights
    return {
      recommendations: analysis.recommendations,
      risks: analysis.risks,
      confidence: analysis.confidence,
    };
  },
});
```

### Adding New Tasks

1. Create new file in `src/automation/tasks/`
2. Export task with unique ID
3. Add to `src/automation/tasks/index.ts`
4. Test with `npx trigger.dev@latest dev`

## 🧪 Testing

### TypeScript Tests

```bash
# Run all tests
npm test

# Run specific test
npm test -- config.test.ts

# Watch mode
npm test -- --watch
```

### Manual Testing

```bash
# Start development server
npx trigger.dev@latest dev

# Test specific task
# Use Trigger.dev dashboard to trigger tasks manually
```

## 🔄 CI/CD Pipeline

### GitHub Actions

Located in `.github/workflows/ci.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test
      - name: Build
        run: npm run build
```

### Deployment

- **Development**: Auto-deploy on push to `develop` branch
- **Production**: Auto-deploy on push to `main` branch
- **Target**: Trigger.dev cloud platform

## 📝 Code Standards

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### Linting & Formatting

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format
```

## 🔧 Environment Management

### Development Environment

```bash
# .env for local development
DEEPSEEK_API_KEY=sk-your-dev-key
TRIGGER_ACCESS_TOKEN=tr_pat_your-dev-token
TRIGGER_SECRET_KEY=tr_dev_your-secret
SLACK_BOT_TOKEN=xoxb-your-dev-token
SLACK_CHANNEL=#dev-alerts
```

### Production Environment

Set in Trigger.dev dashboard:

- `DEEPSEEK_API_KEY`
- `TRIGGER_ACCESS_TOKEN`
- `TRIGGER_SECRET_KEY`
- `SLACK_BOT_TOKEN`
- `SLACK_CHANNEL`

## 🔍 Debugging

### Local Development

```bash
# Start with debug logs
npx trigger.dev@latest dev --log-level debug

# Check task execution
# View logs in terminal and Trigger.dev dashboard
```

### Common Issues

1. **Task not triggering**: Check environment variables
2. **DeepSeek API errors**: Verify API key and quota
3. **Build failures**: Check TypeScript compilation

## 📊 Monitoring

### Task Performance

- Monitor execution time in Trigger.dev dashboard
- Set up alerts for task failures
- Track AI API usage and costs

### Health Checks

The `health-check.ts` task monitors:

- API connectivity
- Task execution status
- Error rates

## 🚀 Deployment Workflow

### Development

1. Create feature branch
2. Implement changes
3. Test locally with `npx trigger.dev@latest dev`
4. Run tests: `npm test`
5. Push to trigger CI/CD

### Production

1. Merge to `main` branch
2. CI/CD runs tests and builds
3. Auto-deploy to Trigger.dev
4. Monitor deployment in dashboard

## 📚 Resources

### Documentation

- [Trigger.dev Docs](https://trigger.dev/docs)
- [DeepSeek API Docs](https://platform.deepseek.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Tools

- **IDE**: VS Code with TypeScript extension
- **Testing**: Vitest
- **Linting**: ESLint + Prettier
- **Deployment**: Trigger.dev

---

_Development is now streamlined - focus on AI task logic, not infrastructure!_
