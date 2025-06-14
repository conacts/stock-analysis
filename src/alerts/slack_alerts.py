"""
Slack notification system for stock alerts

Setup Instructions:
1. Go to https://api.slack.com/apps
2. Create a new app for your workspace
3. Go to "OAuth & Permissions"
4. Add these scopes: chat:write, chat:write.public
5. Install app to workspace
6. Copy the "Bot User OAuth Token" (starts with xoxb-)
7. Set SLACK_BOT_TOKEN environment variable
8. Get your user ID by going to your Slack profile -> More -> Copy member ID
9. Set SLACK_USER_ID environment variable

No payment required - completely free!
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import requests


@dataclass
class SlackMessage:
    """Slack message structure"""

    text: str
    channel: Optional[str] = None
    blocks: Optional[List[Dict]] = None
    attachments: Optional[List[Dict]] = None


class SlackNotifier:
    """
    Simple Slack notification system for stock alerts

    Free to use - just needs a Slack app with bot token
    """

    def __init__(self, bot_token: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize Slack notifier

        Args:
            bot_token: Slack bot token (or set SLACK_BOT_TOKEN env var)
            user_id: Your Slack user ID (or set SLACK_USER_ID env var)
        """
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.user_id = user_id or os.getenv("SLACK_USER_ID")

        if not self.bot_token:
            raise ValueError("Slack bot token required. Set SLACK_BOT_TOKEN environment variable or pass bot_token parameter.")

        if not self.user_id:
            raise ValueError("Slack user ID required. Set SLACK_USER_ID environment variable or pass user_id parameter.")

        self.base_url = "https://slack.com/api"
        self.headers = {"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json"}

        self.logger = logging.getLogger(__name__)

        # Test connection on initialization
        if not self._test_connection():
            raise ConnectionError("Failed to connect to Slack API. Check your bot token.")

    def _test_connection(self) -> bool:
        """Test Slack API connection"""
        try:
            response = requests.post(f"{self.base_url}/auth.test", headers=self.headers, timeout=10)
            result = response.json()
            return result.get("ok", False)
        except Exception as e:
            self.logger.error(f"Slack connection test failed: {e}")
            return False

    def send_stock_alert(self, analysis: Dict, alert_type: str = "BUY_SIGNAL") -> bool:
        """
        Send a formatted stock alert to Slack

        Args:
            analysis: Stock analysis results
            alert_type: Type of alert (BUY_SIGNAL, SELL_SIGNAL, PRICE_TARGET, etc.)

        Returns:
            bool: True if message sent successfully
        """
        try:
            symbol = analysis.get("symbol", "UNKNOWN")
            rating = analysis.get("recommendation", {}).get("rating", "Unknown")
            confidence = analysis.get("recommendation", {}).get("confidence", "Unknown")
            score = analysis.get("score", {}).get("composite_score", 0)
            current_price = analysis.get("fundamentals", {}).get("current_price", 0)
            target_price = analysis.get("recommendation", {}).get("price_target", 0)
            allocation = analysis.get("recommendation", {}).get("suggested_allocation", "Unknown")

            # Create rich message with blocks
            blocks = self._create_stock_alert_blocks(symbol, rating, confidence, score, current_price, target_price, allocation, alert_type)

            message = SlackMessage(
                text=f"🚨 Stock Alert: {symbol} - {rating}",
                channel=self.user_id,  # Send as DM
                blocks=blocks,
            )

            return self._send_message(message)

        except Exception as e:
            self.logger.error(f"Failed to send stock alert: {e}")
            return False

    def send_simple_alert(self, message: str, emoji: str = "📈") -> bool:
        """
        Send a simple text alert

        Args:
            message: Alert message
            emoji: Emoji to prefix the message

        Returns:
            bool: True if message sent successfully
        """
        try:
            slack_message = SlackMessage(text=f"{emoji} {message}", channel=self.user_id)
            return self._send_message(slack_message)
        except Exception as e:
            self.logger.error(f"Failed to send simple alert: {e}")
            return False

    def send_daily_summary(self, top_picks: List[Dict], summary_stats: Dict) -> bool:
        """
        Send daily analysis summary

        Args:
            top_picks: List of top stock picks
            summary_stats: Summary statistics

        Returns:
            bool: True if message sent successfully
        """
        try:
            blocks = self._create_daily_summary_blocks(top_picks, summary_stats)

            message = SlackMessage(text="📊 Daily Stock Analysis Summary", channel=self.user_id, blocks=blocks)

            return self._send_message(message)

        except Exception as e:
            self.logger.error(f"Failed to send daily summary: {e}")
            return False

    def _send_message(self, message: SlackMessage) -> bool:
        """Send message to Slack"""
        try:
            payload = {"channel": message.channel, "text": message.text}

            if message.blocks:
                payload["blocks"] = message.blocks

            if message.attachments:
                payload["attachments"] = message.attachments

            response = requests.post(f"{self.base_url}/chat.postMessage", headers=self.headers, json=payload, timeout=10)

            result = response.json()

            if result.get("ok"):
                self.logger.info("Slack message sent successfully")
                return True
            else:
                self.logger.error(f"Slack API error: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to send Slack message: {e}")
            return False

    def _create_stock_alert_blocks(self, symbol: str, rating: str, confidence: str, score: float, current_price: float, target_price: float, allocation: str, alert_type: str) -> List[Dict]:
        """Create rich Slack blocks for stock alerts"""

        # Determine emoji and color based on rating
        if rating in ["Strong Buy", "Buy"]:
            emoji = "🚀"
        elif rating == "Hold":
            emoji = "⏸️"
        else:
            emoji = "🔻"

        # Calculate upside potential
        upside = ((target_price - current_price) / current_price * 100) if current_price > 0 else 0

        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": f"{emoji} {alert_type}: {symbol}"}},
            {"type": "section", "fields": [{"type": "mrkdwn", "text": f"*Rating:* {rating}"}, {"type": "mrkdwn", "text": f"*Confidence:* {confidence}"}, {"type": "mrkdwn", "text": f"*Score:* {score:.1f}/100"}, {"type": "mrkdwn", "text": f"*Allocation:* {allocation}"}]},
            {
                "type": "section",
                "fields": [{"type": "mrkdwn", "text": f"*Current Price:* ${current_price:.2f}"}, {"type": "mrkdwn", "text": f"*Target Price:* ${target_price:.2f}"}, {"type": "mrkdwn", "text": f"*Upside Potential:* {upside:+.1f}%"}, {"type": "mrkdwn", "text": f"*Time:* {datetime.now().strftime('%H:%M:%S')}"}],
            },
        ]

        return blocks

    def _create_daily_summary_blocks(self, top_picks: List[Dict], summary_stats: Dict) -> List[Dict]:
        """Create rich Slack blocks for daily summary"""

        blocks = [{"type": "header", "text": {"type": "plain_text", "text": f"📊 Daily Analysis Summary - {datetime.now().strftime('%Y-%m-%d')}"}}, {"type": "section", "text": {"type": "mrkdwn", "text": f"*Top {len(top_picks)} Stock Picks Today*"}}]

        # Add top picks
        for i, pick in enumerate(top_picks[:5], 1):
            symbol = pick.get("symbol", "UNKNOWN")
            rating = pick.get("recommendation", {}).get("rating", "Unknown")
            score = pick.get("score", {}).get("composite_score", 0)

            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*{i}. {symbol}* - {rating} ({score:.1f}/100)"}})

        # Add summary stats
        if summary_stats:
            stats_text = []
            for key, value in summary_stats.items():
                stats_text.append(f"*{key.replace('_', ' ').title()}:* {value}")

            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(stats_text)}})

        return blocks
