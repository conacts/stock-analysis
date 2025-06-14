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
    STRONG_SELL = "STRONG_SELL"
    TRIM_POSITION = "TRIM_POSITION"
    PRICE_TARGET_HIT = "PRICE_TARGET_HIT"
    DAILY_SUMMARY = "DAILY_SUMMARY"
    PORTFOLIO_ALERT = "PORTFOLIO_ALERT"
    PORTFOLIO_HEALTH = "PORTFOLIO_HEALTH"
    REBALANCE_ALERT = "REBALANCE_ALERT"
    RISK_WARNING = "RISK_WARNING"


@dataclass
class AlertConfig:
    """Configuration for alert triggers"""

    # Score thresholds
    min_buy_score: float = 75.0
    min_strong_buy_score: float = 85.0
    min_sell_score: float = 40.0
    min_strong_sell_score: float = 60.0
    min_confidence_threshold: str = "Medium"

    # Rating filters
    trigger_ratings: List[str] = field(default_factory=lambda: ["Buy", "Strong Buy"])
    sell_ratings: List[str] = field(default_factory=lambda: ["Sell", "Strong Sell"])

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

    # Portfolio-specific settings
    portfolio_enabled: bool = False
    default_portfolio_id: Optional[int] = None
    enable_sell_alerts: bool = True
    enable_rebalance_alerts: bool = True
    portfolio_health_check_frequency: int = 7  # days

    # Custom filters
    custom_filters: List[Callable] = field(default_factory=list)


class AlertTrigger:
    """
    Alert trigger engine that determines when to send notifications

    Now includes portfolio-aware functionality for sell signals and position management.
    """

    def __init__(self, config: AlertConfig = None, portfolio_analyzer=None):
        """
        Initialize alert trigger

        Args:
            config: Alert configuration (uses defaults if None)
            portfolio_analyzer: Portfolio analyzer for sell signals (optional)
        """
        self.config = config or AlertConfig()
        self.portfolio_analyzer = portfolio_analyzer
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

            # Portfolio-aware checks for buy signals
            if alert_type in [AlertType.BUY_SIGNAL, AlertType.STRONG_BUY] and self.config.portfolio_enabled:
                if not self._check_portfolio_buy_conditions(analysis):
                    return False, None

            # All checks passed
            self.logger.info(f"Alert triggered for {analysis.get('symbol', 'UNKNOWN')}: {alert_type.value}")
            return True, alert_type

        except Exception as e:
            self.logger.error(f"Error checking alert trigger: {e}")
            return False, None

    def check_portfolio_sell_alerts(self, portfolio_id: int) -> List[Dict]:
        """
        Check portfolio positions for sell opportunities

        Args:
            portfolio_id: Portfolio to analyze

        Returns:
            List of sell alert data
        """
        if not self.portfolio_analyzer or not self.config.enable_sell_alerts:
            return []

        try:
            sell_recommendations = self.portfolio_analyzer.analyze_portfolio_for_sells(portfolio_id)
            alerts = []

            for rec in sell_recommendations:
                sell_score = rec.get("sell_recommendation", {}).get("sell_score", 0)

                # Determine alert type based on sell score
                if sell_score >= self.config.min_strong_sell_score:
                    alert_type = AlertType.STRONG_SELL
                elif sell_score >= self.config.min_sell_score:
                    alert_type = AlertType.SELL_SIGNAL
                else:
                    alert_type = AlertType.TRIM_POSITION

                # Create alert data
                alert_data = {"symbol": rec["symbol"], "alert_type": alert_type, "sell_recommendation": rec["sell_recommendation"], "current_position": rec["current_position"], "analysis_date": rec["analysis_date"]}

                alerts.append(alert_data)

            return alerts

        except Exception as e:
            self.logger.error(f"Error checking portfolio sell alerts: {e}")
            return []

    def check_portfolio_health_alert(self, portfolio_id: int) -> Optional[Dict]:
        """
        Check if portfolio health alert should be triggered

        Args:
            portfolio_id: Portfolio to check

        Returns:
            Portfolio health alert data or None
        """
        if not self.portfolio_analyzer:
            return None

        try:
            health = self.portfolio_analyzer.get_portfolio_health_score(portfolio_id)

            # Trigger alert if health score is poor or has significant issues
            if health.get("health_score", 100) < 60 or len(health.get("issues", [])) >= 3:
                return {"alert_type": AlertType.PORTFOLIO_HEALTH, "health_data": health, "portfolio_id": portfolio_id}

            return None

        except Exception as e:
            self.logger.error(f"Error checking portfolio health: {e}")
            return None

    def check_rebalancing_alerts(self, portfolio_id: int) -> List[Dict]:
        """
        Check for portfolio rebalancing opportunities

        Args:
            portfolio_id: Portfolio to analyze

        Returns:
            List of rebalancing alert data
        """
        if not self.portfolio_analyzer or not self.config.enable_rebalance_alerts:
            return []

        try:
            rebalance_recs = self.portfolio_analyzer.generate_rebalancing_recommendations(portfolio_id)
            alerts = []

            for rec in rebalance_recs:
                if rec.get("priority") in ["HIGH", "MEDIUM"]:
                    alert_data = {"alert_type": AlertType.REBALANCE_ALERT, "rebalance_data": rec, "portfolio_id": portfolio_id}
                    alerts.append(alert_data)

            return alerts

        except Exception as e:
            self.logger.error(f"Error checking rebalancing alerts: {e}")
            return []

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

        # Sell signals (if enabled)
        if rating in self.config.sell_ratings:
            if score <= 30:  # Very low score
                return AlertType.STRONG_SELL
            elif score <= 50:  # Low score
                return AlertType.SELL_SIGNAL

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
            current_confidence_index = confidence_levels.index(confidence) if confidence in confidence_levels else 0

            if current_confidence_index < min_confidence_index:
                return False

        elif alert_type in [AlertType.SELL_SIGNAL, AlertType.STRONG_SELL]:
            # Check sell score threshold
            min_score = self.config.min_strong_sell_score if alert_type == AlertType.STRONG_SELL else self.config.min_sell_score
            if score > (100 - min_score):  # Invert for sell signals
                return False

            # Check sell rating
            if rating not in self.config.sell_ratings and score > 40:
                return False

        elif alert_type == AlertType.RISK_WARNING:
            # Risk warnings always trigger if we got this far
            pass

        # Apply custom filters
        for custom_filter in self.config.custom_filters:
            if not custom_filter(analysis):
                return False

        return True

    def _check_portfolio_buy_conditions(self, analysis: Dict) -> bool:
        """Check portfolio-specific conditions for buy signals"""
        if not self.portfolio_analyzer or not self.config.default_portfolio_id:
            return True  # Skip portfolio checks if not configured

        try:
            symbol = analysis.get("symbol")
            suggested_allocation = analysis.get("recommendation", {}).get("suggested_allocation", "5%")

            # Parse allocation percentage
            try:
                allocation_pct = float(suggested_allocation.replace("%", ""))
            except (ValueError, AttributeError):
                allocation_pct = 5.0

            # Check against portfolio
            portfolio_check = self.portfolio_analyzer.check_buy_against_portfolio(self.config.default_portfolio_id, symbol, allocation_pct)

            # Only allow if action is BUY or ADD
            return portfolio_check.get("action") in ["BUY", "ADD"]

        except Exception as e:
            self.logger.error(f"Error checking portfolio buy conditions: {e}")
            return True  # Default to allowing the alert

    def _check_frequency_limits(self, analysis: Dict) -> bool:
        """Check if we've hit frequency limits"""

        # Check daily limit
        if self.daily_alert_count >= self.config.max_alerts_per_day:
            return False

        # Check per-symbol frequency
        symbol = analysis.get("symbol")
        if symbol in self.last_alert_times:
            last_alert = self.last_alert_times[symbol]
            hours_since_last = (datetime.now() - last_alert).total_seconds() / 3600

            if hours_since_last < self.config.min_hours_between_same_stock:
                return False

        return True

    def _check_time_restrictions(self) -> bool:
        """Check if current time allows alerts"""

        if not self.config.market_hours_only:
            return True

        current_time = datetime.now().time()
        return self.config.start_time <= current_time <= self.config.end_time

    def get_alert_summary(self) -> Dict:
        """Get summary of alert trigger status"""

        return {
            "daily_alert_count": self.daily_alert_count,
            "max_daily_alerts": self.config.max_alerts_per_day,
            "alerts_remaining": max(0, self.config.max_alerts_per_day - self.daily_alert_count),
            "tracked_symbols": len(self.last_alert_times),
            "last_reset_date": self.last_reset_date.isoformat(),
            "recent_alerts": {symbol: time.isoformat() for symbol, time in self.last_alert_times.items()},
            "portfolio_enabled": self.config.portfolio_enabled,
            "sell_alerts_enabled": self.config.enable_sell_alerts,
            "rebalance_alerts_enabled": self.config.enable_rebalance_alerts,
        }
