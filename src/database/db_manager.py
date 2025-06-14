"""
Database Manager for conversation history and portfolio data
"""

from typing import Any, List, Tuple

from sqlalchemy import text

from src.db.connection import get_db_connection


class DatabaseManager:
    """Database manager for conversation history operations"""

    def __init__(self):
        self.db_connection = get_db_connection()

    def execute_query(self, query: str, params: List[Any] = None) -> List[Tuple]:
        """Execute a query and return results"""
        try:
            with self.db_connection.get_session() as session:
                if params:
                    result = session.execute(text(query), params)
                else:
                    result = session.execute(text(query))

                # For SELECT queries, fetch all results
                if query.strip().upper().startswith("SELECT"):
                    return result.fetchall()

                # For INSERT/UPDATE/DELETE, commit and return affected rows
                session.commit()
                return result.fetchall() if result.returns_rows else []

        except Exception as e:
            print(f"Database query failed: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connection"""
        return self.db_connection.test_connection()
