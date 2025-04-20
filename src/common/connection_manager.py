"""
Connection Manager for handling service connections.
"""
import asyncio
from typing import Dict, Any, Optional, Set
from src.common.logging_config import setup_logging, get_logger
from src.base_classes.base_connection import BaseConnection
from src.base_classes.base_connection_provider import BaseConnectionProvider
from .connection_observer import ConnectionEvent, ConnectionObserver
from .connection_pool import ConnectionPool

# Setup logging for connection manager
logger = setup_logging("connection_manager", "DEBUG")


class ConnectionManager:
    """Manages service connections and their lifecycle."""

    def __init__(self):
        """Initialize the connection manager."""
        logger.info("Initializing ConnectionManager")
        self._connection_pool = ConnectionPool()
        self._providers: Dict[str, BaseConnectionProvider] = {}
        self._observers: Set[Any] = set()
        self._lock = asyncio.Lock()
        self._initialized = False
        logger.debug("Connection manager components initialized")

    async def initialize(self) -> None:
        """Initialize the connection manager."""
        if self._initialized:
            logger.warning("Connection manager already initialized")
            return

        logger.info("Starting connection manager initialization")
        try:
            self._initialized = True
            logger.info("Connection manager initialized successfully")
        except Exception as e:
            logger.error(f"Error during connection manager initialization: {str(e)}", exc_info=True)
            raise

    async def attach_observer(self, observer: ConnectionObserver) -> None:
        """Attach a connection observer"""
        async with self._lock:
            self._observers.add(observer)
            await self._connection_pool.attach(observer)

    async def notify_observers(self, event: ConnectionEvent) -> None:
        """Notify all observers of a connection event"""
        logger.debug(f"Notifying {len(self._observers)} observers of event: {event}")
        async with self._lock:
            for observer in self._observers:
                try:
                    await observer.on_connection_event(event)
                    logger.debug(f"Successfully notified observer: {observer}")
                except Exception as e:
                    logger.error(f"Error notifying observer {observer}: {str(e)}", exc_info=True)

    async def register_provider(self, service_type: str, provider: BaseConnectionProvider) -> None:
        """Register a new connection provider."""
        logger.info(f"Registering provider for service type: {service_type}")
        try:
            async with self._lock:
                self._providers[service_type] = provider
                logger.info(f"Successfully registered provider for {service_type}")
                logger.debug(f"Provider details: {provider}")
                await self._connection_pool.register_provider(service_type, provider)
        except Exception as e:
            logger.error(f"Failed to register provider for {service_type}: {str(e)}", exc_info=True)
            raise

    async def get_provider(self, service_type: str) -> Optional[BaseConnectionProvider]:
        """Get a provider by service type"""
        async with self._lock:
            return self._providers.get(service_type)

    async def create_connection(self, service_type: str, connection_id: Optional[str] = None) -> Optional[BaseConnection]:
        """Create a new connection."""
        logger.info(f"Creating connection for service type: {service_type}")
        try:
            provider = self._providers.get(service_type)
            if not provider:
                logger.warning(f"No provider found for service type: {service_type}")
                return None

            async with self._lock:
                connection = await provider.create_connection(connection_id)
                if connection:
                    logger.info(f"Successfully created connection for {service_type}")
                    logger.debug(f"Connection details: {connection}")
                else:
                    logger.warning(f"Failed to create connection for {service_type}")
                return connection
        except Exception as e:
            logger.error(f"Error creating connection for {service_type}: {str(e)}", exc_info=True)
            return None

    async def get_connection(self, service_type: str, connection_id: str, config: Any) -> Optional[BaseConnection]:
        """Get an existing connection."""
        logger.debug(f"Retrieving connection {connection_id} for {service_type}")
        try:
            return await self._connection_pool.get_connection(service_type, connection_id, config)
        except Exception as e:
            logger.error(f"Error retrieving connection {connection_id}: {str(e)}", exc_info=True)
            return None

    async def close_connection(self, service_type: str, connection_id: str) -> None:
        """Close a connection."""
        logger.info(f"Closing connection for {service_type}")
        try:
            await self._connection_pool.close_connection(service_type, connection_id)
            logger.info(f"Successfully closed connection for {service_type}")
        except Exception as e:
            logger.error(f"Error closing connection for {service_type}: {str(e)}", exc_info=True)
            raise

    async def close_all_connections(self) -> None:
        """Close all connections"""
        await self._connection_pool.close_all_connections()

    async def shutdown(self) -> None:
        """Shutdown the connection manager and cleanup resources."""
        logger.info("Starting connection manager shutdown")
        try:
            async with self._lock:
                # Get all connections from the pool
                connections = await self._connection_pool.get_all_connections()
                
                # Close all connections
                for service_type, service_connections in connections.items():
                    logger.debug(f"Closing {len(service_connections)} connections for {service_type}")
                    for connection_id in service_connections:
                        try:
                            await self._connection_pool.close_connection(service_type, connection_id)
                            logger.debug(f"Closed connection {connection_id} for {service_type}")
                        except Exception as e:
                            logger.error(f"Error closing connection {connection_id}: {str(e)}", exc_info=True)
                
                # Clear all providers and observers
                self._providers.clear()
                self._observers.clear()
                self._initialized = False
                logger.info("Connection manager shutdown completed successfully")
        except Exception as e:
            logger.error(f"Error during connection manager shutdown: {str(e)}", exc_info=True)
            raise

    def add_observer(self, observer: Any) -> None:
        """Add an observer for connection events."""
        logger.debug("Adding new observer")
        self._observers.add(observer)
        logger.debug(f"Total observers: {len(self._observers)}")

    def remove_observer(self, observer: Any) -> None:
        """Remove an observer."""
        logger.debug("Removing observer")
        self._observers.discard(observer)
        logger.debug(f"Total observers: {len(self._observers)}")
