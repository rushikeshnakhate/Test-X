"""
Remote database client implementation.
"""
from typing import Any, Optional, Dict, List, Tuple
import aiohttp
import json
from src.base_classes.base_connection import BaseConnection
from src.common.logging_config import setup_logging

# Setup logging
logger = setup_logging("database_client", "DEBUG")


class DatabaseClient(BaseConnection):
    """Client for connecting to remote database server"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the database client with configuration"""
        super().__init__(config)
        self._session = None
        self._base_url = f"http://{config['host']}:{config['port']}"
        logger.debug(f"Initialized database client with config: {config}")

    async def connect(self) -> None:
        """Establish connection to the database server"""
        logger.info(f"Connecting to database server at {self._base_url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self._base_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        if health_data and isinstance(health_data, dict):
                            if health_data.get('status') == 'healthy' and health_data.get('connected', False):
                                self._connected = True
                                logger.info("Successfully connected to database server")
                                return
                            else:
                                error_msg = health_data.get('error', 'Unknown error')
                                raise ConnectionError(f"Database server reported unhealthy status: {error_msg}")
                        else:
                            raise ConnectionError("Invalid health check response format")
                    else:
                        raise ConnectionError(f"Health check failed with status code: {response.status}")
        except Exception as e:
            self._connected = False
            logger.error(f"Failed to connect to database server: {str(e)}", exc_info=True)
            raise ConnectionError(f"Failed to connect to database server: {str(e)}")

    async def disconnect(self) -> None:
        """Close the database connection"""
        logger.info("Disconnecting from database server")
        try:
            if self._session:
                await self._session.close()
            self._connected = False
            logger.info("Successfully disconnected from database server")
        except Exception as e:
            logger.error(f"Error disconnecting from database server: {str(e)}", exc_info=True)
            raise

    async def health_check(self) -> bool:
        """Check if the database connection is healthy"""
        logger.debug("Performing database connection health check")
        try:
            if not self._connected:
                return False

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self._base_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return health_data.get('status') == 'healthy' and health_data.get('connected', False)
                    return False
        except Exception as e:
            logger.error(f"Error during health check: {str(e)}", exc_info=True)
            return False

    async def execute(self, query: str, params: List[Any] = None) -> Dict[str, Any]:
        """
        Execute a SQL query
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Query results or affected rows count
        """
        if not self.is_connected:
            logger.error("Not connected to database server")
            raise ConnectionError("Not connected to database server")

        logger.debug(f"Executing query: {query} with params: {params}")
        try:
            async with self._session.post(
                    f"{self._base_url}/execute",
                    json={'query': query, 'params': params or []}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Query execution failed: {response.status}")
                result = await response.json()
                if 'error' in result:
                    logger.error(f"Query execution failed: {result['error']}")
                    raise Exception(result['error'])
                logger.debug("Query executed successfully")
                return result
        except Exception as e:
            raise Exception(f"Failed to execute query: {str(e)}")

    async def select(self, query: str, params: List[Any] = None) -> Tuple[List[str], List[Tuple]]:
        """
        Execute a SELECT query
        
        Args:
            query: SELECT query to execute
            params: Query parameters
            
        Returns:
            Tuple of (columns, results)
        """
        logger.info(f"Executing SELECT query: {query}")
        result = await self.execute(query, params)
        logger.info(f"SELECT query returned {len(result['results'])} rows")
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
        logger.info(f"Executing INSERT query: {query}")
        result = await self.execute(query, params)
        logger.info(f"INSERT query affected {result['affected_rows']} rows")
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
        logger.info(f"Executing UPDATE query: {query}")
        result = await self.execute(query, params)
        logger.info(f"UPDATE query affected {result['affected_rows']} rows")
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
        logger.info(f"Executing DELETE query: {query}")
        result = await self.execute(query, params)
        logger.info(f"DELETE query affected {result['affected_rows']} rows")
        return result['affected_rows']
