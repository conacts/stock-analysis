"""
Database migration system for moving from SQLite to PostgreSQL
"""

import json
import os
import sqlite3
import subprocess
from datetime import datetime

from sqlalchemy import text

from .connection import get_db_connection, get_engine
from .models import Base, DailyAnalysis, DailyDecision, MarketContext, MigrationHistory, PerformanceTracking
from .swarm_db import SwarmDatabase


class MigrationRunner:
    """Handles database migrations and data transfer"""

    def __init__(self):
        self.engine = get_engine()
        self.session = get_db_connection().get_session()

    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            print("🏗️  Creating database tables...")
            Base.metadata.create_all(bind=self.engine)

            # Create portfolio tables using raw SQL
            self._create_portfolio_tables_sql()

            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False

    def _create_portfolio_tables_sql(self):
        """Create portfolio tables using raw SQL for PostgreSQL"""
        try:
            with self.engine.connect() as conn:
                # Portfolios table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS portfolios (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        description TEXT,
                        portfolio_type VARCHAR(50) DEFAULT 'personal',
                        base_currency VARCHAR(10) DEFAULT 'USD',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT true
                    )
                """
                    )
                )

                # Portfolio positions table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS portfolio_positions (
                        id SERIAL PRIMARY KEY,
                        portfolio_id INTEGER NOT NULL,
                        symbol VARCHAR(20) NOT NULL,
                        quantity DECIMAL(15,6) NOT NULL DEFAULT 0.0,
                        average_cost DECIMAL(15,6) NOT NULL DEFAULT 0.0,
                        current_price DECIMAL(15,6) DEFAULT 0.0,
                        market_value DECIMAL(15,6) DEFAULT 0.0,
                        unrealized_pnl DECIMAL(15,6) DEFAULT 0.0,
                        unrealized_pnl_pct DECIMAL(8,4) DEFAULT 0.0,
                        sector VARCHAR(100),
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (portfolio_id) REFERENCES portfolios (id),
                        UNIQUE(portfolio_id, symbol)
                    )
                """
                    )
                )

                # Portfolio transactions table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS portfolio_transactions (
                        id SERIAL PRIMARY KEY,
                        portfolio_id INTEGER NOT NULL,
                        symbol VARCHAR(20) NOT NULL,
                        transaction_type VARCHAR(20) NOT NULL,
                        quantity DECIMAL(15,6) NOT NULL,
                        price DECIMAL(15,6) NOT NULL,
                        total_amount DECIMAL(15,6) NOT NULL,
                        fees DECIMAL(15,6) DEFAULT 0.0,
                        transaction_date DATE NOT NULL,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
                    )
                """
                    )
                )

                # Portfolio snapshots table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                        id SERIAL PRIMARY KEY,
                        portfolio_id INTEGER NOT NULL,
                        snapshot_date DATE NOT NULL,
                        total_value DECIMAL(15,6) DEFAULT 0.0,
                        cash_balance DECIMAL(15,6) DEFAULT 0.0,
                        invested_amount DECIMAL(15,6) DEFAULT 0.0,
                        unrealized_pnl DECIMAL(15,6) DEFAULT 0.0,
                        unrealized_pnl_pct DECIMAL(8,4) DEFAULT 0.0,
                        day_change DECIMAL(15,6) DEFAULT 0.0,
                        day_change_pct DECIMAL(8,4) DEFAULT 0.0,
                        positions_count INTEGER DEFAULT 0,
                        top_holdings JSONB,
                        sector_allocation JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (portfolio_id) REFERENCES portfolios (id),
                        UNIQUE(portfolio_id, snapshot_date)
                    )
                """
                    )
                )

                conn.commit()
                print("✅ Portfolio tables created successfully")

        except Exception as e:
            print(f"❌ Error creating portfolio tables: {e}")
            raise

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
            migration = self.session.query(MigrationHistory).filter_by(version=version).first()
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
            self.record_migration("001_initial_migration", "Initial migration from SQLite to PostgreSQL")

            print("✅ SQLite migration completed successfully")
            return True

        except Exception as e:
            print(f"❌ Error during SQLite migration: {e}")
            self.session.rollback()
            return False

    def _migrate_daily_analysis(self, sqlite_conn: sqlite3.Connection):
        """Migrate daily_analysis table"""
        print("📊 Migrating daily_analysis table...")

        cursor = sqlite_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_analysis'")
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
                    date=(datetime.strptime(row["date"], "%Y-%m-%d").date() if row["date"] else None),
                    symbol=row["symbol"],
                    analysis_data=(json.loads(row["analysis_data"]) if row["analysis_data"] else {}),
                    composite_score=row["composite_score"],
                    rating=row["rating"],
                    confidence=row["confidence"],
                    created_at=(datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now()),
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

        cursor = sqlite_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_decisions'")
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
                    date=(datetime.strptime(row["date"], "%Y-%m-%d").date() if row["date"] else None),
                    decision_type=row["decision_type"],
                    reasoning=row["reasoning"],
                    selected_stocks=(json.loads(row["selected_stocks"]) if row["selected_stocks"] else None),
                    market_context=(json.loads(row["market_context"]) if row["market_context"] else None),
                    created_at=(datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now()),
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

        cursor = sqlite_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='performance_tracking'")
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
                    recommendation_date=(datetime.strptime(row["recommendation_date"], "%Y-%m-%d").date() if row["recommendation_date"] else None),
                    entry_price=row["entry_price"],
                    current_price=row["current_price"],
                    target_price=row["target_price"],
                    rating=row["rating"],
                    days_held=row["days_held"],
                    return_pct=row["return_pct"],
                    status=row["status"],
                    updated_at=(datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now()),
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

        cursor = sqlite_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_context'")
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
                    date=(datetime.strptime(row["date"], "%Y-%m-%d").date() if row["date"] else None),
                    market_sentiment=row["market_sentiment"],
                    vix_level=row["vix_level"],
                    sector_rotation=(json.loads(row["sector_rotation"]) if row["sector_rotation"] else None),
                    economic_indicators=(json.loads(row["economic_indicators"]) if row["economic_indicators"] else None),
                    news_themes=(json.loads(row["news_themes"]) if row["news_themes"] else None),
                    created_at=(datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now()),
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

    def create_swarm_tables(self) -> bool:
        """Create Swarm AI trading system tables"""
        try:
            print("🤖 Creating Swarm database tables...")

            # Initialize SwarmDatabase which will create tables
            SwarmDatabase()

            # Record migration
            self.record_migration("003_swarm_tables", "Create Swarm AI trading system tables")

            print("✅ Swarm database tables created successfully")
            return True

        except Exception as e:
            print(f"❌ Error creating Swarm tables: {e}")
            return False

    def migrate_swarm_data(self, sqlite_path: str = "data/swarm_conversations.db") -> bool:
        """Migrate existing Swarm conversation data if it exists"""
        if not os.path.exists(sqlite_path):
            print(f"⚠️  Swarm SQLite database not found at {sqlite_path}, skipping Swarm data migration")
            return True  # Not an error if no existing Swarm data

        try:
            print(f"🤖 Starting Swarm data migration from SQLite: {sqlite_path}")

            # Connect to SQLite
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row

            # Migrate conversations if table exists
            try:
                cursor = sqlite_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
                if cursor.fetchone():
                    self._migrate_swarm_conversations(sqlite_conn)
            except sqlite3.OperationalError:
                print("   ⚠️  No conversations table found in Swarm database")

            # Migrate trading decisions if table exists
            try:
                cursor = sqlite_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trading_decisions'")
                if cursor.fetchone():
                    self._migrate_swarm_decisions(sqlite_conn)
            except sqlite3.OperationalError:
                print("   ⚠️  No trading_decisions table found in Swarm database")

            sqlite_conn.close()

            # Record migration
            self.record_migration("004_swarm_data", "Migrate Swarm conversation and decision data")

            print("✅ Swarm data migration completed successfully")
            return True

        except Exception as e:
            print(f"❌ Error during Swarm data migration: {e}")
            return False

    def _migrate_swarm_conversations(self, sqlite_conn: sqlite3.Connection):
        """Migrate Swarm conversation data"""
        print("   🗣️  Migrating Swarm conversations...")

        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM conversations")

        count = 0
        for row in cursor.fetchall():
            try:
                from models.swarm_models import SwarmConversation

                conversation = SwarmConversation(
                    portfolio_id=row.get("portfolio_id", "default"),
                    conversation_id=row["conversation_id"],
                    user_message=row["user_message"],
                    agent_responses=json.loads(row["agent_responses"]) if row["agent_responses"] else [],
                    final_agent=row.get("final_agent", "unknown"),
                    turns_used=row.get("turns_used", 1),
                    success=bool(row.get("success", True)),
                    error_message=row.get("error_message"),
                    metadata=json.loads(row["metadata"]) if row.get("metadata") else None,
                )

                SwarmDatabase().save_conversation(conversation)
                count += 1

            except Exception as e:
                print(f"   ⚠️  Error migrating conversation record: {e}")

        print(f"   ✅ Migrated {count} Swarm conversation records")

    def _migrate_swarm_decisions(self, sqlite_conn: sqlite3.Connection):
        """Migrate Swarm trading decision data"""
        print("   📈 Migrating Swarm trading decisions...")

        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM trading_decisions")

        count = 0
        for row in cursor.fetchall():
            try:
                from models.swarm_models import TradingDecision

                decision = TradingDecision(
                    conversation_id=row["conversation_id"],
                    portfolio_id=row.get("portfolio_id", "default"),
                    decision_type=row["decision_type"],
                    symbol=row.get("symbol"),
                    quantity=float(row["quantity"]) if row.get("quantity") else None,
                    price=float(row["price"]) if row.get("price") else None,
                    reasoning=row["reasoning"],
                    confidence_score=float(row["confidence_score"]) if row.get("confidence_score") else None,
                    risk_assessment=row.get("risk_assessment"),
                    executed=bool(row.get("executed", False)),
                    execution_result=json.loads(row["execution_result"]) if row.get("execution_result") else None,
                )

                SwarmDatabase().save_trading_decision(decision)
                count += 1

            except Exception as e:
                print(f"   ⚠️  Error migrating trading decision record: {e}")

        print(f"   ✅ Migrated {count} Swarm trading decision records")

    def setup_alembic(self) -> bool:
        """Set up Alembic for automatic migration generation"""
        try:
            print("🔧 Setting up Alembic for automatic migrations...")

            # Check if alembic is already initialized
            if os.path.exists("src/db/alembic"):
                print("   ✅ Alembic already initialized")
                return True

            # Initialize Alembic
            result = subprocess.run(["uv", "run", "alembic", "init", "src/db/alembic"], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"   ❌ Failed to initialize Alembic: {result.stderr}")
                return False

            print("   ✅ Alembic initialized successfully")
            return True

        except Exception as e:
            print(f"❌ Error setting up Alembic: {e}")
            return False

    def generate_migration(self, message: str = "Auto-generated migration") -> bool:
        """Generate a new migration using Alembic autogenerate"""
        try:
            print(f"🔄 Generating migration: {message}")

            # Run alembic revision --autogenerate
            result = subprocess.run(["uv", "run", "alembic", "revision", "--autogenerate", "-m", message], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"   ❌ Failed to generate migration: {result.stderr}")
                return False

            print("   ✅ Migration generated successfully")
            print(f"   📝 Output: {result.stdout}")
            return True

        except Exception as e:
            print(f"❌ Error generating migration: {e}")
            return False

    def apply_migrations(self) -> bool:
        """Apply pending migrations using Alembic"""
        try:
            print("🚀 Applying pending migrations...")

            # Run alembic upgrade head
            result = subprocess.run(["uv", "run", "alembic", "upgrade", "head"], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"   ❌ Failed to apply migrations: {result.stderr}")
                return False

            print("   ✅ Migrations applied successfully")
            print(f"   📝 Output: {result.stdout}")
            return True

        except Exception as e:
            print(f"❌ Error applying migrations: {e}")
            return False

    def show_migration_history(self) -> bool:
        """Show current migration history"""
        try:
            print("📋 Current migration history:")

            # Run alembic history
            result = subprocess.run(["uv", "run", "alembic", "history"], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"   ❌ Failed to get migration history: {result.stderr}")
                return False

            print(result.stdout)
            return True

        except Exception as e:
            print(f"❌ Error getting migration history: {e}")
            return False

    def run_alembic_migration_workflow(self) -> bool:
        """Complete Alembic-based migration workflow"""
        print("🚀 Starting Alembic migration workflow...")

        # Test connection
        if not get_db_connection().test_connection():
            print("❌ Database connection failed")
            return False

        # Set up Alembic if needed
        if not self.setup_alembic():
            return False

        # Generate initial migration if no migrations exist
        migrations_dir = "src/db/alembic/versions"
        if os.path.exists(migrations_dir) and not os.listdir(migrations_dir):
            print("📝 No existing migrations found, generating initial migration...")
            if not self.generate_migration("Initial migration with all models"):
                return False

        # Apply migrations
        if not self.apply_migrations():
            return False

        # Show current state
        self.show_migration_history()

        print("🎉 Alembic migration workflow completed successfully!")
        return True

    def run_full_migration(self) -> bool:
        """Run complete migration process"""
        print("🚀 Starting full database migration...")

        # Test connection
        if not get_db_connection().test_connection():
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

        # Create Swarm tables
        if not self.create_swarm_tables():
            return False

        # Migrate Swarm data
        if not self.migrate_swarm_data():
            return False

        print("🎉 Full migration completed successfully!")
        return True

    def __del__(self):
        """Clean up database session"""
        if hasattr(self, "session"):
            self.session.close()

    def create_performance_tracking_table(self):
        """Create performance tracking table"""
        query = """
        CREATE TABLE IF NOT EXISTS performance_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            recommendation_date TEXT NOT NULL,
            entry_price REAL,
            current_price REAL,
            target_price REAL,
            rating TEXT,
            days_held INTEGER,
            return_pct REAL,
            status TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
        self.logger.info("Created performance_tracking table")

    def create_portfolio_tables(self):
        """Create all portfolio-related tables"""
        # Portfolios table
        portfolios_query = """
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            portfolio_type TEXT DEFAULT 'personal',
            base_currency TEXT DEFAULT 'USD',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """

        # Portfolio positions table
        positions_query = """
        CREATE TABLE IF NOT EXISTS portfolio_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 0.0,
            average_cost REAL NOT NULL DEFAULT 0.0,
            current_price REAL DEFAULT 0.0,
            market_value REAL DEFAULT 0.0,
            unrealized_pnl REAL DEFAULT 0.0,
            unrealized_pnl_pct REAL DEFAULT 0.0,
            sector TEXT,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios (id),
            UNIQUE(portfolio_id, symbol)
        )
        """

        # Portfolio transactions table
        transactions_query = """
        CREATE TABLE IF NOT EXISTS portfolio_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            fees REAL DEFAULT 0.0,
            transaction_date TEXT NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
        )
        """

        # Portfolio snapshots table
        snapshots_query = """
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            snapshot_date TEXT NOT NULL,
            total_value REAL DEFAULT 0.0,
            cash_balance REAL DEFAULT 0.0,
            invested_amount REAL DEFAULT 0.0,
            unrealized_pnl REAL DEFAULT 0.0,
            unrealized_pnl_pct REAL DEFAULT 0.0,
            day_change REAL DEFAULT 0.0,
            day_change_pct REAL DEFAULT 0.0,
            positions_count INTEGER DEFAULT 0,
            top_holdings TEXT,
            sector_allocation TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios (id),
            UNIQUE(portfolio_id, snapshot_date)
        )
        """

        # Execute all queries
        self.execute_query(portfolios_query)
        self.logger.info("Created portfolios table")

        self.execute_query(positions_query)
        self.logger.info("Created portfolio_positions table")

        self.execute_query(transactions_query)
        self.logger.info("Created portfolio_transactions table")

        self.execute_query(snapshots_query)
        self.logger.info("Created portfolio_snapshots table")

    def run_all_migrations(self):
        """Run all database migrations"""
        try:
            self.create_migration_history_table()
            self.create_daily_analysis_table()
            self.create_daily_decisions_table()
            self.create_performance_tracking_table()
            self.create_portfolio_tables()  # Add portfolio tables

            # Record migration
            self.record_migration("001_initial_schema")
            self.record_migration("002_portfolio_tables")

            self.logger.info("All migrations completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False
