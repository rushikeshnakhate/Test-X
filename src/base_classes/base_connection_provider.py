from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, List
from .base_connection import BaseConnection
from src.common.logging_config import setup_logging, get_logger
from src.common.config_loader import ConfigLoader

# Setup logging for base provider
logger = setup_logging("base_provider", "DEBUG")


class BaseConnectionProvider(ABC):
    """Base class for all connection providers"""

    def __init__(self):
        """Initialize the provider."""
        logger.info(f"Initializing {self.__class__.__name__}")
        self._connections: Dict[str, BaseConnection] = {}
        self._config: Dict[str, Dict[str, Any]] = {}
        self._enabled_connections: List[str] = []
        self._connection_class: Optional[Type[BaseConnection]] = None
        self._config_loader = ConfigLoader()
        logger.debug("Provider components initialized")

    async def initialize(self) -> None:
        """Initialize the provider with configuration."""
        logger.info(f"Starting initialization of {self.__class__.__name__}")
        try:
            # Load configuration - concrete classes should override this
            await self.load_config()
            logger.info(f"{self.__class__.__name__} initialized successfully")
            logger.debug(f"Loaded configuration: {self._config}")
        except Exception as e:
            logger.error(f"Error initializing {self.__class__.__name__}: {str(e)}", exc_info=True)
            raise

    @abstractmethod
    async def load_config(self) -> None:
        """Load provider-specific configuration. Must be implemented by concrete classes."""
        pass

    @abstractmethod
    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new connection instance for the given connection ID"""
        pass

    async def create_connections(self) -> Dict[str, BaseConnection]:
        """Create all enabled connections"""
        logger.info(f"Creating connections for {self.__class__.__name__}")
        created_connections = {}

        for connection_id in self._enabled_connections:
            try:
                connection = await self.create_connection(connection_id)
                if connection:
                    created_connections[connection_id] = connection
                    logger.info(f"Successfully created connection {connection_id}")
                else:
                    logger.warning(f"Failed to create connection {connection_id}")
            except Exception as e:
                logger.error(f"Error creating connection {connection_id}: {str(e)}", exc_info=True)

        return created_connections

    @abstractmethod
    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the connection class type"""
        pass

    async def connect(self, connection_id: Optional[str] = None) -> Optional[BaseConnection]:
        """
        Connect to a specific connection or the default one if no ID provided
        
        Args:
            connection_id: Optional ID of the connection to connect to
            
        Returns:
            Connected BaseConnection instance or None if connection failed
        """
        if connection_id is None and self._enabled_connections:
            connection_id = self._enabled_connections[0]

        if connection_id not in self._enabled_connections:
            return None

        if connection_id not in self._connections:
            connection = await self.create_connection(connection_id)
            if connection:
                self._connections[connection_id] = connection

        if connection_id in self._connections:
            connection = self._connections[connection_id]
            await connection.connect()
            return connection

        return None

    async def connect_all(self) -> Dict[str, BaseConnection]:
        """
        Connect to all enabled connections
        
        Returns:
            Dictionary of connection_id to BaseConnection for all connected instances
        """
        connected = {}
        for connection_id in self._enabled_connections:
            connection = await self.connect(connection_id)
            if connection:
                connected[connection_id] = connection
        return connected

    async def get_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Get or create a connection"""
        if connection_id not in self._connections:
            connection = await self.create_connection(connection_id)
            if connection:
                self._connections[connection_id] = connection
        return self._connections.get(connection_id)

    async def close_connection(self, connection_id: str) -> None:
        """Close and remove a connection"""
        if connection_id in self._connections:
            await self._connections[connection_id].disconnect()
            del self._connections[connection_id]

    async def close_all_connections(self) -> None:
        """Close all connections"""
        for connection_id in list(self._connections.keys()):
            await self.close_connection(connection_id)

    async def get_connection_status(self, connection_id: str) -> Optional[bool]:
        """Get connection status"""
        if connection_id in self._connections:
            return self._connections[connection_id].is_connected
        return None

    def get_enabled_connections(self) -> List[str]:
        """Get list of enabled connection IDs"""
        return self._enabled_connections.copy()

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate provider configuration."""
        logger.debug(f"Validating configuration for {self.__class__.__name__}")
        try:
            # Implementation specific to each provider
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}", exc_info=True)
            return False

    async def get_health_status(self) -> Dict[str, Any]:
        """Get provider health status."""
        logger.debug(f"Getting health status for {self.__class__.__name__}")
        try:
            # Implementation specific to each provider
            return {"status": "healthy"}
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}", exc_info=True)
            return {"status": "unhealthy", "error": str(e)}

    async def shutdown(self) -> None:
        """Shutdown the provider."""
        logger.info(f"Shutting down {self.__class__.__name__}")
        try:
            await self.close_all_connections()
            logger.info(f"{self.__class__.__name__} shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
            raise
