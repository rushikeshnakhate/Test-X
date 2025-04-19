"""
Connection manager for handling connections and providers.
"""
import asyncio
from typing import Dict, Any, Optional, Type, List
from ..base_classes.base_connection import BaseConnection
from ..base_classes.base_connection_provider import BaseConnectionProvider
from .connection_observer import ConnectionEvent, ConnectionObserver
from .connection_pool import ConnectionPool


class ConnectionManager:
    """Manager for connections and providers"""

    def __init__(self):
        self._connection_pool = ConnectionPool()
        self._providers: Dict[str, BaseConnectionProvider] = {}
        self._observers: List[ConnectionObserver] = []
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the connection manager"""
        if not self._initialized:
            self._initialized = True

    async def attach_observer(self, observer: ConnectionObserver) -> None:
        """Attach a connection observer"""
        async with self._lock:
            self._observers.append(observer)
            await self._connection_pool.attach_observer(observer)

    async def notify_observers(self, event: ConnectionEvent) -> None:
        """Notify all observers of a connection event"""
        async with self._lock:
            for observer in self._observers:
                await observer.on_connection_event(event)

    async def register_provider(self, service_type: str, provider: BaseConnectionProvider) -> None:
        """Register a connection provider"""
        async with self._lock:
            self._providers[service_type] = provider
            await self._connection_pool.register_provider(service_type, provider)

    async def get_provider(self, service_type: str) -> Optional[BaseConnectionProvider]:
        """Get a provider by service type"""
        async with self._lock:
            return self._providers.get(service_type)

    async def create_connection(self, service_type: str, connection_id: str) -> Optional[BaseConnection]:
        """
        Create a new connection using the appropriate provider
        
        Args:
            service_type: Type of service (e.g., 'ssh', 'winrm')
            connection_id: ID of the connection to create
            
        Returns:
            BaseConnection or None if creation failed
        """
        async with self._lock:
            provider = self._providers.get(service_type)
            if not provider:
                return None

            try:
                # Create the connection using the provider
                connection = await provider.create_connection()

                # Add to connection pool
                if connection:
                    await self._connection_pool.add_connection(service_type, connection_id, connection)

                    # Notify observers
                    event = ConnectionEvent(
                        connection_id=connection_id,
                        service_type=service_type,
                        event_type="created",
                        timestamp=asyncio.get_event_loop().time()
                    )
                    await self.notify_observers(event)

                return connection
            except Exception as e:
                # Log the error and return None
                print(f"Error creating connection for {service_type}:{connection_id}: {str(e)}")
                return None

    async def get_connection(self, service_type: str, connection_id: str, config: Any) -> BaseConnection:
        """Get or create a connection"""
        return await self._connection_pool.get_connection(service_type, connection_id, config)

    async def close_connection(self, service_type: str, connection_id: str) -> None:
        """Close a specific connection"""
        await self._connection_pool.close_connection(service_type, connection_id)

    async def close_all_connections(self) -> None:
        """Close all connections"""
        await self._connection_pool.close_all_connections()

    async def shutdown(self) -> None:
        """Shutdown the connection manager"""
        await self.close_all_connections()
        self._initialized = False
