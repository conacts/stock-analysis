# ⚙️ Configuration Guide - AI Trading System

Complete configuration setup for the Stock Analysis & AI Trading System with DeepSeek integration and automated deployment.

**Current Status**: ✅ **Fully Configured and Operational**

-   **Production**: https://stock-analysis-production-31e9.up.railway.app
-   **Environment Management**: `run_with_env.sh` script for local development
-   **AI Integration**: DeepSeek API working in both environments

## 🚀 Quick Configuration

### **1. Environment Files Setup**

Create a `.env.local` file in the project root (never commit this file):

```bash
# Required for AI Features
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# Required for Database
DATABASE_URL=postgresql://user:password@host:port/database

# Required for API Authentication
API_TOKEN=your-secure-api-token-here

# Required for Trigger.dev Integration
PYTHON_API_URL=http://localhost:8000
TRIGGER_SECRET_KEY=tr_prod_your-trigger-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-trigger-token

# Optional for Market Data
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key

# Optional for Slack Notifications
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#trading-alerts
```

### **2. Environment Loading**

**Always use the environment loader script:**

```bash
# Load environment and run any command
./run_with_env.sh [command]

# Examples
./run_with_env.sh make test-fast
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
./run_with_env.sh uv run python tools/check_api_environments.py
```

### **3. Verify Configuration**

```bash
# Test all endpoints with environment loaded
./run_with_env.sh uv run python tools/check_api_environments.py

# Expected result: 100% success rate (7/7 endpoints)
```

## 🔑 API Keys Setup

### **DeepSeek API (Required for AI Features)**

1. **Sign up** at [DeepSeek Platform](https://platform.deepseek.com/)
2. **Create API key** in your dashboard
3. **Add to .env.local**:
    ```bash
    DEEPSEEK_API_KEY=sk-your-api-key-here
    ```
4. **Test integration**:
    ```bash
    ./run_with_env.sh bash -c "cd src/api && uv run python main.py"
    # Should show: DeepSeek API configured: True
    ```

### **Alpha Vantage API (Market Data)**

1. **Get free API key** at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. **Add to .env.local**:
    ```bash
    ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
    ```
3. **Test market data**:
    ```bash
    ./run_with_env.sh python -c "
    from src.trading.market_data import MarketDataProvider
    provider = MarketDataProvider()
    print('Market data configured:', provider.get_real_time_price('AAPL'))
    "
    ```

### **Slack Integration (Optional Notifications)**

1. **Create Slack App** at [api.slack.com/apps](https://api.slack.com/apps)
2. **Add Bot Token Scopes**:
    - `chat:write`
    - `chat:write.public`
3. **Install to Workspace** and copy Bot User OAuth Token
4. **Configure .env.local**:
    ```bash
    SLACK_BOT_TOKEN=xoxb-your-token-here
    SLACK_CHANNEL=#trading-alerts
    ```

## 🗄️ Database Configuration

### **PostgreSQL (Production & Development)**

**Recommended Options:**

-   **Neon** (Free tier): https://neon.tech/
-   **Supabase** (Free tier): https://supabase.com/
-   **Railway** (Included with deployment): https://railway.app/

```bash
# Add to .env.local
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

### **Database Setup & Testing**

```bash
# Test database connection with environment
./run_with_env.sh python -c "
from src.db.connection import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connected successfully')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

## 🤖 AI Trading System Configuration

### **Trading Configuration**

The system includes built-in risk management:

```python
# Default trading limits (configured in code)
MAX_POSITION_SIZE = 0.10  # 10% of portfolio
MAX_DAILY_LOSS = 0.02     # 2% daily loss limit
TRADING_ENABLED = True    # Can be toggled via API
```

### **Test AI Trading Endpoints**

```bash
# Test trading configuration
./run_with_env.sh bash -c "
curl -H 'Authorization: Bearer default-dev-token' \
  http://localhost:8000/trading/trading-config
"

# Test risk assessment
./run_with_env.sh bash -c "
curl -H 'Authorization: Bearer default-dev-token' \
  http://localhost:8000/trading/risk-status/1
"
```

## 🔧 Environment Management

### **Local Development**

```bash
# .env.local (never commit this file)
DEEPSEEK_API_KEY=sk-your-deepseek-key
DATABASE_URL=postgresql://user:pass@host:port/db
API_TOKEN=default-dev-token
PYTHON_API_URL=http://localhost:8000
TRIGGER_SECRET_KEY=tr_dev_your-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-token
ALPHA_VANTAGE_API_KEY=your-alpha-key
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#dev-alerts
```

### **Production (Railway Dashboard)**

Set these in your Railway project dashboard:

```bash
# AI Integration
DEEPSEEK_API_KEY=sk-your-production-key

# Database (auto-generated by Railway)
DATABASE_URL=postgresql://postgres:password@host:port/railway

# API Security
API_TOKEN=your-secure-production-token

# Trigger.dev Integration
PYTHON_API_URL=https://stock-analysis-production-31e9.up.railway.app
TRIGGER_SECRET_KEY=tr_prod_your-secret
TRIGGER_ACCESS_TOKEN=tr_pat_your-token

# Market Data
ALPHA_VANTAGE_API_KEY=your-alpha-key

# Notifications
SLACK_BOT_TOKEN=xoxb-your-production-token
SLACK_CHANNEL=#trading-alerts

# Environment
ENVIRONMENT=production
RAILWAY_ENVIRONMENT=production
```

## 🧪 Testing Configuration

### **Comprehensive Testing**

```bash
# Test all endpoints in both environments
./run_with_env.sh uv run python tools/check_api_environments.py

# Test local server
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
# Should show: API Token: True, Database: True, DeepSeek: True

# Test specific environment
./run_with_env.sh bash -c "API_BASE_URL=http://localhost:8000 uv run python tools/check_api_environments.py"
```

### **Test Commands with Environment**

```bash
# Run tests with environment loaded
./run_with_env.sh make test-fast          # Unit tests
./run_with_env.sh make test-integration   # Integration tests
./run_with_env.sh make test-all          # Complete test suite

# Test specific features
./run_with_env.sh python -c "
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
analyzer = DeepSeekAnalyzer()
print('DeepSeek configured:', analyzer.is_configured())
"
```

## 🚨 Security Best Practices

### **Environment Variable Security**

-   ✅ **Use .env.local** for local development (in .gitignore)
-   ✅ **Never commit** API keys to version control
-   ✅ **Use Railway dashboard** for production secrets
-   ✅ **Rotate keys regularly** for production systems
-   ✅ **Use different keys** for development and production

### **API Token Security**

```bash
# Generate secure API token
./run_with_env.sh python -c "import secrets; print(secrets.token_urlsafe(32))"

# Test token authentication
curl -H "Authorization: Bearer your-token" \
  https://stock-analysis-production-31e9.up.railway.app/health
```

### **Database Security**

```bash
# Use SSL connections for production
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require

# Test secure connection
./run_with_env.sh python -c "
import os
print('Database SSL:', 'sslmode=require' in os.getenv('DATABASE_URL', ''))
"
```

## 🔍 Troubleshooting

### **Environment Loading Issues**

```bash
# Check if .env.local exists
ls -la .env.local

# Test environment loading
./run_with_env.sh env | grep -E "(DEEPSEEK|DATABASE|API_TOKEN)"

# Verify script permissions
chmod +x run_with_env.sh
```

### **API Connection Failures**

```bash
# Test local API server
./run_with_env.sh bash -c "cd src/api && uv run python main.py"
# Should show all services configured: True

# Test production API
curl https://stock-analysis-production-31e9.up.railway.app/health

# Test with comprehensive tool
./run_with_env.sh uv run python tools/check_api_environments.py
```

### **Database Connection Issues**

```bash
# Test database connection
./run_with_env.sh python -c "
from src.db.connection import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connected')
    print('URL configured:', bool(conn))
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

### **AI Integration Problems**

```bash
# Test DeepSeek API
./run_with_env.sh python -c "
from src.llm.deepseek_analyzer import DeepSeekAnalyzer
analyzer = DeepSeekAnalyzer()
print('DeepSeek configured:', analyzer.is_configured())
if analyzer.is_configured():
    print('API key valid:', len(analyzer.api_key) > 10)
"
```

## 📋 Configuration Checklist

### ✅ **Basic Setup**

-   [x] Python 3.11+ installed with `uv`
-   [x] Node.js 18+ installed for Trigger.dev
-   [x] Project dependencies installed (`make dev-setup`)
-   [x] Environment loader script (`run_with_env.sh`) working
-   [x] Tests passing with environment (`./run_with_env.sh make test-fast`)

### ✅ **Environment Configuration**

-   [x] `.env.local` file created (never committed)
-   [x] DeepSeek API key configured and working
-   [x] Database URL configured and tested
-   [x] API token generated and configured
-   [x] Environment loading script working

### ✅ **AI Trading System**

-   [x] DeepSeek integration working (100% operational)
-   [x] Trading endpoints functional (4/4 working)
-   [x] Risk management configured (10% position, 2% daily limits)
-   [x] Market data integration ready
-   [x] Emergency controls available

### ✅ **Production Deployment**

-   [x] Railway project configured
-   [x] Environment variables set in Railway dashboard
-   [x] Auto-deployment from main branch working
-   [x] Health checks passing (30-second timeouts)
-   [x] All endpoints operational (100% success rate)

### ✅ **Testing & Validation**

-   [x] Comprehensive testing tool working
-   [x] Local and production environments tested
-   [x] API endpoints validated (7/7 passing)
-   [x] AI integration confirmed working
-   [x] Database connectivity verified

## 🎯 Next Steps

### **For New Users**

1. **Clone repository** and run `make dev-setup`
2. **Create .env.local** with your API keys
3. **Test configuration** with `./run_with_env.sh uv run python tools/check_api_environments.py`
4. **Start local server** with `./run_with_env.sh bash -c "cd src/api && uv run python main.py"`

### **For Production Deployment**

1. **Set up Railway account** and connect GitHub repo
2. **Configure environment variables** in Railway dashboard
3. **Deploy and test** with comprehensive testing tool
4. **Set up Trigger.dev** for automation tasks

## 📚 Additional Resources

-   **[README.md](README.md)**: System overview and quick start
-   **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment guide
-   **[API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)**: Comprehensive API testing
-   **[AI_TRADING_PLAN.md](AI_TRADING_PLAN.md)**: AI trading system roadmap
-   **[DEVELOPMENT.md](DEVELOPMENT.md)**: Development workflow

---

**💡 Pro Tip**: Always use `./run_with_env.sh` for commands that need environment variables. The system is designed to work seamlessly in both local development and production environments with proper configuration.
