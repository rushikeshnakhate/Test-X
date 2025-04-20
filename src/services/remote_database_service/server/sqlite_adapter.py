import sqlite3
from typing import List, Dict, Any
from .database_adapter import DatabaseAdapter


class SQLiteAdapter(DatabaseAdapter):
    """SQLite implementation of DatabaseAdapter"""

    def __init__(self):
        self._connection = None

    def connect(self, connection_params: Dict[str, Any]) -> None:
        """Connect to SQLite database"""
        db_path = connection_params.get('database_path', ':memory:')
        self._connection = sqlite3.connect(db_path)

    def disconnect(self) -> None:
        """Close SQLite connection"""
        if self._connection:
            self._connection.close()

    def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        """Execute query against SQLite"""
        params = params or []
        cursor = self._connection.cursor()

        try:
            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return {
                    'columns': columns,
                    'results': results
                }
            else:
                self._connection.commit()
                return {
                    'affected_rows': cursor.rowcount
                }
        except Exception as e:
            self._connection.rollback()
            raise
