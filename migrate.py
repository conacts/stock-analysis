#!/usr/bin/env python3
"""
Database Migration CLI Tool
Run database migrations for the stock analysis system
"""

import argparse
import sys

from src.db.connection import get_db_connection
from src.db.migrations import MigrationRunner


def test_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    db = get_db_connection()
    if db.test_connection():
        print("✅ Database connection successful")
        return True
    else:
        print("❌ Database connection failed")
        print("   Check your .env.local file and DATABASE_URL")
        return False


def run_migration():
    """Run full migration process"""
    runner = MigrationRunner()
    return runner.run_full_migration()


def create_tables():
    """Create database tables only"""
    runner = MigrationRunner()
    return runner.create_tables()


def drop_tables():
    """Drop all database tables"""
    print("⚠️  WARNING: This will delete all data!")
    confirm = input("Type 'DELETE ALL DATA' to confirm: ")
    if confirm == "DELETE ALL DATA":
        runner = MigrationRunner()
        return runner.drop_tables()
    else:
        print("❌ Operation cancelled")
        return False


def validate_migration():
    """Validate migration results"""
    runner = MigrationRunner()
    return runner.validate_migration()


def main():
    parser = argparse.ArgumentParser(description="Database Migration Tool")
    parser.add_argument(
        "command",
        choices=["test", "migrate", "create", "drop", "validate"],
        help="Migration command to run",
    )

    args = parser.parse_args()

    print("🗄️  STOCK ANALYSIS DATABASE MIGRATION")
    print("=" * 50)

    success = False

    if args.command == "test":
        success = test_connection()
    elif args.command == "migrate":
        success = run_migration()
    elif args.command == "create":
        success = create_tables()
    elif args.command == "drop":
        success = drop_tables()
    elif args.command == "validate":
        success = validate_migration()

    if success:
        print("\n🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
