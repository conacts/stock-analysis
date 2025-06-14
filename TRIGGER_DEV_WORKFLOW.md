# 🚀 Trigger.dev Development Workflow

This guide outlines the recommended workflow for developing and deploying Trigger.dev automation tasks.

## 📋 Environment Strategy

### **Development Workflow (Recommended)**

**Use Local Development Mode**: `npx trigger.dev@latest dev`

**Why this is perfect for development**:

-   ✅ Tasks run locally on your machine (easy debugging)
-   ✅ Scheduling handled by Trigger.dev cloud
-   ✅ Hot reload when you save files
-   ✅ Full access to debuggers and breakpoints
-   ✅ Same build system as production
-   ✅ No deployment needed for testing

### **Production Deployment**

**Use Production Environment**: `npm run trigger:deploy:prod`

**When to deploy to production**:

-   ✅ After thorough local testing
-   ✅ When ready for live automation
-   ✅ For scheduled tasks that need to run 24/7

## 🎉 **Plan Upgrade Complete!**

✅ **Trigger.dev plan upgraded** - All scheduled tasks now available
✅ **12+ scheduled tasks** can now run simultaneously
✅ **No schedule limits** for development and production
✅ **Full AI trading automation** ready to deploy

## 🔧 Development Setup

### **1. Start Local Development**

```bash
# Start Trigger.dev in development mode
npx trigger.dev@latest dev

# This will:
# - Build your tasks locally
# - Connect to Trigger.dev cloud for scheduling
# - Watch for file changes and hot reload
# - Allow debugging with breakpoints
```

### **2. Test Your Tasks**

```bash
# In another terminal, test your API
./run_with_env.sh bash -c "cd src/api && uv run python main.py"

# Test API endpoints
./run_with_env.sh uv run python tools/check_api_environments.py
```

### **3. Trigger Tasks for Testing**

You can trigger tasks from your local API or directly from the Trigger.dev dashboard while in dev mode.

## 🎯 Current Task Status - **All Available!**

### **Available Tasks (12+ scheduled tasks)**

1. **Simple Health Check** (`simple-health-check`)

    - Basic environment validation
    - Perfect for testing the setup

2. **Manual Test** (`manual-test`)

    - Accepts custom payload
    - Good for debugging

3. **Enhanced Portfolio Analysis** (`enhanced-daily-portfolio-analysis`)

    - Full AI-powered portfolio analysis
    - Includes conversation history

4. **Risk Monitoring** (`portfolio-risk-monitor`)

    - Real-time risk assessment
    - Context-aware alerts

5. **Market Event Response** (`market-event-response-trigger`)

    - Event-driven market analysis
    - Historical pattern recognition

6. **Simplified Enhanced Analysis** (`simplified-enhanced-analysis`)

    - Streamlined AI analysis
    - Daily at 9:50 AM

7. **Daily Portfolio Analysis** (`daily-portfolio-analysis`)

    - Comprehensive daily analysis
    - Daily at 8 AM

8. **Weekly Portfolio Analysis** (`weekly-portfolio-analysis`)

    - Weekly performance review
    - Sundays at 10 AM

9. **End of Day Summary** (`end-of-day-portfolio-summary`)

    - Market close analysis
    - Daily at 4:30 PM

10. **System Health Check** (`system-health-check`)

    - Every 15 minutes
    - System monitoring

11. **Daily Health Summary** (`daily-health-summary`)

    - Daily at 6 AM
    - Health reports

12. **Weekly Health Analysis** (`weekly-health-analysis`)
    - Weekly on Sundays
    - Comprehensive health review

**Plus Stock Alert Tasks**:

-   Continuous price monitoring (every 5 minutes)
-   After-hours alert setup (daily 4 PM)
-   Pre-market review (daily 8:30 AM)
-   Weekly alert cleanup (Sundays)

### **Task Testing Commands**

```bash
# Test simple health check
curl -X POST http://localhost:3000/api/trigger/simple-health-check

# Test manual task with payload
curl -X POST http://localhost:3000/api/trigger/manual-test \
  -H "Content-Type: application/json" \
  -d '{"message": "Testing from development"}'
```

## 🚀 Production Deployment Process

### **When Ready for Production**

1. **Ensure Local Testing is Complete**

    ```bash
    # All tasks working in dev mode
    # API integration tested
    # No errors in local development
    ```

2. **Set Up Environment Variables**

    Go to your Trigger.dev dashboard and set these environment variables for production:

    ```bash
    # Required for AI features
    DEEPSEEK_API_KEY=sk-your-production-key

    # Required for database
    DATABASE_URL=postgresql://your-production-db-url

    # Required for API integration
    PYTHON_API_URL=https://stock-analysis-production-31e9.up.railway.app
    API_TOKEN=your-secure-production-token

    # Optional for enhanced features
    ALPHA_VANTAGE_API_KEY=your-alpha-key
    SLACK_BOT_TOKEN=xoxb-your-production-token
    SLACK_CHANNEL=#trading-alerts
    ```

3. **Deploy to Production**

    ```bash
    npm run trigger:deploy:prod
    ```

4. **Verify Production Deployment**

    ```bash
    # Check deployment status
    npx trigger.dev@latest whoami

    # Test production API integration
    API_BASE_URL=https://stock-analysis-production-31e9.up.railway.app \
    ./run_with_env.sh uv run python tools/check_api_environments.py
    ```

## 🔍 Troubleshooting Development Issues

### **Common Development Issues**

1. **Tasks Not Appearing in Dashboard**

    ```bash
    # Check if dev mode is running
    npx trigger.dev@latest dev

    # Verify task syntax
    npx trigger.dev@latest deploy --dry-run
    ```

2. **API Connection Issues**

    ```bash
    # Ensure local API is running
    ./run_with_env.sh bash -c "cd src/api && uv run python main.py"

    # Check environment variables
    ./run_with_env.sh env | grep -E "(DEEPSEEK|DATABASE|API_TOKEN)"
    ```

3. **Environment Variable Issues**
    ```bash
    # Verify .env.local exists and is loaded
    ls -la .env.local
    ./run_with_env.sh python -c "import os; print('API URL:', os.getenv('PYTHON_API_URL'))"
    ```

### **Production Deployment Issues**

1. **ServiceValidationError**

    - Usually means missing environment variables
    - Check Trigger.dev dashboard environment variables
    - Ensure all required variables are set

2. **Task Execution Failures**
    - Check Trigger.dev dashboard logs
    - Verify API endpoints are accessible
    - Confirm database connectivity

## 📊 Development vs Production Comparison

| Feature         | Development Mode     | Production Deployment    |
| --------------- | -------------------- | ------------------------ |
| **Execution**   | Local machine        | Trigger.dev cloud        |
| **Debugging**   | Full debugger access | Log-based debugging      |
| **Hot Reload**  | ✅ Automatic         | ❌ Requires redeployment |
| **Environment** | Local .env.local     | Trigger.dev dashboard    |
| **Scheduling**  | Trigger.dev cloud    | Trigger.dev cloud        |
| **Scaling**     | Single instance      | Auto-scaling             |
| **Reliability** | Development only     | Production-grade         |

## 🎯 Recommended Workflow

### **Daily Development**

1. **Start Development Environment**

    ```bash
    # Terminal 1: Start Trigger.dev dev mode
    npx trigger.dev@latest dev

    # Terminal 2: Start local API
    ./run_with_env.sh bash -c "cd src/api && uv run python main.py"
    ```

2. **Develop and Test**

    - Edit task files in `src/automation/tasks/`
    - Test via Trigger.dev dashboard or API calls
    - Debug with breakpoints and console logs
    - Iterate quickly with hot reload

3. **Validate Before Production**

    ```bash
    # Run comprehensive tests
    ./run_with_env.sh make test-all

    # Test API integration
    ./run_with_env.sh uv run python tools/check_api_environments.py

    # Dry run deployment
    npx trigger.dev@latest deploy --dry-run
    ```

### **Production Release**

1. **Final Testing**

    - All tasks working in development
    - API integration confirmed
    - Environment variables configured

2. **Deploy**

    ```bash
    npm run trigger:deploy:prod
    ```

3. **Monitor**
    - Check Trigger.dev dashboard
    - Monitor task execution logs
    - Verify scheduled tasks are running

## 📚 Additional Resources

-   **[Trigger.dev Documentation](https://trigger.dev/docs)**
-   **[Local Development Guide](https://trigger.dev/docs/development/cli-dev-command)**
-   **[Environment Variables](https://trigger.dev/docs/deployment/environment-variables)**
-   **[Task Writing Guide](https://trigger.dev/docs/writing-tasks/overview)**

---

**💡 Key Takeaway**: Use local development mode (`npx trigger.dev@latest dev`) for all development work. Only deploy to production when you're ready for live automation. This gives you the best development experience with full debugging capabilities while ensuring production reliability.
