#!/usr/bin/env python3
"""
Alert Manager CLI - Test and manage the stock alert system

Usage:
    python alert_manager.py test           # Test the alert system
    python alert_manager.py scan AAPL MSFT # Scan specific stocks
    python alert_manager.py watchlist      # Scan default watchlist
    python alert_manager.py daily-summary  # Send daily summary
    python alert_manager.py status         # Show system status
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv(".env.local")
except ImportError:
    pass  # dotenv not available, use system env vars

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.alerts.automated_alerts import create_alert_system


def print_banner():
    """Print the alert manager banner"""
    print("🚨 STOCK ALERT MANAGER")
    print("Slack-powered stock notifications")
    print("=" * 50)


async def test_system():
    """Test the alert system"""
    print("🧪 Testing alert system...")

    try:
        alert_system = create_alert_system()
        success = await alert_system.test_alert_system()

        if success:
            print("✅ Alert system test PASSED!")
            print("Check your Slack DMs for the test message.")
        else:
            print("❌ Alert system test FAILED!")
            print("Check your Slack configuration.")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure SLACK_BOT_TOKEN is set")
        print("2. Make sure SLACK_USER_ID is set")
        print("3. Check that your Slack app has proper permissions")


async def scan_symbols(symbols):
    """Scan specific symbols for alerts"""
    print(f"📊 Scanning {len(symbols)} symbols: {', '.join(symbols)}")

    try:
        alert_system = create_alert_system()
        results = await alert_system.scan_watchlist(symbols)

        print("\n📈 Scan Results:")
        print(f"   Symbols scanned: {results['symbols_scanned']}")
        print(f"   Alerts sent: {results['alerts_sent']}")
        print(f"   Errors: {results['errors']}")

        if results["triggered_symbols"]:
            print(f"   Triggered alerts: {', '.join(results['triggered_symbols'])}")
        else:
            print("   No alerts triggered")

        duration = (results["end_time"] - results["start_time"]).total_seconds()
        print(f"   Duration: {duration:.1f}s")

    except Exception as e:
        print(f"❌ Scan failed: {e}")


async def scan_watchlist():
    """Scan default watchlist"""
    # Default watchlist of popular stocks
    watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "CRM"]

    await scan_symbols(watchlist)


async def send_daily_summary():
    """Send daily summary"""
    print("📊 Generating daily summary...")

    try:
        alert_system = create_alert_system()
        success = await alert_system.run_daily_summary()

        if success:
            print("✅ Daily summary sent successfully!")
            print("Check your Slack DMs for the summary.")
        else:
            print("❌ Failed to send daily summary")

    except Exception as e:
        print(f"❌ Daily summary failed: {e}")


def show_status():
    """Show system status"""
    print("📊 System Status:")

    try:
        alert_system = create_alert_system()
        status = alert_system.get_system_status()

        print(f"   Slack connected: {'✅' if status['slack_connected'] else '❌'}")
        print(f"   Total alerts sent: {status['total_alerts_sent']}")
        print(f"   Errors count: {status['errors_count']}")
        print(f"   Daily alerts: {status['alert_system']['daily_alert_count']}/{status['alert_system']['max_daily_alerts']}")
        print(f"   Alerts remaining: {status['alert_system']['alerts_remaining']}")

        if status["alert_system"]["recent_alerts"]:
            print("   Recent alerts:")
            for symbol, time_str in status["alert_system"]["recent_alerts"].items():
                print(f"     {symbol}: {time_str}")
        else:
            print("   No recent alerts")

    except Exception as e:
        print(f"❌ Status check failed: {e}")


def show_help():
    """Show help message"""
    print("Available commands:")
    print("  test              - Test the alert system")
    print("  scan SYMBOL...    - Scan specific symbols")
    print("  watchlist         - Scan default watchlist")
    print("  daily-summary     - Send daily summary")
    print("  status            - Show system status")
    print("  help              - Show this help")
    print()
    print("Setup Instructions:")
    print("1. Create a Slack app at https://api.slack.com/apps")
    print("2. Add chat:write and chat:write.public scopes")
    print("3. Install app to your workspace")
    print("4. Set environment variables:")
    print("   export SLACK_BOT_TOKEN='xoxb-your-token'")
    print("   export SLACK_USER_ID='your-user-id'")


async def main():
    """Main CLI function"""
    print_banner()

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "test":
        await test_system()
    elif command == "scan":
        if len(sys.argv) < 3:
            print("❌ Please provide symbols to scan")
            print("Example: python alert_manager.py scan AAPL MSFT GOOGL")
            return
        symbols = [s.upper() for s in sys.argv[2:]]
        await scan_symbols(symbols)
    elif command == "watchlist":
        await scan_watchlist()
    elif command == "daily-summary":
        await send_daily_summary()
    elif command == "status":
        show_status()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    # Check environment variables
    if not os.getenv("SLACK_BOT_TOKEN"):
        print("⚠️  Warning: SLACK_BOT_TOKEN not set")
        print("Set it with: export SLACK_BOT_TOKEN='xoxb-your-token'")
        print()

    if not os.getenv("SLACK_USER_ID"):
        print("⚠️  Warning: SLACK_USER_ID not set")
        print("Set it with: export SLACK_USER_ID='your-user-id'")
        print()

    # Run the CLI
    asyncio.run(main())
