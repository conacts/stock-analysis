#!/bin/bash
# Trigger.dev Development Mode
# Runs tasks locally pointing to localhost API

echo "🧪 Starting Trigger.dev in DEVELOPMENT mode"
echo "📍 API URL: http://localhost:8000"
echo "🔧 Environment: Local Development"
echo ""

# Set development environment
export PYTHON_API_URL=http://localhost:8000
export NODE_ENV=development

# Start Trigger.dev in dev mode
./run_with_env.sh npx trigger.dev@latest dev --env-file .env.local

echo ""
echo "🛑 Trigger.dev development session ended"
