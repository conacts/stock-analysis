# ⚙️ Configuration Guide

Complete configuration setup for the Stock Analysis System with automation.

## 🚀 Quick Configuration

### 1. Environment Files

Create a `.env` file in the project root:

```bash
# AI Features (Optional but Recommended)
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# Slack Notifications (Optional)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_USER_ID=@your-username

# Database (Optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/stockdb

# API Authentication (For Automation)
API_TOKEN=your-secure-api-token-here
PYTHON_API_URL=http://localhost:8000
```

### 2. Trigger.dev Dashboard Configuration

Set these environment variables in your [Trigger.dev dashboard](https://cloud.trigger.dev/):

**Required:**

-   `PYTHON_API_URL` - Your FastAPI server URL
-   `API_TOKEN` - Secure token for API authentication

**Optional:**

-   `DEEPSEEK_API_KEY` - For AI-powered analysis
-   `DATABASE_URL` - For enhanced data storage

## 🔑 API Keys Setup

### DeepSeek API (AI Features)

1. **Sign up** at [DeepSeek](https://platform.deepseek.com/)
2. **Create API key** in your dashboard
3. **Add to environment**:
    ```bash
    export DEEPSEEK_API_KEY="your-api-key-here"
    ```
4. **Test integration**:
    ```bash
    make test-llm
    ```

### Slack Integration (Notifications)

1. **Create Slack App** at [api.slack.com/apps](https://api.slack.com/apps)
2. **Add Bot Token Scopes**:
    - `chat:write`
    - `chat:write.public`
3. **Install to Workspace** and copy Bot User OAuth Token
4. **Configure environment**:
    ```bash
    export SLACK_BOT_TOKEN="xoxb-your-token-here"
    export SLACK_USER_ID="@your-username"
    ```
5. **Test alerts**:
    ```bash
    uv run alert_manager.py test
    ```

## 🗄️ Database Configuration

### SQLite (Default - No Setup Required)

```bash
DATABASE_URL=sqlite:///data/stock_analysis.db
```

### PostgreSQL (Production Recommended)

```bash
# Local PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/stockdb

# Cloud PostgreSQL (e.g., Supabase, Neon)
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
```

### Database Setup

```bash
# Initialize database
make db-setup

# Run migrations
make db-migrate

# Verify connection
python -c "from src.db.connection import get_db_connection; print('✅ Database connected')"
```

## 🤖 Automation Configuration

### Trigger.dev Setup

1. **Create Account** at [trigger.dev](https://trigger.dev/)
2. **Create Project** and note your project ID
3. **Deploy Tasks**:
    ```bash
    bunx trigger.dev@latest deploy
    ```
4. **Set Environment Variables** in dashboard:
    - `PYTHON_API_URL=http://your-api-server.com`
    - `API_TOKEN=your-secure-token`
    - `DEEPSEEK_API_KEY=your-deepseek-key`

### FastAPI Server Configuration

```bash
# Start API server
make run-api

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Interactive documentation
```

## 🔧 Development vs Production

### Development Configuration

```bash
# .env (local development)
DEEPSEEK_API_KEY=your-dev-key
SLACK_BOT_TOKEN=xoxb-dev-token
DATABASE_URL=sqlite:///data/stock_analysis.db
API_TOKEN=mock-api-token-12345
PYTHON_API_URL=http://localhost:8000
```

### Production Configuration

```bash
# Trigger.dev Dashboard (production)
PYTHON_API_URL=https://your-api-server.com
API_TOKEN=secure-production-token
DEEPSEEK_API_KEY=your-production-key
DATABASE_URL=postgresql://user:pass@prod-host:5432/db
```

## 🧪 Testing Configuration

### Mock Values for Testing

```bash
export API_TOKEN="mock-api-token-12345"
export PYTHON_API_URL="http://localhost:8000"
export DEEPSEEK_API_KEY="mock-deepseek-key-67890"
export DATABASE_URL="sqlite:///data/test_stock_analysis.db"
```

### Test Commands

```bash
# Test with mock environment
make test-fast

# Test with real APIs (requires keys)
make test-integration

# Test LLM features (requires DEEPSEEK_API_KEY)
make test-llm
```

## 🚨 Security Best Practices

### API Key Management

-   **Never commit** API keys to version control
-   **Use environment variables** for all sensitive data
-   **Rotate keys regularly** for production systems
-   **Use different keys** for development and production

### Environment Validation

The system uses fail-fast validation:

```typescript
// Missing required variables will cause immediate failure
❌ Missing environment variables: PYTHON_API_URL, API_TOKEN
```

### Secure Token Generation

```bash
# Generate secure API token
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🔍 Troubleshooting

### Common Configuration Issues

**Environment Variables Not Loading:**

```bash
# Check if .env file exists
ls -la .env

# Verify variables are set
echo $DEEPSEEK_API_KEY
```

**API Connection Failures:**

```bash
# Test API server connectivity
curl -f http://localhost:8000/health || echo "API server not running"

# Check Trigger.dev environment variables
# Visit: https://cloud.trigger.dev/ → Your Project → Environment Variables
```

**Database Connection Issues:**

```bash
# Test database connection
python -c "
from src.db.connection import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connected successfully')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

**Slack Integration Problems:**

```bash
# Test Slack configuration
uv run alert_manager.py test

# Check bot permissions in Slack workspace
# Ensure bot has 'chat:write' scope
```

### Validation Commands

```bash
# Validate complete configuration
make validate-config

# Check specific components
make check-api          # API server health
make check-db           # Database connectivity
make check-slack        # Slack integration
make check-automation   # Trigger.dev tasks
```

## 📋 Configuration Checklist

### ✅ Basic Setup

-   [ ] Python 3.11+ installed with `uv`
-   [ ] Node.js 18+ installed with `bun`
-   [ ] Project dependencies installed (`make dev-setup`)
-   [ ] Tests passing (`make test-fast`)

### ✅ API Keys (Optional)

-   [ ] DeepSeek API key configured
-   [ ] Slack bot token configured
-   [ ] API authentication token generated

### ✅ Database (Optional)

-   [ ] Database URL configured
-   [ ] Database connection tested
-   [ ] Migrations applied

### ✅ Automation (Optional)

-   [ ] Trigger.dev account created
-   [ ] Environment variables set in dashboard
-   [ ] Tasks deployed successfully
-   [ ] Health checks passing

### ✅ Production Ready

-   [ ] Secure tokens generated
-   [ ] Production database configured
-   [ ] API server deployed
-   [ ] Monitoring configured

## 📚 Additional Resources

-   **[Main README](README.md)**: System overview and quick start
-   **[Development Guide](DEVELOPMENT.md)**: Development workflow
-   **[Automation Guide](src/automation/README.md)**: Trigger.dev setup
-   **[Slack Setup Guide](src/alerts/README.md)**: Detailed Slack configuration

---

**💡 Pro Tip**: Start with the basic configuration and add optional features incrementally. The system works great with just the default SQLite database and mock API keys for development.
