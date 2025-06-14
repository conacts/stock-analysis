"""
Automated alert system that monitors stocks and sends Slack notifications

This is the main orchestrator that:
1. Runs stock analysis
2. Checks alert triggers
3. Sends Slack notifications
4. Tracks alert history
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from ..core.analyzer import StockAnalyzer
from .alert_triggers import AlertConfig, AlertTrigger
from .slack_alerts import SlackNotifier


class AutomatedAlertSystem:
    """
    Main automated alert system

    Monitors stocks and sends intelligent Slack notifications
    """

    def __init__(self, slack_notifier: SlackNotifier = None, alert_trigger: AlertTrigger = None, analyzer: StockAnalyzer = None):
        """
        Initialize automated alert system

        Args:
            slack_notifier: Slack notification system
            alert_trigger: Alert trigger engine
            analyzer: Stock analyzer
        """
        self.slack_notifier = slack_notifier or SlackNotifier()
        self.alert_trigger = alert_trigger or AlertTrigger()
        self.analyzer = analyzer or StockAnalyzer()

        self.logger = logging.getLogger(__name__)

        # Track system status
        self.is_running = False
        self.last_run_time = None
        self.total_alerts_sent = 0
        self.errors_count = 0

    async def analyze_and_alert(self, symbol: str) -> bool:
        """
        Analyze a single stock and send alert if triggered

        Args:
            symbol: Stock symbol to analyze

        Returns:
            bool: True if alert was sent
        """
        try:
            self.logger.info(f"Analyzing {symbol} for potential alerts...")

            # Run comprehensive analysis
            analysis = self.analyzer.analyze_stock(symbol)

            if not analysis:
                self.logger.warning(f"No analysis results for {symbol}")
                return False

            # Check if alert should be triggered
            should_trigger, alert_type = self.alert_trigger.should_trigger_alert(analysis)

            if not should_trigger:
                self.logger.debug(f"No alert triggered for {symbol}")
                return False

            # Send Slack notification
            success = self.slack_notifier.send_stock_alert(analysis, alert_type.value)

            if success:
                # Record the alert
                self.alert_trigger.record_alert_sent(symbol)
                self.total_alerts_sent += 1
                self.logger.info(f"Alert sent successfully for {symbol}: {alert_type.value}")
                return True
            else:
                self.logger.error(f"Failed to send alert for {symbol}")
                self.errors_count += 1
                return False

        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            self.errors_count += 1
            return False

    async def scan_watchlist(self, symbols: List[str]) -> Dict:
        """
        Scan a list of symbols and send alerts as needed

        Args:
            symbols: List of stock symbols to scan

        Returns:
            dict: Summary of scan results
        """
        self.logger.info(f"Starting watchlist scan of {len(symbols)} symbols...")

        results = {"symbols_scanned": 0, "alerts_sent": 0, "errors": 0, "triggered_symbols": [], "start_time": datetime.now(), "end_time": None}

        alerts_sent_this_scan = 0

        for symbol in symbols:
            try:
                results["symbols_scanned"] += 1

                # Check if we've hit daily alert limit
                if self.alert_trigger.daily_alert_count >= self.alert_trigger.config.max_alerts_per_day:
                    self.logger.info("Daily alert limit reached, stopping scan")
                    break

                # Analyze and potentially alert
                alert_sent = await self.analyze_and_alert(symbol)

                if alert_sent:
                    alerts_sent_this_scan += 1
                    results["alerts_sent"] += 1
                    results["triggered_symbols"].append(symbol)

                # Small delay to avoid overwhelming APIs
                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {e}")
                results["errors"] += 1

        results["end_time"] = datetime.now()
        duration = (results["end_time"] - results["start_time"]).total_seconds()

        self.logger.info(f"Watchlist scan completed: {alerts_sent_this_scan} alerts sent in {duration:.1f}s")

        # Send scan summary if any alerts were sent
        if alerts_sent_this_scan > 0:
            await self._send_scan_summary(results)

        return results

    async def run_daily_summary(self, top_picks: List[Dict] = None) -> bool:
        """
        Send daily summary of top stock picks

        Args:
            top_picks: List of top stock picks (if None, will generate)

        Returns:
            bool: True if summary sent successfully
        """
        try:
            if top_picks is None:
                # Generate top picks by scanning popular stocks
                popular_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
                top_picks = []

                for symbol in popular_symbols[:5]:  # Limit to 5 for daily summary
                    try:
                        analysis = self.analyzer.analyze_stock(symbol)
                        if analysis and analysis.get("score", {}).get("composite_score", 0) > 70:
                            top_picks.append(analysis)
                    except Exception as e:
                        self.logger.warning(f"Error analyzing {symbol} for daily summary: {e}")

            # Create summary stats
            summary_stats = {
                "total_analyzed": len(top_picks),
                "avg_score": sum(pick.get("score", {}).get("composite_score", 0) for pick in top_picks) / len(top_picks) if top_picks else 0,
                "buy_signals": len([p for p in top_picks if p.get("recommendation", {}).get("rating") in ["Buy", "Strong Buy"]]),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Send daily summary
            success = self.slack_notifier.send_daily_summary(top_picks, summary_stats)

            if success:
                self.logger.info("Daily summary sent successfully")
            else:
                self.logger.error("Failed to send daily summary")

            return success

        except Exception as e:
            self.logger.error(f"Error sending daily summary: {e}")
            return False

    async def _send_scan_summary(self, scan_results: Dict):
        """Send a summary of the scan results"""
        try:
            duration = (scan_results["end_time"] - scan_results["start_time"]).total_seconds()

            summary_message = f"📊 Scan Complete!\n" f"• Analyzed: {scan_results['symbols_scanned']} stocks\n" f"• Alerts sent: {scan_results['alerts_sent']}\n" f"• Duration: {duration:.1f}s\n" f"• Triggered: {', '.join(scan_results['triggered_symbols']) if scan_results['triggered_symbols'] else 'None'}"

            self.slack_notifier.send_simple_alert(summary_message, "📊")

        except Exception as e:
            self.logger.error(f"Error sending scan summary: {e}")

    def get_system_status(self) -> Dict:
        """Get current system status"""
        alert_summary = self.alert_trigger.get_alert_summary()

        return {
            "is_running": self.is_running,
            "last_run_time": self.last_run_time.isoformat() if self.last_run_time else None,
            "total_alerts_sent": self.total_alerts_sent,
            "errors_count": self.errors_count,
            "alert_system": alert_summary,
            "slack_connected": self.slack_notifier._test_connection(),
            "system_uptime": datetime.now().isoformat(),
        }

    def update_config(self, new_config: AlertConfig):
        """Update alert configuration"""
        self.alert_trigger.config = new_config
        self.logger.info("Alert configuration updated")

    async def test_alert_system(self) -> bool:
        """
        Test the alert system with a sample stock

        Returns:
            bool: True if test successful
        """
        try:
            self.logger.info("Testing alert system...")

            # Test with NVDA (usually has good scores)
            test_symbol = "NVDA"

            # Temporarily disable time restrictions for testing
            original_market_hours_only = self.alert_trigger.config.market_hours_only
            self.alert_trigger.config.market_hours_only = False

            try:
                # Run analysis
                analysis = self.analyzer.analyze_stock(test_symbol)

                if analysis:
                    # Force send a test alert
                    success = self.slack_notifier.send_simple_alert(f"🧪 Alert System Test - {test_symbol} analysis completed successfully! " f"Score: {analysis.get('score', {}).get('composite_score', 0):.1f}/100", "🧪")

                    if success:
                        self.logger.info("Alert system test passed!")
                        return True
                    else:
                        self.logger.error("Alert system test failed - could not send message")
                        return False
                else:
                    self.logger.error("Alert system test failed - no analysis results")
                    return False

            finally:
                # Restore original setting
                self.alert_trigger.config.market_hours_only = original_market_hours_only

        except Exception as e:
            self.logger.error(f"Alert system test failed: {e}")
            return False


# Convenience function for quick setup
def create_alert_system(slack_bot_token: str = None, slack_user_id: str = None, alert_config: AlertConfig = None) -> AutomatedAlertSystem:
    """
    Create a fully configured alert system

    Args:
        slack_bot_token: Slack bot token
        slack_user_id: Slack user ID
        alert_config: Alert configuration

    Returns:
        AutomatedAlertSystem: Configured alert system
    """
    slack_notifier = SlackNotifier(slack_bot_token, slack_user_id)
    alert_trigger = AlertTrigger(alert_config)
    analyzer = StockAnalyzer()

    return AutomatedAlertSystem(slack_notifier, alert_trigger, analyzer)
