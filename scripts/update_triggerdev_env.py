#!/usr/bin/env python3
"""
Helper script to update Trigger.dev environment variables.

This script helps update environment variables in Trigger.dev, particularly
useful for fixing the PYTHON_API_URL after Railway deployment.

Usage:
    python scripts/update_triggerdev_env.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """Update Trigger.dev environment variables."""
    print("🔧 Trigger.dev Environment Variable Update Helper")
    print("=" * 50)

    # Current Railway URL (without port)
    railway_url = "https://stock-analysis-production-31e9.up.railway.app"

    print(f"✅ Current Railway API URL: {railway_url}")
    print(f"✅ Health endpoint: {railway_url}/health")

    print("\n📋 Environment Variables to Update in Trigger.dev:")
    print("-" * 50)
    print(f"PYTHON_API_URL = {railway_url}")
    print("API_TOKEN = [your API token]")
    print("DATABASE_URL = [your Neon PostgreSQL URL]")
    print("DEEPSEEK_API_KEY = [your DeepSeek API key]")
    print("SLACK_BOT_TOKEN = [your Slack bot token]")
    print("SLACK_USER_ID = [your Slack user ID]")

    print("\n🔗 Update Instructions:")
    print("-" * 50)
    print("1. Go to your Trigger.dev dashboard")
    print("2. Navigate to your project settings")
    print("3. Update the environment variables listed above")
    print("4. Make sure PYTHON_API_URL does NOT include :8000 port")
    print("5. Redeploy your Trigger.dev tasks")

    print(f"\n✅ The correct PYTHON_API_URL is: {railway_url}")
    print("❌ Do NOT use: https://stock-analysis-production-31e9.up.railway.app:8000")

    # Test the API endpoint
    print("\n🧪 Testing API endpoint...")
    try:
        import requests

        response = requests.get(f"{railway_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API endpoint is accessible")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Database: {health_data.get('database', 'unknown')}")
            print(f"   LLM: {health_data.get('llm', 'unknown')}")
        else:
            print(f"❌ API endpoint returned status {response.status_code}")
    except ImportError:
        print("⚠️  requests not available - install with: uv add requests")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

    print("\n🎯 Next Steps:")
    print("-" * 50)
    print("1. Update PYTHON_API_URL in Trigger.dev to remove :8000")
    print("2. Test your Trigger.dev tasks")
    print("3. Monitor the logs for successful API calls")


if __name__ == "__main__":
    main()
