# 🔧 Configuration Guide

## 🎯 Overview

This simplified AI stock analysis system requires minimal configuration for **Trigger.dev automation** and **DeepSeek AI integration**.

## 📋 Required Environment Variables

### Core Configuration

Create a `.env` file in the project root:

```bash
# Required for AI analysis
DEEPSEEK_API_KEY=sk-your-deepseek-api-key

# Required for automation
TRIGGER_SECRET_KEY=tr_prod_your-trigger-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-trigger-token

# Optional for notifications
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#your-channel
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
# Start development server
npx trigger.dev@latest dev
```

### Production

```bash
# Deploy to Trigger.dev
npx trigger.dev@latest deploy
```

## 📁 Configuration Files

### `.env.example`

Template file showing required variables:

```bash
DEEPSEEK_API_KEY=sk-your-key-here
TRIGGER_ACCESS_TOKEN=tr_pat_your-token
TRIGGER_SECRET_KEY=tr_prod_your-secret
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

## 🔍 Validation

### Test Configuration

```bash
# Check TypeScript configuration
npm run type-check

# Test tasks locally
npx trigger.dev@latest dev
```

### Verify API Keys

The system will validate API keys on startup and log any issues.

## 🛠️ Troubleshooting

### Common Issues

1. **Missing DeepSeek API Key**

   - Error: `DeepSeek API key not found`
   - Solution: Add valid `DEEPSEEK_API_KEY` to `.env`

2. **Trigger.dev Authentication Failed**

   - Error: `Unauthorized`
   - Solution: Check `TRIGGER_ACCESS_TOKEN` is valid

3. **Task Not Running**
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

## 📊 Monitoring

### Health Checks

The system includes automatic health monitoring:

- Task execution status
- API connectivity checks
- Error rate monitoring

### Logs

View logs in Trigger.dev dashboard:

1. Visit your Trigger.dev project
2. Navigate to "Runs" tab
3. Click on specific task runs for detailed logs

---

_Configuration is now dramatically simplified - just AI API keys and Trigger.dev setup!_
