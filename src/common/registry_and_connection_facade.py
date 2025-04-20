"""
Registry and Connection Facade for managing service connections.
"""
import asyncio
from typing import Dict, Any, Optional
from src.common.logging_config import setup_logging
from src.base_classes.base_connection import BaseConnection
from src.base_classes.base_connection_provider import BaseConnectionProvider
from .connection_manager import ConnectionManager
from .connection_observer import ConnectionObserver, HealthObserver, MetricsObserver
from src.services.oracle.oracle_provider import OracleProvider
from src.services.imix_service.imix_provider import IMIXProvider
from src.services.quickfix.quickfix_provider import QuickFixProvider
from src.services.remote_command_service.command_provider import RemoteCommandProvider
from src.services.remote_database_service.client.database_provider import RemoteDatabaseProvider

# Setup logging for registry facade
logger = setup_logging("registry_facade", "DEBUG")


class RegistryAndConnectionFacade:
    """Facade for registry and connection management"""

    def __init__(self):
        """Initialize the registry and connection facade."""
        logger.info("Initializing RegistryAndConnectionFacade")
        self._connection_manager = ConnectionManager()
        self._providers: Dict[str, BaseConnectionProvider] = {}
        self._observers: Dict[str, ConnectionObserver] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
        logger.debug("Facade components initialized")

    async def initialize(self) -> None:
        """Initialize the facade."""
        if self._initialized:
            logger.warning("Registry facade already initialized")
            return

        logger.info("Starting facade initialization")
        try:
            # Initialize connection manager
            await self._connection_manager.initialize()

            # Initialize registry provider
            await self._initialize_registry_provider()

            # Attach observers
            observer = HealthObserver()
            await self._connection_manager.attach_observer(observer)
            self._observers["health"] = observer

            observer = MetricsObserver()
            await self._connection_manager.attach_observer(observer)
            self._observers["metrics"] = observer

            self._initialized = True
        except Exception as e:
            logger.error(f"Error during facade initialization: {str(e)}", exc_info=True)
            raise

    async def _initialize_registry_provider(self) -> None:
        """Initialize all providers."""
        logger.info("Initializing all providers")
        try:
            # Initialize Oracle provider
            oracle_provider = OracleProvider()
            await oracle_provider.initialize()
            await self.register_provider('oracle', oracle_provider)

            # Initialize IMIX provider
            imix_provider = IMIXProvider()
            await imix_provider.initialize()
            await self.register_provider('imix', imix_provider)

            # Initialize QuickFix provider
            quickfix_provider = QuickFixProvider()
            await quickfix_provider.initialize()
            await self.register_provider('quickfix', quickfix_provider)

            # Initialize Remote Command provider
            command_provider = RemoteCommandProvider()
            await command_provider.initialize()
            await self.register_provider('remotecommand', command_provider)

            # Initialize Remote Database provider
            database_provider = RemoteDatabaseProvider()
            await database_provider.initialize()
            await self.register_provider('remotedatabase', database_provider)

            logger.info("All providers initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing providers: {str(e)}", exc_info=True)
            raise

    async def register_provider(self, service_type: str, provider: BaseConnectionProvider) -> None:
        """Register a new connection provider."""
        logger.info(f"Registering provider for service type: {service_type}")
        try:
            async with self._lock:
                self._providers[service_type] = provider
                logger.info(f"Successfully registered provider for {service_type}")
                logger.debug(f"Provider details: {provider}")
                await self._connection_manager.register_provider(service_type, provider)
        except Exception as e:
            logger.error(f"Failed to register provider for {service_type}: {str(e)}", exc_info=True)
            raise

    async def get_provider(self, service_type: str) -> Optional[BaseConnectionProvider]:
        """Get a provider by service type"""
        async with self._lock:
            return self._providers.get(service_type)

    async def get_all_providers(self) -> Dict[str, BaseConnectionProvider]:
        """Get all registered providers"""
        logger.debug("Retrieving all registered providers")
        try:
            async with self._lock:
                providers = self._providers.copy()
                logger.info(f"Found {len(providers)} registered providers")
                logger.debug(f"Provider types: {list(providers.keys())}")
                return providers
        except Exception as e:
            logger.error(f"Error retrieving all providers: {str(e)}", exc_info=True)
            raise

    async def create_connection(self, service_type: str, connection_id: Optional[str] = None) -> Optional[
        BaseConnection]:
        """Create a new connection."""
        logger.info(f"Creating connection for service type: {service_type}")
        try:
            return await self._connection_manager.create_connection(service_type, connection_id)
        except Exception as e:
            logger.error(f"Error creating connection for {service_type}: {str(e)}", exc_info=True)
            return None

    async def create_connections(self, service_type: Optional[str] = None) -> Dict[str, Dict[str, BaseConnection]]:
        """Create all connections for a specific service type or all services if not specified."""
        logger.info(f"Creating connections for service type: {service_type if service_type else 'all'}")
        try:
            created_connections = {}
            
            if service_type:
                provider = await self.get_provider(service_type)
                if provider:
                    connections = await provider.create_connections()
                    if connections:
                        created_connections[service_type] = connections
            else:
                providers = await self.get_all_providers()
                for svc_type, provider in providers.items():
                    connections = await provider.create_connections()
                    if connections:
                        created_connections[svc_type] = connections
                        
            logger.info(f"Successfully created connections for {len(created_connections)} services")
            return created_connections
        except Exception as e:
            logger.error(f"Error creating connections: {str(e)}", exc_info=True)
            return {}

    async def get_connection(self, service_type: str, connection_id: str, config: Any) -> BaseConnection:
        """Get or create a connection"""
        logger.debug(f"Retrieving connection {connection_id} for {service_type}")
        try:
            connection = await self._connection_manager.get_connection(service_type, connection_id, config)
            if connection:
                logger.debug(f"Found connection {connection_id} for {service_type}")
            else:
                logger.warning(f"Connection {connection_id} not found for {service_type}")
            return connection
        except Exception as e:
            logger.error(f"Error retrieving connection {connection_id}: {str(e)}", exc_info=True)
            raise

    async def close_connection(self, service_type: str, connection_id: str) -> None:
        """Close a specific connection"""
        logger.info(f"Closing connection for {service_type}")
        try:
            await self._connection_manager.close_connection(service_type, connection_id)
            logger.info(f"Successfully closed connection for {service_type}")
        except Exception as e:
            logger.error(f"Error closing connection for {service_type}: {str(e)}", exc_info=True)
            raise

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

    async def shutdown(self) -> None:
        """Shutdown the facade and cleanup resources."""
        logger.info("Starting registry facade shutdown")
        try:
            await self._connection_manager.shutdown()
            self._providers.clear()
            self._observers.clear()
            self._initialized = False
            logger.info("Registry facade shutdown completed successfully")
        except Exception as e:
            logger.error(f"Error during facade shutdown: {str(e)}", exc_info=True)
            raise
