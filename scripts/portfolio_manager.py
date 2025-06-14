#!/usr/bin/env python3
"""
Portfolio Manager CLI

Command-line interface for portfolio management operations.
"""

import argparse
import os
import sys
from datetime import datetime

# Add project root to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from dotenv import load_dotenv  # noqa: E402

from src.core.analyzer import StockAnalyzer  # noqa: E402
from src.db.migrations import MigrationRunner  # noqa: E402
from src.portfolio.portfolio_analyzer import PortfolioAnalyzer  # noqa: E402
from src.portfolio.portfolio_manager import PortfolioManager  # noqa: E402


def setup_environment():
    """Load environment variables"""
    # Try different env files
    env_files = [".env.local", ".env"]
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"✅ Loaded environment from {env_file}")
            break
    else:
        print("⚠️  No .env file found")


def create_portfolio(args):
    """Create a new portfolio"""
    try:
        pm = PortfolioManager()
        portfolio_id = pm.create_portfolio(name=args.name, description=args.description or "", portfolio_type=args.type or "personal")

        if portfolio_id:
            print(f"✅ Created portfolio '{args.name}' with ID {portfolio_id}")
        else:
            print(f"❌ Failed to create portfolio '{args.name}'")

    except Exception as e:
        print(f"❌ Error creating portfolio: {e}")


def list_portfolios(args):
    """List all portfolios"""
    try:
        pm = PortfolioManager()
        portfolios = pm.list_portfolios()

        if not portfolios:
            print("📁 No portfolios found")
            return

        print(f"📁 Found {len(portfolios)} portfolio(s):")
        print("-" * 80)

        for portfolio in portfolios:
            print(f"ID: {portfolio.id}")
            print(f"Name: {portfolio.name}")
            print(f"Type: {portfolio.portfolio_type}")
            print(f"Description: {portfolio.description}")
            print(f"Created: {portfolio.created_at}")
            print("-" * 80)

    except Exception as e:
        print(f"❌ Error listing portfolios: {e}")


def add_position(args):
    """Add a position to portfolio"""
    try:
        pm = PortfolioManager()

        success = pm.add_position(portfolio_id=args.portfolio_id, symbol=args.symbol.upper(), quantity=args.quantity, average_cost=args.price, sector=args.sector or "")

        if success:
            print(f"✅ Added {args.quantity} shares of {args.symbol.upper()} @ ${args.price}")

            # Record transaction
            pm.record_transaction(portfolio_id=args.portfolio_id, symbol=args.symbol.upper(), transaction_type="buy", quantity=args.quantity, price=args.price, fees=args.fees or 0.0, notes=f"Added via CLI on {datetime.now().strftime('%Y-%m-%d')}")
        else:
            print(f"❌ Failed to add position {args.symbol.upper()}")

    except Exception as e:
        print(f"❌ Error adding position: {e}")


def show_portfolio(args):
    """Show portfolio summary and positions"""
    try:
        pm = PortfolioManager()

        # Get portfolio info
        portfolio = pm.get_portfolio(args.portfolio_id)
        if not portfolio:
            print(f"❌ Portfolio {args.portfolio_id} not found")
            return

        print(f"📊 Portfolio: {portfolio.name}")
        print(f"Type: {portfolio.portfolio_type}")
        print(f"Description: {portfolio.description}")
        print("=" * 80)

        # Update all positions first
        print("🔄 Updating position prices...")
        pm.update_all_positions(args.portfolio_id)

        # Get positions
        positions = pm.get_portfolio_positions(args.portfolio_id)
        if not positions:
            print("📁 No positions in portfolio")
            return

        # Show positions
        print(f"\n📈 Positions ({len(positions)}):")
        print("-" * 100)
        print(f"{'Symbol':<8} {'Qty':<8} {'Avg Cost':<10} {'Current':<10} {'Value':<12} {'P&L':<10} {'P&L%':<8} {'Sector':<15}")
        print("-" * 100)

        total_value = 0
        total_cost = 0

        for pos in positions:
            total_value += pos.market_value
            total_cost += pos.quantity * pos.average_cost

            print(f"{pos.symbol:<8} {pos.quantity:<8.2f} ${pos.average_cost:<9.2f} ${pos.current_price:<9.2f} " f"${pos.market_value:<11.2f} ${pos.unrealized_pnl:<9.2f} {pos.unrealized_pnl_pct:<7.1f}% {pos.sector:<15}")

        print("-" * 100)
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0

        print(f"{'TOTAL':<8} {'':<8} {'':<10} {'':<10} ${total_value:<11.2f} ${total_pnl:<9.2f} {total_pnl_pct:<7.1f}%")

        # Show summary
        summary = pm.get_portfolio_summary(args.portfolio_id)
        if summary.get("top_holdings"):
            print("\n🏆 Top Holdings:")
            for holding in summary["top_holdings"][:3]:
                print(f"  {holding['symbol']}: ${holding['value']:.2f} ({holding['allocation_pct']:.1f}%)")

        if summary.get("sector_allocation"):
            print("\n🏭 Sector Allocation:")
            for sector, allocation in sorted(summary["sector_allocation"].items(), key=lambda x: x[1], reverse=True):
                print(f"  {sector}: {allocation:.1f}%")

    except Exception as e:
        print(f"❌ Error showing portfolio: {e}")


def analyze_sells(args):
    """Analyze portfolio for sell opportunities"""
    try:
        pm = PortfolioManager()
        analyzer = StockAnalyzer()
        pa = PortfolioAnalyzer(pm, analyzer)

        print(f"🔍 Analyzing portfolio {args.portfolio_id} for sell opportunities...")

        sell_recommendations = pa.analyze_portfolio_for_sells(args.portfolio_id)

        if not sell_recommendations:
            print("✅ No sell recommendations at this time")
            return

        print(f"\n🚨 Found {len(sell_recommendations)} sell recommendation(s):")
        print("=" * 100)

        for rec in sell_recommendations:
            pos = rec["current_position"]
            sell = rec["sell_recommendation"]

            print(f"\n📉 {rec['symbol']} - {sell['suggested_action']}")
            print(f"Current Position: {pos['quantity']:.2f} shares @ ${pos['average_cost']:.2f}")
            print(f"Current Price: ${pos['current_price']:.2f}")
            print(f"Market Value: ${pos['market_value']:.2f}")
            print(f"P&L: ${pos['unrealized_pnl']:.2f} ({pos['unrealized_pnl_pct']:.1f}%)")
            print(f"Rating: {sell['rating']} (Score: {sell['score']:.1f})")
            print(f"Sell Score: {sell['sell_score']}/100")
            print(f"Suggested Quantity: {sell['suggested_quantity']:.2f} shares")
            print("Sell Signals:")
            for signal in sell["sell_signals"]:
                print(f"  • {signal}")
            print("-" * 80)

    except Exception as e:
        print(f"❌ Error analyzing sells: {e}")


def portfolio_health(args):
    """Check portfolio health"""
    try:
        pm = PortfolioManager()
        analyzer = StockAnalyzer()
        pa = PortfolioAnalyzer(pm, analyzer)

        print(f"🏥 Checking health of portfolio {args.portfolio_id}...")

        health = pa.get_portfolio_health_score(args.portfolio_id)

        print("\n📊 Portfolio Health Report")
        print("=" * 50)
        print(f"Health Score: {health['health_score']}/100")
        print(f"Status: {health['status']}")
        print(f"Total Positions: {health.get('total_positions', 0)}")
        print(f"Total Value: ${health.get('total_value', 0):.2f}")
        print(f"Avg Performance: {health.get('avg_performance', 0):.1f}%")

        if health.get("issues"):
            print("\n⚠️  Issues Found:")
            for issue in health["issues"]:
                print(f"  • {issue}")
        else:
            print("\n✅ No issues found!")

    except Exception as e:
        print(f"❌ Error checking portfolio health: {e}")


def run_migrations(args):
    """Run database migrations"""
    try:
        print("🔄 Running database migrations...")
        migrator = MigrationRunner()

        # Create tables first
        if not migrator.create_tables():
            print("❌ Failed to create database tables")
            return

        # Try to migrate from SQLite if it exists
        if migrator.migrate_from_sqlite():
            print("✅ Database migrations completed successfully")
        else:
            print("❌ Database migrations failed")

    except Exception as e:
        print(f"❌ Error running migrations: {e}")


def main():
    """Main CLI entry point"""
    setup_environment()

    parser = argparse.ArgumentParser(description="Portfolio Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create portfolio
    create_parser = subparsers.add_parser("create", help="Create a new portfolio")
    create_parser.add_argument("name", help="Portfolio name")
    create_parser.add_argument("--description", help="Portfolio description")
    create_parser.add_argument("--type", help="Portfolio type (personal, ira, 401k)", default="personal")
    create_parser.set_defaults(func=create_portfolio)

    # List portfolios
    list_parser = subparsers.add_parser("list", help="List all portfolios")
    list_parser.set_defaults(func=list_portfolios)

    # Add position
    add_parser = subparsers.add_parser("add", help="Add position to portfolio")
    add_parser.add_argument("portfolio_id", type=int, help="Portfolio ID")
    add_parser.add_argument("symbol", help="Stock symbol")
    add_parser.add_argument("quantity", type=float, help="Number of shares")
    add_parser.add_argument("price", type=float, help="Price per share")
    add_parser.add_argument("--sector", help="Stock sector")
    add_parser.add_argument("--fees", type=float, help="Transaction fees", default=0.0)
    add_parser.set_defaults(func=add_position)

    # Show portfolio
    show_parser = subparsers.add_parser("show", help="Show portfolio details")
    show_parser.add_argument("portfolio_id", type=int, help="Portfolio ID")
    show_parser.set_defaults(func=show_portfolio)

    # Analyze sells
    sells_parser = subparsers.add_parser("sells", help="Analyze portfolio for sell opportunities")
    sells_parser.add_argument("portfolio_id", type=int, help="Portfolio ID")
    sells_parser.set_defaults(func=analyze_sells)

    # Portfolio health
    health_parser = subparsers.add_parser("health", help="Check portfolio health")
    health_parser.add_argument("portfolio_id", type=int, help="Portfolio ID")
    health_parser.set_defaults(func=portfolio_health)

    # Run migrations
    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations")
    migrate_parser.set_defaults(func=run_migrations)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
