#!/usr/bin/env python3
"""
Run the Stock Analysis API Server
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import uvicorn

from api.main import app


def main():
    """Run the API server"""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")  # nosec B104

    print("🚀 Starting Stock Analysis API Server")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📖 Docs: http://{host}:{port}/docs")
    print(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Check required environment variables
    required_vars = ["DATABASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")

    optional_vars = ["DEEPSEEK_API_KEY", "API_TOKEN"]
    missing_optional = [var for var in optional_vars if not os.getenv(var)]

    if missing_optional:
        print(f"ℹ️  Optional variables not set: {', '.join(missing_optional)}")

    print("-" * 60)

    # Run the server
    uvicorn.run(app, host=host, port=port, reload=os.getenv("ENVIRONMENT") == "development", log_level="info")


if __name__ == "__main__":
    main()
