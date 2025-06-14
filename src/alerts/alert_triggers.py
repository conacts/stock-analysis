"""
Alert trigger system for automated stock notifications

This module defines when and how to trigger alerts based on analysis results.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Callable, Dict, List, Optional


class AlertType(Enum):
    """Types of alerts that can be triggered"""

    BUY_SIGNAL = "BUY_SIGNAL"
    SELL_SIGNAL = "SELL_SIGNAL"
    STRONG_BUY = "STRONG_BUY"
    PRICE_TARGET_HIT = "PRICE_TARGET_HIT"
    DAILY_SUMMARY = "DAILY_SUMMARY"
    PORTFOLIO_ALERT = "PORTFOLIO_ALERT"
    RISK_WARNING = "RISK_WARNING"


@dataclass
class AlertConfig:
    """Configuration for alert triggers"""

    # Score thresholds
    min_buy_score: float = 75.0
    min_strong_buy_score: float = 85.0
    min_confidence_threshold: str = "Medium"

    # Rating filters
    trigger_ratings: List[str] = field(default_factory=lambda: ["Buy", "Strong Buy"])

    # Time restrictions
    market_hours_only: bool = True
    start_time: time = time(9, 30)  # 9:30 AM
    end_time: time = time(16, 0)  # 4:00 PM

    # Frequency limits
    max_alerts_per_day: int = 10
    min_hours_between_same_stock: int = 4

    # Portfolio filters
    max_allocation_threshold: float = 10.0  # Don't alert if allocation > 10%
    exclude_symbols: List[str] = field(default_factory=list)

    # Custom filters
    custom_filters: List[Callable] = field(default_factory=list)


class AlertTrigger:
    """
    Alert trigger engine that determines when to send notifications
    """

    def __init__(self, config: AlertConfig = None):
        """
        Initialize alert trigger

        Args:
            config: Alert configuration (uses defaults if None)
        """
        self.config = config or AlertConfig()
        self.logger = logging.getLogger(__name__)

        # Track sent alerts to avoid spam
        self.daily_alert_count = 0
        self.last_alert_times = {}  # symbol -> datetime
        self.last_reset_date = datetime.now().date()

    def should_trigger_alert(self, analysis: Dict, alert_type: AlertType = None) -> tuple[bool, AlertType]:
        """
        Determine if an alert should be triggered based on analysis

        Args:
            analysis: Stock analysis results
            alert_type: Specific alert type to check (if None, auto-determine)

        Returns:
            tuple: (should_trigger, alert_type)
        """
        try:
            # Reset daily counters if new day
            self._reset_daily_counters_if_needed()

            # Check basic prerequisites
            if not self._check_basic_prerequisites(analysis):
                return False, None

            # Determine alert type if not specified
            if alert_type is None:
                alert_type = self._determine_alert_type(analysis)

            if alert_type is None:
                return False, None

            # Check specific trigger conditions
            if not self._check_trigger_conditions(analysis, alert_type):
                return False, None

            # Check frequency limits
            if not self._check_frequency_limits(analysis):
                return False, None

            # Check time restrictions
            if not self._check_time_restrictions():
                return False, None

            # All checks passed
            self.logger.info(f"Alert triggered for {analysis.get('symbol', 'UNKNOWN')}: {alert_type.value}")
            return True, alert_type

        except Exception as e:
            self.logger.error(f"Error checking alert trigger: {e}")
            return False, None

    def record_alert_sent(self, symbol: str):
        """Record that an alert was sent for tracking purposes"""
        self.daily_alert_count += 1
        self.last_alert_times[symbol] = datetime.now()
        self.logger.info(f"Alert recorded for {symbol}. Daily count: {self.daily_alert_count}")

    def _reset_daily_counters_if_needed(self):
        """Reset daily counters if it's a new day"""
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_alert_count = 0
            self.last_alert_times.clear()
            self.last_reset_date = current_date
            self.logger.info("Daily alert counters reset")

    def _check_basic_prerequisites(self, analysis: Dict) -> bool:
        """Check basic prerequisites for any alert"""

        # Must have symbol
        symbol = analysis.get("symbol")
        if not symbol:
            return False

        # Check if symbol is excluded
        if symbol in self.config.exclude_symbols:
            return False

        # Must have recommendation
        recommendation = analysis.get("recommendation", {})
        if not recommendation:
            return False

        # Must have score
        score = analysis.get("score", {}).get("composite_score", 0)
        if score <= 0:
            return False

        return True

    def _determine_alert_type(self, analysis: Dict) -> Optional[AlertType]:
        """Automatically determine the appropriate alert type"""

        recommendation = analysis.get("recommendation", {})
        rating = recommendation.get("rating", "")
        score = analysis.get("score", {}).get("composite_score", 0)

        # Strong Buy signals
        if score >= self.config.min_strong_buy_score and rating in ["Strong Buy", "Buy"]:
            return AlertType.STRONG_BUY

        # Regular Buy signals
        if score >= self.config.min_buy_score and rating in self.config.trigger_ratings:
            return AlertType.BUY_SIGNAL

        # Risk warnings for high allocation recommendations
        allocation_str = recommendation.get("suggested_allocation", "0%")
        try:
            allocation = float(allocation_str.replace("%", ""))
            if allocation > self.config.max_allocation_threshold:
                return AlertType.RISK_WARNING
        except (ValueError, AttributeError):
            pass

        return None

    def _check_trigger_conditions(self, analysis: Dict, alert_type: AlertType) -> bool:
        """Check specific conditions for the alert type"""

        recommendation = analysis.get("recommendation", {})
        score = analysis.get("score", {}).get("composite_score", 0)
        rating = recommendation.get("rating", "")
        confidence = recommendation.get("confidence", "")

        if alert_type in [AlertType.BUY_SIGNAL, AlertType.STRONG_BUY]:
            # Check score threshold
            min_score = self.config.min_strong_buy_score if alert_type == AlertType.STRONG_BUY else self.config.min_buy_score
            if score < min_score:
                return False

            # Check rating
            if rating not in self.config.trigger_ratings:
                return False

            # Check confidence
            confidence_levels = ["Low", "Medium", "High"]
            min_confidence_index = confidence_levels.index(self.config.min_confidence_threshold)
            try:
                current_confidence_index = confidence_levels.index(confidence)
                if current_confidence_index < min_confidence_index:
                    return False
            except ValueError:
                return False

        elif alert_type == AlertType.RISK_WARNING:
            # Risk warnings have different criteria
            allocation_str = recommendation.get("suggested_allocation", "0%")
            try:
                allocation = float(allocation_str.replace("%", ""))
                if allocation <= self.config.max_allocation_threshold:
                    return False
            except (ValueError, AttributeError):
                return False

        # Apply custom filters
        for custom_filter in self.config.custom_filters:
            try:
                if not custom_filter(analysis):
                    return False
            except Exception as e:
                self.logger.warning(f"Custom filter error: {e}")
                return False

        return True

    def _check_frequency_limits(self, analysis: Dict) -> bool:
        """Check if frequency limits allow sending this alert"""

        symbol = analysis.get("symbol")

        # Check daily limit
        if self.daily_alert_count >= self.config.max_alerts_per_day:
            self.logger.info(f"Daily alert limit reached ({self.config.max_alerts_per_day})")
            return False

        # Check per-symbol frequency
        if symbol in self.last_alert_times:
            last_alert = self.last_alert_times[symbol]
            hours_since_last = (datetime.now() - last_alert).total_seconds() / 3600

            if hours_since_last < self.config.min_hours_between_same_stock:
                self.logger.info(f"Too soon since last alert for {symbol} ({hours_since_last:.1f}h < {self.config.min_hours_between_same_stock}h)")
                return False

        return True

    def _check_time_restrictions(self) -> bool:
        """Check if current time allows sending alerts"""

        if not self.config.market_hours_only:
            return True

        current_time = datetime.now().time()

        # Check if within market hours
        if self.config.start_time <= current_time <= self.config.end_time:
            return True

        self.logger.info(f"Outside market hours ({self.config.start_time} - {self.config.end_time})")
        return False

    def get_alert_summary(self) -> Dict:
        """Get summary of alert activity"""
        return {
            "daily_alert_count": self.daily_alert_count,
            "max_daily_alerts": self.config.max_alerts_per_day,
            "alerts_remaining": max(0, self.config.max_alerts_per_day - self.daily_alert_count),
            "last_reset_date": self.last_reset_date.isoformat(),
            "tracked_symbols": len(self.last_alert_times),
            "recent_alerts": {symbol: alert_time.isoformat() for symbol, alert_time in self.last_alert_times.items()},
        }
