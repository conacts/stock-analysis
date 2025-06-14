#!/bin/bash
# Trigger.dev Production Testing Mode
# Runs tasks locally but points to Railway production API

echo "🚀 Starting Trigger.dev in PRODUCTION TEST mode"
echo "📍 API URL: https://stock-analysis-production-31e9.up.railway.app"
echo "🔧 Environment: Production Testing"
echo ""

# Set production environment
export PYTHON_API_URL=https://stock-analysis-production-31e9.up.railway.app
export NODE_ENV=production

# Start Trigger.dev in dev mode but with production API
./run_with_env.sh npx trigger.dev@latest dev --env-file .env.local

echo ""
echo "🛑 Trigger.dev production test session ended"
