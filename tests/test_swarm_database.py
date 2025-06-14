"""Test swarm database functionality with proper test isolation"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.models.swarm_models import PortfolioConfig, SwarmConversation, TradingDecision


class TestSwarmDatabase:
    """Test swarm database operations with mocked connections"""

    @pytest.fixture
    def mock_swarm_db(self):
        """Mock swarm database for testing"""
        with patch("src.db.swarm_db.SwarmDatabase") as mock_db_class:
            mock_db = MagicMock()
            mock_db_class.return_value = mock_db

            # Mock connection methods
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_db.get_connection.return_value = mock_conn

            yield mock_db

    @pytest.mark.unit
    def test_save_portfolio_config(self, mock_swarm_db):
        """Test saving portfolio configuration"""
        # Arrange
        mock_swarm_db.save_portfolio_config.return_value = 123
        config = PortfolioConfig(portfolio_id="test_portfolio", name="Test Portfolio", symbols=["AAPL", "MSFT"], risk_tolerance="moderate")

        # Act
        config_id = mock_swarm_db.save_portfolio_config(config)

        # Assert
        assert config_id == 123
        mock_swarm_db.save_portfolio_config.assert_called_once_with(config)

    @pytest.mark.unit
    def test_get_portfolio_config(self, mock_swarm_db):
        """Test retrieving portfolio configuration"""
        # Arrange
        expected_config = PortfolioConfig(portfolio_id="test_portfolio", name="Test Portfolio", symbols=["AAPL", "MSFT"], risk_tolerance="moderate")
        mock_swarm_db.get_portfolio_config.return_value = expected_config

        # Act
        config = mock_swarm_db.get_portfolio_config("test_portfolio")

        # Assert
        assert config == expected_config
        mock_swarm_db.get_portfolio_config.assert_called_once_with("test_portfolio")

    @pytest.mark.unit
    def test_save_conversation(self, mock_swarm_db):
        """Test saving swarm conversation"""
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
        conv_id = mock_swarm_db.save_conversation(conversation)

        # Assert
        assert conv_id == 456
        mock_swarm_db.save_conversation.assert_called_once_with(conversation)

    @pytest.mark.unit
    def test_get_conversation_history(self, mock_swarm_db):
        """Test retrieving conversation history"""
        # Arrange
        expected_conversations = [SwarmConversation(portfolio_id="test_portfolio", conversation_id="test_conv_001", user_message="What stocks should I buy?", agent_responses=[{"agent": "trader", "message": "Buy AAPL"}], final_agent="trader", turns_used=1, success=True)]
        mock_swarm_db.get_conversation_history.return_value = expected_conversations

        # Act
        history = mock_swarm_db.get_conversation_history("test_portfolio", limit=5)

        # Assert
        assert len(history) == 1
        assert history[0].portfolio_id == "test_portfolio"
        mock_swarm_db.get_conversation_history.assert_called_once_with("test_portfolio", limit=5)

    @pytest.mark.unit
    def test_save_trading_decision(self, mock_swarm_db):
        """Test saving trading decision"""
        # Arrange
        mock_swarm_db.save_trading_decision.return_value = 789
        decision = TradingDecision(conversation_id="test_conv_001", portfolio_id="test_portfolio", decision_type="buy", symbol="AAPL", quantity=10.0, price=150.0, reasoning="Strong technical indicators and positive market sentiment", confidence_score=0.85)

        # Act
        decision_id = mock_swarm_db.save_trading_decision(decision)

        # Assert
        assert decision_id == 789
        mock_swarm_db.save_trading_decision.assert_called_once_with(decision)

    @pytest.mark.integration
    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"})
    def test_swarm_database_integration_with_sqlite(self):
        """Integration test with in-memory SQLite database"""
        # This test would need the SwarmDatabase to support SQLite
        # For now, we'll skip it until we implement SQLite support
        pytest.skip("SwarmDatabase SQLite support not yet implemented")

    @pytest.mark.unit
    def test_swarm_database_initialization_error(self):
        """Test swarm database initialization with missing DATABASE_URL"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.db.swarm_db.SwarmDatabase") as mock_db_class:
                mock_db_class.side_effect = ValueError("DATABASE_URL environment variable is required")

                with pytest.raises(ValueError, match="DATABASE_URL environment variable is required"):
                    from src.db.swarm_db import SwarmDatabase

                    SwarmDatabase()
