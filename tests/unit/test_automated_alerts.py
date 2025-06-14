"""
Tests for automated alert system
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.alerts.alert_triggers import AlertConfig, AlertTrigger, AlertType
from src.alerts.automated_alerts import AutomatedAlertSystem, create_alert_system
from src.alerts.slack_alerts import SlackNotifier
from src.core.analyzer import StockAnalyzer


class TestAutomatedAlertSystem:
    """Test the AutomatedAlertSystem class"""

    @pytest.fixture
    def mock_slack_notifier(self):
        """Mock Slack notifier"""
        mock = Mock(spec=SlackNotifier)
        mock.send_stock_alert.return_value = True
        mock.send_simple_alert.return_value = True
        mock.send_daily_summary.return_value = True
        mock._test_connection.return_value = True
        return mock

    @pytest.fixture
    def mock_alert_trigger(self):
        """Mock alert trigger"""
        mock = Mock(spec=AlertTrigger)
        mock.should_trigger_alert.return_value = (True, AlertType.BUY_SIGNAL)
        mock.daily_alert_count = 0
        mock.config = AlertConfig()
        mock.get_alert_summary.return_value = {"daily_alert_count": 0, "max_daily_alerts": 10, "alerts_remaining": 10, "last_reset_date": datetime.now().date().isoformat(), "tracked_symbols": 0, "recent_alerts": {}}
        return mock

    @pytest.fixture
    def mock_analyzer(self):
        """Mock stock analyzer"""
        mock = Mock(spec=StockAnalyzer)
        mock.analyze_stock.return_value = {"symbol": "AAPL", "recommendation": {"rating": "Buy", "confidence": "High", "price_target": 200.0, "suggested_allocation": "5.0%"}, "score": {"composite_score": 85.0}, "fundamentals": {"current_price": 180.0}}
        return mock

    @pytest.fixture
    def alert_system(self, mock_slack_notifier, mock_alert_trigger, mock_analyzer):
        """Create alert system with mocked dependencies"""
        return AutomatedAlertSystem(mock_slack_notifier, mock_alert_trigger, mock_analyzer)

    def test_init_default(self):
        """Test initialization with default components"""
        with patch("src.alerts.automated_alerts.SlackNotifier") as mock_slack, patch("src.alerts.automated_alerts.AlertTrigger") as mock_trigger, patch("src.alerts.automated_alerts.StockAnalyzer") as mock_analyzer:
            system = AutomatedAlertSystem()

            mock_slack.assert_called_once()
            mock_trigger.assert_called_once()
            mock_analyzer.assert_called_once()

            assert system.is_running is False
            assert system.last_run_time is None
            assert system.total_alerts_sent == 0
            assert system.errors_count == 0

    def test_init_with_components(self, mock_slack_notifier, mock_alert_trigger, mock_analyzer):
        """Test initialization with provided components"""
        system = AutomatedAlertSystem(mock_slack_notifier, mock_alert_trigger, mock_analyzer)

        assert system.slack_notifier == mock_slack_notifier
        assert system.alert_trigger == mock_alert_trigger
        assert system.analyzer == mock_analyzer

    @pytest.mark.asyncio
    async def test_analyze_and_alert_success(self, alert_system, mock_alert_trigger, mock_slack_notifier):
        """Test successful analysis and alert"""
        result = await alert_system.analyze_and_alert("AAPL")

        assert result is True
        alert_system.analyzer.analyze_stock.assert_called_once_with("AAPL")
        mock_alert_trigger.should_trigger_alert.assert_called_once()
        mock_slack_notifier.send_stock_alert.assert_called_once()
        mock_alert_trigger.record_alert_sent.assert_called_once_with("AAPL")
        assert alert_system.total_alerts_sent == 1

    @pytest.mark.asyncio
    async def test_analyze_and_alert_no_analysis(self, alert_system):
        """Test when analysis returns None"""
        alert_system.analyzer.analyze_stock.return_value = None

        result = await alert_system.analyze_and_alert("INVALID")

        assert result is False
        assert alert_system.total_alerts_sent == 0

    @pytest.mark.asyncio
    async def test_analyze_and_alert_no_trigger(self, alert_system, mock_alert_trigger):
        """Test when alert is not triggered"""
        mock_alert_trigger.should_trigger_alert.return_value = (False, None)

        result = await alert_system.analyze_and_alert("AAPL")

        assert result is False
        assert alert_system.total_alerts_sent == 0

    @pytest.mark.asyncio
    async def test_analyze_and_alert_send_failure(self, alert_system, mock_slack_notifier):
        """Test when Slack message sending fails"""
        mock_slack_notifier.send_stock_alert.return_value = False

        result = await alert_system.analyze_and_alert("AAPL")

        assert result is False
        assert alert_system.total_alerts_sent == 0
        assert alert_system.errors_count == 1

    @pytest.mark.asyncio
    async def test_analyze_and_alert_exception(self, alert_system):
        """Test exception handling in analyze_and_alert"""
        alert_system.analyzer.analyze_stock.side_effect = Exception("Analysis error")

        result = await alert_system.analyze_and_alert("AAPL")

        assert result is False
        assert alert_system.errors_count == 1

    @pytest.mark.asyncio
    async def test_scan_watchlist_success(self, alert_system):
        """Test successful watchlist scan"""
        symbols = ["AAPL", "MSFT", "GOOGL"]

        with patch.object(alert_system, "analyze_and_alert", return_value=True) as mock_analyze:
            results = await alert_system.scan_watchlist(symbols)

        assert results["symbols_scanned"] == 3
        assert results["alerts_sent"] == 3
        assert results["errors"] == 0
        assert results["triggered_symbols"] == symbols
        assert mock_analyze.call_count == 3

    @pytest.mark.asyncio
    async def test_scan_watchlist_mixed_results(self, alert_system):
        """Test watchlist scan with mixed results"""
        symbols = ["AAPL", "MSFT", "GOOGL"]

        # Mock different return values
        side_effects = [True, False, True]
        with patch.object(alert_system, "analyze_and_alert", side_effect=side_effects):
            results = await alert_system.scan_watchlist(symbols)

        assert results["symbols_scanned"] == 3
        assert results["alerts_sent"] == 2
        assert results["triggered_symbols"] == ["AAPL", "GOOGL"]

    @pytest.mark.asyncio
    async def test_scan_watchlist_daily_limit(self, alert_system, mock_alert_trigger):
        """Test watchlist scan stops at daily limit"""
        symbols = ["AAPL", "MSFT", "GOOGL"]
        mock_alert_trigger.daily_alert_count = 10  # At limit
        mock_alert_trigger.config.max_alerts_per_day = 10

        results = await alert_system.scan_watchlist(symbols)

        # Should scan first symbol but then stop
        assert results["symbols_scanned"] == 1
        assert results["alerts_sent"] == 0

    @pytest.mark.asyncio
    async def test_scan_watchlist_with_errors(self, alert_system):
        """Test watchlist scan with errors"""
        symbols = ["AAPL", "MSFT"]

        with patch.object(alert_system, "analyze_and_alert", side_effect=[True, Exception("Error")]):
            results = await alert_system.scan_watchlist(symbols)

        assert results["symbols_scanned"] == 2
        assert results["alerts_sent"] == 1
        assert results["errors"] == 1

    @pytest.mark.asyncio
    async def test_run_daily_summary_with_picks(self, alert_system, mock_slack_notifier):
        """Test daily summary with provided picks"""
        top_picks = [{"symbol": "AAPL", "recommendation": {"rating": "Buy"}, "score": {"composite_score": 85.0}}]

        result = await alert_system.run_daily_summary(top_picks)

        assert result is True
        mock_slack_notifier.send_daily_summary.assert_called_once()

        # Check the call arguments
        call_args = mock_slack_notifier.send_daily_summary.call_args
        assert call_args[0][0] == top_picks  # top_picks argument
        assert "total_analyzed" in call_args[0][1]  # summary_stats argument

    @pytest.mark.asyncio
    async def test_run_daily_summary_generate_picks(self, alert_system, mock_slack_notifier):
        """Test daily summary with generated picks"""
        result = await alert_system.run_daily_summary()

        assert result is True
        mock_slack_notifier.send_daily_summary.assert_called_once()

        # Should have called analyzer multiple times to generate picks
        assert alert_system.analyzer.analyze_stock.call_count > 0

    @pytest.mark.asyncio
    async def test_run_daily_summary_failure(self, alert_system, mock_slack_notifier):
        """Test daily summary sending failure"""
        mock_slack_notifier.send_daily_summary.return_value = False

        result = await alert_system.run_daily_summary([])

        assert result is False

    @pytest.mark.asyncio
    async def test_run_daily_summary_exception(self, alert_system, mock_slack_notifier):
        """Test daily summary with exception"""
        mock_slack_notifier.send_daily_summary.side_effect = Exception("Send error")

        result = await alert_system.run_daily_summary([])

        assert result is False

    def test_get_system_status(self, alert_system, mock_alert_trigger, mock_slack_notifier):
        """Test getting system status"""
        alert_system.total_alerts_sent = 5
        alert_system.errors_count = 1

        status = alert_system.get_system_status()

        assert status["is_running"] is False
        assert status["total_alerts_sent"] == 5
        assert status["errors_count"] == 1
        assert "alert_system" in status
        assert status["slack_connected"] is True
        assert "system_uptime" in status

    def test_update_config(self, alert_system, mock_alert_trigger):
        """Test updating alert configuration"""
        new_config = AlertConfig(min_buy_score=80.0)

        alert_system.update_config(new_config)

        assert alert_system.alert_trigger.config == new_config

    @pytest.mark.asyncio
    async def test_test_alert_system_success(self, alert_system, mock_slack_notifier):
        """Test successful alert system test"""
        result = await alert_system.test_alert_system()

        assert result is True
        alert_system.analyzer.analyze_stock.assert_called_once_with("NVDA")
        mock_slack_notifier.send_simple_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_alert_system_no_analysis(self, alert_system):
        """Test alert system test with no analysis"""
        alert_system.analyzer.analyze_stock.return_value = None

        result = await alert_system.test_alert_system()

        assert result is False

    @pytest.mark.asyncio
    async def test_test_alert_system_send_failure(self, alert_system, mock_slack_notifier):
        """Test alert system test with send failure"""
        mock_slack_notifier.send_simple_alert.return_value = False

        result = await alert_system.test_alert_system()

        assert result is False

    @pytest.mark.asyncio
    async def test_test_alert_system_exception(self, alert_system):
        """Test alert system test with exception"""
        alert_system.analyzer.analyze_stock.side_effect = Exception("Test error")

        result = await alert_system.test_alert_system()

        assert result is False

    @pytest.mark.asyncio
    async def test_test_alert_system_market_hours_handling(self, alert_system, mock_alert_trigger):
        """Test that test temporarily disables market hours restriction"""
        mock_alert_trigger.config.market_hours_only = True

        await alert_system.test_alert_system()

        # Should be restored to original value
        assert mock_alert_trigger.config.market_hours_only is True

    @pytest.mark.asyncio
    async def test_send_scan_summary(self, alert_system, mock_slack_notifier):
        """Test sending scan summary"""
        scan_results = {"symbols_scanned": 5, "alerts_sent": 2, "errors": 0, "triggered_symbols": ["AAPL", "MSFT"], "start_time": datetime.now(), "end_time": datetime.now()}

        await alert_system._send_scan_summary(scan_results)

        mock_slack_notifier.send_simple_alert.assert_called_once()
        call_args = mock_slack_notifier.send_simple_alert.call_args
        message = call_args[0][0]

        assert "Scan Complete" in message
        assert "5" in message  # symbols_scanned
        assert "2" in message  # alerts_sent


class TestCreateAlertSystem:
    """Test the create_alert_system convenience function"""

    @patch("src.alerts.automated_alerts.SlackNotifier")
    @patch("src.alerts.automated_alerts.AlertTrigger")
    @patch("src.alerts.automated_alerts.StockAnalyzer")
    def test_create_alert_system_default(self, mock_analyzer, mock_trigger, mock_slack):
        """Test creating alert system with defaults"""
        system = create_alert_system()

        mock_slack.assert_called_once_with(None, None)
        mock_trigger.assert_called_once_with(None)
        mock_analyzer.assert_called_once()

        assert isinstance(system, AutomatedAlertSystem)

    @patch("src.alerts.automated_alerts.SlackNotifier")
    @patch("src.alerts.automated_alerts.AlertTrigger")
    @patch("src.alerts.automated_alerts.StockAnalyzer")
    def test_create_alert_system_with_params(self, mock_analyzer, mock_trigger, mock_slack):
        """Test creating alert system with parameters"""
        config = AlertConfig(min_buy_score=80.0)

        system = create_alert_system(slack_bot_token="test-token", slack_user_id="test-user", alert_config=config)

        mock_slack.assert_called_once_with("test-token", "test-user")
        mock_trigger.assert_called_once_with(config)
        mock_analyzer.assert_called_once()

        assert isinstance(system, AutomatedAlertSystem)
