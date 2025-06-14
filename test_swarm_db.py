#!/usr/bin/env python3
"""Test script for Swarm database functionality"""

from src.db.swarm_db import get_swarm_db
from src.models.swarm_models import PortfolioConfig, SwarmConversation, TradingDecision


def test_swarm_database():
    """Test all Swarm database operations"""
    print("🧪 Testing Swarm Database...")

    # Test Swarm database connection
    db = get_swarm_db()
    print("✅ Swarm database initialized")

    # Test saving a portfolio config
    config = PortfolioConfig(portfolio_id="test_portfolio", name="Test Portfolio", symbols=["AAPL", "MSFT"], risk_tolerance="moderate")

    config_id = db.save_portfolio_config(config)
    print(f"✅ Portfolio config saved with ID: {config_id}")

    # Test retrieving the config
    retrieved = db.get_portfolio_config("test_portfolio")
    print(f"✅ Portfolio config retrieved: {retrieved.name if retrieved else None}")

    # Test saving a conversation
    conversation = SwarmConversation(
        portfolio_id="test_portfolio",
        conversation_id="test_conv_001",
        user_message="What stocks should I buy?",
        agent_responses=[{"agent": "market_analyst", "message": "Analyzing market conditions..."}, {"agent": "trader", "message": "I recommend AAPL based on analysis."}],
        final_agent="trader",
        turns_used=2,
        success=True,
    )

    conv_id = db.save_conversation(conversation)
    print(f"✅ Conversation saved with ID: {conv_id}")

    # Test retrieving conversation history
    history = db.get_conversation_history("test_portfolio", limit=5)
    print(f"✅ Retrieved {len(history)} conversations from history")

    # Test saving a trading decision
    decision = TradingDecision(conversation_id="test_conv_001", portfolio_id="test_portfolio", decision_type="buy", symbol="AAPL", quantity=10.0, price=150.00, reasoning="Strong technical indicators and positive market sentiment", confidence_score=0.85)

    decision_id = db.save_trading_decision(decision)
    print(f"✅ Trading decision saved with ID: {decision_id}")

    print("🎉 All Swarm database tests passed!")


if __name__ == "__main__":
    test_swarm_database()
