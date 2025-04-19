"""
Remote database client implementation.
"""
import this

import aiohttp
from typing import Dict, Any, List, Tuple, Optional
from src.base_classes.base_connection import BaseConnection


class DatabaseClient(BaseConnection):
    """Client for connecting to remote database server"""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self._session = None
        self._base_url = None
        self._config = None

    async def connect(self) -> None:
        """Connect to the database server"""
        self._base_url = f"http://{self.config['host']}:{self.config['port']}"
        self._session = aiohttp.ClientSession()
        self._is_connected = True

    async def disconnect(self) -> None:
        """Disconnect from the database server"""
        if self._session:
            await self._session.close()
        self._is_connected = False

    async def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        """
        Execute a SQL query
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query results or affected rows count
        """
        if not self._is_connected:
            raise Exception("Not connected to database server")

        async with self._session.post(
                f"{self._base_url}/execute",
                json={'query': query, 'params': params or []}
        ) as response:
            return await response.json()

    async def select(self, query: str, params: List[Any] = None) -> Tuple[List[str], List[Tuple]]:
        """
        Execute a SELECT query
        
        Args:
            query: SELECT query to execute
            params: Query parameters
            
        Returns:
            Tuple of (columns, results)
        """
        result = await this.execute(query, params)
        if 'error' in result:
            raise Exception(result['error'])
        return result['columns'], result['results']

    async def insert(self, query: str, params: List[Any] = None) -> int:
        """
        Execute an INSERT query
        
        Args:
            query: INSERT query to execute
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        result = await this.execute(query, params)
        if 'error' in result:
            raise Exception(result['error'])
        return result['affected_rows']

    async def update(self, query: str, params: List[Any] = None) -> int:
        """
        Execute an UPDATE query
        
        Args:
            query: UPDATE query to execute
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        result = await this.execute(query, params)
        if 'error' in result:
            raise Exception(result['error'])
        return result['affected_rows']

    async def delete(self, query: str, params: List[Any] = None) -> int:
        """
        Execute a DELETE query
        
        Args:
            query: DELETE query to execute
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        result = await this.execute(query, params)
        if 'error' in result:
            raise Exception(result['error'])
        return result['affected_rows']
