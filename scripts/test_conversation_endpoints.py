#!/usr/bin/env python3
"""
Test script for enhanced conversation history endpoints
"""

import os
from datetime import datetime

import requests

# Configuration
RAILWAY_URL = os.getenv("RAILWAY_URL", "https://stock-analysis-production-31e9.up.railway.app")
API_TOKEN = os.getenv("API_TOKEN", "default-dev-token")


def test_conversation_endpoints():
    """Test all conversation endpoints"""
    print("🧠 Testing Enhanced Conversation History Endpoints")
    print(f"API URL: {RAILWAY_URL}")
    print("=" * 60)

    # Test conversation context
    print("Testing conversation context...")
    url = f"{RAILWAY_URL}/trading/swarm/conversation-context/1"
    headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
    data = {"days_back": 7, "include_market_context": True, "include_trading_decisions": True}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Context endpoint working! Thread ID: {result.get('thread_id')}")
        else:
            print(f"❌ Context endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Context endpoint failed: {e}")

    # Test store conversation
    print("\nTesting store conversation...")
    url = f"{RAILWAY_URL}/trading/swarm/store-conversation-thread/1"
    data = {
        "thread_id": f'test-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
        "conversation_type": "analysis",
        "ai_responses": [{"role": "assistant", "content": "Test response", "agent": "market_analyst"}],
        "actions_taken": [{"action_type": "analysis", "symbol": "AAPL"}],
        "trigger_source": "test_script",
        "metadata": {"test": True},
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Store endpoint working! Conversation ID: {result.get('conversation_id')}")
        else:
            print(f"❌ Store endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Store endpoint failed: {e}")


if __name__ == "__main__":
    test_conversation_endpoints()
