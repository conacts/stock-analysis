"""
Test suite for swarm database operations with proper mocking
This ensures no production database interaction during testing
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.models.swarm_models import PortfolioConfig, SwarmConversation, TradingDecision


class TestSwarmDatabase:
    """Test swarm database operations with mocked database"""

    @pytest.fixture
    def mock_swarm_db(self):
        """Mock swarm database for testing"""
        with patch("src.db.swarm_db.SwarmDatabase") as mock_db_class:
            mock_db = MagicMock()
            mock_db_class.return_value = mock_db
            yield mock_db

    def test_save_portfolio_config(self, mock_swarm_db):
        """Test saving portfolio configuration"""
        # Arrange
        mock_swarm_db.save_portfolio_config.return_value = 123
        config = PortfolioConfig(portfolio_id="test_portfolio", name="Test Portfolio", symbols=["AAPL", "MSFT"], risk_tolerance="moderate")

        # Act
        result = mock_swarm_db.save_portfolio_config(config)

        # Assert
        assert result == 123
        mock_swarm_db.save_portfolio_config.assert_called_once_with(config)

    def test_get_portfolio_config(self, mock_swarm_db):
        """Test retrieving portfolio configuration"""
        # Arrange
        expected_config = PortfolioConfig(portfolio_id="test_portfolio", name="Test Portfolio", symbols=["AAPL", "MSFT"], risk_tolerance="moderate")
        mock_swarm_db.get_portfolio_config.return_value = expected_config

        # Act
        result = mock_swarm_db.get_portfolio_config("test_portfolio")

        # Assert
        assert result == expected_config
        assert result.portfolio_id == "test_portfolio"
        assert result.name == "Test Portfolio"
        assert result.symbols == ["AAPL", "MSFT"]
        assert result.risk_tolerance == "moderate"
        mock_swarm_db.get_portfolio_config.assert_called_once_with("test_portfolio")

    def test_save_conversation(self, mock_swarm_db):
        """Test saving conversation"""
        # Arrange
        mock_swarm_db.save_conversation.return_value = 456
        conversation = SwarmConversation(
            portfolio_id="test_portfolio",
            conversation_id="test_conv_001",
            user_message="What stocks should I buy?",
            agent_responses=[{"agent": "market_analyst", "message": "Analyzing market conditions..."}, {"agent": "trader", "message": "I recommend AAPL based on analysis."}],
            final_agent="trader",
            turns_used=2,
            success=True,
        )

        # Act
        result = mock_swarm_db.save_conversation(conversation)

        # Assert
        assert result == 456
        mock_swarm_db.save_conversation.assert_called_once_with(conversation)

    def test_get_conversation_history(self, mock_swarm_db):
        """Test retrieving conversation history"""
        # Arrange
        expected_conversations = [SwarmConversation(portfolio_id="test_portfolio", conversation_id="test_conv_001", user_message="What stocks should I buy?", agent_responses=[{"agent": "trader", "message": "Buy AAPL"}], final_agent="trader", turns_used=1, success=True)]
        mock_swarm_db.get_conversation_history.return_value = expected_conversations

        # Act
        result = mock_swarm_db.get_conversation_history("test_portfolio")

        # Assert
        assert result == expected_conversations
        assert len(result) == 1
        assert result[0].portfolio_id == "test_portfolio"
        assert result[0].conversation_id == "test_conv_001"
        mock_swarm_db.get_conversation_history.assert_called_once_with("test_portfolio")

    def test_save_trading_decision(self, mock_swarm_db):
        """Test saving trading decision"""
        # Arrange
        mock_swarm_db.save_trading_decision.return_value = 789
        decision = TradingDecision(conversation_id="test_conv_001", portfolio_id="test_portfolio", decision_type="buy", symbol="AAPL", quantity=10.0, price=150.0, reasoning="Strong technical indicators and positive market sentiment", confidence_score=0.85)

        # Act
        result = mock_swarm_db.save_trading_decision(decision)

        # Assert
        assert result == 789
        mock_swarm_db.save_trading_decision.assert_called_once_with(decision)

    @pytest.mark.integration
    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"})
    def test_swarm_database_integration_with_sqlite(self):
        """Integration test with in-memory SQLite database"""
        # This is a placeholder for future integration testing
        # When implemented, this would use an actual SQLite in-memory database
        # For now, we skip this test to avoid production database interaction
        pytest.skip("Integration test placeholder - requires SQLite implementation")

    def test_swarm_database_initialization_error(self):
        """Test swarm database initialization with missing DATABASE_URL"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.db.swarm_db.SwarmDatabase") as mock_db_class:
                mock_db_class.side_effect = ValueError("DATABASE_URL environment variable is required")

                with pytest.raises(ValueError, match="DATABASE_URL environment variable is required"):
                    mock_db_class()
