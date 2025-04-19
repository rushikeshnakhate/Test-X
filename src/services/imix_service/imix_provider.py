"""IMIX provider implementation"""

from typing import Dict, Any, Type, Optional, List
import hydra
from omegaconf import DictConfig
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.base_classes.base_connection import BaseConnection
from src.services.imix_service.imix_service import IMIXConnection


class IMIXProvider(BaseConnectionProvider):
    """Provider for IMIX service connections"""

    def __init__(self):
        super().__init__()
        self._config: Dict[str, Dict[str, Any]] = {}
        self._enabled_connections: List[str] = []
        self.load_config()

    @hydra.main(version_base=None, config_path="../../../config", config_name="command_execution_config")
    def load_config(self, cfg: DictConfig = None) -> None:
        """Load IMIX-specific configuration"""
        imix_config = cfg.get('imix', {})

        if imix_config.get('enable', True):
            connections = imix_config.get('connections', [])

            for conn in connections:
                if conn.get('enable', True):
                    connection_id = conn.get('name', 'default')
                    self._enabled_connections.append(connection_id)
                    self._config[connection_id] = conn

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the IMIX connection class"""
        return IMIXConnection

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new IMIX connection"""
        if connection_id not in self._config:
            return None

        config = self._config[connection_id]
        connection = IMIXConnection(config)
        await connection.connect()
        return connection
