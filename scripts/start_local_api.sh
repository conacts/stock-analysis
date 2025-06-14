#!/bin/bash
# Start local API server for development

echo "🚀 Starting local Stock Analysis API server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API docs at: http://localhost:8000/docs"
echo "🔍 Health check at: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"

# Set development environment
export ENVIRONMENT=development

# Start the server
uv run python src/api/main.py
