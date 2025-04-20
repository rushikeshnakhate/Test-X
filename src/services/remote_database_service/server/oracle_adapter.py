import cx_Oracle
from typing import List, Dict, Any
from .database_adapter import DatabaseAdapter


class OracleAdapter(DatabaseAdapter):
    """Oracle implementation of DatabaseAdapter"""

    def __init__(self):
        self._connection = None

    def connect(self, connection_params: Dict[str, Any]) -> None:
        """Connect to Oracle database"""
        dsn = cx_Oracle.makedsn(
            connection_params['host'],
            connection_params['port'],
            service_name=connection_params.get('service_name')
        )
        self._connection = cx_Oracle.connect(
            user=connection_params['username'],
            password=connection_params['password'],
            dsn=dsn
        )

    def disconnect(self) -> None:
        if self._connection:
            self._connection.close()

    def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
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
