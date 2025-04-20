import sqlite3
from typing import Dict, Any, List, Tuple, Optional

from src.common.logging_config import setup_logging

# Setup logging
logger = setup_logging("database_adapter", "DEBUG")


class DatabaseAdapter:
    """Adapter for SQLite database operations"""

    def __init__(self):
        """Initialize the database adapter"""
        self._connection = None
        self._is_connected = False
        logger.debug("Initialized database adapter")

    def connect(self, config: Dict[str, Any]) -> None:
        """Connect to the database"""
        try:
            logger.info(f"Connecting to database at {config.get('database_path', ':memory:')}")
            self._connection = sqlite3.connect(config.get('database_path', ':memory:'))
            self._is_connected = True
            logger.info("Successfully connected to database")
        except Exception as e:
            self._is_connected = False
            logger.error(f"Failed to connect to database: {str(e)}", exc_info=True)
            raise

    def disconnect(self) -> None:
        """Disconnect from the database"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
            self._is_connected = False
            logger.info("Successfully disconnected from database")
        except Exception as e:
            logger.error(f"Error disconnecting from database: {str(e)}", exc_info=True)
            raise

    def is_connected(self) -> bool:
        """Check if the database is connected"""
        return self._is_connected and self._connection is not None

    def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        """Execute a SQL query"""
        if not self.is_connected():
            logger.error("Not connected to database")
            raise ConnectionError("Not connected to database")

        try:
            logger.debug(f"Executing query: {query} with params: {params}")
            cursor = self._connection.cursor()
            cursor.execute(query, params or [])
            self._connection.commit()

            if query.strip().upper().startswith('SELECT'):
                columns = [description[0] for description in cursor.description]
                results = cursor.fetchall()
                return {
                    'columns': columns,
                    'results': results
                }
            else:
                return {
                    'affected_rows': cursor.rowcount
                }
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}", exc_info=True)
            raise
