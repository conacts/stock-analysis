#!/usr/bin/env python3
"""
Helper script to update Trigger.dev environment variables with Railway URL
Run this after Railway deployment is successful
"""

import os
import sys


def main():
    """Display instructions for updating Trigger.dev environment variables"""
    railway_url = input("Enter your Railway deployment URL (e.g., https://your-app.railway.app): ").strip()

    if not railway_url:
        print("❌ Railway URL is required")
        sys.exit(1)

    if not railway_url.startswith("https://"):
        print("❌ Railway URL must start with https://")
        sys.exit(1)

    # Remove trailing slash if present
    railway_url = railway_url.rstrip("/")

    print("\n🔧 Update your Trigger.dev environment variables:")
    print("=" * 60)
    print(f"PYTHON_API_URL={railway_url}")
    print(f"API_TOKEN={os.getenv('API_TOKEN', 'default-dev-token')}")
    print("=" * 60)
    print("\n📋 Steps:")
    print("1. Go to your Trigger.dev project settings")
    print("2. Update the PYTHON_API_URL environment variable")
    print("3. Redeploy your Trigger.dev project")
    print(f"4. Test the connection: curl {railway_url}/health")
    print("\n✅ Your Railway API is now ready for Trigger.dev integration!")


if __name__ == "__main__":
    main()
