# 🌍 Deployment Environments

This document outlines the two-environment deployment strategy for the AI Trading System.

## 📋 Environment Overview

The system operates with **two environments only**:

1. **Development** - Local development and testing
2. **Production** - Live deployment on Railway

**Note**: There is no staging environment. Changes are tested locally in development, then deployed directly to production.

## 🔧 Trigger.dev Environment Mapping

**Important**: Trigger.dev only supports two environment names: `staging` and `prod`. We map these to our conceptual environments:

| Our Environment | Trigger.dev Environment | Purpose                               |
| --------------- | ----------------------- | ------------------------------------- |
| **Development** | `staging`               | Local development, testing, debugging |
| **Production**  | `prod`                  | Live system serving real users        |

**Why this works perfectly**:

-   ✅ Trigger.dev's `staging` environment is perfect for development work
-   ✅ Trigger.dev's `prod` environment matches our production needs
-   ✅ No confusion with multiple staging environments
-   ✅ Clear separation between development and production

## 🔧 Environment Configuration

### Development Environment

**Location**: Local machine
**Purpose**: Development, testing, and debugging
**API URL**: `http://localhost:8000`
**Database**: Local PostgreSQL or development database
**Trigger.dev**: Staging environment (used for development)

**Environment Variables (.env.local)**:

```bash
# Core Configuration
ENVIRONMENT=development
API_TOKEN=default-dev-token
DATABASE_URL=postgresql://user:pass@localhost:5432/stockanalysis_dev

# AI Integration
DEEPSEEK_API_KEY=sk-your-dev-key

# Trigger.dev Development
PYTHON_API_URL=http://localhost:8000
TRIGGER_SECRET_KEY=tr_dev_your-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-dev-token

# Optional Services
ALPHA_VANTAGE_API_KEY=your-alpha-key
SLACK_BOT_TOKEN=xoxb-your-dev-token
SLACK_CHANNEL=#dev-alerts
```

### Production Environment

**Location**: Railway cloud platform
**Purpose**: Live system serving real users
**API URL**: `https://stock-analysis-production-31e9.up.railway.app`
**Database**: Railway PostgreSQL
**Trigger.dev**: Production environment

**Environment Variables (Railway Dashboard)**:

```bash
# Core Configuration
ENVIRONMENT=production
RAILWAY_ENVIRONMENT=production
API_TOKEN=your-secure-production-token
DATABASE_URL=postgresql://postgres:password@host:port/railway

# AI Integration
DEEPSEEK_API_KEY=sk-your-production-key

# Trigger.dev Production
PYTHON_API_URL=https://stock-analysis-production-31e9.up.railway.app
TRIGGER_SECRET_KEY=tr_prod_your-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-production-token

# Production Services
ALPHA_VANTAGE_API_KEY=your-alpha-key
SLACK_BOT_TOKEN=xoxb-your-production-token
SLACK_CHANNEL=#trading-alerts
```

## 🚀 Deployment Workflow

### Development Workflow

1. **Local Development**:

    ```bash
    # Set up environment
    ./run_with_env.sh make dev-setup

    # Start local API server
    ./run_with_env.sh bash -c "cd src/api && uv run python main.py"

    # Test Trigger.dev tasks locally
    npx trigger.dev@latest dev
    ```

2. **Testing**:

    ```bash
    # Run comprehensive tests
    ./run_with_env.sh make test-all

    # Test API endpoints
    ./run_with_env.sh uv run python tools/check_api_environments.py
    ```

3. **Trigger.dev Development**:

    ```bash
    # Deploy to development environment
    npm run trigger:deploy:dev

    # Test development deployment
    npx trigger.dev@latest whoami
    ```

### Production Deployment

1. **Automatic Deployment**:

    ```bash
    # Push to main branch triggers automatic Railway deployment
    git push origin main
    ```

2. **Manual Trigger.dev Deployment**:

    ```bash
    # Deploy automation tasks to production
    npm run trigger:deploy:prod
    ```

3. **Verification**:

    ```bash
    # Check production health
    curl https://stock-analysis-production-31e9.up.railway.app/health

    # Test production API
    API_BASE_URL=https://stock-analysis-production-31e9.up.railway.app \
    ./run_with_env.sh uv run python tools/check_api_environments.py
    ```

## 🔄 Environment Detection

The system automatically detects the environment using these variables:

```typescript
// Environment detection logic
const isProduction =
    process.env.ENVIRONMENT === "production" ||
    process.env.NODE_ENV === "production" ||
    process.env.RAILWAY_ENVIRONMENT === "production";
```

**Environment Priority**:

1. `ENVIRONMENT` variable (explicit setting)
2. `NODE_ENV` variable (Node.js standard)
3. `RAILWAY_ENVIRONMENT` variable (Railway platform)

## 📊 Environment Differences

| Feature            | Development             | Production                                              |
| ------------------ | ----------------------- | ------------------------------------------------------- |
| **API URL**        | `http://localhost:8000` | `https://stock-analysis-production-31e9.up.railway.app` |
| **Database**       | Local/Dev PostgreSQL    | Railway PostgreSQL                                      |
| **Trigger.dev**    | Development project     | Production project                                      |
| **Logging**        | Debug level             | Info level                                              |
| **Error Handling** | Detailed stack traces   | User-friendly messages                                  |
| **Rate Limiting**  | Disabled                | Enabled                                                 |
| **SSL/TLS**        | Not required            | Required                                                |
| **Monitoring**     | Basic                   | Comprehensive                                           |

## 🛡️ Security Considerations

### Development Environment

-   Use development API keys when possible
-   Keep sensitive data in `.env.local` (never commit)
-   Use weak authentication tokens for convenience
-   Enable debug logging for troubleshooting

### Production Environment

-   Use production API keys with appropriate limits
-   Store secrets in Railway environment variables
-   Use strong, randomly generated authentication tokens
-   Disable debug logging for security
-   Enable comprehensive monitoring and alerting

## 🔧 Configuration Management

### Environment Variable Management

**Development**:

```bash
# Use .env.local file
cp .env.example .env.local
# Edit .env.local with your development values
```

**Production**:

```bash
# Set via Railway CLI
railway variables set DEEPSEEK_API_KEY=sk-your-production-key

# Or via Railway Dashboard
# Go to your project → Variables tab → Add variables
```

### Database Management

**Development**:

```bash
# Use local PostgreSQL or development database
# Run migrations manually if needed
./run_with_env.sh python -c "from src.db.database import create_tables; create_tables()"
```

**Production**:

```bash
# Railway automatically provisions PostgreSQL
# Migrations run automatically on deployment
# Monitor via Railway dashboard
```

## 📈 Monitoring and Observability

### Development Monitoring

-   Local logs via console output
-   Manual testing with API tools
-   Trigger.dev development dashboard
-   Local database inspection

### Production Monitoring

-   Railway application logs
-   Health check endpoints (`/health`, `/healthz`)
-   Trigger.dev production dashboard
-   Database monitoring via Railway
-   Slack notifications for critical issues

## 🚨 Troubleshooting

### Common Environment Issues

1. **Wrong Environment Detection**:

    ```bash
    # Check environment variables
    echo $ENVIRONMENT
    echo $NODE_ENV
    echo $RAILWAY_ENVIRONMENT
    ```

2. **API URL Mismatch**:

    ```bash
    # Verify PYTHON_API_URL setting
    ./run_with_env.sh python -c "import os; print('API URL:', os.getenv('PYTHON_API_URL'))"
    ```

3. **Database Connection Issues**:

    ```bash
    # Test database connectivity
    ./run_with_env.sh python -c "from src.db.connection import get_db_connection; get_db_connection()"
    ```

4. **Trigger.dev Environment Confusion**:

    ```bash
    # Check current Trigger.dev environment
    npx trigger.dev@latest whoami

    # Switch environments if needed
    npm run trigger:deploy:dev    # For development
    npm run trigger:deploy:prod   # For production
    ```

### Environment Switching

**From Development to Production Testing**:

```bash
# Test production API from local environment
export PYTHON_API_URL=https://stock-analysis-production-31e9.up.railway.app
./run_with_env.sh uv run python tools/check_api_environments.py
```

**From Production back to Development**:

```bash
# Reset to local development
unset PYTHON_API_URL
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
```

## 📚 Related Documentation

-   **[CONFIGURATION.md](CONFIGURATION.md)**: Detailed configuration guide
-   **[DEPLOYMENT.md](DEPLOYMENT.md)**: Railway deployment specifics
-   **[DEVELOPMENT.md](DEVELOPMENT.md)**: Development workflow
-   **[README.md](README.md)**: System overview

---

**💡 Key Takeaway**: The two-environment approach keeps things simple while ensuring proper separation between development and production. Always test thoroughly in development before pushing to production, as there's no intermediate staging environment.
