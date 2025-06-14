"""
Database connection management for Neon PostgreSQL
"""

import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

# Load environment variables
load_dotenv(".env.local")


class DatabaseConnection:
    """Manages PostgreSQL database connections with connection pooling"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            # In testing environment, we might not have DATABASE_URL set
            # The actual connection will be created when needed
            if os.getenv("TESTING"):
                self.database_url = "sqlite:///:memory:"
            else:
                raise ValueError("DATABASE_URL environment variable is required")

        self._engine: Optional[Engine] = None
        self._SessionLocal: Optional[sessionmaker] = None

    @property
    def engine(self) -> Engine:
        """Lazy initialization of database engine"""
        if self._engine is None:
            # Create engine with connection pooling
            if self.database_url.startswith("sqlite"):
                # SQLite doesn't support connection pooling
                self._engine = create_engine(
                    self.database_url,
                    echo=False,  # Set to True for SQL debugging
                )
            else:
                # PostgreSQL with connection pooling
                self._engine = create_engine(
                    self.database_url,
                    poolclass=QueuePool,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,  # Validate connections before use
                    echo=False,  # Set to True for SQL debugging
                )
        return self._engine

    @property
    def SessionLocal(self) -> sessionmaker:
        """Lazy initialization of session factory"""
        if self._SessionLocal is None:
            self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return self._SessionLocal

    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()

    def get_engine(self) -> Engine:
        """Get the database engine"""
        return self.engine

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False


# Global database instance - lazy initialization
_db_instance: Optional[DatabaseConnection] = None


def get_db_connection() -> DatabaseConnection:
    """Get or create the global database connection instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    return _db_instance


def get_db_session() -> Session:
    """Dependency function to get database session"""
    db = get_db_connection()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


def get_engine() -> Engine:
    """Get database engine for migrations and raw queries"""
    db = get_db_connection()
    return db.get_engine()
