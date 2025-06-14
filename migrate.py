#!/usr/bin/env python3
"""
Migration management script using Alembic for automatic migration generation.

This script provides a Python-based alternative to Drizzle's automatic migration
generation, using SQLAlchemy models as the source of truth.

Usage:
    python migrate.py generate "Add new column"  # Generate migration
    python migrate.py apply                      # Apply pending migrations
    python migrate.py history                    # Show migration history
    python migrate.py full                       # Full migration workflow
"""

import argparse
import sys

from src.db.migrations import MigrationRunner


def main():
    parser = argparse.ArgumentParser(description="Database migration management")
    parser.add_argument("command", choices=["generate", "apply", "history", "full", "legacy"], help="Migration command to run")
    parser.add_argument("message", nargs="?", default="Auto-generated migration", help="Migration message (for generate command)")

    args = parser.parse_args()

    runner = MigrationRunner()

    try:
        if args.command == "generate":
            success = runner.generate_migration(args.message)
        elif args.command == "apply":
            success = runner.apply_migrations()
        elif args.command == "history":
            success = runner.show_migration_history()
        elif args.command == "full":
            success = runner.run_alembic_migration_workflow()
        elif args.command == "legacy":
            print("🔄 Running legacy SQLAlchemy migration workflow...")
            success = runner.run_full_migration()
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1

        if success:
            print("✅ Migration command completed successfully!")
            return 0
        else:
            print("❌ Migration command failed!")
            return 1

    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
