"""Remote Search provider implementation"""

from typing import Dict, Any, Type, Optional, List
import hydra
from omegaconf import DictConfig
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.base_classes.base_connection import BaseConnection
from src.services.remote_search_service.pattern_search_service import RemoteSearchConnection


class RemoteSearchProvider(BaseConnectionProvider):
    """Provider for Remote Search connections"""

    def __init__(self):
        super().__init__()
        self._config: Dict[str, Dict[str, Any]] = {}
        self._enabled_connections: List[str] = []
        self.load_config()

    @hydra.main(version_base=None, config_path="../../../config", config_name="command_execution_config")
    def load_config(self, cfg: DictConfig = None) -> None:
        """Load Remote Search-specific configuration"""
        remote_search_config = cfg.get('remote_search', {})

        if remote_search_config.get('enable', True):
            connections = remote_search_config.get('connections', [])

            for conn in connections:
                if conn.get('enable', True):
                    connection_id = conn.get('name', 'default')
                    self._enabled_connections.append(connection_id)
                    self._config[connection_id] = conn

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the Remote Search connection class"""
        return RemoteSearchConnection

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new Remote Search connection"""
        if connection_id not in self._config:
            return None

        config = self._config[connection_id]
        connection = RemoteSearchConnection(config)
        await connection.connect()
        return connection
