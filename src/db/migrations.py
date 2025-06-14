"""
Database migration system for moving from SQLite to PostgreSQL
"""

import json
import os
import sqlite3
from datetime import datetime

from .connection import db, get_engine
from .models import (Base, DailyAnalysis, DailyDecision, MarketContext,
                     MigrationHistory, PerformanceTracking)


class MigrationRunner:
    """Handles database migrations and data transfer"""

    def __init__(self):
        self.engine = get_engine()
        self.session = db.get_session()

    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            print("🏗️  Creating database tables...")
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

    def drop_tables(self) -> bool:
        """Drop all database tables (use with caution!)"""
        try:
            print("🗑️  Dropping database tables...")
            Base.metadata.drop_all(bind=self.engine)
            print("✅ Database tables dropped successfully")
            return True
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
            return False

    def record_migration(self, version: str, description: str) -> bool:
        """Record a migration in the migration history"""
        try:
            migration = MigrationHistory(version=version, description=description)
            self.session.add(migration)
            self.session.commit()
            return True
        except Exception as e:
            print(f"❌ Error recording migration: {e}")
            self.session.rollback()
            return False

    def is_migration_applied(self, version: str) -> bool:
        """Check if a migration has already been applied"""
        try:
            migration = (
                self.session.query(MigrationHistory).filter_by(version=version).first()
            )
            return migration is not None
        except Exception as e:
            print(f"❌ Error checking migration status: {e}")
            return False

    def migrate_from_sqlite(self, sqlite_path: str = "data/stock_analysis.db") -> bool:
        """Migrate data from SQLite to PostgreSQL"""
        if not os.path.exists(sqlite_path):
            print(f"⚠️  SQLite database not found at {sqlite_path}")
            return True  # Not an error if no existing data

        try:
            print(f"🔄 Starting migration from SQLite: {sqlite_path}")

            # Connect to SQLite
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name

            # Migrate each table
            self._migrate_daily_analysis(sqlite_conn)
            self._migrate_daily_decisions(sqlite_conn)
            self._migrate_performance_tracking(sqlite_conn)
            self._migrate_market_context(sqlite_conn)

            sqlite_conn.close()

            # Record migration
            self.record_migration(
                "001_initial_migration", "Initial migration from SQLite to PostgreSQL"
            )

            print("✅ SQLite migration completed successfully")
            return True

        except Exception as e:
            print(f"❌ Error during SQLite migration: {e}")
            self.session.rollback()
            return False

    def _migrate_daily_analysis(self, sqlite_conn: sqlite3.Connection):
        """Migrate daily_analysis table"""
        print("📊 Migrating daily_analysis table...")

        cursor = sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='daily_analysis'"
        )
        if not cursor.fetchone():
            print("   No daily_analysis table found in SQLite")
            return

        cursor = sqlite_conn.execute(
            """
            SELECT date, symbol, analysis_data, composite_score, rating, confidence, created_at
            FROM daily_analysis
        """
        )

        count = 0
        for row in cursor:
            try:
                analysis = DailyAnalysis(
                    date=(
                        datetime.strptime(row["date"], "%Y-%m-%d").date()
                        if row["date"]
                        else None
                    ),
                    symbol=row["symbol"],
                    analysis_data=(
                        json.loads(row["analysis_data"]) if row["analysis_data"] else {}
                    ),
                    composite_score=row["composite_score"],
                    rating=row["rating"],
                    confidence=row["confidence"],
                    created_at=(
                        datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else datetime.now()
                    ),
                )
                self.session.add(analysis)
                count += 1
            except Exception as e:
                print(f"   ⚠️  Error migrating analysis record: {e}")

        self.session.commit()
        print(f"   ✅ Migrated {count} daily_analysis records")

    def _migrate_daily_decisions(self, sqlite_conn: sqlite3.Connection):
        """Migrate daily_decisions table"""
        print("🎯 Migrating daily_decisions table...")

        cursor = sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='daily_decisions'"
        )
        if not cursor.fetchone():
            print("   No daily_decisions table found in SQLite")
            return

        cursor = sqlite_conn.execute(
            """
            SELECT date, decision_type, reasoning, selected_stocks, market_context, created_at
            FROM daily_decisions
        """
        )

        count = 0
        for row in cursor:
            try:
                decision = DailyDecision(
                    date=(
                        datetime.strptime(row["date"], "%Y-%m-%d").date()
                        if row["date"]
                        else None
                    ),
                    decision_type=row["decision_type"],
                    reasoning=row["reasoning"],
                    selected_stocks=(
                        json.loads(row["selected_stocks"])
                        if row["selected_stocks"]
                        else None
                    ),
                    market_context=(
                        json.loads(row["market_context"])
                        if row["market_context"]
                        else None
                    ),
                    created_at=(
                        datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else datetime.now()
                    ),
                )
                self.session.add(decision)
                count += 1
            except Exception as e:
                print(f"   ⚠️  Error migrating decision record: {e}")

        self.session.commit()
        print(f"   ✅ Migrated {count} daily_decisions records")

    def _migrate_performance_tracking(self, sqlite_conn: sqlite3.Connection):
        """Migrate performance_tracking table"""
        print("📈 Migrating performance_tracking table...")

        cursor = sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='performance_tracking'"
        )
        if not cursor.fetchone():
            print("   No performance_tracking table found in SQLite")
            return

        cursor = sqlite_conn.execute(
            """
            SELECT symbol, recommendation_date, entry_price, current_price, target_price,
                   rating, days_held, return_pct, status, updated_at
            FROM performance_tracking
        """
        )

        count = 0
        for row in cursor:
            try:
                performance = PerformanceTracking(
                    symbol=row["symbol"],
                    recommendation_date=(
                        datetime.strptime(row["recommendation_date"], "%Y-%m-%d").date()
                        if row["recommendation_date"]
                        else None
                    ),
                    entry_price=row["entry_price"],
                    current_price=row["current_price"],
                    target_price=row["target_price"],
                    rating=row["rating"],
                    days_held=row["days_held"],
                    return_pct=row["return_pct"],
                    status=row["status"],
                    updated_at=(
                        datetime.fromisoformat(row["updated_at"])
                        if row["updated_at"]
                        else datetime.now()
                    ),
                )
                self.session.add(performance)
                count += 1
            except Exception as e:
                print(f"   ⚠️  Error migrating performance record: {e}")

        self.session.commit()
        print(f"   ✅ Migrated {count} performance_tracking records")

    def _migrate_market_context(self, sqlite_conn: sqlite3.Connection):
        """Migrate market_context table"""
        print("🌍 Migrating market_context table...")

        cursor = sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='market_context'"
        )
        if not cursor.fetchone():
            print("   No market_context table found in SQLite")
            return

        cursor = sqlite_conn.execute(
            """
            SELECT date, market_sentiment, vix_level, sector_rotation,
                   economic_indicators, news_themes, created_at
            FROM market_context
        """
        )

        count = 0
        for row in cursor:
            try:
                context = MarketContext(
                    date=(
                        datetime.strptime(row["date"], "%Y-%m-%d").date()
                        if row["date"]
                        else None
                    ),
                    market_sentiment=row["market_sentiment"],
                    vix_level=row["vix_level"],
                    sector_rotation=(
                        json.loads(row["sector_rotation"])
                        if row["sector_rotation"]
                        else None
                    ),
                    economic_indicators=(
                        json.loads(row["economic_indicators"])
                        if row["economic_indicators"]
                        else None
                    ),
                    news_themes=(
                        json.loads(row["news_themes"]) if row["news_themes"] else None
                    ),
                    created_at=(
                        datetime.fromisoformat(row["created_at"])
                        if row["created_at"]
                        else datetime.now()
                    ),
                )
                self.session.add(context)
                count += 1
            except Exception as e:
                print(f"   ⚠️  Error migrating context record: {e}")

        self.session.commit()
        print(f"   ✅ Migrated {count} market_context records")

    def validate_migration(self) -> bool:
        """Validate that migration was successful"""
        try:
            print("🔍 Validating migration...")

            # Check table counts
            analysis_count = self.session.query(DailyAnalysis).count()
            decisions_count = self.session.query(DailyDecision).count()
            performance_count = self.session.query(PerformanceTracking).count()
            context_count = self.session.query(MarketContext).count()

            print(f"   📊 Daily Analysis records: {analysis_count}")
            print(f"   🎯 Daily Decisions records: {decisions_count}")
            print(f"   📈 Performance Tracking records: {performance_count}")
            print(f"   🌍 Market Context records: {context_count}")

            # Test a sample query
            if analysis_count > 0:
                sample = self.session.query(DailyAnalysis).first()
                print(f"   📝 Sample record: {sample}")

            print("✅ Migration validation completed")
            return True

        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return False

    def run_full_migration(self) -> bool:
        """Run complete migration process"""
        print("🚀 Starting full database migration...")

        # Test connection
        if not db.test_connection():
            print("❌ Database connection failed")
            return False

        # Create tables
        if not self.create_tables():
            return False

        # Check if initial migration already applied
        if self.is_migration_applied("001_initial_migration"):
            print("⚠️  Initial migration already applied, skipping SQLite migration")
        else:
            # Migrate from SQLite
            if not self.migrate_from_sqlite():
                return False

        # Validate migration
        if not self.validate_migration():
            return False

        print("🎉 Full migration completed successfully!")
        return True

    def __del__(self):
        """Clean up database session"""
        if hasattr(self, "session"):
            self.session.close()
