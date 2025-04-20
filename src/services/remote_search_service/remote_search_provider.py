"""Remote search provider implementation"""

from typing import Dict, Any, Type, Optional

from src.base_classes.base_connection import BaseConnection
from src.base_classes.base_connection_provider import BaseConnectionProvider
from src.common.logging_config import setup_logging
from src.services.remote_search_service.search_client import RemoteSearchConnection

# Setup logging for remote search provider
logger = setup_logging("remote_search_provider", "DEBUG")


class RemoteSearchProvider(BaseConnectionProvider):
    """Provider for remote search execution"""

    def __init__(self):
        """Initialize the remote search provider."""
        logger.info("Initializing RemoteSearchProvider")
        super().__init__()
        logger.debug("Remote search provider initialized")

    async def load_config(self) -> None:
        """Load remote search-specific configuration"""
        logger.debug("Loading remote search configuration")
        try:
            # Get configuration from config loader
            all_configs = self._config_loader.get_all_configs()
            if not all_configs or 'config' not in all_configs:
                logger.warning("No configuration found in config loader")
                return

            # Extract remote search configuration from the nested config structure
            cfg = all_configs['config'].get('search')
            if not cfg:
                logger.warning(
                    f"No remote search configuration found in config, available services: {list(all_configs['config'].keys())}")
                return

            # Extract remote search configuration
            if cfg.get('enable', True):
                connections = cfg.get('connections', [])
                for conn in connections:
                    if conn.get('enable', True):
                        connection_id = conn.get('name', 'default')
                        self._enabled_connections.append(connection_id)
                        self._config[connection_id] = conn
                logger.info("Remote search configuration loaded successfully")
                logger.debug(f"Enabled connections: {self._enabled_connections}")
            else:
                logger.info("Remote search provider is disabled in configuration")
        except Exception as e:
            logger.error(f"Error loading remote search configuration: {str(e)}", exc_info=True)
            raise

    def get_connection_class(self) -> Type[BaseConnection]:
        """Get the remote search connection class"""
        return RemoteSearchConnection

    async def create_connection(self, connection_id: str) -> Optional[BaseConnection]:
        """Create a new remote search connection"""
        logger.debug(f"Creating remote search connection for ID: {connection_id}")
        try:
            if connection_id not in self._config:
                logger.warning(f"No configuration found for connection ID: {connection_id}")
                return None

            config = self._config[connection_id]
            connection = RemoteSearchConnection(config)
            await connection.connect()
            logger.info(f"Remote search connection created successfully for ID: {connection_id}")
            return connection
        except Exception as e:
            logger.error(f"Error creating remote search connection: {str(e)}", exc_info=True)
            return None
