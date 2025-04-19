"""
Facade for registry and connection management.
"""
from typing import Dict, Any, Type, Optional
from .connection_manager import ConnectionManager
from .connection_observer import ConnectionEvent, ConnectionObserver, LoggingObserver, MetricsObserver, \
    HealthCheckObserver
from ..base_classes.base_connection import BaseConnection
from .registry_provider import RegistryProvider
import asyncio


class RegistryAndConnectionFacade:
    """Facade for registry and connection management"""

    def __init__(self):
        self._connection_manager = ConnectionManager()
        self._registry_provider = RegistryProvider()
        self._observers: Dict[str, ConnectionObserver] = {
            "logging": LoggingObserver(),
            "metrics": MetricsObserver(),
            "health": HealthCheckObserver()
        }
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the facade and attach observers"""
        if not self._initialized:
            # Initialize connection manager
            await self._connection_manager.initialize()

            # Initialize registry provider
            await self._registry_provider.initialize()

            # Attach observers
            for observer in self._observers.values():
                await self._connection_manager.attach_observer(observer)

            self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown all connections"""
        if self._initialized:
            # Shutdown connection manager
            await self._connection_manager.shutdown()

            # Clear registry provider
            await self._registry_provider.clear()

            self._initialized = False

    async def register_provider(self, service_type: str, provider: Any) -> None:
        """Register a new provider"""
        if not self._initialized:
            await self.initialize()

        # Register with both the registry provider and connection manager
        await self._registry_provider.register(service_type, provider)
        await self._connection_manager.register_provider(service_type, provider)

    async def get_provider(self, service_type: str) -> Optional[Any]:
        """Get a provider by service type"""
        if not self._initialized:
            await self.initialize()
        return await self._registry_provider.get(service_type)

    async def get_all_providers(self) -> Dict[str, Any]:
        """Get all registered providers"""
        if not self._initialized:
            await self.initialize()
        return await self._registry_provider.get_all()

    async def create_connection(self, service_type: str, connection_id: Optional[str] = None) -> Optional[
        BaseConnection]:
        """
        Create a new connection using the appropriate provider
        
        Args:
            service_type: Type of service (e.g., 'ssh', 'winrm')
            connection_id: Optional ID of the connection to create. If None, connects to all enabled connections
            
        Returns:
            BaseConnection or None if creation failed
        """
        if not self._initialized:
            await self.initialize()

        # Check if provider exists
        provider = await self.get_provider(service_type)
        if not provider:
            return None

        try:
            # Connect using the provider's connect method
            connection = await provider.connect(connection_id)
            if connection:
                # Register the provider with the connection manager
                await self._connection_manager.register_provider(service_type, provider)

                # Notify observers about the connection creation
                event = ConnectionEvent(
                    connection_id=connection_id or "default",
                    service_type=service_type,
                    event_type="created",
                    timestamp=asyncio.get_event_loop().time()
                )
                await self._connection_manager.notify_observers(event)

            return connection
        except Exception as e:
            print(f"Error creating connection for {service_type}:{connection_id}: {str(e)}")
            return None

    async def get_connection(self, service_type: str, connection_id: str, config: Any) -> BaseConnection:
        """Get or create a connection"""
        if not self._initialized:
            await self.initialize()
        return await self._connection_manager.get_connection(service_type, connection_id, config)

    async def close_connection(self, service_type: str, connection_id: str) -> None:
        """Close a specific connection"""
        if not self._initialized:
            await self.initialize()
        await self._connection_manager.close_connection(service_type, connection_id)

    async def get_connection_health(self) -> Dict[str, bool]:
        """Get health status of all connections"""
        if not self._initialized:
            await self.initialize()
        health_observer = self._observers["health"]
        return health_observer.health_status

    async def get_connection_metrics(self) -> Dict[str, Dict[str, int]]:
        """Get metrics for all connections"""
        if not self._initialized:
            await self.initialize()
        metrics_observer = self._observers["metrics"]
        return metrics_observer.metrics

    async def notify_connection_event(self, connection_id: str, event_type: str,
                                      details: Dict[str, Any] = None) -> None:
        """Notify observers of a connection event"""
        if not self._initialized:
            await self.initialize()
        event = ConnectionEvent(connection_id, event_type, details)
        await self._connection_manager.notify_observers(event)
