"""
Tests for alert trigger system
"""

from datetime import datetime, time, timedelta
from unittest.mock import patch

import pytest

from src.alerts.alert_triggers import AlertConfig, AlertTrigger, AlertType


class TestAlertConfig:
    """Test the AlertConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = AlertConfig()

        assert config.min_buy_score == 75.0
        assert config.min_strong_buy_score == 85.0
        assert config.min_confidence_threshold == "Medium"
        assert config.trigger_ratings == ["Buy", "Strong Buy"]
        assert config.market_hours_only is True
        assert config.start_time == time(9, 30)
        assert config.end_time == time(16, 0)
        assert config.max_alerts_per_day == 10
        assert config.min_hours_between_same_stock == 4
        assert config.max_allocation_threshold == 10.0
        assert config.exclude_symbols == []
        assert config.custom_filters == []

    def test_custom_config(self):
        """Test custom configuration"""
        config = AlertConfig(min_buy_score=80.0, trigger_ratings=["Strong Buy"], market_hours_only=False, exclude_symbols=["TSLA", "GME"])

        assert config.min_buy_score == 80.0
        assert config.trigger_ratings == ["Strong Buy"]
        assert config.market_hours_only is False
        assert config.exclude_symbols == ["TSLA", "GME"]


class TestAlertTrigger:
    """Test the AlertTrigger class"""

    @pytest.fixture
    def sample_analysis_buy(self):
        """Sample analysis that should trigger buy alert"""
        return {"symbol": "AAPL", "recommendation": {"rating": "Buy", "confidence": "High", "suggested_allocation": "5.0%"}, "score": {"composite_score": 80.0}}

    @pytest.fixture
    def sample_analysis_strong_buy(self):
        """Sample analysis that should trigger strong buy alert"""
        return {"symbol": "MSFT", "recommendation": {"rating": "Strong Buy", "confidence": "High", "suggested_allocation": "7.0%"}, "score": {"composite_score": 90.0}}

    @pytest.fixture
    def sample_analysis_low_score(self):
        """Sample analysis with low score (should not trigger)"""
        return {"symbol": "WEAK", "recommendation": {"rating": "Buy", "confidence": "Low", "suggested_allocation": "2.0%"}, "score": {"composite_score": 60.0}}

    @pytest.fixture
    def sample_analysis_high_allocation(self):
        """Sample analysis with high allocation (risk warning)"""
        return {"symbol": "RISKY", "recommendation": {"rating": "Buy", "confidence": "Medium", "suggested_allocation": "15.0%"}, "score": {"composite_score": 85.0}}

    def test_init_default_config(self):
        """Test initialization with default config"""
        trigger = AlertTrigger()

        assert trigger.config is not None
        assert trigger.daily_alert_count == 0
        assert trigger.last_alert_times == {}
        assert trigger.last_reset_date == datetime.now().date()

    def test_init_custom_config(self):
        """Test initialization with custom config"""
        config = AlertConfig(min_buy_score=80.0)
        trigger = AlertTrigger(config)

        assert trigger.config.min_buy_score == 80.0

    def test_should_trigger_alert_buy_signal(self, sample_analysis_buy):
        """Test triggering buy signal alert"""
        config = AlertConfig(market_hours_only=False)  # Disable time restrictions
        trigger = AlertTrigger(config)

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)

        assert should_trigger is True
        assert alert_type == AlertType.BUY_SIGNAL

    def test_should_trigger_alert_strong_buy(self, sample_analysis_strong_buy):
        """Test triggering strong buy alert"""
        config = AlertConfig(market_hours_only=False)
        trigger = AlertTrigger(config)

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_strong_buy)

        assert should_trigger is True
        assert alert_type == AlertType.STRONG_BUY

    def test_should_not_trigger_low_score(self, sample_analysis_low_score):
        """Test not triggering alert for low score"""
        config = AlertConfig(market_hours_only=False)
        trigger = AlertTrigger(config)

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_low_score)

        assert should_trigger is False
        assert alert_type is None

    def test_should_trigger_risk_warning(self, sample_analysis_high_allocation):
        """Test triggering risk warning for high allocation"""
        config = AlertConfig(market_hours_only=False)
        trigger = AlertTrigger(config)

        # Lower the score so it doesn't trigger Strong Buy
        sample_analysis_high_allocation["score"]["composite_score"] = 70.0
        sample_analysis_high_allocation["recommendation"]["rating"] = "Hold"

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_high_allocation)

        assert should_trigger is True
        assert alert_type == AlertType.RISK_WARNING

    def test_excluded_symbol(self, sample_analysis_buy):
        """Test that excluded symbols don't trigger alerts"""
        config = AlertConfig(market_hours_only=False, exclude_symbols=["AAPL"])
        trigger = AlertTrigger(config)

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)

        assert should_trigger is False
        assert alert_type is None

    def test_daily_limit_reached(self, sample_analysis_buy):
        """Test that daily limit prevents alerts"""
        config = AlertConfig(market_hours_only=False, max_alerts_per_day=1)
        trigger = AlertTrigger(config)

        # First alert should work
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is True
        trigger.record_alert_sent("AAPL")

        # Second alert should be blocked
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is False

    def test_frequency_limit_same_stock(self, sample_analysis_buy):
        """Test frequency limit for same stock"""
        config = AlertConfig(market_hours_only=False, min_hours_between_same_stock=4)
        trigger = AlertTrigger(config)

        # First alert should work
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is True
        trigger.record_alert_sent("AAPL")

        # Immediate second alert should be blocked
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is False

    @patch("src.alerts.alert_triggers.datetime")
    def test_market_hours_restriction(self, mock_datetime, sample_analysis_buy):
        """Test market hours restriction"""
        # Mock time outside market hours (8 AM)
        mock_datetime.now.return_value.time.return_value = time(8, 0)
        mock_datetime.now.return_value.date.return_value = datetime.now().date()

        config = AlertConfig(market_hours_only=True)
        trigger = AlertTrigger(config)

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)

        assert should_trigger is False

    @patch("src.alerts.alert_triggers.datetime")
    def test_within_market_hours(self, mock_datetime, sample_analysis_buy):
        """Test alert during market hours"""
        # Mock time within market hours (10 AM)
        mock_datetime.now.return_value.time.return_value = time(10, 0)
        mock_datetime.now.return_value.date.return_value = datetime.now().date()

        config = AlertConfig(market_hours_only=True)
        trigger = AlertTrigger(config)

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)

        assert should_trigger is True
        assert alert_type == AlertType.BUY_SIGNAL

    def test_confidence_threshold(self, sample_analysis_buy):
        """Test confidence threshold filtering"""
        config = AlertConfig(market_hours_only=False, min_confidence_threshold="High")
        trigger = AlertTrigger(config)

        # High confidence should pass
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is True

        # Lower confidence should fail
        sample_analysis_buy["recommendation"]["confidence"] = "Medium"
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is False

    def test_custom_filter(self, sample_analysis_buy):
        """Test custom filter functionality"""

        def custom_filter(analysis):
            # Only allow symbols starting with 'A'
            return analysis.get("symbol", "").startswith("A")

        config = AlertConfig(market_hours_only=False, custom_filters=[custom_filter])
        trigger = AlertTrigger(config)

        # AAPL should pass
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is True

        # Change symbol to something not starting with 'A'
        sample_analysis_buy["symbol"] = "MSFT"
        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is False

    def test_custom_filter_exception(self, sample_analysis_buy):
        """Test custom filter that raises exception"""

        def broken_filter(analysis):
            raise ValueError("Filter error")

        config = AlertConfig(market_hours_only=False, custom_filters=[broken_filter])
        trigger = AlertTrigger(config)

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)
        assert should_trigger is False

    def test_record_alert_sent(self):
        """Test recording sent alerts"""
        trigger = AlertTrigger()

        initial_count = trigger.daily_alert_count
        trigger.record_alert_sent("AAPL")

        assert trigger.daily_alert_count == initial_count + 1
        assert "AAPL" in trigger.last_alert_times
        assert isinstance(trigger.last_alert_times["AAPL"], datetime)

    def test_reset_daily_counters(self):
        """Test daily counter reset"""
        trigger = AlertTrigger()

        # Set some data
        trigger.daily_alert_count = 5
        trigger.last_alert_times["AAPL"] = datetime.now()

        # Mock new day
        trigger.last_reset_date = datetime.now().date() - timedelta(days=1)

        # This should trigger reset
        trigger._reset_daily_counters_if_needed()

        assert trigger.daily_alert_count == 0
        assert trigger.last_alert_times == {}
        assert trigger.last_reset_date == datetime.now().date()

    def test_get_alert_summary(self):
        """Test getting alert summary"""
        trigger = AlertTrigger()
        trigger.daily_alert_count = 3
        trigger.last_alert_times["AAPL"] = datetime.now()

        summary = trigger.get_alert_summary()

        assert summary["daily_alert_count"] == 3
        assert summary["max_daily_alerts"] == 10
        assert summary["alerts_remaining"] == 7
        assert summary["tracked_symbols"] == 1
        assert "AAPL" in summary["recent_alerts"]

    def test_missing_symbol(self):
        """Test analysis without symbol"""
        trigger = AlertTrigger()
        analysis = {"recommendation": {"rating": "Buy"}}

        should_trigger, alert_type = trigger.should_trigger_alert(analysis)

        assert should_trigger is False
        assert alert_type is None

    def test_missing_recommendation(self, sample_analysis_buy):
        """Test analysis without recommendation"""
        trigger = AlertTrigger()
        del sample_analysis_buy["recommendation"]

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)

        assert should_trigger is False
        assert alert_type is None

    def test_missing_score(self, sample_analysis_buy):
        """Test analysis without score"""
        trigger = AlertTrigger()
        del sample_analysis_buy["score"]

        should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)

        assert should_trigger is False
        assert alert_type is None

    def test_determine_alert_type_edge_cases(self):
        """Test alert type determination edge cases"""
        trigger = AlertTrigger()

        # Test with invalid allocation format
        analysis = {"symbol": "TEST", "recommendation": {"rating": "Buy", "confidence": "High", "suggested_allocation": "invalid"}, "score": {"composite_score": 80.0}}

        alert_type = trigger._determine_alert_type(analysis)
        assert alert_type == AlertType.BUY_SIGNAL  # Should still work

    def test_exception_handling(self, sample_analysis_buy):
        """Test exception handling in should_trigger_alert"""
        trigger = AlertTrigger()

        # Mock an exception in one of the check methods
        with patch.object(trigger, "_check_basic_prerequisites", side_effect=Exception("Test error")):
            should_trigger, alert_type = trigger.should_trigger_alert(sample_analysis_buy)

            assert should_trigger is False
            assert alert_type is None


class TestAlertType:
    """Test the AlertType enum"""

    def test_alert_type_values(self):
        """Test alert type enum values"""
        assert AlertType.BUY_SIGNAL.value == "BUY_SIGNAL"
        assert AlertType.SELL_SIGNAL.value == "SELL_SIGNAL"
        assert AlertType.STRONG_BUY.value == "STRONG_BUY"
        assert AlertType.PRICE_TARGET_HIT.value == "PRICE_TARGET_HIT"
        assert AlertType.DAILY_SUMMARY.value == "DAILY_SUMMARY"
        assert AlertType.PORTFOLIO_ALERT.value == "PORTFOLIO_ALERT"
        assert AlertType.RISK_WARNING.value == "RISK_WARNING"
