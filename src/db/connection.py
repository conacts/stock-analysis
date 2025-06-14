"""
Database connection management for Neon PostgreSQL
"""

import os

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
            raise ValueError("DATABASE_URL environment variable is required")

        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Validate connections before use
            echo=False,  # Set to True for SQL debugging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

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


# Global database instance
db = DatabaseConnection()


def get_db_session() -> Session:
    """Dependency function to get database session"""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


def get_engine() -> Engine:
    """Get database engine for migrations and raw queries"""
    return db.get_engine()
