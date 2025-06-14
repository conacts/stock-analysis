"""
Tests for Slack notification system
"""

from unittest.mock import Mock, patch

import pytest
import requests

from src.alerts.slack_alerts import SlackMessage, SlackNotifier


class TestSlackNotifier:
    """Test the SlackNotifier class"""

    @pytest.fixture
    def mock_env_vars(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")
        monkeypatch.setenv("SLACK_CHANNEL", "#test-channel")

    @pytest.fixture
    def sample_analysis(self):
        """Sample stock analysis for testing"""
        return {"symbol": "AAPL", "recommendation": {"rating": "Buy", "confidence": "High", "price_target": 200.0, "suggested_allocation": "5.0%"}, "score": {"composite_score": 85.5}, "fundamentals": {"current_price": 180.0}}

    @pytest.fixture
    def mock_successful_response(self):
        """Mock successful Slack API response"""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "ts": "1234567890.123456"}
        return mock_response

    @pytest.fixture
    def mock_failed_response(self):
        """Mock failed Slack API response"""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": False, "error": "channel_not_found"}
        return mock_response

    def test_init_with_env_vars(self, mock_env_vars):
        """Test initialization with environment variables"""
        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()
            assert notifier.bot_token == "xoxb-test-token"
            assert notifier.channel == "#test-channel"

    def test_init_with_parameters(self):
        """Test initialization with direct parameters"""
        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier("xoxb-direct-token", "#direct-channel")
            assert notifier.bot_token == "xoxb-direct-token"
            assert notifier.channel == "#direct-channel"

    def test_init_missing_bot_token(self, monkeypatch):
        """Test initialization fails without bot token"""
        # Clear environment variables
        monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
        monkeypatch.delenv("SLACK_CHANNEL", raising=False)
        monkeypatch.delenv("SLACK_USER_ID", raising=False)

        with pytest.raises(ValueError, match="Slack bot token required"):
            SlackNotifier(None, "#test-channel", test_connection=False)

    def test_init_missing_channel(self, monkeypatch):
        """Test initialization fails without channel"""
        # Clear environment variables
        monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
        monkeypatch.delenv("SLACK_CHANNEL", raising=False)
        monkeypatch.delenv("SLACK_USER_ID", raising=False)

        with pytest.raises(ValueError, match="Slack channel required"):
            SlackNotifier("xoxb-test-token", None, test_connection=False)

    def test_backward_compatibility_user_id(self, monkeypatch):
        """Test backward compatibility with SLACK_USER_ID env var"""
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")
        monkeypatch.setenv("SLACK_USER_ID", "U123456789")
        monkeypatch.delenv("SLACK_CHANNEL", raising=False)

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()
            assert notifier.channel == "U123456789"

    def test_init_connection_failure(self, mock_env_vars):
        """Test initialization fails if connection test fails"""
        with patch.object(SlackNotifier, "_test_connection", return_value=False):
            with pytest.raises(ConnectionError, match="Failed to connect to Slack API"):
                SlackNotifier()

    @patch("requests.post")
    def test_connection_test_success(self, mock_post, mock_env_vars):
        """Test successful connection test"""
        mock_post.return_value.json.return_value = {"ok": True}

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        # Now test the actual connection method
        notifier._test_connection = SlackNotifier._test_connection.__get__(notifier, SlackNotifier)
        result = notifier._test_connection()
        assert result is True

    @patch("requests.post")
    def test_connection_test_failure(self, mock_post, mock_env_vars):
        """Test failed connection test"""
        mock_post.return_value.json.return_value = {"ok": False}

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        # Test the actual connection method
        notifier._test_connection = SlackNotifier._test_connection.__get__(notifier, SlackNotifier)
        result = notifier._test_connection()
        assert result is False

    @patch("requests.post")
    def test_send_stock_alert_success(self, mock_post, mock_env_vars, sample_analysis, mock_successful_response):
        """Test successful stock alert sending"""
        mock_post.return_value = mock_successful_response

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        result = notifier.send_stock_alert(sample_analysis, "BUY_SIGNAL")

        assert result is True
        mock_post.assert_called()

        # Check the call was made to the right endpoint
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://slack.com/api/chat.postMessage"

        # Check the payload structure
        payload = call_args[1]["json"]
        assert payload["channel"] == "#test-channel"
        assert "AAPL" in payload["text"]
        assert "blocks" in payload

    @patch("requests.post")
    def test_send_stock_alert_failure(self, mock_post, mock_env_vars, sample_analysis, mock_failed_response):
        """Test failed stock alert sending"""
        mock_post.return_value = mock_failed_response

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        result = notifier.send_stock_alert(sample_analysis, "BUY_SIGNAL")

        assert result is False

    @patch("requests.post")
    def test_send_simple_alert_success(self, mock_post, mock_env_vars, mock_successful_response):
        """Test successful simple alert sending"""
        mock_post.return_value = mock_successful_response

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        result = notifier.send_simple_alert("Test message", "🚀")

        assert result is True

        # Check the payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["text"] == "🚀 Test message"
        assert payload["channel"] == "#test-channel"

    @patch("requests.post")
    def test_send_daily_summary_success(self, mock_post, mock_env_vars, mock_successful_response):
        """Test successful daily summary sending"""
        mock_post.return_value = mock_successful_response

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        top_picks = [{"symbol": "AAPL", "recommendation": {"rating": "Buy"}, "score": {"composite_score": 85.0}}, {"symbol": "MSFT", "recommendation": {"rating": "Strong Buy"}, "score": {"composite_score": 90.0}}]

        summary_stats = {"total_analyzed": 2, "avg_score": 87.5, "buy_signals": 2}

        result = notifier.send_daily_summary(top_picks, summary_stats)

        assert result is True

        # Check the payload contains summary information
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "Daily Stock Analysis Summary" in payload["text"]
        assert "blocks" in payload

    def test_create_stock_alert_blocks_buy_signal(self, mock_env_vars):
        """Test creation of stock alert blocks for buy signal"""
        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        blocks = notifier._create_stock_alert_blocks("AAPL", "Buy", "High", 85.0, 180.0, 200.0, "5.0%", "BUY_SIGNAL")

        assert len(blocks) == 3  # Header + 2 sections
        assert blocks[0]["type"] == "header"
        assert "🚀" in blocks[0]["text"]["text"]  # Buy signal emoji
        assert "AAPL" in blocks[0]["text"]["text"]

        # Check fields are present
        fields = blocks[1]["fields"] + blocks[2]["fields"]
        field_texts = [field["text"] for field in fields]

        assert any("Buy" in text for text in field_texts)
        assert any("High" in text for text in field_texts)
        assert any("85.0" in text for text in field_texts)
        assert any("180.00" in text for text in field_texts)
        assert any("200.00" in text for text in field_texts)

    def test_create_stock_alert_blocks_sell_signal(self, mock_env_vars):
        """Test creation of stock alert blocks for sell signal"""
        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        blocks = notifier._create_stock_alert_blocks("AAPL", "Sell", "Medium", 30.0, 180.0, 150.0, "0%", "SELL_SIGNAL")

        assert blocks[0]["text"]["text"].startswith("🔻")  # Sell signal emoji

    def test_create_daily_summary_blocks(self, mock_env_vars):
        """Test creation of daily summary blocks"""
        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        top_picks = [{"symbol": "AAPL", "recommendation": {"rating": "Buy"}, "score": {"composite_score": 85.0}}]

        summary_stats = {"total_analyzed": 1, "avg_score": 85.0}

        blocks = notifier._create_daily_summary_blocks(top_picks, summary_stats)

        assert len(blocks) >= 3  # Header + picks + stats
        assert blocks[0]["type"] == "header"
        assert "Daily Analysis Summary" in blocks[0]["text"]["text"]

        # Check that stock pick is included
        pick_found = False
        for block in blocks:
            if block.get("text", {}).get("text", "").find("AAPL") != -1:
                pick_found = True
                break
        assert pick_found

    @patch("requests.post")
    def test_send_message_request_exception(self, mock_post, mock_env_vars):
        """Test handling of request exceptions"""
        mock_post.side_effect = requests.RequestException("Network error")

        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        message = SlackMessage("Test", "#test-channel")
        result = notifier._send_message(message)

        assert result is False

    def test_send_stock_alert_missing_data(self, mock_env_vars):
        """Test stock alert with missing data"""
        with patch.object(SlackNotifier, "_test_connection", return_value=True):
            notifier = SlackNotifier()

        # Analysis with missing fields
        incomplete_analysis = {
            "symbol": "AAPL"
            # Missing recommendation, score, etc.
        }

        with patch.object(notifier, "_send_message", return_value=True):
            result = notifier.send_stock_alert(incomplete_analysis)
            assert result is True  # Should handle missing data gracefully


class TestSlackMessage:
    """Test the SlackMessage dataclass"""

    def test_slack_message_creation(self):
        """Test SlackMessage creation"""
        message = SlackMessage("Test message", "#test-channel")

        assert message.text == "Test message"
        assert message.channel == "#test-channel"
        assert message.blocks is None
        assert message.attachments is None

    def test_slack_message_with_blocks(self):
        """Test SlackMessage with blocks"""
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Test"}}]
        message = SlackMessage("Test", "#test-channel", blocks=blocks)

        assert message.blocks == blocks
