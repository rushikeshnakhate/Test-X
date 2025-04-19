from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, List
from .base_connection import BaseConnection
import hydra
from omegaconf import DictConfig, OmegaConf


class BaseConnectionProvider(ABC):
    """Base class for all connection providers"""

    def __init__(self):
        self._connections: Dict[str, BaseConnection] = {}
        self._config: DictConfig = None
        self._enabled_connections: List[str] = []

    @hydra.main(version_base=None, config_path="../../config", config_name="command_execution_config")
    def load_config(self, cfg: DictConfig = None) -> None:
        """
        Load configuration from config.yaml using hydra-core.
        Checks if services are enabled and creates a store list of connection objects.
        
        Args:
            cfg: Hydra configuration object containing all parameters
        """
        self._config = cfg
        service_type = self.__class__.__name__.lower().replace('provider', '')

        # Get service-specific config
        service_config = cfg.get(service_type, {})

        # Check if service is enabled and create connections
        if service_config.get('enable', True):
            connections = service_config.get('connections', [])
            for conn in connections:
                if conn.get('enable', True):
                    connection_id = conn.get('name', 'default')
                    self._enabled_connections.append(connection_id)
                    # Create connection object
                    self._connections[connection_id] = self.create_connection(conn)

    @abstractmethod
    async def create_connection(self, config: Dict[str, Any]) -> BaseConnection:
        """Create a new connection instance"""
        pass

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
            config = self._config.get(connection_id)
            if not config:
                return None
            self._connections[connection_id] = self.create_connection(config)

        connection = self._connections[connection_id]
        await connection.connect()
        return connection

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

    async def get_connection(self, connection_id: str, config: Dict[str, Any]) -> BaseConnection:
        """Get or create a connection"""
        if connection_id not in self._connections:
            connection = await self.create_connection(config)
            self._connections[connection_id] = connection
        return self._connections[connection_id]

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
