"""
Remote database provider implementation.
"""
from typing import Dict, Any, Type, Optional, List
import hydra
from omegaconf import DictConfig
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.base_classes.base_connection import BaseConnection
from .database_server import DatabaseServer
from .database_client import DatabaseClient


class RemoteDatabaseProvider(BaseConnectionProvider):
    """Provider for remote database connections"""

    def __init__(self):
        super().__init__()
        self._config: Dict[str, Dict[str, Any]] = {}
        self._enabled_connections: List[str] = []
        self.load_config()

    @hydra.main(version_base=None, config_path="../../../config", config_name="command_execution_config")
    def load_config(self, cfg: DictConfig = None) -> None:
        """Load database-specific configuration"""
        db_config = cfg.get('remote_database_server', {})

        if db_config.get('enable', True):
            connections = db_config.get('connections', [])
            for conn in connections:
                if conn.get('enable', True):
                    connection_id = conn.get('name', 'default')
                    self._enabled_connections.append(connection_id)
                    self._config[connection_id] = conn

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the database connection class"""
        return DatabaseClient

    async def create_connection(self, config: Dict[str, Any]) -> Optional[BaseConnection]:
        """Create a new database connection"""
        if not config:
            return None

        # Create server instance for this connection
        server = DatabaseServer()
        await server.connect(config)

        # Create client instance
        client = DatabaseClient()
        await client.connect(config)

        return client
