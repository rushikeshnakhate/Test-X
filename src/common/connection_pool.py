from typing import Dict, Any, Optional, Type
import asyncio
from ..base_classes.base_connection import BaseConnection
from ..base_classes.base_connection_provider import BaseConnectionProvider
from .connection_observer import ConnectionEvent, ConnectionSubject


class ConnectionPool(ConnectionSubject):
    """Connection pool for managing multiple connections"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionPool, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            super().__init__()
            self._providers: Dict[str, BaseConnectionProvider] = {}
            self._connections: Dict[str, Dict[str, BaseConnection]] = {}
            self._lock = asyncio.Lock()
            self._initialized = True

    async def register_provider(self, service_type: str, provider: BaseConnectionProvider) -> None:
        """Register a connection provider"""
        async with self._lock:
            self._providers[service_type] = provider

    async def get_connection(self, service_type: str, connection_id: str, config: Any) -> BaseConnection:
        """Get or create a connection using the appropriate provider"""
        async with self._lock:
            if service_type not in self._providers:
                raise ValueError(f"No provider registered for service type: {service_type}")

            provider = self._providers[service_type]
            connection = await provider.get_connection(connection_id, config)
            
            # Store the connection in the pool
            if service_type not in self._connections:
                self._connections[service_type] = {}
            self._connections[service_type][connection_id] = connection

            # Notify observers about the connection creation
            await self.notify(ConnectionEvent(
                connection_id=connection_id,
                event_type="connection_created",
                details={"service_type": service_type}
            ))

            return connection

    async def close_connection(self, service_type: str, connection_id: str) -> None:
        """Close a specific connection"""
        async with self._lock:
            if service_type in self._providers:
                provider = self._providers[service_type]
                await provider.close_connection(connection_id)
                
                # Remove the connection from the pool
                if service_type in self._connections and connection_id in self._connections[service_type]:
                    del self._connections[service_type][connection_id]
                    if not self._connections[service_type]:
                        del self._connections[service_type]

                # Notify observers about the connection closure
                await self.notify(ConnectionEvent(
                    connection_id=connection_id,
                    event_type="connection_closed",
                    details={"service_type": service_type}
                ))

    async def close_all_connections(self) -> None:
        """Close all connections across all providers"""
        async with self._lock:
            for service_type, provider in self._providers.items():
                await provider.close_all_connections()
            self._connections.clear()

    async def get_connection_status(self, service_type: str, connection_id: str) -> Optional[bool]:
        """Get the status of a specific connection"""
        async with self._lock:
            if service_type in self._providers:
                return await self._providers[service_type].get_connection_status(connection_id)
            return None

    async def get_all_providers(self) -> Dict[str, BaseConnectionProvider]:
        """Get all registered providers"""
        async with self._lock:
            return self._providers.copy()
            
    async def get_all_connections(self) -> Dict[str, Dict[str, BaseConnection]]:
        """Get all connections in the pool"""
        async with self._lock:
            return self._connections.copy()
